"""Temporal YOLOv8 object detection and OpenPose postural analysis.

The academic prototype follows one person selected by YOLO in each sampled
frame. OpenPose COCO heatmaps provide 2D keypoints; this implementation does
not perform OpenPose part-affinity multi-person assembly or clinical diagnosis.
"""

from __future__ import annotations

from pathlib import Path
import math
import statistics
import subprocess
import time

from .analysis import event


OPENPOSE_POINTS = (
    "nariz",
    "pescoço",
    "ombro_direito",
    "cotovelo_direito",
    "punho_direito",
    "ombro_esquerdo",
    "cotovelo_esquerdo",
    "punho_esquerdo",
    "quadril_direito",
    "joelho_direito",
    "tornozelo_direito",
    "quadril_esquerdo",
    "joelho_esquerdo",
    "tornozelo_esquerdo",
    "olho_direito",
    "olho_esquerdo",
    "orelha_direita",
    "orelha_esquerda",
)

DEFAULT_THRESHOLDS = {
    "min_arm_angle": 45.0,
    "min_elbow_angle": 135.0,
    "max_shoulder_elevation_ratio": 0.15,
    "max_head_tilt_deg": 15.0,
    "max_forward_lateral_ratio": 0.25,
}


def _angle(a, vertex, c):
    """Return a two-dimensional joint angle in degrees."""
    if not all((a, vertex, c)):
        return None
    first = (a["x"] - vertex["x"], a["y"] - vertex["y"])
    second = (c["x"] - vertex["x"], c["y"] - vertex["y"])
    denominator = math.hypot(*first) * math.hypot(*second)
    if denominator < 1e-9:
        return None
    cosine = (first[0] * second[0] + first[1] * second[1]) / denominator
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def _pose_features(points, person_box):
    point = {entry["name"]: entry for entry in points}
    required = (
        "ombro_direito",
        "cotovelo_direito",
        "punho_direito",
        "quadril_direito",
        "ombro_esquerdo",
        "quadril_esquerdo",
    )
    if any(name not in point for name in required):
        return None

    right_shoulder = point["ombro_direito"]
    right_elbow = point["cotovelo_direito"]
    right_wrist = point["punho_direito"]
    right_hip = point["quadril_direito"]
    left_shoulder = point["ombro_esquerdo"]
    left_hip = point["quadril_esquerdo"]
    neck = point.get("pescoço")

    arm_angle = _angle(right_elbow, right_shoulder, right_hip)
    elbow_angle = _angle(right_shoulder, right_elbow, right_wrist)
    torso_height = abs(
        (right_shoulder["y"] + left_shoulder["y"])
        - (right_hip["y"] + left_hip["y"])
    ) / 2
    shoulder_elevation = (
        (left_shoulder["y"] - right_shoulder["y"]) / torso_height
        if torso_height > 1e-6
        else None
    )

    head_tilt = None
    right_ear, left_ear = point.get("orelha_direita"), point.get("orelha_esquerda")
    if right_ear and left_ear:
        dx = left_ear["x"] - right_ear["x"]
        dy = left_ear["y"] - right_ear["y"]
        if abs(dx) > 1e-6:
            head_tilt = abs(math.degrees(math.atan2(dy, dx)))

    body_width = max(1.0, abs(left_shoulder["x"] - right_shoulder["x"]))
    lateral_ratio = abs(right_wrist["x"] - right_shoulder["x"]) / body_width
    confidence_names = required + ("cotovelo_direito", "punho_direito")
    confidence = sum(point[name]["confidence"] for name in confidence_names) / len(
        confidence_names
    )
    if neck:
        confidence = (confidence * len(confidence_names) + neck["confidence"]) / (
            len(confidence_names) + 1
        )

    return {
        "arm_angle": round(arm_angle, 2) if arm_angle is not None else None,
        "elbow_angle": round(elbow_angle, 2) if elbow_angle is not None else None,
        "shoulder_elevation_ratio": round(shoulder_elevation, 4)
        if shoulder_elevation is not None
        else None,
        "head_tilt_deg": round(head_tilt, 2) if head_tilt is not None else None,
        "arm_lateral_ratio": round(lateral_ratio, 4),
        "pose_confidence": round(confidence, 3),
        "person_box": [round(float(value), 1) for value in person_box],
    }


def aggregate_repetition_features(frame_records, first_frame, last_frame):
    """Aggregate sampled pose features over one annotated repetition."""
    records = [
        record
        for record in frame_records
        if first_frame <= record["frame_index"] <= last_frame
        and record.get("features")
    ]
    if not records:
        return {"pose_status": "inconclusivo", "sample_count": 0}

    def values(name):
        return [
            record["features"][name]
            for record in records
            if record["features"].get(name) is not None
        ]

    arm_angles = values("arm_angle")
    elbow_angles = values("elbow_angle")
    shoulder_elevation = values("shoulder_elevation_ratio")
    head_tilts = values("head_tilt_deg")
    arm_angles_and_lateral = [
        record["features"]["arm_lateral_ratio"]
        for record in records
        if record["features"].get("arm_angle") is not None
        and record["features"]["arm_angle"] >= 45
    ]
    confidences = values("pose_confidence")
    return {
        "pose_status": "avaliavel" if len(records) >= 2 else "inconclusivo",
        "sample_count": len(records),
        "max_arm_angle": round(max(arm_angles), 2) if arm_angles else None,
        "min_elbow_angle": round(min(elbow_angles), 2) if elbow_angles else None,
        "max_shoulder_elevation_ratio": round(max(shoulder_elevation), 4)
        if shoulder_elevation
        else None,
        "max_head_tilt_deg": round(max(head_tilts), 2) if head_tilts else None,
        "median_arm_lateral_ratio": round(statistics.median(arm_angles_and_lateral), 4)
        if arm_angles_and_lateral
        else None,
        "mean_pose_confidence": round(sum(confidences) / len(confidences), 3)
        if confidences
        else None,
        "evidence_frames": [record["frame_index"] for record in records],
    }


def _pose_events(frame_records, case_id, thresholds=None):
    thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    eligible = [
        record
        for record in frame_records
        if record.get("features") and record["features"].get("arm_angle") is not None
    ]
    # Dataset annotations are used for evaluation; this segmentation is only an
    # exploratory runtime approximation for the unlabelled demonstration video.
    repetitions = []
    if len(eligible) >= 2:
        from .repetitions import summarize_repetitions

        angles = [
            {
                "time_s": record["time_s"],
                "angle": record["features"]["arm_angle"],
                "side": "direito",
            }
            for record in eligible
        ]
        measurements = [
            {
                "time_s": record["time_s"],
                "side": "direito",
                "elbow_angle": record["features"].get("elbow_angle") or 180.0,
                "trunk_tilt": 0.0,
            }
            for record in eligible
        ]
        repetitions = summarize_repetitions(
            angles, measurements, side="direito", low=12, min_samples=2
        )

    events = []
    details = []
    checks = (
        ("max_arm_angle", "amplitude_baixa", "lt", "min_arm_angle"),
        ("min_elbow_angle", "cotovelo_flexionado", "lt", "min_elbow_angle"),
        (
            "max_shoulder_elevation_ratio",
            "ombro_elevado",
            "gt",
            "max_shoulder_elevation_ratio",
        ),
        ("max_head_tilt_deg", "cabeca_inclinada", "gt", "max_head_tilt_deg"),
        (
            "median_arm_lateral_ratio",
            "braco_fora_do_plano",
            "lt",
            "max_forward_lateral_ratio",
        ),
    )
    for index, repetition in enumerate(repetitions, start=1):
        matching = [
            record
            for record in eligible
            if repetition["start_s"] <= record["time_s"] <= repetition["end_s"]
        ]
        if not matching:
            continue
        start_frame = matching[0]["frame_index"]
        end_frame = matching[-1]["frame_index"]
        features = aggregate_repetition_features(
            eligible, start_frame, end_frame
        )
        details.append(
            {
                "repetition": index,
                "start_s": repetition["start_s"],
                "end_s": repetition["end_s"],
                **features,
            }
        )
        if features["pose_status"] != "avaliavel":
            continue
        for field, kind, operator, threshold_name in checks:
            value = features.get(field)
            if value is None:
                continue
            threshold = thresholds[threshold_name]
            # Forward-plane proxy is only evaluated while the arm is raised.
            if field == "median_arm_lateral_ratio" and not (
                (features.get("max_arm_angle") or 0) >= thresholds["min_arm_angle"]
            ):
                continue
            is_anomaly = value < threshold if operator == "lt" else value > threshold
            if not is_anomaly:
                continue
            frame_feature = {
                "max_arm_angle": "arm_angle",
                "min_elbow_angle": "elbow_angle",
                "max_shoulder_elevation_ratio": "shoulder_elevation_ratio",
                "max_head_tilt_deg": "head_tilt_deg",
                "median_arm_lateral_ratio": "arm_lateral_ratio",
            }[field]
            candidates = [
                record
                for record in matching
                if record["features"].get(frame_feature) is not None
                and (
                    field != "median_arm_lateral_ratio"
                    or record["features"].get("arm_angle", 0)
                    >= thresholds["min_arm_angle"]
                )
            ]
            selector = min if operator == "lt" else max
            record = selector(
                candidates or matching,
                key=lambda item: item["features"].get(frame_feature, value),
            )
            source_frame = record["frame_index"]
            threshold_description = (
                f"experimental {operator} {threshold:g}"
            )
            output_event = event(
                case_id,
                record["time_s"],
                "video",
                kind,
                f"{field}={value:g}; repetição {repetition['start_s']:.2f}–{repetition['end_s']:.2f}s",
                threshold_description,
                source=record.get("source"),
                model="OpenPose COCO + YOLOv8n",
                frame_index=source_frame,
                confidence=features.get("mean_pose_confidence"),
                review_status="revisao_humana_requerida",
            )
            events.append(output_event)
    return details, events


def analyze_video_models(
    video_path,
    output_dir,
    weights_dir,
    case_id=None,
    sample_fps=5.0,
    thresholds=None,
    write_video=False,
    frame_ranges=None,
):
    """Run YOLOv8 and OpenPose on a temporal sample of a complete video.

    The largest YOLO person detection is used as the OpenPose region of
    interest. `sample_fps` controls the inference rate while each record keeps
    its source frame number and timestamp. Video and weights remain external
    assets; outputs are written only to the requested output directory.
    """
    import cv2
    from ultralytics import YOLO

    video_path = Path(video_path)
    output_dir = Path(output_dir)
    weights_dir = Path(weights_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if sample_fps <= 0:
        raise ValueError("sample_fps must be positive.")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    source_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if not width or not height or not frame_count:
        cap.release()
        raise ValueError("Video has no valid dimensions or frames.")

    yolo_path = weights_dir.parent / "yolov8n.pt"
    yolo = YOLO(str(yolo_path))
    proto_path = weights_dir / "pose_deploy.prototxt"
    weights_path = weights_dir / "pose_iter_440000.caffemodel"
    openpose = None
    if proto_path.exists() and weights_path.exists():
        openpose = cv2.dnn.readNetFromCaffe(str(proto_path), str(weights_path))

    interval = max(1, round(source_fps / sample_fps))
    actual_sample_fps = source_fps / interval
    selected_ranges = sorted(
        (int(start), int(end)) for start, end in (frame_ranges or [])
    )
    range_index = 0
    output_video = output_dir / "openpose_yolo_temporal.mp4"
    intermediate_video = output_dir / "openpose_yolo_temporal_intermediario.mp4"
    writer = None
    if write_video:
        writer = cv2.VideoWriter(
            str(intermediate_video),
            cv2.VideoWriter_fourcc(*"mp4v"),
            source_fps,
            (width, height),
        )
        if not writer.isOpened():
            cap.release()
            raise RuntimeError("Could not create the annotated video.")

    records = []
    latencies = []
    object_counts = {}
    count = 0
    last_boxes = []
    last_points = []
    start_all = time.perf_counter()
    try:
        while True:
            if selected_ranges:
                while (
                    range_index < len(selected_ranges)
                    and count > selected_ranges[range_index][1]
                ):
                    range_index += 1
                in_selected_range = (
                    range_index < len(selected_ranges)
                    and selected_ranges[range_index][0]
                    <= count
                    <= selected_ranges[range_index][1]
                )
            else:
                in_selected_range = frame_ranges is None
            should_infer = count % interval == 0 and in_selected_range
            needs_frame = writer is not None or should_infer
            if needs_frame:
                ok, frame = cap.read()
            else:
                ok, frame = cap.grab(), None
            if not ok:
                break
            if should_infer:
                start = time.perf_counter()
                prediction = yolo.predict(frame, verbose=False, device="cpu")[0]
                boxes = []
                people = []
                for box in prediction.boxes:
                    class_id = int(box.cls[0])
                    label = prediction.names[class_id]
                    confidence = float(box.conf[0])
                    coordinates = [float(value) for value in box.xyxy[0]]
                    item = {
                        "class": label,
                        "confidence": round(confidence, 3),
                        "box": [round(value, 1) for value in coordinates],
                    }
                    boxes.append(item)
                    object_counts[label] = object_counts.get(label, 0) + 1
                    if label == "person":
                        x1, y1, x2, y2 = coordinates
                        area = max(0, x2 - x1) * max(0, y2 - y1)
                        people.append((area * confidence, coordinates))

                points = []
                features = None
                person_box = None
                pose_status = "indisponivel" if openpose is None else "sem_pessoa"
                if people:
                    _, coordinates = max(people, key=lambda item: item[0])
                    x1, y1, x2, y2 = coordinates
                    padding_x = (x2 - x1) * 0.08
                    padding_y = (y2 - y1) * 0.08
                    x1 = max(0, int(x1 - padding_x))
                    y1 = max(0, int(y1 - padding_y))
                    x2 = min(width, int(x2 + padding_x))
                    y2 = min(height, int(y2 + padding_y))
                    person_box = [x1, y1, x2, y2]
                    if openpose is not None and x2 > x1 and y2 > y1:
                        crop = frame[y1:y2, x1:x2]
                        blob = cv2.dnn.blobFromImage(
                            crop,
                            1 / 255.0,
                            (368, 368),
                            (0, 0, 0),
                            swapRB=False,
                            crop=False,
                        )
                        openpose.setInput(blob)
                        output = openpose.forward()
                        for point_index, name in enumerate(OPENPOSE_POINTS):
                            if point_index >= output.shape[1]:
                                break
                            heatmap = output[0, point_index, :, :]
                            _, confidence, _, location = cv2.minMaxLoc(heatmap)
                            if confidence < 0.1:
                                continue
                            x = x1 + int(location[0] * (x2 - x1) / output.shape[3])
                            y = y1 + int(location[1] * (y2 - y1) / output.shape[2])
                            points.append(
                                {
                                    "name": name,
                                    "x": x,
                                    "y": y,
                                    "confidence": round(float(confidence), 3),
                                }
                            )
                        features = _pose_features(points, person_box)
                        pose_status = "avaliavel" if features else "pose_insuficiente"

                timestamp = count / source_fps
                record = {
                    "frame_index": count,
                    "time_s": round(timestamp, 3),
                    "objects": boxes,
                    "person_box": person_box,
                    "points": points,
                    "features": features,
                    "pose_status": pose_status,
                    "source": video_path.name,
                }
                records.append(record)
                latencies.append(time.perf_counter() - start)
                last_boxes, last_points = boxes, points

            if writer is not None:
                annotated = frame.copy()
                for item in last_boxes:
                    x1, y1, x2, y2 = map(int, item["box"])
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 180, 0), 2)
                    cv2.putText(
                        annotated,
                        f"{item['class']} {item['confidence']:.2f}",
                        (x1, max(18, y1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (255, 180, 0),
                        1,
                    )
                for point in last_points:
                    cv2.circle(annotated, (point["x"], point["y"]), 4, (0, 255, 0), -1)
                cv2.putText(
                    annotated,
                    f"{count / source_fps:.2f}s | amostragem {actual_sample_fps:.2f} fps",
                    (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )
                writer.write(annotated)
            count += 1
    finally:
        cap.release()
        if writer is not None:
            writer.release()

    if not count:
        intermediate_video.unlink(missing_ok=True)
        raise ValueError("Video contains no decodable frames.")

    if write_video:
        import imageio_ffmpeg

        try:
            subprocess.run(
                [
                    imageio_ffmpeg.get_ffmpeg_exe(),
                    "-y",
                    "-i",
                    str(intermediate_video),
                    "-vf",
                    "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "23",
                    "-pix_fmt",
                    "yuv420p",
                    "-movflags",
                    "+faststart",
                    str(output_video),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        finally:
            intermediate_video.unlink(missing_ok=True)

    case_id = case_id or video_path.stem
    repetitions, pose_events = _pose_events(records, case_id, thresholds)
    sorted_latencies = sorted(latencies)
    p95_index = min(len(sorted_latencies) - 1, int(math.ceil(0.95 * len(sorted_latencies))) - 1)
    summary = {
        "source": video_path.name,
        "frames": count,
        "source_fps": source_fps,
        "sample_fps": round(actual_sample_fps, 3),
        "duration_s": round(count / source_fps, 3),
        "sampled_frames": len(records),
        "frame_selection": "annotated_ranges" if frame_ranges is not None else "full_video",
        "pose_frames": sum(record["pose_status"] == "avaliavel" for record in records),
        "objects_by_class": object_counts,
        "yolov8_status": "ok",
        "openpose_status": "ok" if openpose is not None else "indisponivel",
        "repetitions": repetitions,
        "events": pose_events,
        "inference_latency_ms": {
            "median": round(sorted_latencies[len(sorted_latencies) // 2] * 1000, 2),
            "p95": round(sorted_latencies[p95_index] * 1000, 2),
        }
        if sorted_latencies
        else None,
        "elapsed_s": round(time.perf_counter() - start_all, 3),
        "annotated_video": str(output_video) if write_video else None,
        "limitation": (
            "YOLOv8 usa classes gerais e seleciona a pessoa principal; OpenPose COCO usa máximos dos mapas 2D. "
            "Regras e segmentos são exploratórios e requerem revisão humana."
        ),
    }
    return {**summary, "frames_data": records}


def analyze_frame(video_path, output_dir, weights_dir, seconds=1.0):
    """Backward-compatible single-frame view built on the temporal analyzer."""
    import cv2
    from ultralytics import YOLO

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError("Could not open video.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_index = min(frame_count - 1, max(0, round(seconds * fps)))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, frame = cap.read()
    cap.release()
    if not ok or seconds < 0 or seconds * fps >= frame_count:
        raise ValueError("Requested timestamp is outside the video.")
    model_path = Path(weights_dir).parent / "yolov8n.pt"
    prediction = YOLO(str(model_path)).predict(frame, verbose=False, device="cpu")[0]
    objects = []
    person = None
    for box in prediction.boxes:
        class_id = int(box.cls[0])
        label = prediction.names[class_id]
        coordinates = [float(value) for value in box.xyxy[0]]
        item = {
            "class": label,
            "confidence": round(float(box.conf[0]), 3),
            "box": [round(value, 1) for value in coordinates],
        }
        objects.append(item)
        if label == "person" and (
            person is None or item["confidence"] > person["confidence"]
        ):
            person = item
    yolo_image = output_dir / "yolov8_quadro.jpg"
    cv2.imwrite(str(yolo_image), prediction.plot())

    points = []
    openpose_image = output_dir / "openpose_quadro.jpg"
    proto_path = Path(weights_dir) / "pose_deploy.prototxt"
    weights_path = Path(weights_dir) / "pose_iter_440000.caffemodel"
    if person and proto_path.exists() and weights_path.exists():
        x1, y1, x2, y2 = map(int, person["box"])
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
        crop = frame[y1:y2, x1:x2]
        net = cv2.dnn.readNetFromCaffe(str(proto_path), str(weights_path))
        net.setInput(
            cv2.dnn.blobFromImage(
                crop, 1 / 255.0, (368, 368), (0, 0, 0), swapRB=False, crop=False
            )
        )
        output = net.forward()
        for index, name in enumerate(OPENPOSE_POINTS):
            heatmap = output[0, index, :, :]
            _, confidence, _, location = cv2.minMaxLoc(heatmap)
            if confidence < 0.1:
                continue
            x = x1 + int(location[0] * crop.shape[1] / output.shape[3])
            y = y1 + int(location[1] * crop.shape[0] / output.shape[2])
            points.append(
                {"name": name, "x": x, "y": y, "confidence": round(float(confidence), 3)}
            )
        overlay = frame.copy()
        for point in points:
            cv2.circle(overlay, (point["x"], point["y"]), 4, (0, 255, 0), -1)
        cv2.imwrite(str(openpose_image), overlay)

    return {
        "time_s": round(frame_index / fps, 3),
        "yolov8": {
            "status": "ok",
            "objects": objects,
            "image": str(yolo_image),
        },
        "openpose": {
            "status": "ok" if points else "inconclusivo",
            "points": points,
            "image": str(openpose_image) if points else None,
            "limitation": "Inferência de um quadro em ROI detectada pelo YOLOv8; pontos 2D experimentais.",
        },
        "elapsed_s": None,
    }

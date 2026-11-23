"""Estimativa de pose e análise exploratória de elevação do braço."""

from pathlib import Path
import math
import subprocess
from .analysis import event, refresh_event_id
from .repetitions import summarize_repetitions, evaluate_repetitions


def shoulder_angle(shoulder, elbow, hip, aspect_ratio=1.0):
    a = ((elbow.x - shoulder.x) * aspect_ratio, elbow.y - shoulder.y)
    b = ((hip.x - shoulder.x) * aspect_ratio, hip.y - shoulder.y)
    norm = math.hypot(*a) * math.hypot(*b)
    if norm < 1e-9:
        return None
    return math.degrees(
        math.acos(max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / norm)))
    )


def analyze_video(
    path,
    output_path,
    case_id,
    sample_every=3,
    thresholds=None,
    save_video=True,
    frame_ranges=None,
    sample_fps=None,
):
    import cv2
    import mediapipe as mp

    path, output_path = Path(path), Path(output_path)
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Vídeo não pôde ser aberto: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    if sample_fps is not None:
        if sample_fps <= 0:
            cap.release()
            raise ValueError("sample_fps must be positive.")
        sample_every = max(1, round(fps / sample_fps))
    width, height = int(cap.get(3)), int(cap.get(4))
    if not width or not height:
        cap.release()
        raise ValueError("Vídeo sem dimensões válidas.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    intermediate = output_path.with_name(output_path.stem + "_intermediario.mp4")
    writer = None
    if save_video:
        writer = cv2.VideoWriter(
            str(intermediate), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )
        if not writer.isOpened():
            cap.release()
            raise RuntimeError("Não foi possível criar o vídeo anotado.")
    pose = mp.solutions.pose.Pose(
        model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5
    )
    drawing, connections = (
        mp.solutions.drawing_utils,
        mp.solutions.pose.POSE_CONNECTIONS,
    )
    count = detected = 0
    frame_samples = 0
    selected_ranges = sorted(
        (int(start), int(end)) for start, end in (frame_ranges or [])
    )
    range_index = 0
    angles = []
    measurements = []
    raised = False
    repetitions = 0
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
            should_analyze = count % sample_every == 0 and in_selected_range
            needs_frame = writer is not None or should_analyze
            if needs_frame:
                ok, frame = cap.read()
            else:
                ok, frame = cap.grab(), None
            if not ok:
                break
            if should_analyze:
                frame_samples += 1
                result = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                if result.pose_landmarks:
                    detected += 1
                    drawing.draw_landmarks(frame, result.pose_landmarks, connections)
                    l = result.pose_landmarks.landmark
                    for s, e, h in [(11, 13, 23), (12, 14, 24)]:
                        if (
                            min(l[s].visibility, l[e].visibility, l[h].visibility)
                            >= 0.5
                        ):
                            angle = shoulder_angle(l[s], l[e], l[h], width / height)
                            if angle is not None:
                                angles.append(
                                    {
                                        "time_s": round(count / fps, 3),
                                        "angle": round(angle, 1),
                                        "side": "esquerdo" if s == 11 else "direito",
                                    }
                                )
                    # Medidas de cotovelo e tronco, ainda sem limiares validados.
                    for shoulder, elbow, wrist, hip in [
                        (11, 13, 15, 23),
                        (12, 14, 16, 24),
                    ]:
                        if (
                            min(
                                l[shoulder].visibility,
                                l[elbow].visibility,
                                l[wrist].visibility,
                                l[hip].visibility,
                            )
                            >= 0.5
                        ):
                            elbow_angle = shoulder_angle(
                                l[elbow], l[shoulder], l[wrist], width / height
                            )
                            dx = (l[shoulder].x - l[hip].x) * width
                            dy = (l[shoulder].y - l[hip].y) * height
                            trunk_tilt = math.degrees(math.atan2(abs(dx), abs(dy)))
                            if elbow_angle is not None:
                                measurements.append(
                                    {
                                        "time_s": round(count / fps, 3),
                                        "side": (
                                            "esquerdo" if shoulder == 11 else "direito"
                                        ),
                                        "elbow_angle": round(elbow_angle, 1),
                                        "trunk_tilt": round(trunk_tilt, 1),
                                    }
                                )
                    valid = [
                        x["angle"]
                        for x in angles[-2:]
                        if x["time_s"] == round(count / fps, 3)
                    ]
                    up = bool(valid and max(valid) >= 90)
                    if up and not raised:
                        repetitions += 1
                    raised = up
                    cv2.putText(
                        frame,
                        f"Elevacoes: {repetitions}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                    )
            if writer is not None:
                writer.write(frame)
            count += 1
    finally:
        pose.close()
        cap.release()
        if writer is not None:
            writer.release()
    if not count:
        intermediate.unlink(missing_ok=True)
        raise ValueError("Vídeo sem quadros decodificáveis.")
    if save_video:
        import imageio_ffmpeg

        try:
            subprocess.run(
                [
                    imageio_ffmpeg.get_ffmpeg_exe(),
                    "-y",
                    "-i",
                    str(intermediate),
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-movflags",
                    "+faststart",
                    str(output_path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        finally:
            intermediate.unlink(missing_ok=True)
    reps = summarize_repetitions(angles, measurements)
    if thresholds:
        evaluate_repetitions(reps, thresholds, case_id)
    # Sem calibração, as medidas são exploratórias.
    events = [item for rep in reps for item in rep["events"]]
    enough_pose = (
        len(angles) >= 3
        and detected / max(1, frame_samples) >= 0.5
    )
    if enough_pose and max(x["angle"] for x in angles) < 45:
        events.append(
            event(
                case_id,
                angles[-1]["time_s"],
                "video",
                "amplitude_limitada",
                f'Maior ângulo observado: {max(x["angle"] for x in angles):.1f} graus',
                "Heurística experimental: amplitude máxima inferior a 45 graus no trecho",
            )
        )
    for item in events:
        item["source"] = path.name
        item["model"] = "MediaPipe Pose"
        if item.get("frame_index") is None:
            item["frame_index"] = round(item["time_s"] * fps)
        refresh_event_id(item)
    return {
        "frames": count,
        "fps": fps,
        "duration_s": round(count / fps, 2),
        "frames_pose": detected,
        "frames_analyzed": frame_samples,
        "frame_selection": "annotated_ranges" if frame_ranges is not None else "full_video",
        "repetitions": repetitions,
        "angles": angles,
        "measurements": measurements,
        "repetition_details": reps,
        "events": events,
        "output_video": str(output_path) if save_video else None,
        "status_movimento": (
            "avaliado" if enough_pose else "inconclusivo: pose insuficiente"
        ),
        "limitation": "Ângulo 2D depende da câmera; limiar exploratório, não diagnóstico.",
    }

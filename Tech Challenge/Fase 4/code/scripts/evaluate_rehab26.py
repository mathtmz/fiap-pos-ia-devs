"""Participant-wise evaluation of OpenPose/YOLO and the MediaPipe baseline."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
sys.path.insert(0, str(CODE_DIR / "src"))

from fisio_fase4.video import analyze_video
from fisio_fase4.vision_models import aggregate_repetition_features, analyze_video_models


PARTICIPANTS = ("Honza", "Mima", "Petra", "Terka", "Vasil")
ERROR_FEATURES = {
    "ERR_LOW_ABDUCTION": ("max_arm_angle", "lt"),
    "ERR_BENT_ARM": ("min_elbow_angle", "lt"),
    "ERR_ELEVATED_SHOULDER": ("max_shoulder_elevation_ratio", "gt"),
    "ERR_HEAD_TO_SIDE": ("max_head_tilt_deg", "gt"),
    "ERR_ARM_FORWARD": ("median_arm_lateral_ratio", "lt"),
}


def confusion_metrics(truth, prediction):
    tp = sum(actual and guess for actual, guess in zip(truth, prediction))
    fp = sum((not actual) and guess for actual, guess in zip(truth, prediction))
    fn = sum(actual and (not guess) for actual, guess in zip(truth, prediction))
    tn = sum((not actual) and (not guess) for actual, guess in zip(truth, prediction))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def aggregate_confusion_metrics(rows, total_repetitions):
    """Combine held-out predictions without averaging fold-level ratios."""
    counts = {
        key: sum(row.get(key, 0) for row in rows)
        for key in ("tp", "fp", "fn", "tn")
    }
    tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    evaluated = sum(row.get("evaluated", 0) for row in rows)
    return {
        "evaluated": evaluated,
        "coverage": round(evaluated / total_repetitions, 4)
        if total_repetitions
        else 0.0,
        **counts,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def threshold_prediction(value, threshold, direction):
    if value is None:
        return None
    return value < threshold if direction == "lt" else value > threshold


def fit_threshold(rows, feature, direction):
    """Choose a threshold using only the supplied development participants."""
    usable = [
        (float(row["features"][feature]), bool(row["target"]))
        for row in rows
        if row.get("features") and row["features"].get(feature) is not None
    ]
    if len(usable) < 4 or len({label for _, label in usable}) < 2:
        return None
    values = sorted({value for value, _ in usable})
    candidates = [
        (left + right) / 2 for left, right in zip(values, values[1:])
    ]
    if len(values) == 1:
        candidates = [values[0]]

    scored = []
    for threshold in candidates:
        truth = [label for _, label in usable]
        guesses = [threshold_prediction(value, threshold, direction) for value, _ in usable]
        metrics = confusion_metrics(truth, guesses)
        scored.append((metrics["f1"], metrics["precision"], threshold))
    return max(scored, key=lambda item: (item[0], item[1], -item[2]))[2]


def parse_error_codes(row):
    text = ",".join(
        value.strip()
        for value in (row.get("error_description", ""), row.get("additional_errors", ""))
        if value and value.strip()
    )
    return {value.strip() for value in text.split(",") if value.strip()}


def load_annotations(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return [
            row
            for row in csv.DictReader(file, delimiter=";")
            if row["exercise_id"] == "1"
        ]


def repetition_rows_for_participant(participant, annotations, vision_records, mediapipe_result, fps):
    rows = []
    for annotation in annotations:
        if annotation["person"] != participant:
            continue
        first = int(annotation["first_frame"])
        last = int(annotation["last_frame"])
        errors = parse_error_codes(annotation)
        features = aggregate_repetition_features(vision_records, first, last)
        start_s, end_s = first / fps, last / fps
        angle_values = [
            item["angle"]
            for item in mediapipe_result["angles"]
            if item["side"] == "direito" and start_s <= item["time_s"] <= end_s
        ]
        rows.append(
            {
                "participant": participant,
                "video_id": annotation["video_id"],
                "repetition": int(annotation["repetition_number"]),
                "first_frame": first,
                "last_frame": last,
                "correctness_score": int(annotation["correctness_score"]),
                "error_codes": sorted(errors),
                "features": features,
                "mediapipe": {
                    "max_arm_angle": max(angle_values) if angle_values else None,
                },
            }
        )
    return rows


def evaluate_fold(participant, all_rows):
    train = [row for row in all_rows if row["participant"] != participant]
    test = [row for row in all_rows if row["participant"] == participant]
    output = {
        "held_out_participant": participant,
        "training_participants": sorted({row["participant"] for row in train}),
        "test_repetitions": len(test),
        "per_error_type": {},
    }
    test_predictions = {
        f"{row['video_id']}_rep{row['repetition']}": {
            "participant": row["participant"],
            "frames": [row["first_frame"], row["last_frame"]],
            "true_errors": row["error_codes"],
            "predicted_errors": [],
            "type_predictions": {},
            "features": row["features"],
            "pose_status": row["features"].get("pose_status"),
        }
        for row in test
    }

    any_error_train = [
        {"target": bool(row["error_codes"]), "features": row["mediapipe"]}
        for row in train
    ]
    baseline_threshold = fit_threshold(any_error_train, "max_arm_angle", "lt")
    baseline_test = [
        row
        for row in test
        if row["mediapipe"].get("max_arm_angle") is not None
    ]
    baseline_predictions = [
        threshold_prediction(
            row["mediapipe"]["max_arm_angle"], baseline_threshold, "lt"
        )
        for row in baseline_test
    ] if baseline_threshold is not None else []
    output["mediapipe_binary"] = {
        "threshold": round(baseline_threshold, 4) if baseline_threshold is not None else None,
        "evaluated": len(baseline_test),
        "coverage": round(len(baseline_test) / len(test), 4) if test else 0,
        **(
            confusion_metrics(
                [bool(row["error_codes"]) for row in baseline_test],
                baseline_predictions,
            )
            if baseline_test and baseline_predictions
            else {}
        ),
    }
    baseline_prediction_by_row = {
        id(row): prediction for row, prediction in zip(baseline_test, baseline_predictions)
    }
    for row in test:
        test_predictions[f"{row['video_id']}_rep{row['repetition']}"]["mediapipe_binary_prediction"] = baseline_prediction_by_row.get(id(row))

    predictions_any = []
    for error_code, (feature, direction) in ERROR_FEATURES.items():
        development = [
            {
                "target": error_code in row["error_codes"],
                "features": row["features"],
            }
            for row in train
        ]
        threshold = fit_threshold(development, feature, direction)
        eligible = [
            row for row in test if row["features"].get(feature) is not None
        ]
        guesses = [
            threshold_prediction(row["features"][feature], threshold, direction)
            for row in eligible
        ] if threshold is not None else []
        truth = [error_code in row["error_codes"] for row in eligible]
        metrics = confusion_metrics(truth, guesses) if guesses else {}
        output["per_error_type"][error_code] = {
            "feature": feature,
            "direction": direction,
            "threshold": round(threshold, 4) if threshold is not None else None,
            "evaluated": len(eligible),
            "coverage": round(len(eligible) / len(test), 4) if test else 0,
            **metrics,
        }
        prediction_by_row = {
            id(row): prediction for row, prediction in zip(eligible, guesses)
        }
        for row in test:
            key = f"{row['video_id']}_rep{row['repetition']}"
            guess = prediction_by_row.get(id(row))
            test_predictions[key]["type_predictions"][error_code] = guess
            if guess is True:
                test_predictions[key]["predicted_errors"].append(error_code)
        if threshold is not None:
            predictions_any.append(
                [
                    threshold_prediction(
                        row["features"].get(feature), threshold, direction
                    )
                    for row in test
                ]
            )

    if predictions_any:
        new_predictions = [
            any(prediction[index] is True for prediction in predictions_any)
            for index in range(len(test))
        ]
        prediction_by_row = {
            id(row): prediction for row, prediction in zip(test, new_predictions)
        }
        new_eval = [
            row
            for row in test
            if row["features"].get("pose_status") == "avaliavel"
        ]
        output["openpose_yolo_binary"] = {
            "evaluated": len(new_eval),
            "inconclusive": len(test) - len(new_eval),
            "coverage": round(len(new_eval) / len(test), 4) if test else 0,
            **(
                confusion_metrics(
                    [bool(row["error_codes"]) for row in new_eval],
                    [prediction_by_row[id(row)] for row in new_eval],
                )
                if new_eval
                else {}
            ),
        }
    else:
        output["openpose_yolo_binary"] = {"evaluated": 0, "coverage": 0}

    per_class_f1 = [
        values["f1"]
        for values in output["per_error_type"].values()
        if "f1" in values
    ]
    output["openpose_yolo_macro_f1"] = (
        round(statistics.mean(per_class_f1), 4) if per_class_f1 else None
    )
    output["test_predictions"] = list(test_predictions.values())
    return output


def evaluate(sample_fps=0.5, force=False):
    data_dir = PROJECT_ROOT / "data" / "public" / "rehab26"
    video_dir = data_dir / "videos"
    model_dir = PROJECT_ROOT / "data" / "public" / "modelos" / "openpose"
    cache_dir = CODE_DIR / "outputs" / "rehab26_features"
    cache_dir.mkdir(parents=True, exist_ok=True)
    annotations = load_annotations(data_dir / "Segmentation.csv")
    all_rows = []
    inference_summary = {}

    for participant in PARTICIPANTS:
        source = video_dir / f"ex1_{participant}_cam1.mp4"
        if not source.exists():
            raise FileNotFoundError(
                f"Missing {source.name}. Run scripts/download_consultas_rehab26.py "
                "--video --participants all first."
            )
        fps_key = f"{sample_fps:g}".replace(".", "p")
        participant_annotations = [
            row for row in annotations if row["person"] == participant
        ]
        annotated_ranges = [
            (int(row["first_frame"]), int(row["last_frame"]))
            for row in participant_annotations
        ]
        cache = cache_dir / f"ex1_{participant}_{fps_key}fps_annotated_features.json"
        if cache.exists() and not force:
            vision = json.loads(cache.read_text(encoding="utf-8"))
        else:
            vision = analyze_video_models(
                source,
                cache_dir / f"{participant}_artifacts",
                model_dir,
                case_id=f"rehab26_{participant}",
                sample_fps=sample_fps,
                write_video=False,
                frame_ranges=annotated_ranges,
            )
            cache.write_text(
                json.dumps(vision, ensure_ascii=False), encoding="utf-8"
            )

        baseline = analyze_video(
            source,
            cache_dir / f"{participant}_baseline.mp4",
            f"rehab26_{participant}",
            thresholds=None,
            save_video=False,
            frame_ranges=annotated_ranges,
            sample_fps=sample_fps,
        )
        participant_rows = repetition_rows_for_participant(
            participant, annotations, vision["frames_data"], baseline, baseline["fps"]
        )
        all_rows.extend(participant_rows)
        inference_summary[participant] = {
            "sample_fps": vision["sample_fps"],
            "sampled_frames": vision["sampled_frames"],
            "pose_frames": vision["pose_frames"],
            "elapsed_s": vision["elapsed_s"],
            "inference_latency_ms": vision["inference_latency_ms"],
            "object_classes": vision["objects_by_class"],
            "repetitions": len(participant_rows),
        }
        print(f"Processed {participant}: {len(participant_rows)} annotated repetitions")

    folds = [evaluate_fold(participant, all_rows) for participant in PARTICIPANTS]
    f1_values = [fold["openpose_yolo_macro_f1"] for fold in folds if fold["openpose_yolo_macro_f1"] is not None]
    binary_new = [fold["openpose_yolo_binary"].get("f1") for fold in folds if "f1" in fold["openpose_yolo_binary"]]
    binary_baseline = [fold["mediapipe_binary"].get("f1") for fold in folds if "f1" in fold["mediapipe_binary"]]
    result = {
        "dataset": "REHAB26-ViewAngles, exercise 1 (arm abduction)",
        "participants": list(PARTICIPANTS),
        "evaluation": "5-fold leave-one-participant-out; thresholds fit on four training participants only",
        "sample_fps": sample_fps,
        "repetitions": len(all_rows),
        "error_types": list(ERROR_FEATURES),
        "folds": folds,
        "aggregate": {
            "openpose_yolo_macro_f1_mean": round(statistics.mean(f1_values), 4) if f1_values else None,
            "openpose_yolo_binary_f1_mean": round(statistics.mean(binary_new), 4) if binary_new else None,
            "mediapipe_binary_f1_mean": round(statistics.mean(binary_baseline), 4) if binary_baseline else None,
            "openpose_yolo_binary_micro": aggregate_confusion_metrics(
                [fold["openpose_yolo_binary"] for fold in folds], len(all_rows)
            ),
            "mediapipe_binary_micro": aggregate_confusion_metrics(
                [fold["mediapipe_binary"] for fold in folds], len(all_rows)
            ),
            "per_error_type_micro": {
                code: aggregate_confusion_metrics(
                    [fold["per_error_type"][code] for fold in folds], len(all_rows)
                )
                for code in ERROR_FEATURES
            },
        },
        "inference": inference_summary,
        "limitations": [
            "Volunteer demonstrations in controlled settings, not hospitalized patients.",
            "OpenPose COCO points are two-dimensional; arm-forward is represented by a limited lateral-projection proxy.",
            "YOLOv8 uses general pretrained object classes and is not trained to identify clinical critical regions.",
            "Thresholds and alerts are experimental; no clinical validity is claimed.",
        ],
    }
    output = PROJECT_ROOT / "docs" / "resultados" / "rehab26_lopo.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample-fps",
        type=float,
        default=0.5,
        help="Inference sampling rate; annotated repetitions span several seconds.",
    )
    parser.add_argument("--force", action="store_true", help="Recompute pose features instead of using local cache.")
    args = parser.parse_args()
    result = evaluate(args.sample_fps, args.force)
    print(json.dumps(result["aggregate"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

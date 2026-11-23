import json
import sys
from pathlib import Path

import pytest


CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_DIR / "src"))
sys.path.insert(0, str(CODE_DIR / "scripts"))

from evaluate_rehab26 import (
    aggregate_confusion_metrics,
    confusion_metrics,
    fit_threshold,
    threshold_prediction,
)
from fisio_fase4.replay import replay_events
from fisio_fase4.vision_models import aggregate_repetition_features
from summarize_public_consultations import summarize


def test_aggregate_repetition_features_uses_only_frames_in_window():
    records = [
        {
            "frame_index": frame,
            "features": {
                "arm_angle": angle,
                "elbow_angle": 160.0,
                "shoulder_elevation_ratio": 0.02,
                "head_tilt_deg": 3.0,
                "arm_lateral_ratio": 0.7,
                "pose_confidence": 0.9,
            },
        }
        for frame, angle in ((10, 25.0), (20, 80.0), (30, 120.0))
    ]

    result = aggregate_repetition_features(records, 15, 25)

    assert result["pose_status"] == "inconclusivo"
    assert result["sample_count"] == 1
    assert result["max_arm_angle"] == 80.0


def test_aggregate_repetition_features_marks_missing_pose_inconclusive():
    result = aggregate_repetition_features([], 0, 100)

    assert result == {"pose_status": "inconclusivo", "sample_count": 0}


def test_development_threshold_separates_labeled_examples():
    development_rows = [
        {"target": True, "features": {"amplitude": 20.0}},
        {"target": True, "features": {"amplitude": 30.0}},
        {"target": False, "features": {"amplitude": 100.0}},
        {"target": False, "features": {"amplitude": 110.0}},
    ]

    threshold = fit_threshold(development_rows, "amplitude", "lt")

    assert threshold == 65.0
    assert threshold_prediction(30.0, threshold, "lt") is True
    assert threshold_prediction(100.0, threshold, "lt") is False
    assert confusion_metrics([True, False], [True, False])["f1"] == 1.0


def test_aggregate_metrics_combine_counts_and_track_coverage():
    result = aggregate_confusion_metrics(
        [
            {"tp": 2, "fp": 1, "fn": 1, "tn": 3, "evaluated": 7},
            {"tp": 1, "fp": 0, "fn": 2, "tn": 4, "evaluated": 7},
        ],
        total_repetitions=20,
    )

    assert result == {
        "evaluated": 14,
        "coverage": 0.7,
        "tp": 3,
        "fp": 1,
        "fn": 3,
        "tn": 7,
        "precision": 0.75,
        "recall": 0.5,
        "f1": 0.6,
    }


def test_replay_emits_events_in_time_order_and_writes_trace(tmp_path):
    trace = tmp_path / "replay.jsonl"
    events = [
        {"event_id": "later", "time_s": 0.001, "evidence": "second"},
        {"event_id": "first", "time_s": 0.0, "evidence": "first"},
    ]
    observed = []

    summary, records = replay_events(
        events, speed=1000, output_path=trace, on_event=observed.append
    )

    assert [record["event"]["event_id"] for record in records] == ["first", "later"]
    assert observed == records
    assert summary["events_expected"] == summary["events_delivered"] == 2
    assert summary["median_delivery_latency_ms"] < 100
    assert [
        json.loads(line)["event"]["event_id"] for line in trace.read_text().splitlines()
    ] == ["first", "later"]


def test_replay_rejects_duplicate_event_ids():
    duplicate_events = [
        {"event_id": "same", "time_s": 0.0},
        {"event_id": "same", "time_s": 0.001},
    ]

    with pytest.raises(ValueError, match="Duplicate event id"):
        replay_events(duplicate_events, speed=1000)


def test_public_consultation_summary_does_not_retain_transcript(tmp_path):
    report = tmp_path / "private_report.json"
    report.write_text(
        json.dumps(
            {
                "modalities": {
                    "audio": {
                        "status": "ok",
                        "elapsed_s": 2.5,
                        "result": {
                            "transcription": {
                                "text": "conteúdo de áudio que deve permanecer local",
                                "language": "pt",
                                "segments": [{"text": "conteúdo privado"}],
                            },
                            "acoustics": {"duration_s": 10.0},
                        },
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    summary = summarize(
        {
            "id": "test",
            "title": "source",
            "url": "https://example.org/source",
            "report": report,
        }
    )

    serialized = json.dumps(summary, ensure_ascii=False)
    assert "conteúdo de áudio" not in serialized
    assert "conteúdo privado" not in serialized
    assert summary["transcribed_word_count"] == 7
    assert summary["transcript_included"] is False
    assert summary["manual_reference_available"] is False

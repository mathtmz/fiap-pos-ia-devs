"""Replay precomputed multimodal events at the source timeline rate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys

CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_DIR / "src"))
from fisio_fase4.replay import replay_events


def replay(report_path, speed=1.0, output_path=None, on_event=None):
    report_path = Path(report_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    summary, records = replay_events(
        report.get("events", []), speed, output_path, on_event
    )
    summary["report"] = report_path.name
    return summary, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "outputs/stream/replay.jsonl",
    )
    args = parser.parse_args()
    summary, records = replay(args.report, args.speed, args.output)
    for record in records:
        print(json.dumps(record, ensure_ascii=False), flush=True)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

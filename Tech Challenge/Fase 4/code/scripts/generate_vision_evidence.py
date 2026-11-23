"""Generate compact annotated examples for the report and presentation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
sys.path.insert(0, str(CODE_DIR / "src"))

from fisio_fase4.vision_models import analyze_video_models


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-fps", type=float, default=5.0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    input_dir = PROJECT_ROOT / "data/public/rehab26/demo_clips"
    manifest_path = input_dir / "manifest.json"
    if not manifest_path.exists():
        parser.error("Run scripts/prepare_rehab26_examples.py first.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    weights_dir = PROJECT_ROOT / "data/public/modelos/openpose"
    output_root = PROJECT_ROOT / "docs/resultados/vision_examples"
    output_root.mkdir(parents=True, exist_ok=True)
    summaries = []
    for item in manifest:
        label = Path(item["clip"]).stem
        source = input_dir / item["clip"]
        destination = output_root / label
        summary_path = destination / "resumo.json"
        video_path = destination / "openpose_yolo_temporal.mp4"
        if summary_path.exists() and video_path.exists() and not args.force:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        else:
            result = analyze_video_models(
                source,
                destination,
                weights_dir,
                case_id=f"rehab26_demo_{label}",
                sample_fps=args.sample_fps,
                write_video=True,
            )
            summary = {
                key: value
                for key, value in result.items()
                if key != "frames_data"
            }
            summary.update(
                {
                    "demonstration_label": label,
                    "ground_truth_error": item["error"],
                    "ground_truth_additional_errors": item["additional_errors"],
                    "source_video": item["video_id"],
                    "source_frames": item["source_frames"],
                    "source_url": item["source_url"],
                }
            )
            summary_path.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        summaries.append(
            {
                "label": label,
                "ground_truth_error": item["error"],
                "video": str(video_path.relative_to(PROJECT_ROOT)),
                "summary": str(summary_path.relative_to(PROJECT_ROOT)),
                "events": len(summary.get("events", [])),
            }
        )
        print(json.dumps(summaries[-1], ensure_ascii=False), flush=True)
    index = output_root / "indice.json"
    index.write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Evidence index: {index}")


if __name__ == "__main__":
    main()

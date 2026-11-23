"""Create short, local demo clips from annotated REHAB26 repetitions."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg


CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
VIDEO_DIR = PROJECT_ROOT / "data/public/rehab26/videos"
ANNOTATIONS = PROJECT_ROOT / "data/public/rehab26/Segmentation.csv"
OUTPUT_DIR = PROJECT_ROOT / "data/public/rehab26/demo_clips"
CLASS_NAMES = {
    "ERR_ARM_FORWARD": "arm_forward",
    "ERR_ELEVATED_SHOULDER": "shoulder_elevated",
    "ERR_HEAD_TO_SIDE": "head_tilt",
    "ERR_LOW_ABDUCTION": "low_abduction",
    "ERR_BENT_ARM": "bent_arm",
}


def load_rows(participant):
    with ANNOTATIONS.open(encoding="utf-8-sig", newline="") as file:
        return [
            row
            for row in csv.DictReader(file, delimiter=";")
            if row["exercise_id"] == "1" and row["person"] == participant
        ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--participant", choices=["Honza", "Mima", "Petra", "Terka", "Vasil"], default="Petra")
    parser.add_argument("--fps", type=float, default=30.0)
    args = parser.parse_args()
    source = VIDEO_DIR / f"ex1_{args.participant}_cam1.mp4"
    if not source.exists():
        parser.error(
            f"Missing {source.name}; run download_consultas_rehab26.py --video --participants {args.participant}."
        )
    rows = load_rows(args.participant)
    examples = {}
    correct = next((row for row in rows if row["correctness_score"] == "1"), None)
    if correct:
        examples["normal"] = correct
    for row in rows:
        codes = {
            code.strip()
            for raw in (row["error_description"], row["additional_errors"])
            if raw
            for code in raw.split(",")
            if code.strip()
        }
        for code, label in CLASS_NAMES.items():
            if code in codes and label not in examples:
                examples[label] = row

    missing = set(["normal", *CLASS_NAMES.values()]).difference(examples)
    if missing:
        parser.error("No annotated clip found for: " + ", ".join(sorted(missing)))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    manifest = []
    for label, row in examples.items():
        first = int(row["first_frame"])
        last = int(row["last_frame"])
        start_frame = max(0, first - 15)
        end_frame = last + 15
        target = OUTPUT_DIR / f"{label}.mp4"
        command = [
            ffmpeg,
            "-y",
            "-ss",
            f"{start_frame / args.fps:.3f}",
            "-i",
            str(source),
            "-t",
            f"{(end_frame - start_frame + 1) / args.fps:.3f}",
            "-an",
            "-vf",
            "scale=640:-2",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "27",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(target),
        ]
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        manifest.append(
            {
                "clip": target.name,
                "participant": args.participant,
                "video_id": row["video_id"],
                "repetition": int(row["repetition_number"]),
                "source_frames": [first, last],
                "source_url": "https://zenodo.org/records/23018128",
                "error": row["error_description"] or None,
                "additional_errors": row["additional_errors"] or None,
                "correctness_score": int(row["correctness_score"]),
            }
        )
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created {len(manifest)} local demonstration clips in {OUTPUT_DIR}")
    print(f"Clip manifest: {manifest_path}")


if __name__ == "__main__":
    main()

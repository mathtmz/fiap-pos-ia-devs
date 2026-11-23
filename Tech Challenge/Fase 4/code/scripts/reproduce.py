"""Run the documented quick or complete reproduction workflow."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "docs/resultados"


def run(command, label):
    print(f"\n=== {label} ===", flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def copy_report(source, target):
    source = Path(source)
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def quick_reproduction(python):
    run([python, "code/scripts/check_environment.py"], "Environment check")
    run([python, "-m", "pytest", "code/tests", "-q"], "Automated tests")
    output_root = CODE_DIR / "outputs/reproduction/quick"
    normal = output_root / "normal"
    anomaly = output_root / "anomaly"
    run(
        [python, "code/scripts/run_demo.py", "--normal", "--no-qwen", "--output", str(normal)],
        "Synthetic normal case",
    )
    run(
        [python, "code/scripts/run_demo.py", "--no-qwen", "--output", str(anomaly)],
        "Synthetic anomaly case",
    )
    copy_report(normal / "relatorio.json", RESULTS_DIR / "reproduction_quick_normal.json")
    copy_report(anomaly / "relatorio.json", RESULTS_DIR / "reproduction_quick_anomaly.json")


def full_reproduction(python, sample_fps):
    run(
        [
            python,
            "code/scripts/download_consultas_rehab26.py",
            "--video",
            "--participants",
            "all",
        ],
        "Download public data and REHAB26 exercise 1 clips (~0.92 GiB)",
    )
    run([python, "code/scripts/setup_vision_models.py"], "Get OpenPose model files")
    run([python, "code/scripts/compare_whisper.py"], "Whisper WER, runtime and memory comparison")
    oaw04_audio = PROJECT_ROOT / "data/public/consultas/OAW04_consultation.wav"
    run(
        [
            python,
            "code/scripts/run_demo.py",
            "--audio",
            str(oaw04_audio),
            "--normal",
            "--diarize",
            "--output",
            "code/outputs/diarizacao_experimental",
            "--case-id",
            "oaw04_diarizacao",
        ],
        "Synthetic speaker grouping with human-unassigned roles",
    )
    run([python, "code/scripts/evaluate_diarization.py"], "Exploratory diarization comparison")
    run([python, "code/scripts/evaluate_vad.py"], "Whisper VAD comparison on the same reference")
    run([python, "code/scripts/evaluate_text.py"], "Qwen fixed synthetic evaluation set")
    run(
        [python, "code/scripts/evaluate_rehab26.py", "--sample-fps", str(sample_fps)],
        "REHAB26 leave-one-participant-out evaluation",
    )
    run([python, "code/scripts/prepare_rehab26_examples.py"], "Prepare short source-linked demo clips")
    run(
        [python, "code/scripts/generate_vision_evidence.py", "--sample-fps", "5"],
        "Generate compact annotated visual evidence",
    )
    run(
        [python, "code/scripts/prepare_audio_demo.py"],
        "Prepare synthetic audio demonstration",
    )

    output_root = CODE_DIR / "outputs/reproduction/full"
    normal = output_root / "normal"
    anomaly = output_root / "anomaly"
    run(
        [python, "code/scripts/run_demo.py", "--normal", "--no-qwen", "--output", str(normal)],
        "Normal synthetic-data case",
    )
    example_video = PROJECT_ROOT / "data/public/rehab26/demo_clips/low_abduction.mp4"
    example_audio = PROJECT_ROOT / "data/public/consultas/OAW04_consultation.wav"
    run(
        [
            python,
            "code/scripts/run_demo.py",
            "--video",
            str(example_video),
            "--audio",
            str(example_audio),
            "--vision-fps",
            str(sample_fps),
            "--output",
            str(anomaly),
            "--case-id",
            "caso_demo_sintetico",
        ],
        "Integrated synthetic multimodal anomaly case",
    )
    copy_report(normal / "relatorio.json", RESULTS_DIR / "reproduction_normal_case.json")
    anomaly_report = RESULTS_DIR / "reproduction_anomaly_case.json"
    copy_report(anomaly / "relatorio.json", anomaly_report)
    run(
        [
            python,
            "code/scripts/replay_multimodal.py",
            str(anomaly_report),
            "--speed",
            "1",
            "--output",
            str(RESULTS_DIR / "replay_anomaly.jsonl"),
        ],
        "Synchronized local alert replay at 1x",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--quick", action="store_true", help="Run offline setup checks, tests and synthetic cases.")
    mode.add_argument("--full", action="store_true", help="Download external inputs and run all experiments.")
    parser.add_argument(
        "--accept-external-downloads",
        action="store_true",
        help="Required with --full; acknowledges approximately 0.92 GiB of source video downloads plus model weights.",
    )
    parser.add_argument("--sample-fps", type=float, default=0.5)
    args = parser.parse_args()
    python = sys.executable
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if args.quick:
        quick_reproduction(python)
    else:
        if not args.accept_external_downloads:
            parser.error("--full downloads external video. Add --accept-external-downloads to continue.")
        full_reproduction(python, args.sample_fps)
    print("\nReproduction workflow completed.")


if __name__ == "__main__":
    main()

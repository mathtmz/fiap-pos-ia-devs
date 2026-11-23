"""Prepare the lightweight demo artifacts used in the 15-minute recording."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
OUTPUT_DIR = CODE_DIR / "outputs/recording"
RESULTS_DIR = PROJECT_ROOT / "docs/resultados"


def run(label: str, command: list[str], *, quiet: bool = False) -> None:
    print(f"\n[{label}]", flush=True)
    subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
        stdout=subprocess.DEVNULL if quiet else None,
    )


def summary(path: Path) -> tuple[int, int, float]:
    report = json.loads(path.read_text(encoding="utf-8"))
    return (
        len(report.get("events", [])),
        len(report.get("alerts", [])),
        float(report.get("processing_elapsed_s", 0.0)),
    )


def prepare(python: str, app_port: int) -> None:
    normal_dir = OUTPUT_DIR / "normal"
    anomaly_dir = OUTPUT_DIR / "anomaly"
    replay_path = OUTPUT_DIR / "integrated_replay.jsonl"
    integrated_report = RESULTS_DIR / "reproduction_anomaly_case.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    run("Verificando o ambiente", [python, "code/scripts/check_environment.py"])
    run(
        "Gerando o cenário normal com dados sintéticos",
        [
            python,
            "code/scripts/run_demo.py",
            "--normal",
            "--no-qwen",
            "--output",
            str(normal_dir),
            "--case-id",
            "caso_normal_gravacao",
        ],
    )
    run(
        "Gerando o cenário anômalo com dados sintéticos",
        [
            python,
            "code/scripts/run_demo.py",
            "--no-qwen",
            "--output",
            str(anomaly_dir),
            "--case-id",
            "caso_anomalo_gravacao",
        ],
    )
    run(
        "Preparando a reprodução integrada de eventos pré-calculados",
        [
            python,
            "code/scripts/replay_multimodal.py",
            str(integrated_report),
            "--speed",
            "12",
            "--output",
            str(replay_path),
        ],
        quiet=True,
    )

    normal = summary(normal_dir / "relatorio.json")
    anomaly = summary(anomaly_dir / "relatorio.json")
    integrated = json.loads(integrated_report.read_text(encoding="utf-8"))
    print("\nRESUMO PARA A GRAVAÇÃO")
    print(f"Normal: {normal[0]} eventos, {normal[1]} alertas")
    print(f"Anômalo: {anomaly[0]} eventos, {anomaly[1]} alertas")
    print(
        "Integrado versionado: "
        f"{len(integrated.get('events', []))} eventos, "
        f"{len(integrated.get('alerts', []))} alertas"
    )
    print(f"Relatórios da execução: {OUTPUT_DIR}")
    print(f"JSON integrado: {integrated_report}")
    print(f"Vídeo anotado: {RESULTS_DIR / 'vision_examples/low_abduction/openpose_yolo_temporal.mp4'}")
    print(f"Interface: http://localhost:{app_port}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--launch-app",
        action="store_true",
        help="Open Streamlit after the preparation steps finish.",
    )
    parser.add_argument("--app-port", type=int, default=8501)
    args = parser.parse_args()

    python = sys.executable
    prepare(python, args.app_port)
    if args.launch_app:
        run(
            "Abrindo a interface Streamlit",
            [
                python,
                "-m",
                "streamlit",
                "run",
                "code/app.py",
                "--server.port",
                str(args.app_port),
            ],
        )


if __name__ == "__main__":
    main()

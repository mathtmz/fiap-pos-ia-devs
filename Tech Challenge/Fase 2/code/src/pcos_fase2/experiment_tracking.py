from __future__ import annotations

import json
import numbers
from pathlib import Path
from typing import Any

import mlflow

from .config import MLRUNS_DIR


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def log_run_to_mlflow(
    experiment_name: str,
    run_name: str,
    params: dict[str, Any],
    metrics: dict[str, Any],
    artifact_paths: list[Path] | None = None,
    tracking_dir: Path = MLRUNS_DIR,
) -> None:
    """Registra parametros, metricas e artefatos de um job no MLflow, com
    backend em arquivo local (sem servidor, sem dependencia de nuvem).
    """
    tracking_dir.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"file:{tracking_dir}")
    mlflow.set_experiment(experiment_name)

    numeric_metrics = {
        key: float(value) for key, value in metrics.items() if isinstance(value, numbers.Number)
    }

    with mlflow.start_run(run_name=run_name):
        mlflow.log_params(params)
        if numeric_metrics:
            mlflow.log_metrics(numeric_metrics)
        for artifact_path in artifact_paths or []:
            if artifact_path.exists():
                mlflow.log_artifact(str(artifact_path))

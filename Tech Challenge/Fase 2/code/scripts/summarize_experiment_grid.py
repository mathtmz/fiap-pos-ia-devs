from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_CODE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_CODE_DIR / "outputs" / ".matplotlib"))
sys.path.insert(0, str(PROJECT_CODE_DIR / "src"))

import pandas as pd

from pcos_fase2.config import METRICS_DIR, ensure_output_dirs
from pcos_fase2.experiment_tracking import write_json


JOB_DIR = METRICS_DIR / "ga_jobs"


def main() -> None:
    ensure_output_dirs()
    rows = []
    for path in sorted(JOB_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        metrics = payload.get("validation_metrics", {})
        config = payload.get("config", {})
        rows.append(
            {
                "experiment": payload.get("experiment"),
                "status": payload.get("status"),
                "elapsed_seconds": payload.get("elapsed_seconds"),
                "best_fitness": payload.get("best_fitness"),
                "recall_pos": metrics.get("recall_pos"),
                "f1_pos": metrics.get("f1_pos"),
                "auc_roc": metrics.get("auc_roc"),
                "accuracy": metrics.get("accuracy"),
                "population_size": config.get("population_size"),
                "generations": config.get("generations"),
                "mutation_rate": config.get("mutation_rate"),
                "crossover_rate": config.get("crossover_rate"),
                "best_genes": json.dumps(payload.get("best_genes", {}), sort_keys=True),
            }
        )

    if not rows:
        raise FileNotFoundError(f"Nenhum resumo de job encontrado em {JOB_DIR}")

    frame = pd.DataFrame(rows).sort_values(
        ["status", "best_fitness", "f1_pos"],
        ascending=[False, False, False],
    )
    output_csv = METRICS_DIR / "ga_job_summary.csv"
    output_json = METRICS_DIR / "ga_job_summary.json"
    frame.to_csv(output_csv, index=False)
    write_json(output_json, {"jobs": rows})

    print(frame.to_string(index=False))
    print(f"\nResumo salvo em: {output_csv}")


if __name__ == "__main__":
    main()

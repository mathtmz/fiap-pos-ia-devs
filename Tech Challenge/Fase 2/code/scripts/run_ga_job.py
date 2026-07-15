from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_CODE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_CODE_DIR / "outputs" / ".matplotlib"))
sys.path.insert(0, str(PROJECT_CODE_DIR / "src"))

from pcos_fase2.config import METRICS_DIR, ensure_output_dirs
from pcos_fase2.data import prepare_data
from pcos_fase2.experiment_tracking import log_run_to_mlflow, write_json
from pcos_fase2.genetic_optimizer import GeneticExperimentConfig, run_genetic_experiment
from pcos_fase2.logging_setup import configure_logging


JOB_DIR = METRICS_DIR / "ga_jobs"
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa um job de algoritmo genetico com parametros informados."
    )
    parser.add_argument("--name", required=True, help="Nome do experimento.")
    parser.add_argument("--population-size", type=int, required=True)
    parser.add_argument("--generations", type=int, required=True)
    parser.add_argument("--mutation-rate", type=float, required=True)
    parser.add_argument("--crossover-rate", type=float, required=True)
    parser.add_argument("--elitism-rate", type=float, default=0.10)
    parser.add_argument("--tournament-size", type=int, default=3)
    parser.add_argument("--patience", type=int, default=8)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def run_job(params: dict[str, Any]) -> dict[str, Any]:
    configure_logging()
    ensure_output_dirs()
    JOB_DIR.mkdir(parents=True, exist_ok=True)

    config = GeneticExperimentConfig(
        name=params["name"],
        population_size=int(params["population_size"]),
        generations=int(params["generations"]),
        mutation_rate=float(params["mutation_rate"]),
        crossover_rate=float(params["crossover_rate"]),
        elitism_rate=float(params.get("elitism_rate", 0.10)),
        tournament_size=int(params.get("tournament_size", 3)),
        patience=int(params.get("patience", 8)),
    )

    logger.info("Iniciando job de GA '%s'.", config.name)
    started = time.perf_counter()
    summary_path = JOB_DIR / f"{config.name}.json"
    log_path = JOB_DIR / f"{config.name}.jsonl"

    try:
        prepared = prepare_data()
        result = run_genetic_experiment(
            prepared,
            model_family="random_forest",
            config=config,
            log_path=log_path,
            random_state=int(params.get("random_state", 42)),
        )
        best = result.best_individual
        job_config = {
            "population_size": config.population_size,
            "generations": config.generations,
            "mutation_rate": config.mutation_rate,
            "crossover_rate": config.crossover_rate,
            "elitism_rate": config.elitism_rate,
            "tournament_size": config.tournament_size,
            "patience": config.patience,
        }
        payload = {
            "status": "success",
            "experiment": config.name,
            "config": job_config,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "best_fitness": best.fitness,
            "best_genes": best.genes,
            "validation_metrics": best.validation_metrics.as_dict(),
            "log_path": str(log_path.relative_to(PROJECT_CODE_DIR)),
        }
        log_run_to_mlflow(
            experiment_name="ga_jobs",
            run_name=config.name,
            params=job_config,
            metrics={"best_fitness": best.fitness, **best.validation_metrics.as_dict()},
            artifact_paths=[log_path],
        )
        logger.info(
            "Job de GA '%s' concluido em %.2fs (fitness=%.4f).",
            config.name,
            payload["elapsed_seconds"],
            best.fitness,
        )
    except Exception as error:
        payload = {
            "status": "error",
            "experiment": config.name,
            "config": params,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "error": str(error),
        }
        logger.error("Job de GA '%s' falhou: %s", config.name, error)

    write_json(summary_path, payload)
    return payload


def main() -> None:
    args = parse_args()
    payload = run_job(
        {
            "name": args.name,
            "population_size": args.population_size,
            "generations": args.generations,
            "mutation_rate": args.mutation_rate,
            "crossover_rate": args.crossover_rate,
            "elitism_rate": args.elitism_rate,
            "tournament_size": args.tournament_size,
            "patience": args.patience,
            "random_state": args.random_state,
        }
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

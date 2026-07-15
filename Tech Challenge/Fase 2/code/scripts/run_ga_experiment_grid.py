from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_CODE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_CODE_DIR / "outputs" / ".matplotlib"))
sys.path.insert(0, str(PROJECT_CODE_DIR / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pcos_fase2.config import ensure_output_dirs
from pcos_fase2.logging_setup import configure_logging
from pcos_fase2.scaling import auto_worker_count
from run_ga_job import run_job

logger = logging.getLogger(__name__)


FULL_GRID = [
    {"name": "job_exploratorio", "population_size": 20, "generations": 20, "mutation_rate": 0.25, "crossover_rate": 0.80},
    {"name": "job_balanceado", "population_size": 30, "generations": 30, "mutation_rate": 0.15, "crossover_rate": 0.75},
    {"name": "job_conservador", "population_size": 20, "generations": 40, "mutation_rate": 0.08, "crossover_rate": 0.65},
    {"name": "job_mutacao_alta", "population_size": 24, "generations": 24, "mutation_rate": 0.30, "crossover_rate": 0.70},
]

QUICK_GRID = [
    {"name": "job_validacao_a", "population_size": 6, "generations": 2, "mutation_rate": 0.10, "crossover_rate": 0.70},
    {"name": "job_validacao_b", "population_size": 6, "generations": 2, "mutation_rate": 0.25, "crossover_rate": 0.80},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa uma grade de experimentos de GA em paralelo local."
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help=(
            "Numero de workers. Se omitido, e calculado automaticamente a partir "
            "da quantidade de jobs pendentes e dos nucleos de CPU disponiveis "
            "(equivalente ao escalonamento automatico de um compute cluster)."
        ),
    )
    parser.add_argument("--backend", choices=["thread", "process"], default="thread")
    parser.add_argument("--quick", action="store_true", help="Executa uma grade pequena para validacao rapida.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging()
    ensure_output_dirs()
    grid = QUICK_GRID if args.quick else FULL_GRID

    worker_count = args.workers if args.workers is not None else auto_worker_count(len(grid))
    logger.info(
        "Grade de %s job(s) sera executada com %s worker(s) (%s).",
        len(grid),
        worker_count,
        "definido manualmente" if args.workers is not None else "dimensionado automaticamente",
    )

    results = []
    executor_class = ThreadPoolExecutor if args.backend == "thread" else ProcessPoolExecutor
    with executor_class(max_workers=worker_count) as executor:
        futures = [executor.submit(run_job, params) for params in grid]
        for future in as_completed(futures):
            payload = future.result()
            results.append(payload)
            logger.info("Job %s finalizado com status=%s.", payload.get("experiment"), payload.get("status"))
            print(json.dumps(payload, ensure_ascii=False))

    errors = [item for item in results if item.get("status") != "success"]
    if errors:
        logger.error("%s job(s) terminaram com erro.", len(errors))
        raise SystemExit(f"{len(errors)} job(s) terminaram com erro.")


if __name__ == "__main__":
    main()

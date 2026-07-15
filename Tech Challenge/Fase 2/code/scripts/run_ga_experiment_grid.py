from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_CODE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_CODE_DIR / "outputs" / ".matplotlib"))
sys.path.insert(0, str(PROJECT_CODE_DIR / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pcos_fase2.config import ensure_output_dirs
from run_ga_job import run_job


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
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--backend", choices=["thread", "process"], default="thread")
    parser.add_argument("--quick", action="store_true", help="Executa uma grade pequena para validacao rapida.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_output_dirs()
    grid = QUICK_GRID if args.quick else FULL_GRID

    results = []
    executor_class = ThreadPoolExecutor if args.backend == "thread" else ProcessPoolExecutor
    with executor_class(max_workers=args.workers) as executor:
        futures = [executor.submit(run_job, params) for params in grid]
        for future in as_completed(futures):
            payload = future.result()
            results.append(payload)
            print(json.dumps(payload, ensure_ascii=False))

    errors = [item for item in results if item.get("status") != "success"]
    if errors:
        raise SystemExit(f"{len(errors)} job(s) terminaram com erro.")


if __name__ == "__main__":
    main()

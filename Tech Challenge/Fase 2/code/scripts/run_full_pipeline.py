from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_CODE_DIR = Path(__file__).resolve().parents[1]


def run_step(command: list[str], env: dict[str, str] | None = None) -> None:
    merged_env = os.environ.copy()
    merged_env.setdefault("LLM_PROVIDER", "mock")
    if env:
        merged_env.update(env)
    print(f"\n$ {' '.join(command)}")
    subprocess.run(command, cwd=PROJECT_CODE_DIR, env=merged_env, check=True)


def main() -> None:
    python = sys.executable
    run_step([python, "scripts/run_baseline.py"])
    run_step([python, "scripts/run_ga_experiments.py"])
    run_step([python, "scripts/run_ga_experiment_grid.py", "--workers", "2", "--quick"])
    run_step([python, "scripts/summarize_experiment_grid.py"])
    run_step([python, "scripts/run_advanced_tuning.py"])
    run_step([python, "scripts/finalize_ga_results.py"])
    run_step([python, "scripts/generate_llm_report.py"], env={"LLM_PROVIDER": "mock"})


if __name__ == "__main__":
    main()

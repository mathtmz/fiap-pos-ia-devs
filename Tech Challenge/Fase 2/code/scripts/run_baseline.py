from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

PROJECT_CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_CODE_DIR / "src"))

from pcos_fase2.config import METRICS_DIR, ensure_output_dirs
from pcos_fase2.data import prepare_data
from pcos_fase2.evaluation import metrics_to_frame
from pcos_fase2.logging_setup import configure_logging
from pcos_fase2.models import train_baselines

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()
    ensure_output_dirs()
    logger.info("Iniciando treinamento dos modelos baseline.")

    prepared = prepare_data()
    _, metrics = train_baselines(prepared)

    frame = metrics_to_frame(metrics)
    output_path = METRICS_DIR / "baseline_metrics.csv"
    frame.to_csv(output_path)

    display_frame = frame.drop(columns=["confusion_matrix"]).copy()
    print("\n=== Baselines Fase 2 ===")
    print((display_frame * 100).round(2).to_string())
    print(f"\nMetricas salvas em: {output_path}")
    logger.info("Treinamento dos modelos baseline concluido. Metricas salvas em %s.", output_path)


if __name__ == "__main__":
    main()

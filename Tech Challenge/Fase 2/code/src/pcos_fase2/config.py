from __future__ import annotations

from pathlib import Path


RANDOM_STATE = 42
TARGET_COLUMN = "PCOS (Y/N)"
POSITIVE_LABEL = 1

PACKAGE_DIR = Path(__file__).resolve().parent
CODE_DIR = PACKAGE_DIR.parents[1]
FASE2_DIR = CODE_DIR.parent
DATA_DIR = FASE2_DIR / "data"
OUTPUT_DIR = CODE_DIR / "outputs"
METRICS_DIR = OUTPUT_DIR / "metrics"
MODELS_DIR = OUTPUT_DIR / "models"
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORTS_DIR = OUTPUT_DIR / "reports"

EXCEL_PATH = DATA_DIR / "PCOS_data_without_infertility.xlsx"

GENERATED_FEATURES = [
    "total_foliculos",
    "soma_sintomas",
    "faixa_imc",
    "razao_lh_fsh",
]

BASELINE_MODELS = [
    "Regressao Logistica",
    "Arvore de Decisao",
    "Random Forest",
    "KNN",
]


def ensure_output_dirs() -> None:
    """Cria as pastas de saida usadas pelos scripts da Fase 2."""
    for path in [METRICS_DIR, MODELS_DIR, FIGURES_DIR, REPORTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)

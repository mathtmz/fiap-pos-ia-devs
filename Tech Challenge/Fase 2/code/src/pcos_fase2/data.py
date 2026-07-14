from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from .config import EXCEL_PATH, RANDOM_STATE, TARGET_COLUMN


@dataclass
class PreparedData:
    x_train: pd.DataFrame
    x_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    x_train_scaled: np.ndarray
    x_test_scaled: np.ndarray
    scaler: StandardScaler
    feature_names: list[str]
    removed_features: list[str]
    full_dataset: pd.DataFrame


def load_raw_data(excel_path: Path = EXCEL_PATH) -> pd.DataFrame:
    """Carrega o Excel principal, que ja contem as colunas clinicas usadas na Fase 1."""
    if not excel_path.exists():
        raise FileNotFoundError(f"Arquivo de dados nao encontrado: {excel_path}")
    return pd.read_excel(excel_path, sheet_name="Full_new")


def clean_dataset(raw_data: pd.DataFrame) -> pd.DataFrame:
    data = raw_data.copy()

    columns_to_drop = ["Sl. No", "Patient File No.", "Unnamed: 44"]
    data = data.drop(columns=[col for col in columns_to_drop if col in data.columns])

    # Algumas colunas hormonais chegam como texto por erro de digitacao no dataset.
    for column in ["AMH(ng/mL)", "II    beta-HCG(mIU/mL)"]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    text_columns = data.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        encoder = LabelEncoder()
        data[column] = encoder.fit_transform(data[column].astype(str))

    return fill_missing_with_median(data)


def fill_missing_with_median(data: pd.DataFrame) -> pd.DataFrame:
    cleaned = data.copy()
    numeric_columns = cleaned.select_dtypes(include=[np.number]).columns
    for column in numeric_columns:
        if cleaned[column].isna().any():
            cleaned[column] = cleaned[column].fillna(cleaned[column].median())
    return cleaned


def add_clinical_features(data: pd.DataFrame) -> pd.DataFrame:
    enriched = data.copy()

    enriched["total_foliculos"] = (
        enriched["Follicle No. (L)"] + enriched["Follicle No. (R)"]
    )

    symptom_columns = [
        "Weight gain(Y/N)",
        "hair growth(Y/N)",
        "Skin darkening (Y/N)",
        "Hair loss(Y/N)",
        "Pimples(Y/N)",
    ]
    enriched["soma_sintomas"] = enriched[symptom_columns].sum(axis=1)

    bmi_bins = [0, 18.5, 24.9, 29.9, 34.9, 100]
    bmi_labels = [0, 1, 2, 3, 4]
    enriched["faixa_imc"] = pd.cut(
        enriched["BMI"], bins=bmi_bins, labels=bmi_labels, right=True
    ).astype(float)

    enriched["razao_lh_fsh"] = enriched["LH(mIU/mL)"] / (
        enriched["FSH(mIU/mL)"] + 1e-6
    )

    return fill_missing_with_median(enriched)


def select_features_by_correlation(
    data: pd.DataFrame, threshold: float = 0.05
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    y = data[TARGET_COLUMN]
    x = data.drop(columns=[TARGET_COLUMN])

    correlations = data.corr(numeric_only=True)[TARGET_COLUMN].drop(TARGET_COLUMN)
    removed_features = correlations[correlations.abs() < threshold].index.tolist()
    x_selected = x.drop(columns=removed_features, errors="ignore")

    return x_selected, y, removed_features


def prepare_data(
    excel_path: Path = EXCEL_PATH,
    test_size: float = 0.20,
    correlation_threshold: float = 0.05,
    random_state: int = RANDOM_STATE,
) -> PreparedData:
    raw_data = load_raw_data(excel_path)
    cleaned = clean_dataset(raw_data)
    enriched = add_clinical_features(cleaned)
    x, y, removed_features = select_features_by_correlation(
        enriched, threshold=correlation_threshold
    )

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        stratify=y,
        random_state=random_state,
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    return PreparedData(
        x_train=x_train,
        x_test=x_test,
        y_train=y_train,
        y_test=y_test,
        x_train_scaled=x_train_scaled,
        x_test_scaled=x_test_scaled,
        scaler=scaler,
        feature_names=x.columns.tolist(),
        removed_features=removed_features,
        full_dataset=enriched,
    )

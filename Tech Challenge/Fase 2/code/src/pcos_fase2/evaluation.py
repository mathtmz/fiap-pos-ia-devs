from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    auc,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
)


@dataclass(frozen=True)
class ModelMetrics:
    accuracy: float
    precision_pos: float
    recall_pos: float
    f1_pos: float
    auc_roc: float
    confusion_matrix: list[list[int]]

    def as_dict(self) -> dict[str, float | list[list[int]]]:
        return {
            "accuracy": self.accuracy,
            "precision_pos": self.precision_pos,
            "recall_pos": self.recall_pos,
            "f1_pos": self.f1_pos,
            "auc_roc": self.auc_roc,
            "confusion_matrix": self.confusion_matrix,
        }


def evaluate_classifier(model, x_test, y_test) -> ModelMetrics:
    predictions = model.predict(x_test)
    probabilities = model.predict_proba(x_test)[:, 1]
    return evaluate_predictions(y_test, predictions, probabilities)


def evaluate_classifier_with_threshold(model, x_test, y_test, threshold: float) -> ModelMetrics:
    probabilities = model.predict_proba(x_test)[:, 1]
    predictions = (probabilities >= threshold).astype(int)
    return evaluate_predictions(y_test, predictions, probabilities)


def evaluate_predictions(y_test, predictions, probabilities) -> ModelMetrics:
    false_positive_rate, true_positive_rate, _ = roc_curve(y_test, probabilities)

    return ModelMetrics(
        accuracy=accuracy_score(y_test, predictions),
        precision_pos=precision_score(y_test, predictions, zero_division=0),
        recall_pos=recall_score(y_test, predictions, zero_division=0),
        f1_pos=f1_score(y_test, predictions, zero_division=0),
        auc_roc=auc(false_positive_rate, true_positive_rate),
        confusion_matrix=confusion_matrix(y_test, predictions).tolist(),
    )


def metrics_to_frame(results: dict[str, ModelMetrics]) -> pd.DataFrame:
    rows = []
    for model_name, metrics in results.items():
        row = metrics.as_dict()
        row["model"] = model_name
        rows.append(row)
    return pd.DataFrame(rows).set_index("model")


def calculate_fitness(
    validation_metrics: ModelMetrics,
    train_metrics: ModelMetrics | None = None,
    overfit_tolerance: float = 0.08,
    overfit_weight: float = 0.50,
) -> float:
    base_fitness = (
        0.50 * validation_metrics.recall_pos
        + 0.30 * validation_metrics.f1_pos
        + 0.15 * validation_metrics.auc_roc
        + 0.05 * validation_metrics.accuracy
    )

    if train_metrics is None:
        return float(base_fitness)

    overfit_gap = train_metrics.f1_pos - validation_metrics.f1_pos
    penalty = max(0.0, overfit_gap - overfit_tolerance) * overfit_weight
    return float(base_fitness - penalty)


def finite_metric(value: float) -> float:
    return float(value) if np.isfinite(value) else 0.0

from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from .config import RANDOM_STATE
from .data import PreparedData
from .evaluation import ModelMetrics, evaluate_classifier


def build_random_forest(**params) -> RandomForestClassifier:
    defaults = {
        "n_estimators": 100,
        "max_depth": 10,
        "class_weight": "balanced",
        "random_state": RANDOM_STATE,
        # Mantemos execucao serial para evitar instabilidade de multiprocessing
        # em notebooks, sandboxes e maquinas com configuracao limitada de CPU.
        "n_jobs": 1,
    }
    defaults.update(params)
    return RandomForestClassifier(**defaults)


def build_logistic_regression(**params) -> LogisticRegression:
    defaults = {
        "max_iter": 1000,
        "class_weight": "balanced",
        "random_state": RANDOM_STATE,
    }
    defaults.update(params)
    return LogisticRegression(**defaults)


def train_baselines(prepared: PreparedData) -> tuple[dict[str, object], dict[str, ModelMetrics]]:
    models = {
        "Regressao Logistica": build_logistic_regression(),
        "Arvore de Decisao": DecisionTreeClassifier(
            random_state=RANDOM_STATE,
            max_depth=5,
            criterion="entropy",
            class_weight="balanced",
        ),
        "Random Forest": build_random_forest(),
        "KNN": KNeighborsClassifier(n_neighbors=5, metric="euclidean"),
    }

    metrics = {}
    for name, model in models.items():
        model.fit(prepared.x_train_scaled, prepared.y_train)
        metrics[name] = evaluate_classifier(model, prepared.x_test_scaled, prepared.y_test)

    return models, metrics


def build_model_from_chromosome(model_family: str, genes: dict) -> object:
    if model_family == "random_forest":
        return build_random_forest(**genes)
    if model_family == "logistic_regression":
        return build_logistic_regression(**genes)
    raise ValueError(f"Familia de modelo desconhecida: {model_family}")

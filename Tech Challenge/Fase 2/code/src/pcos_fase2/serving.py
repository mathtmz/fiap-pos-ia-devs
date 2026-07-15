from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

import joblib
import pandas as pd

from .config import MODELS_DIR
from .llm_explainer import LLMExplanationRequest, generate_explanation


LOGGER = logging.getLogger("pcos_fase2.api")
MODEL_PATH = MODELS_DIR / "best_model.joblib"


@dataclass
class ApiMetrics:
    request_count: int = 0
    error_count: int = 0
    llm_calls: int = 0
    positive_predictions: int = 0
    negative_predictions: int = 0
    total_latency_ms: float = 0.0
    by_endpoint: dict[str, int] = field(default_factory=dict)

    def record(self, endpoint: str, latency_ms: float, error: bool = False) -> None:
        self.request_count += 1
        self.total_latency_ms += latency_ms
        self.by_endpoint[endpoint] = self.by_endpoint.get(endpoint, 0) + 1
        if error:
            self.error_count += 1

    def record_prediction(self, predicted_label: int) -> None:
        if predicted_label == 1:
            self.positive_predictions += 1
        else:
            self.negative_predictions += 1

    def as_dict(self) -> dict[str, Any]:
        average_latency = (
            self.total_latency_ms / self.request_count if self.request_count else 0.0
        )
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "llm_calls": self.llm_calls,
            "positive_predictions": self.positive_predictions,
            "negative_predictions": self.negative_predictions,
            "average_latency_ms": round(average_latency, 2),
            "by_endpoint": dict(self.by_endpoint),
        }


METRICS = ApiMetrics()


@lru_cache(maxsize=1)
def load_model_bundle() -> dict[str, Any]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modelo nao encontrado em {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def expected_features() -> list[str]:
    bundle = load_model_bundle()
    return list(bundle["feature_names"])


def validate_feature_payload(features: dict[str, float]) -> None:
    expected = set(expected_features())
    received = set(features)
    missing = sorted(expected - received)
    extra = sorted(received - expected)
    if missing or extra:
        details = []
        if missing:
            details.append(f"features ausentes: {missing}")
        if extra:
            details.append(f"features extras: {extra}")
        raise ValueError("; ".join(details))


def prediction_threshold() -> float:
    return float(os.getenv("PREDICTION_THRESHOLD", "0.50"))


def predict_from_features(features: dict[str, float]) -> dict[str, Any]:
    validate_feature_payload(features)
    bundle = load_model_bundle()
    feature_names = list(bundle["feature_names"])
    frame = pd.DataFrame([[features[name] for name in feature_names]], columns=feature_names)
    scaled = bundle["scaler"].transform(frame)
    probabilities = bundle["model"].predict_proba(scaled)[0]
    probability_pcos = float(probabilities[1])
    threshold = prediction_threshold()
    predicted_label = int(probability_pcos >= threshold)

    return {
        "predicted_label": predicted_label,
        "probability_pcos": probability_pcos,
        "threshold": threshold,
        "model_metrics": normalize_metrics(bundle.get("metrics", {})),
        "model_genes": bundle.get("genes", {}),
        "feature_names": feature_names,
    }


def explain_prediction(features: dict[str, float]) -> dict[str, Any]:
    prediction = predict_from_features(features)
    request = LLMExplanationRequest(
        model_name="Random Forest otimizado por algoritmo genetico",
        predicted_label=prediction["predicted_label"],
        probability_pcos=prediction["probability_pcos"],
        model_metrics=prediction["model_metrics"],
        top_features=prediction["feature_names"][:5],
    )
    response, safety = generate_explanation(request)
    METRICS.llm_calls += 1
    return {
        "prediction": prediction,
        "explanation": response,
        "safety": safety,
    }


def normalize_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    normalized = {}
    for key, value in metrics.items():
        if hasattr(value, "item"):
            normalized[key] = value.item()
        else:
            normalized[key] = value
    return normalized


def log_event(endpoint: str, status: str, latency_ms: float, **extra: Any) -> None:
    fields = {
        "endpoint": endpoint,
        "status": status,
        "latency_ms": round(latency_ms, 2),
        **extra,
    }
    LOGGER.info("api_event %s", fields)


def timed_call(endpoint: str, action):
    start = time.perf_counter()
    try:
        result = action()
    except Exception:
        latency_ms = (time.perf_counter() - start) * 1000
        METRICS.record(endpoint, latency_ms, error=True)
        log_event(endpoint, "error", latency_ms)
        raise
    latency_ms = (time.perf_counter() - start) * 1000
    METRICS.record(endpoint, latency_ms)
    log_event(endpoint, "ok", latency_ms)
    return result

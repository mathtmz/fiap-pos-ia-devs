from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from .serving import (
    METRICS,
    expected_features,
    explain_prediction,
    load_model_bundle,
    log_event,
    predict_from_features,
    timed_call,
)


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(
    title="PCOS Fase 2 API",
    description="API simples para inferencia e explicacao do modelo de apoio a triagem de SOP.",
    version="1.0.0",
)


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    features: dict[str, float]


class PredictionResponse(BaseModel):
    predicted_label: int
    probability_pcos: float
    threshold: float
    model_metrics: dict[str, Any]
    model_genes: dict[str, Any]


class ExplanationResponse(BaseModel):
    prediction: PredictionResponse
    explanation: str
    safety: dict[str, bool]


@app.get("/health")
def health() -> dict[str, Any]:
    def action() -> dict[str, Any]:
        bundle = load_model_bundle()
        return {
            "status": "ok",
            "model_loaded": True,
            "feature_count": len(bundle["feature_names"]),
            "llm_provider": os.getenv("LLM_PROVIDER", "mock"),
        }

    return timed_call("/health", action)


@app.get("/features")
def features() -> dict[str, Any]:
    return timed_call("/features", lambda: {"features": expected_features()})


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> dict[str, Any]:
    def action() -> dict[str, Any]:
        result = predict_from_features(request.features)
        METRICS.record_prediction(result["predicted_label"])
        log_event(
            "/predict",
            "prediction",
            0,
            predicted_label=result["predicted_label"],
            probability_pcos=round(result["probability_pcos"], 4),
        )
        result.pop("feature_names", None)
        return result

    try:
        return timed_call("/predict", action)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/explain", response_model=ExplanationResponse)
def explain(request: PredictionRequest) -> dict[str, Any]:
    def action() -> dict[str, Any]:
        result = explain_prediction(request.features)
        METRICS.record_prediction(result["prediction"]["predicted_label"])
        result["prediction"].pop("feature_names", None)
        return result

    try:
        return timed_call("/explain", action)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    return timed_call("/metrics", METRICS.as_dict)

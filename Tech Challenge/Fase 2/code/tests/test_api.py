from fastapi.testclient import TestClient

from pcos_fase2.api import app
from pcos_fase2.serving import expected_features


client = TestClient(app)


def sample_features() -> dict[str, float]:
    return {feature: 1.0 for feature in expected_features()}


def test_health_endpoint_returns_model_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model_loaded"] is True


def test_predict_endpoint_returns_prediction():
    response = client.post("/predict", json={"features": sample_features()})

    assert response.status_code == 200
    payload = response.json()
    assert payload["predicted_label"] in [0, 1]
    assert 0 <= payload["probability_pcos"] <= 1
    assert "model_metrics" in payload


def test_predict_rejects_missing_feature():
    features = sample_features()
    features.pop(next(iter(features)))

    response = client.post("/predict", json={"features": features})

    assert response.status_code == 422
    assert "features ausentes" in response.text


def test_predict_rejects_extra_feature():
    features = sample_features()
    features["feature_inexistente"] = 1.0

    response = client.post("/predict", json={"features": features})

    assert response.status_code == 422
    assert "features extras" in response.text


def test_metrics_endpoint_returns_counters():
    client.post("/predict", json={"features": sample_features()})

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.json()["request_count"] >= 1


def test_explain_endpoint_uses_mock_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")

    response = client.post("/explain", json={"features": sample_features()})

    assert response.status_code == 200
    payload = response.json()
    assert "explanation" in payload
    assert payload["safety"]["mentions_professional"] is True

"""
test_api.py
────────────
Integration tests for the FastAPI churn prediction service.
Run with: pytest tests/test_api.py -v

Note: These tests mock the predictor so they run without a trained
model present, keeping CI fast and deterministic.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).parent.parent))
from src.api.app import app
from src.inference.predictor import ChurnPrediction

client = TestClient(app)


def _mock_prediction(cid="C00001", prob=0.42):
    return ChurnPrediction(
        customer_id=cid,
        churn_probability=prob,
        will_churn=prob >= 0.5,
        risk_level="medium" if 0.3 <= prob < 0.6 else ("high" if prob >= 0.6 else "low"),
        confidence="mocked",
        inference_time_ms=5.2,
    )


VALID_CUSTOMER = {
    "CustomerID": "C00001",
    "Tenure": 12,
    "MonthlyCharges": 85.0,
    "TotalCharges": 1020.0,
    "Contract": "Month-to-month",
    "PaymentMethod": "Electronic Check",
    "PaperlessBilling": "Yes",
    "SeniorCitizen": 0,
}


class TestHealthEndpoint:

    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_payload_has_required_fields(self):
        response = client.get("/health")
        data = response.json()
        for field in ["status", "uptime_seconds", "model_loaded", "version"]:
            assert field in data

    def test_health_status_is_healthy(self):
        assert client.get("/health").json()["status"] == "healthy"


class TestMetricsEndpoint:

    def test_metrics_returns_200(self):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_is_prometheus_format(self):
        response = client.get("/metrics")
        text = response.text
        assert "# HELP" in text
        assert "# TYPE" in text
        assert "churn_requests_total" in text


class TestPredictEndpoint:

    @patch("src.api.app.get_predictor")
    def test_predict_valid_customer_returns_200(self, mock_get_predictor):
        mock_predictor = MagicMock()
        mock_predictor.predict_one.return_value = _mock_prediction()
        mock_get_predictor.return_value = mock_predictor

        response = client.post("/predict", json=VALID_CUSTOMER)
        assert response.status_code == 200
        body = response.json()
        assert body["customer_id"] == "C00001"
        assert 0 <= body["churn_probability"] <= 1

    def test_predict_invalid_contract_rejected(self):
        bad_customer = {**VALID_CUSTOMER, "Contract": "Lifetime"}
        response = client.post("/predict", json=bad_customer)
        assert response.status_code == 422  # pydantic validation error

    def test_predict_missing_field_rejected(self):
        incomplete = {k: v for k, v in VALID_CUSTOMER.items() if k != "Tenure"}
        response = client.post("/predict", json=incomplete)
        assert response.status_code == 422

    def test_predict_negative_tenure_rejected(self):
        bad_customer = {**VALID_CUSTOMER, "Tenure": -5}
        response = client.post("/predict", json=bad_customer)
        assert response.status_code == 422

    @patch("src.api.app.get_predictor")
    def test_predict_handles_model_error_gracefully(self, mock_get_predictor):
        mock_predictor = MagicMock()
        mock_predictor.predict_one.side_effect = RuntimeError("model exploded")
        mock_get_predictor.return_value = mock_predictor

        response = client.post("/predict", json=VALID_CUSTOMER)
        assert response.status_code == 500
        assert "model exploded" in response.json()["detail"]


class TestBatchPredictEndpoint:

    @patch("src.api.app.get_predictor")
    def test_batch_predict_returns_aggregates(self, mock_get_predictor):
        mock_predictor = MagicMock()
        mock_predictor.predict_batch.return_value = [
            _mock_prediction("C001", 0.8),
            _mock_prediction("C002", 0.2),
            _mock_prediction("C003", 0.65),
        ]
        mock_get_predictor.return_value = mock_predictor

        payload = {"customers": [VALID_CUSTOMER, VALID_CUSTOMER, VALID_CUSTOMER]}
        response = client.post("/batch_predict", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["total_customers"] == 3
        assert body["churn_count"] == 2          # 0.8 and 0.65 → churn
        assert body["high_risk_count"] == 2

    def test_batch_predict_empty_list_returns_zero_results(self):
        # An empty customers list is valid input, not malformed —
        # it should return cleanly with zero predictions, not error.
        response = client.post("/batch_predict", json={"customers": []})
        assert response.status_code == 200
        body = response.json()
        assert body["total_customers"] == 0
        assert body["predictions"] == []
        assert body["churn_count"] == 0

    def test_batch_predict_over_limit_rejected(self):
        too_many = {"customers": [VALID_CUSTOMER] * 501}
        response = client.post("/batch_predict", json=too_many)
        assert response.status_code == 422


class TestRootDocs:

    def test_openapi_schema_available(self):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.json()["info"]["title"] == "Customer Churn Prediction API"

    def test_docs_page_loads(self):
        response = client.get("/docs")
        assert response.status_code == 200

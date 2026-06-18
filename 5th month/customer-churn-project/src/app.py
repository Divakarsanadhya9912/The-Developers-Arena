"""
app.py
──────
FastAPI REST API for the Customer Churn Prediction service.

Endpoints
---------
GET  /health              → service status & uptime
GET  /metrics             → Prometheus-style metrics
POST /predict             → single customer prediction
POST /batch_predict       → up to 500 customers at once
POST /predict_file        → upload CSV, receive predictions

Run locally:
    uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
"""

import time
import logging
import io
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

logger = logging.getLogger(__name__)

# ── App setup ──────────────────────────────────────────────────────────── #

app = FastAPI(
    title="Customer Churn Prediction API",
    description=(
        "Production-ready REST API for predicting customer churn probability "
        "using a deep neural network trained on customer behavioural data."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global state ───────────────────────────────────────────────────────── #

_predictor = None
_start_time = time.time()
_request_count = 0
_error_count = 0
_total_latency_ms = 0.0


def get_predictor():
    global _predictor
    if _predictor is None:
        try:
            import sys
            sys.path.append(str(Path(__file__).parent.parent.parent))
            from src.inference.predictor import ChurnPredictor
            _predictor = ChurnPredictor()
        except Exception as exc:
            logger.error(f"Failed to load model: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Model not loaded. Run training first."
            )
    return _predictor


# ── Pydantic schemas ───────────────────────────────────────────────────── #

class CustomerRecord(BaseModel):
    CustomerID: str = Field(..., json_schema_extra={"example": "C00001"})
    Tenure: int = Field(..., ge=0, le=100, json_schema_extra={"example": 12})
    MonthlyCharges: float = Field(..., ge=0, json_schema_extra={"example": 85.0})
    TotalCharges: float = Field(..., ge=0, json_schema_extra={"example": 1020.0})
    Contract: str = Field(..., json_schema_extra={"example": "Month-to-month"})
    PaymentMethod: str = Field(..., json_schema_extra={"example": "Electronic Check"})
    PaperlessBilling: str = Field(..., json_schema_extra={"example": "Yes"})
    SeniorCitizen: int = Field(..., ge=0, le=1, json_schema_extra={"example": 0})

    @field_validator("Contract")
    @classmethod
    def validate_contract(cls, v):
        valid = {"Month-to-month", "One year", "Two year"}
        if v not in valid:
            raise ValueError(f"Contract must be one of {valid}")
        return v


class PredictionResponse(BaseModel):
    customer_id: str
    churn_probability: float
    will_churn: bool
    risk_level: str
    confidence: str
    inference_time_ms: float


class BatchRequest(BaseModel):
    customers: List[CustomerRecord] = Field(..., max_length=500)


class BatchResponse(BaseModel):
    predictions: List[PredictionResponse]
    total_customers: int
    churn_count: int
    high_risk_count: int
    batch_time_ms: float


# ── Endpoints ──────────────────────────────────────────────────────────── #

@app.get("/health", tags=["System"])
def health_check():
    """Returns service status, uptime, and model info."""
    uptime_s = round(time.time() - _start_time, 1)
    return {
        "status": "healthy",
        "uptime_seconds": uptime_s,
        "uptime_human": f"{uptime_s // 3600:.0f}h {(uptime_s % 3600) // 60:.0f}m",
        "model_loaded": _predictor is not None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }


@app.get("/metrics", tags=["System"])
def prometheus_metrics():
    """Returns Prometheus-compatible plain-text metrics."""
    avg_latency = (_total_latency_ms / max(_request_count, 1))
    lines = [
        "# HELP churn_requests_total Total prediction requests",
        "# TYPE churn_requests_total counter",
        f"churn_requests_total {_request_count}",
        "# HELP churn_errors_total Total errors",
        "# TYPE churn_errors_total counter",
        f"churn_errors_total {_error_count}",
        "# HELP churn_avg_latency_ms Average inference latency",
        "# TYPE churn_avg_latency_ms gauge",
        f"churn_avg_latency_ms {avg_latency:.2f}",
        "# HELP churn_uptime_seconds Service uptime",
        "# TYPE churn_uptime_seconds counter",
        f"churn_uptime_seconds {time.time() - _start_time:.0f}",
    ]
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("\n".join(lines))


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_single(customer: CustomerRecord):
    """
    Predict churn probability for a single customer.

    Returns probability, binary decision, and risk tier.
    """
    global _request_count, _error_count, _total_latency_ms
    _request_count += 1
    try:
        predictor = get_predictor()
        result = predictor.predict_one(customer.model_dump())
        _total_latency_ms += result.inference_time_ms
        return result.to_dict()
    except Exception as exc:
        _error_count += 1
        logger.error(f"Prediction error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/batch_predict", response_model=BatchResponse, tags=["Prediction"])
def predict_batch(request: BatchRequest):
    """
    Predict churn for up to 500 customers in one call.

    Returns predictions plus aggregated risk statistics. An empty
    `customers` list is valid input and returns an empty result rather
    than an error — there's nothing to predict, not a malformed request.
    """
    global _request_count, _error_count, _total_latency_ms

    if not request.customers:
        return {
            "predictions": [],
            "total_customers": 0,
            "churn_count": 0,
            "high_risk_count": 0,
            "batch_time_ms": 0.0,
        }

    _request_count += len(request.customers)
    t0 = time.perf_counter()
    try:
        predictor = get_predictor()
        records = [c.model_dump() for c in request.customers]
        predictions = predictor.predict_batch(records)
        batch_ms = (time.perf_counter() - t0) * 1000
        _total_latency_ms += batch_ms

        churn_count = sum(1 for p in predictions if p.will_churn)
        high_risk = sum(1 for p in predictions if p.risk_level == "high")

        return {
            "predictions": [p.to_dict() for p in predictions],
            "total_customers": len(predictions),
            "churn_count": churn_count,
            "high_risk_count": high_risk,
            "batch_time_ms": round(batch_ms, 2),
        }
    except Exception as exc:
        _error_count += 1
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/predict_file", tags=["Prediction"])
async def predict_from_file(file: UploadFile = File(...)):
    """
    Upload a CSV file, receive predictions as a downloadable CSV.
    """
    global _request_count, _error_count
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        _request_count += len(df)

        predictor = get_predictor()
        records = df.to_dict(orient="records")
        predictions = predictor.predict_batch(records)

        df["churn_probability"] = [p.churn_probability for p in predictions]
        df["will_churn"] = [p.will_churn for p in predictions]
        df["risk_level"] = [p.risk_level for p in predictions]

        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=predictions.csv"}
        )
    except Exception as exc:
        _error_count += 1
        raise HTTPException(status_code=500, detail=str(exc))


# ── Startup event ──────────────────────────────────────────────────────── #

@app.on_event("startup")
async def startup_event():
    logger.info("Churn Prediction API started. Warming up model …")
    try:
        get_predictor()
        logger.info("Model warm-up complete.")
    except Exception as exc:
        logger.warning(f"Model warm-up skipped (train first): {exc}")

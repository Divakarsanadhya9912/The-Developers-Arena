"""
predictor.py
────────────
Production inference engine for the churn prediction model.
Supports single-record and batch prediction with confidence scores.
"""

import numpy as np
import pandas as pd
import joblib
import logging
import time
from pathlib import Path
from typing import Union, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ChurnPrediction:
    customer_id: str
    churn_probability: float
    will_churn: bool
    risk_level: str          # low / medium / high
    confidence: str          # label for UI display
    inference_time_ms: float

    def to_dict(self) -> dict:
        return asdict(self)


def _risk_label(prob: float) -> tuple:
    """Map probability to risk level and confidence label."""
    if prob < 0.30:
        return "low", f"{(1 - prob) * 100:.1f}% confident no churn"
    elif prob < 0.60:
        return "medium", f"Uncertain ({prob * 100:.1f}% churn probability)"
    else:
        return "high", f"{prob * 100:.1f}% confident will churn"


class ChurnPredictor:
    """
    Wraps the trained keras model + preprocessing pipeline for inference.
    Thread-safe; suitable for concurrent FastAPI requests.
    """

    def __init__(self,
                 model_path: str = "models/churn_model.keras",
                 preprocessor_path: str = "models/preprocessor.joblib"):
        self._load(model_path, preprocessor_path)

    def _load(self, model_path: str, preprocessor_path: str):
        import tensorflow as tf
        logger.info(f"Loading model from {model_path} …")
        self.model = tf.keras.models.load_model(model_path)
        logger.info(f"Loading preprocessor from {preprocessor_path} …")
        self.preprocessor = joblib.load(preprocessor_path)
        logger.info("Predictor ready.")

    # ── Public API ──────────────────────────────────────────────────── #

    def predict_one(self, record: dict) -> ChurnPrediction:
        """
        Predict churn for a single customer.

        Parameters
        ----------
        record : dict  (must contain the required customer fields)
        """
        t0 = time.perf_counter()
        df = pd.DataFrame([record])
        X = self.preprocessor.transform(df)
        prob = float(self.model.predict(X, verbose=0)[0][0])
        elapsed_ms = (time.perf_counter() - t0) * 1000

        risk, confidence = _risk_label(prob)
        cid = record.get("CustomerID", "UNKNOWN")
        return ChurnPrediction(
            customer_id=cid,
            churn_probability=round(prob, 4),
            will_churn=prob >= 0.5,
            risk_level=risk,
            confidence=confidence,
            inference_time_ms=round(elapsed_ms, 2),
        )

    def predict_batch(self, records: List[dict]) -> List[ChurnPrediction]:
        """
        Predict churn for a list of customer records (vectorised).
        """
        t0 = time.perf_counter()
        df = pd.DataFrame(records)
        X = self.preprocessor.transform(df)
        probs = self.model.predict(X, verbose=0).ravel()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        per_record = elapsed_ms / max(len(records), 1)

        results = []
        for i, (record, prob) in enumerate(zip(records, probs)):
            risk, confidence = _risk_label(float(prob))
            results.append(ChurnPrediction(
                customer_id=record.get("CustomerID", f"CUST_{i:04d}"),
                churn_probability=round(float(prob), 4),
                will_churn=float(prob) >= 0.5,
                risk_level=risk,
                confidence=confidence,
                inference_time_ms=round(per_record, 2),
            ))
        logger.info(
            f"Batch prediction: {len(records)} records in {elapsed_ms:.1f}ms "
            f"({per_record:.1f}ms/record)"
        )
        return results

    def predict_csv(self, csv_path: str) -> pd.DataFrame:
        """Load a CSV, predict, and return a DataFrame with predictions."""
        df = pd.read_csv(csv_path)
        records = df.to_dict(orient="records")
        predictions = self.predict_batch(records)
        result_df = df.copy()
        result_df["churn_probability"] = [p.churn_probability for p in predictions]
        result_df["will_churn"] = [p.will_churn for p in predictions]
        result_df["risk_level"] = [p.risk_level for p in predictions]
        return result_df


# ── Standalone demo ────────────────────────────────────────────────────── #

if __name__ == "__main__":
    # Simulate without a real trained model (loads mock data)
    sample = {
        "CustomerID": "C99999",
        "Tenure": 2,
        "MonthlyCharges": 180,
        "TotalCharges": 360,
        "Contract": "Month-to-month",
        "PaymentMethod": "Electronic Check",
        "PaperlessBilling": "Yes",
        "SeniorCitizen": 1,
    }
    print("Sample customer record:")
    for k, v in sample.items():
        print(f"  {k}: {v}")
    print("\nModel files must exist at models/ to run inference.")
    print("Run: python src/training/train.py  to generate them first.")

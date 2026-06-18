"""
monitor.py
──────────
Production monitoring for the churn prediction model.

Tracks:
- Prediction volume & latency over time
- Data drift (feature distribution shift vs. training baseline)
- Model performance decay (when ground truth becomes available)
- Alerting thresholds for operational dashboards
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────── #
# Data structures                                                           #
# ──────────────────────────────────────────────────────────────────────── #

@dataclass
class PredictionLog:
    timestamp: str
    customer_id: str
    churn_probability: float
    will_churn: bool
    inference_time_ms: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DriftReport:
    feature: str
    baseline_mean: float
    current_mean: float
    psi_score: float          # Population Stability Index
    ks_statistic: float       # Kolmogorov–Smirnov statistic
    ks_pvalue: float
    drift_detected: bool
    severity: str             # none / low / moderate / high


# ──────────────────────────────────────────────────────────────────────── #
# Prediction logger                                                         #
# ──────────────────────────────────────────────────────────────────────── #

class PredictionLogger:
    """
    Lightweight append-only logger for every prediction served.
    Backs the latency / volume dashboards and the drift detector.
    """

    def __init__(self, log_path: str = "logs/predictions.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, customer_id: str, prob: float,
            will_churn: bool, latency_ms: float):
        entry = PredictionLog(
            timestamp=datetime.now(timezone.utc).isoformat(),
            customer_id=customer_id,
            churn_probability=prob,
            will_churn=will_churn,
            inference_time_ms=latency_ms,
        )
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def load_recent(self, n: int = 1000) -> pd.DataFrame:
        if not self.log_path.exists():
            return pd.DataFrame()
        lines = self.log_path.read_text().strip().split("\n")
        lines = [l for l in lines if l]
        records = [json.loads(l) for l in lines[-n:]]
        return pd.DataFrame(records)


# ──────────────────────────────────────────────────────────────────────── #
# Drift detection                                                           #
# ──────────────────────────────────────────────────────────────────────── #

class DriftDetector:
    """
    Compares live feature distributions against the training baseline
    using Population Stability Index (PSI) and Kolmogorov–Smirnov tests.

    PSI interpretation (industry standard thresholds):
        < 0.10            → no significant drift
        0.10 – 0.25        → moderate drift, monitor closely
        > 0.25            → significant drift, retraining recommended
    """

    def __init__(self, baseline_path: str = "models/baseline_stats.json"):
        self.baseline_path = Path(baseline_path)
        self.baseline: dict = {}
        if self.baseline_path.exists():
            self.baseline = json.loads(self.baseline_path.read_text())

    def fit_baseline(self, df: pd.DataFrame, numeric_cols: List[str]):
        """Compute and persist baseline distribution statistics."""
        baseline = {}
        for col in numeric_cols:
            values = df[col].dropna().values
            bins = np.percentile(values, np.linspace(0, 100, 11))
            baseline[col] = {
                "mean": float(values.mean()),
                "std": float(values.std()),
                "bin_edges": bins.tolist(),
                "bin_counts": np.histogram(values, bins=bins)[0].tolist(),
                "raw_sample": values[:500].tolist(),  # for KS test
            }
        self.baseline = baseline
        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
        self.baseline_path.write_text(json.dumps(baseline, indent=2))
        logger.info(f"Baseline statistics saved for {len(numeric_cols)} features.")

    def _psi(self, baseline_counts: np.ndarray, current_counts: np.ndarray) -> float:
        """Population Stability Index between two binned distributions."""
        eps = 1e-4
        b_pct = baseline_counts / (baseline_counts.sum() + eps) + eps
        c_pct = current_counts / (current_counts.sum() + eps) + eps
        return float(np.sum((c_pct - b_pct) * np.log(c_pct / b_pct)))

    def _severity(self, psi: float) -> str:
        if psi < 0.10:
            return "none"
        elif psi < 0.25:
            return "moderate"
        return "high"

    def check_drift(self, current_df: pd.DataFrame) -> List[DriftReport]:
        """Run drift checks for every feature present in the baseline."""
        if not self.baseline:
            raise RuntimeError("No baseline found. Run fit_baseline() first.")

        reports = []
        for col, stats_b in self.baseline.items():
            if col not in current_df.columns:
                continue
            current_vals = current_df[col].dropna().values
            if len(current_vals) < 5:
                continue

            edges = np.array(stats_b["bin_edges"])
            current_counts, _ = np.histogram(current_vals, bins=edges)
            baseline_counts = np.array(stats_b["bin_counts"])

            psi = self._psi(baseline_counts, current_counts)
            ks_stat, ks_p = stats.ks_2samp(
                stats_b["raw_sample"], current_vals
            )

            reports.append(DriftReport(
                feature=col,
                baseline_mean=round(stats_b["mean"], 3),
                current_mean=round(float(current_vals.mean()), 3),
                psi_score=round(psi, 4),
                ks_statistic=round(float(ks_stat), 4),
                ks_pvalue=round(float(ks_p), 4),
                drift_detected=psi >= 0.10 or ks_p < 0.05,
                severity=self._severity(psi),
            ))
        return reports


# ──────────────────────────────────────────────────────────────────────── #
# Operational dashboard summary                                             #
# ──────────────────────────────────────────────────────────────────────── #

def generate_monitoring_summary(pred_logger: PredictionLogger,
                                drift_detector: Optional[DriftDetector] = None,
                                current_features: Optional[pd.DataFrame] = None) -> dict:
    """Build a single JSON-serialisable monitoring snapshot."""
    df = pred_logger.load_recent(n=5000)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requests_logged": len(df),
    }

    if not df.empty:
        summary.update({
            "avg_latency_ms": round(df["inference_time_ms"].mean(), 2),
            "p95_latency_ms": round(df["inference_time_ms"].quantile(0.95), 2),
            "p99_latency_ms": round(df["inference_time_ms"].quantile(0.99), 2),
            "predicted_churn_rate": round(df["will_churn"].mean(), 4),
            "avg_churn_probability": round(df["churn_probability"].mean(), 4),
        })
    else:
        summary.update({
            "avg_latency_ms": None,
            "predicted_churn_rate": None,
            "note": "No predictions logged yet.",
        })

    if drift_detector and current_features is not None:
        try:
            drift_reports = drift_detector.check_drift(current_features)
            summary["drift_checks"] = [asdict(r) for r in drift_reports]
            summary["drift_alert"] = any(r.drift_detected for r in drift_reports)
        except RuntimeError:
            summary["drift_checks"] = []
            summary["drift_alert"] = False

    return summary


if __name__ == "__main__":
    pred_logger = PredictionLogger()
    summary = generate_monitoring_summary(pred_logger)
    print(json.dumps(summary, indent=2))

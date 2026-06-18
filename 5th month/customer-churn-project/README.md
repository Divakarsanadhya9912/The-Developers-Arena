# Customer Churn Prediction — Deep Learning Pipeline

Production-grade churn prediction service: a regularized deep neural network served behind a FastAPI REST API, containerized with Docker, and monitored with Prometheus/Grafana.

**Specialization:** Time Series / Tabular Deep Learning (binary classification)
**Dataset:** `customer_churn.csv` (500 customers, 9 columns)
**Test ROC-AUC:** 0.987 | **Recall (churn):** 1.00 | **Precision (churn):** 0.44

## Quick Start

```bash
bash scripts/setup.sh
source .venv/bin/activate
python src/training/train.py
uvicorn src.api.app:app --reload
```

Open `http://localhost:8000/docs` for interactive API docs.

## Docker

```bash
docker-compose up --build
bash scripts/smoke_test_api.sh
```

Spins up the API (`:8000`), Prometheus (`:9090`), and Grafana (`:3000`, admin/admin).

## Project Structure

```
src/
  data_processing/   # ChurnDataPreprocessor — encoding, scaling, SMOTE
  models/             # Keras MLP + Wide&Deep architectures
  training/           # train.py — full train/eval/save pipeline
  inference/           # ChurnPredictor — single & batch prediction
  api/                 # FastAPI app (/predict, /batch_predict, /health, /metrics)
  monitoring/         # Drift detection (PSI, KS-test) + prediction logging
data/                 # customer_churn.csv, supermarket_sales.csv
notebooks/             # EDA
tests/                 # pytest — 35 tests across preprocessing/model/API
docker/, deployment/   # Dockerfile, docker-compose.yml, k8s/cloud guide
scripts/               # setup.sh, run_pipeline.sh, smoke_test_api.sh
```

## API

| Endpoint              | Method | Purpose                          |
|------------------------|--------|------------------------------------|
| `/predict`             | POST   | Single customer prediction         |
| `/batch_predict`       | POST   | Up to 500 customers at once        |
| `/predict_file`         | POST   | Upload CSV → download predictions  |
| `/health`               | GET    | Service status                     |
| `/metrics`             | GET    | Prometheus metrics                 |

```bash
curl -X POST localhost:8000/predict -H "Content-Type: application/json" -d '{
  "CustomerID": "C99999", "Tenure": 2, "MonthlyCharges": 180,
  "TotalCharges": 360, "Contract": "Month-to-month",
  "PaymentMethod": "Electronic Check", "PaperlessBilling": "Yes",
  "SeniorCitizen": 1
}'
```

## Model

10-feature input → Dense(128)→BN→Dropout(0.4) → Dense(64)→BN→Dropout(0.3) → Dense(32)→BN→Dropout(0.2) → sigmoid. Trained with class-weighted binary cross-entropy + SMOTE oversampling, early stopping on `val_auc`. 12,673 params, converges in ~17 epochs.

Engineered features: `AvgMonthlyRevenue`, `TenureBucket`, `HighChargeFlag`.

## Testing

```bash
pytest tests/ -v          # 35 tests: preprocessing, model, API
```

## Notes on Results

With only 500 rows (≈11% churn), the model trades precision for recall — it catches every churner in the test set (0 false negatives) at the cost of some false positives (14/89 non-churners flagged). For a retention use case this is usually the right tradeoff; tune the decision threshold in `predictor.py`'s `_risk_label()` if you want fewer false alarms instead.

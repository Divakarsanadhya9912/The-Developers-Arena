#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# smoke_test_api.sh — Manual curl-based verification of every endpoint
# Run after `docker-compose up` or `uvicorn ...` to confirm the API
# is responding correctly before declaring a deployment healthy.
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

HOST="${1:-http://localhost:8000}"

echo "Testing API at $HOST"
echo ""

echo "──── GET /health ────"
curl -s "$HOST/health" | python3 -m json.tool
echo ""

echo "──── GET /metrics ────"
curl -s "$HOST/metrics"
echo ""

echo "──── POST /predict (single customer) ────"
curl -s -X POST "$HOST/predict" \
    -H "Content-Type: application/json" \
    -d '{
        "CustomerID": "C99999",
        "Tenure": 2,
        "MonthlyCharges": 180,
        "TotalCharges": 360,
        "Contract": "Month-to-month",
        "PaymentMethod": "Electronic Check",
        "PaperlessBilling": "Yes",
        "SeniorCitizen": 1
    }' | python3 -m json.tool
echo ""

echo "──── POST /batch_predict (3 customers) ────"
curl -s -X POST "$HOST/batch_predict" \
    -H "Content-Type: application/json" \
    -d '{
        "customers": [
            {"CustomerID": "C001", "Tenure": 60, "MonthlyCharges": 45, "TotalCharges": 2700, "Contract": "Two year", "PaymentMethod": "Bank Transfer", "PaperlessBilling": "No", "SeniorCitizen": 0},
            {"CustomerID": "C002", "Tenure": 1,  "MonthlyCharges": 195, "TotalCharges": 195, "Contract": "Month-to-month", "PaymentMethod": "Electronic Check", "PaperlessBilling": "Yes", "SeniorCitizen": 1},
            {"CustomerID": "C003", "Tenure": 24, "MonthlyCharges": 90, "TotalCharges": 2160, "Contract": "One year", "PaymentMethod": "Credit Card", "PaperlessBilling": "Yes", "SeniorCitizen": 0}
        ]
    }' | python3 -m json.tool

echo ""
echo "All smoke tests sent. Review JSON output above for correctness."

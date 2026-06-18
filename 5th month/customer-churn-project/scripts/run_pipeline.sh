#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# run_pipeline.sh — Full pipeline: test → train → evaluate → serve
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

echo "════════════════════════════════════════════════════════"
echo "  STEP 1/4 — Running test suite"
echo "════════════════════════════════════════════════════════"
pytest tests/ -v --tb=short

echo ""
echo "════════════════════════════════════════════════════════"
echo "  STEP 2/4 — Training model"
echo "════════════════════════════════════════════════════════"
python src/training/train.py --epochs "${EPOCHS:-100}" --batch "${BATCH_SIZE:-32}"

echo ""
echo "════════════════════════════════════════════════════════"
echo "  STEP 3/4 — Validating saved artifacts"
echo "════════════════════════════════════════════════════════"
for f in models/churn_model.keras models/preprocessor.joblib reports/metrics.json; do
    if [ -f "$f" ]; then
        echo "  ✓ $f"
    else
        echo "  ✗ MISSING: $f"
        exit 1
    fi
done

echo ""
echo "════════════════════════════════════════════════════════"
echo "  STEP 4/4 — Starting API server"
echo "════════════════════════════════════════════════════════"
echo "  API docs will be available at http://localhost:8000/docs"
echo ""
uvicorn src.api.app:app --host 0.0.0.0 --port 8000

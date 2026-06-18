#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# setup.sh — One-command environment bootstrap
#
# Creates a virtual environment, installs dependencies, and prepares
# the directory structure needed for training/serving.
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

echo "════════════════════════════════════════════════════════"
echo "  Customer Churn Prediction — Environment Setup"
echo "════════════════════════════════════════════════════════"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo "ERROR: $PYTHON_BIN not found. Install Python 3.10+ first."
    exit 1
fi

echo "→ Creating virtual environment (.venv) ..."
$PYTHON_BIN -m venv .venv
source .venv/bin/activate

echo "→ Upgrading pip ..."
pip install --upgrade pip --quiet

echo "→ Installing dependencies from requirements.txt ..."
pip install -r requirements.txt --quiet

echo "→ Creating runtime directories ..."
mkdir -p models logs/tensorboard reports

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Setup complete."
echo ""
echo "  Activate the environment with:"
echo "      source .venv/bin/activate"
echo ""
echo "  Then train the model with:"
echo "      python src/training/train.py"
echo ""
echo "  Or run everything end-to-end with:"
echo "      bash scripts/run_pipeline.sh"
echo "════════════════════════════════════════════════════════"

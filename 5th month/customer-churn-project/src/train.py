"""
train.py
────────
End-to-end training pipeline for customer churn prediction.

Usage
-----
python src/training/train.py [--data data/customer_churn.csv]
                             [--epochs 100] [--batch 32]
                             [--model deep|wide_deep]
"""

import argparse
import json
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    classification_report, roc_auc_score,
    confusion_matrix, f1_score, average_precision_score
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Local imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.data_processing.data_preprocessing import ChurnDataPreprocessor
from src.models.churn_model import (
    build_churn_model, build_wide_and_deep_model,
    get_training_callbacks, compute_class_weights, save_model
)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────── #
# Core training function                                                    #
# ──────────────────────────────────────────────────────────────────────── #

def train(data_path: str = "data/customer_churn.csv",
          epochs: int = 100,
          batch_size: int = 32,
          model_type: str = "deep") -> dict:
    """
    Full training run: preprocess → build → train → evaluate → save.

    Returns
    -------
    Dictionary of evaluation metrics for logging / CI checks.
    """
    Path("models").mkdir(exist_ok=True)
    Path("logs/tensorboard").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(exist_ok=True)

    # ── 1. Data ─────────────────────────────────────────────────────────
    logger.info("═" * 60)
    logger.info("  STEP 1/5 — Data Preprocessing")
    logger.info("═" * 60)
    df = pd.read_csv(data_path)
    logger.info(f"Raw dataset: {df.shape[0]} rows, {df.shape[1]} cols")

    prep = ChurnDataPreprocessor(test_size=0.2, val_size=0.1, random_state=42)
    X_train, X_val, X_test, y_train, y_val, y_test, feature_names = \
        prep.fit_transform(df)
    prep.save("models/preprocessor.joblib")

    logger.info(f"Train: {X_train.shape} | Val: {X_val.shape} | "
                f"Test: {X_test.shape}")
    logger.info(f"Churn rate — train: {y_train.mean():.3f}, "
                f"test: {y_test.mean():.3f}")

    # ── 2. Model ─────────────────────────────────────────────────────────
    logger.info("═" * 60)
    logger.info("  STEP 2/5 — Model Construction")
    logger.info("═" * 60)
    input_dim = X_train.shape[1]
    if model_type == "wide_deep":
        model = build_wide_and_deep_model(input_dim=input_dim)
    else:
        model = build_churn_model(input_dim=input_dim)
    model.summary(print_fn=logger.info)

    # ── 3. Training ──────────────────────────────────────────────────────
    logger.info("═" * 60)
    logger.info("  STEP 3/5 — Training")
    logger.info("═" * 60)
    callbacks = get_training_callbacks(
        checkpoint_path="models/best_model.keras",
        log_dir="logs/tensorboard"
    )
    class_weights = compute_class_weights(y_train)

    t0 = time.time()
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_val, y_val),
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1
    )
    train_time = time.time() - t0
    logger.info(f"Training complete in {train_time:.1f}s")

    # ── 4. Evaluation ────────────────────────────────────────────────────
    logger.info("═" * 60)
    logger.info("  STEP 4/5 — Evaluation")
    logger.info("═" * 60)
    metrics = evaluate_model(model, X_test, y_test, feature_names)
    metrics["train_time_seconds"] = round(train_time, 1)
    metrics["epochs_run"] = len(history.history["loss"])
    metrics["model_type"] = model_type

    with open("reports/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Metrics saved → reports/metrics.json")

    # ── 5. Persist ───────────────────────────────────────────────────────
    logger.info("═" * 60)
    logger.info("  STEP 5/5 — Saving Model")
    logger.info("═" * 60)
    save_model(model, "models/churn_model.keras", metadata=metrics)

    plot_training_history(history, "reports/training_history.png")
    plot_confusion_matrix(
        y_test,
        (model.predict(X_test) >= 0.5).astype(int).ravel(),
        "reports/confusion_matrix.png"
    )

    print_summary(metrics)
    return metrics


# ──────────────────────────────────────────────────────────────────────── #
# Evaluation helpers                                                        #
# ──────────────────────────────────────────────────────────────────────── #

def evaluate_model(model, X_test: np.ndarray,
                   y_test: np.ndarray, feature_names: list) -> dict:
    y_prob = model.predict(X_test).ravel()
    y_pred = (y_prob >= 0.5).astype(int)

    report = classification_report(y_test, y_pred, output_dict=True)
    auc = roc_auc_score(y_test, y_prob)
    f1 = f1_score(y_test, y_pred)
    avg_prec = average_precision_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "roc_auc": round(auc, 4),
        "f1_score": round(f1, 4),
        "average_precision": round(avg_prec, 4),
        "accuracy": round(report["accuracy"], 4),
        "precision": round(report["1"]["precision"], 4),
        "recall": round(report["1"]["recall"], 4),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "feature_count": len(feature_names),
        "feature_names": feature_names,
    }

    logger.info(f"ROC-AUC: {auc:.4f} | F1: {f1:.4f} | "
                f"Precision: {metrics['precision']:.4f} | "
                f"Recall: {metrics['recall']:.4f}")
    return metrics


# ──────────────────────────────────────────────────────────────────────── #
# Plotting helpers                                                          #
# ──────────────────────────────────────────────────────────────────────── #

def plot_training_history(history, save_path: str):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Training History — Churn Prediction Model", fontsize=14)

    axes[0].plot(history.history["loss"], label="Train Loss")
    axes[0].plot(history.history["val_loss"], label="Val Loss")
    axes[0].set_title("Loss (Binary Cross-Entropy)")
    axes[0].set_xlabel("Epoch"); axes[0].set_ylabel("Loss")
    axes[0].legend(); axes[0].grid(True, alpha=0.3)

    axes[1].plot(history.history["auc"], label="Train AUC")
    axes[1].plot(history.history["val_auc"], label="Val AUC")
    axes[1].set_title("ROC-AUC Score")
    axes[1].set_xlabel("Epoch"); axes[1].set_ylabel("AUC")
    axes[1].legend(); axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    logger.info(f"Training history plot saved → {save_path}")


def plot_confusion_matrix(y_true, y_pred, save_path: str):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=["No Churn", "Churn"],
                yticklabels=["No Churn", "Churn"])
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("Actual", fontsize=12)
    ax.set_title("Confusion Matrix — Test Set", fontsize=13)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    logger.info(f"Confusion matrix saved → {save_path}")


def print_summary(metrics: dict):
    print("\n" + "═" * 55)
    print("  TRAINING COMPLETE — PERFORMANCE SUMMARY")
    print("═" * 55)
    print(f"  ROC-AUC Score      : {metrics['roc_auc']:.4f}")
    print(f"  F1 Score (Churn)   : {metrics['f1_score']:.4f}")
    print(f"  Avg Precision      : {metrics['average_precision']:.4f}")
    print(f"  Accuracy           : {metrics['accuracy']:.4f}")
    print(f"  Precision (Churn)  : {metrics['precision']:.4f}")
    print(f"  Recall (Churn)     : {metrics['recall']:.4f}")
    print(f"  Epochs Run         : {metrics['epochs_run']}")
    print(f"  Training Time      : {metrics['train_time_seconds']}s")
    print("═" * 55 + "\n")


# ──────────────────────────────────────────────────────────────────────── #
# CLI entry-point                                                           #
# ──────────────────────────────────────────────────────────────────────── #

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train churn prediction model")
    parser.add_argument("--data",    default="data/customer_churn.csv")
    parser.add_argument("--epochs",  type=int, default=100)
    parser.add_argument("--batch",   type=int, default=32)
    parser.add_argument("--model",   choices=["deep", "wide_deep"], default="deep")
    args = parser.parse_args()

    train(data_path=args.data, epochs=args.epochs,
          batch_size=args.batch, model_type=args.model)

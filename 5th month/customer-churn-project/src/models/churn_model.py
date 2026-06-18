"""
churn_model.py
──────────────
Deep learning model for customer churn prediction.

Architecture: Multi-Layer Perceptron with Batch Normalization,
Dropout regularization, and residual connections.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard
)
import json
import logging
from pathlib import Path
from typing import Tuple, List, Optional

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────── #
# Model factory                                                             #
# ──────────────────────────────────────────────────────────────────────── #

def build_churn_model(input_dim: int,
                      hidden_units: List[int] = (128, 64, 32),
                      dropout_rates: List[float] = (0.4, 0.3, 0.2),
                      learning_rate: float = 0.001,
                      l2_lambda: float = 1e-4) -> keras.Model:
    """
    Build a regularised deep MLP for binary churn prediction.

    Parameters
    ----------
    input_dim     : number of input features after preprocessing
    hidden_units  : neurons in each hidden layer
    dropout_rates : dropout probability after each hidden layer
    learning_rate : Adam learning rate
    l2_lambda     : L2 weight-decay coefficient

    Returns
    -------
    Compiled keras.Model
    """
    inputs = keras.Input(shape=(input_dim,), name="features")

    x = inputs
    for i, (units, drop) in enumerate(zip(hidden_units, dropout_rates)):
        x = layers.Dense(
            units,
            activation="relu",
            kernel_regularizer=regularizers.l2(l2_lambda),
            name=f"dense_{i+1}"
        )(x)
        x = layers.BatchNormalization(name=f"bn_{i+1}")(x)
        x = layers.Dropout(drop, name=f"dropout_{i+1}")(x)

    # Output — sigmoid for binary classification
    output = layers.Dense(1, activation="sigmoid", name="churn_probability")(x)

    model = keras.Model(inputs=inputs, outputs=output, name="ChurnPredictor")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            keras.metrics.AUC(name="auc"),
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
        ]
    )

    logger.info(f"Model built: {model.count_params():,} trainable parameters")
    return model


def build_wide_and_deep_model(input_dim: int,
                              deep_units: List[int] = (64, 32),
                              learning_rate: float = 0.001) -> keras.Model:
    """
    Wide-and-Deep variant: combines a shallow linear path (wide) with
    a deep MLP path to capture both memorisation and generalisation.
    """
    inputs = keras.Input(shape=(input_dim,), name="features")

    # Wide path (linear)
    wide = layers.Dense(1, name="wide_linear")(inputs)

    # Deep path
    deep = layers.Dense(deep_units[0], activation="relu", name="deep_1")(inputs)
    deep = layers.BatchNormalization()(deep)
    deep = layers.Dropout(0.3)(deep)
    for i, units in enumerate(deep_units[1:], start=2):
        deep = layers.Dense(units, activation="relu", name=f"deep_{i}")(deep)
        deep = layers.BatchNormalization()(deep)
        deep = layers.Dropout(0.2)(deep)
    deep = layers.Dense(1, name="deep_out")(deep)

    # Combine
    combined = layers.Add(name="wide_deep_add")([wide, deep])
    output = layers.Activation("sigmoid", name="churn_probability")(combined)

    model = keras.Model(inputs=inputs, outputs=output, name="WideDeepChurnPredictor")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc"),
                 keras.metrics.Precision(name="precision"),
                 keras.metrics.Recall(name="recall")]
    )
    logger.info(f"Wide-and-Deep model: {model.count_params():,} params")
    return model


# ──────────────────────────────────────────────────────────────────────── #
# Training utilities                                                        #
# ──────────────────────────────────────────────────────────────────────── #

def get_training_callbacks(checkpoint_path: str = "models/best_model.keras",
                           log_dir: str = "logs/tensorboard") -> list:
    """Return standard callbacks for stable training."""
    return [
        EarlyStopping(
            monitor="val_auc", patience=15, restore_best_weights=True,
            mode="max", verbose=1
        ),
        ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=7,
            min_lr=1e-6, verbose=1
        ),
        ModelCheckpoint(
            filepath=checkpoint_path, monitor="val_auc",
            save_best_only=True, mode="max", verbose=1
        ),
        TensorBoard(log_dir=log_dir, histogram_freq=1),
    ]


def compute_class_weights(y_train: np.ndarray) -> dict:
    """
    Compute inverse-frequency class weights to handle imbalance.
    """
    neg, pos = np.bincount(y_train.astype(int))
    total = neg + pos
    w_neg = total / (2 * neg)
    w_pos = total / (2 * pos)
    logger.info(f"Class weights → 0: {w_neg:.3f}, 1: {w_pos:.3f}")
    return {0: w_neg, 1: w_pos}


# ──────────────────────────────────────────────────────────────────────── #
# Model persistence                                                         #
# ──────────────────────────────────────────────────────────────────────── #

def save_model(model: keras.Model, path: str = "models/churn_model.keras",
               metadata: Optional[dict] = None):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    model.save(path)
    if metadata:
        meta_path = Path(path).with_suffix(".json")
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
    logger.info(f"Model saved → {path}")


def load_model(path: str = "models/churn_model.keras") -> keras.Model:
    model = keras.models.load_model(path)
    logger.info(f"Model loaded ← {path}")
    return model


if __name__ == "__main__":
    # Quick smoke-test
    model = build_churn_model(input_dim=11)
    model.summary()
    wide_deep = build_wide_and_deep_model(input_dim=11)
    wide_deep.summary()

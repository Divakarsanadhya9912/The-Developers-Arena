"""
test_model.py
──────────────
Unit tests for model construction and training utilities.
Run with: pytest tests/test_model.py -v
"""

import sys
from pathlib import Path
import pytest
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
from src.models.churn_model import (
    build_churn_model, build_wide_and_deep_model,
    compute_class_weights, get_training_callbacks,
    save_model, load_model,
)


class TestBuildChurnModel:

    def test_model_compiles_with_correct_input_shape(self):
        model = build_churn_model(input_dim=11)
        assert model.input_shape == (None, 11)
        assert model.output_shape == (None, 1)

    def test_model_has_sigmoid_output(self):
        model = build_churn_model(input_dim=11)
        last_layer = model.layers[-1]
        assert last_layer.activation.__name__ == "sigmoid"

    def test_model_predicts_probabilities_in_range(self):
        model = build_churn_model(input_dim=5)
        X = np.random.randn(10, 5).astype(np.float32)
        preds = model.predict(X, verbose=0)
        assert preds.shape == (10, 1)
        assert np.all(preds >= 0) and np.all(preds <= 1)

    def test_custom_architecture_respected(self):
        model = build_churn_model(
            input_dim=8, hidden_units=[16, 8], dropout_rates=[0.1, 0.1]
        )
        # Hidden layers are named "dense_1", "dense_2", ...; the output
        # layer is intentionally named "churn_probability" (not "dense_N")
        # for readability in model.summary(). Count both explicitly
        # rather than pattern-matching on "dense" in the name.
        hidden_dense = [l for l in model.layers if l.name.startswith("dense_")]
        assert len(hidden_dense) == 2          # matches hidden_units=[16, 8]
        assert "churn_probability" in [l.name for l in model.layers]

    def test_model_metrics_include_auc_precision_recall(self):
        # model.metrics only exposes 'loss' and 'compile_metrics' before
        # any fit/evaluate call populates the individual metric objects —
        # this is a Keras runtime quirk, not a sign compile() was wrong.
        # The metrics that matter (used by EarlyStopping(monitor="val_auc")
        # and train.py's evaluation step) only materialise by name in
        # history.history after fit() actually runs, so assert there.
        model = build_churn_model(input_dim=6)
        X = np.random.randn(20, 6).astype(np.float32)
        y = np.random.randint(0, 2, 20).astype(np.float32)
        history = model.fit(X, y, epochs=1, verbose=0)
        for expected in ["auc", "precision", "recall", "accuracy"]:
            assert expected in history.history


class TestWideAndDeepModel:

    def test_wide_deep_compiles(self):
        model = build_wide_and_deep_model(input_dim=10)
        assert model.input_shape == (None, 10)
        assert model.output_shape == (None, 1)

    def test_wide_deep_predicts_valid_probabilities(self):
        model = build_wide_and_deep_model(input_dim=7)
        X = np.random.randn(5, 7).astype(np.float32)
        preds = model.predict(X, verbose=0)
        assert np.all((preds >= 0) & (preds <= 1))


class TestClassWeights:

    def test_balanced_classes_give_equal_weights(self):
        y = np.array([0, 1, 0, 1, 0, 1])
        weights = compute_class_weights(y)
        assert weights[0] == pytest.approx(weights[1], rel=1e-6)

    def test_imbalanced_classes_give_higher_weight_to_minority(self):
        y = np.array([0] * 90 + [1] * 10)
        weights = compute_class_weights(y)
        assert weights[1] > weights[0]


class TestCallbacks:

    def test_returns_four_callbacks(self, tmp_path):
        cb = get_training_callbacks(
            checkpoint_path=str(tmp_path / "model.keras"),
            log_dir=str(tmp_path / "logs"),
        )
        assert len(cb) == 4


class TestModelPersistence:

    def test_save_and_load_roundtrip(self, tmp_path):
        model = build_churn_model(input_dim=4)
        save_path = tmp_path / "test_model.keras"
        save_model(model, str(save_path), metadata={"test": True})

        assert save_path.exists()
        assert save_path.with_suffix(".json").exists()

        loaded = load_model(str(save_path))
        X = np.random.randn(3, 4).astype(np.float32)
        original_preds = model.predict(X, verbose=0)
        loaded_preds = loaded.predict(X, verbose=0)
        np.testing.assert_allclose(original_preds, loaded_preds, rtol=1e-5)

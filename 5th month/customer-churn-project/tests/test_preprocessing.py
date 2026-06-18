"""
test_preprocessing.py
──────────────────────
Unit tests for the data preprocessing pipeline.
Run with: pytest tests/test_preprocessing.py -v
"""

import sys
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from src.data_processing.data_preprocessing import ChurnDataPreprocessor, load_sales_data


@pytest.fixture
def sample_df():
    """Small synthetic dataset mirroring the real schema."""
    return pd.DataFrame({
        "CustomerID": [f"C{i:05d}" for i in range(1, 51)],
        "Tenure": np.random.randint(1, 72, 50),
        "MonthlyCharges": np.random.uniform(20, 200, 50),
        "TotalCharges": np.random.uniform(150, 8000, 50),
        "Contract": np.random.choice(
            ["Month-to-month", "One year", "Two year"], 50
        ),
        "PaymentMethod": np.random.choice(
            ["Credit Card", "Electronic Check", "Bank Transfer"], 50
        ),
        "PaperlessBilling": np.random.choice(["Yes", "No"], 50),
        "SeniorCitizen": np.random.choice([0, 1], 50),
        "Churn": np.random.choice([0, 1], 50, p=[0.85, 0.15]),
    })


class TestChurnDataPreprocessor:

    def test_fit_transform_returns_correct_shapes(self, sample_df):
        prep = ChurnDataPreprocessor(test_size=0.2, val_size=0.1, random_state=42)
        X_train, X_val, X_test, y_train, y_val, y_test, features = \
            prep.fit_transform(sample_df)

        total_input_rows = len(sample_df)
        # Training set will be larger than the raw split due to SMOTE
        assert X_train.shape[1] == X_val.shape[1] == X_test.shape[1]
        assert len(y_train) == X_train.shape[0]
        assert len(y_val) == X_val.shape[0]
        assert len(y_test) == X_test.shape[0]
        assert isinstance(features, list) and len(features) > 0

    def test_missing_required_column_raises(self, sample_df):
        broken = sample_df.drop(columns=["Tenure"])
        prep = ChurnDataPreprocessor()
        with pytest.raises(ValueError, match="Missing required columns"):
            prep.fit_transform(broken)

    def test_feature_engineering_adds_columns(self, sample_df):
        prep = ChurnDataPreprocessor()
        engineered = prep._engineer_features(sample_df.copy())
        for col in ["AvgMonthlyRevenue", "TenureBucket", "HighChargeFlag"]:
            assert col in engineered.columns

    def test_smote_balances_classes(self, sample_df):
        prep = ChurnDataPreprocessor(test_size=0.2, val_size=0.1, random_state=42)
        X_train, _, _, y_train, _, _, _ = prep.fit_transform(sample_df)
        # After SMOTE, the two classes should be equal (or near-equal)
        counts = np.bincount(y_train.astype(int))
        assert abs(counts[0] - counts[1]) <= 1

    def test_transform_requires_fit_first(self, sample_df):
        prep = ChurnDataPreprocessor()
        with pytest.raises(RuntimeError, match="must be fitted"):
            prep.transform(sample_df)

    def test_transform_after_fit_matches_feature_count(self, sample_df):
        prep = ChurnDataPreprocessor()
        prep.fit_transform(sample_df)
        new_records = sample_df.drop(columns=["Churn"]).iloc[:5]
        X_new = prep.transform(new_records)
        assert X_new.shape[0] == 5
        assert X_new.shape[1] == len(prep.feature_columns)

    def test_save_and_load_roundtrip(self, sample_df, tmp_path):
        prep = ChurnDataPreprocessor()
        prep.fit_transform(sample_df)
        save_path = tmp_path / "prep.joblib"
        prep.save(str(save_path))
        loaded = ChurnDataPreprocessor.load(str(save_path))
        assert loaded.is_fitted
        assert loaded.feature_columns == prep.feature_columns

    def test_no_nan_in_output(self, sample_df):
        prep = ChurnDataPreprocessor()
        X_train, X_val, X_test, *_ = prep.fit_transform(sample_df)
        assert not np.isnan(X_train).any()
        assert not np.isnan(X_val).any()
        assert not np.isnan(X_test).any()


class TestLoadSalesData:

    def test_load_sales_adds_time_features(self, tmp_path):
        csv_path = tmp_path / "sales.csv"
        df = pd.DataFrame({
            "Invoice_ID": ["INV1", "INV2"],
            "Date": ["2023-01-15", "2023-06-30"],
            "Time": ["14:30", "09:05"],
            "Total": [100.0, 250.0],
        })
        df.to_csv(csv_path, index=False)

        loaded = load_sales_data(str(csv_path))
        assert "Month" in loaded.columns
        assert "DayOfWeek" in loaded.columns
        assert "Hour" in loaded.columns
        assert loaded["Hour"].tolist() == [14, 9]

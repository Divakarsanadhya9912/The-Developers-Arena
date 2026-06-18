"""
data_preprocessing.py
─────────────────────
Complete preprocessing pipeline for customer churn prediction.
Handles missing values, encoding, scaling, and class imbalance.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
import joblib
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChurnDataPreprocessor:
    """
    End-to-end preprocessing pipeline for customer churn data.
    
    Handles:
    - Missing value imputation
    - Categorical encoding (Label + One-Hot)
    - Numerical feature scaling
    - Class imbalance correction via SMOTE
    - Train/validation/test split
    """

    def __init__(self, test_size: float = 0.2, val_size: float = 0.1,
                 random_state: int = 42):
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state

        self.scaler = StandardScaler()
        self.label_encoders: dict = {}
        self.imputer = SimpleImputer(strategy="median")
        self.feature_columns: list = []
        self.is_fitted = False

    # ------------------------------------------------------------------ #
    # Public interface                                                      #
    # ------------------------------------------------------------------ #

    def fit_transform(self, df: pd.DataFrame):
        """
        Fit the pipeline on training data and return processed splits.

        Returns
        -------
        X_train, X_val, X_test : np.ndarray
        y_train, y_val, y_test : np.ndarray
        feature_names          : list[str]
        """
        logger.info("Starting data preprocessing pipeline …")
        df = self._load_and_validate(df)
        df = self._engineer_features(df)
        df = self._encode_categoricals(df, fit=True)

        X, y = self._split_features_target(df)
        X = self._impute_and_scale(X, fit=True)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state,
            stratify=y
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train,
            test_size=self.val_size / (1 - self.test_size),
            random_state=self.random_state, stratify=y_train
        )

        # Balance training set with SMOTE
        X_train, y_train = self._apply_smote(X_train, y_train)

        self.is_fitted = True
        logger.info(
            f"Preprocessing complete. "
            f"Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}"
        )
        return X_train, X_val, X_test, y_train, y_val, y_test, self.feature_columns

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform new data using the fitted pipeline (inference)."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before transform().")
        df = self._load_and_validate(df)
        df = self._engineer_features(df)
        df = self._encode_categoricals(df, fit=False)
        X, _ = self._split_features_target(df, inference=True)
        return self._impute_and_scale(X, fit=False)

    def save(self, path: str = "models/preprocessor.joblib"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        logger.info(f"Preprocessor saved → {path}")

    @staticmethod
    def load(path: str = "models/preprocessor.joblib") -> "ChurnDataPreprocessor":
        return joblib.load(path)

    # ------------------------------------------------------------------ #
    # Private helpers                                                       #
    # ------------------------------------------------------------------ #

    def _load_and_validate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        required = {"Tenure", "MonthlyCharges", "TotalCharges",
                    "Contract", "PaymentMethod", "PaperlessBilling", "SeniorCitizen"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        logger.info(f"Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")
        return df

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features that improve model signal."""
        # Revenue density – captures pricing efficiency
        df["AvgMonthlyRevenue"] = df["TotalCharges"] / (df["Tenure"].replace(0, 1))
        # Tenure buckets (short / medium / long)
        df["TenureBucket"] = pd.cut(
            df["Tenure"], bins=[0, 12, 36, 72], labels=[0, 1, 2]
        ).astype(int)
        # High monthly charge flag
        df["HighChargeFlag"] = (df["MonthlyCharges"] > df["MonthlyCharges"].median()).astype(int)
        logger.info("Feature engineering complete (+3 derived features).")
        return df

    def _encode_categoricals(self, df: pd.DataFrame, fit: bool) -> pd.DataFrame:
        cat_cols = ["Contract", "PaymentMethod", "PaperlessBilling"]
        for col in cat_cols:
            if fit:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
            else:
                le = self.label_encoders.get(col)
                if le is None:
                    raise RuntimeError(f"No encoder for column '{col}'.")
                df[col] = le.transform(df[col].astype(str))
        return df

    def _split_features_target(self, df: pd.DataFrame, inference: bool = False):
        drop_cols = ["CustomerID", "Churn"] if not inference else ["CustomerID"]
        drop_cols = [c for c in drop_cols if c in df.columns]
        self.feature_columns = [c for c in df.columns if c not in drop_cols]
        X = df[self.feature_columns].values
        y = df["Churn"].values if "Churn" in df.columns else None
        return X, y

    def _impute_and_scale(self, X: np.ndarray, fit: bool) -> np.ndarray:
        if fit:
            X = self.imputer.fit_transform(X)
            X = self.scaler.fit_transform(X)
        else:
            X = self.imputer.transform(X)
            X = self.scaler.transform(X)
        return X

    @staticmethod
    def _apply_smote(X: np.ndarray, y: np.ndarray):
        """
        Apply SMOTE oversampling, adapting k_neighbors to the minority
        class size. SMOTE's default k_neighbors=5 raises a ValueError
        whenever the minority class has 5 or fewer samples (it needs
        k_neighbors + 1 points to find a neighbourhood), which happens
        on small datasets or after an unlucky stratified split. Capping
        k_neighbors at (minority_count - 1) keeps SMOTE usable in both
        cases without changing behaviour on datasets large enough for
        the default.
        """
        minority_count = int(min(np.bincount(y.astype(int))))
        if minority_count <= 1:
            logger.warning(
                "Minority class has ≤1 sample; skipping SMOTE (nothing to "
                "interpolate between)."
            )
            return X, y

        k_neighbors = min(5, minority_count - 1)
        smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
        X_res, y_res = smote.fit_resample(X, y)
        logger.info(
            f"SMOTE applied (k_neighbors={k_neighbors}). "
            f"Minority class: {y.sum()} → {y_res.sum()} samples."
        )
        return X_res, y_res


# ------------------------------------------------------------------ #
# Sales data loader (secondary dataset)                                #
# ------------------------------------------------------------------ #

def load_sales_data(path: str = "data/supermarket_sales.csv") -> pd.DataFrame:
    """Load and lightly clean the supermarket sales dataset."""
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.month
    df["DayOfWeek"] = df["Date"].dt.dayofweek
    df["Hour"] = pd.to_datetime(df["Time"], format="%H:%M").dt.hour
    logger.info(f"Sales data loaded: {df.shape}")
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/customer_churn.csv")
    prep = ChurnDataPreprocessor()
    splits = prep.fit_transform(df)
    X_train, X_val, X_test, y_train, y_val, y_test, feats = splits
    print("Feature names:", feats)
    print("Train shape:", X_train.shape, "| Churn rate:", y_train.mean().round(3))
    prep.save("models/preprocessor.joblib")

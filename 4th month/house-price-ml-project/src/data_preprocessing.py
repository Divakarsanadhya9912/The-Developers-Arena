"""
Data Preprocessing Module
House Price Prediction System
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data(filepath: str) -> pd.DataFrame:
    """Load and perform initial validation on dataset."""
    logger.info(f"Loading data from {filepath}")
    df = pd.read_csv(filepath)
    logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean the dataset."""
    logger.info("Validating data...")

    required_cols = ['area_sqft', 'bedrooms', 'bathrooms', 'age_years',
                     'floors', 'parking_spaces', 'location', 'property_type', 'price']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    initial_rows = len(df)
    df = df.dropna()
    df = df[df['price'] > 0]
    df = df[df['area_sqft'] > 0]
    df = df[df['bedrooms'] >= 1]
    df = df[df['age_years'] >= 0]

    logger.info(f"Removed {initial_rows - len(df)} invalid rows. Remaining: {len(df)}")
    return df.reset_index(drop=True)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create engineered features from raw data."""
    logger.info("Engineering features...")
    df = df.copy()

    # Derived features
    df['price_per_sqft'] = df['price'] / df['area_sqft']
    df['room_ratio'] = df['bathrooms'] / df['bedrooms']
    df['total_rooms'] = df['bedrooms'] + df['bathrooms']
    df['is_new'] = (df['age_years'] <= 5).astype(int)
    df['has_parking'] = (df['parking_spaces'] > 0).astype(int)
    df['size_category'] = pd.cut(df['area_sqft'],
                                  bins=[0, 800, 1500, 2500, float('inf')],
                                  labels=['Small', 'Medium', 'Large', 'Luxury'])

    logger.info(f"Created features: price_per_sqft, room_ratio, total_rooms, is_new, has_parking, size_category")
    return df


def build_preprocessor(numeric_features: list, categorical_features: list) -> ColumnTransformer:
    """Build sklearn preprocessing pipeline."""
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop'
    )
    return preprocessor


def prepare_data(filepath: str, test_size: float = 0.2, random_state: int = 42):
    """Full data preparation pipeline."""
    df = load_data(filepath)
    df = validate_data(df)
    df = engineer_features(df)

    numeric_features = ['area_sqft', 'bedrooms', 'bathrooms', 'age_years',
                        'floors', 'parking_spaces', 'room_ratio', 'total_rooms',
                        'is_new', 'has_parking']
    categorical_features = ['location', 'property_type', 'size_category']

    target = 'price'
    feature_cols = numeric_features + categorical_features

    X = df[feature_cols]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    preprocessor = build_preprocessor(numeric_features, categorical_features)

    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test, preprocessor, numeric_features, categorical_features


def get_data_summary(df: pd.DataFrame) -> dict:
    """Return summary statistics for documentation."""
    return {
        'rows': len(df),
        'columns': list(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'price_stats': df['price'].describe().to_dict() if 'price' in df.columns else {}
    }

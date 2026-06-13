"""
Model Training Module
Trains and compares: Linear Regression, Random Forest, Gradient Boosting
"""

import numpy as np
import pandas as pd
import joblib
import os
import json
import logging
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                              r2_score, mean_absolute_percentage_error)
from sklearn.inspection import permutation_importance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MODELS = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(
        n_estimators=100, max_depth=15, min_samples_split=5,
        random_state=42, n_jobs=-1
    ),
    'Gradient Boosting': GradientBoostingRegressor(
        n_estimators=150, learning_rate=0.1, max_depth=5,
        subsample=0.8, random_state=42
    )
}


def evaluate_model(y_true, y_pred, model_name: str) -> dict:
    """Calculate comprehensive evaluation metrics."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100

    logger.info(f"\n{'='*40}")
    logger.info(f"Model: {model_name}")
    logger.info(f"MAE:   ₹{mae:,.0f}")
    logger.info(f"RMSE:  ₹{rmse:,.0f}")
    logger.info(f"R²:    {r2:.4f}")
    logger.info(f"MAPE:  {mape:.2f}%")

    return {
        'model_name': model_name,
        'mae': float(mae),
        'rmse': float(rmse),
        'r2': float(r2),
        'mape': float(mape)
    }


def train_all_models(X_train, X_test, y_train, y_test, preprocessor):
    """Train all 3 models and compare performance."""
    results = []
    trained_pipelines = {}

    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    for name, regressor in MODELS.items():
        logger.info(f"\nTraining: {name}")

        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', regressor)
        ])

        # Train
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        # Evaluate
        metrics = evaluate_model(y_test, y_pred, name)

        # Cross-validation
        cv_scores = cross_val_score(pipeline, X_train, y_train,
                                     cv=cv, scoring='r2', n_jobs=-1)
        metrics['cv_mean'] = float(cv_scores.mean())
        metrics['cv_std'] = float(cv_scores.std())
        logger.info(f"CV R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

        results.append(metrics)
        trained_pipelines[name] = pipeline

    return results, trained_pipelines


def get_best_model(results: list, trained_pipelines: dict):
    """Select best model based on R² score."""
    best = max(results, key=lambda x: x['r2'])
    logger.info(f"\n✅ Best Model: {best['model_name']} (R²={best['r2']:.4f})")
    return best['model_name'], trained_pipelines[best['model_name']], best


def get_feature_importance(pipeline, feature_names: list, X_test, y_test) -> pd.DataFrame:
    """Extract feature importance from the best model."""
    regressor = pipeline.named_steps['regressor']

    if hasattr(regressor, 'feature_importances_'):
        preprocessor = pipeline.named_steps['preprocessor']
        try:
            cat_features = preprocessor.named_transformers_['cat'].get_feature_names_out()
            num_features = preprocessor.named_transformers_['num'].feature_names_in_
            all_features = list(num_features) + list(cat_features)
        except Exception:
            all_features = [f"feature_{i}" for i in range(len(regressor.feature_importances_))]

        importance_df = pd.DataFrame({
            'feature': all_features[:len(regressor.feature_importances_)],
            'importance': regressor.feature_importances_
        }).sort_values('importance', ascending=False).reset_index(drop=True)

        importance_df['importance_pct'] = (importance_df['importance'] * 100).round(2)
        return importance_df

    # Fallback: permutation importance
    perm = permutation_importance(pipeline, X_test, y_test, n_repeats=10, random_state=42)
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': perm.importances_mean
    }).sort_values('importance', ascending=False).reset_index(drop=True)
    importance_df['importance_pct'] = (importance_df['importance'] / importance_df['importance'].sum() * 100).round(2)
    return importance_df


def save_model(pipeline, model_name: str, metrics: dict, save_dir: str = 'models') -> str:
    """Save model with metadata."""
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = model_name.replace(' ', '_').lower()
    filepath = os.path.join(save_dir, f'{safe_name}_v1_{timestamp}.pkl')

    metadata = {
        'model_name': model_name,
        'version': 'v1',
        'timestamp': timestamp,
        'metrics': metrics,
        'file': filepath
    }

    joblib.dump({'pipeline': pipeline, 'metadata': metadata}, filepath)

    meta_path = os.path.join(save_dir, 'model_registry.json')
    registry = []
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            registry = json.load(f)
    registry.append(metadata)
    with open(meta_path, 'w') as f:
        json.dump(registry, f, indent=2)

    logger.info(f"Model saved: {filepath}")
    return filepath


def load_model(filepath: str):
    """Load a saved model."""
    data = joblib.load(filepath)
    return data['pipeline'], data['metadata']


def generate_training_report(results: list, best_name: str, importance_df: pd.DataFrame) -> str:
    """Generate a formatted training report."""
    lines = [
        "=" * 60,
        "       HOUSE PRICE PREDICTION - TRAINING REPORT",
        "=" * 60,
        f"\nTraining Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"\n{'Model':<25} {'R²':>8} {'MAE (₹)':>15} {'RMSE (₹)':>15} {'MAPE':>8}",
        "-" * 75
    ]

    for r in results:
        marker = " ✅" if r['model_name'] == best_name else "   "
        lines.append(
            f"{r['model_name']:<25}{marker} {r['r2']:>6.4f}  "
            f"₹{r['mae']:>12,.0f}  ₹{r['rmse']:>12,.0f}  {r['mape']:>6.2f}%"
        )

    lines += [
        "\n" + "=" * 60,
        f"  BEST MODEL: {best_name}",
        "=" * 60,
        "\nTOP 5 FEATURE IMPORTANCES:",
        "-" * 40
    ]

    for i, row in importance_df.head(5).iterrows():
        lines.append(f"  {i+1}. {row['feature']:<30} {row['importance_pct']:>6.2f}%")

    return "\n".join(lines)

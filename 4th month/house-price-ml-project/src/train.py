"""
Main Training Script
Run this to train models, evaluate, and save the best model.
Usage: python src/train.py
"""

import os
import sys
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_preprocessing import prepare_data, load_data, engineer_features, validate_data
from model_training import (train_all_models, get_best_model, get_feature_importance,
                             save_model, generate_training_report)


DATA_PATH = 'data/house_prices.csv'
MODEL_DIR = 'models'
PLOTS_DIR = 'docs/plots'
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


def plot_model_comparison(results: list, save_path: str):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    names = [r['model_name'] for r in results]
    colors = ['#3498db', '#2ecc71', '#e74c3c']

    metrics = [('r2', 'R² Score (Higher = Better)'),
               ('mae', 'MAE - ₹ (Lower = Better)'),
               ('mape', 'MAPE % (Lower = Better)')]

    for ax, (metric, title) in zip(axes, metrics):
        vals = [r[metric] for r in results]
        bars = ax.bar(names, vals, color=colors)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=15, ha='right', fontsize=9)
        for bar, val in zip(bars, vals):
            label = f'{val:.4f}' if metric == 'r2' else f'{val:,.0f}' if metric == 'mae' else f'{val:.2f}%'
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                    label, ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_feature_importance(importance_df: pd.DataFrame, save_path: str):
    top10 = importance_df.head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(top10)))[::-1]
    bars = ax.barh(top10['feature'][::-1], top10['importance_pct'][::-1], color=colors)
    for bar, val in zip(bars, top10['importance_pct'][::-1]):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}%', va='center', fontsize=10)
    ax.set_xlabel('Importance (%)', fontsize=12)
    ax.set_title('Feature Importance - Top 10', fontsize=14, fontweight='bold')
    ax.set_xlim(0, top10['importance_pct'].max() * 1.2)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_actual_vs_predicted(pipeline, X_test, y_test, save_path: str):
    y_pred = pipeline.predict(X_test)
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.scatter(y_test / 1e6, y_pred / 1e6, alpha=0.6, edgecolors='white', s=60, color='#3498db')
    mn = min(y_test.min(), y_pred.min()) / 1e6
    mx = max(y_test.max(), y_pred.max()) / 1e6
    ax.plot([mn, mx], [mn, mx], 'r--', linewidth=2, label='Perfect Prediction')
    ax.set_xlabel('Actual Price (₹ Million)', fontsize=12)
    ax.set_ylabel('Predicted Price (₹ Million)', fontsize=12)
    ax.set_title('Actual vs Predicted Prices', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_price_distribution(df: pd.DataFrame, save_path: str):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist(df['price'] / 1e6, bins=30, color='#3498db', edgecolor='white')
    axes[0].set_xlabel('Price (₹ Million)', fontsize=12)
    axes[0].set_ylabel('Count', fontsize=12)
    axes[0].set_title('Price Distribution', fontsize=13, fontweight='bold')

    loc_avg = df.groupby('location')['price'].mean().sort_values(ascending=False) / 1e6
    axes[1].bar(loc_avg.index, loc_avg.values, color=['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6'])
    axes[1].set_ylabel('Average Price (₹ Million)', fontsize=12)
    axes[1].set_title('Average Price by Location', fontsize=13, fontweight='bold')
    axes[1].tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def main():
    print("\n" + "="*60)
    print("   HOUSE PRICE PREDICTION - TRAINING PIPELINE")
    print("="*60)

    # 1. Prepare data
    X_train, X_test, y_train, y_test, preprocessor, num_features, cat_features = prepare_data(DATA_PATH)

    # 2. Load full df for EDA plots
    df_raw = load_data(DATA_PATH)
    df_eng = engineer_features(validate_data(df_raw))
    plot_price_distribution(df_eng, f'{PLOTS_DIR}/price_distribution.png')

    # 3. Train all 3 models
    results, trained_pipelines = train_all_models(X_train, X_test, y_train, y_test, preprocessor)

    # 4. Model comparison plot
    plot_model_comparison(results, f'{PLOTS_DIR}/model_comparison.png')

    # 5. Best model
    best_name, best_pipeline, best_metrics = get_best_model(results, trained_pipelines)

    # 6. Feature importance
    all_features = num_features + cat_features
    importance_df = get_feature_importance(best_pipeline, all_features, X_test, y_test)
    plot_feature_importance(importance_df, f'{PLOTS_DIR}/feature_importance.png')

    # 7. Actual vs predicted
    plot_actual_vs_predicted(best_pipeline, X_test, y_test, f'{PLOTS_DIR}/actual_vs_predicted.png')

    # 8. Save model
    model_path = save_model(best_pipeline, best_name, best_metrics, MODEL_DIR)

    # 9. Save results JSON
    results_data = {
        'all_models': results,
        'best_model': best_name,
        'best_metrics': best_metrics,
        'model_path': model_path,
        'feature_importance': importance_df.to_dict('records')
    }
    with open(f'{MODEL_DIR}/training_results.json', 'w') as f:
        json.dump(results_data, f, indent=2)

    # 10. Print report
    report = generate_training_report(results, best_name, importance_df)
    print(report)

    print(f"\n✅ Training complete! Model saved to: {model_path}")
    print(f"📊 Plots saved to: {PLOTS_DIR}/")
    return best_pipeline, results, importance_df


if __name__ == '__main__':
    main()

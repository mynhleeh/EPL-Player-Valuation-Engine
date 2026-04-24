import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from .config import CHARTS_PATH


def plot_comparison(y_test: np.ndarray, y_pred: np.ndarray) -> None:
    y_test = np.expm1(y_test)
    y_pred = np.expm1(y_pred)

    plt.figure(figsize=(9, 7))
    sns.scatterplot(x=y_test, y=y_pred, alpha=0.6, edgecolor='w', s=60, label='Actual vs Predicted')

    min_val = min(min(y_test), min(y_pred))
    max_val = max(max(y_test), max(y_pred))

    plt.plot(
        [min_val, max_val], [min_val, max_val],
        color='red', linestyle='--', lw=2,
        label='Perfect Fit (y=x)'
    )

    plt.title('Actual vs Predicted Transfer Values')
    plt.xlabel('Actual Price (Million Euro)')
    plt.ylabel('Predicted Price (Million Euro)')
    
    plt.legend(loc='lower right')
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(str(CHARTS_PATH / "actual_vs_predicted.png"), dpi=300)
    plt.close()


def plot_importance(importance: np.ndarray, x_test_col: pd.Index) -> None:
    df = pd.DataFrame({
        'Feature': x_test_col,
        'Importance': importance
    })
    df = df.sort_values(by='Importance', ascending=False)
    
    sns.set_theme(style='whitegrid')
    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=df,
        x='Importance',
        y='Feature',
        hue='Feature',
        estimator='mean',
        errorbar=None,
        palette='viridis',
        legend=False,
    )

    plt.title("Features Importance")
    plt.xlabel('Importance')
    plt.ylabel("Feature")
    plt.savefig(str(CHARTS_PATH / "feature_importance.png"))
    plt.close()


def plot_residuals(y_test: np.ndarray, y_pred: np.ndarray) -> None:
    y_test_actual = np.expm1(y_test)
    y_pred_actual = np.expm1(y_pred)
    residuals = y_test_actual - y_pred_actual

    plt.figure(figsize=(9, 7))
    sns.histplot(residuals, kde=True, color='purple')
    plt.axvline(x=0, color='red', linestyle='--', linewidth=2)
    
    plt.title('Distribution of Residuals')
    plt.xlabel('Residual Error (Million Euro)')
    plt.ylabel('Frequency')

    plt.savefig(str(CHARTS_PATH / "residual_analysis.png"))
    plt.close()

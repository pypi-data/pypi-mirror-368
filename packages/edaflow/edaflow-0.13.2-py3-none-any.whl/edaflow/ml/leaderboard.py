"""
edaflow.ml.leaderboard - Model comparison and ranking functionality

This module provides utilities for comparing multiple models, ranking them
based on performance metrics, and displaying comprehensive leaderboards.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.base import BaseEstimator
import matplotlib.pyplot as plt
import seaborn as sns
import time
import warnings


def compare_models(
    models: Dict[str, BaseEstimator],
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
    y_train: pd.Series,
    y_val: pd.Series,
    problem_type: str = 'auto',
    metrics: Optional[List[str]] = None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Compare multiple models across various performance metrics.
    
    Parameters:
    -----------
    models : Dict[str, BaseEstimator]
        Dictionary of model name -> fitted model pairs
    X_train : pd.DataFrame
        Training features
    X_val : pd.DataFrame
        Validation features  
    y_train : pd.Series
        Training target
    y_val : pd.Series
        Validation target
    problem_type : str, default='auto'
        'classification', 'regression', or 'auto' to detect
    metrics : List[str], optional
        Specific metrics to calculate. If None, uses default metrics
    verbose : bool, default=True
        Whether to print comparison progress
        
    Returns:
    --------
    pd.DataFrame
        Comparison results with models as rows and metrics as columns
    """
    
    if verbose:
        print("🏆 Comparing Models...")
        print(f"📊 Models to compare: {len(models)}")
    
    # Auto-detect problem type
    if problem_type == 'auto':
        problem_type = _detect_problem_type(y_train)
    
    # Set default metrics based on problem type
    if metrics is None:
        if problem_type == 'classification':
            metrics = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
        else:
            metrics = ['mse', 'mae', 'r2']
    
    results = []
    
    for model_name, model in models.items():
        if verbose:
            print(f"⚡ Evaluating {model_name}...")
        
        start_time = time.time()
        
        # Make predictions
        try:
            y_pred = model.predict(X_val)
            if problem_type == 'classification' and hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(X_val)
        except Exception as e:
            if verbose:
                print(f"❌ Error with {model_name}: {str(e)}")
            continue
        
        # Calculate metrics
        model_results = {'model': model_name}
        
        for metric in metrics:
            try:
                if problem_type == 'classification':
                    score = _calculate_classification_metric(metric, y_val, y_pred, y_proba if 'y_proba' in locals() else None)
                else:
                    score = _calculate_regression_metric(metric, y_val, y_pred)
                
                model_results[metric] = score
            except Exception as e:
                if verbose:
                    print(f"⚠️ Could not calculate {metric} for {model_name}: {str(e)}")
                model_results[metric] = np.nan
        
        # Calculate training time (if available)
        end_time = time.time()
        model_results['eval_time_ms'] = (end_time - start_time) * 1000
        
        # Add model complexity info if available
        if hasattr(model, 'get_params'):
            n_params = len(str(model.get_params()))
            model_results['complexity'] = n_params
        
        results.append(model_results)
    
    # Convert to DataFrame
    comparison_df = pd.DataFrame(results)
    
    if verbose:
        print(f"✅ Comparison complete! {len(comparison_df)} models evaluated.")
    
    return comparison_df


def rank_models(
    comparison_df: pd.DataFrame,
    primary_metric: str,
    ascending: bool = False,
    secondary_metrics: Optional[List[str]] = None,
    weights: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    Rank models based on performance metrics.
    
    Parameters:
    -----------
    comparison_df : pd.DataFrame
        Results from compare_models()
    primary_metric : str
        Main metric to rank by
    ascending : bool, default=False
        Whether to sort in ascending order (True for error metrics)
    secondary_metrics : List[str], optional
        Additional metrics to consider for tie-breaking
    weights : Dict[str, float], optional
        Weights for weighted ranking across multiple metrics
        
    Returns:
    --------
    pd.DataFrame
        Ranked models with additional ranking columns
    """
    
    ranked_df = comparison_df.copy()
    
    # Validate primary metric exists
    if primary_metric not in ranked_df.columns:
        raise ValueError(f"Primary metric '{primary_metric}' not found in comparison results")
    
    # Simple ranking by primary metric
    if weights is None:
        ranked_df = ranked_df.sort_values(
            by=[primary_metric] + (secondary_metrics or []),
            ascending=ascending
        ).reset_index(drop=True)
        
        ranked_df['rank'] = range(1, len(ranked_df) + 1)
        ranked_df['rank_score'] = ranked_df[primary_metric]
    
    # Weighted ranking across multiple metrics
    else:
        # Normalize metrics to 0-1 scale
        metric_columns = [col for col in weights.keys() if col in ranked_df.columns]
        normalized_df = ranked_df[metric_columns].copy()
        
        for metric in metric_columns:
            col_values = ranked_df[metric].dropna()
            if len(col_values) > 0:
                min_val, max_val = col_values.min(), col_values.max()
                if max_val > min_val:
                    # Normalize to 0-1, flip if lower is better (like error metrics)
                    if metric.lower() in ['mse', 'mae', 'rmse', 'error']:
                        normalized_df[metric] = 1 - (ranked_df[metric] - min_val) / (max_val - min_val)
                    else:
                        normalized_df[metric] = (ranked_df[metric] - min_val) / (max_val - min_val)
        
        # Calculate weighted score
        weighted_scores = []
        for idx, row in normalized_df.iterrows():
            score = sum(row[metric] * weights[metric] for metric in metric_columns if not pd.isna(row[metric]))
            weighted_scores.append(score)
        
        ranked_df['rank_score'] = weighted_scores
        ranked_df = ranked_df.sort_values('rank_score', ascending=False).reset_index(drop=True)
        ranked_df['rank'] = range(1, len(ranked_df) + 1)
    
    return ranked_df


def display_leaderboard(
    ranked_df: pd.DataFrame,
    top_n: int = 10,
    show_metrics: Optional[List[str]] = None,
    highlight_best: bool = True,
    figsize: Tuple[int, int] = (12, 8)
) -> None:
    """
    Display a visual leaderboard of model performance.
    
    Parameters:
    -----------
    ranked_df : pd.DataFrame
        Ranked results from rank_models()
    top_n : int, default=10
        Number of top models to display
    show_metrics : List[str], optional
        Specific metrics to show. If None, shows all numeric metrics
    highlight_best : bool, default=True
        Whether to highlight the best performing model
    figsize : Tuple[int, int], default=(12, 8)
        Figure size for the visualization
    """
    
    print("🏆 MODEL LEADERBOARD 🏆")
    print("=" * 50)
    
    display_df = ranked_df.head(top_n).copy()
    
    # Select metrics to show
    if show_metrics is None:
        numeric_cols = display_df.select_dtypes(include=[np.number]).columns
        show_metrics = [col for col in numeric_cols if col not in ['rank', 'complexity', 'eval_time_ms']]
    
    # Create display table
    table_cols = ['rank', 'model'] + show_metrics
    if 'eval_time_ms' in display_df.columns:
        table_cols.append('eval_time_ms')
    
    display_table = display_df[table_cols].copy()
    
    # Format numeric columns
    for col in show_metrics:
        if col in display_table.columns:
            display_table[col] = display_table[col].round(4)
    
    if 'eval_time_ms' in display_table.columns:
        display_table['eval_time_ms'] = display_table['eval_time_ms'].round(1)
    
    # Print text leaderboard
    print(display_table.to_string(index=False))
    print("=" * 50)
    
    if highlight_best and len(display_df) > 0:
        best_model = display_df.iloc[0]
        print(f"🥇 WINNER: {best_model['model']}")
        if 'rank_score' in best_model:
            print(f"📊 Score: {best_model['rank_score']:.4f}")
        print()
    
    # Create visualization
    if len(show_metrics) > 0:
        fig, axes = plt.subplots(1, min(len(show_metrics), 3), figsize=figsize)
        if len(show_metrics) == 1:
            axes = [axes]
        elif len(show_metrics) == 2:
            axes = axes
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(display_df)))
        
        for i, metric in enumerate(show_metrics[:3]):
            ax = axes[i] if len(show_metrics) > 1 else axes[0]
            
            bars = ax.barh(display_df['model'], display_df[metric], color=colors)
            ax.set_xlabel(metric.upper())
            ax.set_title(f'Model Performance: {metric.upper()}')
            
            # Highlight best model
            if highlight_best:
                bars[0].set_color('gold')
                bars[0].set_edgecolor('black')
                bars[0].set_linewidth(2)
            
            # Add value labels
            for j, (model, value) in enumerate(zip(display_df['model'], display_df[metric])):
                if not pd.isna(value):
                    ax.text(value, j, f' {value:.3f}', va='center')
        
        plt.tight_layout()
        plt.show()


def export_model_comparison(
    comparison_df: pd.DataFrame,
    filepath: str,
    include_config: bool = True,
    format: str = 'csv'
) -> None:
    """
    Export model comparison results to file.
    
    Parameters:
    -----------
    comparison_df : pd.DataFrame
        Comparison results to export
    filepath : str
        Path where to save the file
    include_config : bool, default=True
        Whether to include experiment configuration
    format : str, default='csv'
        Export format ('csv', 'excel', 'json')
    """
    
    print(f"💾 Exporting comparison results to {filepath}...")
    
    if format.lower() == 'csv':
        comparison_df.to_csv(filepath, index=False)
    elif format.lower() == 'excel':
        comparison_df.to_excel(filepath, index=False)
    elif format.lower() == 'json':
        comparison_df.to_json(filepath, indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    print("✅ Export completed!")


def _detect_problem_type(y: pd.Series) -> str:
    """Detect if problem is classification or regression."""
    if y.dtype == 'object' or pd.api.types.is_categorical_dtype(y):
        return 'classification'
    
    if y.dtype in ['int64', 'int32']:
        unique_ratio = len(y.unique()) / len(y)
        if unique_ratio < 0.05 or len(y.unique()) <= 20:
            return 'classification'
    
    return 'regression'


def _calculate_classification_metric(metric: str, y_true: pd.Series, y_pred: np.ndarray, y_proba: Optional[np.ndarray] = None) -> float:
    """Calculate classification metric."""
    metric = metric.lower()
    
    if metric == 'accuracy':
        return accuracy_score(y_true, y_pred)
    elif metric == 'precision':
        return precision_score(y_true, y_pred, average='weighted', zero_division=0)
    elif metric == 'recall':
        return recall_score(y_true, y_pred, average='weighted', zero_division=0)
    elif metric == 'f1':
        return f1_score(y_true, y_pred, average='weighted', zero_division=0)
    elif metric == 'roc_auc':
        if y_proba is not None and len(np.unique(y_true)) == 2:
            return roc_auc_score(y_true, y_proba[:, 1])
        else:
            return np.nan
    else:
        raise ValueError(f"Unknown classification metric: {metric}")


def _calculate_regression_metric(metric: str, y_true: pd.Series, y_pred: np.ndarray) -> float:
    """Calculate regression metric."""
    metric = metric.lower()
    
    if metric == 'mse':
        return mean_squared_error(y_true, y_pred)
    elif metric == 'mae':
        return mean_absolute_error(y_true, y_pred)
    elif metric == 'rmse':
        return np.sqrt(mean_squared_error(y_true, y_pred))
    elif metric == 'r2':
        return r2_score(y_true, y_pred)
    else:
        raise ValueError(f"Unknown regression metric: {metric}")

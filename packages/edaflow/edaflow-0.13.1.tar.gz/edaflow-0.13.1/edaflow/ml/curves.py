"""
edaflow.ml.curves - Learning curves and performance visualization

This module provides utilities for creating various performance visualizations
including learning curves, validation curves, ROC curves, and feature importance plots.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import learning_curve, validation_curve
from sklearn.metrics import roc_curve, auc, precision_recall_curve, confusion_matrix
from sklearn.base import BaseEstimator
import warnings


def plot_learning_curves(
    model: BaseEstimator,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    cv: int = 5,
    scoring: str = 'auto',
    train_sizes: Optional[np.ndarray] = None,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
    show_std: bool = True
) -> plt.Figure:
    """
    Plot learning curves to analyze model performance vs training set size.
    
    Parameters:
    -----------
    model : BaseEstimator
        The model to analyze
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    cv : int, default=5
        Number of cross-validation folds
    scoring : str, default='auto'
        Scoring metric
    train_sizes : np.ndarray, optional
        Training set sizes to use
    title : str, optional
        Plot title
    figsize : Tuple[int, int], default=(10, 6)
        Figure size
    show_std : bool, default=True
        Whether to show standard deviation bands
        
    Returns:
    --------
    plt.Figure
        The matplotlib figure
    """
    
    # Auto-detect scoring metric
    if scoring == 'auto':
        scoring = _detect_scoring_metric(y_train)
    
    # Default training sizes
    if train_sizes is None:
        train_sizes = np.linspace(0.1, 1.0, 10)
    
    # Calculate learning curves
    train_sizes_abs, train_scores, val_scores = learning_curve(
        model, X_train, y_train,
        cv=cv,
        train_sizes=train_sizes,
        scoring=scoring,
        n_jobs=-1,
        random_state=42
    )
    
    # Calculate mean and std
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot mean scores
    ax.plot(train_sizes_abs, train_mean, 'o-', color='blue', label='Training score')
    ax.plot(train_sizes_abs, val_mean, 'o-', color='red', label='Validation score')
    
    # Add standard deviation bands
    if show_std:
        ax.fill_between(train_sizes_abs, train_mean - train_std, train_mean + train_std,
                       alpha=0.2, color='blue')
        ax.fill_between(train_sizes_abs, val_mean - val_std, val_mean + val_std,
                       alpha=0.2, color='red')
    
    # Formatting
    ax.set_xlabel('Training Set Size')
    ax.set_ylabel(f'Score ({scoring})')
    ax.set_title(title or f'Learning Curves - {type(model).__name__}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_validation_curves(
    model: BaseEstimator,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    param_name: str,
    param_range: List[Any],
    cv: int = 5,
    scoring: str = 'auto',
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
    log_scale: bool = False
) -> plt.Figure:
    """
    Plot validation curves for hyperparameter analysis.
    
    Parameters:
    -----------
    model : BaseEstimator
        The model to analyze
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    param_name : str
        Name of the parameter to vary
    param_range : List[Any]
        Range of parameter values to test
    cv : int, default=5
        Number of cross-validation folds
    scoring : str, default='auto'
        Scoring metric
    title : str, optional
        Plot title
    figsize : Tuple[int, int], default=(10, 6)
        Figure size
    log_scale : bool, default=False
        Whether to use log scale for x-axis
        
    Returns:
    --------
    plt.Figure
        The matplotlib figure
    """
    
    # Auto-detect scoring metric
    if scoring == 'auto':
        scoring = _detect_scoring_metric(y_train)
    
    # Calculate validation curves
    train_scores, val_scores = validation_curve(
        model, X_train, y_train,
        param_name=param_name,
        param_range=param_range,
        cv=cv,
        scoring=scoring,
        n_jobs=-1
    )
    
    # Calculate mean and std
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot mean scores
    ax.plot(param_range, train_mean, 'o-', color='blue', label='Training score')
    ax.plot(param_range, val_mean, 'o-', color='red', label='Validation score')
    
    # Add standard deviation bands
    ax.fill_between(param_range, train_mean - train_std, train_mean + train_std,
                   alpha=0.2, color='blue')
    ax.fill_between(param_range, val_mean - val_std, val_mean + val_std,
                   alpha=0.2, color='red')
    
    # Formatting
    if log_scale:
        ax.set_xscale('log')
    ax.set_xlabel(param_name)
    ax.set_ylabel(f'Score ({scoring})')
    ax.set_title(title or f'Validation Curves - {param_name}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_roc_curves(
    models: Dict[str, BaseEstimator],
    X_val: pd.DataFrame,
    y_val: pd.Series,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Plot ROC curves for multiple models (binary classification only).
    
    Parameters:
    -----------
    models : Dict[str, BaseEstimator]
        Dictionary of model name -> fitted model pairs
    X_val : pd.DataFrame
        Validation features
    y_val : pd.Series
        Validation target
    title : str, optional
        Plot title
    figsize : Tuple[int, int], default=(10, 8)
        Figure size
        
    Returns:
    --------
    plt.Figure
        The matplotlib figure
    """
    
    # Check if binary classification
    if len(y_val.unique()) != 2:
        raise ValueError("ROC curves are only available for binary classification")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot ROC curve for each model
    for model_name, model in models.items():
        try:
            # Get prediction probabilities
            if hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(X_val)[:, 1]
            elif hasattr(model, 'decision_function'):
                y_proba = model.decision_function(X_val)
            else:
                warnings.warn(f"Model {model_name} doesn't support probability predictions")
                continue
            
            # Calculate ROC curve
            fpr, tpr, _ = roc_curve(y_val, y_proba)
            roc_auc = auc(fpr, tpr)
            
            # Plot
            ax.plot(fpr, tpr, label=f'{model_name} (AUC = {roc_auc:.3f})')
            
        except Exception as e:
            warnings.warn(f"Could not plot ROC curve for {model_name}: {str(e)}")
            continue
    
    # Plot diagonal line
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Random Classifier')
    
    # Formatting
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title(title or 'ROC Curves Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_precision_recall_curves(
    models: Dict[str, BaseEstimator],
    X_val: pd.DataFrame,
    y_val: pd.Series,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Plot Precision-Recall curves for multiple models.
    
    Parameters:
    -----------
    models : Dict[str, BaseEstimator]
        Dictionary of model name -> fitted model pairs
    X_val : pd.DataFrame
        Validation features
    y_val : pd.Series
        Validation target
    title : str, optional
        Plot title
    figsize : Tuple[int, int], default=(10, 8)
        Figure size
        
    Returns:
    --------
    plt.Figure
        The matplotlib figure
    """
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate baseline (random classifier)
    baseline_precision = (y_val == 1).sum() / len(y_val)
    
    # Plot PR curve for each model
    for model_name, model in models.items():
        try:
            # Get prediction probabilities
            if hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(X_val)[:, 1]
            elif hasattr(model, 'decision_function'):
                y_proba = model.decision_function(X_val)
            else:
                warnings.warn(f"Model {model_name} doesn't support probability predictions")
                continue
            
            # Calculate PR curve
            precision, recall, _ = precision_recall_curve(y_val, y_proba)
            pr_auc = auc(recall, precision)
            
            # Plot
            ax.plot(recall, precision, label=f'{model_name} (AUC = {pr_auc:.3f})')
            
        except Exception as e:
            warnings.warn(f"Could not plot PR curve for {model_name}: {str(e)}")
            continue
    
    # Plot baseline
    ax.axhline(y=baseline_precision, color='k', linestyle='--', alpha=0.5, 
              label=f'Random Classifier (P = {baseline_precision:.3f})')
    
    # Formatting
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_title(title or 'Precision-Recall Curves Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_confusion_matrix(
    model: BaseEstimator,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    normalize: bool = False,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (8, 6)
) -> plt.Figure:
    """
    Plot confusion matrix for a classification model.
    
    Parameters:
    -----------
    model : BaseEstimator
        Fitted classification model
    X_val : pd.DataFrame
        Validation features
    y_val : pd.Series
        Validation target
    normalize : bool, default=False
        Whether to normalize the confusion matrix
    title : str, optional
        Plot title
    figsize : Tuple[int, int], default=(8, 6)
        Figure size
        
    Returns:
    --------
    plt.Figure
        The matplotlib figure
    """
    
    # Make predictions
    y_pred = model.predict(X_val)
    
    # Calculate confusion matrix
    cm = confusion_matrix(y_val, y_pred)
    
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot heatmap
    sns.heatmap(cm, annot=True, fmt='.2f' if normalize else 'd', 
                cmap='Blues', ax=ax, square=True)
    
    # Formatting
    ax.set_xlabel('Predicted Label')
    ax.set_ylabel('True Label')
    ax.set_title(title or f'Confusion Matrix - {type(model).__name__}')
    
    # Add class labels if available
    classes = sorted(y_val.unique())
    ax.set_xticklabels(classes)
    ax.set_yticklabels(classes)
    
    plt.tight_layout()
    return fig


def plot_feature_importance(
    model: BaseEstimator,
    feature_names: List[str],
    top_n: int = 20,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Plot feature importance for models that support it.
    
    Parameters:
    -----------
    model : BaseEstimator
        Fitted model with feature_importances_ attribute
    feature_names : List[str]
        Names of the features
    top_n : int, default=20
        Number of top features to display
    title : str, optional
        Plot title
    figsize : Tuple[int, int], default=(10, 8)
        Figure size
        
    Returns:
    --------
    plt.Figure
        The matplotlib figure
    """
    
    # Check if model has feature importance
    if not hasattr(model, 'feature_importances_'):
        raise ValueError(f"Model {type(model).__name__} doesn't have feature_importances_ attribute")
    
    # Get feature importance
    importance = model.feature_importances_
    
    # Create feature importance DataFrame
    feature_imp_df = pd.DataFrame({
        'feature': feature_names[:len(importance)],
        'importance': importance
    }).sort_values('importance', ascending=True)
    
    # Select top N features
    if len(feature_imp_df) > top_n:
        feature_imp_df = feature_imp_df.tail(top_n)
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Horizontal bar plot
    bars = ax.barh(feature_imp_df['feature'], feature_imp_df['importance'])
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
               f'{width:.3f}', ha='left', va='center')
    
    # Formatting
    ax.set_xlabel('Feature Importance')
    ax.set_title(title or f'Feature Importance - {type(model).__name__}')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    return fig


def _detect_scoring_metric(y: pd.Series) -> str:
    """Detect appropriate scoring metric based on target variable."""
    
    # Check if classification
    if y.dtype == 'object' or pd.api.types.is_categorical_dtype(y):
        return 'accuracy'
    
    if y.dtype in ['int64', 'int32']:
        unique_ratio = len(y.unique()) / len(y)
        if unique_ratio < 0.05 or len(y.unique()) <= 20:
            return 'accuracy'
    
    # Default to regression
    return 'neg_mean_squared_error'

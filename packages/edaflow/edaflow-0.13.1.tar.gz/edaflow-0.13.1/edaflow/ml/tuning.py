"""
edaflow.ml.tuning - Automated hyperparameter optimization

This module provides utilities for automated hyperparameter tuning using
various optimization strategies including grid search, random search, and
Bayesian optimization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.base import BaseEstimator, clone
import matplotlib.pyplot as plt
import seaborn as sns
import time
import warnings


def optimize_hyperparameters(
    model: BaseEstimator,
    param_distributions: Dict[str, Any],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    cv: int = 5,
    scoring: str = 'auto',
    n_iter: int = 50,
    method: str = 'random',
    verbose: bool = True,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Optimize hyperparameters using various search strategies.
    
    Parameters:
    -----------
    model : BaseEstimator
        The base model to optimize
    param_distributions : Dict[str, Any]
        Parameter distributions to search over
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    cv : int, default=5
        Number of cross-validation folds
    scoring : str, default='auto'
        Scoring metric ('auto' detects based on problem type)
    n_iter : int, default=50
        Number of iterations for random/bayesian search
    method : str, default='random'
        Search method ('grid', 'random', 'bayesian')
    verbose : bool, default=True
        Whether to print optimization progress
    random_state : int, default=42
        Random seed for reproducibility
        
    Returns:
    --------
    Dict[str, Any]
        Dictionary containing best model, parameters, and optimization results
    """
    
    if verbose:
        print(f"🔍 Optimizing hyperparameters using {method} search...")
        print(f"📊 Parameters to optimize: {len(param_distributions)}")
        print(f"🔄 Cross-validation folds: {cv}")
    
    # Auto-detect scoring metric
    if scoring == 'auto':
        scoring = _detect_scoring_metric(y_train)
        if verbose:
            print(f"📈 Scoring metric: {scoring}")
    
    start_time = time.time()
    
    # Choose optimization method
    if method.lower() == 'grid':
        optimizer = GridSearchCV(
            estimator=model,
            param_grid=param_distributions,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=1 if verbose else 0
        )
        total_combinations = np.prod([len(v) if isinstance(v, list) else 1 
                                    for v in param_distributions.values()])
        if verbose:
            print(f"🎯 Grid search: {total_combinations} combinations")
    
    elif method.lower() == 'random':
        optimizer = RandomizedSearchCV(
            estimator=model,
            param_distributions=param_distributions,
            n_iter=n_iter,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=1 if verbose else 0,
            random_state=random_state
        )
        if verbose:
            print(f"🎲 Random search: {n_iter} iterations")
    
    elif method.lower() == 'bayesian':
        try:
            return _bayesian_optimization(
                model, param_distributions, X_train, y_train,
                cv, scoring, n_iter, verbose, random_state
            )
        except ImportError:
            warnings.warn("scikit-optimize not available. Falling back to random search.")
            optimizer = RandomizedSearchCV(
                estimator=model,
                param_distributions=param_distributions,
                n_iter=n_iter,
                cv=cv,
                scoring=scoring,
                n_jobs=-1,
                verbose=1 if verbose else 0,
                random_state=random_state
            )
    else:
        raise ValueError(f"Unknown optimization method: {method}")
    
    # Perform optimization
    try:
        optimizer.fit(X_train, y_train)
        
        end_time = time.time()
        optimization_time = end_time - start_time
        
        if verbose:
            print(f"✅ Optimization completed in {optimization_time:.2f} seconds")
            print(f"🏆 Best score: {optimizer.best_score_:.4f}")
            print(f"🎯 Best parameters:")
            for param, value in optimizer.best_params_.items():
                print(f"   {param}: {value}")
        
        # Prepare results
        results = {
            'best_model': optimizer.best_estimator_,
            'best_params': optimizer.best_params_,
            'best_score': optimizer.best_score_,
            'cv_results': pd.DataFrame(optimizer.cv_results_),
            'optimization_time': optimization_time,
            'method': method,
            'scoring': scoring,
            'n_folds': cv,
            'model_name': type(model).__name__
        }
        
        return results
        
    except Exception as e:
        if verbose:
            print(f"❌ Optimization failed: {str(e)}")
        raise


def grid_search_models(
    models: Dict[str, BaseEstimator],
    param_grids: Dict[str, Dict[str, Any]],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    cv: int = 5,
    scoring: str = 'auto',
    verbose: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Perform grid search optimization for multiple models.
    
    Parameters:
    -----------
    models : Dict[str, BaseEstimator]
        Dictionary of model name -> model pairs
    param_grids : Dict[str, Dict[str, Any]]
        Dictionary of model name -> parameter grid pairs
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    cv : int, default=5
        Number of cross-validation folds
    scoring : str, default='auto'
        Scoring metric
    verbose : bool, default=True
        Whether to print progress
        
    Returns:
    --------
    Dict[str, Dict[str, Any]]
        Dictionary of model name -> optimization results pairs
    """
    
    if verbose:
        print("🔍 Grid Search for Multiple Models")
        print(f"📊 Models to optimize: {len(models)}")
    
    results = {}
    
    for model_name, model in models.items():
        if model_name not in param_grids:
            if verbose:
                print(f"⚠️ No parameter grid for {model_name}, skipping...")
            continue
        
        if verbose:
            print(f"\n🎯 Optimizing {model_name}...")
        
        try:
            model_results = optimize_hyperparameters(
                model=model,
                param_distributions=param_grids[model_name],
                X_train=X_train,
                y_train=y_train,
                cv=cv,
                scoring=scoring,
                method='grid',
                verbose=verbose
            )
            results[model_name] = model_results
            
        except Exception as e:
            if verbose:
                print(f"❌ Failed to optimize {model_name}: {str(e)}")
            continue
    
    if verbose:
        print(f"\n✅ Completed optimization for {len(results)} models")
        
        # Show comparison
        if len(results) > 1:
            print("\n🏆 OPTIMIZATION RESULTS:")
            comparison = []
            for name, result in results.items():
                comparison.append({
                    'model': name,
                    'best_score': result['best_score'],
                    'optimization_time': result['optimization_time']
                })
            
            comparison_df = pd.DataFrame(comparison).sort_values('best_score', ascending=False)
            print(comparison_df.to_string(index=False))
    
    return results


def random_search_models(
    models: Dict[str, BaseEstimator],
    param_distributions: Dict[str, Dict[str, Any]],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_iter: int = 50,
    cv: int = 5,
    scoring: str = 'auto',
    verbose: bool = True,
    random_state: int = 42
) -> Dict[str, Dict[str, Any]]:
    """
    Perform random search optimization for multiple models.
    
    Parameters:
    -----------
    models : Dict[str, BaseEstimator]
        Dictionary of model name -> model pairs
    param_distributions : Dict[str, Dict[str, Any]]
        Dictionary of model name -> parameter distributions pairs
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    n_iter : int, default=50
        Number of random search iterations
    cv : int, default=5
        Number of cross-validation folds
    scoring : str, default='auto'
        Scoring metric
    verbose : bool, default=True
        Whether to print progress
    random_state : int, default=42
        Random seed for reproducibility
        
    Returns:
    --------
    Dict[str, Dict[str, Any]]
        Dictionary of model name -> optimization results pairs
    """
    
    if verbose:
        print("🎲 Random Search for Multiple Models")
        print(f"📊 Models to optimize: {len(models)}")
        print(f"🔄 Iterations per model: {n_iter}")
    
    results = {}
    
    for model_name, model in models.items():
        if model_name not in param_distributions:
            if verbose:
                print(f"⚠️ No parameter distribution for {model_name}, skipping...")
            continue
        
        if verbose:
            print(f"\n🎯 Optimizing {model_name}...")
        
        try:
            model_results = optimize_hyperparameters(
                model=model,
                param_distributions=param_distributions[model_name],
                X_train=X_train,
                y_train=y_train,
                cv=cv,
                scoring=scoring,
                n_iter=n_iter,
                method='random',
                verbose=verbose,
                random_state=random_state
            )
            results[model_name] = model_results
            
        except Exception as e:
            if verbose:
                print(f"❌ Failed to optimize {model_name}: {str(e)}")
            continue
    
    return results


def bayesian_optimization(
    model: BaseEstimator,
    param_space: Dict[str, Any],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_calls: int = 50,
    cv: int = 5,
    scoring: str = 'auto',
    verbose: bool = True,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Perform Bayesian optimization using scikit-optimize.
    
    Parameters:
    -----------
    model : BaseEstimator
        The base model to optimize
    param_space : Dict[str, Any]
        Parameter space definition (requires skopt)
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    n_calls : int, default=50
        Number of optimization calls
    cv : int, default=5
        Number of cross-validation folds
    scoring : str, default='auto'
        Scoring metric
    verbose : bool, default=True
        Whether to print progress
    random_state : int, default=42
        Random seed for reproducibility
        
    Returns:
    --------
    Dict[str, Any]
        Optimization results including best parameters and convergence plot
    """
    
    try:
        return _bayesian_optimization(
            model, param_space, X_train, y_train,
            cv, scoring, n_calls, verbose, random_state
        )
    except ImportError:
        raise ImportError(
            "scikit-optimize is required for Bayesian optimization. "
            "Install with: pip install scikit-optimize"
        )


def _bayesian_optimization(
    model: BaseEstimator,
    param_space: Dict[str, Any],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    cv: int,
    scoring: str,
    n_calls: int,
    verbose: bool,
    random_state: int
) -> Dict[str, Any]:
    """Internal Bayesian optimization implementation."""
    
    try:
        from skopt import gp_minimize
        from skopt.space import Real, Integer, Categorical
        from skopt.utils import use_named_args
    except ImportError:
        raise ImportError("scikit-optimize not available")
    
    # Convert parameter space to skopt format
    dimensions = []
    param_names = []
    
    for param_name, param_range in param_space.items():
        param_names.append(param_name)
        
        if isinstance(param_range, tuple) and len(param_range) == 2:
            if isinstance(param_range[0], int) and isinstance(param_range[1], int):
                dimensions.append(Integer(param_range[0], param_range[1], name=param_name))
            else:
                dimensions.append(Real(param_range[0], param_range[1], name=param_name))
        elif isinstance(param_range, list):
            dimensions.append(Categorical(param_range, name=param_name))
        else:
            raise ValueError(f"Unsupported parameter range format for {param_name}: {param_range}")
    
    # Define objective function
    @use_named_args(dimensions)
    def objective(**params):
        model_clone = clone(model)
        model_clone.set_params(**params)
        
        try:
            scores = cross_val_score(model_clone, X_train, y_train, cv=cv, scoring=scoring)
            # Return negative score for minimization
            return -np.mean(scores)
        except:
            return 0  # Return neutral score if evaluation fails
    
    if verbose:
        print("🔬 Starting Bayesian optimization...")
    
    start_time = time.time()
    
    # Perform Bayesian optimization
    result = gp_minimize(
        func=objective,
        dimensions=dimensions,
        n_calls=n_calls,
        random_state=random_state,
        verbose=verbose
    )
    
    end_time = time.time()
    optimization_time = end_time - start_time
    
    # Extract best parameters
    best_params = dict(zip(param_names, result.x))
    best_score = -result.fun  # Convert back to positive score
    
    # Fit best model
    best_model = clone(model)
    best_model.set_params(**best_params)
    best_model.fit(X_train, y_train)
    
    if verbose:
        print(f"✅ Bayesian optimization completed in {optimization_time:.2f} seconds")
        print(f"🏆 Best score: {best_score:.4f}")
        print(f"🎯 Best parameters:")
        for param, value in best_params.items():
            print(f"   {param}: {value}")
    
    return {
        'best_model': best_model,
        'best_params': best_params,
        'best_score': best_score,
        'optimization_result': result,
        'optimization_time': optimization_time,
        'method': 'bayesian',
        'scoring': scoring,
        'n_folds': cv,
        'model_name': type(model).__name__
    }


def _detect_scoring_metric(y: pd.Series) -> str:
    """Detect appropriate scoring metric based on target variable."""
    
    # Check if classification
    if y.dtype == 'object' or pd.api.types.is_categorical_dtype(y):
        return 'accuracy' if len(y.unique()) > 2 else 'roc_auc'
    
    if y.dtype in ['int64', 'int32']:
        unique_ratio = len(y.unique()) / len(y)
        if unique_ratio < 0.05 or len(y.unique()) <= 20:
            return 'accuracy' if len(y.unique()) > 2 else 'roc_auc'
    
    # Default to regression
    return 'neg_mean_squared_error'

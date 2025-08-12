"""
edaflow.ml.config - Configuration and setup utilities for ML experiments

This module provides utilities for setting up machine learning experiments,
configuring model pipelines, and validating data for ML workflows.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import warnings


def setup_ml_experiment(
    data: pd.DataFrame,
    target_column: str,
    test_size: float = 0.2,
    validation_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = True,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Set up a complete ML experiment with train/validation/test splits.
    
    Parameters:
    -----------
    data : pd.DataFrame
        The dataset to prepare for ML
    target_column : str
        Name of the target variable column
    test_size : float, default=0.2
        Proportion of data to use for testing
    validation_size : float, default=0.2
        Proportion of training data to use for validation
    random_state : int, default=42
        Random seed for reproducibility
    stratify : bool, default=True
        Whether to stratify the splits (for classification)
    verbose : bool, default=True
        Whether to print experiment setup details
        
    Returns:
    --------
    Dict[str, Any]
        Dictionary containing X_train, X_val, X_test, y_train, y_val, y_test,
        feature_names, target_name, and experiment_config
    """
    
    if verbose:
        print("🧪 Setting up ML Experiment...")
        print(f"📊 Dataset shape: {data.shape}")
        print(f"🎯 Target column: {target_column}")
    
    # Validate target column exists
    if target_column not in data.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset")
    
    # Separate features and target
    X = data.drop(columns=[target_column])
    y = data[target_column]
    
    # Determine problem type
    is_classification = _is_classification_problem(y)
    problem_type = "classification" if is_classification else "regression"
    
    if verbose:
        print(f"📈 Problem type: {problem_type}")
        print(f"📋 Features: {len(X.columns)}")
        if is_classification:
            print(f"🏷️  Classes: {len(y.unique())} unique values")
        else:
            print(f"📊 Target range: [{y.min():.3f}, {y.max():.3f}]")
    
    # Configure stratification
    stratify_param = y if (stratify and is_classification) else None
    
    # First split: separate test set
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_param
    )
    
    # Second split: training and validation from remaining data
    val_size_adjusted = validation_size / (1 - test_size)
    stratify_temp = y_temp if (stratify and is_classification) else None
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        test_size=val_size_adjusted,
        random_state=random_state,
        stratify=stratify_temp
    )
    
    if verbose:
        print(f"✅ Train set: {X_train.shape[0]} samples")
        print(f"✅ Validation set: {X_val.shape[0]} samples") 
        print(f"✅ Test set: {X_test.shape[0]} samples")
    
    # Create experiment configuration
    experiment_config = {
        'problem_type': problem_type,
        'target_column': target_column,
        'feature_names': list(X.columns),
        'n_classes': len(y.unique()) if is_classification else None,
        'test_size': test_size,
        'validation_size': validation_size,
        'random_state': random_state,
        'stratified': stratify and is_classification,
        'total_samples': len(data),
        'train_samples': len(X_train),
        'val_samples': len(X_val),
        'test_samples': len(X_test)
    }
    
    return {
        'X_train': X_train,
        'X_val': X_val,
        'X_test': X_test,
        'y_train': y_train,
        'y_val': y_val,
        'y_test': y_test,
        'feature_names': list(X.columns),
        'target_name': target_column,
        'experiment_config': experiment_config
    }


def configure_model_pipeline(
    data_config: Dict[str, Any],
    numerical_strategy: str = 'standard',
    categorical_strategy: str = 'onehot',
    handle_missing: str = 'drop',
    verbose: bool = True
) -> Pipeline:
    """
    Configure a preprocessing pipeline for the ML experiment.
    
    Parameters:
    -----------
    data_config : Dict[str, Any]
        Configuration dictionary from setup_ml_experiment
    numerical_strategy : str, default='standard'
        Scaling strategy for numerical features ('standard', 'minmax', 'robust', 'none')
    categorical_strategy : str, default='onehot'
        Encoding strategy for categorical features ('onehot', 'target', 'none')
    handle_missing : str, default='drop'
        Missing value strategy ('drop', 'impute', 'flag')
    verbose : bool, default=True
        Whether to print pipeline configuration details
        
    Returns:
    --------
    Pipeline
        Configured sklearn Pipeline for preprocessing
    """
    
    if verbose:
        print("🔧 Configuring Model Pipeline...")
        print(f"📊 Numerical strategy: {numerical_strategy}")
        print(f"🏷️  Categorical strategy: {categorical_strategy}")
        print(f"❓ Missing values: {handle_missing}")
    
    # Get sample data to analyze column types
    X_sample = data_config['X_train']
    
    # Identify numerical and categorical columns
    numerical_columns = X_sample.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = X_sample.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if verbose:
        print(f"📈 Numerical columns: {len(numerical_columns)}")
        print(f"📋 Categorical columns: {len(categorical_columns)}")
    
    # Configure transformers
    transformers = []
    
    # Numerical preprocessing
    if numerical_columns and numerical_strategy != 'none':
        if numerical_strategy == 'standard':
            num_transformer = StandardScaler()
        elif numerical_strategy == 'minmax':
            num_transformer = MinMaxScaler()
        elif numerical_strategy == 'robust':
            num_transformer = RobustScaler()
        else:
            raise ValueError(f"Unknown numerical strategy: {numerical_strategy}")
        
        transformers.append(('num', num_transformer, numerical_columns))
    
    # Categorical preprocessing
    if categorical_columns and categorical_strategy != 'none':
        if categorical_strategy == 'onehot':
            from sklearn.preprocessing import OneHotEncoder
            cat_transformer = OneHotEncoder(drop='first', sparse_output=False)
            transformers.append(('cat', cat_transformer, categorical_columns))
        elif categorical_strategy == 'target':
            warnings.warn("Target encoding not implemented yet. Using OneHot encoding.")
            from sklearn.preprocessing import OneHotEncoder
            cat_transformer = OneHotEncoder(drop='first', sparse_output=False)
            transformers.append(('cat', cat_transformer, categorical_columns))
    
    # Create column transformer
    if transformers:
        preprocessor = ColumnTransformer(
            transformers=transformers,
            remainder='passthrough'  # Keep other columns as-is
        )
    else:
        # No transformation needed
        from sklearn.preprocessing import FunctionTransformer
        preprocessor = FunctionTransformer(validate=False)
    
    # Create pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor)
    ])
    
    if verbose:
        print("✅ Pipeline configured successfully!")
    
    return pipeline


def validate_ml_data(
    experiment_data: Dict[str, Any],
    check_missing: bool = True,
    check_duplicates: bool = True,
    check_outliers: bool = True,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Validate data quality for ML experiments.
    
    Parameters:
    -----------
    experiment_data : Dict[str, Any]
        Dictionary from setup_ml_experiment containing splits
    check_missing : bool, default=True
        Whether to check for missing values
    check_duplicates : bool, default=True
        Whether to check for duplicate rows
    check_outliers : bool, default=True
        Whether to check for outliers
    verbose : bool, default=True
        Whether to print validation details
        
    Returns:
    --------
    Dict[str, Any]
        Dictionary containing validation results and recommendations
    """
    
    if verbose:
        print("🔍 Validating ML Data Quality...")
    
    validation_results = {}
    recommendations = []
    
    # Get data splits
    X_train = experiment_data['X_train']
    X_val = experiment_data['X_val'] 
    X_test = experiment_data['X_test']
    y_train = experiment_data['y_train']
    
    # Check missing values
    if check_missing:
        train_missing = X_train.isnull().sum()
        missing_cols = train_missing[train_missing > 0]
        
        validation_results['missing_values'] = {
            'total_missing': train_missing.sum(),
            'columns_with_missing': len(missing_cols),
            'missing_percentages': (missing_cols / len(X_train) * 100).to_dict()
        }
        
        if len(missing_cols) > 0:
            recommendations.append(f"⚠️ {len(missing_cols)} columns have missing values")
            if verbose:
                print(f"❓ Missing values found in {len(missing_cols)} columns")
    
    # Check duplicates
    if check_duplicates:
        train_duplicates = X_train.duplicated().sum()
        validation_results['duplicates'] = {
            'duplicate_rows': train_duplicates,
            'duplicate_percentage': (train_duplicates / len(X_train) * 100)
        }
        
        if train_duplicates > 0:
            recommendations.append(f"⚠️ {train_duplicates} duplicate rows found")
            if verbose:
                print(f"🔄 {train_duplicates} duplicate rows detected")
    
    # Check for class imbalance (classification only)
    if experiment_data['experiment_config']['problem_type'] == 'classification':
        class_counts = y_train.value_counts()
        class_ratios = class_counts / len(y_train)
        min_class_ratio = class_ratios.min()
        
        validation_results['class_balance'] = {
            'class_counts': class_counts.to_dict(),
            'class_ratios': class_ratios.to_dict(),
            'min_class_ratio': min_class_ratio,
            'is_imbalanced': min_class_ratio < 0.1
        }
        
        if min_class_ratio < 0.1:
            recommendations.append(f"⚠️ Class imbalance detected (min class: {min_class_ratio:.1%})")
            if verbose:
                print(f"⚖️ Class imbalance: smallest class is {min_class_ratio:.1%}")
    
    # Data quality score
    quality_score = 100.0
    if validation_results.get('missing_values', {}).get('total_missing', 0) > 0:
        quality_score -= 20
    if validation_results.get('duplicates', {}).get('duplicate_rows', 0) > 0:
        quality_score -= 10
    if validation_results.get('class_balance', {}).get('is_imbalanced', False):
        quality_score -= 15
    
    validation_results['quality_score'] = quality_score
    validation_results['recommendations'] = recommendations
    
    if verbose:
        print(f"📊 Data Quality Score: {quality_score:.1f}/100")
        if recommendations:
            print("📋 Recommendations:")
            for rec in recommendations:
                print(f"   {rec}")
        else:
            print("✅ No major data quality issues detected!")
    
    return validation_results


def _is_classification_problem(y: pd.Series) -> bool:
    """
    Determine if the target variable represents a classification problem.
    
    Parameters:
    -----------
    y : pd.Series
        Target variable
        
    Returns:
    --------
    bool
        True if classification, False if regression
    """
    
    # Check data type
    if y.dtype == 'object' or pd.api.types.is_categorical_dtype(y):
        return True
    
    # Check if all values are integers and relatively few unique values
    if y.dtype in ['int64', 'int32']:
        unique_ratio = len(y.unique()) / len(y)
        if unique_ratio < 0.05 or len(y.unique()) <= 20:
            return True
    
    # Check for boolean values
    if y.dtype == 'bool':
        return True
    
    # Default to regression for continuous values
    return False

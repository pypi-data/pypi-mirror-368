"""
edaflow.ml.artifacts - Model persistence and experiment tracking

This module provides utilities for saving and loading model artifacts,
tracking experiments, and generating comprehensive model reports.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
import pickle
import joblib
import json
import os
from datetime import datetime
from pathlib import Path
import warnings


def save_model_artifacts(
    model: Any,
    model_name: str,
    experiment_config: Dict[str, Any],
    performance_metrics: Dict[str, float],
    save_dir: str = "model_artifacts",
    include_data_sample: bool = True,
    X_sample: Optional[pd.DataFrame] = None,
    format: str = 'joblib'
) -> Dict[str, str]:
    """
    Save complete model artifacts including model, config, and metadata.
    
    Parameters:
    -----------
    model : Any
        The trained model to save
    model_name : str
        Name of the model for file naming
    experiment_config : Dict[str, Any]
        Configuration dictionary from setup_ml_experiment
    performance_metrics : Dict[str, float]
        Dictionary of performance metrics
    save_dir : str, default="model_artifacts"
        Directory to save artifacts
    include_data_sample : bool, default=True
        Whether to save a sample of training data
    X_sample : pd.DataFrame, optional
        Sample data to save (if not provided, uses first 100 rows)
    format : str, default='joblib'
        Format to save model ('joblib' or 'pickle')
        
    Returns:
    --------
    Dict[str, str]
        Dictionary with paths to saved artifacts
    """
    
    print(f"💾 Saving model artifacts for '{model_name}'...")
    
    # Create save directory
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for unique naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{model_name}_{timestamp}"
    
    saved_files = {}
    
    # Save the model
    if format.lower() == 'joblib':
        model_file = save_path / f"{base_filename}_model.joblib"
        joblib.dump(model, model_file)
    elif format.lower() == 'pickle':
        model_file = save_path / f"{base_filename}_model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    saved_files['model'] = str(model_file)
    print(f"✅ Model saved: {model_file}")
    
    # Save experiment configuration
    config_file = save_path / f"{base_filename}_config.json"
    with open(config_file, 'w') as f:
        # Convert any non-serializable objects to strings
        serializable_config = _make_json_serializable(experiment_config)
        json.dump(serializable_config, f, indent=2)
    
    saved_files['config'] = str(config_file)
    print(f"✅ Config saved: {config_file}")
    
    # Save performance metrics
    metrics_file = save_path / f"{base_filename}_metrics.json"
    with open(metrics_file, 'w') as f:
        serializable_metrics = _make_json_serializable(performance_metrics)
        json.dump(serializable_metrics, f, indent=2)
    
    saved_files['metrics'] = str(metrics_file)
    print(f"✅ Metrics saved: {metrics_file}")
    
    # Save model metadata
    metadata = {
        'model_name': model_name,
        'model_type': type(model).__name__,
        'saved_at': datetime.now().isoformat(),
        'saved_format': format,
        'feature_count': experiment_config.get('feature_count', 'unknown'),
        'problem_type': experiment_config.get('problem_type', 'unknown'),
        'training_samples': experiment_config.get('train_samples', 'unknown')
    }
    
    metadata_file = save_path / f"{base_filename}_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    saved_files['metadata'] = str(metadata_file)
    print(f"✅ Metadata saved: {metadata_file}")
    
    # Save data sample if requested
    if include_data_sample and X_sample is not None:
        sample_file = save_path / f"{base_filename}_data_sample.csv"
        sample_data = X_sample.head(100) if len(X_sample) > 100 else X_sample
        sample_data.to_csv(sample_file, index=False)
        saved_files['data_sample'] = str(sample_file)
        print(f"✅ Data sample saved: {sample_file}")
    
    print(f"🎉 All artifacts saved to: {save_path}")
    return saved_files


def load_model_artifacts(
    artifact_path: str,
    load_model: bool = True,
    load_config: bool = True,
    load_metrics: bool = True
) -> Dict[str, Any]:
    """
    Load model artifacts from saved files.
    
    Parameters:
    -----------
    artifact_path : str
        Path to the model file or directory containing artifacts
    load_model : bool, default=True
        Whether to load the model
    load_config : bool, default=True
        Whether to load the configuration
    load_metrics : bool, default=True
        Whether to load the metrics
        
    Returns:
    --------
    Dict[str, Any]
        Dictionary containing loaded artifacts
    """
    
    print(f"📂 Loading model artifacts from: {artifact_path}")
    
    artifact_path = Path(artifact_path)
    loaded_artifacts = {}
    
    # If path is a directory, find model files
    if artifact_path.is_dir():
        model_files = list(artifact_path.glob("*_model.joblib")) + list(artifact_path.glob("*_model.pkl"))
        if not model_files:
            raise FileNotFoundError(f"No model files found in {artifact_path}")
        
        # Use the most recent model file
        model_file = max(model_files, key=os.path.getctime)
        base_name = model_file.stem.replace("_model", "")
        
    else:
        # Path is a specific model file
        model_file = artifact_path
        base_name = model_file.stem.replace("_model", "")
        artifact_path = model_file.parent
    
    # Load model
    if load_model:
        try:
            if model_file.suffix == '.joblib':
                model = joblib.load(model_file)
            elif model_file.suffix == '.pkl':
                with open(model_file, 'rb') as f:
                    model = pickle.load(f)
            else:
                raise ValueError(f"Unsupported model file format: {model_file.suffix}")
            
            loaded_artifacts['model'] = model
            print(f"✅ Model loaded: {model_file}")
            
        except Exception as e:
            print(f"❌ Failed to load model: {str(e)}")
    
    # Load configuration
    if load_config:
        config_file = artifact_path / f"{base_name}_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                loaded_artifacts['config'] = config
                print(f"✅ Config loaded: {config_file}")
            except Exception as e:
                print(f"❌ Failed to load config: {str(e)}")
        else:
            print(f"⚠️ Config file not found: {config_file}")
    
    # Load metrics
    if load_metrics:
        metrics_file = artifact_path / f"{base_name}_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                loaded_artifacts['metrics'] = metrics
                print(f"✅ Metrics loaded: {metrics_file}")
            except Exception as e:
                print(f"❌ Failed to load metrics: {str(e)}")
        else:
            print(f"⚠️ Metrics file not found: {metrics_file}")
    
    # Load metadata if available
    metadata_file = artifact_path / f"{base_name}_metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            loaded_artifacts['metadata'] = metadata
            print(f"✅ Metadata loaded: {metadata_file}")
        except Exception as e:
            print(f"❌ Failed to load metadata: {str(e)}")
    
    print(f"🎉 Loaded {len(loaded_artifacts)} artifact types")
    return loaded_artifacts


def track_experiment(
    experiment_name: str,
    model_results: Dict[str, Any],
    experiment_config: Dict[str, Any],
    notes: Optional[str] = None,
    log_file: str = "experiment_log.csv"
) -> None:
    """
    Track experiment results in a CSV log file.
    
    Parameters:
    -----------
    experiment_name : str
        Name of the experiment
    model_results : Dict[str, Any]
        Results dictionary from model comparison
    experiment_config : Dict[str, Any]
        Configuration dictionary from setup_ml_experiment
    notes : str, optional
        Additional notes about the experiment
    log_file : str, default="experiment_log.csv"
        Path to the log file
    """
    
    print(f"📊 Tracking experiment: {experiment_name}")
    
    # Prepare experiment record
    record = {
        'timestamp': datetime.now().isoformat(),
        'experiment_name': experiment_name,
        'model_type': model_results.get('model_name', 'unknown'),
        'problem_type': experiment_config.get('problem_type', 'unknown'),
        'dataset_size': experiment_config.get('total_samples', 'unknown'),
        'feature_count': len(experiment_config.get('feature_names', [])),
        'best_score': model_results.get('best_score', 'unknown'),
        'optimization_time': model_results.get('optimization_time', 'unknown'),
        'notes': notes or ''
    }
    
    # Add specific metrics if available
    if 'cv_results' in model_results and isinstance(model_results['cv_results'], pd.DataFrame):
        cv_results = model_results['cv_results']
        if not cv_results.empty:
            record.update({
                'mean_test_score': cv_results['mean_test_score'].iloc[0] if 'mean_test_score' in cv_results else 'unknown',
                'std_test_score': cv_results['std_test_score'].iloc[0] if 'std_test_score' in cv_results else 'unknown'
            })
    
    # Convert record to DataFrame
    record_df = pd.DataFrame([record])
    
    # Append to log file
    log_path = Path(log_file)
    if log_path.exists():
        # Append to existing log
        existing_log = pd.read_csv(log_file)
        updated_log = pd.concat([existing_log, record_df], ignore_index=True)
    else:
        # Create new log
        updated_log = record_df
    
    # Save updated log
    updated_log.to_csv(log_file, index=False)
    print(f"✅ Experiment logged to: {log_file}")


def create_model_report(
    model: Any,
    model_name: str,
    experiment_config: Dict[str, Any],
    performance_metrics: Dict[str, float],
    feature_importance: Optional[pd.DataFrame] = None,
    validation_results: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None
) -> str:
    """
    Generate a comprehensive model report.
    
    Parameters:
    -----------
    model : Any
        The trained model
    model_name : str
        Name of the model
    experiment_config : Dict[str, Any]
        Configuration dictionary
    performance_metrics : Dict[str, float]
        Performance metrics dictionary
    feature_importance : pd.DataFrame, optional
        Feature importance data
    validation_results : Dict[str, Any], optional
        Validation results from validate_ml_data
    save_path : str, optional
        Path to save the report
        
    Returns:
    --------
    str
        The generated report as a string
    """
    
    print(f"📄 Generating model report for '{model_name}'...")
    
    # Generate report content
    report_lines = [
        "="*80,
        f"MODEL PERFORMANCE REPORT",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "="*80,
        "",
        f"📊 MODEL INFORMATION",
        f"Model Name: {model_name}",
        f"Model Type: {type(model).__name__}",
        f"Problem Type: {experiment_config.get('problem_type', 'unknown')}",
        "",
        f"📈 DATASET INFORMATION",
        f"Total Samples: {experiment_config.get('total_samples', 'unknown')}",
        f"Training Samples: {experiment_config.get('train_samples', 'unknown')}",
        f"Validation Samples: {experiment_config.get('val_samples', 'unknown')}",
        f"Test Samples: {experiment_config.get('test_samples', 'unknown')}",
        f"Number of Features: {len(experiment_config.get('feature_names', []))}",
        "",
        f"🎯 PERFORMANCE METRICS",
    ]
    
    # Add performance metrics
    for metric_name, metric_value in performance_metrics.items():
        if isinstance(metric_value, (int, float)):
            report_lines.append(f"{metric_name.upper()}: {metric_value:.4f}")
        else:
            report_lines.append(f"{metric_name.upper()}: {metric_value}")
    
    report_lines.append("")
    
    # Add data quality information if available
    if validation_results:
        report_lines.extend([
            f"📊 DATA QUALITY ASSESSMENT",
            f"Quality Score: {validation_results.get('quality_score', 'unknown'):.1f}/100"
        ])
        
        if validation_results.get('recommendations'):
            report_lines.append("Recommendations:")
            for rec in validation_results['recommendations']:
                report_lines.append(f"  - {rec}")
        
        report_lines.append("")
    
    # Add feature importance if available
    if feature_importance is not None and not feature_importance.empty:
        report_lines.extend([
            f"🔍 TOP 10 MOST IMPORTANT FEATURES",
        ])
        
        top_features = feature_importance.head(10)
        for _, row in top_features.iterrows():
            report_lines.append(f"{row['feature']}: {row['importance']:.4f}")
        
        report_lines.append("")
    
    # Add model parameters if available
    if hasattr(model, 'get_params'):
        params = model.get_params()
        if params:
            report_lines.extend([
                f"⚙️  MODEL PARAMETERS",
            ])
            for param_name, param_value in params.items():
                report_lines.append(f"{param_name}: {param_value}")
            
            report_lines.append("")
    
    # Add experiment configuration
    report_lines.extend([
        f"🧪 EXPERIMENT CONFIGURATION",
        f"Random State: {experiment_config.get('random_state', 'unknown')}",
        f"Test Size: {experiment_config.get('test_size', 'unknown')}",
        f"Validation Size: {experiment_config.get('validation_size', 'unknown')}",
        f"Stratified Split: {experiment_config.get('stratified', 'unknown')}",
    ])
    
    report_lines.extend([
        "",
        "="*80,
        "Report generated by edaflow.ml",
        "="*80
    ])
    
    # Combine into single report string
    report_content = "\n".join(report_lines)
    
    # Save report if path provided
    if save_path:
        report_path = Path(save_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        print(f"✅ Report saved to: {report_path}")
    
    return report_content


def _make_json_serializable(obj: Any) -> Any:
    """Convert non-JSON-serializable objects to serializable format."""
    
    if isinstance(obj, dict):
        return {key: _make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_make_json_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        try:
            # Test if object is JSON serializable
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            # Convert to string if not serializable
            return str(obj)

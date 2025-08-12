"""
edaflow.ml - Machine Learning workflows and model evaluation tools

A comprehensive subpackage for automated machine learning workflows, model comparison,
hyperparameter tuning, and performance visualization.

Modules:
--------
- config: Configuration and setup utilities for ML experiments
- leaderboard: Model comparison and ranking functionality  
- tuning: Automated hyperparameter optimization
- curves: Learning curves and performance visualization
- artifacts: Model persistence and experiment tracking
"""

from .config import (
    setup_ml_experiment,
    configure_model_pipeline,
    validate_ml_data
)

from .leaderboard import (
    compare_models,
    rank_models,
    display_leaderboard,
    export_model_comparison
)

from .tuning import (
    optimize_hyperparameters,
    grid_search_models,
    bayesian_optimization,
    random_search_models
)

from .curves import (
    plot_learning_curves,
    plot_validation_curves,
    plot_roc_curves,
    plot_precision_recall_curves,
    plot_confusion_matrix,
    plot_feature_importance
)

from .artifacts import (
    save_model_artifacts,
    load_model_artifacts,
    track_experiment,
    create_model_report
)

__version__ = "0.12.33"
__author__ = "Evan Low"

# Expose main functions at subpackage level
__all__ = [
    # Config functions
    'setup_ml_experiment',
    'configure_model_pipeline', 
    'validate_ml_data',
    
    # Leaderboard functions
    'compare_models',
    'rank_models',
    'display_leaderboard',
    'export_model_comparison',
    
    # Tuning functions
    'optimize_hyperparameters',
    'grid_search_models',
    'bayesian_optimization',
    'random_search_models',
    
    # Curves functions
    'plot_learning_curves',
    'plot_validation_curves',
    'plot_roc_curves',
    'plot_precision_recall_curves',
    'plot_confusion_matrix',
    'plot_feature_importance',
    
    # Artifacts functions
    'save_model_artifacts',
    'load_model_artifacts',
    'track_experiment',
    'create_model_report'
]

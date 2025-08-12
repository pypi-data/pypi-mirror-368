API Reference
=============

This section contains the complete API documentation for all edaflow functions.

.. toctree::
   :maxdepth: 2

   core_functions
   visualization_functions
   ml_functions

Complete Function Index
-----------------------

Exploratory Data Analysis (EDA) Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: edaflow

**Data Quality & Analysis**

.. autosummary::
   :toctree: generated/

   check_null_columns
   analyze_categorical_columns
   convert_to_numeric
   display_column_types
   summarize_eda_insights

**Data Cleaning & Preprocessing**

.. autosummary::
   :toctree: generated/

   impute_numerical_median
   impute_categorical_mode
   handle_outliers_median

**Visualization & Analysis**

.. autosummary::
   :toctree: generated/

   visualize_categorical_values
   visualize_numerical_boxplots
   visualize_interactive_boxplots
   visualize_heatmap
   visualize_histograms
   visualize_scatter_matrix

Machine Learning (ML) Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: edaflow.ml

**ML Configuration & Setup**

.. autosummary::
   :toctree: generated/

   setup_ml_experiment
   configure_model_pipeline
   validate_ml_data

**Model Comparison & Ranking**

.. autosummary::
   :toctree: generated/

   compare_models
   rank_models
   display_leaderboard
   export_model_comparison

**Hyperparameter Optimization**

.. autosummary::
   :toctree: generated/

   optimize_hyperparameters
   grid_search_models
   bayesian_optimization
   random_search_models

**Performance Visualization**

.. autosummary::
   :toctree: generated/

   plot_learning_curves
   plot_validation_curves
   plot_roc_curves
   plot_precision_recall_curves
   plot_confusion_matrix
   plot_feature_importance

**Model Artifacts & Tracking**

.. autosummary::
   :toctree: generated/

   save_model_artifacts
   load_model_artifacts
   track_experiment
   create_model_report

**Helper Functions**

.. autosummary::
   :toctree: generated/

   hello
   summarize_eda_insights

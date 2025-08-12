Machine Learning Functions
==========================

This section documents the complete ML workflow functions introduced in edaflow v0.13.0.

.. currentmodule:: edaflow.ml

ML Configuration & Setup
-------------------------

.. autosummary::
   :toctree: generated/

   setup_ml_experiment
   configure_model_pipeline
   validate_ml_data

Model Comparison & Ranking
---------------------------

.. autosummary::
   :toctree: generated/

   compare_models
   rank_models
   display_leaderboard
   export_model_comparison

Hyperparameter Optimization
----------------------------

.. autosummary::
   :toctree: generated/

   optimize_hyperparameters
   grid_search_models
   bayesian_optimization
   random_search_models

Performance Visualization
--------------------------

.. autosummary::
   :toctree: generated/

   plot_learning_curves
   plot_validation_curves
   plot_roc_curves
   plot_precision_recall_curves
   plot_confusion_matrix
   plot_feature_importance

Model Artifacts & Tracking
---------------------------

.. autosummary::
   :toctree: generated/

   save_model_artifacts
   load_model_artifacts
   track_experiment
   create_model_report

Function Details
----------------

Configuration Functions
~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: setup_ml_experiment
.. autofunction:: configure_model_pipeline
.. autofunction:: validate_ml_data

Model Comparison Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: compare_models
.. autofunction:: rank_models
.. autofunction:: display_leaderboard
.. autofunction:: export_model_comparison

Hyperparameter Tuning Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: optimize_hyperparameters
.. autofunction:: grid_search_models
.. autofunction:: bayesian_optimization
.. autofunction:: random_search_models

Performance Visualization Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: plot_learning_curves
.. autofunction:: plot_validation_curves
.. autofunction:: plot_roc_curves
.. autofunction:: plot_precision_recall_curves
.. autofunction:: plot_confusion_matrix
.. autofunction:: plot_feature_importance

Model Artifacts Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: save_model_artifacts
.. autofunction:: load_model_artifacts
.. autofunction:: track_experiment
.. autofunction:: create_model_report

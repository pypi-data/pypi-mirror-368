edaflow Documentation
=====================

.. image:: https://img.shields.io/pypi/v/edaflow.svg
   :target: https://pypi.org/project/edaflow/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/edaflow.svg
   :target: https://pypi.org/project/edaflow/
   :alt: Python versions

.. image:: https://img.shields.io/github/license/evanlow/edaflow.svg
   :target: https://github.com/evanlow/edaflow/blob/main/LICENSE
   :alt: License

edaflow is a Python package designed to streamline both exploratory data analysis (EDA) and machine learning (ML) workflows. It provides 18+ comprehensive EDA functions and 26 powerful ML functions that cover the essential steps from data exploration to model deployment.

**edaflow** simplifies and accelerates data science workflows by providing a collection of powerful functions for data scientists and analysts. The package integrates popular data science libraries to create a cohesive workflow for data exploration, visualization, preprocessing, machine learning model development, and intelligent categorical encoding - now including computer vision datasets and quality assessment.

🎯 **Key Features**
-------------------

**Exploratory Data Analysis (EDA)**

* **Missing Data Analysis**: Color-coded analysis of null values with customizable thresholds
* **Categorical Data Insights**: Identify object columns that might be numeric, detect data type issues
* **Automatic Data Type Conversion**: Smart conversion of object columns to numeric when appropriate
* **Data Imputation**: Smart missing value imputation using median for numerical and mode for categorical columns
* **Advanced Visualizations**: Interactive boxplots, comprehensive heatmaps, statistical histograms
* **Scatter Matrix Analysis**: Advanced pairwise relationship visualization with regression lines
* **Computer Vision EDA**: Class-wise image sample visualization for image classification datasets
* **Image Quality Assessment**: Automated detection of corrupted, blurry, or low-quality images
* **Smart Categorical Encoding**: Intelligent analysis and automated application of optimal encoding strategies
* **Outlier Handling**: Automated outlier detection and replacement using multiple statistical methods

**Machine Learning (ML) Workflow**

* **ML Experiment Setup**: Automated train/validation/test splits and configuration management
* **Model Comparison**: Multi-model evaluation with comprehensive performance leaderboards
* **Hyperparameter Optimization**: Grid search, random search, and Bayesian optimization
* **Performance Visualization**: Learning curves, ROC curves, confusion matrices, and feature importance
* **Model Persistence**: Complete model artifacts saving with metadata and experiment tracking
* **Pipeline Configuration**: Automated preprocessing pipeline setup for ML workflows

**Professional Output**: Beautiful, color-coded results optimized for Jupyter notebooks

📦 **Quick Installation**
-------------------------

.. code-block:: bash

   pip install edaflow

🚀 **Quick Start Example**
--------------------------

**EDA Workflow:**

.. code-block:: python

   import edaflow
   import pandas as pd

   # Load your data
   df = pd.read_csv('your_data.csv')

   # Complete EDA workflow
   edaflow.check_null_columns(df)
   edaflow.analyze_categorical_columns(df)
   edaflow.visualize_heatmap(df)
   edaflow.visualize_scatter_matrix(df)

**ML Workflow:**

.. code-block:: python

   import edaflow.ml as ml
   from sklearn.ensemble import RandomForestClassifier
   from sklearn.linear_model import LogisticRegression

   # Setup ML experiment
   config = ml.setup_ml_experiment(
       X=X, y=y, 
       test_size=0.2,
       experiment_name="model_comparison"
   )

   # Compare multiple models
   models = {
       'rf': RandomForestClassifier(),
       'lr': LogisticRegression()
   }
   
   results = ml.compare_models(
       models=models,
       X_train=config['X_train'],
       y_train=config['y_train'],
       X_test=config['X_test'],
       y_test=config['y_test']
   )
   df = pd.read_csv('your_data.csv')

   # Complete EDA workflow with 18 functions
   edaflow.check_null_columns(df)                    # 1. Missing data analysis
   edaflow.analyze_categorical_columns(df)           # 2. Categorical insights
   df_clean = edaflow.convert_to_numeric(df)         # 3. Smart type conversion
   edaflow.visualize_categorical_values(df_clean)    # 4. Category exploration
   edaflow.visualize_scatter_matrix(df_clean)        # 5. Relationship analysis
   edaflow.visualize_heatmap(df_clean)              # 6. Correlation heatmaps
   edaflow.visualize_histograms(df_clean)           # 7. Distribution analysis
   # ... and 11 more powerful functions!
   
   # NEW: Computer Vision EDA & Quality Assessment
   edaflow.visualize_image_classes(
       data_source='dataset/images/',  # Simple directory path
       samples_per_class=4,
       max_classes_display=8
   )
   edaflow.assess_image_quality(
       image_paths=image_list,         # List of image paths
       check_corruption=True,
       analyze_color=True,
       detect_blur=True,
       sample_size=200
   )

📚 **Documentation Contents**
-----------------------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   user_guide/index
   api_reference/index
   examples/index
   changelog
   contributing

🔗 **Useful Links**
-------------------

* **GitHub Repository**: https://github.com/evanlow/edaflow
* **PyPI Package**: https://pypi.org/project/edaflow/
* **Issue Tracker**: https://github.com/evanlow/edaflow/issues
* **Changelog**: :doc:`changelog`

📊 **Function Overview**
------------------------

edaflow provides 18 comprehensive EDA functions organized into logical categories:

**Data Quality & Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.check_null_columns` - Missing data analysis with color coding
* :func:`~edaflow.analyze_categorical_columns` - Categorical data insights
* :func:`~edaflow.convert_to_numeric` - Smart data type conversion
* :func:`~edaflow.display_column_types` - Column type classification

**Data Cleaning & Preprocessing**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.impute_numerical_median` - Numerical missing value imputation
* :func:`~edaflow.impute_categorical_mode` - Categorical missing value imputation
* :func:`~edaflow.handle_outliers_median` - Outlier detection and handling

**Visualization & Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.visualize_categorical_values` - Categorical value exploration
* :func:`~edaflow.visualize_numerical_boxplots` - Distribution and outlier analysis
* :func:`~edaflow.visualize_interactive_boxplots` - Interactive Plotly visualizations
* :func:`~edaflow.visualize_heatmap` - Comprehensive heatmap analysis
* :func:`~edaflow.visualize_histograms` - Statistical distribution analysis
* :func:`~edaflow.visualize_scatter_matrix` - Advanced pairwise relationship analysis

**Computer Vision EDA** 🖼️ **NEW in v0.9.0-v0.12.3!**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.visualize_image_classes` - Class-wise image sample visualization for image classification datasets

**Image Quality Assessment** 🔍 **NEW in v0.10.0-v0.12.3!**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.assess_image_quality` - Comprehensive automated quality assessment and corruption detection for image datasets

**Smart Encoding** 🧠 **NEW in v0.12.4-v0.12.7!**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.analyze_encoding_needs` - Intelligent categorical encoding analysis and recommendations
* :func:`~edaflow.apply_smart_encoding` - Automated encoding application with optimal strategy selection

**Helper Functions**
~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.hello` - Package verification function

🎓 **Background**
-----------------------------

edaflow was developed in part of a Capstone project during an AI/ML course conducted by NTUC LearningHub (Cohort 15). 
Special thanks to our instructor, Ms. Isha Sehgal, who inspired the project works which led to the development of this comprehensive EDA toolkit.

📄 **License**
--------------

This project is licensed under the MIT License - see the `LICENSE <https://github.com/evanlow/edaflow/blob/main/LICENSE>`_ file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

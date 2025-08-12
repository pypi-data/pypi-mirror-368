Quick Start Guide
=================

This guide will get you up and running with edaflow for both EDA and ML workflows in just a few minutes!

🚀 **Installation & Basic Setup**
----------------------------------

First, install and import edaflow:

.. code-block:: bash

   pip install edaflow

.. code-block:: python

   import edaflow
   import edaflow.ml as ml  # For ML workflows
   import pandas as pd
   
   # ⭐ For perfect visibility in any notebook environment:
   edaflow.optimize_display()  # Universal dark mode support!
   
   # Verify installation
   print(edaflow.hello())

📊 **EDA Workflow Quick Start**
-------------------------------

.. code-block:: python
   
   # Load your data and start exploring
   df = pd.read_csv('your_data.csv')
   
   # Essential EDA functions
   edaflow.check_null_columns(df)  # Beautiful, visible output!
   edaflow.analyze_categorical_columns(df)
   
   # Smart conversion
   df_converted = edaflow.convert_to_numeric(df, threshold=35)
   print(df_converted.dtypes)  # 'price' now converted to float
   
   # Visualizations
   edaflow.visualize_heatmap(df_converted)
   edaflow.visualize_scatter_matrix(df_converted)

🤖 **ML Workflow Quick Start**
------------------------------

.. code-block:: python

   # Prepare your data
   X = df_converted.drop('target', axis=1)
   y = df_converted['target']
   
   # Step 1: Setup ML Experiment
   config = ml.setup_ml_experiment(
       X=X, y=y,
       test_size=0.2,
       experiment_name="quick_start_ml"
   )
   
   # Step 2: Compare Models
   from sklearn.ensemble import RandomForestClassifier
   from sklearn.linear_model import LogisticRegression
   
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
   
   # Step 3: Display Results
   ml.display_leaderboard(results)
   
   # Step 4: Optimize Best Model
   tuning_results = ml.optimize_hyperparameters(
       model=RandomForestClassifier(),
       X_train=config['X_train'],
       y_train=config['y_train'],
       param_distributions={
           'n_estimators': [100, 200],
           'max_depth': [5, 10, None]
       },
       method='grid_search'
   )

🖼️ **Computer Vision Quick Start**
-----------------------------------

.. code-block:: python

   # Computer Vision EDA - Explore image datasets
   
   # Method 1: Directory path (most common)
   edaflow.visualize_image_classes(
       data_source='ecommerce_images/', 
       samples_per_class=4,
       max_classes_display=8,
       figsize=(12, 8)
   )
   
   # Method 2: File list with glob
   import glob
   product_photos = glob.glob('ecommerce_images/*/*.jpg')
   edaflow.visualize_image_classes(
       data_source=product_photos, 
       samples_per_class=4,
       max_classes_display=8,
       figsize=(12, 8)
   )

🔍 **Function Categories**
--------------------------

🖼️ **Computer Vision EDA** ⭐ *New in v0.9.0-v0.12.3*
---------------------------------------------------------e-block:: python

   # Install (if not already done)
   # pip install edaflow
   
   import edaflow
   import pandas as pd
   
   # Verify installation
   print(edaflow.hello())

🎨 **Perfect Display Optimization** ⭐ *New in v0.12.30*
--------------------------------------------------------

edaflow is the **FIRST** EDA library with universal dark mode compatibility! Use ``optimize_display()`` for perfect visibility across all notebook platforms:

.. code-block:: python

   import edaflow
   
   # One line for perfect visibility everywhere!
   edaflow.optimize_display()
   
   # Now all edaflow functions display perfectly in:
   # ✅ Google Colab (light & dark modes)
   # ✅ JupyterLab (all themes)  
   # ✅ VS Code Notebooks (auto theme detection)
   # ✅ Classic Jupyter (all themes)
   # ✅ High contrast accessibility support

**Platform-Specific Benefits:**

* **Google Colab**: Automatic theme detection and optimization
* **JupyterLab**: Perfect dark mode compatibility with all themes
* **VS Code**: Native integration with VS Code theme system
* **Accessibility**: High contrast mode support for better visibility

.. tip::
   **Best Practice**: Always call ``edaflow.optimize_display()`` at the start of your notebook for the best experience!

📊 **Complete EDA Workflow**
----------------------------

Here's how to perform a complete exploratory data analysis with edaflow's 18 functions (15 for tabular data + 3 for computer vision):

.. code-block:: python

   import pandas as pd
   import edaflow
   
   # ⭐ NEW: Optimize display for perfect visibility (Jupyter, Colab, VS Code)
   edaflow.optimize_display()  # Universal dark mode compatibility!
   
   # Load your dataset
   df = pd.read_csv('your_data.csv')
   print(f"Dataset shape: {df.shape}")
   
   # Step 1: Missing Data Analysis
   null_analysis = edaflow.check_null_columns(df, threshold=10)
   null_analysis  # Beautiful color-coded output in Jupyter
   
   # Step 2: Categorical Data Insights
   edaflow.analyze_categorical_columns(df, threshold=35)
   
   # Step 3: Smart Data Type Conversion
   df_cleaned = edaflow.convert_to_numeric(df, threshold=35)
   
   # Step 4: Explore Categorical Values
   edaflow.visualize_categorical_values(df_cleaned)
   
   # Step 5: Column Type Classification
   column_types = edaflow.display_column_types(df_cleaned)
   
   # Step 6: Data Imputation
   df_numeric_imputed = edaflow.impute_numerical_median(df_cleaned)
   df_fully_imputed = edaflow.impute_categorical_mode(df_numeric_imputed)
   
   # Step 7: Statistical Distribution Analysis
   edaflow.visualize_histograms(df_fully_imputed, kde=True, show_normal_curve=True)
   
   # Step 8: Comprehensive Relationship Analysis
   edaflow.visualize_heatmap(df_fully_imputed, heatmap_type='correlation')
   edaflow.visualize_scatter_matrix(df_fully_imputed, regression_type='linear')
   
   # Step 9: Generate Comprehensive EDA Insights (NEW in v0.12.27!)
   insights = edaflow.summarize_eda_insights(
       df_fully_imputed, 
       target_column='your_target_column',
       eda_functions_used=['check_null_columns', 'analyze_categorical_columns', 
                          'convert_to_numeric', 'visualize_histograms'],
       class_threshold=0.1
   )
   
   # View structured insights
   print("Dataset Overview:", insights['dataset_overview'])
   print("Data Quality Assessment:", insights['data_quality']) 
   print("Recommendations:", insights['recommendations'])
   
   # Step 10: Outlier Detection and Visualization
   edaflow.visualize_numerical_boxplots(df_fully_imputed, show_skewness=True)
   edaflow.visualize_interactive_boxplots(df_fully_imputed)
   
   # Step 11: Advanced Heatmap Analysis
   edaflow.visualize_heatmap(df_fully_imputed, heatmap_type='missing')
   edaflow.visualize_heatmap(df_fully_imputed, heatmap_type='values')
   
   # Step 12: Outlier Handling
   df_final = edaflow.handle_outliers_median(df_fully_imputed, method='iqr', verbose=True)
   
   # Step 13: Smart Encoding for ML (⭐ New Clean APIs in v0.12.33)
   # Analyze optimal encoding strategies
   encoding_analysis = edaflow.analyze_encoding_needs(
       df_final,
       target_column=None,               # Optional: specify target if available
       max_cardinality_onehot=15,        # Max categories for one-hot encoding  
       ordinal_columns=None              # Optional: specify ordinal columns if known
   )
   
   # ✅ RECOMMENDED: Apply encoding with clean, consistent API
   df_encoded = edaflow.apply_encoding(
       df_final,                         # Use the full dataset
       encoding_analysis=encoding_analysis
   )
   
   # Alternative: If you need access to encoders for test data
   # df_encoded, encoders = edaflow.apply_encoding_with_encoders(
   #     df_final,
   #     encoding_analysis=encoding_analysis
   # )
   
   # Step 14: Results Verification
   edaflow.visualize_scatter_matrix(df_encoded, title="ML-Ready Encoded Data")
   edaflow.visualize_numerical_boxplots(df_encoded, title="Final Encoded Distribution")

🎯 **Key Function Examples**
----------------------------

**Universal Display Optimization** ⭐ *New in v0.12.30*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import edaflow
   
   # One line for perfect visibility across ALL platforms
   config = edaflow.optimize_display(
       high_contrast=False,    # Set to True for accessibility
       verbose=True           # Show optimization details
   )
   
   # Platform auto-detection results:
   print(f"Platform detected: {config['platform']}")
   print(f"Theme: {config['theme']}")
   print(f"Optimizations applied: {config['optimizations']}")
   
   # Now ALL edaflow functions display perfectly:
   # ✅ Google Colab - Auto-detects light/dark mode
   # ✅ JupyterLab - Works with ANY theme
   # ✅ VS Code - Native theme integration  
   # ✅ Classic Jupyter - Full compatibility

.. note::
   **Why optimize_display()?** Different notebook platforms handle CSS and styling differently. This function automatically detects your environment and applies the perfect styling for maximum visibility and readability.

**Missing Data Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   import edaflow
   
   # Essential: Optimize display first!
   edaflow.optimize_display()
   
   # Sample data with missing values
   df = pd.DataFrame({
       'name': ['Alice', 'Bob', None, 'Diana'],
       'age': [25, None, 35, None],
       'salary': [50000, 60000, None, 70000]
   })
   
   # Color-coded missing data analysis
   result = edaflow.check_null_columns(df, threshold=20)
   result  # Display in Jupyter for beautiful formatting

**Scatter Matrix Analysis** ⭐ *New in v0.8.4*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Advanced pairwise relationship visualization
   edaflow.visualize_scatter_matrix(
       df,
       columns=['feature1', 'feature2', 'feature3'],
       color_by='category',         # Color by category
       diagonal='kde',              # KDE plots on diagonal
       upper='corr',                # Correlations in upper triangle
       lower='scatter',             # Scatter plots in lower triangle
       regression_type='linear',    # Add regression lines
       figsize=(12, 12)
   )

**Interactive Visualizations**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import edaflow
   
   # Ensure perfect visibility for interactive plots
   edaflow.optimize_display()
   
   # Interactive Plotly boxplots with zoom and hover
   edaflow.visualize_interactive_boxplots(
       df,
       title="Interactive Data Exploration",
       height=600,
       show_points='outliers'  # Show outlier points
   )

**Comprehensive Heatmaps**
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import edaflow
   
   # Perfect visibility for all heatmap types
   edaflow.optimize_display()
   
   # Multiple heatmap types for different insights
   
   # 1. Correlation analysis
   edaflow.visualize_heatmap(df, heatmap_type='correlation', method='pearson')
   
   # 2. Missing data patterns
   edaflow.visualize_heatmap(df, heatmap_type='missing')
   
   # 3. Cross-tabulation analysis
   edaflow.visualize_heatmap(df, heatmap_type='crosstab')
   
   # 4. Data values visualization
   edaflow.visualize_heatmap(df.head(20), heatmap_type='values')

**Statistical Distribution Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Advanced histogram analysis with statistical testing
   edaflow.visualize_histograms(
       df,
       kde=True,                    # Add KDE curves
       show_normal_curve=True,      # Compare to normal distribution
       show_stats=True,             # Statistical summary boxes
       bins=30                      # Custom bin count
   )

**Smart Data Type Conversion**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Automatically detect and convert numeric columns stored as text
   df_original = pd.DataFrame({
       'product': ['Laptop', 'Mouse', 'Keyboard'],
       'price_text': ['999', '25', '75'],        # Should be numeric
       'category': ['Electronics', 'Accessories', 'Accessories']
   })
   
   # Smart conversion
   df_converted = edaflow.convert_to_numeric(df_original, threshold=35)
   print(df_converted.dtypes)  # 'price_text' now converted to float

🖼️ **Computer Vision EDA** ⭐ *New in v0.9.0-v0.12.3*
---------------------------------------------------------

Explore image datasets with the same systematic approach as tabular data! edaflow's Computer Vision EDA provides a complete pipeline for understanding image collections.

**Complete CV EDA Workflow**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import edaflow
   import glob
   
   # Ensure perfect image visualization across all platforms
   edaflow.optimize_display()
   
   # Load image dataset
   # Method 1: Simple directory path (recommended for organized datasets)
   edaflow.visualize_image_classes(
       data_source='path/to/dataset/',  # Directory with class subfolders
       samples_per_class=4,
       max_classes_display=8,           # Limit displayed classes
       figsize=(12, 8),
       title="Training Set Overview"
   )
   
   # Method 2: File list approach (for custom filtering)
   image_paths = glob.glob('dataset/train/*/*.jpg')  # Collect specific files
   edaflow.visualize_image_classes(
       data_source=image_paths,         # List of image paths
       samples_per_class=4,
       max_classes_display=8,
       figsize=(12, 8),
       title="Training Set Overview"
   )
   
   # Step 2: Image Quality Assessment
   print("\\n🔍 STEP 2: QUALITY ASSESSMENT")
   print("-" * 50)
   quality_report = edaflow.assess_image_quality(
       data_source='ecommerce_images/',  # Consistent with visualize_image_classes
       check_corruption=True,      # Corruption detection
       analyze_color=True,         # Color property analysis
       detect_blur=True,           # Blur detection
       check_artifacts=True,       # Artifact detection
       sample_size=200,            # Balance speed vs completeness
       verbose=True               # Detailed progress reporting
   )
   
   # Step 3: Advanced Feature Analysis
   print("\\n📊 STEP 3: FEATURE ANALYSIS")  
   print("-" * 50)
   feature_analysis = edaflow.analyze_image_features(
       image_paths,
       analyze_color=True,         # RGB histogram analysis
       analyze_edges=True,         # Edge density patterns
       analyze_texture=True,       # Texture complexity metrics
       analyze_gradients=True,     # Gradient magnitude analysis
       sample_size=100,            # Computational efficiency
       bins_per_channel=50        # Histogram granularity
   )

**Individual Function Examples**

**1. Dataset Visualization**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Understand your image dataset at a glance
   
   # Method 1: Directory path (simplest approach)
   edaflow.visualize_image_classes(
       data_source='path/to/dataset/',  # Directory with class subfolders
       samples_per_class=4,
       max_classes_display=8,           # Limit displayed classes
       figsize=(12, 8),
       title="Training Set Overview"
   )
   
   # Method 2: Specific file patterns (for custom control)  
   edaflow.visualize_image_classes(
       data_source=['path/to/class1/*.jpg', 'path/to/class2/*.jpg'],
       samples_per_class=4,
       max_classes_display=8,
       figsize=(12, 8),
       title="Training Set Overview"
   )
   
   # Output: Beautiful grid showing class distribution and sample images

**2. Quality Assessment** ⭐ *New in v0.10.0*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Comprehensive image quality analysis
   quality_metrics = edaflow.assess_image_quality(
       data_source='ecommerce_images/',  # Consistent parameter naming
       check_corruption=True,      # Detect corrupted files
       analyze_color=True,         # Color property analysis
       detect_blur=True,           # Blur detection  
       check_artifacts=True,       # Compression artifacts
       sample_size=200,            # Balance speed vs completeness
       verbose=True               # Detailed progress reporting
   )
   
   # Returns detailed report with:
   # - Corruption detection results
   # - Color distribution analysis (grayscale vs color)
   # - Blur detection using Laplacian variance
   # - Artifact and quality issue identification
   # - Statistical summaries and recommendations

**3. Advanced Feature Analysis** ⭐ *New in v0.11.0*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Deep feature analysis for dataset understanding
   features = edaflow.analyze_image_features(
       image_paths,
       analyze_color=True,         # RGB histogram analysis
       analyze_edges=True,         # Edge density patterns
       analyze_texture=True,       # Texture complexity metrics
       analyze_gradients=True,     # Gradient magnitude analysis
       sample_size=100,            # Computational efficiency
       bins_per_channel=50        # Histogram granularity
   )
   
   # Comprehensive visualizations:
   # - Color distribution heatmaps across dataset
   # - Edge density patterns by class
   # - Texture complexity analysis
   # - Gradient magnitude distributions
   # - Statistical summaries with actionable insights

**Computer Vision Use Cases**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Medical Imaging Dataset
   medical_scans = glob.glob('medical_data/*/*.dcm')
   edaflow.assess_image_quality(
       data_source=medical_scans,  # Consistent parameter naming
       check_corruption=True,
       analyze_color=True,
       detect_blur=True
   )
   
   # Satellite Imagery Analysis  
   satellite_images = glob.glob('satellite_data/**/*.tif', recursive=True)
   edaflow.analyze_image_features(
       satellite_images, 
       analyze_color=True,
       analyze_texture=True,
       sample_size=100
   )
   
   # Product Photography Quality Control
   edaflow.visualize_image_classes(
       data_source='ecommerce_images/', 
       samples_per_class=4,
       max_classes_display=8,
       figsize=(12, 8),
       title="Product Catalog Overview"
   )

�🔍 **Function Categories**
--------------------------

**Data Quality & Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``check_null_columns()`` - Missing data analysis
* ``analyze_categorical_columns()`` - Categorical insights  
* ``convert_to_numeric()`` - Smart type conversion
* ``display_column_types()`` - Column classification

**Data Cleaning & Preprocessing**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``impute_numerical_median()`` - Numerical imputation
* ``impute_categorical_mode()`` - Categorical imputation
* ``handle_outliers_median()`` - Outlier handling

**Visualization & Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``visualize_categorical_values()`` - Category exploration
* ``visualize_numerical_boxplots()`` - Distribution analysis
* ``visualize_interactive_boxplots()`` - Interactive plots
* ``visualize_heatmap()`` - Comprehensive heatmaps
* ``visualize_histograms()`` - Statistical distributions
* ``visualize_scatter_matrix()`` - Pairwise relationships

**Computer Vision EDA** ⭐ *New*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``visualize_image_classes()`` - Dataset visualization & class distribution
* ``assess_image_quality()`` - Quality analysis & corruption detection  
* ``analyze_image_features()`` - Advanced feature analysis (colors, edges, texture)

**Smart Encoding for ML** ⭐ *New Clean APIs in v0.12.33*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``analyze_encoding_needs()`` - Intelligent analysis of optimal encoding strategies
* ``apply_encoding()`` - Clean, consistent DataFrame return (recommended)
* ``apply_encoding_with_encoders()`` - Explicit tuple return when encoders needed
* ``apply_smart_encoding()`` - Legacy function (still works, shows deprecation warning)

.. code-block:: python

   # Comprehensive encoding analysis and application
   
   # Step 1: Analyze optimal encoding strategies
   encoding_analysis = edaflow.analyze_encoding_needs(
       df,
       target_column=None,               # Optional: specify if you have a target
       max_cardinality_onehot=15,        # Threshold for one-hot encoding
       max_cardinality_target=50,        # Threshold for target encoding
       ordinal_columns=None              # Specify ordinal relationships if known
   )
   
   # Step 2A: ✅ RECOMMENDED - Always returns DataFrame
   df_encoded = edaflow.apply_encoding(
       df,                               # Use your full dataset
       encoding_analysis=encoding_analysis
   )
   
   # Step 2B: Alternative - When you need encoders for test data  
   df_encoded, encoders = edaflow.apply_encoding_with_encoders(
       df,                               # Use your full dataset
       encoding_analysis=encoding_analysis
   )
   
   # The pipeline automatically selects:
   # • One-hot encoding for low cardinality
   # • Target encoding for high cardinality (supervised)
   # • Ordinal encoding for ordered categories
   # • Binary encoding for medium cardinality
   # • Frequency encoding as fallback

💡 **Pro Tips**
---------------

**For Tabular Data:**
1. **Jupyter Notebooks**: Use edaflow in Jupyter for the best visual experience with color-coded outputs
2. **Large Datasets**: For datasets with >10,000 rows, consider sampling for visualization functions
3. **Memory Management**: Process data in chunks for very large datasets
4. **Custom Thresholds**: Adjust threshold parameters based on your data quality tolerance
5. **Interactive Mode**: Use ``visualize_interactive_boxplots()`` for presentations and exploratory analysis

**For Computer Vision:**
6. **Start Small**: Use ``sample_size`` parameters to test workflows on subsets before full analysis
7. **Quality First**: Always run ``assess_image_quality()`` before feature analysis to identify issues
8. **Organized Data**: Structure images in class folders for automatic class detection
9. **Memory Efficiency**: CV functions are optimized for memory usage but consider batch processing for huge datasets
10. **Dependencies**: Install OpenCV (``pip install opencv-python``) for enhanced edge detection and texture analysis

🚀 **Next Steps**
-----------------

* Explore the :doc:`user_guide/index` for detailed function documentation
* Check out :doc:`examples/index` for real-world use cases
* Review the :doc:`api_reference/index` for complete function parameters
* See :doc:`changelog` for the latest features and improvements

**Ready to dive deeper?** The User Guide contains comprehensive examples and advanced usage patterns!

# edaflow

[![Documentation Status](https://readthedocs.org/projects/edaflow/badge/?version=latest)](https://edaflow.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/edaflow.svg)](https://badge.fury.io/py/edaflow)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/edaflow)](https://pepy.tech/project/edaflow)

**Quick Navigation**: 
📚 [Documentation](https://edaflow.readthedocs.io) | 
📦 [PyPI Package](https://pypi.org/project/edaflow/) | 
🚀 [Quick Start](https://edaflow.readthedocs.io/en/latest/quickstart.html) | 
📋 [Changelog](#-changelog) | 
🐛 [Issues](https://github.com/evanlow/edaflow/issues)

A Python package for streamlined exploratory data analysis workflows.

> **📦 Current Version: v0.13.2** - [Latest Release](https://pypi.org/project/edaflow/0.13.2/) includes enhanced display optimization and visual improvements for better data analysis presentation across all environments. *Updated: August 12, 2025*

## 📖 Table of Contents

- [Description](#description)
- [✨ What's New](#-whats-new-in-v01221)
- [Features](#features)
- [🆕 Recent Updates](#-recent-updates)
- [📚 Documentation](#-documentation)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [📋 Changelog](#-changelog)
- [Support](#support)
- [Roadmap](#roadmap)

## Description

`edaflow` is designed to simplify and accelerate the exploratory data analysis (EDA) process by providing a collection of tools and utilities for data scientists and analysts. The package integrates popular data science libraries to create a cohesive workflow for data exploration, visualization, and preprocessing.

## ✨ What's New in v0.13.2

### Display Enhancement (v0.13.2)
**ENHANCED VISUAL EXPERIENCE**: Improved Rich console styling across all EDA functions for consistent, professional data analysis presentation. Enhanced Google Colab compatibility with optimized display formatting.

### ML Expansion (v0.13.0)
**NEW MACHINE LEARNING SUBPACKAGE**: Introduced comprehensive `edaflow.ml` subpackage with complete ML workflow capabilities.

**Root Enhancement**: Extended edaflow beyond EDA into full machine learning workflows, providing end-to-end data science capabilities from exploration to model deployment.

**New ML Modules Added**:
- **`ml.config`**: ML experiment setup and data validation
- **`ml.leaderboard`**: Multi-model comparison and ranking
- **`ml.tuning`**: Advanced hyperparameter optimization
- **`ml.curves`**: Learning curves and performance visualization
- **`ml.artifacts`**: Model persistence and experiment tracking

**Key ML Features**:
```python
# Complete ML workflow in one package
import edaflow.ml as ml

# Setup experiment with automatic data splitting
experiment = ml.setup_ml_experiment(df, 'target')

# Compare multiple models
results = ml.compare_models(models, **experiment)

# Optimize hyperparameters with multiple strategies
best_model = ml.optimize_hyperparameters(model, params, **experiment)

# Generate comprehensive visualizations
ml.plot_learning_curves(model, **experiment)
```

### Previous: API Improvement (v0.12.33)
**NEW CLEAN APIs**: Introduced consistent, user-friendly encoding functions that eliminate confusion and crashes.

**Root Cause Solved**: The inconsistent return type of `apply_smart_encoding()` (sometimes DataFrame, sometimes tuple) was causing AttributeError crashes and user confusion.

**New Functions Added**:
```python
# ✅ NEW: Clean, consistent DataFrame return (RECOMMENDED)
df_encoded = edaflow.apply_encoding(df)  # Always returns DataFrame

# ✅ NEW: Explicit tuple return when encoders needed
df_encoded, encoders = edaflow.apply_encoding_with_encoders(df)  # Always returns tuple

# ⚠️ DEPRECATED: Inconsistent behavior (still works with warnings)
df_encoded = edaflow.apply_smart_encoding(df, return_encoders=True)  # Sometimes tuple!
```

**Benefits**:
- 🎯 **Zero Breaking Changes**: All existing workflows continue working exactly the same
- 🛡️ **Better Error Messages**: Helpful guidance when mistakes are made  
- 🔄 **Migration Path**: Multiple options for users who want cleaner APIs
- 📚 **Clear Documentation**: Explicit examples showing best practices

### 🐛 Critical Input Validation Fix (v0.12.32)
**RESOLVED**: Fixed AttributeError: 'tuple' object has no attribute 'empty' in visualization functions when `apply_smart_encoding(..., return_encoders=True)` result is used incorrectly.

**Problem Solved**: Users who passed the tuple result from `apply_smart_encoding` directly to visualization functions without unpacking were experiencing crashes in step 14 of EDA workflows.

**Enhanced Error Messages**: Added intelligent input validation with helpful error messages guiding users to the correct usage pattern:
```python
# ❌ WRONG - This causes the AttributeError:
df_encoded = edaflow.apply_smart_encoding(df, return_encoders=True)  # Returns (df, encoders) tuple!
edaflow.visualize_scatter_matrix(df_encoded)  # Crashes with AttributeError

# ✅ CORRECT - Unpack the tuple:  
df_encoded, encoders = edaflow.apply_smart_encoding(df, return_encoders=True)
edaflow.visualize_scatter_matrix(df_encoded)  # Should work well!
```

### 🎨 BREAKTHROUGH: Universal Dark Mode Compatibility (v0.12.30)
- **NEW FUNCTION**: `optimize_display()` - The **FIRST** EDA library with universal notebook compatibility!
- **Universal Platform Support**: Improved visibility across Google Colab, JupyterLab, VS Code, and Classic Jupyter
- **Automatic Detection**: Zero configuration needed - automatically detects your environment
- **Accessibility Support**: Built-in high contrast mode for improved accessibility
- **One-Line Solution**: `edaflow.optimize_display()` fixes all visibility issues instantly

### 🐛 Critical KeyError Hotfix (v0.12.31)
- **Fixed KeyError**: Resolved "KeyError: 'type'" in `summarize_eda_insights()` function
- **Enhanced Error Handling**: Added robust exception handling for target analysis edge cases
- **Improved Stability**: Function now handles missing or invalid target columns gracefully

### 🌟 Platform Benefits:
- ✅ **Google Colab**: Auto light/dark mode detection with improved text visibility
- ✅ **JupyterLab**: Dark theme compatibility with custom theme support
- ✅ **VS Code**: Native theme integration with seamless notebook experience  
- ✅ **Classic Jupyter**: Full compatibility with enhanced readability options

```python
import edaflow
# ⭐ NEW: Improved visibility everywhere!
edaflow.optimize_display()  # Universal dark mode fix!

# All functions now display beautifully
edaflow.check_null_columns(df)
edaflow.visualize_histograms(df)
```

### ✨ NEW FUNCTION: `summarize_eda_insights()` (Added in v0.12.28)
- **Comprehensive Analysis**: Generate complete EDA insights and actionable recommendations after completing your analysis workflow
- **Smart Recommendations**: Provides intelligent next steps for modeling, preprocessing, and data quality improvements
- **Target-Aware Analysis**: Supports both classification and regression scenarios with specific insights
- **Function Tracking**: Knows which edaflow functions you've already used in your workflow
- **Structured Output**: Returns organized dictionary with dataset overview, data quality assessment, and recommendations

### 🎨 Display Formatting Excellence
- **Enhanced Visual Experience**: Refined Rich console styling with optimized panel borders and alignment
- **Google Colab Optimized**: Improved display formatting specifically tailored for notebook environments
- **Consistent Design**: Professional rounded borders, proper width constraints, and refined color schemes
- **Universal Compatibility**: Beautiful output rendering across all major Python environments and notebooks

### � Recent Fixes (v0.12.24-0.12.26)
- **LBP Warning Resolution**: Fixed scikit-image UserWarning in texture analysis functions
- **Parameter Documentation**: Corrected `analyze_image_features` documentation mismatches
- **RTD Synchronization**: Updated Read the Docs changelog with all recent improvements

### 🌈 Rich Styling (v0.12.20-0.12.21)
- **Vibrant Output**: ALL major EDA functions now feature professional, color-coded styling
- **Smart Indicators**: Color-coded severity levels (✅ CLEAN, ⚠️ WARNING, 🚨 CRITICAL)
- **Professional Tables**: Beautiful formatted output with rich library integration
- **Actionable Insights**: Context-aware recommendations and visual status indicators

## Features

### 🔍 **Exploratory Data Analysis**
- **Missing Data Analysis**: Color-coded analysis of null values with customizable thresholds
- **Categorical Data Insights**: 🐛 *FIXED in v0.12.29* Identify object columns that might be numeric, detect data type issues (now handles unhashable types)
- **Automatic Data Type Conversion**: Smart conversion of object columns to numeric when appropriate
- **Categorical Values Visualization**: Detailed exploration of categorical column values with insights
- **Column Type Classification**: Simple categorization of DataFrame columns into categorical and numerical types
- **Data Type Detection**: Smart analysis to flag potential data conversion needs
- **EDA Insights Summary**: ⭐ *NEW in v0.12.28* Comprehensive EDA insights and actionable recommendations after completing analysis workflow

### 📊 **Advanced Visualizations**
- **Numerical Distribution Visualization**: Advanced boxplot analysis with outlier detection and statistical summaries
- **Interactive Boxplot Visualization**: Interactive Plotly Express boxplots with zoom, hover, and statistical tooltips
- **Comprehensive Heatmap Visualizations**: Correlation matrices, missing data patterns, values heatmaps, and cross-tabulations
- **Statistical Histogram Analysis**: Advanced histogram visualization with skewness detection, normality testing, and distribution analysis
- **Scatter Matrix Analysis**: Advanced pairwise relationship visualization with customizable matrix layouts, regression lines, and statistical insights

### 🤖 **Machine Learning Preprocessing** ⭐ *Introduced in v0.12.0*
- **Intelligent Encoding Analysis**: Automatic detection of optimal encoding strategies for categorical variables
- **Smart Encoding Application**: Automated categorical encoding with support for:
  - One-Hot Encoding for low cardinality categories
  - Target Encoding for high cardinality with target correlation
  - Ordinal Encoding for ordinal relationships
  - Binary Encoding for medium cardinality
  - Text Vectorization (TF-IDF) for text features
  - Leave Unchanged for numeric columns
- **Memory-Efficient Processing**: Intelligent handling of high-cardinality features to prevent memory issues
- **Comprehensive Encoding Pipeline**: End-to-end preprocessing solution for ML model preparation

### 🤖 **Machine Learning Workflows** ⭐ *NEW in v0.13.0*
The powerful `edaflow.ml` subpackage provides comprehensive machine learning workflow capabilities:

#### **ML Experiment Setup (`ml.config`)**
- **Smart Data Validation**: Automatic data quality assessment and problem type detection
- **Intelligent Data Splitting**: Train/validation/test splits with stratification support
- **ML Pipeline Configuration**: Automated preprocessing pipeline setup for ML workflows

#### **Model Comparison & Ranking (`ml.leaderboard`)**
- **Multi-Model Evaluation**: Compare multiple models with comprehensive metrics
- **Smart Leaderboards**: Automatically rank models by performance with visual displays
- **Export Capabilities**: Save comparison results for reporting and analysis

#### **Hyperparameter Optimization (`ml.tuning`)**
- **Multiple Search Strategies**: Grid search, random search, and Bayesian optimization
- **Cross-Validation Integration**: Built-in CV with customizable scoring metrics
- **Parallel Processing**: Multi-core hyperparameter optimization for faster results

#### **Learning & Performance Curves (`ml.curves`)**
- **Learning Curves**: Visualize model performance vs training size
- **Validation Curves**: Analyze hyperparameter impact on model performance
- **ROC & Precision-Recall Curves**: Comprehensive classification performance analysis
- **Feature Importance**: Visual analysis of model feature contributions

#### **Model Persistence & Tracking (`ml.artifacts`)**
- **Complete Model Artifacts**: Save models, configs, and metadata
- **Experiment Tracking**: Track multiple experiments with organized storage
- **Model Reports**: Generate comprehensive model performance reports
- **Version Management**: Organized model versioning and retrieval

**Quick ML Example:**
```python
import edaflow.ml as ml
from sklearn.ensemble import RandomForestClassifier

# Setup ML experiment
experiment = ml.setup_ml_experiment(df, target_column='target')

# Compare multiple models
models = {
    'RandomForest': RandomForestClassifier(),
    'LogisticRegression': LogisticRegression()
}
comparison = ml.compare_models(models, **experiment)

# Optimize hyperparameters
results = ml.optimize_hyperparameters(
    RandomForestClassifier(),
    param_distributions={'n_estimators': [50, 100, 200]},
    **experiment
)

# Generate learning curves
ml.plot_learning_curves(results['best_model'], **experiment)

# Save complete artifacts
ml.save_model_artifacts(
    model=results['best_model'],
    model_name='optimized_rf',
    experiment_config=experiment,
    performance_metrics=results['cv_results']
)
```

### 🖼️ **Computer Vision Support**
- **Computer Vision EDA**: Class-wise image sample visualization and comprehensive quality assessment for image classification datasets
- **Image Quality Assessment**: Automated detection of corrupted images, quality issues, blur, artifacts, and dataset health metrics

### 🛠️ **Data Preprocessing**
- **Data Imputation**: Smart missing value imputation using median for numerical and mode for categorical columns
- **Outlier Handling**: Automated outlier detection and replacement using IQR, Z-score, and Modified Z-score methods
- **Styled Output**: Beautiful, color-coded results for Jupyter notebooks and terminals
- **Easy Integration**: Works easily with pandas, numpy, scikit-learn, and other popular libraries

## 🆕 Recent Updates

### v0.13.2 (Latest) - Enhanced Display Experience
- **ENHANCED**: Improved Rich console styling across all major EDA functions for professional data presentation
- **VISUAL CONSISTENCY**: Applied consistent rounded borders, optimal alignment, and refined color schemes
- **GOOGLE COLAB**: Enhanced compatibility with optimized display formatting for better notebook rendering
- **USER EXPERIENCE**: Improved readability and visual hierarchy in all data analysis outputs

### v0.13.0 - Machine Learning Expansion
- **FEATURE**: Complete `edaflow.ml` subpackage with comprehensive ML workflow capabilities
- **NEW MODULES**: Added 5 core ML modules (config, leaderboard, tuning, curves, artifacts)
- **ML WORKFLOWS**: End-to-end machine learning from experiment setup to model deployment
- **HYPERPARAMETER OPTIMIZATION**: Grid search, random search, and Bayesian optimization
- **MODEL COMPARISON**: Multi-model evaluation with comprehensive metrics and leaderboards
- **PERFORMANCE VISUALIZATION**: Learning curves, ROC curves, validation curves, and feature importance
- **MODEL PERSISTENCE**: Complete artifact saving with experiment tracking and reporting

### v0.12.22 - Google Colab Compatibility  
- **🔧 CRITICAL FIX**: Resolved KeyError in `apply_smart_encoding` for Google Colab environments
- **FIXED**: Removed hardcoded 'target' column assumptions in documentation examples
- **ENHANCED**: Documentation examples now work universally across all Python environments
- **IMPROVED**: More robust ML encoding workflow that adapts to user datasets
- **MODERNIZED**: Clean workflow documentation without redundant print statements

### v0.12.21 - Documentation Parameter Fixes
- **🔧 CRITICAL FIXES**: Resolved parameter name mismatches in `visualize_scatter_matrix` documentation
- **FIXED**: `regression_line` → `regression_type` parameter name in all examples
- **FIXED**: `diagonal_type` → `diagonal` parameter name corrections
- **FIXED**: `upper_triangle`/`lower_triangle` → `upper`/`lower` parameter names
- **FIXED**: `color_column` → `color_by` parameter name corrections
- **RESOLVED**: TypeError when using sample code from official documentation

### v0.12.20 - Comprehensive Rich Styling
- **🌈 VIBRANT OUTPUT**: ALL major EDA functions now feature rich, professional styling
- **ENHANCED**: `check_null_columns` with color-coded severity levels (✅ CLEAN, ⚠️ MINOR, 🚨 WARNING, 💀 CRITICAL)
- **ENHANCED**: `display_column_types` with side-by-side rich tables and memory usage analysis
- **ENHANCED**: `impute_numerical_median` with professional imputation reporting and smart value formatting
- **COMPREHENSIVE**: Professional tables, color-coded indicators, and actionable insights across all functions
- **🎨 ROW OVERLAP FIX**: Eliminated overlapping rows in visualization layouts for cleaner displays
- **🔬 SCIENTIFIC NAME OPTIMIZATION**: Enhanced spacing specifically for long taxonomic/scientific class names
- **� PROFESSIONAL SPACING**: Improved hspace values and font sizing for publication-ready visualizations
- **✅ SCALABLE DESIGN**: Better layouts from small (5 classes) to large datasets (100+ classes)

### v0.12.15 - Transparency & Context
- **� CLASS LIMITING TRANSPARENCY**: Informative remarks when displaying subset of classes
- **🎯 SMART USER GUIDANCE**: Clear context about total dataset scope with actionable instructions
- **� ENHANCED UX**: Users always understand when seeing curated vs complete class sets

### v0.12.14 - Title Spacing Excellence  
- **🎨 TITLE SPACING IMPROVEMENTS**: Generous margins eliminate title overlap across all figure sizes
- **📐 PROFESSIONAL LAYOUTS**: Publication-ready spacing with height-based positioning
- **✨ VISUAL EXCELLENCE**: Dynamic title positioning for optimal appearance

## 📚 Documentation & Learning Resources

### 🎓 **Complete Learning Path**
- **[EDA Learning Guide](EDA_LEARNING_GUIDE.md)** - 🔍 Comprehensive guide combining EDA theory with hands-on edaflow practice
- **[ML Learning Guide](ML_LEARNING_GUIDE.md)** - 🤖 Complete machine learning concepts from theory to production with edaflow.ml
- **[Quick Start Guide](QUICKSTART.md)** - Fast-track tutorials for immediate productivity

### 📖 **Choose Your Learning Path**
- **New to EDA?** Start with [EDA Learning Guide](EDA_LEARNING_GUIDE.md) → [Quick Start](QUICKSTART.md) 
- **Ready for ML?** Complete [EDA Learning Guide](EDA_LEARNING_GUIDE.md) → [ML Learning Guide](ML_LEARNING_GUIDE.md)
- **Need Quick Reference?** Jump to [API Documentation](https://edaflow.readthedocs.io)

### 🔗 **Technical Documentation**
Complete documentation is available at **[edaflow.readthedocs.io](https://edaflow.readthedocs.io)**

- **[Installation Guide](https://edaflow.readthedocs.io/en/latest/installation.html)** - Setup instructions and troubleshooting
- **[Quick Start Tutorial](https://edaflow.readthedocs.io/en/latest/quickstart.html)** - Comprehensive guide with examples
- **[API Reference](https://edaflow.readthedocs.io/en/latest/api_reference/index.html)** - Complete function documentation
- **[User Guide](https://edaflow.readthedocs.io/en/latest/user_guide/index.html)** - Advanced usage patterns
- **[Examples](https://edaflow.readthedocs.io/en/latest/examples/index.html)** - Real-world applications

## Installation

### From PyPI
```bash
# Install latest version (recommended)
pip install edaflow

# Or install specific version  
pip install edaflow==0.13.0
```

### From Source
```bash
git clone https://github.com/evanlow/edaflow.git
cd edaflow
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/evanlow/edaflow.git
cd edaflow
pip install -e ".[dev]"
```

## Requirements

- Python 3.8+
- pandas >= 1.5.0
- numpy >= 1.21.0
- matplotlib >= 3.5.0
- seaborn >= 0.11.0
- scipy >= 1.9.0
- scikit-learn >= 1.0.0
- missingno >= 0.5.0
- plotly >= 5.0.0
- joblib >= 1.0.0

### Optional ML Dependencies
For advanced ML features:
- **scikit-optimize** >= 0.9.0 (for Bayesian optimization)

## Quick Start

### 🔍 **Complete EDA Workflow**
```python
import edaflow
import pandas as pd

# Test the installation
print(edaflow.hello())

# Load your data
df = pd.read_csv('your_data.csv')

# Complete EDA workflow with all core functions:
# 1. Analyze missing data with styled output
null_analysis = edaflow.check_null_columns(df, threshold=10)

# 2. Analyze categorical columns to identify data type issues
edaflow.analyze_categorical_columns(df, threshold=35)

# 3. Convert appropriate object columns to numeric automatically
df_cleaned = edaflow.convert_to_numeric(df, threshold=35)

# 4. Visualize categorical column values
edaflow.visualize_categorical_values(df_cleaned)

# 5. Display column type classification
edaflow.display_column_types(df_cleaned)

# 6. Impute missing values
df_numeric_imputed = edaflow.impute_numerical_median(df_cleaned)
df_fully_imputed = edaflow.impute_categorical_mode(df_numeric_imputed)

# 7. Statistical distribution analysis with advanced insights
edaflow.visualize_histograms(df_fully_imputed, kde=True, show_normal_curve=True)

# 8. Comprehensive relationship analysis
edaflow.visualize_heatmap(df_fully_imputed, heatmap_type='correlation')
edaflow.visualize_scatter_matrix(df_fully_imputed, show_regression=True)

# 9. Generate comprehensive EDA insights and recommendations
insights = edaflow.summarize_eda_insights(df_fully_imputed, target_column='your_target_col')
print(insights)  # View insights dictionary

# 10. Outlier detection and visualization
edaflow.visualize_numerical_boxplots(df_fully_imputed, show_skewness=True)
edaflow.visualize_interactive_boxplots(df_fully_imputed)

# 10. Advanced heatmap analysis
edaflow.visualize_heatmap(df_fully_imputed, heatmap_type='missing')
edaflow.visualize_heatmap(df_fully_imputed, heatmap_type='values')

# 11. Final data cleaning with outlier handling
df_final = edaflow.handle_outliers_median(df_fully_imputed, method='iqr', verbose=True)

# 12. Results verification
edaflow.visualize_scatter_matrix(df_final, title="Clean Data Relationships")
edaflow.visualize_numerical_boxplots(df_final, title="Final Clean Distribution")
```

### 🤖 **Complete ML Workflow** ⭐ *NEW in v0.13.0*
```python
import edaflow.ml as ml
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

# Continue from cleaned data above...
df_final['target'] = your_target_data  # Add your target column

# 1. Setup ML experiment with automatic data splitting
experiment = ml.setup_ml_experiment(df_final, target_column='target')

# 2. Compare multiple models
models = {
    'RandomForest': RandomForestClassifier(random_state=42),
    'GradientBoosting': GradientBoostingClassifier(random_state=42), 
    'LogisticRegression': LogisticRegression(random_state=42)
}

# Train and compare models
comparison = ml.compare_models(models, **experiment)
print(comparison)  # Professional styled output

# 3. Hyperparameter optimization for good model selection
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 7]
}

best_results = ml.optimize_hyperparameters(
    RandomForestClassifier(random_state=42),
    param_distributions=param_grid,
    **experiment,
    method='grid',
    cv=5
)

# 4. Generate performance visualizations
ml.plot_learning_curves(best_results['best_model'], **experiment)
ml.plot_roc_curves(best_results['best_model'], **experiment) 
ml.plot_feature_importance(best_results['best_model'], **experiment)

# 5. Save complete model artifacts
ml.save_model_artifacts(
    model=best_results['best_model'],
    model_name='final_optimized_model',
    experiment_config=experiment,
    performance_metrics=best_results['cv_results']
)
```

### 🤖 **ML Preprocessing with Smart Encoding** ⭐ *Introduced in v0.12.0*
```python
import edaflow
import pandas as pd

# Load your data
df = pd.read_csv('your_data.csv')

# Step 1: Analyze encoding needs (with or without target)
encoding_analysis = edaflow.analyze_encoding_needs(
    df, 
    target_column=None,            # Optional: specify target if you have one
    max_cardinality_onehot=15,     # Optional: max categories for one-hot encoding
    max_cardinality_target=50,     # Optional: max categories for target encoding
    ordinal_columns=None           # Optional: specify ordinal columns if known
)

# Step 2: Apply intelligent encoding transformations  
df_encoded = edaflow.apply_smart_encoding(
    df,                            # Use your full dataset (or df.drop('target_col', axis=1) if needed)
    encoding_analysis=encoding_analysis,  # Optional: use previous analysis
    handle_unknown='ignore'        # Optional: how to handle unknown categories
)

# The encoding pipeline automatically:
# ✅ One-hot encodes low cardinality categoricals
# ✅ Target encodes high cardinality with target correlation  
# ✅ Binary encodes medium cardinality features
# ✅ TF-IDF vectorizes text columns
# ✅ Preserves numeric columns unchanged
# ✅ Handles memory efficiently for large datasets

print(f"Shape transformation: {df.shape} → {df_encoded.shape}")
print(f"Encoding methods applied: {len(encoding_analysis['encoding_methods'])} different strategies")
```

## Usage Examples

### Basic Usage
```python
import edaflow

# Verify installation
message = edaflow.hello()
print(message)  # Output: "Hello from edaflow! Ready for exploratory data analysis."
```

### Missing Data Analysis with `check_null_columns`

The `check_null_columns` function provides a color-coded analysis of missing data in your DataFrame:

```python
import pandas as pd
import edaflow

# Create sample data with missing values
df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', None, 'Diana', 'Eve'],
    'age': [25, None, 35, None, 45],
    'email': [None, None, None, None, None],  # All missing
    'purchase_amount': [100.5, 250.0, 75.25, None, 320.0]
})

# Analyze missing data with default threshold (10%)
styled_result = edaflow.check_null_columns(df)
styled_result  # Display in Jupyter notebook for color-coded styling

# Use custom threshold (20%) to change color coding sensitivity
styled_result = edaflow.check_null_columns(df, threshold=20)
styled_result

# Access underlying data if needed
data = styled_result.data
print(data)
```

**Color Coding:**
- 🔴 **Red**: > 20% missing (high concern)
- 🟡 **Yellow**: 10-20% missing (medium concern)  
- 🟨 **Light Yellow**: 1-10% missing (low concern)
- ⬜ **Gray**: 0% missing (no issues)

### Categorical Data Analysis with `analyze_categorical_columns`

The `analyze_categorical_columns` function helps identify data type issues and provides insights into object-type columns:

```python
import pandas as pd
import edaflow

# Create sample data with mixed categorical types
df = pd.DataFrame({
    'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
    'price_str': ['999', '25', '75', '450'],  # Numbers stored as strings
    'category': ['Electronics', 'Accessories', 'Accessories', 'Electronics'],
    'rating': [4.5, 3.8, 4.2, 4.7],  # Already numeric
    'mixed_ids': ['001', '002', 'ABC', '004'],  # Mixed format
    'status': ['active', 'inactive', 'active', 'pending']
})

# Analyze categorical columns with default threshold (35%)
edaflow.analyze_categorical_columns(df)

# Use custom threshold (50%) to be more lenient about mixed data
edaflow.analyze_categorical_columns(df, threshold=50)
```

**Output Interpretation:**
- 🔴🔵 **Highlighted in Red/Blue**: Potentially numeric columns that might need conversion
- 🟡⚫ **Highlighted in Yellow/Black**: Shows unique values for potential numeric columns
- **Regular text**: Truly categorical columns with statistics
- **"not an object column"**: Already properly typed numeric columns

### Data Type Conversion with `convert_to_numeric`

After analyzing your categorical columns, you can automatically convert appropriate columns to numeric:

```python
import pandas as pd
import edaflow

# Create sample data with string numbers
df = pd.DataFrame({
    'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
    'price_str': ['999', '25', '75', '450'],      # Should convert
    'mixed_ids': ['001', '002', 'ABC', '004'],    # Mixed data
    'category': ['Electronics', 'Accessories', 'Electronics', 'Electronics']
})

# Convert appropriate columns to numeric (threshold=35% by default)
df_converted = edaflow.convert_to_numeric(df, threshold=35)

# Or modify the original DataFrame in place
edaflow.convert_to_numeric(df, threshold=35, inplace=True)

# Use a stricter threshold (only convert if <20% non-numeric values)
df_strict = edaflow.convert_to_numeric(df, threshold=20)
```

**Function Features:**
- ✅ **Smart Detection**: Only converts columns with few non-numeric values
- ✅ **Customizable Threshold**: Control conversion sensitivity 
- ✅ **Safe Conversion**: Non-numeric values become NaN (not errors)
- ✅ **Inplace Option**: Modify original DataFrame or create new one
- ✅ **Detailed Output**: Shows exactly what was converted and why

### Categorical Data Visualization with `visualize_categorical_values`

After cleaning your data, explore categorical columns in detail to understand value distributions:

```python
import pandas as pd
import edaflow

# Example DataFrame with categorical data
df = pd.DataFrame({
    'department': ['Sales', 'Marketing', 'Sales', 'HR', 'Marketing', 'Sales', 'IT'],
    'status': ['Active', 'Inactive', 'Active', 'Pending', 'Active', 'Active', 'Inactive'],
    'priority': ['High', 'Medium', 'High', 'Low', 'Medium', 'High', 'Low'],
    'employee_id': [1001, 1002, 1003, 1004, 1005, 1006, 1007],  # Numeric (ignored)
    'salary': [50000, 60000, 55000, 45000, 58000, 62000, 70000]  # Numeric (ignored)
})

# Visualize all categorical columns
edaflow.visualize_categorical_values(df)
```

**Advanced Usage Examples:**

```python
# Handle high-cardinality data (many unique values)
large_df = pd.DataFrame({
    'product_id': [f'PROD_{i:04d}' for i in range(100)],  # 100 unique values
    'category': ['Electronics'] * 40 + ['Clothing'] * 35 + ['Books'] * 25,
    'status': ['Available'] * 80 + ['Out of Stock'] * 15 + ['Discontinued'] * 5
})

# Limit display for high-cardinality columns
edaflow.visualize_categorical_values(large_df, max_unique_values=5)
```

```python
# DataFrame with missing values for comprehensive analysis
df_with_nulls = pd.DataFrame({
    'region': ['North', 'South', None, 'East', 'West', 'North', None],
    'customer_type': ['Premium', 'Standard', 'Premium', None, 'Standard', 'Premium', 'Standard'],
    'transaction_id': [f'TXN_{i}' for i in range(7)],  # Mostly unique (ID-like)
})

# Get detailed insights including missing value analysis
edaflow.visualize_categorical_values(df_with_nulls)
```

**Function Features:**
- 🎯 **Smart Column Detection**: Automatically finds categorical (object-type) columns
- 📊 **Value Distribution**: Shows counts and percentages for each unique value  
- 🔍 **Missing Value Analysis**: Tracks and reports NaN/missing values
- ⚡ **High-Cardinality Handling**: Truncates display for columns with many unique values
- 💡 **Actionable Insights**: Identifies ID-like columns and provides data quality recommendations
- 🎨 **Color-Coded Output**: Easy-to-read formatted results with highlighting

### Column Type Classification with `display_column_types`

The `display_column_types` function provides a simple way to categorize DataFrame columns into categorical and numerical types:

```python
import pandas as pd
import edaflow

# Create sample data with mixed types
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['NYC', 'LA', 'Chicago'],
    'salary': [50000, 60000, 70000],
    'is_active': [True, False, True]
}
df = pd.DataFrame(data)

# Display column type classification
result = edaflow.display_column_types(df)

# Access the categorized column lists
categorical_cols = result['categorical']  # ['name', 'city']
numerical_cols = result['numerical']      # ['age', 'salary', 'is_active']
```

**Example Output:**
```
📊 Column Type Analysis
==================================================

📝 Categorical Columns (2 total):
    1. name                 (unique values: 3)
    2. city                 (unique values: 3)

🔢 Numerical Columns (3 total):
    1. age                  (dtype: int64)
    2. salary               (dtype: int64)
    3. is_active            (dtype: bool)

📈 Summary:
   Total columns: 5
   Categorical: 2 (40.0%)
   Numerical: 3 (60.0%)
```

**Function Features:**
- 🔍 **Simple Classification**: Separates columns into categorical (object dtype) and numerical (all other dtypes)
- 📊 **Detailed Information**: Shows unique value counts for categorical columns and data types for numerical columns
- 📈 **Summary Statistics**: Provides percentage breakdown of column types
- 🎯 **Return Values**: Returns dictionary with categorized column lists for programmatic use
- ⚡ **Fast Processing**: Efficient classification based on pandas data types
- 🛡️ **Error Handling**: Validates input and handles edge cases like empty DataFrames

### Data Imputation with `impute_numerical_median` and `impute_categorical_mode`

After analyzing your data, you often need to handle missing values. The edaflow package provides two specialized imputation functions for this purpose:

#### Numerical Imputation with `impute_numerical_median`

The `impute_numerical_median` function fills missing values in numerical columns using the median value:

```python
import pandas as pd
import edaflow

# Create sample data with missing numerical values
df = pd.DataFrame({
    'age': [25, None, 35, None, 45],
    'salary': [50000, 60000, None, 70000, None],
    'score': [85.5, None, 92.0, 88.5, None],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
})

# Impute all numerical columns with median values
df_imputed = edaflow.impute_numerical_median(df)

# Impute specific columns only
df_imputed = edaflow.impute_numerical_median(df, columns=['age', 'salary'])

# Impute in place (modifies original DataFrame)
edaflow.impute_numerical_median(df, inplace=True)
```

**Function Features:**
- 🔢 **Smart Detection**: Automatically identifies numerical columns (int, float, etc.)
- 📊 **Median Imputation**: Uses median values which are robust to outliers
- 🎯 **Selective Imputation**: Option to specify which columns to impute
- 🔄 **Inplace Option**: Modify original DataFrame or create new one
- 🛡️ **Safe Handling**: Gracefully handles edge cases like all-missing columns
- 📋 **Detailed Reporting**: Shows exactly what was imputed and summary statistics

#### Categorical Imputation with `impute_categorical_mode`

The `impute_categorical_mode` function fills missing values in categorical columns using the mode (most frequent value):

```python
import pandas as pd
import edaflow

# Create sample data with missing categorical values
df = pd.DataFrame({
    'category': ['A', 'B', 'A', None, 'A'],
    'status': ['Active', None, 'Active', 'Inactive', None],
    'priority': ['High', 'Medium', None, 'Low', 'High'],
    'age': [25, 30, 35, 40, 45]
})

# Impute all categorical columns with mode values
df_imputed = edaflow.impute_categorical_mode(df)

# Impute specific columns only
df_imputed = edaflow.impute_categorical_mode(df, columns=['category', 'status'])

# Impute in place (modifies original DataFrame)
edaflow.impute_categorical_mode(df, inplace=True)
```

**Function Features:**
- 📝 **Smart Detection**: Automatically identifies categorical (object) columns
- 🎯 **Mode Imputation**: Uses most frequent value for each column
- ⚖️ **Tie Handling**: Gracefully handles mode ties (multiple values with same frequency)
- 🔄 **Inplace Option**: Modify original DataFrame or create new one
- 🛡️ **Safe Handling**: Gracefully handles edge cases like all-missing columns
- 📋 **Detailed Reporting**: Shows exactly what was imputed and mode tie warnings

#### Complete Imputation Workflow Example

```python
import pandas as pd
import edaflow

# Sample data with both numerical and categorical missing values
df = pd.DataFrame({
    'age': [25, None, 35, None, 45],
    'salary': [50000, None, 70000, 80000, None],
    'category': ['A', 'B', None, 'A', None],
    'status': ['Active', None, 'Active', 'Inactive', None],
    'score': [85.5, 92.0, None, 88.5, None]
})

print("Original DataFrame:")
print(df)
print("\n" + "="*50)

# Step 1: Impute numerical columns
print("STEP 1: Numerical Imputation")
df_step1 = edaflow.impute_numerical_median(df)

# Step 2: Impute categorical columns
print("\nSTEP 2: Categorical Imputation")
df_final = edaflow.impute_categorical_mode(df_step1)

print("\nFinal DataFrame (all missing values imputed):")
print(df_final)

# Verify no missing values remain
print(f"\nMissing values remaining: {df_final.isnull().sum().sum()}")
```

**Expected Output:**
```
🔢 Numerical Missing Value Imputation (Median)
=======================================================
🔄 age                  - Imputed 2 values with median: 35.0
🔄 salary               - Imputed 2 values with median: 70000.0
🔄 score                - Imputed 1 values with median: 88.75

📊 Imputation Summary:
   Columns processed: 3
   Columns imputed: 3
   Total values imputed: 5

📝 Categorical Missing Value Imputation (Mode)
=======================================================
🔄 category             - Imputed 2 values with mode: 'A'
🔄 status               - Imputed 1 values with mode: 'Active'

📊 Imputation Summary:
   Columns processed: 2
   Columns imputed: 2
   Total values imputed: 3
```

### Numerical Distribution Analysis with `visualize_numerical_boxplots`

Analyze numerical columns to detect outliers, understand distributions, and assess skewness:

```python
import pandas as pd
import edaflow

# Create sample dataset with outliers
df = pd.DataFrame({
    'age': [25, 30, 35, 40, 45, 28, 32, 38, 42, 100],  # 100 is an outlier
    'salary': [50000, 60000, 75000, 80000, 90000, 55000, 65000, 70000, 85000, 250000],  # 250000 is outlier
    'experience': [2, 5, 8, 12, 15, 3, 6, 9, 13, 30],  # 30 might be an outlier
    'score': [85, 92, 78, 88, 95, 82, 89, 91, 86, 20],  # 20 is an outlier
    'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C']  # Non-numerical
})

# Basic boxplot analysis
edaflow.visualize_numerical_boxplots(
    df, 
    title="Employee Data Analysis - Outlier Detection",
    show_skewness=True
)

# Custom layout and specific columns
edaflow.visualize_numerical_boxplots(
    df, 
    columns=['age', 'salary'],
    rows=1, 
    cols=2,
    title="Age vs Salary Analysis",
    orientation='vertical',
    color_palette='viridis'
)
```

**Expected Output:**
```
📊 Creating boxplots for 4 numerical column(s): age, salary, experience, score

📈 Summary Statistics:
==================================================
📊 age:
   Range: 25.00 to 100.00
   Median: 36.50
   IQR: 11.00 (Q1: 30.50, Q3: 41.50)
   Skewness: 2.66 (highly skewed)
   Outliers: 1 values outside [14.00, 58.00]
   Outlier values: [100]

📊 salary:
   Range: 50000.00 to 250000.00
   Median: 72500.00
   IQR: 22500.00 (Q1: 61250.00, Q3: 83750.00)
   Skewness: 2.88 (highly skewed)
   Outliers: 1 values outside [27500.00, 117500.00]
   Outlier values: [250000]

📊 experience:
   Range: 2.00 to 30.00
   Median: 8.50
   IQR: 7.50 (Q1: 5.25, Q3: 12.75)
   Skewness: 1.69 (highly skewed)
   Outliers: 1 values outside [-6.00, 24.00]
   Outlier values: [30]

📊 score:
   Range: 20.00 to 95.00
   Median: 87.00
   IQR: 7.75 (Q1: 82.75, Q3: 90.50)
   Skewness: -2.87 (highly skewed)
   Outliers: 1 values outside [71.12, 102.12]
   Outlier values: [20]
```

### Complete EDA Workflow Example

```python
import pandas as pd
import edaflow

# Load your dataset
df = pd.read_csv('customer_data.csv')

print("=== EXPLORATORY DATA ANALYSIS WITH EDAFLOW ===")
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Step 1: Check for missing data
null_analysis = edaflow.check_null_columns(df, threshold=15)
null_analysis  # Shows color-coded missing data summary

# Step 2: Analyze categorical columns for data type issues
edaflow.analyze_categorical_columns(df, threshold=30)

# Step 3: Convert appropriate columns to numeric automatically
df_cleaned = edaflow.convert_to_numeric(df, threshold=30)

# Step 4: Visualize categorical column values in detail
edaflow.visualize_categorical_values(df_cleaned, max_unique_values=10)

# Step 5: Display column type classification
column_types = edaflow.display_column_types(df_cleaned)

# Step 6: Handle missing values with imputation
# Impute numerical columns with median
df_numeric_imputed = edaflow.impute_numerical_median(df_cleaned)
# Impute categorical columns with mode
df_fully_imputed = edaflow.impute_categorical_mode(df_numeric_imputed)

# Step 7: Visualize numerical distributions and outliers
edaflow.visualize_numerical_boxplots(
    df_fully_imputed,
    title="Distribution Analysis - Outlier Detection",
    show_skewness=True,
    orientation='horizontal'
)

# Step 8: Handle outliers with median replacement
df_outliers_handled = edaflow.handle_outliers_median(
    df_fully_imputed,
    method='iqr',
    iqr_multiplier=1.5,
    verbose=True
)

# Step 9: Post-outlier handling verification
edaflow.visualize_numerical_boxplots(
    df_outliers_handled,
    title="After Outlier Handling - Clean Distribution",
    show_skewness=True,
    orientation='horizontal'
)

# Final data review (using rich styled functions or simple prints as needed)
print("Original data types:")
print(df.dtypes)
print("\nCleaned data types:")
print(df_outliers_handled.dtypes)
print(f"\nOriginal dataset shape: {df.shape}")
print(f"Final dataset shape: {df_outliers_handled.shape}")
print(f"Missing values remaining: {df_outliers_handled.isnull().sum().sum()}")

# Compare outlier statistics
print("\nOutlier handling summary:")
for col in df_fully_imputed.select_dtypes(include=['number']).columns:
    original_range = f"{df_fully_imputed[col].min():.2f} to {df_fully_imputed[col].max():.2f}"
    cleaned_range = f"{df_outliers_handled[col].min():.2f} to {df_outliers_handled[col].max():.2f}"
    print(f"  {col}: {original_range} → {cleaned_range}")

# Step 10: Interactive visualization for final data exploration
edaflow.visualize_interactive_boxplots(
    df_outliers_handled,
    title="Final Interactive Data Exploration",
    height=600,
    show_points='outliers'  # Show any remaining outliers as interactive points
)

# Step 11: Comprehensive heatmap analysis for relationships
# Correlation heatmap to understand variable relationships
edaflow.visualize_heatmap(
    df_outliers_handled,
    heatmap_type="correlation",
    title="Final Correlation Analysis After Data Cleaning",
    method="pearson"
)

# Missing data pattern heatmap (if any missing values remain)
edaflow.visualize_heatmap(
    df_outliers_handled,
    heatmap_type="missing",
    title="Remaining Missing Data Patterns"
)

# Now your data is ready for further analysis!
# You can proceed with:
# - Statistical analysis
# - Machine learning preprocessing  
# - Visualization
# - Advanced EDA techniques
```

### Outlier Handling with `handle_outliers_median`

The `handle_outliers_median` function complements the boxplot visualization by providing automated outlier detection and replacement with median values. This creates a complete outlier analysis workflow:

```python
import pandas as pd
import numpy as np
import edaflow

# Create sample data with outliers
np.random.seed(42)
df = pd.DataFrame({
    'sales': [100, 120, 110, 105, 115, 2000, 95, 125],  # 2000 is an outlier
    'age': [25, 30, 28, 35, 32, 29, 31, 33],  # Clean data
    'price': [50, 55, 48, 52, 51, -100, 49, 53],  # -100 is an outlier
    'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B']  # Non-numerical
})

# Step 1: Visualize outliers first
edaflow.visualize_numerical_boxplots(
    df, 
    title="Before Outlier Handling",
    show_skewness=True
)

# Step 2: Handle outliers using IQR method (default)
df_clean = edaflow.handle_outliers_median(df, verbose=True)

# Step 3: Visualize after cleaning
edaflow.visualize_numerical_boxplots(
    df_clean,
    title="After Outlier Handling", 
    show_skewness=True
)

# Alternative: Handle specific columns only
df_sales_clean = edaflow.handle_outliers_median(
    df, 
    columns=['sales'],  # Only clean sales column
    method='iqr',
    iqr_multiplier=1.5,
    verbose=True
)

# Alternative: Use Z-score method for outlier detection
df_zscore_clean = edaflow.handle_outliers_median(
    df,
    method='zscore',  # Z-score method (|z| > 3)
    verbose=True
)

# Alternative: Use modified Z-score (more robust)
df_mod_zscore_clean = edaflow.handle_outliers_median(
    df,
    method='modified_zscore',  # Modified Z-score using MAD
    verbose=True
)

# Modify original DataFrame in place
edaflow.handle_outliers_median(df, inplace=True, verbose=True)
print("Original DataFrame now cleaned!")
```

**Outlier Detection Methods:**
- 🎯 **IQR Method** (default): Values outside Q1 - 1.5×IQR to Q3 + 1.5×IQR
- 📊 **Z-Score Method**: Values with |z-score| > 3
- 🎪 **Modified Z-Score**: Uses median absolute deviation, more robust to outliers

**Key Features:**
- 🔍 **Multiple Detection Methods**: Choose between IQR, Z-score, or modified Z-score
- 🎯 **Median Replacement**: Replaces outliers with column median (robust central tendency)
- 📊 **Detailed Reporting**: Shows exactly which values were replaced and why
- 🔧 **Flexible Column Selection**: Process all numerical columns or specify which ones
- 💾 **Safe Operation**: Default behavior preserves original data (inplace=False)
- 📈 **Statistical Summary**: Displays before/after statistics for transparency

### Interactive Boxplot Visualization with `visualize_interactive_boxplots`

The `visualize_interactive_boxplots` function provides an interactive Plotly Express-based boxplot visualization that complements the static matplotlib boxplots with full interactivity. This is perfect for final data exploration and presentation:

```python
import pandas as pd
import numpy as np
import edaflow

# Create sample data for demonstration
np.random.seed(42)
df = pd.DataFrame({
    'age': np.random.normal(35, 10, 100),
    'salary': np.random.normal(60000, 15000, 100),
    'experience': np.random.normal(8, 4, 100),
    'rating': np.random.normal(4.2, 0.8, 100),
    'category': np.random.choice(['A', 'B', 'C'], 100)
})

# Basic interactive boxplot (all numerical columns)
edaflow.visualize_interactive_boxplots(df)

# Customized interactive visualization
edaflow.visualize_interactive_boxplots(
    df,
    columns=['age', 'salary'],  # Specific columns only
    title="Age and Salary Distribution Analysis",
    height=500,
    show_points='all',  # Show all data points
    color_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
)

# Advanced customization
edaflow.visualize_interactive_boxplots(
    df,
    title="Complete Salary Analysis Dashboard",
    height=700,
    show_points='outliers',  # Only show outlier points
    color_sequence=['steelblue']
)
```

**Interactive Features:**
- 🖱️ **Hover Information**: Detailed statistics appear on hover
- 🔍 **Zoom & Pan**: Click and drag to zoom, double-click to reset
- 📊 **Statistical Tooltips**: Median, quartiles, and outlier information
- 💾 **Export Options**: Built-in toolbar for saving plots
- 🎨 **Custom Styling**: Full control over colors, dimensions, and layout

**Key Features:**
- 🎯 **Plotly Express Integration**: Full px.box functionality with enhanced features
- 📈 **Automatic Statistics**: Displays comprehensive statistical summaries
- 🎨 **Customizable Styling**: Colors, dimensions, and layout options
- 📊 **Smart Column Selection**: Automatically detects numerical columns
- 🖥️ **Responsive Design**: Works perfectly in Jupyter notebooks and standalone
- 📋 **Detailed Reporting**: Comprehensive statistical analysis with emoji formatting

**Perfect for:**
- 📊 Final data exploration after cleaning
- 🎨 Interactive presentations and dashboards
- 🔍 Detailed outlier investigation
- 📈 Sharing insights with stakeholders

### Comprehensive Heatmap Visualizations with `visualize_heatmap`

The `visualize_heatmap` function provides multiple types of heatmap visualizations essential for comprehensive exploratory data analysis. This powerful function covers correlation analysis, missing data patterns, data values visualization, and categorical relationships:

```python
import pandas as pd
import numpy as np
import edaflow

# Create sample data for demonstration
np.random.seed(42)
df = pd.DataFrame({
    'age': np.random.normal(35, 10, 100),
    'salary': np.random.normal(60000, 15000, 100),
    'experience': np.random.normal(8, 4, 100),
    'rating': np.random.normal(4.2, 0.8, 100),
    'department': np.random.choice(['Engineering', 'Sales', 'Marketing'], 100),
    'level': np.random.choice(['Junior', 'Senior', 'Lead'], 100)
})

# 1. Correlation Heatmap (Default)
edaflow.visualize_heatmap(df)

# 2. Custom Correlation Analysis
edaflow.visualize_heatmap(
    df,
    heatmap_type="correlation",
    method="spearman",  # Use Spearman correlation
    title="Spearman Correlation Matrix",
    cmap="coolwarm",
    figsize=(10, 8)
)

# 3. Missing Data Pattern Analysis
edaflow.visualize_heatmap(
    df,
    heatmap_type="missing",
    title="Missing Data Patterns",
    missing_threshold=5.0  # Highlight columns with >5% missing
)

# 4. Data Values Heatmap (for small datasets)
edaflow.visualize_heatmap(
    df.head(25),  # Use first 25 rows
    heatmap_type="values",
    title="Data Values Visualization",
    cmap="viridis"
)

# 5. Cross-tabulation Heatmap
edaflow.visualize_heatmap(
    df,
    heatmap_type="crosstab",
    title="Department vs Level Distribution",
    cmap="Blues"
)

# 6. Advanced Customization
edaflow.visualize_heatmap(
    df,
    columns=['age', 'salary', 'experience', 'rating'],  # Specific columns
    title="Key Metrics Correlation Analysis",
    method="kendall",
    annot=True,
    fmt='.3f',
    linewidths=1.0,
    cbar_kws={'label': 'Correlation Coefficient'}
)
```

**Heatmap Types Available:**

🔥 **Correlation Heatmap (`"correlation"`):**
- 📊 **Purpose**: Analyze relationships between numerical variables
- 🔢 **Methods**: Pearson, Spearman, Kendall correlations
- 💡 **Insights**: Identifies strong positive/negative correlations, multicollinearity
- 🎯 **Best for**: Feature selection, understanding variable relationships

🕳️ **Missing Data Heatmap (`"missing"`):**
- 📊 **Purpose**: Visualize missing data patterns across columns
- 🔍 **Features**: Pattern detection, missing percentage analysis
- 💡 **Insights**: Identifies systematic missing data, data quality issues
- 🎯 **Best for**: Data quality assessment, imputation strategy planning

🔢 **Values Heatmap (`"values"`):**
- 📊 **Purpose**: Visualize actual data values (normalized 0-1)
- 📏 **Features**: Row-by-row value comparison, pattern identification
- 💡 **Insights**: Spot outliers, understand data distribution patterns
- 🎯 **Best for**: Small datasets, detailed data inspection

📋 **Cross-tabulation Heatmap (`"crosstab"`):**
- 📊 **Purpose**: Analyze relationships between categorical variables
- 🔢 **Features**: Frequency analysis, category distribution
- 💡 **Insights**: Understand categorical dependencies, group distributions
- 🎯 **Best for**: Categorical data analysis, segment analysis

**Key Features:**
- 🎨 **Multiple Visualization Types**: 4 different heatmap types for comprehensive analysis
- 📊 **Automatic Statistics**: Detailed correlation insights and missing data summaries
- 🔧 **Flexible Customization**: Full control over colors, sizing, annotations
- 🎯 **Smart Column Detection**: Automatically selects appropriate columns for each type
- 📈 **Responsive Design**: Auto-sizing based on data dimensions
- 💪 **Robust Error Handling**: Comprehensive validation and informative error messages
- 📋 **Detailed Reporting**: Statistical summaries with emoji-formatted output

**Statistical Insights Provided:**
- 🔺 Strongest positive and negative correlations
- 💪 Count of strong correlations (>0.7, <-0.7)
- 📊 Missing data percentages and patterns
- 🔢 Data range and distribution summaries
- 📈 Cross-tabulation frequencies and totals

### Statistical Histogram Analysis with `visualize_histograms` (NEW!)

The `visualize_histograms` function provides comprehensive distribution analysis with advanced skewness detection, normality testing, and statistical insights. This powerful visualization combines histograms with KDE curves, normal distribution overlays, and detailed statistical assessments:

```python
import pandas as pd
import numpy as np
import edaflow

# Create sample data with different distribution shapes
np.random.seed(42)
df = pd.DataFrame({
    'normal_dist': np.random.normal(100, 15, 1000),
    'right_skewed': np.random.exponential(2, 1000),  
    'left_skewed': 10 - np.random.exponential(2, 1000),
    'uniform': np.random.uniform(0, 100, 1000),
    'bimodal': np.concatenate([
        np.random.normal(30, 5, 500),
        np.random.normal(70, 5, 500)
    ])
})

# 1. Basic Histogram Analysis (All Numerical Columns)
edaflow.visualize_histograms(df)

# 2. Customized Histogram with Statistical Features
edaflow.visualize_histograms(
    df,
    columns=['normal_dist', 'right_skewed'],  # Specific columns
    kde=True,  # Add KDE curves
    show_normal_curve=True,  # Add normal distribution overlay
    show_stats=True,  # Display statistical text box
    title="Distribution Analysis with Statistical Overlays"
)

# 3. Advanced Customization
edaflow.visualize_histograms(
    df,
    bins=30,  # Custom bin count
    alpha=0.7,  # Transparency
    figsize=(15, 10),  # Custom figure size
    colors=['skyblue', 'lightcoral', 'lightgreen'],
    title="Custom Styled Distribution Analysis"
)

# 4. Single Column Detailed Analysis
edaflow.visualize_histograms(
    df,
    columns=['bimodal'],
    kde=True,
    show_normal_curve=True,
    show_stats=True,
    title="Detailed Bimodal Distribution Analysis"
)
```

**🎯 Key Features:**

**📊 Comprehensive Distribution Analysis:**
- 📈 Multi-column histogram visualization with subplots
- 🔍 Automatic skewness detection and interpretation
- 📊 Kurtosis analysis (normal, heavy-tailed, light-tailed)
- 📏 Basic statistics (mean, median, std, range, sample size)

**🧪 Advanced Statistical Testing:**
- 🔬 **Shapiro-Wilk Test**: Tests normality for smaller samples
- 📊 **Jarque-Bera Test**: Tests normality using skewness and kurtosis
- 📈 **Anderson-Darling Test**: Powerful normality test with critical values
- ✅ **Automated Interpretation**: Clear pass/fail results with p-values

**⚖️ Skewness Detection & Interpretation:**
- 🟢 **Normal/Symmetric** (|skew| < 0.5): Approximately symmetric distribution
- 🟡 **Moderately Skewed** (0.5 ≤ |skew| < 1): Noticeable but manageable skew
- 🔴 **Highly Skewed** (|skew| ≥ 1): Significant skew requiring transformation
- 📈 **Direction Analysis**: Right-skewed (positive) vs Left-skewed (negative)

**📈 Visual Enhancements:**
- 🎨 **KDE Curves**: Smooth density estimation overlays
- 📊 **Normal Distribution Overlay**: Compare actual vs theoretical normal
- 📏 **Mean/Median Lines**: Visual reference lines with values
- 📋 **Statistical Text Boxes**: Comprehensive stats display on plots

**💡 Transformation Recommendations:**
- 📈 **Right Skew**: Suggests log, sqrt, or Box-Cox transformations
- 📉 **Left Skew**: Suggests square, exponential, or reflect + transform
- 🎯 **Actionable Insights**: Specific recommendations based on skewness level

**🔍 Distribution Shape Insights:**
- 📊 **Kurtosis Interpretation**: 
  - 🟢 Normal (mesokurtic): -0.5 to 0.5
  - 🔺 Heavy-tailed (leptokurtic): > 0.5
  - 🔻 Light-tailed (platykurtic): < -0.5
- 📈 **Pattern Recognition**: Identifies normal, uniform, bimodal, exponential patterns
- 🎯 **Statistical Summary**: Overall assessment of distribution health

**Example Output Summary:**
```
📈 Distribution Analysis Summary:
============================================================
🔢 normal_dist:
   📊 Basic Stats: μ=100.29, σ=14.69, median=100.38
   📏 Range: 51.38 to 157.79
   📈 Sample Size: 1,000 observations
   ⚖️  Skewness: 0.117 - 🟢 NORMAL - Approximately symmetric distribution
   📊 Kurtosis: 0.073 - 🟢 NORMAL - Normal tail behavior (mesokurtic)
   🧪 Normality Assessment:
      Shapiro-Wilk: ✅ Likely Normal (p=0.6273)
      Jarque-Bera: ✅ Likely Normal (p=0.2928)

🎯 Overall Distribution Summary:
🟢 Normal/Symmetric: 1/1 columns
🟡 Moderately Skewed: 0/1 columns  
🔴 Highly Skewed: 0/1 columns
```

**Perfect for:**
- 🔍 **Distribution Assessment**: Understanding data shape before modeling
- 📊 **Normality Testing**: Determining if data meets normal distribution assumptions
- 🎯 **Data Transformation Planning**: Identifying which columns need transformation
- 📈 **Statistical Reporting**: Comprehensive distribution documentation
- 🧪 **Assumption Validation**: Verifying statistical test prerequisites

### Integration with Jupyter Notebooks

For the best experience, use these functions in Jupyter notebooks where:
- `check_null_columns()` displays beautiful color-coded tables
- `analyze_categorical_columns()` shows colored terminal output
- You can iterate quickly on data cleaning decisions

```python
# In Jupyter notebook cell
import pandas as pd
import edaflow

df = pd.read_csv('your_data.csv')

# This will display a nicely formatted, color-coded table
edaflow.check_null_columns(df)
```

# Load your dataset
df = pd.read_csv('data.csv')

# Analyze categorical columns to identify potential issues
edaflow.analyze_categorical_columns(df, threshold=35)

# This will identify:
# - Object columns that might actually be numeric (need conversion)
# - Truly categorical columns with their unique values
# - Mixed data type issues
```

### Scatter Matrix Analysis

Create comprehensive pairwise relationship visualizations with advanced customization options:

```python
import pandas as pd
import edaflow

# Load your dataset
df = pd.read_csv('data.csv')

# Basic scatter matrix for numerical columns
edaflow.visualize_scatter_matrix(df)

# Custom scatter matrix with specific columns
numeric_cols = ['age', 'income', 'score', 'rating']
edaflow.visualize_scatter_matrix(df, columns=numeric_cols)

# Advanced configuration with color coding
edaflow.visualize_scatter_matrix(
    df, 
    columns=['feature1', 'feature2', 'feature3'],
    color_by='category',         # Color points by category
    diagonal='kde',              # Use KDE plots on diagonal
    upper='corr',                # Show correlations in upper triangle
    lower='scatter',             # Scatter plots in lower triangle
    figsize=(12, 12)
)

# Matrix with regression lines
edaflow.visualize_scatter_matrix(
    df,
    regression_type='linear',    # Add linear regression lines
    alpha=0.7,                   # Semi-transparent points
    diagonal='hist',             # Histograms on diagonal
    figsize=(12, 12)            # Custom figure size
)

# Advanced statistical analysis
edaflow.visualize_scatter_matrix(
    df,
    columns=['x1', 'x2', 'x3', 'x4'],
    regression_type='linear',    # Linear regression lines  
    upper='blank',               # Clean upper triangle
    lower='scatter',             # Focus on lower scatter plots
    color_by='group',            # Color by categorical variable
    figsize=(15, 15)
)
```

**Key Features:**
- **Flexible Layout**: Configure diagonal, upper triangle, and lower triangle independently
- **Multiple Plot Types**: Histograms, KDE plots, box plots, scatter plots, correlation values
- **Statistical Analysis**: Linear, polynomial, and LOWESS regression lines
- **Color Coding**: Visualize relationships by categorical variables
- **Customizable Styling**: Control figure size, transparency, colors, and more
- **Smart Defaults**: Automatically handles missing data and optimal plot configurations

**Diagonal Options:**
- `'hist'`: Histograms showing distribution of each variable
- `'kde'`: Kernel Density Estimation plots for smooth distributions  
- `'box'`: Box plots showing quartiles and outliers

**Triangle Options:**
- `'scatter'`: Scatter plots showing pairwise relationships
- `'corr'`: Correlation coefficients with color coding
- `'blank'`: Empty space for cleaner presentation

**Regression Line Types:**
- `'linear'`: Linear regression lines
- `'poly2'`: 2nd degree polynomial curves
- `'poly3'`: 3rd degree polynomial curves
- `'lowess'`: LOWESS smoothing curves

Perfect for exploring complex relationships in multivariate datasets and identifying patterns, correlations, and outliers across multiple dimensions.

### EDA Insights Summary with `summarize_eda_insights` (NEW in v0.12.28!)

After completing your exploratory data analysis workflow, generate comprehensive insights and actionable recommendations with a single function call:

```python
import pandas as pd
import edaflow

# After completing your EDA workflow
df = pd.read_csv('healthcare_data.csv')

# Run various edaflow functions first...
null_analysis = edaflow.check_null_columns(df)
edaflow.analyze_categorical_columns(df)
df_clean = edaflow.convert_to_numeric(df)
# ... additional EDA functions ...

# Generate comprehensive insights
insights = edaflow.summarize_eda_insights(
    df_clean, 
    target_column='diagnosis',  # Your target column
    eda_functions_used=['check_null_columns', 'analyze_categorical_columns', 'convert_to_numeric'],
    class_threshold=0.1  # Flag classes with <10% representation
)

# Access structured insights
print("Dataset Overview:", insights['dataset_overview'])
print("Data Quality:", insights['data_quality'])
print("Recommendations:", insights['recommendations'])
```

**What It Analyzes:**
- 📊 **Dataset Characteristics**: Shape, memory usage, feature distribution
- 🔍 **Data Quality Assessment**: Missing data patterns, completeness scores
- ⚖️ **Class Balance Detection**: Identifies underrepresented classes for imbalanced datasets
- 📈 **Feature Type Analysis**: Categorical vs numerical distributions
- 🎯 **Smart Recommendations**: Actionable next steps for modeling and preprocessing

**Key Features:**
- ✅ **Comprehensive Analysis**: Single function covers all major EDA aspects
- ✅ **Target-Aware**: Provides classification/regression specific insights
- ✅ **Function Tracking**: Knows which edaflow functions you've already used
- ✅ **Customizable Thresholds**: Adjust class imbalance detection sensitivity
- ✅ **Structured Output**: Returns organized dictionary for programmatic use
- ✅ **Beautiful Display**: Rich formatting with colors and tables when available

## 🖼️ Computer Vision EDA with `visualize_image_classes()` (NEW in v0.9.0!)

Comprehensive exploratory data analysis for image classification datasets with professional visualizations and statistical insights.

### Complete Image Classification EDA Workflow

```python
import edaflow
import pandas as pd

# Method 1: Directory-based Analysis (Most Common)
# Dataset organized as: dataset/train/cats/, dataset/train/dogs/, etc.
edaflow.visualize_image_classes(
    data_source='dataset/train/',   # Directory with class subfolders
    samples_per_class=8,            # Show 8 random samples per class
    show_class_counts=True,         # Display distribution analysis
    figsize=(18, 12)               # Large figure for detailed view
)

# Method 2: DataFrame-based Analysis  
df = pd.DataFrame({
    'image_path': ['images/cat1.jpg', 'images/dog1.jpg', ...],
    'class': ['cat', 'dog', 'bird', 'fish', ...],
    'split': ['train', 'val', 'test', ...]
})

# Comprehensive analysis with statistics
stats = edaflow.visualize_image_classes(
    data_source=df,
    image_column='image_path',
    label_column='class',
    samples_per_class=6,
    show_image_info=True,       # Show dimensions and file sizes
    return_stats=True,          # Get detailed statistics
    title="Medical Image Classification Dataset"
)

# Check dataset health
print(f"📊 Total classes: {stats['num_classes']}")
print(f"📈 Total samples: {stats['total_samples']:,}")
print(f"⚖️  Balance ratio: {stats['balance_ratio']:.3f}")

if stats['balance_ratio'] < 0.5:
    print("⚠️  Significant class imbalance detected!")
    print("💡 Consider data augmentation or resampling")

# Method 3: Production Dataset Validation
validation_stats = edaflow.visualize_image_classes(
    data_source=production_df,
    image_column='file_path',
    label_column='predicted_class',
    samples_per_class=10,
    shuffle_samples=False,      # Reproducible sampling
    save_path='dataset_report.png',  # Save for documentation
    return_stats=True
)
```

### Key Features

**📁 Flexible Input Support:**
- **Directory Structure**: Automatically detect classes from folder names
- **DataFrame Integration**: Work with existing metadata and file paths
- **Mixed Sources**: Handle various image formats and organizations

**📊 Comprehensive Analytics:**
```python
# What you get from the analysis:
{
    'class_counts': {'cats': 1200, 'dogs': 1150, 'birds': 890},
    'total_samples': 3240,
    'num_classes': 3,
    'balance_ratio': 0.742,  # Smallest class / Largest class
    'imbalance_warnings': ['birds has 25.8% fewer samples than average'],
    'corrupted_images': []   # List of problematic files
}
```

**🎨 Professional Visualizations:**
- **Smart Grid Layouts**: Automatically optimized for readability
- **Class Distribution Charts**: Visual and statistical balance analysis  
- **Random Sampling**: Representative samples from each class
- **Quality Indicators**: Highlight corrupted or unusual images
- **Technical Details**: Optional file sizes and dimensions display

**🔍 Quality Assessment:**
- ✅ **Balance Detection**: Identify over/under-represented classes
- ✅ **Corruption Checking**: Flag unreadable or damaged images  
- ✅ **Dimension Analysis**: Spot unusual aspect ratios or sizes
- ✅ **Statistical Summary**: Comprehensive dataset health metrics

### Perfect For:

**🎯 Initial Dataset Exploration:**
```python
# Quick dataset overview
edaflow.visualize_image_classes(data_source='new_dataset/', samples_per_class=5)
```

**🧪 Medical/Scientific Imaging:**
```python
# Detailed analysis for medical scans
edaflow.visualize_image_classes(
    data_source='medical_scans/',
    samples_per_class=4,
    figsize=(20, 15),
    show_image_info=True,
    title="Medical Scan Classification Analysis"
)
```

**📊 Production Monitoring:**
```python
# Validate production datasets
stats = edaflow.visualize_image_classes(
    data_source=production_data,
    image_column='path',
    label_column='label', 
    return_stats=True
)

# Automated quality checks
assert stats['balance_ratio'] > 0.3, "Class imbalance too severe!"
assert len(stats['corrupted_images']) == 0, "Corrupted images found!"
```

### Integration with Existing EDA Workflow

```python
# Complete ML Pipeline EDA
import edaflow

# 1. Understand your image dataset
stats = edaflow.visualize_image_classes(
    data_source='dataset/', 
    samples_per_class=8,
    return_stats=True
)

# 2. Prepare metadata for analysis  
metadata_df = prepare_metadata_from_stats(stats)

# 3. Apply traditional EDA to metadata
edaflow.check_null_columns(metadata_df)
edaflow.visualize_categorical_values(metadata_df)
edaflow.visualize_heatmap(metadata_df)

# 4. Ready for model training with confidence!
```

**🎓 Educational Benefits:**
- **Understand Dataset Characteristics**: Learn what makes a good training set
- **Identify Common Pitfalls**: Spot issues before they affect model performance  
- **Statistical Thinking**: Apply EDA principles to computer vision
- **Best Practices**: Learn industry-standard dataset validation techniques

## 🔍 Image Quality Assessment with `assess_image_quality()` (NEW in v0.10.0!)

Comprehensive automated quality assessment for image datasets, designed to identify potential issues that could impact model training performance.

### Complete Quality Assessment Workflow

```python
import edaflow

# Method 1: Comprehensive Quality Check
report = edaflow.assess_image_quality(
    'dataset/train/',              # Directory with images
    check_corruption=True,         # Detect corrupted files
    analyze_color=True,           # Color vs grayscale analysis
    detect_blur=True,             # Blur detection
    check_artifacts=True,         # Compression artifact detection
    brightness_threshold=(30, 220), # Brightness range
    contrast_threshold=20,        # Minimum contrast
    verbose=True                  # Detailed progress
)

print(f"📊 Quality Score: {report['quality_score']}/100")
print(f"🚨 Corrupted Images: {len(report['corrupted_images'])}")
print(f"💡 Recommendations: {len(report['recommendations'])}")

# Method 2: Production Pipeline Integration  
validation_report = edaflow.assess_image_quality(
    production_df,
    image_column='file_path',
    label_column='label',
    sample_size=1000,             # Sample for large datasets
    return_detailed_report=True   # Per-image analysis
)

# Automated quality gates
assert validation_report['quality_score'] >= 80, "Dataset quality too low!"
assert len(validation_report['corrupted_images']) == 0, "Corrupted images found!"

# Method 3: Medical/Scientific Imaging (Stricter Requirements)
medical_report = edaflow.assess_image_quality(
    medical_scans_paths,
    brightness_threshold=(50, 180),  # Narrow brightness range
    contrast_threshold=30,           # High contrast requirement
    aspect_ratio_tolerance=0.05,     # Strict dimension consistency
    file_size_outlier_factor=2.0,    # Sensitive to size anomalies
    check_artifacts=True             # Critical for medical data
)
```

### Key Features

**🔍 Comprehensive Quality Metrics:**
- **Corruption Detection**: Identify unreadable or damaged image files
- **Brightness Analysis**: Flag overly dark or bright images with statistical thresholds
- **Contrast Assessment**: Detect low-contrast images that might hurt training
- **Blur Detection**: Use Laplacian variance to identify potentially blurry images
- **Color Analysis**: Distinguish between grayscale and color images, detect mixed modes
- **Dimension Consistency**: Find unusual aspect ratios and size outliers
- **Artifact Detection**: Identify compression artifacts and unusual patterns

**📊 Statistical Insights:**
```python
# What you get from the analysis:
{
    'total_images': 5000,
    'corrupted_images': ['path/to/bad1.jpg', 'path/to/bad2.jpg'],
    'quality_score': 87,  # Overall score 0-100
    'brightness_analysis': {
        'brightness_stats': {'min': 25.3, 'max': 245.1, 'mean': 128.4},
        'problematic_count': 23,
        'percentage_problematic': 0.46
    },
    'blur_analysis': {
        'blurry_count': 15,
        'percentage_blurry': 0.3
    },
    'recommendations': [
        '🚨 Remove 2 corrupted image(s) before training',
        '💡 0.5% of images have brightness issues - consider histogram equalization'
    ]
}
```

**🎯 Production-Ready Features:**
- **Automated Quality Gates**: Set thresholds for pipeline validation
- **Scalable Analysis**: Sample large datasets for efficient processing
- **Detailed Reporting**: Per-image analysis for debugging issues
- **Class-wise Analysis**: Identify quality issues specific to certain classes
- **Flexible Thresholds**: Customize quality criteria for your domain

### Perfect For:

**🏥 Medical Imaging:**
```python
# Strict quality requirements for medical data
report = edaflow.assess_image_quality(
    medical_dataset,
    brightness_threshold=(60, 180),   # Narrow brightness range
    contrast_threshold=35,            # High contrast requirement
    detect_blur=True,                # Critical for diagnosis
    check_artifacts=True,            # Detect compression issues
    aspect_ratio_tolerance=0.03      # Very strict consistency
)
```

**🏭 Production ML Pipelines:**
```python
# Automated data validation
quality_report = edaflow.assess_image_quality(new_batch_images)

# Automated filtering
clean_images = [
    img for img in all_images 
    if img not in quality_report['corrupted_images']
]

# Quality monitoring
if quality_report['quality_score'] < 85:
    alert_data_team("Dataset quality degraded!")
```

**🔬 Research & Development:**
```python
# Compare dataset quality across experiments
before_report = edaflow.assess_image_quality('dataset_v1/')
after_report = edaflow.assess_image_quality('dataset_v2_cleaned/')

print(f"Quality improvement: {after_report['quality_score'] - before_report['quality_score']} points")
```

### Integration with Computer Vision EDA

```python
# Complete CV dataset validation workflow
import edaflow

# Step 1: Quality Assessment (NEW!)
quality_report = edaflow.assess_image_quality(
    'dataset/', 
    return_detailed_report=True
)

# Step 2: Remove problematic images
clean_dataset = [
    img for img in all_images 
    if img not in quality_report['corrupted_images']
]

# Step 3: Visual exploration with clean data
edaflow.visualize_image_classes(
    clean_dataset,
    samples_per_class=6,
    show_image_info=True
)

# Step 4: Ready for model training with confidence!
print(f"✅ Dataset validated: {quality_report['quality_score']}/100 quality score")
```

**🎓 Educational Benefits:**
- **Learn Quality Standards**: Understand what makes images suitable for ML
- **Identify Common Issues**: Learn to spot systematic problems in datasets
- **Quantitative Assessment**: Apply statistical methods to image quality
- **Production Readiness**: Build robust data validation pipelines

## 🎨 Image Feature Analysis with `analyze_image_features()` (NEW in v0.11.0!)

Deep statistical analysis of visual features across image classes including edge density, texture patterns, color distributions, and gradient characteristics. Perfect for understanding dataset characteristics, guiding feature engineering decisions, and identifying visual patterns that distinguish different classes.

### Complete Feature Analysis Workflow

```python
import edaflow

# Comprehensive feature analysis
features = edaflow.analyze_image_features(
    'dataset/train/',           # Dataset directory
    analyze_edges=True,         # Edge detection analysis
    analyze_texture=True,       # Texture pattern analysis
    analyze_color=True,         # Color distribution analysis
    analyze_gradients=True,     # Gradient pattern analysis
    create_visualizations=True  # Generate comprehensive plots
)

# Check most discriminative features
print("Top discriminative features:")
for feature, score in features['feature_rankings'][:5]:
    print(f"  {feature}: {score:.3f}")

# Get actionable insights
for rec in features['recommendations']:
    print(f"💡 {rec}")
```

### Advanced Feature Engineering Guidance

```python
# Focus on specific feature types for different domains
medical_features = edaflow.analyze_image_features(
    medical_df,
    image_column='scan_path',
    label_column='diagnosis',
    analyze_color=False,        # Medical scans often grayscale
    analyze_texture=True,       # Critical for medical diagnosis
    analyze_edges=True,         # Important for structure detection
    texture_method='lbp',
    lbp_radius=5,              # Larger radius for medical details
    edge_method='canny'
)

# Production feature selection pipeline
production_features = edaflow.analyze_image_features(
    production_dataset,
    sample_size=500,           # Sample for efficiency
    color_spaces=['RGB', 'HSV', 'LAB'],  # Multiple color spaces
    bins_per_channel=32,       # Balanced detail vs speed
    return_feature_vectors=True # Get raw features for ML
)

# Use results for feature selection
top_features = production_features['feature_rankings'][:10]
feature_vectors = production_features['feature_vectors']
```

### Understanding Feature Analysis Results

The function returns a comprehensive dictionary with:

- **`'edge_analysis'`**: Edge density statistics and distributions per class
- **`'texture_analysis'`**: Texture descriptor statistics and patterns (LBP, uniformity, contrast)
- **`'color_analysis'`**: Color histogram distributions across RGB, HSV, LAB color spaces
- **`'gradient_analysis'`**: Gradient magnitude and direction statistics
- **`'feature_rankings'`**: Most discriminative features between classes (sorted by discriminative power)
- **`'recommendations'`**: Actionable insights for feature engineering and preprocessing
- **`'class_comparisons'`**: Statistical comparisons between classes

### Complete Computer Vision EDA Pipeline

```python
# Complete workflow: Quality → Features → Visualization
import edaflow

# Step 1: Quality assessment
quality_report = edaflow.assess_image_quality('dataset/')

# Step 2: Feature analysis
feature_report = edaflow.analyze_image_features(
    'dataset/',
    create_visualizations=True
)

# Step 3: Visual exploration
class_stats = edaflow.visualize_image_classes(
    data_source='dataset/',
    samples_per_class=6
)

# Step 4: Comprehensive dataset insights
print(f"📊 Quality Score: {quality_report['quality_score']}/100")
print(f"🎯 Top Feature: {feature_report['feature_rankings'][0][0]}")
print(f"📈 Class Balance: {class_stats['class_balance']}")
print(f"🔍 Total Images: {class_stats['total_images']}")

# Ready for informed model development!
```

**🎓 Educational Benefits:**
- **Feature Engineering Guidance**: Understand which visual features distinguish your classes
- **Quantitative Analysis**: Learn to apply statistical methods to visual data
- **Model Architecture Decisions**: Use insights to choose appropriate CNN architectures
- **Dataset Understanding**: Identify biases, patterns, and preprocessing needs
- **Research Applications**: Compare feature distributions across different datasets

### Working with Data (Future Implementation)
```python
import pandas as pd
import edaflow

# Load your dataset
df = pd.read_csv('data.csv')

# Perform EDA workflow
# summary = edaflow.quick_summary(df)
# edaflow.plot_overview(df)
# clean_df = edaflow.clean_data(df)
```

## Project Structure

```
edaflow/
├── edaflow/
│   ├── __init__.py
│   ├── analysis/
│   ├── visualization/
│   └── preprocessing/
├── tests/
├── docs/
├── examples/
├── setup.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/evanlow/edaflow.git
cd edaflow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 edaflow/
black edaflow/
isort edaflow/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

> **🚀 Latest Updates**: This changelog reflects the most current releases including v0.12.32 critical input validation fix, v0.12.31 hotfix with KeyError resolution and v0.12.30 universal display optimization breakthrough.

### v0.12.32 (2025-08-11) - Critical Input Validation Fix 🐛
- **CRITICAL**: Fixed AttributeError: 'tuple' object has no attribute 'empty' in visualization functions
- **ROOT CAUSE**: Users passing tuple result from `apply_smart_encoding(..., return_encoders=True)` directly to visualization functions
- **ENHANCED**: Added intelligent input validation with helpful error messages for common usage mistakes
- **IMPROVED**: Better error handling in `visualize_scatter_matrix` and other visualization functions
- **DOCUMENTED**: Clear examples showing correct vs incorrect usage patterns for `apply_smart_encoding`
- **STABILITY**: Prevents crashes in step 14 of EDA workflows when encoding functions are misused

### v0.12.31 (2025-01-05) - Critical KeyError Hotfix 🚨
- **CRITICAL**: Fixed KeyError: 'type' in `summarize_eda_insights()` function during Google Colab usage
- **RESOLVED**: Exception handling when target analysis dictionary missing expected keys
- **IMPROVED**: Enhanced error handling with safe dictionary access using `.get()` method
- **MAINTAINED**: All existing functionality preserved - pure stability fix
- **TESTED**: Verified fix works across all notebook platforms (Colab, JupyterLab, VS Code)

### v0.12.30 (2025-01-05) - Universal Display Optimization Breakthrough 🎨
- **BREAKTHROUGH**: Introduced `optimize_display()` function for universal notebook compatibility
- **REVOLUTIONARY**: Automatic platform detection (Google Colab, JupyterLab, VS Code Notebooks, Classic Jupyter)
- **ENHANCED**: Dynamic CSS injection for perfect dark/light mode visibility across all platforms
- **NEW FEATURE**: Automatic matplotlib backend optimization for each notebook environment  
- **ACCESSIBILITY**: Solves visibility issues in dark mode themes universally
- **SEAMLESS**: Zero configuration required - automatically detects and optimizes for your platform
- **COMPATIBILITY**: Works flawlessly across Google Colab, JupyterLab, VS Code, Classic Jupyter
- **EXAMPLE**: Simple usage: `from edaflow import optimize_display; optimize_display()`

### v0.12.3 (2025-08-06) - Complete Positional Argument Compatibility Fix 🔧
- **CRITICAL**: Fixed positional argument usage for `visualize_image_classes()` function  
- **RESOLVED**: TypeError when calling `visualize_image_classes(image_paths, ...)` with positional arguments
- **ENHANCED**: Comprehensive backward compatibility supporting all three usage patterns:
  - Positional: `visualize_image_classes(path, ...)` (shows warning)
  - Deprecated keyword: `visualize_image_classes(image_paths=path, ...)` (shows warning)
  - Recommended: `visualize_image_classes(data_source=path, ...)` (no warning)
- **IMPROVED**: Clear deprecation warnings guiding users toward recommended syntax
- **MAINTAINED**: Full functionality identical to previous versions
- **TESTED**: Comprehensive test suite validating all compatibility scenarios

### v0.12.2 (2025-08-06) - Documentation Refresh 📚
- **IMPROVED**: Enhanced README.md with updated timestamps and current version indicators
- **FIXED**: Ensured PyPI displays the most current changelog information including v0.12.1 fixes
- **ENHANCED**: Added latest updates indicator to changelog for better visibility
- **DOCUMENTATION**: Forced PyPI cache refresh to display current version information
- **MAINTAINED**: All functionality identical to v0.12.1 - purely documentation improvements

### v0.12.1 (2025-08-06) - Backward Compatibility Patch 🔧
- **CRITICAL**: Fixed backward compatibility for `visualize_image_classes()` function
- **FIXED**: Added support for deprecated `image_paths` parameter that was causing TypeError
- **ENHANCED**: Function now accepts both `data_source` (recommended) and `image_paths` (deprecated) parameters
- **IMPROVED**: Added deprecation warning when `image_paths` is used to encourage migration to `data_source`
- **SECURE**: Prevents using both parameters simultaneously to avoid confusion
- **RESOLVED**: TypeError for users calling with `image_paths=` parameter from v0.12.0 breaking change
- **ENHANCED**: Improved error messages for parameter validation in image visualization functions
- **DOCUMENTATION**: Added comprehensive parameter documentation including deprecation notices

### v0.12.0 (2025-08-06) - Machine Learning Preprocessing Release 🤖
- **NEW**: `analyze_encoding_needs()` function for intelligent categorical encoding strategy analysis
- **NEW**: Automatic cardinality analysis for optimal encoding method selection
- **NEW**: Target correlation analysis for supervised encoding recommendations  
- **NEW**: Memory impact assessment for high-cardinality features
- **NEW**: Support for 7 different encoding strategies: One-Hot, Target, Ordinal, Binary, TF-IDF, Text, and Keep Numeric
- **NEW**: `apply_smart_encoding()` function for automated categorical variable transformation
- **NEW**: Intelligent preprocessing pipeline with automatic analysis integration
- **NEW**: Memory-efficient handling of high-cardinality categorical variables
- **NEW**: Support for scikit-learn encoders: OneHotEncoder, TargetEncoder, OrdinalEncoder
- **NEW**: TF-IDF vectorization for text features with customizable parameters
- **NEW**: Binary encoding for medium cardinality features to optimize memory usage
- **BREAKING**: Changed `visualize_image_classes()` parameter from `image_paths` to `data_source` (fixed in v0.12.1)
- **ENHANCED**: Beautiful emoji-rich output with detailed recommendations and summaries
- **ENHANCED**: Complete ML preprocessing workflow from analysis to implementation
- **ENHANCED**: Expanded edaflow from 17 to 19 comprehensive EDA and preprocessing functions

### v0.11.0 (2025-01-30) - Image Feature Analysis Release 🎨
- **NEW**: `analyze_image_features()` function for deep statistical analysis of visual features
- **NEW**: Edge density analysis using Canny, Sobel, and Laplacian edge detection methods
- **NEW**: Texture analysis with Local Binary Patterns (LBP) for pattern characterization
- **NEW**: Color histogram analysis across RGB, HSV, LAB, and grayscale color spaces
- **NEW**: Gradient magnitude and direction analysis for understanding image structure
- **NEW**: Feature ranking system to identify most discriminative features between classes
- **NEW**: Statistical comparison framework for quantifying inter-class visual differences
- **NEW**: Comprehensive visualization suite with box plots for feature distributions
- **NEW**: Automated recommendation system for feature engineering and preprocessing decisions
- **NEW**: Production-ready feature extraction with optional raw feature vector export
- **NEW**: OpenCV and scikit-image integration with graceful fallback mechanisms
- **NEW**: Support for custom analysis parameters (LBP radius, edge thresholds, color spaces)
- **ENHANCED**: Expanded edaflow from 16 to 17 comprehensive EDA functions
- **ENHANCED**: Complete computer vision EDA trinity: Visualization + Quality + Features
- **ENHANCED**: Advanced dependency handling for optimal performance with available libraries

### v0.10.0 (2025-08-05) - Image Quality Assessment Release 🔍
- **NEW**: `assess_image_quality()` function for comprehensive image dataset quality assessment
- **NEW**: Automated corruption detection for identifying unreadable or damaged images  
- **NEW**: Brightness and contrast analysis with configurable thresholds
- **NEW**: Blur detection using Laplacian variance for identifying potentially blurry images
- **NEW**: Color mode analysis to distinguish grayscale vs color images and detect mixed modes
- **NEW**: Dimension consistency analysis for detecting unusual aspect ratios and size outliers
- **NEW**: Compression artifact detection for identifying potential quality issues
- **NEW**: Statistical quality scoring system (0-100) for overall dataset health assessment
- **NEW**: Automated recommendation system for actionable dataset improvement suggestions
- **NEW**: Production-ready quality gates with customizable thresholds for ML pipelines
- **NEW**: Scalable analysis with sampling support for large datasets
- **ENHANCED**: Expanded edaflow from 15 to 16 comprehensive EDA functions
- **ENHANCED**: Extended computer vision capabilities with quality assessment workflows
- **ENHANCED**: Added scipy optimization for advanced blur detection algorithms

### v0.9.0 (2025-08-05) - Computer Vision EDA Release 🖼️
- **NEW**: `visualize_image_classes()` function for comprehensive image classification dataset analysis
- **NEW**: Computer Vision EDA workflow support with class-wise sample visualization
- **NEW**: Directory-based and DataFrame-based image dataset analysis capabilities
- **NEW**: Automatic class distribution analysis with imbalance detection
- **NEW**: Image quality assessment with corrupted image detection
- **NEW**: Statistical insights for image datasets (balance ratios, sample counts, warnings)
- **NEW**: Professional grid layouts for image sample visualization
- **NEW**: Comprehensive documentation for computer vision EDA workflows
- **ENHANCED**: Expanded edaflow from 14 to 15 comprehensive EDA functions
- **ENHANCED**: Added Pillow dependency for robust image processing
- **ENHANCED**: Complete computer vision integration maintaining edaflow's educational philosophy

### v0.8.6 (2025-08-05) - PyPI Changelog Display Fix
- **CRITICAL**: Fixed PyPI changelog not displaying latest releases (v0.8.4, v0.8.5)
- **DOCUMENTATION**: Updated README.md changelog section that PyPI displays instead of CHANGELOG.md
- **PYPI**: Synchronized README.md changelog with comprehensive CHANGELOG.md content
- **ENHANCED**: Ensured PyPI users see complete version history and latest features

### v0.8.5 (2025-08-05) - Code Organization and Structure Improvement Release
- **REFACTORED**: Renamed `missing_data.py` to `core.py` to better reflect comprehensive EDA functionality
- **ENHANCED**: Updated module docstring to describe complete suite of analysis functions
- **IMPROVED**: Better project structure with appropriately named core module containing all 14 EDA functions
- **FIXED**: Updated all imports and tests to reference the new core module structure
- **MAINTAINED**: Full backward compatibility - all functions work exactly the same

### v0.8.4 (2025-08-05) - Comprehensive Scatter Matrix Visualization Release
- **NEW**: `visualize_scatter_matrix()` function with advanced pairwise relationship analysis
- **NEW**: Flexible diagonal plots: histograms, KDE curves, and box plots
- **NEW**: Customizable upper/lower triangles: scatter plots, correlation coefficients, or blank
- **NEW**: Color coding by categorical variables for group-specific pattern analysis
- **NEW**: Multiple regression line types: linear, polynomial (2nd/3rd degree), and LOWESS smoothing
- **NEW**: Comprehensive statistical insights: correlation analysis, pattern identification
- **NEW**: Professional scatter matrix layouts with adaptive figure sizing
- **NEW**: Full integration with existing edaflow workflow and styling consistency
- **ENHANCED**: Complete EDA visualization suite now includes 14 functions (from 13)
- **ENHANCED**: Added scikit-learn and statsmodels dependencies for advanced analytics
- **ENHANCED**: Updated package metadata and documentation for scatter matrix capabilities

### v0.8.3 (2025-08-04) - Critical Documentation Fix Release
- **CRITICAL**: Updated README.md changelog section that PyPI was displaying instead of CHANGELOG.md
- **PYPI**: Fixed PyPI changelog display by synchronizing README.md changelog with main CHANGELOG.md
- **DOCUMENTATION**: Ensured consistent changelog information across all package files

### v0.8.2 (2025-08-04) - Metadata Enhancement Release
- **METADATA**: Enhanced PyPI metadata to ensure proper changelog display
- **PYPI**: Forced PyPI cache refresh by updating package metadata
- **LINKS**: Added additional project URLs for better discoverability
- **FIXED**: Updated changelog dates and formatting for better PyPI presentation

### v0.8.1 (2025-08-04) - Changelog Formatting Release
- **FIXED**: Updated changelog dates to current date format
- **FIXED**: Removed duplicate changelog header that was causing PyPI display issues
- **ENHANCED**: Improved changelog formatting for better PyPI presentation

### v0.8.0 (2025-08-04) - Statistical Histogram Analysis Release
- **NEW**: `visualize_histograms()` function with advanced statistical analysis and skewness detection
- **NEW**: Comprehensive distribution analysis with normality testing (Shapiro-Wilk, Jarque-Bera, Anderson-Darling)
- **NEW**: Advanced skewness interpretation: Normal (|skew| < 0.5), Moderate (0.5-1), High (≥1)
- **NEW**: Kurtosis analysis: Normal, Heavy-tailed (leptokurtic), Light-tailed (platykurtic)
- **NEW**: KDE curve overlays and normal distribution comparisons
- **NEW**: Statistical text boxes with comprehensive distribution metrics
- **NEW**: Transformation recommendations based on skewness analysis
- **NEW**: Multi-column histogram visualization with automatic subplot layout
- **ENHANCED**: Updated Complete EDA Workflow to include 12 functions (from 9)
- **ENHANCED**: Added histogram analysis as Step 10 in the comprehensive workflow
- **FIXED**: Fixed Anderson-Darling test attribute error and improved statistical test error handling

### v0.7.0 (2025-08-03) - Comprehensive Heatmap Visualization Release
- **NEW**: `visualize_heatmap()` function with comprehensive heatmap visualizations
- **NEW**: Four distinct heatmap types: correlation, missing data patterns, values, and cross-tabulation
- **NEW**: Multiple correlation methods: Pearson, Spearman, and Kendall
- **NEW**: Missing data pattern visualization with threshold highlighting
- **NEW**: Data values heatmap for detailed small dataset inspection
- **NEW**: Cross-tabulation heatmaps for categorical relationship analysis
- **ENHANCED**: Complete EDA workflow with comprehensive heatmap analysis
- **ENHANCED**: Updated package features to highlight new visualization capabilities

### v0.6.0 (2025-08-02) - Interactive Boxplot Visualization Release
- **NEW**: `visualize_interactive_boxplots()` function with full Plotly Express integration
- **NEW**: Interactive boxplot visualization with hover tooltips, zoom, and pan functionality
- **NEW**: Statistical summaries with emoji-formatted output for better readability
- **NEW**: Customizable styling options (colors, dimensions, margins)
- **NEW**: Smart column selection for numerical data
- **ENHANCED**: Added plotly>=5.0.0 dependency for interactive visualizations

### v0.5.1 (Documentation Sync Release)
- **FIXED**: Updated PyPI documentation to properly showcase handle_outliers_median() function in Complete EDA Workflow Example
- **ENHANCED**: Ensured PyPI page displays the complete 9-step EDA workflow including outlier handling
- **SYNCHRONIZED**: Local documentation improvements now reflected on PyPI for better user experience

### v0.5.0 (Outlier Handling Release)
- **NEW**: `handle_outliers_median()` function for automated outlier detection and replacement
- **NEW**: Multiple outlier detection methods: IQR, Z-score, and Modified Z-score
- **NEW**: Complete outlier analysis workflow: visualize → detect → handle → verify
- **NEW**: Median-based outlier replacement for robust statistical handling
- **NEW**: Flexible column selection with automatic numerical column detection
- **NEW**: Detailed reporting showing exactly which outliers were replaced and why
- **NEW**: Safe operation mode (inplace=False by default) to preserve original data
- **NEW**: Statistical method comparison with customizable IQR multipliers
- **NEW**: Color-coded terminal output for better readability
- Enhanced testing coverage with 12 comprehensive tests
- Improved documentation with detailed usage examples

### v0.1.1 (Documentation Update)
- Updated README with improved acknowledgments
- Fixed GitHub repository URLs
- Enhanced PyPI package presentation

### v0.1.0 (Initial Release)
- Basic package structure
- Sample hello() function
- `check_null_columns()` function for missing data analysis
- Core dependencies setup
- Documentation framework

## 📋 Changelog

### [0.12.22] - 2025-08-08 (Current)
#### Fixed
- **🔧 GOOGLE COLAB COMPATIBILITY**: Fixed KeyError in `apply_smart_encoding` documentation examples
- **FIXED**: Removed hardcoded 'target' column assumption in documentation examples
- **RESOLVED**: Documentation examples now work in Google Colab, Jupyter, and all environments
- **ENHANCED**: More robust ML encoding workflow that adapts to user datasets
#### Enhanced
- **📚 CLEAN WORKFLOW**: Removed redundant print statements from documentation examples
- **MODERNIZED**: Documentation showcases rich styling without primitive print statements

### [0.12.21] - 2025-08-08
#### Fixed
- **🔧 DOCUMENTATION PARAMETER FIXES**: Corrected parameter name mismatches in `visualize_scatter_matrix` documentation
- **FIXED**: Changed `regression_line` → `regression_type` in README.md and quickstart.rst examples
- **FIXED**: Changed `diagonal_type` → `diagonal` in documentation examples
- **FIXED**: Changed `upper_triangle`/`lower_triangle` → `upper`/`lower` parameter names
- **FIXED**: Changed `color_column` → `color_by` in documentation examples
- **RESOLVED**: TypeError when using sample code from documentation

### [0.12.20] - 2025-08-08
#### Enhanced 
- **🌈 COMPREHENSIVE RICH STYLING**: Enhanced ALL major EDA functions with vibrant, professional output
- **ENHANCED MISSING DATA ANALYSIS**: `check_null_columns` with rich tables and color-coded severity levels
- **ADVANCED COLUMN CLASSIFICATION**: `display_column_types` with side-by-side rich tables and memory analysis
- **PROFESSIONAL IMPUTATION**: `impute_numerical_median` with smart formatting and completion rates
- **COMPREHENSIVE ENHANCEMENT**: Professional tables, color-coded indicators, and actionable insights

### [0.12.19] - 2025-08-08
#### Enhanced
- **🎨 RICH STYLING EXPANSION**: Enhanced `analyze_categorical_columns` and `convert_to_numeric` with professional output
- **RICH TABLES**: Beautiful formatted tables with borders, colors, and professional styling
- **SMART RECOMMENDATIONS**: Context-aware suggestions based on data characteristics
- **VISUAL INDICATORS**: Emoji-based status indicators and color-coded warnings

### [0.12.18] - 2025-08-08
#### Enhanced
- **🎨 RICH STYLING**: Enhanced `check_null_columns` with rich library formatting and color-coded output
- **PROFESSIONAL TABLES**: Beautiful table formatting with borders and styling
- **SMART INDICATORS**: Color-coded severity levels and visual status indicators

### [0.12.17] - 2025-08-08
#### Fixed
- **DOCUMENTATION**: Fixed parameter name mismatches in function examples
- **API CONSISTENCY**: Ensured documentation matches actual function signatures

### [0.12.16] - 2025-08-07
#### Enhanced
- **🎨 LAYOUT SPACING**: Eliminated overlapping rows in visualization layouts
- **SCIENTIFIC NAMES**: Enhanced spacing for long taxonomic/class names
- **PROFESSIONAL SPACING**: Improved hspace values for publication-ready visualizations

### [0.12.15] - 2025-08-07
#### Enhanced
- **📋 TRANSPARENCY**: Informative remarks when displaying subset of classes
- **SMART GUIDANCE**: Clear context about total dataset scope
- **ENHANCED UX**: Users understand curated vs complete class sets

> 📖 **Full Changelog**: For complete version history and detailed changes, see [CHANGELOG.md](https://github.com/evanlow/edaflow/blob/main/CHANGELOG.md)

## Support

If you encounter any issues or have questions, please file an issue on the [GitHub repository](https://github.com/evanlow/edaflow/issues).

## Roadmap

- [ ] Core analysis modules
- [ ] Visualization utilities
- [ ] Data preprocessing tools
- [ ] Missing data handling
- [ ] Statistical testing suite
- [ ] Interactive dashboards
- [ ] CLI interface
- [ ] Documentation website

## Acknowledgments

edaflow was developed during the AI/ML course conducted by NTUC LearningHub. I am grateful for the privilege of working alongside my coursemates from Cohort 15. A special thanks to our awesome instructor, Ms. Isha Sehgal, who not only inspired us but also instilled the data science discipline that we now possess

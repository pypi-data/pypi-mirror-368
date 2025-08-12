# edaflow Quickstart Guide

Welcome to **edaflow** - your comprehensive toolkit for exploratory data analysis and machine learning workflows!

## 🚀 Installation

```bash
pip install edaflow
```

## 📊 Quick EDA Workflow

```python
import pandas as pd
import edaflow as eda

# Load your data
df = pd.read_csv('your_data.csv')

# 1. Check for missing data
eda.check_null_columns(df)

# 2. Analyze categorical columns
eda.analyze_categorical_columns(df)

# 3. Visualize data distribution
eda.visualize_numerical_distribution(df)

# 4. Create correlation heatmap
eda.visualize_correlation_heatmap(df)

# 5. Get EDA insights summary
eda.summarize_eda_insights(df)
```

## 🤖 Complete ML Workflow (NEW in v0.13.0)

```python
import edaflow.ml as ml
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

# 1. Setup ML experiment with automatic data splitting
experiment = ml.setup_ml_experiment(df, target_column='target')

# 2. Compare multiple models
models = {
    'RandomForest': RandomForestClassifier(random_state=42),
    'GradientBoosting': GradientBoostingClassifier(random_state=42),
    'LogisticRegression': LogisticRegression(random_state=42)
}

# Train and compare models
comparison = ml.compare_models(models, **experiment)
print(comparison)

# 3. Hyperparameter optimization
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 7],
    'min_samples_split': [2, 5, 10]
}

best_results = ml.optimize_hyperparameters(
    RandomForestClassifier(random_state=42),
    param_distributions=param_grid,
    **experiment,
    method='grid',
    cv=5
)

print(f"Best score: {best_results['best_score']:.4f}")
print(f"Best parameters: {best_results['best_params']}")

# 4. Generate performance visualizations
# Learning curves
ml.plot_learning_curves(best_results['best_model'], **experiment)

# ROC curves for classification
ml.plot_roc_curves(best_results['best_model'], **experiment)

# Feature importance
ml.plot_feature_importance(best_results['best_model'], **experiment)

# 5. Save complete model artifacts
ml.save_model_artifacts(
    model=best_results['best_model'],
    model_name='optimized_rf_model',
    experiment_config=experiment,
    performance_metrics={
        'best_score': best_results['best_score'],
        'cv_scores': best_results['cv_results']['mean_test_score']
    }
)
```

## 📈 Advanced ML Features

### Model Leaderboard
```python
# Rank models by performance
rankings = ml.rank_models(comparison)
ml.display_leaderboard(rankings)

# Export results
ml.export_model_comparison(comparison, filename='model_comparison.csv')
```

### Validation Curves
```python
# Analyze hyperparameter impact
ml.plot_validation_curves(
    RandomForestClassifier(random_state=42),
    X_train=experiment['X_train'],
    y_train=experiment['y_train'],
    param_name='n_estimators',
    param_range=[10, 50, 100, 200, 500]
)
```

### Bayesian Optimization
```python
# Advanced hyperparameter optimization (requires scikit-optimize)
param_space = {
    'n_estimators': (50, 500),
    'max_depth': (3, 20),
    'min_samples_split': (2, 20)
}

bayesian_results = ml.bayesian_optimization(
    RandomForestClassifier(random_state=42),
    param_space=param_space,
    **experiment,
    n_calls=50
)
```

## 🔍 Computer Vision EDA

```python
# For image classification datasets
eda.visualize_image_classes(image_dir='path/to/images')
eda.assess_image_quality(image_dir='path/to/images')
eda.analyze_image_features(image_dir='path/to/images')
```

## 📊 Advanced Visualizations

### Interactive Plotly Visualizations
```python
# Interactive boxplots
eda.create_interactive_boxplot(df, x_column='category', y_column='value')

# Scatter matrix analysis
eda.visualize_scatter_matrix(df, columns=['col1', 'col2', 'col3'])
```

### Statistical Analysis
```python
# Comprehensive histogram analysis
eda.visualize_statistical_histograms(df)

# Outlier analysis
eda.handle_outliers(df, method='iqr')
```

## 🛠️ Data Preprocessing

```python
# Smart encoding for ML
df_encoded = eda.apply_encoding(df)

# Or get encoders for later use
df_encoded, encoders = eda.apply_encoding_with_encoders(df)

# Impute missing values
df_imputed = eda.impute_numerical_median(df)
```

## 💾 Experiment Tracking

```python
# Track ML experiments
experiment_id = ml.track_experiment({
    'model_type': 'RandomForest',
    'dataset_size': len(df),
    'features': list(df.columns),
    'target': 'target',
    'cv_score': 0.85
})

# Generate comprehensive report
report = ml.create_model_report(
    model=best_results['best_model'],
    experiment_data=experiment,
    performance_metrics=best_results['cv_results']
)
```

## 🎯 Best Practices

### 1. Complete Workflow
```python
# Start with EDA
eda.check_null_columns(df)
eda.analyze_categorical_columns(df)

# Move to preprocessing
df_clean = eda.apply_encoding(df)

# Then ML workflow
experiment = ml.setup_ml_experiment(df_clean, 'target')
results = ml.optimize_hyperparameters(model, params, **experiment)
ml.save_model_artifacts(results['best_model'], 'final_model', experiment, results['cv_results'])
```

### 2. Model Comparison Pipeline
```python
models = {
    'RF': RandomForestClassifier(random_state=42),
    'GB': GradientBoostingClassifier(random_state=42),
    'LR': LogisticRegression(random_state=42)
}

# Compare all models
comparison = ml.compare_models(models, **experiment)

# Pick the best performer for optimization
best_model_name = comparison.loc[comparison['roc_auc_mean'].idxmax(), 'model']
best_model = models[best_model_name]

# Optimize the best model
optimized = ml.optimize_hyperparameters(best_model, param_grid, **experiment)
```

## 📚 Next Steps & Learning Resources

### 🎓 **Comprehensive Learning Guides**
- **[EDA Learning Guide](EDA_LEARNING_GUIDE.md)** - Deep dive into EDA theory and concepts with edaflow examples
- **[ML Learning Guide](ML_LEARNING_GUIDE.md)** - Complete machine learning from basics to production deployment
- **[Educational Integration Guide](EDUCATIONAL_INTEGRATION.md)** - How learning resources work together

### 📖 **Official Documentation**
- **[API Documentation](https://edaflow.readthedocs.io)** - Complete function reference
- **[User Guide](https://edaflow.readthedocs.io/en/latest/user_guide/index.html)** - Advanced usage patterns
- **[Examples Collection](https://edaflow.readthedocs.io/en/latest/examples/index.html)** - Real-world applications

### 🚀 **GitHub Repository**
- **[Source Code](https://github.com/evanlow/edaflow)** - Contribute and explore implementation
- **[Issues & Support](https://github.com/evanlow/edaflow/issues)** - Get help and report bugs
- **[Latest Releases](https://github.com/evanlow/edaflow/releases)** - Version history and updates

## 🎉 Happy Data Science!

edaflow v0.13.0 provides everything you need for comprehensive data analysis and machine learning workflows. From initial data exploration to final model deployment, edaflow streamlines your data science process with professional visualizations and powerful ML capabilities.

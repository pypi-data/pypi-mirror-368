#!/usr/bin/env python3
"""
Test Bayesian optimization with newly installed scikit-optimize
"""

from edaflow import ml
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
import pandas as pd

print("🔬 Testing Bayesian optimization with scikit-optimize...")

# Create test data
X, y = make_classification(n_samples=100, n_features=5, random_state=42)
df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(5)])
df['target'] = y

# Setup experiment
experiment = ml.setup_ml_experiment(df, 'target', verbose=False)

# Define parameter space for Bayesian optimization
# Use lists for parameter ranges (will be converted internally)
param_space = {
    'n_estimators': [10, 20, 30, 40, 50],
    'max_depth': [3, 4, 5, 6, 7, 8, 9, 10]
}

try:
    print("🎯 Running Bayesian optimization via optimize_hyperparameters...")
    results = ml.optimize_hyperparameters(
        RandomForestClassifier(random_state=42),
        param_distributions=param_space,
        X_train=experiment['X_train'],
        y_train=experiment['y_train'],
        method='bayesian',
        n_iter=10,
        verbose=True
    )
    print("✅ Bayesian optimization working!")
    print(f"🏆 Best score: {results['best_score']:.4f}")
    print(f"🎯 Best params: {results['best_params']}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("🎉 Testing complete!")

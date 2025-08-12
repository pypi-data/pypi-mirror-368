"""
Test script for the new edaflow.ml subpackage

This script demonstrates the basic functionality of the new ML subpackage
and verifies that all modules can be imported correctly.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
import sys
sys.path.insert(0, '.')

def test_ml_subpackage():
    """Test the new ML subpackage functionality."""
    
    print("🧪 Testing edaflow.ml subpackage...")
    
    # Test imports
    try:
        import edaflow
        from edaflow import ml
        print("✅ Successfully imported edaflow and ml subpackage")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Create sample dataset
    print("\n📊 Creating sample dataset...")
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=10,
        n_redundant=10,
        n_classes=2,
        random_state=42
    )
    
    # Convert to DataFrame
    feature_names = [f'feature_{i}' for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    
    print(f"✅ Dataset created: {df.shape}")
    
    # Test ML configuration
    print("\n🔧 Testing ML experiment setup...")
    try:
        experiment_data = ml.setup_ml_experiment(
            data=df,
            target_column='target',
            test_size=0.2,
            validation_size=0.2,
            verbose=True
        )
        print("✅ ML experiment setup successful")
    except Exception as e:
        print(f"❌ ML setup failed: {e}")
        return
    
    # Test model comparison
    print("\n🏆 Testing model comparison...")
    try:
        # Create models
        models = {
            'RandomForest': RandomForestClassifier(n_estimators=10, random_state=42),
            'LogisticRegression': LogisticRegression(random_state=42)
        }
        
        # Fit models
        for name, model in models.items():
            model.fit(experiment_data['X_train'], experiment_data['y_train'])
        
        # Compare models
        comparison_results = ml.compare_models(
            models=models,
            X_train=experiment_data['X_train'],
            X_val=experiment_data['X_val'],
            y_train=experiment_data['y_train'],
            y_val=experiment_data['y_val'],
            verbose=True
        )
        
        print("✅ Model comparison successful")
        print(f"📊 Comparison results shape: {comparison_results.shape}")
        
    except Exception as e:
        print(f"❌ Model comparison failed: {e}")
        return
    
    # Test hyperparameter optimization
    print("\n🔍 Testing hyperparameter optimization...")
    try:
        param_distributions = {
            'n_estimators': [10, 20, 50],
            'max_depth': [3, 5, 7]
        }
        
        optimization_results = ml.optimize_hyperparameters(
            model=RandomForestClassifier(random_state=42),
            param_distributions=param_distributions,
            X_train=experiment_data['X_train'],
            y_train=experiment_data['y_train'],
            method='grid',
            cv=3,
            verbose=True
        )
        
        print("✅ Hyperparameter optimization successful")
        print(f"🏆 Best score: {optimization_results['best_score']:.4f}")
        
    except Exception as e:
        print(f"❌ Hyperparameter optimization failed: {e}")
    
    # Test data validation
    print("\n🔍 Testing data validation...")
    try:
        validation_results = ml.validate_ml_data(
            experiment_data=experiment_data,
            verbose=True
        )
        print("✅ Data validation successful")
        print(f"📊 Quality score: {validation_results['quality_score']:.1f}/100")
        
    except Exception as e:
        print(f"❌ Data validation failed: {e}")
    
    print("\n🎉 All ML subpackage tests completed!")
    return True


if __name__ == "__main__":
    test_ml_subpackage()

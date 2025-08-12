#!/usr/bin/env python3
"""
Test script for the new summarize_eda_insights function
This demonstrates comprehensive EDA workflow completion detection and intelligent recommendations.
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the package to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

try:
    import edaflow
    print(f"✅ Successfully imported edaflow version {edaflow.__version__}")
except ImportError as e:
    print(f"❌ Failed to import edaflow: {e}")
    sys.exit(1)

def create_sample_healthcare_data():
    """Create a realistic healthcare dataset with class imbalance for testing."""
    np.random.seed(42)
    
    # Create imbalanced dataset (kidney disease prediction)
    n_samples = 1000
    
    # Majority class (no kidney disease) - 85%
    majority_size = int(n_samples * 0.85)
    
    # Minority class (kidney disease) - 15%
    minority_size = n_samples - majority_size
    
    # Generate features for majority class (healthier patients)
    majority_data = {
        'age': np.random.normal(45, 15, majority_size).astype(int),
        'bp': np.random.normal(75, 10, majority_size),  # blood pressure
        'sg': np.random.normal(1.020, 0.005, majority_size),  # specific gravity
        'al': np.random.choice([0, 1, 2], majority_size, p=[0.8, 0.15, 0.05]),  # albumin
        'su': np.random.choice([0, 1, 2], majority_size, p=[0.9, 0.08, 0.02]),  # sugar
        'bgr': np.random.normal(120, 20, majority_size),  # blood glucose random
        'bu': np.random.normal(25, 8, majority_size),  # blood urea
        'sc': np.random.normal(1.0, 0.3, majority_size),  # serum creatinine
        'sod': np.random.normal(140, 8, majority_size),  # sodium
        'pot': np.random.normal(4.2, 0.5, majority_size),  # potassium
        'hemo': np.random.normal(14, 2, majority_size),  # hemoglobin
        'classification': ['ckd'] * majority_size  # no kidney disease
    }
    
    # Generate features for minority class (kidney disease patients)
    minority_data = {
        'age': np.random.normal(55, 18, minority_size).astype(int),
        'bp': np.random.normal(95, 15, minority_size),  # higher blood pressure
        'sg': np.random.normal(1.015, 0.008, minority_size),  # lower specific gravity
        'al': np.random.choice([0, 1, 2, 3, 4], minority_size, p=[0.3, 0.2, 0.2, 0.2, 0.1]),  # more albumin
        'su': np.random.choice([0, 1, 2, 3, 4], minority_size, p=[0.4, 0.2, 0.2, 0.1, 0.1]),  # more sugar
        'bgr': np.random.normal(180, 40, minority_size),  # higher glucose
        'bu': np.random.normal(45, 15, minority_size),  # higher blood urea
        'sc': np.random.normal(2.5, 1.2, minority_size),  # higher creatinine
        'sod': np.random.normal(135, 10, minority_size),  # lower sodium
        'pot': np.random.normal(4.8, 0.8, minority_size),  # higher potassium
        'hemo': np.random.normal(11, 3, minority_size),  # lower hemoglobin
        'classification': ['notckd'] * minority_size  # kidney disease
    }
    
    # Combine datasets
    combined_data = {}
    for key in majority_data.keys():
        combined_data[key] = np.concatenate([majority_data[key], minority_data[key]])
    
    # Add some categorical features
    combined_data['rbc'] = np.random.choice(['normal', 'abnormal'], n_samples, p=[0.7, 0.3])
    combined_data['pc'] = np.random.choice(['normal', 'abnormal'], n_samples, p=[0.6, 0.4])
    combined_data['pcc'] = np.random.choice(['present', 'notpresent'], n_samples, p=[0.3, 0.7])
    combined_data['ba'] = np.random.choice(['present', 'notpresent'], n_samples, p=[0.2, 0.8])
    combined_data['hypertension'] = np.random.choice(['yes', 'no'], n_samples, p=[0.4, 0.6])
    combined_data['dm'] = np.random.choice(['yes', 'no'], n_samples, p=[0.3, 0.7])  # diabetes mellitus
    combined_data['cad'] = np.random.choice(['yes', 'no'], n_samples, p=[0.25, 0.75])  # coronary artery disease
    
    # Create DataFrame
    df = pd.DataFrame(combined_data)
    
    # Introduce some missing values strategically
    missing_indices = np.random.choice(df.index, size=int(0.05 * len(df)), replace=False)
    missing_columns = ['bp', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo']
    
    for idx in missing_indices:
        col = np.random.choice(missing_columns)
        df.loc[idx, col] = np.nan
    
    # Add some duplicates
    duplicate_indices = np.random.choice(df.index, size=15, replace=False)
    df = pd.concat([df, df.loc[duplicate_indices]], ignore_index=True)
    
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return df

def test_comprehensive_eda_insights():
    """Test the comprehensive EDA insights function with realistic healthcare data."""
    
    print("🧪 Creating sample healthcare dataset...")
    df = create_sample_healthcare_data()
    
    print(f"📊 Dataset created: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"🎯 Target column: 'classification' with classes: {df['classification'].value_counts().to_dict()}")
    print()
    
    # Simulate a typical EDA workflow 
    print("🔬 Simulating comprehensive EDA workflow...")
    
    # List of functions that might be used in a complete EDA workflow
    simulated_eda_functions = [
        'check_null_columns',
        'display_column_types', 
        'analyze_categorical_columns',
        'convert_to_numeric',
        'visualize_histograms',
        'visualize_numerical_boxplots',
        'handle_outliers_median',
        'visualize_heatmap',
        'impute_numerical_median',
        'analyze_encoding_needs'
    ]
    
    print(f"📝 Functions used in workflow: {len(simulated_eda_functions)}")
    for i, func in enumerate(simulated_eda_functions, 1):
        print(f"   {i:2d}. {func}")
    print()
    
    # Test the comprehensive insights function
    print("🔍 Generating comprehensive EDA insights...")
    print("=" * 80)
    
    # Call the new summarize_eda_insights function
    insights = edaflow.summarize_eda_insights(
        df=df,
        target_column='classification',
        eda_functions_used=simulated_eda_functions,
        class_threshold=0.2  # 20% threshold for class imbalance
    )
    
    print("=" * 80)
    
    # Test without function tracking
    print("🔍 Testing insights without function tracking...")
    print("-" * 60)
    
    insights_simple = edaflow.summarize_eda_insights(
        df=df,
        target_column='classification'
    )
    
    print("-" * 60)
    
    # Display key insights programmatically
    print("\n📋 KEY INSIGHTS SUMMARY:")
    print(f"   • Dataset Size: {insights['dataset_overview']['shape']}")
    print(f"   • Memory Usage: {insights['dataset_overview']['memory_usage']}")
    print(f"   • Data Completeness: {insights['data_quality']['data_completeness']:.1f}%")
    print(f"   • Missing Values: {insights['data_quality']['total_missing_values']} ({insights['data_quality']['missing_percentage']:.1f}%)")
    print(f"   • Duplicate Rows: {insights['data_quality']['duplicate_rows']} ({insights['data_quality']['duplicate_percentage']:.1f}%)")
    print(f"   • Feature Mix: {insights['feature_analysis']['feature_ratio']}")
    
    if 'target_analysis' in insights and insights['target_analysis']['type'] == 'classification':
        target_info = insights['target_analysis']
        print(f"   • Target Classes: {target_info['unique_classes']}")
        print(f"   • Class Imbalance: {'🔴 YES' if target_info['class_imbalance']['is_imbalanced'] else '🟢 NO'}")
        if target_info['class_imbalance']['is_imbalanced']:
            print(f"     - Imbalance Ratio: {target_info['class_imbalance']['imbalance_ratio']:.1f}:1")
            print(f"     - Underrepresented: {', '.join(target_info['class_imbalance']['underrepresented_classes'])}")
    
    print(f"   • EDA Completeness: {insights['workflow_completeness']['completeness_percentage']:.1f}%")
    print(f"   • Recommendations: {len(insights['recommendations'])} actionable items")
    
    print("\n🎯 RECOMMENDATIONS:")
    for i, rec in enumerate(insights['recommendations'], 1):
        priority_icon = "🔴" if rec['priority'] == 'High' else "🟡" if rec['priority'] == 'Medium' else "🟢"
        print(f"   {i}. {priority_icon} [{rec['priority']}] {rec['category']}")
        print(f"      Issue: {rec['issue']}")
        print(f"      Action: {rec['action']}")
        print(f"      Functions: {', '.join(rec['functions'][:2])}")
        print()
    
    print("✅ Test completed successfully!")
    return insights

def test_regression_target():
    """Test with regression target."""
    print("\n🧪 Testing with regression target...")
    
    # Create sample regression dataset
    np.random.seed(42)
    n_samples = 500
    
    df_reg = pd.DataFrame({
        'feature1': np.random.normal(10, 3, n_samples),
        'feature2': np.random.uniform(0, 100, n_samples),
        'feature3': np.random.exponential(2, n_samples),
        'category': np.random.choice(['A', 'B', 'C'], n_samples, p=[0.5, 0.3, 0.2]),
        'target_price': np.random.normal(50000, 15000, n_samples)  # Regression target
    })
    
    # Add some missing values
    missing_idx = np.random.choice(df_reg.index, size=25, replace=False)
    df_reg.loc[missing_idx, 'feature1'] = np.nan
    
    print("🔍 Regression insights:")
    print("-" * 40)
    
    insights_reg = edaflow.summarize_eda_insights(
        df=df_reg,
        target_column='target_price',
        eda_functions_used=['check_null_columns', 'visualize_histograms']
    )
    
    print("-" * 40)
    return insights_reg

if __name__ == "__main__":
    print("🚀 Testing edaflow's new summarize_eda_insights function")
    print("=" * 80)
    
    try:
        # Test with classification target (main test)
        classification_insights = test_comprehensive_eda_insights()
        
        # Test with regression target
        regression_insights = test_regression_target()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("The summarize_eda_insights function is working perfectly!")
        print("\n💡 Usage Examples:")
        print("   # After your EDA workflow:")
        print("   insights = edaflow.summarize_eda_insights(df, target_column='your_target')")
        print("   ")
        print("   # With function tracking:")
        print("   functions_used = ['check_null_columns', 'visualize_histograms', ...]")
        print("   insights = edaflow.summarize_eda_insights(df, 'target', functions_used)")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Clean EDA Workflow Demonstration
================================

This script demonstrates the modern, clean edaflow workflow without redundant 
print statements. The functions themselves provide beautiful, rich-styled output
with color-coded indicators and professional formatting.

All major EDA functions now feature:
- ✅ Professional rich styling with color-coded severity levels
- 🎨 Beautiful tables with borders and proper formatting  
- 💡 Smart recommendations and actionable insights
- 📊 Visual indicators replacing primitive text output
"""

import pandas as pd
import numpy as np
import edaflow

def create_sample_dataset():
    """Create a realistic sample dataset for demonstration."""
    np.random.seed(42)
    
    n_samples = 500
    df = pd.DataFrame({
        # Numerical with missing values and outliers
        'age': np.random.normal(35, 10, n_samples),
        'salary': np.random.lognormal(10, 0.8, n_samples),
        'experience': np.random.gamma(2, 2, n_samples),
        
        # Categorical with some data issues
        'department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'HR', 'Finance'], n_samples),
        'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),
        'location': np.random.choice(['NYC', 'SF', 'Chicago', 'Remote', 'Austin'], n_samples),
        
        # Mixed type column that should be numeric
        'rating': np.random.choice(['4.2', '3.8', '4.5', '3.9', '4.1', 'N/A'], n_samples),
        
        # Some completely numeric columns stored as strings
        'years_company': [str(int(x)) if np.random.random() > 0.1 else str(x) 
                         for x in np.random.poisson(3, n_samples)],
    })
    
    # Introduce missing values
    missing_indices = np.random.choice(n_samples, int(0.1 * n_samples), replace=False)
    df.loc[missing_indices[:50], 'age'] = np.nan
    df.loc[missing_indices[50:80], 'salary'] = np.nan
    df.loc[missing_indices[80:], 'department'] = np.nan
    
    # Add some extreme outliers
    df.loc[10, 'salary'] = 1000000  # Extreme salary outlier
    df.loc[15, 'age'] = 120         # Extreme age outlier
    
    return df

def demonstrate_clean_workflow():
    """Demonstrate the complete, clean EDA workflow."""
    
    print("🎯 EDA WORKFLOW DEMONSTRATION")
    print("=" * 50)
    print("Creating sample dataset...")
    
    # Create sample data
    df = create_sample_dataset()
    print(f"Dataset created: {df.shape}")
    
    print("\n" + "="*50)
    print("🚀 CLEAN EDA WORKFLOW - Rich Styled Output")
    print("="*50)
    
    # Step 1: Missing Data Analysis (with beautiful rich styling)
    print("\n📋 Step 1: Missing Data Analysis")
    null_analysis = edaflow.check_null_columns(df, threshold=15)
    # The function displays beautiful color-coded output automatically!
    
    # Step 2: Categorical Data Insights (rich tables)  
    print("\n📊 Step 2: Categorical Data Analysis")
    edaflow.analyze_categorical_columns(df, threshold=30)
    # Professional tables with recommendations!
    
    # Step 3: Smart Data Type Conversion (with progress indicators)
    print("\n🔄 Step 3: Smart Data Type Conversion")
    df_cleaned = edaflow.convert_to_numeric(df, threshold=30)
    # Dynamic conversion tables with visual progress!
    
    # Step 4: Column Type Classification (side-by-side rich tables)
    print("\n🏷️  Step 4: Column Type Classification")
    column_types = edaflow.display_column_types(df_cleaned)
    # Side-by-side tables with memory analysis!
    
    # Step 5: Data Imputation (professional imputation reporting)
    print("\n🔧 Step 5: Missing Value Imputation")
    df_numeric_imputed = edaflow.impute_numerical_median(df_cleaned)
    df_fully_imputed = edaflow.impute_categorical_mode(df_numeric_imputed)
    # Smart value formatting and completion rates!
    
    # Step 6: Visualization & Relationship Analysis
    print("\n📈 Step 6: Advanced Visualizations")
    edaflow.visualize_numerical_boxplots(
        df_fully_imputed,
        title="Distribution Analysis - Outlier Detection",
        show_skewness=True
    )
    
    # Step 7: Scatter Matrix Analysis 
    print("\n🎯 Step 7: Relationship Analysis")
    edaflow.visualize_scatter_matrix(
        df_fully_imputed,
        regression_type='linear',
        title="Pairwise Relationships"
    )
    
    # Step 8: Heatmap Analysis
    print("\n🌡️  Step 8: Correlation Analysis")
    edaflow.visualize_heatmap(
        df_fully_imputed,
        heatmap_type='correlation',
        title="Feature Correlations"
    )
    
    print("\n" + "="*50)
    print("✅ WORKFLOW COMPLETE!")
    print("="*50)
    print("🌈 All functions provided rich, professional output")
    print("📊 Color-coded indicators and beautiful formatting")
    print("💡 Smart recommendations and actionable insights")
    print("🎨 No manual print statements needed!")
    
    return df_fully_imputed

if __name__ == "__main__":
    # Run the demonstration
    final_df = demonstrate_clean_workflow()
    
    print(f"\n📋 Final dataset shape: {final_df.shape}")
    print("🎉 Ready for advanced analysis or machine learning!")
    print("\n💫 The rich styling makes EDA beautiful and professional!")

#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import edaflow

# Create a realistic test dataset
df = pd.DataFrame({
    'age': [25, 30, 35, 40, 45, 28, 32, 38, 42, 100],  # 100 is an outlier
    'salary': [50000, 60000, 75000, 80000, 90000, 55000, 65000, 70000, 85000, 250000],  # 250000 is an outlier
    'experience': [2, 5, 8, 12, 15, 3, 6, 9, 13, 30],  # 30 might be an outlier
    'score': [85, 92, 78, 88, 95, 82, 89, 91, 86, 20],  # 20 is an outlier
    'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C']  # Non-numerical
})

print("Test Dataset:")
print(df)
print(f"\nDataFrame shape: {df.shape}")
print(f"Numerical columns: {df.select_dtypes(include=[np.number]).columns.tolist()}")
print()

# Test the boxplot function
try:
    print("=== Testing basic boxplot functionality ===")
    edaflow.visualize_numerical_boxplots(
        df, 
        title="Employee Data Analysis - Outlier Detection",
        show_skewness=True
    )
    print("✓ Basic boxplot test completed successfully!\n")
    
    print("=== Testing custom parameters ===")
    edaflow.visualize_numerical_boxplots(
        df, 
        columns=['age', 'salary'],
        rows=1, 
        cols=2,
        title="Age vs Salary Analysis",
        orientation='vertical',
        show_skewness=False,
        color_palette='viridis'
    )
    print("✓ Custom parameters test completed successfully!\n")
    
    print("✅ All tests passed! The visualize_numerical_boxplots function is working correctly.")
    
except Exception as e:
    print(f"❌ Error occurred: {e}")
    import traceback
    traceback.print_exc()

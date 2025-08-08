#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys
import os

# Add the current directory to the path so we can import edaflow
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

try:
    import edaflow
    print("✓ Successfully imported edaflow")
    
    # Create test data
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 100, 28, 32, 45],  # 100 is an outlier
        'salary': [50000, 60000, 75000, 80000, 200000, 55000, 65000, 70000],  # 200000 is an outlier
        'experience': [2, 5, 8, 12, 25, 3, 6, 10],
        'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B']  # Non-numerical
    })
    
    print("✓ Created test DataFrame")
    print(f"DataFrame shape: {df.shape}")
    print(f"Numerical columns: {df.select_dtypes(include=[np.number]).columns.tolist()}")
    
    # Test the function - redirect matplotlib output
    import matplotlib.pyplot as plt
    
    # Mock plt.show to prevent display during testing
    original_show = plt.show
    plt.show = lambda: None
    
    try:
        edaflow.visualize_numerical_boxplots(df, title='Test Boxplots', show_skewness=True)
        print("✓ visualize_numerical_boxplots executed successfully!")
    except Exception as e:
        print(f"✗ Error in visualize_numerical_boxplots: {e}")
        import traceback
        traceback.print_exc()
    finally:
        plt.show = original_show
        
except Exception as e:
    print(f"✗ Error importing or running: {e}")
    import traceback
    traceback.print_exc()

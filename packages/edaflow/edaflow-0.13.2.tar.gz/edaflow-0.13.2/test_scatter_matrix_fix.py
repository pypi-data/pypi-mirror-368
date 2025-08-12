#!/usr/bin/env python3
"""
Test script to reproduce and fix the AttributeError in visualize_scatter_matrix
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the current directory to the path so we can import edaflow
sys.path.insert(0, os.path.abspath('.'))

import edaflow

def test_scatter_matrix_with_tuple():
    """Test that passing a tuple raises a proper error message"""
    print("🧪 Testing visualize_scatter_matrix with tuple input...")
    
    # Create a sample tuple (this is what was causing the error)
    test_tuple = (1, 2, 3, 4, 5)
    
    try:
        edaflow.visualize_scatter_matrix(test_tuple)
        print("❌ ERROR: Function should have raised TypeError but didn't!")
        return False
    except TypeError as e:
        print(f"✅ SUCCESS: Proper TypeError raised: {str(e)}")
        return True
    except Exception as e:
        print(f"❌ ERROR: Wrong exception type raised: {type(e).__name__}: {str(e)}")
        return False

def test_scatter_matrix_with_dataframe():
    """Test that passing a DataFrame works correctly"""
    print("\n🧪 Testing visualize_scatter_matrix with DataFrame input...")
    
    # Create a sample DataFrame
    np.random.seed(42)
    data = {
        'feature1': np.random.normal(0, 1, 100),
        'feature2': np.random.normal(1, 1.5, 100),
        'feature3': np.random.normal(-1, 0.5, 100),
    }
    df = pd.DataFrame(data)
    
    try:
        # This should work without errors
        edaflow.visualize_scatter_matrix(df, figsize=(8, 6))
        print("✅ SUCCESS: Function executed with DataFrame input!")
        return True
    except Exception as e:
        print(f"❌ ERROR: Function failed with DataFrame: {type(e).__name__}: {str(e)}")
        return False

def test_scatter_matrix_with_empty_dataframe():
    """Test that passing an empty DataFrame raises proper error"""
    print("\n🧪 Testing visualize_scatter_matrix with empty DataFrame...")
    
    # Create an empty DataFrame
    empty_df = pd.DataFrame()
    
    try:
        edaflow.visualize_scatter_matrix(empty_df)
        print("❌ ERROR: Function should have raised ValueError but didn't!")
        return False
    except ValueError as e:
        print(f"✅ SUCCESS: Proper ValueError raised: {str(e)}")
        return True
    except Exception as e:
        print(f"❌ ERROR: Wrong exception type raised: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing edaflow v0.12.31 - Scatter Matrix Fix")
    print("=" * 50)
    
    # Run tests
    test_results = [
        test_scatter_matrix_with_tuple(),
        test_scatter_matrix_with_dataframe(),
        test_scatter_matrix_with_empty_dataframe()
    ]
    
    print("\n" + "=" * 50)
    success_count = sum(test_results)
    total_tests = len(test_results)
    
    if success_count == total_tests:
        print(f"🎉 ALL TESTS PASSED ({success_count}/{total_tests})")
        print("✅ The AttributeError fix is working correctly!")
    else:
        print(f"⚠️  SOME TESTS FAILED ({success_count}/{total_tests})")
        print("❌ Additional fixes may be needed.")
    
    print(f"\nThis fix addresses the AttributeError: 'tuple' object has no attribute 'empty'")
    print(f"that was occurring in step 14 of the EDA workflow.")

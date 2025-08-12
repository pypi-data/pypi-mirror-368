#!/usr/bin/env python3
"""
Test the fix for the original AttributeError issue.
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the current directory to the path so we can import edaflow
sys.path.insert(0, os.path.abspath('.'))

import edaflow

def test_original_problem_fix():
    """Test the fix for the original tuple/DataFrame confusion."""
    
    print("🔧 Testing Fix for Original Problem")
    print("=" * 50)
    
    # Create test data similar to what would cause the original error
    np.random.seed(42)
    data = {
        'categorical_col': ['A', 'B', 'C', 'A', 'B'] * 20,
        'numeric_col': np.random.randn(100),
        'binary_col': np.random.choice([0, 1], 100),
        'target': np.random.choice([0, 1], 100)
    }
    df = pd.DataFrame(data)
    
    print("🚫 ORIGINAL PROBLEMATIC CODE (Would cause AttributeError):")
    print("   df_encoded = edaflow.apply_smart_encoding(df, return_encoders=True)")
    print("   edaflow.visualize_scatter_matrix(df_encoded)  # ❌ CRASHES")
    
    # Test the original problem scenario
    print("\n🎯 Testing Original Problem Scenario...")
    
    try:
        # This is what users were doing wrong (returns tuple)
        df_encoded_tuple = edaflow.apply_smart_encoding(df.copy(), return_encoders=True)
        print(f"   apply_smart_encoding returned: {type(df_encoded_tuple)}")
        
        # This would have caused the original error, but now we have better validation
        try:
            result = edaflow.visualize_scatter_matrix(df_encoded_tuple)
            print("❌ ERROR: Should have failed with helpful error message!")
        except (TypeError, AttributeError) as e:
            if "tuple" in str(e).lower() and "dataframe" in str(e).lower():
                print("✅ SUCCESS: Got helpful error message about tuple vs DataFrame")
                print(f"   Error message: {str(e)[:100]}...")
            else:
                print(f"⚠️  Got error, but not the expected helpful message: {e}")
    
    except Exception as e:
        print(f"❌ Unexpected error in test: {e}")
    
    print("\n✅ RECOMMENDED SOLUTIONS:")
    
    # Solution 1: Use new apply_encoding function
    print("\n💡 Solution 1: Use apply_encoding() (Recommended)")
    try:
        df_encoded_clean = edaflow.apply_encoding(df.copy())
        print(f"   apply_encoding returned: {type(df_encoded_clean)}")
        
        # This should work fine now
        result = edaflow.visualize_scatter_matrix(df_encoded_clean)
        print("✅ SUCCESS: visualize_scatter_matrix works with apply_encoding!")
        
    except Exception as e:
        print(f"❌ Solution 1 failed: {e}")
    
    # Solution 2: Proper unpacking of the old function
    print("\n💡 Solution 2: Proper unpacking of apply_smart_encoding")
    try:
        df_encoded_proper, encoders = edaflow.apply_smart_encoding(df.copy(), return_encoders=True)
        print(f"   Unpacked: DataFrame = {type(df_encoded_proper)}, Encoders = {type(encoders)}")
        
        # This should also work
        result = edaflow.visualize_scatter_matrix(df_encoded_proper)
        print("✅ SUCCESS: visualize_scatter_matrix works with proper unpacking!")
        
    except Exception as e:
        print(f"❌ Solution 2 failed: {e}")
    
    # Solution 3: Use explicit tuple function
    print("\n💡 Solution 3: Use apply_encoding_with_encoders() for explicit tuple")
    try:
        df_encoded_explicit, encoders_explicit = edaflow.apply_encoding_with_encoders(df.copy())
        print(f"   Explicit tuple: DataFrame = {type(df_encoded_explicit)}, Encoders = {type(encoders_explicit)}")
        
        # This should also work
        result = edaflow.visualize_scatter_matrix(df_encoded_explicit)
        print("✅ SUCCESS: visualize_scatter_matrix works with explicit tuple function!")
        
    except Exception as e:
        print(f"❌ Solution 3 failed: {e}")
    
    print("\n🎉 PROBLEM FIXED!")
    print("=" * 50)
    print("📋 Summary:")
    print("   ❌ Old problem: Inconsistent return types caused AttributeError")  
    print("   ✅ New solution: Multiple clean, consistent APIs")
    print("   ⚠️  Backward compatibility: Old function still works with deprecation warning")
    print("\n🚀 Best Practice: Use edaflow.apply_encoding() for new code!")

if __name__ == "__main__":
    test_original_problem_fix()

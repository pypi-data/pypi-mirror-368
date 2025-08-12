#!/usr/bin/env python3
"""
Test to reproduce and fix the tuple issue in apply_smart_encoding
"""

import pandas as pd
import sys
import os

# Add the local edaflow to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_tuple_issue():
    """Reproduce the tuple issue that causes AttributeError in visualize_scatter_matrix"""
    
    print("🔬 Testing apply_smart_encoding return behavior...")
    
    # Create test data
    data = {
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [2.1, 3.2, 1.5, 4.8, 2.9],
        'category': ['A', 'B', 'A', 'C', 'B'],
        'target': [0, 1, 0, 1, 1]
    }
    df = pd.DataFrame(data)
    
    # Test Case 1: return_encoders=False (should work)
    print("\n✅ Test 1: return_encoders=False")
    try:
        import edaflow
        result1 = edaflow.apply_smart_encoding(df, return_encoders=False)
        print(f"   Result type: {type(result1)}")
        print(f"   Is DataFrame: {isinstance(result1, pd.DataFrame)}")
        print("   ✅ PASS: Returns DataFrame as expected")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # Test Case 2: return_encoders=True (problematic)
    print("\n🐛 Test 2: return_encoders=True")
    try:
        result2 = edaflow.apply_smart_encoding(df, return_encoders=True)
        print(f"   Result type: {type(result2)}")
        print(f"   Is DataFrame: {isinstance(result2, pd.DataFrame)}")
        print(f"   Is tuple: {isinstance(result2, tuple)}")
        if isinstance(result2, tuple):
            print(f"   Tuple length: {len(result2)}")
            print(f"   First element type: {type(result2[0])}")
            print(f"   Second element type: {type(result2[1])}")
        print("   ❌ ISSUE: Returns tuple, not DataFrame!")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
    
    # Test Case 3: Simulate the error in visualize_scatter_matrix
    print("\n💥 Test 3: Reproducing AttributeError")
    try:
        df_encoded = edaflow.apply_smart_encoding(df, return_encoders=True)
        # This should fail with 'tuple' object has no attribute 'empty'
        if df_encoded.empty:  # This line will cause the error!
            print("DataFrame is empty")
    except AttributeError as e:
        print(f"   ✅ REPRODUCED ERROR: {e}")
        print("   This is exactly what's happening in Colab!")
    except Exception as e:
        print(f"   Other error: {e}")

if __name__ == "__main__":
    test_tuple_issue()

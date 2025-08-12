#!/usr/bin/env python3
"""
Test the fix for the tuple issue in visualization functions
"""

import pandas as pd
import sys
import os

# Add the local edaflow to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_fixed_error_handling():
    """Test that the fixed error handling provides helpful messages"""
    
    print("🧪 Testing Fixed Error Handling for Tuple Issue...")
    
    # Create test data
    data = {
        'feature1': [1.1, 2.2, 3.3, 4.4, 5.5],
        'feature2': [2.1, 3.2, 1.5, 4.8, 2.9],
        'feature3': [0.8, 1.9, 2.1, 3.7, 1.2],
        'target': [0, 1, 0, 1, 1]
    }
    df = pd.DataFrame(data)
    
    print(f"📊 Test DataFrame shape: {df.shape}")
    print(f"    Columns: {list(df.columns)}")
    
    # Test Case 1: Simulate the user error (should provide helpful error message)
    print("\n🐛 Test 1: Simulating the problematic code pattern...")
    try:
        import edaflow
        
        # This simulates what the user did wrong
        df_encoded = edaflow.apply_smart_encoding(df, return_encoders=True)  # Returns tuple
        
        # This should now give a helpful error message instead of AttributeError
        edaflow.visualize_scatter_matrix(df_encoded, title="This should fail with helpful message")
        
    except TypeError as e:
        print("✅ HELPFUL ERROR CAUGHT:")
        print(f"   {str(e)}")
        
        # Check if the error message is helpful
        error_msg = str(e)
        if "apply_smart_encoding" in error_msg and "return_encoders=True" in error_msg:
            print("✅ ERROR MESSAGE IS HELPFUL - Contains solution guidance!")
        else:
            print("❌ Error message could be more helpful")
            
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
    
    # Test Case 2: Correct usage (should work)
    print("\n✅ Test 2: Correct usage pattern...")
    try:
        # Correct pattern 1: Unpack the tuple
        df_encoded, encoders = edaflow.apply_smart_encoding(df, return_encoders=True)
        print(f"   DataFrame shape after encoding: {df_encoded.shape}")
        
        # This should work
        edaflow.visualize_scatter_matrix(df_encoded, title="Correct Usage - Unpacked Tuple")
        print("✅ SUCCESS: visualize_scatter_matrix works with unpacked tuple!")
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
    
    # Test Case 3: Alternative correct usage (should work)
    print("\n✅ Test 3: Alternative correct usage pattern...")
    try:
        # Correct pattern 2: Don't use return_encoders
        df_encoded = edaflow.apply_smart_encoding(df, return_encoders=False)
        print(f"   DataFrame shape after encoding: {df_encoded.shape}")
        
        # This should work
        edaflow.visualize_scatter_matrix(df_encoded, title="Correct Usage - No Encoders")
        print("✅ SUCCESS: visualize_scatter_matrix works with return_encoders=False!")
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_fixed_error_handling()

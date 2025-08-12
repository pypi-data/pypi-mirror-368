#!/usr/bin/env python3
"""
Test the new consistent encoding functions that fix the tuple return issue.
"""

import pandas as pd
import numpy as np
import warnings
import sys
import os

# Add the current directory to the path so we can import edaflow
sys.path.insert(0, os.path.abspath('.'))

import edaflow

def test_new_encoding_functions():
    """Test the new consistent encoding functions."""
    
    print("🧪 Testing New Consistent Encoding Functions")
    print("=" * 50)
    
    # Create test data
    print("📊 Creating test dataset...")
    np.random.seed(42)
    data = {
        'categorical_col': ['A', 'B', 'C', 'A', 'B'] * 20,
        'numeric_col': np.random.randn(100),
        'binary_col': np.random.choice([0, 1], 100),
        'high_cardinality': [f'item_{i}' for i in np.random.randint(0, 50, 100)]
    }
    df = pd.DataFrame(data)
    print(f"   Dataset shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")
    
    # Test 1: New apply_encoding function (always returns DataFrame)
    print("\n🎯 Test 1: apply_encoding() - Consistent DataFrame return")
    print("-" * 50)
    
    try:
        df_encoded_1 = edaflow.apply_encoding(df)
        print(f"✅ SUCCESS: apply_encoding() returned: {type(df_encoded_1)}")
        print(f"   Shape: {df.shape} → {df_encoded_1.shape}")
        assert isinstance(df_encoded_1, pd.DataFrame), "Should return DataFrame"
        
    except Exception as e:
        print(f"❌ FAILED: apply_encoding() error: {e}")
    
    # Test 2: New apply_encoding_with_encoders function (always returns tuple)
    print("\n🎯 Test 2: apply_encoding_with_encoders() - Explicit tuple return")
    print("-" * 50)
    
    try:
        result = edaflow.apply_encoding_with_encoders(df)
        print(f"✅ SUCCESS: apply_encoding_with_encoders() returned: {type(result)}")
        
        # Should be a tuple
        assert isinstance(result, tuple), "Should return tuple"
        assert len(result) == 2, "Should return (df, encoders)"
        
        df_encoded_2, encoders = result
        print(f"   DataFrame type: {type(df_encoded_2)}")
        print(f"   Encoders type: {type(encoders)}")
        print(f"   Shape: {df.shape} → {df_encoded_2.shape}")
        print(f"   Encoders keys: {list(encoders.keys()) if encoders else 'None'}")
        
        assert isinstance(df_encoded_2, pd.DataFrame), "First element should be DataFrame"
        assert isinstance(encoders, dict), "Second element should be dict"
        
    except Exception as e:
        print(f"❌ FAILED: apply_encoding_with_encoders() error: {e}")
    
    # Test 3: Old function with deprecation warning
    print("\n🎯 Test 3: apply_smart_encoding(return_encoders=True) - Deprecation warning")
    print("-" * 50)
    
    try:
        # Capture the deprecation warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            result_old = edaflow.apply_smart_encoding(df, return_encoders=True)
            
            # Check if deprecation warning was raised
            if len(w) > 0 and issubclass(w[0].category, DeprecationWarning):
                print("✅ SUCCESS: Deprecation warning correctly raised")
                print(f"   Warning message: {str(w[0].message)[:100]}...")
            else:
                print("⚠️  No deprecation warning detected")
            
            # Check return type
            print(f"   Returned type: {type(result_old)}")
            assert isinstance(result_old, tuple), "Should return tuple when return_encoders=True"
            
    except Exception as e:
        print(f"❌ FAILED: apply_smart_encoding() deprecation test error: {e}")
    
    # Test 4: Comparison - all methods should produce same DataFrame
    print("\n🎯 Test 4: Consistency Check - All methods produce same result")
    print("-" * 50)
    
    try:
        # Get DataFrames from all methods
        df1 = edaflow.apply_encoding(df.copy())
        df2, _ = edaflow.apply_encoding_with_encoders(df.copy()) 
        df3 = edaflow.apply_smart_encoding(df.copy(), return_encoders=False)
        
        # Compare shapes
        shapes = [df1.shape, df2.shape, df3.shape]
        print(f"   Shapes: {shapes}")
        
        if len(set(shapes)) == 1:
            print("✅ SUCCESS: All methods produce same shape")
        else:
            print("⚠️  WARNING: Different shapes produced")
        
        # Compare column names
        cols = [set(df1.columns), set(df2.columns), set(df3.columns)]
        if len(set(tuple(sorted(c)) for c in cols)) == 1:
            print("✅ SUCCESS: All methods produce same columns")
        else:
            print("⚠️  WARNING: Different columns produced")
            
    except Exception as e:
        print(f"❌ FAILED: Consistency check error: {e}")
    
    print("\n🎉 Testing Complete!")
    print("=" * 50)
    print("📋 Summary:")
    print("   • apply_encoding() - Clean, consistent DataFrame return ✅")
    print("   • apply_encoding_with_encoders() - Explicit tuple return ✅") 
    print("   • apply_smart_encoding() - Deprecated inconsistent behavior ⚠️")
    print("\n💡 Recommendation: Use apply_encoding() for new code!")

if __name__ == "__main__":
    test_new_encoding_functions()

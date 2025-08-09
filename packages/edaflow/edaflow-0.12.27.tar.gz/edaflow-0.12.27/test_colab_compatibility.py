#!/usr/bin/env python3
"""
Google Colab Compatibility Test for edaflow
===========================================

This script specifically tests the apply_smart_encoding function to ensure 
it works correctly in Google Colab without assuming specific column names
like 'target' that may not exist in user datasets.
"""

import pandas as pd
import numpy as np
import sys

def test_colab_compatibility():
    """Test edaflow functions for Google Colab compatibility."""
    
    print("🧪 GOOGLE COLAB COMPATIBILITY TEST")
    print("=" * 50)
    
    try:
        import edaflow
        print("✅ edaflow imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import edaflow: {e}")
        return False
    
    # Create test dataset without 'target' column
    np.random.seed(42)
    df = pd.DataFrame({
        'age': np.random.normal(35, 10, 100),
        'salary': np.random.lognormal(10, 0.5, 100),
        'department': np.random.choice(['Engineering', 'Sales', 'Marketing'], 100),
        'education': np.random.choice(['Bachelor', 'Master', 'PhD'], 100),
        'rating_str': np.random.choice(['4.2', '3.8', '4.5', 'N/A'], 100),
        'years_company': [str(int(x)) for x in np.random.poisson(3, 100)],
    })
    
    print(f"\n📊 Created test dataset: {df.shape}")
    print(f"📋 Columns: {list(df.columns)}")
    print("❗ Note: No 'target' column in dataset")
    
    # Test Step 1: Missing Data Analysis
    print("\n🔍 Testing missing data analysis...")
    try:
        null_analysis = edaflow.check_null_columns(df, threshold=10)
        print("✅ check_null_columns works in Colab")
    except Exception as e:
        print(f"❌ check_null_columns failed: {e}")
        return False
    
    # Test Step 2: Encoding Analysis (without target column)
    print("\n🧠 Testing encoding analysis without target column...")
    try:
        encoding_analysis = edaflow.analyze_encoding_needs(
            df,
            target_column=None,  # No target column
            max_cardinality_onehot=15
        )
        print("✅ analyze_encoding_needs works without target")
    except Exception as e:
        print(f"❌ analyze_encoding_needs failed: {e}")
        return False
    
    # Test Step 3: Apply Smart Encoding (the problematic function)
    print("\n🚀 Testing apply_smart_encoding (the main issue)...")
    try:
        # This should work without trying to drop 'target' column
        df_encoded = edaflow.apply_smart_encoding(
            df,  # Full dataset, no column dropping
            encoding_analysis=encoding_analysis,
            return_encoders=True
        )
        print("✅ apply_smart_encoding works in Colab!")
        print(f"📊 Encoded dataset shape: {df_encoded[0].shape if isinstance(df_encoded, tuple) else df_encoded.shape}")
    except KeyError as e:
        print(f"❌ KeyError in apply_smart_encoding: {e}")
        print("🔍 This is likely the 'target' column issue")
        return False
    except Exception as e:
        print(f"❌ apply_smart_encoding failed: {e}")
        return False
    
    # Test Step 4: Other core functions
    print("\n📈 Testing other core functions...")
    try:
        df_clean = edaflow.convert_to_numeric(df)
        edaflow.display_column_types(df_clean)
        print("✅ Other core functions work in Colab")
    except Exception as e:
        print(f"❌ Other functions failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL COLAB COMPATIBILITY TESTS PASSED!")
    print("=" * 50)
    print("✅ No KeyError on missing 'target' column")
    print("✅ apply_smart_encoding works with any dataset")
    print("✅ Documentation examples should work in Colab")
    print("✅ Functions handle edge cases gracefully")
    
    return True

def test_with_target_column():
    """Test that functions still work when target column is present."""
    
    print("\n🎯 TESTING WITH TARGET COLUMN PRESENT")
    print("=" * 50)
    
    try:
        import edaflow
        
        # Create dataset WITH target column
        np.random.seed(42)
        df = pd.DataFrame({
            'age': np.random.normal(35, 10, 100),
            'salary': np.random.lognormal(10, 0.5, 100),
            'department': np.random.choice(['Engineering', 'Sales', 'Marketing'], 100),
            'target': np.random.choice([0, 1], 100)  # Binary target
        })
        
        print(f"📊 Dataset with target: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Test with target column specified
        encoding_analysis = edaflow.analyze_encoding_needs(
            df,
            target_column='target',  # Now we have a target
            max_cardinality_onehot=15
        )
        
        # Test encoding with target column dropped
        features_only = df.drop('target', axis=1)
        df_encoded = edaflow.apply_smart_encoding(
            features_only,
            encoding_analysis=encoding_analysis
        )
        
        print("✅ Functions work correctly with target column present")
        print("✅ Can safely drop target when it exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed with target column: {e}")
        return False

if __name__ == "__main__":
    print("🌐 Testing edaflow compatibility with Google Colab")
    print("=" * 70)
    
    # Test without target column (main issue)
    success_1 = test_colab_compatibility()
    
    # Test with target column (to ensure we didn't break anything)
    success_2 = test_with_target_column()
    
    print("\n" + "=" * 70)
    if success_1 and success_2:
        print("🎉 ALL TESTS PASSED - COLAB COMPATIBLE!")
        print("✅ Documentation examples will now work in Google Colab")
        print("✅ Functions handle both with and without target columns")
        sys.exit(0)
    else:
        print("❌ TESTS FAILED - COMPATIBILITY ISSUES REMAIN")
        sys.exit(1)

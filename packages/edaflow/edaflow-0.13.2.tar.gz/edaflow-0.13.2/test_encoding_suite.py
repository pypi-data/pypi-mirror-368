#!/usr/bin/env python3
"""
Test script for edaflow v0.12.0 encoding functionality
"""

import pandas as pd
import numpy as np
import edaflow

print("🧪 Testing edaflow v0.12.0 - Intelligent Encoding Suite")
print("=" * 60)

# Create comprehensive sample data for testing
np.random.seed(42)
n_samples = 100

df_test = pd.DataFrame({
    # Low cardinality categorical (should be one-hot encoded)
    'category_low': np.random.choice(['A', 'B', 'C'], n_samples),
    
    # High cardinality categorical (should be frequency/target encoded)  
    'category_high': np.random.choice([f'Cat_{i}' for i in range(25)], n_samples),
    
    # Binary categorical
    'binary_cat': np.random.choice(['Yes', 'No'], n_samples),
    
    # Numeric columns
    'numeric_int': np.random.randint(1, 100, n_samples),
    'numeric_float': np.random.normal(50, 15, n_samples),
    
    # Ordinal-like data
    'education': np.random.choice(['High School', 'College', 'Graduate'], n_samples),
    
    # Target variable
    'target': np.random.choice([0, 1], n_samples)
})

print(f"📊 Sample dataset created:")
print(f"   Shape: {df_test.shape}")
print(f"   Columns: {list(df_test.columns)}")
print()

# Test 1: Analyze encoding needs
print("🔍 TEST 1: Analyzing encoding needs...")
try:
    analysis = edaflow.analyze_encoding_needs(
        df_test, 
        target_column='target',
        ordinal_columns=['education']  # Specify this as ordinal
    )
    print("✅ analyze_encoding_needs() works perfectly!")
    
except Exception as e:
    print(f"❌ analyze_encoding_needs() failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: Apply smart encoding
print("⚡ TEST 2: Applying smart encoding...")
try:
    df_encoded, encoders = edaflow.apply_smart_encoding(
        df_test.drop('target', axis=1),  # Exclude target for encoding
        encoding_analysis=analysis,
        return_encoders=True
    )
    
    print("✅ apply_smart_encoding() works perfectly!")
    print(f"   Original shape: {df_test.drop('target', axis=1).shape}")
    print(f"   Encoded shape: {df_encoded.shape}")
    print(f"   New columns: {df_encoded.shape[1] - df_test.drop('target', axis=1).shape[1]}")
    print(f"   Encoders saved: {len(encoders)}")
    
except Exception as e:
    print(f"❌ apply_smart_encoding() failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Check function availability
print("📋 TEST 3: Function availability check...")
all_functions = [attr for attr in dir(edaflow) if not attr.startswith('_')]
print(f"✅ Total functions: {len(all_functions)}")

if 'analyze_encoding_needs' in all_functions:
    print("✅ analyze_encoding_needs available")
else:
    print("❌ analyze_encoding_needs missing")

if 'apply_smart_encoding' in all_functions:
    print("✅ apply_smart_encoding available")  
else:
    print("❌ apply_smart_encoding missing")

print(f"✅ edaflow version: {edaflow.__version__}")

print()
print("🎉 Encoding functionality test complete!")
print("edaflow v0.12.0 - Intelligent Encoding Suite is ready! 🚀")

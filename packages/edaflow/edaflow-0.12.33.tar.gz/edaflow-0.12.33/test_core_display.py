"""Test script to verify display formatting fixes for core functions"""

import pandas as pd
import numpy as np
from edaflow.analysis.core import (
    convert_to_numeric, 
    display_column_types, 
    impute_numerical_median
)

# Create test data for all functions
df_mixed = pd.DataFrame({
    'numeric_str': ['1', '2', '3', '4'],  # Should convert
    'mixed': ['1', '2', 'three', '4'],    # Should not convert (>35% non-numeric)
    'age': [25, 30, None, 35],            # Numerical with missing
    'salary': [50000, None, 60000, None], # Numerical with missing
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],  # Categorical
    'status': ['Active', 'Inactive', 'Active', 'Active']  # Categorical
})

print("Testing display formatting fixes:")
print("=" * 70)

print("\n1. Testing convert_to_numeric function:")
print("-" * 40)
result1 = convert_to_numeric(df_mixed, threshold=35)

print("\n2. Testing display_column_types function:")
print("-" * 40)
result2 = display_column_types(df_mixed)

print("\n3. Testing impute_numerical_median function:")
print("-" * 40)
result3 = impute_numerical_median(df_mixed)

print("\n" + "=" * 70)
print("✅ All tests completed - checking for clean formatting")

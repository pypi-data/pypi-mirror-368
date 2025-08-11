"""Test script to verify check_null_columns display formatting fixes"""

import pandas as pd
import numpy as np
from edaflow.analysis.missing_data import check_null_columns

# Create test data with missing values
np.random.seed(42)
df = pd.DataFrame({
    'name': ['Alice', 'Bob', None, 'Diana', 'Eve'],
    'age': [25, 30, np.nan, 35, None],
    'score': [85.5, None, 92.0, np.nan, 88.5],
    'city': ['NYC', 'LA', 'Chicago', None, 'Miami'],
    'complete_col': [1, 2, 3, 4, 5]  # No missing values
})

print("Testing check_null_columns display formatting:")
print("=" * 50)
check_null_columns(df, detailed=True)
print("\n" + "=" * 50)
print("✅ Test completed - checking for clean output without unnecessary separators")

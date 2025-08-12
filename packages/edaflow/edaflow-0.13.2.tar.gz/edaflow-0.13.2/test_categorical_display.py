"""Test script to verify analyze_categorical_columns display formatting fixes"""

import pandas as pd
import numpy as np
from edaflow.analysis.core import analyze_categorical_columns

# Create test data with mixed categorical columns
df = pd.DataFrame({
    'physical_activity': ['weekly', 'rarely', 'daily', 'weekly'],
    'diet': ['high protein', 'low salt', 'balanced', 'high protein'],
    'smoking': ['yes', 'no', 'yes', 'no'],
    'alcohol': ['daily', 'never', 'occasionally', 'daily'],
    'painkiller_usage': ['2', '4', '0', '2'],  # Potentially numeric
    'family_history': ['yes', 'no', 'yes', 'no'],
    'weight_changes': ['stable', 'loss', 'gain', 'stable'],
    'stress_level': ['low', 'medium', 'high', 'low'],
    'ckd_pred': ['ckd', 'no ckd', 'ckd', 'no ckd'],
    'age': [25, 30, 35, 40],  # Numeric column
    'score': [85.5, 92.0, 88.5, 90.0]  # Another numeric column
})

print("Testing analyze_categorical_columns display formatting:")
print("=" * 60)
analyze_categorical_columns(df, threshold=35)
print("=" * 60)
print("✅ Test completed - checking for clean output formatting")

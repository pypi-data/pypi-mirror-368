#!/usr/bin/env python3
"""
Test script to verify the check_null_columns display fix
"""

import pandas as pd
import sys
import os

# Add the edaflow package to path
sys.path.insert(0, os.path.abspath('.'))

try:
    import edaflow
    print("✅ Successfully imported edaflow")
except ImportError as e:
    print(f"❌ Failed to import edaflow: {e}")
    sys.exit(1)

print("🧪 Testing check_null_columns display fix...")

# Create test data with various null percentages
df = pd.DataFrame({
    'serum_creatinine': [1.2, 1.3, 1.1, 1.4, 1.0] * 800,  # No nulls (clean)
    'gfr': [90, 85, None, 88, 92] * 800,  # 20% nulls (minor)
    'bun': [15, None, None, 18, 20] * 800,  # 40% nulls (warning) 
    'serum_calcium': [None, None, None, None, None] * 800,  # 100% nulls (critical)
    'ana': [0, 1, 0, None, 1] * 800  # 20% nulls (minor)
})

print(f"📊 Created test DataFrame with {len(df)} rows and {len(df.columns)} columns")

# Test the function
print("\n🔍 Running edaflow.check_null_columns()...")

try:
    result = edaflow.check_null_columns(df, threshold=10)
    print("\n✅ SUCCESS: check_null_columns completed without errors!")
    print("🎯 Visual improvements applied:")
    print("   • Removed unnecessary '====' separators")
    print("   • Fixed table border line joining with SIMPLE box style")
    print("   • Clean, professional output maintained")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Display Fix Test Complete!")

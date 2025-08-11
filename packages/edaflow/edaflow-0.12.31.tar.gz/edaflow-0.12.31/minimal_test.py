import sys
print("Python path:", sys.path)

try:
    import pandas as pd
    print("✅ Pandas imported successfully")
except Exception as e:
    print("❌ Pandas import failed:", e)

try:
    import numpy as np
    print("✅ NumPy imported successfully")
except Exception as e:
    print("❌ NumPy import failed:", e)

try:
    from rich.console import Console
    print("✅ Rich imported successfully")
except Exception as e:
    print("❌ Rich import failed:", e)

try:
    from edaflow.analysis.missing_data import check_null_columns
    print("✅ edaflow.analysis.missing_data imported successfully")
except Exception as e:
    print("❌ edaflow import failed:", e)
    import traceback
    traceback.print_exc()

# If all imports successful, test the function
try:
    df = pd.DataFrame({
        'col1': [1, 2, None],
        'col2': ['A', None, 'C']
    })
    print("\n📊 Testing check_null_columns function:")
    print("="*50)
    result = check_null_columns(df)
    print("="*50)
    print("✅ Test completed successfully!")
    print("Result keys:", result.keys())
except Exception as e:
    print("❌ Function test failed:", e)
    import traceback
    traceback.print_exc()

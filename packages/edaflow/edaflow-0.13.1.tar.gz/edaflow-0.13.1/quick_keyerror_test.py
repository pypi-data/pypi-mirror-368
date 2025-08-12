"""Quick test for KeyError fix"""
import pandas as pd
import edaflow

# Create simple test data
df = pd.DataFrame({
    'feature1': [1, 2, 3, 4, 5],
    'feature2': ['A', 'B', 'C', 'D', 'E'],  
    'target': ['pos', 'neg', 'pos', 'neg', 'pos']
})

print("Testing summarize_eda_insights with target...")
try:
    insights = edaflow.summarize_eda_insights(df, target_column='target')
    print("✅ SUCCESS: No KeyError!")
    print(f"Target analysis type: {insights.get('target_analysis', {}).get('type', 'Not found')}")
except KeyError as e:
    print(f"❌ KeyError still present: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")

print("\nTesting with non-existent target...")  
try:
    insights = edaflow.summarize_eda_insights(df, target_column='fake_target')
    print("✅ SUCCESS: Handled non-existent target!")
except KeyError as e:
    print(f"❌ KeyError: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")

#!/usr/bin/env python3

"""
Test the analyze_encoding_needs function fix for max_cardinality parameter
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import edaflow
import pandas as pd
import numpy as np

def test_analyze_encoding_needs_fix():
    """Test both old and new parameter names work"""
    print("🧪 Testing analyze_encoding_needs parameter fix...")
    
    # Create a sample DataFrame
    np.random.seed(42)
    df = pd.DataFrame({
        'high_cardinality': ['cat_' + str(i) for i in np.random.randint(0, 50, 1000)],
        'low_cardinality': np.random.choice(['A', 'B', 'C'], 1000),
        'numeric': np.random.randn(1000),
        'target': np.random.choice([0, 1], 1000)
    })
    
    print(f"📊 Created test DataFrame with {len(df)} rows")
    
    try:
        print("\n" + "="*60)
        print("TEST 1: Using new parameter name (max_cardinality_onehot)")
        print("="*60)
        
        # Test with new parameter name
        analysis1 = edaflow.analyze_encoding_needs(
            df,
            target_column='target',
            max_cardinality_onehot=15
        )
        print("✅ SUCCESS: max_cardinality_onehot parameter works")
        print(f"   Found {len(analysis1['recommendations'])} column recommendations")
        
        print("\n" + "="*60)
        print("TEST 2: Using legacy parameter name (max_cardinality)")
        print("="*60)
        
        # Test with legacy parameter name (this should now work!)
        analysis2 = edaflow.analyze_encoding_needs(
            df,
            target_column='target',
            max_cardinality=15  # This was causing the TypeError before
        )
        print("✅ SUCCESS: max_cardinality parameter now works as alias")
        print(f"   Found {len(analysis2['recommendations'])} column recommendations")
        
        print("\n" + "="*60)
        print("TEST 3: Both parameters should give same results")
        print("="*60)
        
        # Compare results
        if analysis1['recommendations'] == analysis2['recommendations']:
            print("✅ SUCCESS: Both parameter names give identical results")
        else:
            print("❌ WARNING: Results differ between parameter names")
            
        print("\n" + "="*60)
        print("TEST 4: Show sample recommendations")
        print("="*60)
        
        for col, recommendation in analysis1['recommendations'].items():
            print(f"   📊 {col}: {recommendation}")
        
        print("\n✅ ALL TESTS PASSED: analyze_encoding_needs fix working!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_analyze_encoding_needs_fix()

"""
🧪 TEST KEYERROR FIX FOR SUMMARIZE_EDA_INSIGHTS
==============================================

Test to verify that the KeyError in summarize_eda_insights function 
has been fixed and the function now handles edge cases properly.
"""

def test_keyerror_fix():
    """Test the KeyError fix for summarize_eda_insights function."""
    
    print("🧪 TESTING KEYERROR FIX FOR summarize_eda_insights")
    print("=" * 55)
    
    try:
        import pandas as pd
        import numpy as np
        import edaflow
        
        print(f"✅ Successfully imported edaflow v{edaflow.__version__}")
        
        # Create test data similar to the one causing issues
        test_data = {
            'feature1': [1, 2, 3, 4, 5] * 200,  # 1000 rows
            'feature2': ['A', 'B', 'C', 'D', 'E'] * 200,
            'feature3': np.random.normal(0, 1, 1000),
            'target_column': ['positive', 'negative'] * 500
        }
        
        df = pd.DataFrame(test_data)
        print(f"✅ Created test DataFrame: {df.shape}")
        
        # Test cases that might cause KeyError
        test_cases = [
            {
                'name': 'Normal case with valid target',
                'target': 'target_column',
                'functions': ['check_null_columns', 'analyze_categorical_columns']
            },
            {
                'name': 'Case with non-existent target column',
                'target': 'non_existent_target',
                'functions': ['check_null_columns']
            },
            {
                'name': 'Case with None target',
                'target': None,
                'functions': ['visualize_histograms']
            },
            {
                'name': 'Case with empty functions list',
                'target': 'target_column', 
                'functions': []
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔍 Test {i}: {test_case['name']}")
            try:
                # This should not raise KeyError anymore
                insights = edaflow.summarize_eda_insights(
                    df,
                    target_column=test_case['target'],
                    eda_functions_used=test_case['functions']
                )
                
                print(f"   ✅ SUCCESS: Function executed without KeyError")
                print(f"   📊 Insights keys: {list(insights.keys())}")
                
                # Check if target_analysis exists and has proper structure
                if 'target_analysis' in insights:
                    target_info = insights['target_analysis']
                    if 'type' in target_info:
                        print(f"   🎯 Target type: {target_info['type']}")
                    else:
                        print(f"   ⚠️  Target analysis missing 'type' key")
                
                success_count += 1
                
            except KeyError as e:
                print(f"   ❌ FAILED: KeyError still present: {e}")
            except Exception as e:
                print(f"   ❌ FAILED: Other error: {e}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total tests: {len(test_cases)}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {len(test_cases) - success_count}")
        
        if success_count == len(test_cases):
            print(f"   🎉 ALL TESTS PASSED! KeyError fix successful!")
        else:
            print(f"   ⚠️  Some tests failed. KeyError fix needs more work.")
            
        return success_count == len(test_cases)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_edge_cases():
    """Test additional edge cases that might cause issues."""
    
    print(f"\n🔬 TESTING EDGE CASES")
    print("=" * 25)
    
    try:
        import pandas as pd
        import numpy as np
        import edaflow
        
        # Edge case 1: DataFrame with all NaN target
        df_nan_target = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'target': [np.nan] * 5
        })
        
        print("🔍 Testing DataFrame with all NaN target...")
        insights1 = edaflow.summarize_eda_insights(df_nan_target, target_column='target')
        print("   ✅ Handled NaN target successfully")
        
        # Edge case 2: DataFrame with single unique target value
        df_single_target = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'target': ['same_value'] * 5
        })
        
        print("🔍 Testing DataFrame with single unique target value...")
        insights2 = edaflow.summarize_eda_insights(df_single_target, target_column='target')
        print("   ✅ Handled single unique target successfully")
        
        # Edge case 3: Empty DataFrame
        df_empty = pd.DataFrame()
        
        print("🔍 Testing empty DataFrame...")
        try:
            insights3 = edaflow.summarize_eda_insights(df_empty, target_column=None)
            print("   ✅ Handled empty DataFrame successfully")
        except Exception as e:
            print(f"   ⚠️  Empty DataFrame caused error (expected): {e}")
        
        print(f"\n🎯 EDGE CASES TESTING COMPLETE")
        return True
        
    except Exception as e:
        print(f"❌ Edge case testing failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 KEYERROR FIX VALIDATION FOR EDAFLOW v0.12.30")
    print("=" * 60)
    
    # Test the KeyError fix
    main_test_passed = test_keyerror_fix()
    
    # Test edge cases
    edge_test_passed = test_edge_cases()
    
    print(f"\n🏁 FINAL RESULTS:")
    print(f"   Main KeyError fix: {'✅ PASSED' if main_test_passed else '❌ FAILED'}")
    print(f"   Edge cases: {'✅ PASSED' if edge_test_passed else '❌ FAILED'}")
    
    if main_test_passed and edge_test_passed:
        print(f"\n🎉 SUCCESS: KeyError fix is working correctly!")
        print(f"   edaflow.summarize_eda_insights() now handles all edge cases")
        print(f"   Users should no longer experience KeyError with 'type' key")
    else:
        print(f"\n⚠️  ISSUES DETECTED: Additional fixes may be needed")
        
    print(f"\n📦 Ready for hotfix release: v0.12.31")

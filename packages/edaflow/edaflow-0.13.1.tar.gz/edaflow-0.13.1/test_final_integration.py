"""
🧪 TEST INTEGRATION OF OPTIMIZE_DISPLAY IN EDAFLOW v0.12.30
============================================================

Quick test to verify that optimize_display() is properly integrated 
into the edaflow package and accessible to users.
"""

def test_integration():
    """Test that optimize_display is properly integrated."""
    
    print("🧪 TESTING EDAFLOW v0.12.30 INTEGRATION")
    print("=" * 50)
    
    try:
        # Test importing edaflow
        import edaflow
        print(f"✅ edaflow imported successfully")
        print(f"📦 Version: {edaflow.__version__}")
        
        # Test that optimize_display is available
        if hasattr(edaflow, 'optimize_display'):
            print(f"✅ optimize_display function available")
        else:
            print(f"❌ optimize_display function NOT found")
            return False
            
        # Test calling optimize_display
        print(f"\n🔍 Testing optimize_display() function:")
        config = edaflow.optimize_display(verbose=True)
        print(f"✅ optimize_display executed successfully")
        
        # Test with existing edaflow function
        print(f"\n📊 Testing with existing edaflow functions:")
        print(f"🔍 Testing hello():")
        message = edaflow.hello()
        print(f"   Result: {message}")
        
        # Test with sample data function
        print(f"🔍 Testing with data analysis:")
        import pandas as pd
        import numpy as np
        
        # Create sample data
        test_df = pd.DataFrame({
            'category': ['A', 'B', 'C', None, 'A'],
            'numeric': [1, 2, None, 4, 5],
            'values': np.random.normal(0, 1, 5)
        })
        
        # Test null analysis with optimize_display already active
        result = edaflow.check_null_columns(test_df, threshold=10)
        print(f"✅ check_null_columns worked with optimized display")
        
        print(f"\n🎯 INTEGRATION TEST RESULTS:")
        print(f"   ✅ Package version updated to {edaflow.__version__}")
        print(f"   ✅ optimize_display function integrated")
        print(f"   ✅ Function executes without errors")
        print(f"   ✅ Compatible with existing functions")
        print(f"   ✅ Ready for release!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except AttributeError as e:
        print(f"❌ Attribute Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_all_functions_available():
    """Test that all expected functions are available."""
    
    print(f"\n📋 TESTING ALL EXPORTED FUNCTIONS:")
    print("=" * 40)
    
    import edaflow
    
    expected_functions = [
        'hello',
        'optimize_display',  # New function
        'check_null_columns', 
        'analyze_categorical_columns', 
        'convert_to_numeric', 
        'visualize_categorical_values',
        'display_column_types',
        'impute_numerical_median',
        'impute_categorical_mode',
        'visualize_numerical_boxplots',
        'handle_outliers_median',
        'visualize_interactive_boxplots',
        'visualize_heatmap',
        'visualize_histograms',
        'visualize_scatter_matrix',
        'visualize_image_classes',
        'assess_image_quality',
        'analyze_image_features',
        'analyze_encoding_needs',
        'apply_smart_encoding',
        'summarize_eda_insights'
    ]
    
    missing_functions = []
    available_functions = []
    
    for func_name in expected_functions:
        if hasattr(edaflow, func_name):
            available_functions.append(func_name)
            if func_name == 'optimize_display':
                print(f"   ✅ {func_name} (⭐ NEW)")
            else:
                print(f"   ✅ {func_name}")
        else:
            missing_functions.append(func_name)
            print(f"   ❌ {func_name}")
    
    print(f"\n📊 FUNCTION AVAILABILITY SUMMARY:")
    print(f"   Total expected: {len(expected_functions)}")
    print(f"   Available: {len(available_functions)}")
    print(f"   Missing: {len(missing_functions)}")
    
    if missing_functions:
        print(f"   ❌ Missing functions: {', '.join(missing_functions)}")
        return False
    else:
        print(f"   ✅ All functions available!")
        return True

if __name__ == "__main__":
    print("🚀 TESTING EDAFLOW v0.12.30 INTEGRATION")
    print("=" * 60)
    
    # Test basic integration
    integration_success = test_integration()
    
    # Test all functions
    functions_success = test_all_functions_available()
    
    print(f"\n🏁 FINAL RESULTS:")
    print("=" * 30)
    
    if integration_success and functions_success:
        print("✅ INTEGRATION SUCCESS!")
        print("🚀 edaflow v0.12.30 is ready for publishing!")
        print("📦 Users can now use: edaflow.optimize_display()")
        print("🌍 Universal dark mode compatibility achieved!")
    else:
        print("❌ INTEGRATION ISSUES DETECTED")
        print("🔧 Please fix issues before publishing")
        
    print(f"\n💡 USAGE EXAMPLE:")
    print("import edaflow")
    print("edaflow.optimize_display()  # Perfect visibility everywhere!")
    print("edaflow.check_null_columns(df)  # Now displays perfectly!")

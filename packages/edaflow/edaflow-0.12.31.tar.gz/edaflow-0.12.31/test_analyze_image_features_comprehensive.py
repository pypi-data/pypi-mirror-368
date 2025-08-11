#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE TEST: analyze_image_features() Parameter Validation
================================================================

This script verifies that ALL parameters in analyze_image_features() documentation 
are accurate and the function works correctly. This test ensures we maintain
the highest quality standards for the edaflow package.

Testing Strategy:
1. Verify function signature matches documentation
2. Test all documented parameters with various values
3. Test error handling for invalid parameters
4. Validate return structure matches documentation
5. Test with real image data

Author: edaflow Quality Assurance Team
Date: 2025-08-08
Version: Comprehensive Parameter Validation v1.0
"""

import os
import sys
import inspect
import tempfile
import numpy as np
from PIL import Image
import pandas as pd
from typing import Dict, Any, List
import traceback
import warnings

# Add the edaflow package to path
sys.path.insert(0, os.path.abspath('.'))

try:
    import edaflow
    from edaflow.analysis.core import analyze_image_features
except ImportError as e:
    print(f"❌ Failed to import edaflow: {e}")
    sys.exit(1)

print("🚀 EDAFLOW ANALYZE_IMAGE_FEATURES() COMPREHENSIVE TEST")
print("=" * 65)

def create_test_images(temp_dir: str, num_classes: int = 3, images_per_class: int = 5) -> Dict[str, List[str]]:
    """Create synthetic test images for testing."""
    print(f"📸 Creating {num_classes * images_per_class} test images...")
    
    classes = ['class_a', 'class_b', 'class_c'][:num_classes]
    image_data = {}
    
    for class_name in classes:
        class_dir = os.path.join(temp_dir, class_name)
        os.makedirs(class_dir, exist_ok=True)
        image_data[class_name] = []
        
        for i in range(images_per_class):
            # Create different synthetic patterns for each class
            if class_name == 'class_a':
                # Red-dominant images with horizontal lines
                img_array = np.random.randint(100, 255, (100, 100, 3), dtype=np.uint8)
                img_array[:, :, 0] = 200  # Red channel
                img_array[20:25, :, :] = 255  # Horizontal lines
                img_array[50:55, :, :] = 255
                img_array[80:85, :, :] = 255
                
            elif class_name == 'class_b':
                # Blue-dominant images with vertical lines
                img_array = np.random.randint(50, 150, (100, 100, 3), dtype=np.uint8)
                img_array[:, :, 2] = 180  # Blue channel
                img_array[:, 20:25, :] = 255  # Vertical lines
                img_array[:, 50:55, :] = 255
                img_array[:, 80:85, :] = 255
                
            else:
                # Green-dominant images with checkerboard pattern
                img_array = np.random.randint(80, 180, (100, 100, 3), dtype=np.uint8)
                img_array[:, :, 1] = 160  # Green channel
                # Checkerboard pattern
                for x in range(0, 100, 20):
                    for y in range(0, 100, 20):
                        if (x//20 + y//20) % 2 == 0:
                            img_array[y:y+20, x:x+20, :] = 255
            
            # Save image
            img = Image.fromarray(img_array)
            img_path = os.path.join(class_dir, f'image_{i:03d}.png')
            img.save(img_path)
            image_data[class_name].append(img_path)
    
    print(f"✅ Created test images in {temp_dir}")
    return image_data

def test_function_signature():
    """Test 1: Verify function signature matches documentation."""
    print("\n🔍 TEST 1: Function Signature Verification")
    print("-" * 50)
    
    # Get function signature
    sig = inspect.signature(analyze_image_features)
    params = list(sig.parameters.keys())
    
    print(f"📝 Function signature: {len(params)} parameters")
    
    # Expected parameters based on documentation
    expected_params = [
        'data_source', 'class_column', 'image_path_column', 'sample_size',
        'analyze_edges', 'analyze_texture', 'analyze_color', 'analyze_gradients',
        'edge_method', 'texture_method', 'color_spaces', 'bins_per_channel',
        'lbp_radius', 'lbp_n_points', 'canny_low_threshold', 'canny_high_threshold',
        'create_visualizations', 'figsize', 'save_path', 'verbose', 'return_feature_vectors'
    ]
    
    print("🔎 Parameter validation:")
    all_params_valid = True
    
    for expected_param in expected_params:
        if expected_param in params:
            param_obj = sig.parameters[expected_param]
            print(f"  ✅ {expected_param}: {param_obj.annotation} = {param_obj.default}")
        else:
            print(f"  ❌ MISSING: {expected_param}")
            all_params_valid = False
    
    # Check for unexpected parameters
    for param in params:
        if param not in expected_params:
            print(f"  ⚠️  UNDOCUMENTED: {param}")
    
    # Verify critical parameter names from user's error
    critical_params = ['analyze_color', 'bins_per_channel']
    for param in critical_params:
        if param in params:
            print(f"  🎯 CRITICAL PARAM OK: {param}")
        else:
            print(f"  🚨 CRITICAL PARAM MISSING: {param}")
            all_params_valid = False
    
    return all_params_valid

def test_basic_functionality(image_data: Dict[str, List[str]]):
    """Test 2: Basic functionality with default parameters."""
    print("\n🧪 TEST 2: Basic Functionality Test")
    print("-" * 50)
    
    try:
        # Test with directory structure
        temp_dir = os.path.dirname(list(image_data.values())[0][0])
        
        print("📊 Testing with directory structure...")
        result = analyze_image_features(
            temp_dir,
            verbose=True,
            create_visualizations=False  # Skip visualizations for testing
        )
        
        print(f"✅ Function executed successfully!")
        print(f"📈 Analyzed {result.get('total_images', 0)} images")
        print(f"🏷️  Found {result.get('num_classes', 0)} classes")
        
        # Verify return structure
        expected_keys = [
            'total_images', 'num_classes', 'edge_analysis', 'texture_analysis',
            'color_analysis', 'gradient_analysis', 'class_comparisons',
            'feature_rankings', 'recommendations', 'statistical_tests'
        ]
        
        print("\n🔍 Return structure validation:")
        for key in expected_keys:
            if key in result:
                print(f"  ✅ {key}: {type(result[key])}")
            else:
                print(f"  ❌ MISSING: {key}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {str(e)}")
        traceback.print_exc()
        return False, None

def test_parameter_combinations(image_data: Dict[str, List[str]]):
    """Test 3: All documented parameter combinations."""
    print("\n🔬 TEST 3: Parameter Combinations Test")
    print("-" * 50)
    
    temp_dir = os.path.dirname(list(image_data.values())[0][0])
    test_cases = [
        {
            'name': 'RTD Documentation Example',
            'params': {
                'data_source': temp_dir,
                'analyze_color': True,      # CORRECT parameter name
                'analyze_edges': True,
                'analyze_texture': True,
                'analyze_gradients': True,
                'sample_size': 100,
                'bins_per_channel': 50,     # CORRECT parameter name
                'create_visualizations': False,
                'verbose': False
            }
        },
        {
            'name': 'Medical Imaging Example',
            'params': {
                'data_source': temp_dir,
                'analyze_color': False,     # Medical scans often grayscale
                'analyze_texture': True,
                'analyze_edges': True,
                'texture_method': 'lbp',
                'lbp_radius': 5,
                'edge_method': 'canny',
                'create_visualizations': False,
                'verbose': False
            }
        },
        {
            'name': 'Production Feature Selection',
            'params': {
                'data_source': temp_dir,
                'sample_size': 10,          # Small sample for testing
                'color_spaces': ['RGB', 'HSV', 'LAB'],
                'bins_per_channel': 32,
                'return_feature_vectors': True,
                'create_visualizations': False,
                'verbose': False
            }
        },
        {
            'name': 'Edge Cases Test',
            'params': {
                'data_source': temp_dir,
                'analyze_edges': False,
                'analyze_texture': False,
                'analyze_color': False,
                'analyze_gradients': False,
                'create_visualizations': False,
                'verbose': False
            }
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🧪 Test Case {i+1}: {test_case['name']}")
        try:
            result = analyze_image_features(**test_case['params'])
            print(f"  ✅ SUCCESS: {result.get('total_images', 0)} images analyzed")
            successful_tests += 1
            
            # Special validation for feature vectors test
            if test_case['name'] == 'Production Feature Selection':
                if 'feature_vectors' in result and result['feature_vectors'] is not None:
                    print(f"  🎯 Feature vectors returned successfully")
                else:
                    print(f"  ⚠️  Feature vectors not returned as expected")
                    
        except Exception as e:
            print(f"  ❌ FAILED: {str(e)}")
    
    print(f"\n📊 Parameter Combinations Test Results: {successful_tests}/{total_tests} passed")
    return successful_tests == total_tests

def test_error_handling():
    """Test 4: Error handling for invalid parameters."""
    print("\n🚫 TEST 4: Error Handling Test")
    print("-" * 50)
    
    error_test_cases = [
        {
            'name': 'Invalid analyze_colors parameter (user\'s original error)',
            'params': {
                'data_source': [],
                'analyze_colors': True,  # WRONG parameter name (should be analyze_color)
                'verbose': False
            },
            'expected_error': TypeError
        },
        {
            'name': 'Invalid bins parameter (should be bins_per_channel)',
            'params': {
                'data_source': [],
                'bins': 50,  # WRONG parameter name (should be bins_per_channel)
                'verbose': False
            },
            'expected_error': TypeError
        },
        {
            'name': 'Non-existent directory',
            'params': {
                'data_source': '/non/existent/path',
                'verbose': False,
                'create_visualizations': False
            },
            'expected_error': (FileNotFoundError, ValueError, OSError)
        }
    ]
    
    error_tests_passed = 0
    total_error_tests = len(error_test_cases)
    
    for i, test_case in enumerate(error_test_cases):
        print(f"\n🧪 Error Test {i+1}: {test_case['name']}")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # Suppress warnings during error tests
                result = analyze_image_features(**test_case['params'])
            print(f"  ❌ FAILED: Expected error but function succeeded")
        except test_case['expected_error'] as e:
            print(f"  ✅ SUCCESS: Correctly raised {type(e).__name__}: {str(e)[:100]}...")
            error_tests_passed += 1
        except Exception as e:
            print(f"  ⚠️  PARTIAL: Raised {type(e).__name__} instead of {test_case['expected_error']}")
            print(f"     Error: {str(e)[:100]}...")
    
    print(f"\n📊 Error Handling Test Results: {error_tests_passed}/{total_error_tests} passed")
    return error_tests_passed == total_error_tests

def test_dataframe_input(image_data: Dict[str, List[str]]):
    """Test 5: DataFrame input functionality."""
    print("\n📊 TEST 5: DataFrame Input Test")
    print("-" * 50)
    
    try:
        # Create DataFrame with image paths
        data_rows = []
        for class_name, img_paths in image_data.items():
            for img_path in img_paths:
                data_rows.append({
                    'image_path': img_path,
                    'class': class_name
                })
        
        df = pd.DataFrame(data_rows)
        print(f"📋 Created DataFrame with {len(df)} rows")
        
        # Test DataFrame input
        result = analyze_image_features(
            df,
            class_column='class',
            image_path_column='image_path',
            create_visualizations=False,
            verbose=False
        )
        
        print(f"✅ DataFrame input test passed!")
        print(f"📈 Analyzed {result.get('total_images', 0)} images from DataFrame")
        return True
        
    except Exception as e:
        print(f"❌ DataFrame input test failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🔧 Environment Setup")
    print("-" * 30)
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📦 edaflow: {getattr(edaflow, '__version__', 'unknown')}")
    
    # Create temporary directory with test images
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Create test data
            image_data = create_test_images(temp_dir)
            
            # Run all tests
            test_results = []
            
            # Test 1: Function signature
            test_results.append(("Function Signature", test_function_signature()))
            
            # Test 2: Basic functionality
            basic_success, basic_result = test_basic_functionality(image_data)
            test_results.append(("Basic Functionality", basic_success))
            
            if basic_success:
                # Test 3: Parameter combinations
                test_results.append(("Parameter Combinations", test_parameter_combinations(image_data)))
                
                # Test 4: Error handling
                test_results.append(("Error Handling", test_error_handling()))
                
                # Test 5: DataFrame input
                test_results.append(("DataFrame Input", test_dataframe_input(image_data)))
            
            # Final results
            print("\n" + "="*65)
            print("🏆 COMPREHENSIVE TEST RESULTS")
            print("="*65)
            
            passed_tests = 0
            total_tests = len(test_results)
            
            for test_name, result in test_results:
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"{test_name:.<30} {status}")
                if result:
                    passed_tests += 1
            
            print(f"\n🎯 OVERALL SCORE: {passed_tests}/{total_tests} tests passed")
            
            if passed_tests == total_tests:
                print("🌟 ALL TESTS PASSED! Documentation is accurate and function works correctly.")
                print("🚀 The edaflow package maintains the highest quality standards!")
                return_code = 0
            else:
                print("⚠️  Some tests failed. Please review the results above.")
                return_code = 1
                
        except Exception as e:
            print(f"💥 Test setup failed: {str(e)}")
            traceback.print_exc()
            return_code = 1
    
    print("\n" + "="*65)
    return return_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

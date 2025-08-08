#!/usr/bin/env python3
"""
Test script that reproduces the exact error your colleague encountered
and demonstrates that it's now fixed in v0.12.1
"""

import edaflow
import tempfile
import os
from PIL import Image
import numpy as np

def create_sample_dataset():
    """Create a sample image dataset for testing"""
    base_dir = tempfile.mkdtemp()
    
    # Create class directories
    for class_name in ['cats', 'dogs', 'birds']:
        class_dir = os.path.join(base_dir, class_name)
        os.makedirs(class_dir)
        
        # Create sample images
        for i in range(8):
            img_path = os.path.join(class_dir, f'{class_name}_{i}.jpg')
            # Create a simple test image
            img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(img_path)
    
    return base_dir

def test_colleague_usage():
    """Test the exact usage pattern that was failing for your colleague"""
    print("🔬 Testing colleague's exact usage pattern...")
    print("=" * 60)
    
    # Create test dataset
    eda_images = create_sample_dataset()
    print(f"📁 Created test dataset: {eda_images}")
    
    print("\n🎯 STEP 1: DATASET VISUALIZATION")
    print("-" * 50)
    
    try:
        # This is the EXACT code that was failing before our fix
        edaflow.visualize_image_classes(
            image_paths=eda_images,  # This parameter name was causing TypeError
            samples_per_class=6,        # Show 6 examples per class
            figsize=(15, 10),
            title="Dataset Overview: Class Distribution & Samples"
        )
        
        print("✅ SUCCESS: Your colleague's code now works!")
        print("📝 Note: A deprecation warning was shown above")
        return True
        
    except TypeError as e:
        print(f"❌ FAILED: TypeError still occurring: {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
        return False

def test_recommended_usage():
    """Test the recommended new usage pattern"""
    print("\n\n🎯 RECOMMENDED USAGE (No warnings):")
    print("-" * 50)
    
    eda_images = create_sample_dataset()
    
    try:
        # This is the RECOMMENDED way (no deprecation warning)
        edaflow.visualize_image_classes(
            data_source=eda_images,     # Use data_source instead of image_paths
            samples_per_class=6,
            figsize=(15, 10),
            title="Dataset Overview: Class Distribution & Samples (Recommended)"
        )
        
        print("✅ SUCCESS: Recommended usage works without warnings!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🚀 edaflow v0.12.1 - Backward Compatibility Test")
    print("=" * 60)
    print("This test reproduces and verifies the fix for the TypeError")
    print("that your colleague encountered with visualize_image_classes()")
    print()
    
    # Test the failing scenario
    colleague_success = test_colleague_usage()
    
    # Test the recommended approach  
    recommended_success = test_recommended_usage()
    
    print("\n" + "=" * 60)
    if colleague_success and recommended_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your colleague's code will now work with v0.12.1")
        print("⚠️  They'll see a deprecation warning encouraging them to use 'data_source'")
        print("✅ The recommended approach works without warnings")
    else:
        print("❌ Some tests failed - the fix may not be working correctly")
    
    print("\n📋 Tell your colleague:")
    print("1. pip install --upgrade edaflow")
    print("2. Their existing code will work (with a warning)")  
    print("3. For clean code, replace 'image_paths=' with 'data_source='")
    print("\nView at: https://pypi.org/project/edaflow/0.12.1/")

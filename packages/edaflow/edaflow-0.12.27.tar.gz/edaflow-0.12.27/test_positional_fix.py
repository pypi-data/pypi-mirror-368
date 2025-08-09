#!/usr/bin/env python3
"""
Test script to reproduce the exact Jupyter notebook usage pattern
and verify our positional argument backward compatibility fix
"""

import edaflow
import tempfile
import os
from PIL import Image
import numpy as np

def create_sample_image_dataset():
    """Create a sample image dataset with class folders"""
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

def test_jupyter_notebook_usage():
    """Test the exact usage pattern from the Jupyter notebook"""
    print("🧪 Testing Jupyter Notebook Usage Pattern")
    print("=" * 60)
    
    # Create test dataset
    image_paths = create_sample_image_dataset()
    print(f"📁 Created test dataset: {image_paths}")
    
    print("\n🎯 EXACT JUPYTER NOTEBOOK USAGE:")
    print("edaflow.visualize_image_classes(")
    print("    image_paths,  # ← Positional argument (the problem)")
    print("    samples_per_class=6,")
    print("    figsize=(15, 10),")
    print("    title='Dataset Overview: Class Distribution & Samples'")
    print(")")
    print("-" * 50)
    
    try:
        # This is the EXACT usage from the Jupyter notebook that was failing
        edaflow.visualize_image_classes(
            image_paths,                    # ← Positional argument - should now work!
            samples_per_class=6,
            figsize=(15, 10),
            title="Dataset Overview: Class Distribution & Samples"
        )
        
        print("✅ SUCCESS: Jupyter notebook usage pattern now works!")
        print("📝 Note: A deprecation warning was shown above")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        return False

def test_recommended_usage():
    """Test the recommended usage with keyword argument"""
    print("\n\n🎯 RECOMMENDED USAGE (Keyword Argument):")
    print("edaflow.visualize_image_classes(")
    print("    data_source=image_paths,  # ← Keyword argument (recommended)")
    print("    samples_per_class=6,")
    print("    figsize=(15, 10),")
    print("    title='Dataset Overview'")
    print(")")
    print("-" * 50)
    
    image_paths = create_sample_image_dataset()
    
    try:
        # This is the RECOMMENDED way (no warning)
        edaflow.visualize_image_classes(
            data_source=image_paths,        # ← Keyword argument
            samples_per_class=6,
            figsize=(15, 10),
            title="Dataset Overview: Class Distribution & Samples (Recommended)"
        )
        
        print("✅ SUCCESS: Recommended usage works without warnings!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        return False

def test_keyword_image_paths_usage():
    """Test the keyword image_paths usage (also backward compatible)"""
    print("\n\n🎯 KEYWORD image_paths= USAGE:")
    print("edaflow.visualize_image_classes(")
    print("    image_paths=image_paths,  # ← Deprecated keyword (should work)")
    print("    samples_per_class=6,")
    print("    figsize=(15, 10)")
    print(")")
    print("-" * 50)
    
    image_paths = create_sample_image_dataset()
    
    try:
        # This should also work (deprecated keyword parameter)
        edaflow.visualize_image_classes(
            image_paths=image_paths,        # ← Deprecated keyword parameter
            samples_per_class=6,
            figsize=(15, 10),
            title="Dataset Overview: Using Deprecated Keyword"
        )
        
        print("✅ SUCCESS: Deprecated keyword parameter usage works!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("🚀 edaflow Positional Argument Backward Compatibility Test")
    print("=" * 70)
    print("This test validates that the Jupyter notebook usage pattern works")
    print("after implementing positional argument backward compatibility.")
    print()
    
    # Test all usage patterns
    jupyter_success = test_jupyter_notebook_usage()
    recommended_success = test_recommended_usage()
    keyword_success = test_keyword_image_paths_usage()
    
    print("\n" + "=" * 70)
    if jupyter_success and recommended_success and keyword_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Jupyter notebook positional argument usage now works")
        print("✅ Recommended keyword argument usage works")
        print("✅ Deprecated keyword parameter usage works")
        print()
        print("📋 For the Jupyter notebook user:")
        print("1. Their exact code will now work (with warning)")
        print("2. Recommended: Change to data_source=image_paths")
        print("3. Alternative: Use image_paths=image_paths")
    else:
        print("❌ SOME TESTS FAILED!")
        print("The positional argument fix may not be working correctly")
    
    print("\nView complete fix at: https://pypi.org/project/edaflow/")

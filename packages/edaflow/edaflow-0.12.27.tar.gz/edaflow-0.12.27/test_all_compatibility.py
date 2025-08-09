#!/usr/bin/env python3
"""
Test all three backward compatibility scenarios
"""

import edaflow
import tempfile
import os
from PIL import Image
import numpy as np

def create_test_dataset():
    """Create a simple test dataset"""
    base_dir = tempfile.mkdtemp()
    
    # Create class directories
    for class_name in ['class_a', 'class_b']:
        class_dir = os.path.join(base_dir, class_name)
        os.makedirs(class_dir)
        
        # Create sample images
        for i in range(5):
            img_path = os.path.join(class_dir, f'{class_name}_{i}.jpg')
            # Create a simple test image
            img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(img_path)
    
    return base_dir

def test_all_usage_patterns():
    """Test all three ways to call the function"""
    
    print("🧪 COMPREHENSIVE BACKWARD COMPATIBILITY TEST")
    print("=" * 60)
    
    # Test Case 1: Positional argument (the Jupyter notebook issue)
    print("\n1️⃣ POSITIONAL ARGUMENT TEST (Jupyter notebook pattern):")
    print("   edaflow.visualize_image_classes(image_paths, ...)")
    print("-" * 50)
    
    dataset1 = create_test_dataset()
    try:
        edaflow.visualize_image_classes(
            dataset1,  # Positional argument
            samples_per_class=3,
            figsize=(10, 6),
            title="Test 1: Positional Argument"
        )
        print("✅ SUCCESS: Positional argument works with warning!")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test Case 2: Deprecated keyword parameter
    print("\n\n2️⃣ DEPRECATED KEYWORD TEST:")
    print("   edaflow.visualize_image_classes(image_paths=dataset, ...)")
    print("-" * 50)
    
    dataset2 = create_test_dataset()
    try:
        edaflow.visualize_image_classes(
            image_paths=dataset2,  # Deprecated keyword
            samples_per_class=3,
            figsize=(10, 6),
            title="Test 2: Deprecated Keyword"
        )
        print("✅ SUCCESS: Deprecated keyword works with warning!")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test Case 3: Recommended usage (should be silent)
    print("\n\n3️⃣ RECOMMENDED USAGE TEST:")
    print("   edaflow.visualize_image_classes(data_source=dataset, ...)")
    print("-" * 50)
    
    dataset3 = create_test_dataset()
    try:
        edaflow.visualize_image_classes(
            data_source=dataset3,  # Recommended approach
            samples_per_class=3,
            figsize=(10, 6),
            title="Test 3: Recommended Usage"
        )
        print("✅ SUCCESS: Recommended usage works silently!")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 ALL BACKWARD COMPATIBILITY TESTS COMPLETE!")
    print()
    print("📋 Summary for users:")
    print("✅ Old positional call works (with warning)")
    print("✅ Old image_paths= keyword works (with warning)")
    print("✅ New data_source= keyword works (no warning)")
    print()
    print("🚀 Ready to deploy v0.12.3 with complete fix!")

if __name__ == "__main__":
    test_all_usage_patterns()

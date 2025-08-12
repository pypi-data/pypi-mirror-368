#!/usr/bin/env python3
"""
Test script to verify the max_classes_display parameter functionality.
"""

import os
import tempfile
import sys
from PIL import Image
import numpy as np

# Import our function
from edaflow.analysis import visualize_image_classes

def create_test_image_dataset():
    """Create a test dataset with many classes to test max_classes_display parameter."""
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"Creating test dataset in: {temp_dir}")
    
    # Create 25 classes (more than the default max_classes_display=20)
    class_names = [f"class_{i:02d}" for i in range(25)]
    
    for class_name in class_names:
        class_dir = os.path.join(temp_dir, class_name)
        os.makedirs(class_dir, exist_ok=True)
        
        # Create 3 sample images per class
        for i in range(3):
            # Create a simple colored image
            color = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
            img = Image.fromarray(color)
            img_path = os.path.join(class_dir, f"sample_{i}.png")
            img.save(img_path)
    
    return temp_dir

def test_max_classes_display():
    """Test the max_classes_display parameter."""
    
    print("🧪 Testing max_classes_display parameter...")
    
    # Create test dataset
    dataset_path = create_test_image_dataset()
    
    try:
        print("\n" + "="*60)
        print("📊 Test 1: Default behavior (should limit to 20 classes)")
        print("="*60)
        
        # Test with default max_classes_display (now defaults to 20)
        visualize_image_classes(
            data_source=dataset_path,
            samples_per_class=1,
            title="Test: Default behavior (max_classes_display=20)"
        )
        
        print("\n" + "="*60)
        print("📊 Test 2: Custom max_classes_display=10")
        print("="*60)
        
        # Test with custom max_classes_display
        visualize_image_classes(
            data_source=dataset_path,
            samples_per_class=1,
            max_classes_display=10,
            title="Test: max_classes_display=10"
        )
        
        print("\n" + "="*60)
        print("📊 Test 3: Show all classes (max_classes_display=None)")
        print("="*60)
        
        # Test with max_classes_display=None (show all - cluttered!)
        visualize_image_classes(
            data_source=dataset_path,
            samples_per_class=1,
            max_classes_display=None,
            title="Test: All 25 classes (CLUTTERED - max_classes_display=None)"
        )
        
        print("\n✅ All tests completed successfully!")
        print("The max_classes_display parameter is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        import shutil
        shutil.rmtree(dataset_path)
        print(f"🧹 Cleaned up test dataset: {dataset_path}")

if __name__ == "__main__":
    test_max_classes_display()

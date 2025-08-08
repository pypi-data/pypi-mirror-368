#!/usr/bin/env python3
"""
Quick test to verify the class limiting remark functionality
"""
import tempfile
import os
import shutil
from PIL import Image
import numpy as np
import sys

# Add the current directory to Python path so we can import edaflow
sys.path.insert(0, '.')
import edaflow

def create_test_dataset(base_path, num_classes=30):
    """Create a test dataset with specified number of classes"""
    for i in range(num_classes):
        class_name = f"class_{i:02d}"
        class_dir = os.path.join(base_path, class_name)
        os.makedirs(class_dir, exist_ok=True)
        
        # Create 3 sample images per class
        for j in range(3):
            # Create a random noise image
            img_array = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            
            img_path = os.path.join(class_dir, f"sample_{j+1}.png")
            img.save(img_path)
    
    return base_path

def main():
    # Create temporary dataset
    temp_dir = tempfile.mkdtemp()
    print(f"🧪 Testing class limiting remark with 30 classes...")
    print(f"Creating test dataset in: {temp_dir}")
    
    try:
        # Create dataset with 30 classes (will be limited to 20 by default)
        create_test_dataset(temp_dir, num_classes=30)
        
        print("\n" + "="*60)        
        print("📊 Test: Default limiting (30 → 20 classes)")
        print("="*60)        
        
        # Test with default max_classes_display (should show remark)
        edaflow.visualize_image_classes(
            data_source=temp_dir,
            samples_per_class=1,
            title="Test: Class Limiting Remark (30 → 20 classes)"
        )
        
        print("\n" + "="*60)        
        print("📊 Test: Custom limiting (30 → 10 classes)")
        print("="*60)        
        
        # Test with custom max_classes_display (should show remark)
        edaflow.visualize_image_classes(
            data_source=temp_dir,
            samples_per_class=1,
            max_classes_display=10,
            title="Test: Class Limiting Remark (30 → 10 classes)"
        )
        
        print("\n✅ All tests completed!")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up test dataset: {temp_dir}")

if __name__ == "__main__":
    main()

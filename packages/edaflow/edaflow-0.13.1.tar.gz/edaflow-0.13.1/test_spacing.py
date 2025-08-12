#!/usr/bin/env python3
"""
Test improved row spacing in visualize_image_classes
"""
import tempfile
import os
import shutil
from PIL import Image
import numpy as np
import sys

# Add the current directory to Python path
sys.path.insert(0, '.')

def create_test_data():
    """Create test data similar to user's scientific specimen data"""
    temp_dir = tempfile.mkdtemp()
    
    # Class names similar to user's scientific names
    class_names = [
        'Lycodonomorphus_rufulus',
        'Astrochromys_xylorhaga', 
        'Eretmochelys_imbricata',
        'Tintinnabulums_specialis',
        'Pantherophisus_maniensis'
    ]
    
    print(f"Creating test dataset in: {temp_dir}")
    for class_name in class_names:
        class_dir = os.path.join(temp_dir, class_name)
        os.makedirs(class_dir, exist_ok=True)
        
        # Create 6 sample images per class
        for i in range(6):
            # Create test image with some variety
            img_array = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img_path = os.path.join(class_dir, f"specimen_{i+1:02d}.png")
            img.save(img_path)
    
    return temp_dir, class_names

def main():
    temp_dir = None
    try:
        # Import edaflow
        try:
            import edaflow
            print("✅ EDAFlow imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import edaflow: {e}")
            return
        
        # Create test data
        temp_dir, class_names = create_test_data()
        
        print(f"\n🧪 Testing improved row spacing...")
        print(f"Classes: {len(class_names)} classes")
        print(f"Expected layout: 4 samples × 5 classes = 5×4 grid")
        print("="*60)
        
        # Test the improved spacing
        edaflow.visualize_image_classes(
            data_source=temp_dir,
            samples_per_class=4,  # Show 4 samples per class like user's data
            title="Row Spacing Test: Improved Layout",
            show_image_info=False
        )
        
        print("✅ Spacing test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up test data: {temp_dir}")

if __name__ == "__main__":
    main()

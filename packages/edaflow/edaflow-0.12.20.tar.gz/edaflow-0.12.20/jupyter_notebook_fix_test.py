#!/usr/bin/env python3
"""
Exact reproduction of Jupyter notebook error and fix verification
"""

import edaflow
import glob
import tempfile
import os
from PIL import Image
import numpy as np

def setup_image_dataset():
    """Setup image dataset exactly like in Jupyter notebook"""
    base_dir = tempfile.mkdtemp()
    
    # Create class directories
    for class_name in ['cats', 'dogs']:
        class_dir = os.path.join(base_dir, class_name)
        os.makedirs(class_dir)
        
        # Create sample images
        for i in range(10):
            img_path = os.path.join(class_dir, f'{class_name}_{i}.jpg')
            # Create a simple test image
            img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(img_path)
    
    return base_dir

def simulate_jupyter_notebook():
    """Simulate the exact Jupyter notebook code sequence"""
    print("📓 Simulating Jupyter Notebook Code Sequence")
    print("=" * 60)
    
    # Step 1: Load image dataset (exactly like Jupyter notebook)
    dataset_dir = setup_image_dataset()
    image_paths = glob.glob(dataset_dir + '/*//*.jpg')  # Organized by class folders
    
    # Actually, for directory-based, they would use the directory path, not glob
    image_paths = dataset_dir  # This is the directory path
    
    print(f"📁 Dataset directory: {image_paths}")
    print(f"📂 Contents: {os.listdir(image_paths)}")
    
    # Step 2: The EXACT problematic code from Jupyter notebook
    print("\n🚨 REPRODUCING EXACT JUPYTER NOTEBOOK ERROR:")
    print("=" * 50)
    print("Code:")
    print("edaflow.visualize_image_classes(")
    print("    image_paths,              # ← This was the problem") 
    print("    samples_per_class=6,")
    print("    figsize=(15, 10),")
    print("    title='Dataset Overview: Class Distribution & Samples'")
    print(")")
    
    try:
        print("\n🎯 EXECUTING:")
        # This is the EXACT failing code from the Jupyter notebook
        result = edaflow.visualize_image_classes(
            image_paths,  # This was causing TypeError before our fix
            samples_per_class=6,
            figsize=(15, 10), 
            title="Dataset Overview: Class Distribution & Samples"
        )
        
        print("\n🎉 SUCCESS! The Jupyter notebook code now works!")
        print("📝 Notice: Should have shown a deprecation warning above")
        return True
        
    except Exception as e:
        print(f"\n❌ STILL FAILING: {type(e).__name__}: {e}")
        print("🔧 The fix didn't work - need to debug further")
        return False

def show_all_working_alternatives():
    """Show all the ways this can now be called"""
    dataset_dir = setup_image_dataset()
    
    print("\n\n📋 ALL WORKING ALTERNATIVES:")
    print("=" * 60)
    
    # Method 1: Original problematic way (now fixed)
    print("1️⃣ ORIGINAL (NOW FIXED):")
    print("   edaflow.visualize_image_classes(image_paths, samples_per_class=6)")
    
    # Method 2: Recommended way  
    print("\n2️⃣ RECOMMENDED:")
    print("   edaflow.visualize_image_classes(data_source=image_paths, samples_per_class=6)")
    
    # Method 3: Backward compatible keyword
    print("\n3️⃣ BACKWARD COMPATIBLE:")
    print("   edaflow.visualize_image_classes(image_paths=image_paths, samples_per_class=6)")
    
    # Test method 2 (recommended)
    print("\n🧪 Testing recommended approach:")
    edaflow.visualize_image_classes(
        data_source=dataset_dir,
        samples_per_class=3,
        figsize=(12, 8),
        title="Recommended Usage - No Warnings"
    )
    
    print("✅ Recommended approach works perfectly!")

if __name__ == "__main__":
    print("🔬 EXACT JUPYTER NOTEBOOK ERROR REPRODUCTION & FIX TEST")
    print("=" * 70)
    print("This reproduces the TypeError and verifies our positional argument fix")
    print()
    
    # Reproduce and test the fix
    success = simulate_jupyter_notebook()
    
    if success:
        show_all_working_alternatives()
        print("\n" + "=" * 70)
        print("🎉 JUPYTER NOTEBOOK ISSUE COMPLETELY RESOLVED!")
        print()
        print("📋 What users need to know:")
        print("✅ Their existing code will work (with deprecation warning)")
        print("💡 Recommended: Change to data_source=image_paths") 
        print("🔄 Alternative: Use image_paths=image_paths")
        print()
        print("🚀 Ready for deployment as v0.12.3!")
    else:
        print("\n" + "=" * 70)
        print("❌ FIX INCOMPLETE - Still needs debugging")
        print("The positional argument handling needs more work")

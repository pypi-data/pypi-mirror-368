#!/usr/bin/env python3
"""
Test script to verify the local_binary_pattern warning fix
"""

import sys
import os
import tempfile
import numpy as np
from PIL import Image
import warnings

# Add the edaflow package to path
sys.path.insert(0, os.path.abspath('.'))

try:
    import edaflow
    from edaflow.analysis.core import analyze_image_features
    print("✅ Successfully imported edaflow")
except ImportError as e:
    print(f"❌ Failed to import edaflow: {e}")
    sys.exit(1)

print("🧪 Testing LBP warning fix...")

# Capture warnings
warnings.filterwarnings("error", message=".*local_binary_pattern.*floating-point.*")

# Create test images
with tempfile.TemporaryDirectory() as temp_dir:
    # Create class directories
    os.makedirs(os.path.join(temp_dir, 'class_a'))
    os.makedirs(os.path.join(temp_dir, 'class_b'))
    
    # Create simple test images with different patterns
    for class_name in ['class_a', 'class_b']:
        for i in range(2):
            # Create different patterns for each class
            if class_name == 'class_a':
                # Create stripes pattern
                img_array = np.zeros((64, 64, 3), dtype=np.uint8)
                img_array[::4, :, :] = 255  # White stripes
                img_array[1::4, :, :] = 128  # Gray stripes
            else:
                # Create checkerboard pattern
                img_array = np.zeros((64, 64, 3), dtype=np.uint8)
                for x in range(0, 64, 8):
                    for y in range(0, 64, 8):
                        if (x//8 + y//8) % 2 == 0:
                            img_array[y:y+8, x:x+8, :] = 200
            
            # Save image
            img = Image.fromarray(img_array)
            img_path = os.path.join(temp_dir, class_name, f'test_{i}.png')
            img.save(img_path)
    
    print("📸 Created test images")
    
    try:
        # Test with texture analysis enabled
        print("🔍 Running analyze_image_features with texture analysis...")
        
        result = analyze_image_features(
            temp_dir,
            analyze_edges=True,
            analyze_texture=True,  # This should trigger LBP without warnings
            analyze_color=True,
            analyze_gradients=True,
            create_visualizations=False,
            verbose=True
        )
        
        print("✅ SUCCESS: No LBP warnings detected!")
        print(f"📊 Analyzed {result['total_images']} images")
        print(f"🏷️ Found {result['num_classes']} classes")
        
        # Check if texture analysis was performed
        if 'texture_analysis' in result and result['texture_analysis']:
            print("🎯 Texture analysis completed successfully")
        else:
            print("⚠️ Texture analysis might not have been performed")
        
    except UserWarning as e:
        if "local_binary_pattern" in str(e) and "floating-point" in str(e):
            print(f"❌ LBP WARNING STILL PRESENT: {e}")
        else:
            print(f"⚠️ Other warning: {e}")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

print("\n🎯 LBP Warning Fix Test Complete!")

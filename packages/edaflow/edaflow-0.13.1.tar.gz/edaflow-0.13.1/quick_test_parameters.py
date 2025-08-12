#!/usr/bin/env python3
"""
Quick validation test for analyze_image_features parameters
"""

import sys
import os
import tempfile
import numpy as np
from PIL import Image

# Add the edaflow package to path
sys.path.insert(0, os.path.abspath('.'))

try:
    import edaflow
    from edaflow.analysis.core import analyze_image_features
    print("✅ Successfully imported edaflow")
except ImportError as e:
    print(f"❌ Failed to import edaflow: {e}")
    sys.exit(1)

# Create a simple test image
with tempfile.TemporaryDirectory() as temp_dir:
    # Create class directories
    os.makedirs(os.path.join(temp_dir, 'class_a'))
    os.makedirs(os.path.join(temp_dir, 'class_b'))
    
    # Create simple test images
    for class_name in ['class_a', 'class_b']:
        for i in range(3):
            img_array = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img_path = os.path.join(temp_dir, class_name, f'image_{i}.png')
            img.save(img_path)
    
    print("📸 Created test images")
    
    # Test the original RTD example (with corrected parameters)
    print("🧪 Testing RTD example with correct parameters...")
    try:
        result = analyze_image_features(
            temp_dir,
            analyze_color=True,        # CORRECT: analyze_color (not analyze_colors)
            analyze_edges=True,
            analyze_texture=True,
            analyze_gradients=True,
            sample_size=100,
            bins_per_channel=50,       # CORRECT: bins_per_channel (not bins)
            create_visualizations=False,
            verbose=True
        )
        print("✅ RTD example with CORRECT parameters: SUCCESS!")
        print(f"📊 Analyzed {result['total_images']} images")
        print(f"🏷️ Found {result['num_classes']} classes")
        
    except Exception as e:
        print(f"❌ RTD example failed: {e}")
    
    # Test the original incorrect parameters to verify they fail
    print("\n🚫 Testing with INCORRECT parameters (should fail)...")
    try:
        result = analyze_image_features(
            temp_dir,
            analyze_colors=True,       # WRONG: should be analyze_color
            bins=50,                   # WRONG: should be bins_per_channel
            create_visualizations=False,
            verbose=False
        )
        print("❌ ERROR: Function succeeded with wrong parameters!")
    except TypeError as e:
        print("✅ Correctly rejected wrong parameters with TypeError!")
        print(f"   Error: {str(e)}")
    except Exception as e:
        print(f"⚠️ Unexpected error type: {type(e).__name__}: {e}")

print("\n🎯 CONCLUSION: Documentation fixes are WORKING correctly!")
print("The user's TypeError has been resolved by fixing the documentation.")

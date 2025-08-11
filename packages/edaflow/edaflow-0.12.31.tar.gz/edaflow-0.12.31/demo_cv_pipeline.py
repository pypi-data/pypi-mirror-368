#!/usr/bin/env python3
"""
Comprehensive Computer Vision EDA Pipeline Demo
===============================================

This script demonstrates the complete edaflow computer vision EDA pipeline:
1. Image dataset visualization with visualize_image_classes()
2. Quality assessment with assess_image_quality() 
3. Feature analysis with analyze_image_features()

A complete workflow for understanding image datasets before model development.
"""

import edaflow
import numpy as np
from PIL import Image
import os
import tempfile
import shutil

def create_demo_dataset():
    """Create a comprehensive demo dataset with different visual characteristics."""
    
    # Create temporary directory structure
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Creating demo dataset in: {temp_dir}")
    
    # Create class directories
    geometric_dir = os.path.join(temp_dir, 'geometric_patterns')
    natural_dir = os.path.join(temp_dir, 'natural_textures') 
    os.makedirs(geometric_dir)
    os.makedirs(natural_dir)
    
    # Create geometric pattern images (high edge density, structured)
    print("🔺 Creating geometric pattern images...")
    for i in range(4):
        img = np.zeros((128, 128, 3), dtype=np.uint8)
        
        if i % 2 == 0:
            # Checkerboard pattern
            for y in range(0, 128, 16):
                for x in range(0, 128, 16):
                    if (x//16 + y//16) % 2 == 0:
                        img[y:y+16, x:x+16] = [255, 100, 50]  # Orange squares
                    else:
                        img[y:y+16, x:x+16] = [50, 100, 255]  # Blue squares
        else:
            # Diagonal stripes  
            for y in range(128):
                for x in range(128):
                    if (x + y) % 20 < 10:
                        img[y, x] = [255, 255, 100]  # Yellow stripes
                    else:
                        img[y, x] = [100, 255, 100]  # Green stripes
        
        pil_img = Image.fromarray(img)
        pil_img.save(os.path.join(geometric_dir, f'geometric_{i:03d}.png'))
    
    # Create natural texture images (low edge density, gradual changes)
    print("🌿 Creating natural texture images...")
    for i in range(4):
        img = np.zeros((128, 128, 3), dtype=np.uint8)
        
        if i % 2 == 0:
            # Smooth radial gradient
            center_x, center_y = 64, 64
            for y in range(128):
                for x in range(128):
                    distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                    intensity = max(0, 255 - distance * 2)
                    img[y, x] = [intensity, intensity * 0.8, intensity * 0.6]
        else:
            # Smooth noise-like pattern
            np.random.seed(42 + i)  # Reproducible
            for y in range(128):
                for x in range(128):
                    # Create smooth varying pattern
                    r = 100 + 50 * np.sin(x * 0.1) * np.cos(y * 0.1)
                    g = 120 + 40 * np.sin(x * 0.15) * np.sin(y * 0.1) 
                    b = 80 + 60 * np.cos(x * 0.1) * np.sin(y * 0.15)
                    img[y, x] = [max(0, min(255, int(r))), 
                                max(0, min(255, int(g))), 
                                max(0, min(255, int(b)))]
        
        pil_img = Image.fromarray(img)
        pil_img.save(os.path.join(natural_dir, f'natural_{i:03d}.png'))
    
    return temp_dir

def run_complete_cv_eda_pipeline():
    """Run the complete Computer Vision EDA pipeline."""
    
    print("🎨 EDAFLOW COMPUTER VISION EDA PIPELINE DEMO")
    print("=" * 60)
    
    # Create demo dataset
    demo_dir = create_demo_dataset()
    
    try:
        print(f"\n📊 STEP 1: IMAGE DATASET VISUALIZATION")
        print("-" * 45)
        
        # Visualize image classes
        print("   📊 Visualizing image classes and getting statistics...")
        edaflow.visualize_image_classes(
            demo_dir,
            samples_per_class=3,
            figsize=(12, 8)
        )
        
        print(f"\n🔍 STEP 2: IMAGE QUALITY ASSESSMENT")
        print("-" * 42)
        
        # Assess image quality
        quality_report = edaflow.assess_image_quality(
            demo_dir,
            verbose=True
        )
        
        print(f"\n🎯 STEP 3: IMAGE FEATURE ANALYSIS")
        print("-" * 40)
        
        # Analyze image features
        feature_report = edaflow.analyze_image_features(
            demo_dir,
            analyze_edges=True,
            analyze_texture=True,
            analyze_color=True,
            analyze_gradients=True,
            create_visualizations=False,  # Skip for demo
            verbose=True
        )
        
        print(f"\n🎉 COMPLETE PIPELINE RESULTS")
        print("=" * 35)
        
        # Summary insights
        print(f"📈 Dataset Overview:")
        print(f"   • Total Images: 8")
        print(f"   • Classes: 2 (geometric_patterns, natural_textures)")
        print(f"   • Perfect Balance: 4 images per class")
        
        print(f"\n🔍 Quality Analysis:")
        print(f"   • Quality Score: {quality_report['quality_score']}/100") 
        print(f"   • Corrupted Images: {len(quality_report['corrupted_images'])}")
        print(f"   • Recommendations: {len(quality_report['recommendations'])}")
        
        print(f"\n🎨 Feature Analysis:")
        print(f"   • Classes Analyzed: {feature_report['num_classes']}")
        print(f"   • Feature Rankings: {len(feature_report['feature_rankings'])}")
        
        if feature_report['feature_rankings']:
            top_feature = feature_report['feature_rankings'][0]
            print(f"   • Top Discriminative Feature: {top_feature[0]} (score: {top_feature[1]:.3f})")
        
        print(f"\n💡 Key Insights:")
        
        # Quality insights
        for insight in quality_report['recommendations'][:2]:
            print(f"   🔍 {insight}")
        
        # Feature insights  
        for insight in feature_report['recommendations'][:2]:
            print(f"   🎯 {insight}")
        
        print(f"\n✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"🚀 Ready for informed computer vision model development!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        shutil.rmtree(demo_dir, ignore_errors=True)
        print(f"\n🧹 Demo dataset cleaned up")

if __name__ == "__main__":
    print("🎨 EDAFLOW v0.11.0 - Complete Computer Vision EDA Suite")
    print("🔧 Testing the full pipeline: Visualization + Quality + Features")
    print()
    
    success = run_complete_cv_eda_pipeline()
    
    if success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✨ The complete Computer Vision EDA pipeline is ready!")
        print(f"📚 Visit https://edaflow.readthedocs.io for full documentation")
    else:
        print(f"\n💥 TESTS FAILED!")
        print(f"🔧 Please check the implementation")

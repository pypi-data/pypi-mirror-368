#!/usr/bin/env python3
"""
Quick test to verify visualization fix is working.
"""

import edaflow

print("🧪 Testing Visualization Fix - v0.12.12")
print("=" * 50)

try:
    # Test the function with typical parameters that would cause skipping before
    print("\n📋 Testing with parameters that previously caused skipping...")
    print("Parameters: samples_per_class=6, auto_skip_threshold=80")
    
    # This should now show visualization with smart downsampling
    result = edaflow.visualize_image_classes(
        data_source='img_path',  # Assuming this directory exists from your screenshot
        samples_per_class=6,
        show_class_counts=True,
        return_stats=True
    )
    
    if result:
        print(f"\n✅ SUCCESS: Function returned statistics")
        print(f"   📊 Classes: {result.get('num_classes', 'N/A')}")
        print(f"   🖼️  Samples: {result.get('total_samples', 'N/A')}")
    else:
        print("❌ Function returned None")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n🎯 Expected behavior:")
print("- Should see 'Smart downsampling' or 'Auto-downsampling' messages")
print("- Should see '✅ Image classification EDA completed!'")
print("- Should NOT see '🚫 Visualization skipped' messages")
print("- All classes should be visualized")

#!/usr/bin/env python3
"""
Test script to verify the visualization fix works correctly.
This should now ALWAYS show visualization with smart downsampling.
"""

import edaflow

# Test with the same data that was skipping before
print("🧪 Testing visualization fix...")
print("=" * 50)

# This should now work with smart downsampling instead of skipping
result = edaflow.visualize_image_classes(
    data_source='img_path',  # Your image directory
    samples_per_class=6,     # Show 6 examples per class  
    show_class_counts=True,  # Display class distribution
    return_stats=True        # Get statistics back
)

print("\n📊 Test Results:")
if result:
    print(f"✅ Total classes: {result['num_classes']}")
    print(f"✅ Total samples: {result['total_samples']}")
    print(f"✅ Balance ratio: {result['balance_ratio']:.2f}")
else:
    print("❌ No statistics returned")

print("\n🎯 Expected Behavior:")
print("- Should show visualization with smart downsampling")
print("- Should NOT skip visualization")
print("- Should display '✅ Visualization optimized' message")
print("- All classes should be visible")

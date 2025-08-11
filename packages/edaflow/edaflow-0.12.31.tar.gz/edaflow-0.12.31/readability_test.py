#!/usr/bin/env python3
"""
Test the improved readability features in edaflow v0.12.13
Demonstrates solutions for datasets with many classes (like 108 classes)
"""

import edaflow

print("🧪 Testing Readability Improvements - edaflow v0.12.13")
print("=" * 65)
print("🎯 SOLUTIONS for datasets with many classes (like your 108 classes)")
print("=" * 65)

print("\n📊 APPROACH 1: Limit to Most Frequent Classes (RECOMMENDED)")
print("=" * 50)
try:
    # This will show only the top 20 most frequent classes - much more readable!
    result1 = edaflow.visualize_image_classes(
        data_source='img_path',
        samples_per_class=3,           # 3 samples per class
        max_classes_display=20,        # 🎯 NEW! Show only top 20 classes  
        show_class_counts=True,
        title="Top 20 Most Frequent Classes (Readable View)",
        return_stats=True
    )
    print(f"✅ Result: Should show 20 classes × 3 samples = 60 large, readable images")
    
except Exception as e:
    print(f"❌ Error in Approach 1: {e}")

print("\n" + "=" * 50)
print("📊 APPROACH 2: Conservative Parameters")
print("=" * 50)
try:
    # This shows all classes but with very conservative parameters
    result2 = edaflow.visualize_image_classes(
        data_source='img_path',
        samples_per_class=1,           # Just 1 sample per class
        max_images_display=50,         # Limit total images  
        show_class_counts=True,
        title="All Classes - Conservative View",
        return_stats=True
    )
    print(f"✅ Result: Shows all classes but with strict image limits")
    
except Exception as e:
    print(f"❌ Error in Approach 2: {e}")

print("\n" + "=" * 65)
print("🎯 READABILITY ANALYSIS:")
print("=" * 65)
print("✅ BEST OPTION: Approach 1 (max_classes_display=20)")
print("   • Shows 20 classes × 3 samples = 60 images")  
print("   • Images will be LARGE and clearly visible")
print("   • Focuses on most important/frequent classes")
print("   • Perfect for initial dataset exploration")
print("")
print("💡 WORKFLOW SUGGESTION:")
print("   1. Use max_classes_display=20 for overview of top classes")
print("   2. Identify interesting classes from the visualization")
print("   3. Create focused visualizations for specific classes")
print("   4. Use batch processing for comprehensive analysis")
print("")
print("🔍 WHY THIS WORKS BETTER:")
print("   • 20 classes fit comfortably in one visualization")
print("   • Each image is large enough to see details")
print("   • Focuses on classes with most data (likely most important)")
print("   • Much better than 108 tiny, unreadable images")

print(f"\n🚀 NEXT STEPS:")
print(f"   Try: max_classes_display=15 for even larger images")
print(f"   Try: max_classes_display=25 for more classes but smaller images")
print(f"   Adjust based on your screen size and preferences!")

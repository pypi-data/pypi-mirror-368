#!/usr/bin/env python3
"""
SOLUTION: Readability-focused visualization for large class datasets
Perfect for your 108-class dataset issue!
"""

import edaflow

print("🎯 SOLUTION: Readability-First Approach for Large Class Datasets")
print("=" * 70)
print("Problem: 108 classes × 1 sample = 108 tiny, unreadable images")
print("Solution: Show only top 20 classes with larger, readable images")  
print("=" * 70)

try:
    print("\n� APPLYING FIX: max_classes_display=20")
    print("This will show only the 20 most frequent classes...")
    
    # THE SOLUTION: Limit classes for readability
    result = edaflow.visualize_image_classes(
        data_source='img_path',
        samples_per_class=3,          # 3 samples per class (larger images)
        max_classes_display=20,       # 🎯 GAME CHANGER! Only show top 20 classes
        show_class_counts=True,
        title="Top 20 Classes - Readable View",
        return_stats=True
    )
    
    print("\n✅ EXPECTED RESULT:")
    print("   📊 20 classes × 3 samples = 60 images total")
    print("   🔍 Each image will be MUCH larger and clearly visible")
    print("   🎯 Focuses on your most important/frequent classes")
    print("   💡 Perfect for initial dataset exploration!")
    
    if result:
        print(f"\n📈 DATASET STATS:")
        print(f"   • Original classes: {result.get('num_classes', 'N/A')} (filtered from full dataset)")
        print(f"   • Total samples: {result.get('total_samples', 'N/A')}")
        print(f"   • Balance ratio: {result.get('balance_ratio', 'N/A'):.2f}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print(f"\n🎯 WHY THIS WORKS BETTER:")
print(f"   ❌ Before: 108 classes = tiny, unreadable images")
print(f"   ✅ After:  20 classes = large, clearly visible images")
print(f"   📊 Shows your most frequent/important classes first")
print(f"   🔍 Each image is big enough to actually see details!")

print(f"\n💡 CUSTOMIZATION OPTIONS:")
print(f"   • max_classes_display=15 → Even larger images")
print(f"   • max_classes_display=25 → More classes, slightly smaller images")  
print(f"   • max_classes_display=30 → Balance between coverage and size")

print(f"\n🚀 WORKFLOW RECOMMENDATION:")
print(f"   1. Use max_classes_display=20 for overview")
print(f"   2. Identify interesting classes from readable visualization")
print(f"   3. Create focused visualizations for specific classes")
print(f"   4. Repeat for other class batches if needed")

print(f"\n✨ TRY IT NOW:")
print(f"   Replace your current call with:")
print(f"   edaflow.visualize_image_classes(")
print(f"       'img_path',")
print(f"       samples_per_class=3,")
print(f"       max_classes_display=20  # ← ADD THIS!")
print(f"   )")
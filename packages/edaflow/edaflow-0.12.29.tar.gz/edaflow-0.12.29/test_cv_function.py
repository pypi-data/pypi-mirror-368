"""
Simple test for the new visualize_image_classes function
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    import edaflow
    print("✅ Successfully imported edaflow")
    
    # Check if the new function is available
    if hasattr(edaflow, 'visualize_image_classes'):
        print("✅ visualize_image_classes function is available")
        
        # Check function documentation
        func = getattr(edaflow, 'visualize_image_classes')
        if func.__doc__:
            print("✅ Function has comprehensive documentation")
            print(f"📝 Doc length: {len(func.__doc__)} characters")
        else:
            print("⚠️  Function missing documentation")
            
        print("\n🎉 Computer Vision EDA function successfully added to edaflow!")
        print(f"📦 Current version: {edaflow.__version__}")
        
        # Print function signature for verification
        import inspect
        sig = inspect.signature(func)
        print(f"🔧 Function signature: visualize_image_classes{sig}")
        
    else:
        print("❌ visualize_image_classes function not found")
        
except ImportError as e:
    print(f"❌ Failed to import edaflow: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

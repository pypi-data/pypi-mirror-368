# 🔧 edaflow v0.12.1 - Fix for visualize_image_classes() TypeError

## 🚨 The Problem
Your colleague encountered this error:
```
TypeError: visualize_image_classes() got an unexpected keyword argument 'image_paths'
```

## ✅ The Solution
**edaflow v0.12.1** now supports backward compatibility! 

### Quick Fix for Your Colleague:
```bash
pip install --upgrade edaflow
```

Their existing code will now work without any changes:
```python
# This now works (shows a deprecation warning)
edaflow.visualize_image_classes(
    image_paths=eda_images,      # ← OLD parameter name - still works!
    samples_per_class=6,
    figsize=(15, 10),
    title="Dataset Overview"
)
```

### Recommended Code Update:
For clean code without warnings, update to use the new parameter name:
```python
# Recommended approach (no warnings)
edaflow.visualize_image_classes(
    data_source=eda_images,      # ← NEW parameter name
    samples_per_class=6,
    figsize=(15, 10), 
    title="Dataset Overview"
)
```

## 🔄 What Changed
- ✅ **v0.12.0**: Changed `image_paths` → `data_source` (breaking change)
- ✅ **v0.12.1**: Added backward compatibility support
- ✅ Both parameter names now work
- ⚠️  `image_paths` shows deprecation warning
- ✅ `data_source` is the recommended approach

## 📦 Available Now
- **PyPI**: https://pypi.org/project/edaflow/0.12.1/
- **Install**: `pip install --upgrade edaflow==0.12.1`
- **Status**: Fully deployed and tested

## 🧪 Verification
The fix has been tested with the exact error scenario and confirmed working.

---
*Generated: edaflow v0.12.1 Emergency Patch Release*

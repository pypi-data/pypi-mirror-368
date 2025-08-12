# Release Checklist - edaflow v0.13.1

## Pre-Release Verification

### ✅ Code Changes
- [x] Theme detection fix implemented in `display.py`
- [x] Dynamic `_detect_colab_theme()` function with environment variable support
- [x] Enhanced CSS with media queries for auto-theme detection
- [x] Documentation overselling language removed

### ✅ Version Updates
- [x] `pyproject.toml` version: 0.13.0 → 0.13.1
- [x] `edaflow/__init__.py` version: 0.13.0 → 0.13.1
- [x] `CHANGELOG.md` updated with v0.13.1 entry

### ✅ Documentation
- [x] CHANGELOG.md updated with factual language
- [x] Major documentation overselling violations fixed
- [x] Theme detection fix documented
- [x] Documentation policy framework created

### ✅ Policy Framework (New)
- [x] DOCUMENTATION_POLICY.md created
- [x] check_documentation_language.py implemented
- [x] DOCUMENTATION_REVIEW_TEMPLATE.md created
- [x] POLICY_IMPLEMENTATION_GUIDE.md created

### ✅ Testing
- [x] Theme detection test created and verified
- [x] Dynamic behavior confirmed (not hardcoded)
- [x] Documentation language checker functional

## Release Summary

**Version**: 0.13.1
**Type**: Bug fix + policy improvement
**Date**: August 12, 2025

### Fixed
- Theme detection hardcoded to 'light' → Dynamic environment-aware detection
- Google Colab dark mode compatibility improved
- Documentation overselling language toned down

### Added  
- Complete documentation policy framework
- Automated language checking tools
- Review templates and implementation guides

### Impact
- Better user experience in dark-themed notebooks
- Realistic expectations set in documentation
- Framework to prevent future overselling

## Release Commands

### 1. Final Testing
```bash
python test_dynamic_theme_detection.py
python check_documentation_language.py README.md CHANGELOG.md
```

### 2. Build Package
```bash
pip install build twine
python -m build
```

### 3. Upload to PyPI
```bash
twine check dist/edaflow-0.13.1*
twine upload dist/edaflow-0.13.1*
```

### 4. Git Release
```bash
git add .
git commit -m "Release v0.13.1: Fix theme detection and implement documentation policy"
git tag v0.13.1
git push origin main --tags
```

## Post-Release
- [ ] Verify PyPI upload successful
- [ ] Test pip install from PyPI
- [ ] Update GitHub release notes
- [ ] Monitor for user feedback

---

**Release Philosophy**: This release demonstrates our commitment to honest communication and user trust through the "underpromise, overdeliver" approach.

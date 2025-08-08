# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.12.22] - 2025-08-08

### Fixed
- **🔧 GOOGLE COLAB COMPATIBILITY**: Fixed KeyError in `apply_smart_encoding` documentation examples
- **FIXED**: Removed hardcoded 'target' column assumption in documentation examples
- **FIXED**: Updated quickstart.rst and README.md with flexible column handling
- **RESOLVED**: Documentation examples now work in Google Colab, Jupyter, and all environments
- **ENHANCED**: More robust ML encoding workflow that adapts to user datasets

### Enhanced
- **📚 CLEAN WORKFLOW**: Removed redundant print statements from documentation examples
- **IMPROVED**: Professional rich-styled output eliminates need for manual formatting
- **MODERNIZED**: Documentation examples now showcase rich styling capabilities
- **CREATED**: Google Colab compatibility test suite for validation

## [0.12.21] - 2025-08-08

### Fixed
- **🔧 DOCUMENTATION PARAMETER FIXES**: Corrected parameter name mismatches in `visualize_scatter_matrix` documentation
- **FIXED**: Changed `regression_line` → `regression_type` in README.md and quickstart.rst examples
- **FIXED**: Changed `diagonal_type` → `diagonal` in documentation examples
- **FIXED**: Changed `upper_triangle`/`lower_triangle` → `upper`/`lower` parameter names
- **FIXED**: Changed `color_column` → `color_by` in documentation examples
- **RESOLVED**: TypeError when using sample code from documentation
- **ENHANCED**: All documentation examples now match actual function signature

## [0.12.20] - 2025-08-08

### Enhanced 
- **🌈 COMPREHENSIVE RICH STYLING**: Enhanced ALL major EDA functions with vibrant, professional output
- **ENHANCED MISSING DATA ANALYSIS**: `check_null_columns` now features:
  - Rich tables with color-coded severity levels (✅ CLEAN, ⚠️ MINOR, 🚨 WARNING, 💀 CRITICAL)
  - Data integrity indicators with health assessment panels
  - Smart recommendations based on missing data patterns
  - Professional summary with overall dataset health scoring
- **ADVANCED COLUMN CLASSIFICATION**: `display_column_types` now includes:
  - Side-by-side rich tables for categorical vs numerical columns
  - Memory usage analysis with optimization recommendations
  - Data type insights and composition analysis
  - Range information and advanced metrics for better understanding
- **PROFESSIONAL IMPUTATION REPORTING**: `impute_numerical_median` enhanced with:
  - Detailed imputation tables showing before/after status
  - Smart value formatting (K/M notation for large numbers)
  - Color-coded success indicators and completion rates
  - Rich summary panels with actionable insights

### Previous Enhancements (v0.12.19)
- **VIBRANT CATEGORICAL ANALYSIS**: `analyze_categorical_columns` rich styling
- **COLORFUL DATA TYPE CONVERSION**: `convert_to_numeric` professional output

### Dependencies
- **MAINTAINED**: `rich>=13.0.0` for enhanced terminal output formatting

## [Unreleased]

### Added

## [0.12.19] - 2025-08-08

### Enhanced
- **VIBRANT CATEGORICAL ANALYSIS**: Completely redesigned `analyze_categorical_columns` output with rich styling
  - Professional tables with color-coded status indicators (✅ GOOD, ⚠️ MANY, 🚨 HIGH cardinality)  
  - Visual separation between potentially numeric vs truly categorical columns
  - Smart cardinality warnings with recommendations
  - Beautiful summary panels with emoji icons and statistics
- **COLORFUL DATA TYPE CONVERSION**: Enhanced `convert_to_numeric` with rich, dynamic output
  - Professional conversion tables showing before/after status for each column
  - Color-coded actions: ✅ CONVERTED, ⚠️ SKIPPED, 📊 ALREADY NUMERIC
  - Detailed summary panels with conversion statistics and threshold information
  - Visual progress indicators and conversion details table
  - Maintains backward compatibility with fallback to plain output if rich is unavailable
  - Graceful fallback to basic styling if rich library unavailable

### Dependencies
- **NEW**: Added `rich>=13.0.0` dependency for enhanced terminal output formatting

## [Unreleased]

### Added

## [0.12.17] - 2025-08-07

### Fixed
- **CRITICAL DOCUMENTATION FIX**: Corrected parameter names in all documentation
  - Updated function docstring: `image_path_column` → `image_column`, `class_column` → `label_column`
  - Fixed quickstart guide: `max_classes` → `max_classes_display` (7 instances)
  - Fixed README examples: corrected column parameter names (5 instances)
  - Fixed index page: `max_classes` → `max_classes_display`
  - This resolves TypeError when users follow documentation examples

## [0.12.16] - 2025-08-07

### Fixed
- **ROW OVERLAP RESOLUTION**: Eliminated overlapping rows in `visualize_image_classes` multi-row layouts
- **IMPROVED SPACING**: Increased hspace values (0.45-0.6 from 0.3-0.4) for better row separation
- **SCIENTIFIC NAME SUPPORT**: Enhanced layout specifically optimized for long taxonomic/scientific class names
- **PROFESSIONAL LAYOUTS**: Clean separation between class titles and images in dense visualizations

### Improved
- Font sizing optimization: slightly smaller subplot titles for tighter vertical spacing
- Reduced title padding (6px from 8px) to minimize title height interference
- Enhanced bottom margin (0.12 from 0.08) for better class limiting remark positioning
- Better scalability from small datasets (5 classes) to large datasets (100+ classes)

## [0.12.15] - 2025-08-07

### Added
- **CLASS LIMITING TRANSPARENCY**: Added informative remark beneath visualizations when class limiting is applied
- **SMART USER GUIDANCE**: Shows "X of Y total classes (Z not displayed for optimal readability)" with actionable instructions
- **CONTEXT AWARENESS**: Users always understand they're seeing a curated subset of their dataset
- **PROFESSIONAL STYLING**: Subtle gray styling with rounded box that doesn't compete with main visualization

### Improved
- Enhanced transparency in `visualize_image_classes` when `max_classes_display` parameter limits displayed classes
- Better user experience with clear guidance on how to show all classes if desired

## [0.12.14] - 2025-08-07

### Fixed
- **TITLE SPACING IMPROVEMENTS**: Generous margins eliminate title overlap issues across all figure sizes
- **PROFESSIONAL LAYOUTS**: Publication-ready spacing with 15-18% buffer between titles and subplots  
- **DYNAMIC POSITIONING**: Height-based title positioning (0.96-0.98 y-position) for optimal appearance
- **VISUAL EXCELLENCE**: Enhanced `visualize_image_classes` with professional spacing standards

### Changed
- More conservative top margins: 0.82-0.88 (vs previous 0.88-0.92) for better title clearance
- Improved title positioning algorithm based on figure height for consistent professional appearance

## [0.12.11] - 2025-08-07

### Fixed
- **COMPLETE VISUALIZATION FIX**: Fully resolved "visualization skipped due to dataset size" issue in `visualize_image_classes`
- **SMART DOWNSAMPLING**: Implemented complete smart downsampling that always shows images instead of skipping
- **ALWAYS DISPLAY**: Function now never skips visualization - always shows something meaningful
- **ENHANCED UX**: Eliminated all frustrating "visualization skipped" messages for better user experience

## [0.12.10] - 2025-08-07

### Fixed
- **IMPROVED DEFAULTS**: Updated default parameters for better user experience (auto_skip_threshold and max_images_display now 80)
- **PARTIAL VISUALIZATION FIX**: Reduced skipping behavior through better parameter defaults
- **PREPARATION**: Set foundation for complete smart downsampling implementation

## [0.12.9] - 2025-08-07

### Changed
- **UX IMPROVEMENT**: Major enhancement attempt for `visualize_image_classes` with smart downsampling
- **PARAMETER CONSISTENCY**: Both CV functions now use consistent parameter names and defaults
- **BETTER FEEDBACK**: Clear user messages about adjustments made to visualization

## [Unreleased]

### Added

## [0.12.8] - 2025-08-06

### Fixed
- **CRITICAL BUG FIX**: Fixed KeyError: 'target' not found in axis error in `apply_smart_encoding()` function
- **TARGET COLUMN VALIDATION**: Added proper validation for target column existence before accessing DataFrame
- **GRACEFUL FALLBACK**: Function now gracefully falls back to frequency encoding when target column is missing
- **IMPROVED ERROR HANDLING**: Added informative warning messages for missing target column scenarios
- **USER EXPERIENCE**: Enhanced function robustness to prevent crashes when target column doesn't exist

## [0.12.7] - 2025-08-06

### Added
- **COMPREHENSIVE DOCUMENTATION**: Complete documentation synchronization across PyPI and ReadTheDocs platforms
- **SMART ENCODING INTEGRATION**: Added Smart Encoding functions to complete EDA workflow documentation
- **RTD ENHANCEMENT**: Enhanced ReadTheDocs quickstart guide with Smart Encoding section and examples
- **WORKFLOW INTEGRATION**: Smart Encoding now properly integrated as Step 12 in complete 13-step EDA workflow
- **PARAMETER CONSISTENCY**: Standardized parameter examples across all documentation platforms

### Improved
- **DOCUMENTATION ACCURACY**: Corrected parameter names (max_cardinality_onehot, max_cardinality_target) across all docs
- **USER EXPERIENCE**: Consistent examples and function signatures between README and RTD documentation
- **FUNCTION COUNT**: Updated from 16 to 18 functions in all documentation to reflect Smart Encoding additions
- **CODE EXAMPLES**: Comprehensive Smart Encoding examples with practical parameter values
- **PLATFORM CONSISTENCY**: Synchronized information across PyPI README, RTD quickstart, and main index pages

### Fixed
- **LEGACY COMPATIBILITY**: Added `max_cardinality` parameter alias in `analyze_encoding_needs()` for backward compatibility
- **PARAMETER CONFUSION**: Resolved TypeError issues caused by parameter naming inconsistencies
- **DOCUMENTATION GAPS**: Filled missing Smart Encoding information in complete workflow documentation

## [0.12.6] - 2025-08-06

### Added
- **SMART VISUALIZATION**: Intelligent handling of large image datasets in `visualize_image_classes()`
- **AUTO-SKIP THRESHOLD**: Automatically skip visualization for datasets with 200+ images to prevent unreadable plots
- **IMAGE LIMIT CONTROL**: New `max_images_display` parameter to limit total images shown for readability
- **FORCE DISPLAY OPTION**: New `force_display` parameter to override auto-skip behavior when needed
- **DYNAMIC SIZING**: Smart figure and font size adjustments based on dataset size
- **HELPFUL WARNINGS**: Clear guidance when visualizations might be hard to read due to size

### Improved
- **GRID LAYOUTS**: Better automatic grid layout calculations for large datasets
- **FONT SCALING**: Dynamic font sizes that scale appropriately with image count
- **USER GUIDANCE**: Comprehensive suggestions for handling large datasets effectively
- **DOCUMENTATION**: Added examples for large dataset scenarios and parameter usage

### Technical Details
- Images are limited to 50 total by default for optimal readability
- Datasets with 200+ images auto-skip visualization (customizable via `auto_skip_threshold`)
- Smart warnings at 50+ images with optimization suggestions
- Improved grid layouts prevent overlapping and unreadable content

## [0.12.5] - 2025-08-06

### Fixed
- **CRITICAL**: Fixed corrupted image display in `visualize_image_classes()` visualization output
- **BUG FIX**: Resolved PIL Image to matplotlib incompatibility causing garbled/unacceptable visualizations
- **FUNCTIONALITY**: Converted PIL Image objects to numpy arrays for proper matplotlib display
- **DISPLAY**: Images now render correctly in visualizations instead of corrupted content
- **COMPATIBILITY**: Enhanced image processing pipeline for matplotlib.imshow() requirements

## [0.12.4] - 2025-08-06

### Fixed
- **CRITICAL**: Fixed `visualize_image_classes()` not supporting list of image paths from `glob.glob()`
- **BUG FIX**: Resolved TypeError "data_source must be either a directory path (str) or pandas DataFrame" when using `glob.glob()` results
- **FUNCTIONALITY**: Added proper support for list input type in `visualize_image_classes()` function
- **IMPLEMENTATION**: Added `_parse_image_path_list()` helper function to handle file path lists
- **USABILITY**: Function now supports all three input types: directory paths (str), file lists (list), and DataFrames
- **DOCUMENTATION**: Updated function signature and examples to show list support
- **CONSISTENCY**: Aligned function behavior with documentation examples that use `glob.glob()`

### Enhanced  
- **ERROR MESSAGES**: Improved error messages to clearly indicate all supported input types
- **VALIDATION**: Enhanced input validation with better type checking and error reporting
- **EXAMPLES**: Added comprehensive list-based analysis example in function docstring

### Technical Details
- **INPUT TYPES**: Now accepts `Union[str, List[str], pd.DataFrame]` for `data_source` parameter  
- **CLASS DETECTION**: Automatically extracts class names from parent directory names in file paths
- **FILE VALIDATION**: Validates file existence and skips non-existent paths with warnings
- **BACKWARD COMPATIBILITY**: Maintains full compatibility with existing directory and DataFrame workflows

### Added
- Future features will be documented here

### Changed
- Future changes will be documented here

### Deprecated
- Future deprecations will be documented here

### Removed
- Future removals will be documented here

## [0.12.3] - 2025-08-06 - Complete Positional Argument Compatibility Fix 🔧

### Fixed
- **CRITICAL**: Resolved TypeError when calling `visualize_image_classes(image_paths, ...)` with positional arguments
- **Positional Arguments**: Function now properly handles legacy positional argument usage from Jupyter notebooks
- **Backward Compatibility**: Complete support for all three usage patterns:
  1. `visualize_image_classes(path, ...)` - Positional (deprecated, shows warning)  
  2. `visualize_image_classes(image_paths=path, ...)` - Keyword deprecated (shows warning)
  3. `visualize_image_classes(data_source=path, ...)` - Recommended (no warning)

### Improved
- **User Experience**: Clear deprecation warnings guide users toward recommended `data_source=` syntax
- **Function Architecture**: Refactored to wrapper function pattern for robust argument handling
- **Error Messages**: Enhanced error messages provide clear guidance for parameter usage
- **Documentation**: Updated examples showing all supported usage patterns

### Technical Details
- **Implementation**: Split function into public wrapper and internal implementation
- **Argument Handling**: Proper detection and mapping of positional arguments to correct parameters
- **Warning System**: Contextual warnings for different deprecated usage patterns
- **Testing**: Comprehensive test suite validates all backward compatibility scenarios

### Notes
- **Zero Breaking Changes**: All existing code continues to work unchanged
- **Jupyter Notebook Fix**: Resolves the specific TypeError reported in Jupyter notebook usage
- **Migration Path**: Users can migrate at their own pace with clear guidance

## [0.12.3] - 2025-08-06 - Complete Backward Compatibility Fix 🔧

### Fixed
- **Critical Issue**: Resolved TypeError when calling `visualize_image_classes()` with positional arguments
- **Positional Arguments**: Added support for legacy positional syntax: `visualize_image_classes(image_paths, ...)`
- **Function Wrapper**: Implemented comprehensive argument handling to catch all usage patterns

### Enhanced
- **Complete Compatibility**: Now supports all three calling patterns:
  1. Positional: `visualize_image_classes(path, samples_per_class=6)` (shows deprecation warning)
  2. Deprecated keyword: `visualize_image_classes(image_paths=path, samples_per_class=6)` (shows deprecation warning)
  3. Recommended: `visualize_image_classes(data_source=path, samples_per_class=6)` (no warning)
- **Clear Warnings**: Improved deprecation messages with specific migration guidance
- **Educational Value**: Users learn correct API patterns while maintaining backward compatibility

### Documentation
- **Updated Examples**: All README code examples now use recommended `data_source=` parameter
- **User Education**: Ensures new users learn modern API patterns from documentation
- **Migration Guidance**: Clear examples of all supported usage patterns

### Technical Implementation
- **Function Wrapper**: Created wrapper function with `*args, **kwargs` to properly handle positional arguments
- **Internal Implementation**: Separated logic into `_visualize_image_classes_impl()` for clean architecture
- **Comprehensive Testing**: Validated all three usage patterns with proper warning behavior

### Notes
- **Zero Breaking Changes**: All existing code continues to work unchanged
- **Performance**: No performance impact - wrapper adds minimal overhead
- **Future-Proof**: Clean architecture supports future parameter evolution

## [0.12.2] - 2025-08-06 - Documentation Refresh 📚

### Improved
- **Documentation**: Enhanced README.md with updated timestamps and current version indicators
- **PyPI Display**: Forced PyPI cache refresh to ensure current changelog information is displayed
- **Visibility**: Added latest updates indicator to changelog section for better user awareness
- **Metadata**: Updated version indicators throughout documentation files

### Fixed
- **PyPI Cache**: Resolved issue where PyPI was displaying outdated changelog (showing v0.11.0 instead of current releases)
- **Documentation Sync**: Ensured all documentation platforms display consistent current version information

### Notes
- **No Functional Changes**: All code functionality identical to v0.12.1 - purely documentation improvements
- **Compatibility**: Maintains full backward compatibility from v0.12.1 patch

## [0.12.1] - 2025-08-06 - Backward Compatibility Patch 🔧

### Fixed
- **Backward Compatibility**: Added support for deprecated `image_paths` parameter in `visualize_image_classes()`
  - Function now accepts both `data_source` (recommended) and `image_paths` (deprecated) parameters
  - Shows deprecation warning when `image_paths` is used to encourage migration to `data_source`
  - Prevents using both parameters simultaneously to avoid confusion
  - Resolves TypeError for users calling with `image_paths=` parameter

### Enhanced  
- Improved error messages for parameter validation in image visualization functions
- Added comprehensive parameter documentation including deprecation notices

## [0.12.0] - 2025-08-06 - Machine Learning Preprocessing Release 🤖

### Added
- `analyze_encoding_needs()` function for intelligent categorical encoding strategy analysis
  - Automatic cardinality analysis for optimal encoding method selection
  - Target correlation analysis for supervised encoding recommendations
  - Memory impact assessment for high-cardinality features
  - Support for 7 different encoding strategies: One-Hot, Target, Ordinal, Binary, TF-IDF, Text, and Keep Numeric
  - Beautiful emoji-rich output with detailed recommendations and summaries
  
- `apply_smart_encoding()` function for automated categorical variable transformation
  - Intelligent preprocessing pipeline with automatic analysis integration
  - Memory-efficient handling of high-cardinality categorical variables
  - Support for scikit-learn encoders: OneHotEncoder, TargetEncoder, OrdinalEncoder
  - TF-IDF vectorization for text features with customizable parameters
  - Binary encoding for medium cardinality features to optimize memory usage
  - Graceful handling of unknown categories with configurable strategies
  - Comprehensive progress tracking with emoji-rich status updates
  - Automatic shape transformation reporting (columns before/after)

### Enhanced
- Package now includes comprehensive ML preprocessing capabilities alongside EDA functions
- Total function count increased from 18 to 20 with new encoding suite
- Improved integration with scikit-learn ecosystem for end-to-end ML workflows
- Enhanced documentation with ML preprocessing examples and use cases

### Dependencies
- Added scikit-learn integration for advanced encoding transformations
- Maintained backward compatibility with existing EDA functionality
- All new features include graceful fallbacks if optional dependencies unavailable

## [0.11.0] - 2025-01-30 - Image Feature Analysis Release 🎨

### Added
- `analyze_image_features()` function for deep statistical analysis of visual features
- Edge density analysis using Canny, Sobel, and Laplacian edge detection methods  
- Texture analysis with Local Binary Patterns (LBP) for pattern characterization
- Color histogram analysis across RGB, HSV, LAB, and grayscale color spaces
- Gradient magnitude and direction analysis for understanding image structure
- Feature ranking system to identify most discriminative features between classes
- Statistical comparison framework for quantifying inter-class visual differences
- Comprehensive visualization suite with box plots for feature distributions
- Automated recommendation system for feature engineering and preprocessing decisions
- Production-ready feature extraction with optional raw feature vector export
- OpenCV and scikit-image integration with graceful fallback mechanisms
- Support for custom analysis parameters (LBP radius, edge thresholds, color spaces)

### Enhanced
- Expanded edaflow from 16 to 17 comprehensive EDA functions
- Complete computer vision EDA trinity: Visualization + Quality + Features
- Advanced dependency handling for optimal performance with available libraries

### Technical
- Added CV2_AVAILABLE and SKIMAGE_AVAILABLE flags for robust dependency checking
- Implemented comprehensive edge detection fallbacks using scipy when advanced libraries unavailable
- Enhanced texture analysis with multiple feature extraction methods
- Added multi-color-space support with automatic conversion handling

## [0.8.6] - 2025-08-05

### Fixed - PyPI Changelog Display Issue
- **CRITICAL**: Fixed PyPI changelog not displaying latest releases (v0.8.4, v0.8.5)
- **DOCUMENTATION**: Updated README.md changelog section that PyPI displays instead of CHANGELOG.md
- **PYPI**: Synchronized README.md changelog with comprehensive CHANGELOG.md content
- **ENHANCED**: Ensured PyPI users see complete version history and latest features

## [0.8.5] - 2025-08-05

### Changed - Code Organization and Structure Improvement Release
- **REFACTORED**: Renamed `missing_data.py` to `core.py` to better reflect comprehensive EDA functionality
- **ENHANCED**: Updated module docstring to describe complete suite of analysis functions
- **IMPROVED**: Better project structure with appropriately named core module containing all 14 EDA functions
- **FIXED**: Updated all imports and tests to reference the new core module structure
- **MAINTAINED**: Full backward compatibility - all functions work exactly the same

## [0.8.4] - 2025-08-05

### Added - Comprehensive Scatter Matrix Visualization Release
- **NEW**: `visualize_scatter_matrix()` function with advanced pairwise relationship analysis
- **NEW**: Flexible diagonal plots: histograms, KDE curves, and box plots
- **NEW**: Customizable upper/lower triangles: scatter plots, correlation coefficients, or blank
- **NEW**: Color coding by categorical variables for group-specific pattern analysis
- **NEW**: Multiple regression line types: linear, polynomial (2nd/3rd degree), and LOWESS smoothing
- **NEW**: Comprehensive statistical insights: correlation analysis, pattern identification
- **NEW**: Professional scatter matrix layouts with adaptive figure sizing
- **NEW**: Full integration with existing edaflow workflow and styling consistency
- **ENHANCED**: Complete EDA visualization suite now includes 14 functions (from 13)
- **ENHANCED**: Added scikit-learn and statsmodels dependencies for advanced analytics
- **ENHANCED**: Updated package metadata and documentation for scatter matrix capabilities

### Technical Features
- **Matrix Customization**: Independent control of diagonal, upper, and lower triangle content
- **Statistical Analysis**: Automatic correlation strength categorization and reporting  
- **Regression Analysis**: Advanced trend line fitting with multiple algorithm options
- **Color Intelligence**: Automatic categorical/numerical variable handling for color coding
- **Performance Optimization**: Efficient handling of large datasets with smart sampling suggestions
- **Error Handling**: Comprehensive validation with informative error messages
- **Professional Output**: Publication-ready visualizations with consistent edaflow styling

## [0.8.3] - 2025-08-04

### Fixed
- **CRITICAL**: Updated README.md changelog section that PyPI was displaying instead of CHANGELOG.md
- **PYPI**: Fixed PyPI changelog display by synchronizing README.md changelog with main CHANGELOG.md
- **DOCUMENTATION**: Ensured consistent changelog information across all package files

## [0.8.2] - 2025-08-04

### Fixed
- **METADATA**: Enhanced PyPI metadata to ensure proper changelog display
- **PYPI**: Forced PyPI cache refresh by updating package metadata
- **LINKS**: Added additional project URLs for better discoverability

## [0.8.1] - 2025-08-04

### Fixed
- **FIXED**: Updated changelog dates to current date format
- **FIXED**: Removed duplicate changelog header that was causing PyPI display issues
- **ENHANCED**: Improved changelog formatting for better PyPI presentation

## [0.8.0] - 2025-08-04

### Added
- **NEW**: `visualize_histograms()` function with advanced statistical analysis and skewness detection
- Comprehensive distribution analysis with normality testing (Shapiro-Wilk, Jarque-Bera, Anderson-Darling)
- Advanced skewness interpretation: Normal (|skew| < 0.5), Moderate (0.5-1), High (≥1)
- Kurtosis analysis: Normal, Heavy-tailed (leptokurtic), Light-tailed (platykurtic)
- KDE curve overlays and normal distribution comparisons
- Statistical text boxes with comprehensive distribution metrics
- Transformation recommendations based on skewness analysis
- Multi-column histogram visualization with automatic subplot layout
- Missing data handling and robust error validation
- Detailed statistical reporting with emoji-formatted output

### Enhanced
- Updated Complete EDA Workflow to include 12 functions (from 9)
- Added histogram analysis as Step 10 in the comprehensive workflow
- Enhanced README documentation with detailed histogram function examples
- Comprehensive test suite with 7 test scenarios covering various distribution types

### Fixed
- Fixed Anderson-Darling test attribute error (significance_levels → significance_level)
- Improved statistical test error handling and validation

## [0.7.0] - 2025-08-03

### Added
- **NEW**: `visualize_heatmap()` function with comprehensive heatmap visualizations
- Four distinct heatmap types: correlation, missing data patterns, values, and cross-tabulation
- Multiple correlation methods: Pearson, Spearman, and Kendall
- Missing data pattern visualization with threshold highlighting
- Data values heatmap for detailed small dataset inspection  
- Cross-tabulation heatmaps for categorical relationship analysis
- Automatic statistical insights and detailed reporting
- Smart column detection and validation for each heatmap type
- Comprehensive customization options (colors, sizing, annotations)
- Enhanced Complete EDA Workflow with Step 11: Heatmap Analysis
- Comprehensive test suite with error handling validation
- Updated README documentation with detailed heatmap examples and use cases

### Enhanced
- Complete EDA workflow now includes 11 steps with comprehensive heatmap analysis
- Updated package features to highlight new heatmap visualization capabilities
- Improved documentation with statistical insights explanations

## [0.6.0] - 2025-08-02

### Added
- **NEW**: `visualize_interactive_boxplots()` function with full Plotly Express integration
- Interactive boxplot visualization with hover tooltips, zoom, and pan functionality
- Statistical summaries with emoji-formatted output for better readability
- Customizable styling options (colors, dimensions, margins)
- Smart column selection for numerical data
- Complete Plotly Express px.box equivalent functionality
- Added plotly>=5.0.0 dependency for interactive visualizations
- Comprehensive test suite for interactive visualization function
- Updated Complete EDA Workflow Example to include interactive visualization as Step 10
- Enhanced README documentation with interactive visualization examples and features

### Enhanced
- Complete EDA workflow now includes 10 steps with interactive final visualization
- Updated requirements documentation to include plotly dependency
- Improved package feature list to highlight interactive capabilities

## [0.5.1] - 2024-01-14

### Fixed
- Updated PyPI documentation to properly showcase handle_outliers_median() function in Complete EDA Workflow Example
- Ensured PyPI page displays the complete 9-step EDA workflow including outlier handling
- Synchronized local documentation improvements with PyPI display

## [0.5.0] - 2025-08-04

### Added
- `handle_outliers_median()` function for automated outlier detection and replacement
- Multiple outlier detection methods: IQR, Z-score, and Modified Z-score
- Complete outlier analysis workflow integration with boxplot visualization
- Median-based outlier replacement for robust statistical handling
- Flexible column selection with automatic numerical column detection
- Detailed reporting showing exactly which outliers were replaced and statistical bounds
- Safe operation mode (inplace=False by default) to preserve original data
- Statistical method comparison with customizable IQR multipliers
- Complete 9-function EDA package with comprehensive outlier management

### Fixed
- Dtype compatibility improvements to eliminate pandas FutureWarnings
- Enhanced error handling and validation for numerical column processing

## [0.4.2] - 2025-08-04

### Fixed
- Updated README.md changelog to properly reflect v0.4.1 boxplot features on PyPI page
- Corrected version history display for proper PyPI documentation

## [0.4.1] - 2025-08-04

### Added
- `visualize_numerical_boxplots()` function for comprehensive outlier detection and statistical analysis
- Advanced boxplot visualization with customizable layouts (rows/cols), orientations, and color palettes
- Automatic numerical column detection for boxplot analysis
- Detailed statistical summaries including skewness analysis and interpretation
- IQR-based outlier detection with threshold reporting
- Comprehensive outlier identification with actual outlier values displayed
- Support for horizontal and vertical boxplot orientations
- Seaborn integration for enhanced styling and color palettes

### Fixed
- `impute_categorical_mode()` function now properly returns DataFrame instead of None
- Corrected inplace parameter handling for categorical imputation function

### Fixed
- Future fixes will be documented here

### Security
- Future security updates will be documented here

## [0.1.0] - 2025-08-04

### Added
- Initial package structure
- Basic `hello()` function in `edaflow.__init__`
- Setup configuration with `setup.py` and `pyproject.toml`
- Core dependencies: pandas, numpy, matplotlib, seaborn, scipy, missingno
- Comprehensive README with installation and usage instructions
- MIT License
- Development dependencies and tooling configuration
- Git ignore file
- Basic project documentation structure

### Infrastructure
- Package structure with `edaflow/` module directory
- Development tooling setup (black, flake8, isort, pytest, mypy)
- Continuous integration ready configuration
- PyPI publishing ready setup

[Unreleased]: https://github.com/yourusername/edaflow/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/edaflow/releases/tag/v0.1.0

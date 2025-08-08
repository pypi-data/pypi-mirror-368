Changelog
=========

All notable changes to edaflow are documented here.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Version 0.12.3 (2025-08-06) - Complete Positional Argument Compatibility Fix 🔧
--------------------------------------------------------------------------------

**CRITICAL BUG FIX:**

**Fixed:**
- **CRITICAL**: Resolved TypeError when calling ``visualize_image_classes(image_paths, ...)`` with positional arguments
- **Positional Arguments**: Function now properly handles legacy positional argument usage from Jupyter notebooks
- **Backward Compatibility**: Complete support for all three usage patterns:
  1. ``visualize_image_classes(path, ...)`` - Positional (deprecated, shows warning)  
  2. ``visualize_image_classes(image_paths=path, ...)`` - Keyword deprecated (shows warning)
  3. ``visualize_image_classes(data_source=path, ...)`` - Recommended (no warning)

**Improved:**
- **User Experience**: Clear deprecation warnings guide users toward recommended ``data_source=`` syntax
- **Function Architecture**: Refactored to wrapper function pattern for robust argument handling
- **Error Messages**: Enhanced error messages provide clear guidance for parameter usage
- **Documentation**: Updated all examples to show modern ``data_source=`` syntax

**Technical Details:**
- **Implementation**: Split function into public wrapper and internal implementation
- **Argument Handling**: Proper detection and mapping of positional arguments to correct parameters
- **Warning System**: Contextual warnings for different deprecated usage patterns
- **Testing**: Comprehensive test suite validates all backward compatibility scenarios

**Notes:**
- **Zero Breaking Changes**: All existing code continues to work unchanged
- **Jupyter Notebook Fix**: Resolves the specific TypeError reported in Jupyter notebook usage
- **Migration Path**: Users can migrate at their own pace with clear guidance

Version 0.12.2 (2025-08-06) - Documentation Refresh Release 📚
---------------------------------------------------------------

**Documentation:**
- **PyPI Description**: Refreshed PyPI package description with latest feature updates
- **Changelog Display**: Fixed PyPI changelog display showing current version information
- **Version Alignment**: Ensured all documentation reflects current v0.12.2 capabilities

Version 0.12.1 (2025-08-05) - Enhanced Computer Vision EDA 🖼️
--------------------------------------------------------------

**Enhanced Functions:**
- **visualize_image_classes()**: Now supports both directory paths and pandas DataFrames as data sources
  - **DataFrame Support**: Pass image metadata as DataFrame with 'image_path' and 'class' columns
  - **Directory Support**: Continues to support organized folder structure (folder = class)
  - **Flexible Input**: Unified interface for different dataset organizations
  - **Error Handling**: Clear error messages guide proper usage for both input types

**Improvements:**
- **Data Source Flexibility**: Switch between directory-based and metadata-based workflows
- **DataFrame Integration**: Perfect for datasets with existing metadata and annotations
- **Backward Compatibility**: Maintains all existing directory-based functionality
- **User Experience**: Enhanced error messages and parameter validation

Version 0.10.0 (2025-08-05) - Image Quality Assessment Release 🔍
----------------------------------------------------------------

**Major New Feature: Comprehensive Image Quality Assessment**

**NEW Functions:**
- **assess_image_quality()**: Complete automated quality assessment for image datasets

**Key Capabilities:**
- **Corruption Detection**: Automatically identify unreadable or damaged image files
- **Brightness Analysis**: Flag overly dark or bright images with statistical thresholds  
- **Contrast Assessment**: Detect low-contrast images that might impact training
- **Blur Detection**: Use Laplacian variance to identify potentially blurry images
- **Color Analysis**: Distinguish between grayscale and color images, detect mixed modes
- **Dimension Consistency**: Find unusual aspect ratios and size outliers using statistical methods
- **Artifact Detection**: Identify compression artifacts and unusual patterns
- **Quality Scoring**: Statistical quality scoring system (0-100) for overall dataset health
- **Automated Recommendations**: Actionable suggestions for dataset improvement
- **Production Integration**: Quality gates with customizable thresholds for ML pipelines
- **Scalable Analysis**: Sampling support for efficient processing of large datasets

**Enhanced Capabilities:**
- Expanded from 15 to 16 comprehensive EDA functions
- Extended computer vision capabilities with production-ready quality assessment
- Added scipy optimization for advanced blur detection algorithms
- Comprehensive statistical analysis with detailed reporting
- Educational focus on image quality standards and best practices

**Perfect For:**
- Medical and scientific imaging with strict quality requirements
- Production ML pipelines with automated data validation
- Research and development with dataset quality monitoring
- Educational purposes for learning image quality assessment

Version 0.9.0 (2025-08-05) - Computer Vision EDA Release 🖼️
------------------------------------------------------------

**Added**
~~~~~~~~~
* **NEW**: ``visualize_image_classes()`` function for comprehensive image classification dataset analysis
* **NEW**: Computer Vision EDA workflow support with class-wise sample visualization
* **NEW**: Directory-based and DataFrame-based image dataset analysis capabilities  
* **NEW**: Automatic class distribution analysis with imbalance detection
* **NEW**: Image quality assessment with corrupted image detection
* **NEW**: Statistical insights for image datasets (balance ratios, sample counts, warnings)
* **NEW**: Professional grid layouts for image sample visualization with smart sizing
* **NEW**: Technical image information display (dimensions, file sizes, aspect ratios)
* **NEW**: Comprehensive documentation for computer vision EDA workflows

**Enhanced**
~~~~~~~~~~~~
* Complete EDA suite now includes 15 functions (expanded from 14)
* Added Pillow dependency for robust image processing and visualization
* Extended edaflow's educational philosophy to computer vision domains
* Professional documentation with computer vision examples and workflows
* Updated package metadata and dependencies for image processing capabilities

**Technical Features**
~~~~~~~~~~~~~~~~~~~~~~
* **Flexible Input Support**: Both directory structures and DataFrame-based workflows
* **Quality Assessment**: Automatic detection of corrupted images and data quality issues
* **Statistical Analysis**: Comprehensive class balance analysis with actionable warnings
* **Professional Visualization**: Smart grid layouts with customizable sampling strategies
* **Educational Integration**: Maintains edaflow's core principle of teaching through analysis
* **Production Ready**: Robust error handling and validation for real-world datasets

Version 0.8.6 (2025-08-05) - PyPI Changelog Display Fix
--------------------------------------------------------

**Fixed**
~~~~~~~~~
* **CRITICAL**: Fixed PyPI changelog not displaying latest releases (v0.8.4, v0.8.5)
* **DOCUMENTATION**: Updated README.md changelog section that PyPI displays instead of CHANGELOG.md
* **PYPI**: Synchronized README.md changelog with comprehensive CHANGELOG.md content
* **ENHANCED**: Ensured PyPI users see complete version history and latest features

Version 0.8.5 (2025-08-05) - Code Organization and Structure Improvement
--------------------------------------------------------------------------

**Changed**
~~~~~~~~~~~
* **REFACTORED**: Renamed ``missing_data.py`` to ``core.py`` to better reflect comprehensive EDA functionality
* **ENHANCED**: Updated module docstring to describe complete suite of analysis functions
* **IMPROVED**: Better project structure with appropriately named core module containing all 14 EDA functions
* **FIXED**: Updated all imports and tests to reference the new core module structure
* **MAINTAINED**: Full backward compatibility - all functions work exactly the same

Version 0.8.4 (2025-08-05) - Comprehensive Scatter Matrix Visualization Release
--------------------------------------------------------------------------------

**Added**
~~~~~~~~~
* **NEW**: ``visualize_scatter_matrix()`` function with advanced pairwise relationship analysis
* **NEW**: Flexible diagonal plots: histograms, KDE curves, and box plots
* **NEW**: Customizable upper/lower triangles: scatter plots, correlation coefficients, or blank
* **NEW**: Color coding by categorical variables for group-specific pattern analysis
* **NEW**: Multiple regression line types: linear, polynomial (2nd/3rd degree), and LOWESS smoothing
* **NEW**: Comprehensive statistical insights: correlation analysis, pattern identification
* **NEW**: Professional scatter matrix layouts with adaptive figure sizing
* **NEW**: Full integration with existing edaflow workflow and styling consistency

**Enhanced**
~~~~~~~~~~~~
* Complete EDA visualization suite now includes 14 functions (from 13)
* Added scikit-learn and statsmodels dependencies for advanced analytics
* Updated package metadata and documentation for scatter matrix capabilities

**Technical Features**
~~~~~~~~~~~~~~~~~~~~~~
* **Matrix Customization**: Independent control of diagonal, upper, and lower triangle content
* **Statistical Analysis**: Automatic correlation strength categorization and reporting  
* **Regression Analysis**: Advanced trend line fitting with multiple algorithm options
* **Color Intelligence**: Automatic categorical/numerical variable handling for color coding
* **Performance Optimization**: Efficient handling of large datasets with smart sampling suggestions
* **Error Handling**: Comprehensive validation with informative error messages
* **Professional Output**: Publication-ready visualizations with consistent edaflow styling

Version 0.8.3 (2025-08-04) - Critical Documentation Fix Release
----------------------------------------------------------------

**Fixed**
~~~~~~~~~
* **CRITICAL**: Updated README.md changelog section that PyPI was displaying instead of CHANGELOG.md
* **PYPI**: Fixed PyPI changelog display by synchronizing README.md changelog with main CHANGELOG.md
* **DOCUMENTATION**: Ensured consistent changelog information across all package files

Version 0.8.2 (2025-08-04) - Metadata Enhancement Release
----------------------------------------------------------

**Fixed**
~~~~~~~~~
* **METADATA**: Enhanced PyPI metadata to ensure proper changelog display
* **PYPI**: Forced PyPI cache refresh by updating package metadata
* **LINKS**: Added additional project URLs for better discoverability

Version 0.8.1 (2025-08-04) - Changelog Formatting Release
----------------------------------------------------------

**Fixed**
~~~~~~~~~
* Updated changelog dates to current date format
* Removed duplicate changelog header that was causing PyPI display issues
* Improved changelog formatting for better PyPI presentation

Version 0.8.0 (2025-08-04) - Statistical Histogram Analysis Release
--------------------------------------------------------------------

**Added**
~~~~~~~~~
* **NEW**: ``visualize_histograms()`` function with advanced statistical analysis and skewness detection
* Comprehensive distribution analysis with normality testing (Shapiro-Wilk, Jarque-Bera, Anderson-Darling)
* Advanced skewness interpretation: Normal (\|skew\| < 0.5), Moderate (0.5-1), High (≥1)
* Kurtosis analysis: Normal, Heavy-tailed (leptokurtic), Light-tailed (platykurtic)
* KDE curve overlays and normal distribution comparisons
* Statistical text boxes with comprehensive distribution metrics
* Transformation recommendations based on skewness analysis
* Multi-column histogram visualization with automatic subplot layout

**Enhanced**
~~~~~~~~~~~~
* Updated Complete EDA Workflow to include 12 functions (from 9)
* Added histogram analysis as Step 10 in the comprehensive workflow
* Enhanced README documentation with detailed histogram function examples
* Comprehensive test suite with 7 test scenarios covering various distribution types

**Fixed**
~~~~~~~~~
* Fixed Anderson-Darling test attribute error and improved statistical test error handling

Version 0.7.0 (2025-08-03) - Comprehensive Heatmap Visualization Release
-------------------------------------------------------------------------

**Added**
~~~~~~~~~
* **NEW**: ``visualize_heatmap()`` function with comprehensive heatmap visualizations
* Four distinct heatmap types: correlation, missing data patterns, values, and cross-tabulation
* Multiple correlation methods: Pearson, Spearman, and Kendall
* Missing data pattern visualization with threshold highlighting
* Data values heatmap for detailed small dataset inspection
* Cross-tabulation heatmaps for categorical relationship analysis

**Enhanced**
~~~~~~~~~~~~
* Complete EDA workflow now includes 11 steps with comprehensive heatmap analysis
* Updated package features to highlight new heatmap visualization capabilities

Version 0.6.0 (2025-08-02) - Interactive Boxplot Visualization Release
-----------------------------------------------------------------------

**Added**
~~~~~~~~~
* **NEW**: ``visualize_interactive_boxplots()`` function with full Plotly Express integration
* Interactive boxplot visualization with hover tooltips, zoom, and pan functionality
* Statistical summaries with emoji-formatted output for better readability
* Customizable styling options (colors, dimensions, margins)
* Smart column selection for numerical data

**Enhanced**
~~~~~~~~~~~~
* Complete EDA workflow now includes 10 steps with interactive final visualization
* Added plotly>=5.0.0 dependency for interactive visualizations

Version 0.5.1 (2024-01-14) - Documentation Enhancement
-------------------------------------------------------

**Fixed**
~~~~~~~~~
* Updated PyPI documentation to properly showcase handle_outliers_median() function
* Ensured PyPI page displays the complete 9-step EDA workflow including outlier handling
* Synchronized local documentation improvements with PyPI display

Version 0.5.0 (2025-08-04) - Outlier Handling Release
------------------------------------------------------

**Added**
~~~~~~~~~
* ``handle_outliers_median()`` function for automated outlier detection and replacement
* Multiple outlier detection methods: IQR, Z-score, and Modified Z-score
* Complete outlier analysis workflow integration with boxplot visualization
* Median-based outlier replacement for robust statistical handling
* Flexible column selection with automatic numerical column detection

**Fixed**
~~~~~~~~~
* Dtype compatibility improvements to eliminate pandas FutureWarnings
* Enhanced error handling and validation for numerical column processing

Earlier Versions
----------------

For complete version history, see the `GitHub Releases <https://github.com/evanlow/edaflow/releases>`_ page.

.. note::
   This changelog covers the major releases. For detailed commit history and minor updates, 
   visit the `GitHub repository <https://github.com/evanlow/edaflow>`_.

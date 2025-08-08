"""
edaflow - A Python package for exploratory data analysis workflows
"""

from .analysis import (
    check_null_columns,
    analyze_categorical_columns,
    convert_to_numeric,
    visualize_categorical_values,
    display_column_types,
    impute_numerical_median,
    impute_categorical_mode,
    visualize_numerical_boxplots,
    handle_outliers_median,
    visualize_interactive_boxplots,
    visualize_heatmap,
    visualize_histograms,
    visualize_scatter_matrix,
    visualize_image_classes,
    assess_image_quality,
    analyze_image_features,
    analyze_encoding_needs,
    apply_smart_encoding
)

__version__ = "0.12.7"
__author__ = "Evan Low"
__email__ = "evan.low@illumetechnology.com"


def hello():
    """
    A sample hello function to test the package installation.

    Returns:
        str: A greeting message
    """
    return "Hello from edaflow! Ready for exploratory data analysis."


# Import main modules
# from .visualization import *
# from .preprocessing import *

# Export main functions
__all__ = [
    'hello', 
    'check_null_columns', 
    'analyze_categorical_columns', 
    'convert_to_numeric', 
    'visualize_categorical_values',
    'display_column_types',
    'impute_numerical_median',
    'impute_categorical_mode',
    'visualize_numerical_boxplots',
    'handle_outliers_median',
    'visualize_interactive_boxplots',
    'visualize_heatmap',
    'visualize_histograms',
    'visualize_scatter_matrix',
    'visualize_image_classes',
    'assess_image_quality',
    'analyze_image_features',
    'analyze_encoding_needs',
    'apply_smart_encoding'
]

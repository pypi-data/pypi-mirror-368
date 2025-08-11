"""
Analysis module for edaflow package.

This module contains functions for data analysis and exploration.
"""

from .core import (
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
    apply_smart_encoding,
    apply_encoding,
    apply_encoding_with_encoders,
    summarize_eda_insights
)

__all__ = [
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
    'apply_smart_encoding',
    'apply_encoding',
    'apply_encoding_with_encoders',
    'summarize_eda_insights'
]

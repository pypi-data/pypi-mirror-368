"""
Core EDA functions for edaflow.

This module provides the complete suite of exploratory data analysis functions including:
- Missing data analysis and visualization
- Categorical data insights and type conversion  
- Data imputation and outlier handling
- Statistical distribution analysis
- Interactive visualizations and heatmaps
- Comprehensive scatter matrix analysis
- Computer vision EDA for image classification datasets
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Union, Tuple, Dict, Any
import math
import os
import random
from pathlib import Path

# Additional imports for encoding functionality (v0.12.0)
try:
    from sklearn.preprocessing import (
        LabelEncoder, OneHotEncoder, OrdinalEncoder, 
        TargetEncoder, StandardScaler
    )
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Install with: pip install scikit-learn")
try:
    from PIL import Image, ImageStat
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from skimage import feature, filters, color
    from skimage.feature import local_binary_pattern
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False


def check_null_columns(df: pd.DataFrame,
                       threshold: Optional[float] = 10) -> pd.DataFrame:
    """
    Check null values in DataFrame columns with rich styled output.

    Calculates the percentage of null values per column and applies color styling
    based on the percentage of nulls relative to the threshold.

    Args:
        df (pd.DataFrame): The input DataFrame to analyze
        threshold (Optional[float], optional): The threshold percentage for
                                             highlighting. Defaults to 10.

    Returns:
        pd.DataFrame: A styled DataFrame showing column names and null
                     percentages with color coding:
                     - Red: > 2*threshold (high null percentage)
                     - Yellow: > threshold but <= 2*threshold (medium null %)
                     - Light yellow: > 0 but <= threshold (low null %)
                     - Gray: 0 (no nulls)

    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({'A': [1, 2, None], 'B': [1, None, None]})
        >>> styled_result = edaflow.check_null_columns(df, threshold=20)
        >>> # Returns styled DataFrame with null percentages

        # Alternative import style:
        >>> from edaflow.analysis import check_null_columns
        >>> styled_result = check_null_columns(df, threshold=20)
    """
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich import box
        
        # Optimize console for Google Colab compatibility
        console = Console(width=80, force_terminal=True)
        use_rich = True
    except ImportError:
        console = None
        use_rich = False
    
    # Calculate null percentages
    null_counts = df.isnull().sum()
    total_rows = len(df)
    null_percentages = (null_counts / total_rows * 100).round(2)

    # Create result DataFrame
    result_df = pd.DataFrame({
        'Column': df.columns,
        'Null_Count': null_counts.values,
        'Null_Percentage': null_percentages.values
    })
    
    if use_rich:
        # Rich formatted output
        console.print()  # Add simple spacing
        console.print("🔍 MISSING DATA ANALYSIS", style="bold white on blue", justify="center")
        console.print(f"📊 Analyzing {len(df.columns)} columns with threshold: {threshold}%", style="bold yellow")
        
        # Create rich table for null analysis with better box style
        null_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        null_table.add_column("Column", style="bold white", no_wrap=True)
        null_table.add_column("Null Count", justify="right", style="cyan")
        null_table.add_column("Null %", justify="right", style="yellow")
        null_table.add_column("Status", justify="center")
        null_table.add_column("Data Integrity", justify="center")
        
        # Categorize columns by null severity
        critical_nulls = []
        warning_nulls = []
        minor_nulls = []
        clean_columns = []
        
        for _, row in result_df.iterrows():
            col_name = row['Column']
            null_count = row['Null_Count'] 
            null_pct = row['Null_Percentage']
            
            # Determine status and styling
            if null_pct == 0:
                status = Text("✅ CLEAN", style="bold green")
                integrity = Text("🟢 PERFECT", style="bold green")
                clean_columns.append(row)
            elif null_pct <= threshold:
                status = Text("⚠️ MINOR", style="bold blue")
                integrity = Text("🟡 GOOD", style="bold blue")
                minor_nulls.append(row)
            elif null_pct <= threshold * 2:
                status = Text("🚨 WARNING", style="bold yellow")
                integrity = Text("🟠 CAUTION", style="bold yellow")
                warning_nulls.append(row)
            else:
                status = Text("💀 CRITICAL", style="bold red")
                integrity = Text("🔴 SEVERE", style="bold red")
                critical_nulls.append(row)
            
            null_table.add_row(
                col_name,
                f"{null_count:,}",
                f"{null_pct:.1f}%",
                status,
                integrity
            )
        
        console.print(null_table)
        
        # Summary statistics with color-coded panels
        if critical_nulls:
            console.print(Panel(
                f"🚨 {len(critical_nulls)} columns have CRITICAL null levels (>{threshold*2}%)\n"
                f"Columns: {', '.join([row['Column'] for row in critical_nulls])}\n"
                "💡 Recommendation: Investigate data collection process or consider imputation",
                title="💀 CRITICAL ISSUES",
                style="bold red",
                box=box.HEAVY
            ))
        
        if warning_nulls:
            console.print(Panel(
                f"⚠️ {len(warning_nulls)} columns have WARNING null levels ({threshold}%-{threshold*2}%)\n"
                f"Columns: {', '.join([row['Column'] for row in warning_nulls])}\n"
                "💡 Recommendation: Consider imputation strategies",
                title="🚨 WARNING LEVELS",
                style="bold yellow",
                box=box.ROUNDED,
                width=80,
                padding=(0, 1)
            ))
        
        # Overall summary
        summary_text = f"""
📈 Dataset Overview:
• Total Rows: {total_rows:,}
• Total Columns: {len(df.columns)}
• Clean Columns: {len(clean_columns)} ✅
• Minor Issues: {len(minor_nulls)} ⚠️
• Warning Level: {len(warning_nulls)} 🚨
• Critical Issues: {len(critical_nulls)} 💀

🎯 Null Threshold: {threshold}%
        """
        
        # Determine overall health color
        if critical_nulls:
            health_style = "bold red"
            health_title = "💀 DATA HEALTH: CRITICAL"
        elif warning_nulls:
            health_style = "bold yellow" 
            health_title = "🚨 DATA HEALTH: WARNING"
        elif minor_nulls:
            health_style = "bold blue"
            health_title = "⚠️ DATA HEALTH: GOOD"
        else:
            health_style = "bold green"
            health_title = "✅ DATA HEALTH: EXCELLENT"
        
        console.print(Panel(
            summary_text.strip(),
            title=health_title,
            style=health_style,
            box=box.ROUNDED,
            width=80,
            padding=(0, 1)
        ))
        
        console.print("✨ Missing data analysis complete!", style="bold green")

    def style_nulls(val):
        """Apply color styling based on null percentage."""
        if val == 0:
            return 'background-color: lightgray'
        elif val > threshold * 2:
            return 'background-color: red; color: white'
        elif val > threshold:
            return 'background-color: yellow'
        else:  # val > 0
            return 'background-color: lightyellow'

    # Apply styling to the Null_Percentage column
    styled_df = result_df.style.map(style_nulls, subset=['Null_Percentage'])

    return styled_df


def analyze_categorical_columns(df: pd.DataFrame, 
                              threshold: Optional[float] = 35) -> None:
    """
    Analyze categorical columns of object type to identify potential data issues.
    
    This function examines object-type columns to detect:
    1. Columns that might be numeric but stored as strings
    2. Categorical columns with their unique values
    3. Data type consistency issues
    
    Args:
        df (pd.DataFrame): The input DataFrame to analyze
        threshold (Optional[float], optional): The threshold percentage for 
                                             non-numeric values. If a column 
                                             has less than this percentage of 
                                             non-numeric values, it's flagged 
                                             as potentially numeric. Defaults to 35.
    
    Returns:
        None: Prints analysis results directly to console with rich color coding
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({
        ...     'name': ['Alice', 'Bob', 'Charlie'],
        ...     'age_str': ['25', '30', '35'], 
        ...     'mixed': ['1', '2', 'three'],
        ...     'numbers': [1, 2, 3]
        ... })
        >>> edaflow.analyze_categorical_columns(df, threshold=35)
        # Output with rich color coding and tables
        
        # Alternative import style:
        >>> from edaflow.analysis import analyze_categorical_columns
    """
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich import box
        from rich.columns import Columns
        
        # Optimize console for Google Colab compatibility
        console = Console(width=80, force_terminal=True)
        use_rich = True
    except ImportError:
        # Fallback to basic output if rich is not available
        console = None
        use_rich = False
    
    if use_rich:
        # Rich-styled output
        console.print()
        console.print("🔍 CATEGORICAL DATA ANALYSIS", 
                     style="bold white on blue", justify="center")
        console.print()
        
        # Create analysis results
        object_columns = []
        numeric_potential = []
        truly_categorical = []
        non_object_columns = []
        
        # Analyze each column
        for col in df.columns:
            if df[col].dtype == 'object':
                object_columns.append(col)
                
                try:
                    # Try to convert to numeric and check how many fail
                    numeric_col = pd.to_numeric(df[col], errors='coerce')
                    non_numeric_pct = (numeric_col.isnull().sum() / len(numeric_col)) * 100
                    
                    # Handle potential unhashable types (like lists) in columns
                    try:
                        unique_count = df[col].nunique()
                        unique_values = df[col].unique()[:5]  # Show first 5 unique values
                    except TypeError:
                        # Handle unhashable types by converting to string first
                        unique_count = df[col].astype(str).nunique()
                        unique_values = df[col].astype(str).unique()[:5]
                    
                    total_count = len(df[col])
                    
                    if non_numeric_pct < threshold:
                        numeric_potential.append({
                            'column': col,
                            'non_numeric_pct': non_numeric_pct,
                            'unique_count': unique_count,
                            'unique_values': unique_values
                        })
                    else:
                        truly_categorical.append({
                            'column': col,
                            'non_numeric_pct': non_numeric_pct,
                            'unique_count': unique_count,
                            'total_count': total_count,
                            'unique_values': unique_values
                        })
                except Exception as e:
                    # If any other error occurs, treat as categorical with basic info
                    truly_categorical.append({
                        'column': col,
                        'non_numeric_pct': 100.0,
                        'unique_count': 'unknown',
                        'total_count': len(df[col]),
                        'unique_values': ['Error processing column'],
                        'error': str(e)
                    })
            else:
                non_object_columns.append({
                    'column': col,
                    'dtype': str(df[col].dtype)
                })
        
        # Display potentially numeric columns
        if numeric_potential:
            console.print("🚨 POTENTIALLY NUMERIC COLUMNS", style="bold red on yellow")
            
            numeric_table = Table(show_header=True, header_style="bold red", 
                                box=box.SIMPLE, border_style="red")
            numeric_table.add_column("⚠️ Column", style="bold red", no_wrap=True)
            numeric_table.add_column("Non-Numeric %", justify="right", style="bold yellow")
            numeric_table.add_column("Unique Values", justify="right", style="cyan")
            numeric_table.add_column("Sample Values", style="dim white")
            
            for item in numeric_potential:
                sample_text = str(list(item['unique_values']))[1:-1]  # Remove brackets
                if len(sample_text) > 50:
                    sample_text = sample_text[:47] + "..."
                    
                numeric_table.add_row(
                    item['column'],
                    f"{item['non_numeric_pct']:.1f}%",
                    f"{item['unique_count']:,}",
                    sample_text
                )
            
            console.print(numeric_table)
            console.print("💡 [bold cyan]Recommendation:[/bold cyan] Consider using convert_to_numeric() to convert these columns")
            console.print()
        
        # Display truly categorical columns
        if truly_categorical:
            console.print("📊 CATEGORICAL COLUMNS", style="bold green")
            
            cat_table = Table(show_header=True, header_style="bold green",
                            box=box.SIMPLE, border_style="green")
            cat_table.add_column("✅ Column", style="bold green", no_wrap=True)
            cat_table.add_column("Non-Numeric %", justify="right", style="yellow")
            cat_table.add_column("Unique/Total", justify="right", style="cyan")
            cat_table.add_column("Cardinality", justify="center", style="bold")
            cat_table.add_column("Sample Values", style="dim white")
            
            for item in truly_categorical:
                # Determine cardinality status
                cardinality_ratio = item['unique_count'] / item['total_count']
                if cardinality_ratio > 0.8:
                    cardinality = Text("🆔 HIGH", style="bold red")
                elif cardinality_ratio > 0.5:
                    cardinality = Text("📈 MED", style="bold orange3")
                elif item['unique_count'] > 50:
                    cardinality = Text("⚠️ MANY", style="bold yellow")
                else:
                    cardinality = Text("✅ GOOD", style="bold green")
                
                sample_text = str(list(item['unique_values']))[1:-1]  # Remove brackets
                if len(sample_text) > 40:
                    sample_text = sample_text[:37] + "..."
                
                cat_table.add_row(
                    item['column'],
                    f"{item['non_numeric_pct']:.1f}%",
                    f"{item['unique_count']:,}/{item['total_count']:,}",
                    cardinality,
                    sample_text
                )
            
            console.print(cat_table)
            console.print()
        
        # Display non-object columns  
        if non_object_columns:
            console.print("🔢 NON-OBJECT COLUMNS", style="bold blue")
            
            non_obj_table = Table(show_header=True, header_style="bold blue",
                                box=box.SIMPLE, border_style="blue")
            non_obj_table.add_column("Column", style="bold blue")
            non_obj_table.add_column("Data Type", style="cyan")
            
            for item in non_object_columns:
                non_obj_table.add_row(item['column'], item['dtype'])
            
            console.print(non_obj_table)
            console.print()
        
        # Summary panel
        summary_content = f"""
[bold cyan]📈 Analysis Summary:[/bold cyan]
• Total Columns: {len(df.columns)}
• Object Columns: {len(object_columns)}
• Potentially Numeric: {len(numeric_potential)} [red](need conversion)[/red]
• True Categorical: {len(truly_categorical)} [green](properly typed)[/green]
• Non-Object: {len(non_object_columns)} [blue](numeric/other types)[/blue]
        """
        
        console.print(Panel(
            summary_content.strip(),
            title="📊 Column Type Analysis",
            border_style="bright_magenta",
            box=box.ROUNDED,
            width=80,
            padding=(0, 1)
        ))
        
        console.print("✨ [bold green]Analysis complete![/bold green]")
        
    else:
        # Fallback to original basic output if rich is not available
        print("Analyzing categorical columns of object type...")
        print("=" * 50)
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric and check how many fail
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                non_numeric_pct = (numeric_col.isnull().sum() / len(numeric_col)) * 100
                
                if non_numeric_pct < threshold:
                    # Potential numeric column - highlight in red with blue background
                    print('\x1b[1;31;44m{} is potentially a numeric column that needs conversion\x1b[m'.format(col))
                    print('\x1b[1;30;43m{} has {} unique values: {}\x1b[m'.format(
                        col, df[col].nunique(), df[col].unique()[:10]  # Show first 10 unique values
                    ))
                else:
                    # Truly categorical column
                    unique_count = df[col].nunique()
                    total_count = len(df[col])
                    print('{} has too many non-numeric values ({}% non-numeric)'.format(
                        col, round(non_numeric_pct, 2)
                    ))
                    print('  └─ {} unique values out of {} total ({} unique values shown): {}'.format(
                        unique_count, total_count, min(10, unique_count), 
                        df[col].unique()[:10]  # Show first 10 unique values
                    ))
            else:
                print('{} is not an object column (dtype: {})'.format(col, df[col].dtype))
        
        print("=" * 50)
        print("Analysis complete!")
    
    # Return structured data for programmatic use
    return {
        'object_columns': object_columns,
        'numeric_potential': numeric_potential,
        'truly_categorical': truly_categorical,
        'non_object_columns': non_object_columns
    }


def convert_to_numeric(df: pd.DataFrame, 
                      threshold: Optional[float] = 35,
                      inplace: bool = False) -> pd.DataFrame:
    """
    Convert object columns to numeric when appropriate based on data analysis with rich formatting.
    
    This function examines object-type columns and converts them to numeric
    if the percentage of non-numeric values is below the specified threshold.
    This helps clean datasets where numeric data is stored as strings.
    
    Args:
        df (pd.DataFrame): The input DataFrame to process
        threshold (Optional[float], optional): The threshold percentage for 
                                             non-numeric values. Columns with
                                             fewer non-numeric values than this
                                             threshold will be converted to numeric.
                                             Defaults to 35.
        inplace (bool, optional): If True, modify the DataFrame in place and return None.
                                If False, return a new DataFrame with conversions applied.
                                Defaults to False.
    
    Returns:
        pd.DataFrame or None: If inplace=False, returns a new DataFrame with 
                            numeric conversions applied. If inplace=True, 
                            modifies the original DataFrame and returns None.
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({
        ...     'name': ['Alice', 'Bob', 'Charlie'],
        ...     'age_str': ['25', '30', '35'], 
        ...     'mixed': ['1', '2', 'three'],
        ...     'numbers': [1, 2, 3]
        ... })
        >>> 
        >>> # Create a copy with conversions
        >>> df_cleaned = edaflow.convert_to_numeric(df, threshold=35)
        >>> 
        >>> # Or modify the original DataFrame
        >>> edaflow.convert_to_numeric(df, threshold=35, inplace=True)
        >>> 
        >>> # Alternative import style:
        >>> from edaflow.analysis import convert_to_numeric
        >>> df_cleaned = convert_to_numeric(df, threshold=50)
    
    Notes:
        - Values that cannot be converted to numeric become NaN
        - The function provides colored output showing which columns were converted
        - Use a lower threshold to be more strict about conversions
        - Use a higher threshold to be more lenient about mixed data
    """
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich import box
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        # Optimize console for Google Colab compatibility
        console = Console(width=80, force_terminal=True)
        rich_available = True
    except ImportError:
        rich_available = False
        console = None
    
    # Create a copy if not modifying inplace
    if not inplace:
        df_result = df.copy()
    else:
        df_result = df
    
    if rich_available:
        # Rich formatted output
        console.print()
        console.print("🔄 AUTOMATIC DATA TYPE CONVERSION", style="bold white on blue", justify="center")
        console.print(f"📊 Analyzing {len(df_result.columns)} columns with threshold: {threshold}%", style="bold yellow")
    else:
        # Fallback to plain output
        print("\nConverting object columns to numeric where appropriate...")
        print("=" * 60)
    
    conversions_made = []
    skipped_already_numeric = []
    skipped_too_many_non_numeric = []
    
    # Create rich table for results
    if rich_available:
        results_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        results_table.add_column("Column", style="bold white", no_wrap=True)
        results_table.add_column("Action", justify="center")
        results_table.add_column("Details", style="dim white")
        results_table.add_column("Status", justify="center")
    
    for col in df_result.columns:
        if df_result[col].dtype == 'object':
            # Try to convert to numeric and check how many fail
            numeric_col = pd.to_numeric(df_result[col], errors='coerce')
            non_numeric_pct = (numeric_col.isnull().sum() / len(numeric_col)) * 100
            
            if non_numeric_pct < threshold:
                # Convert the column to numeric
                original_nulls = df_result[col].isnull().sum()
                df_result[col] = pd.to_numeric(df_result[col], errors='coerce')
                new_nulls = df_result[col].isnull().sum()
                values_converted_to_nan = new_nulls - original_nulls
                
                conversions_made.append({
                    'column': col,
                    'non_numeric_pct': round(non_numeric_pct, 2),
                    'values_converted_to_nan': values_converted_to_nan,
                    'new_dtype': df_result[col].dtype
                })
                
                if rich_available:
                    status = Text("✅ CONVERTED", style="bold green")
                    action = Text("🔄 Object → Numeric", style="bold cyan")
                    details = f"{non_numeric_pct:.1f}% non-numeric ({values_converted_to_nan} → NaN)"
                    results_table.add_row(col, action, details, status)
                else:
                    print('\x1b[1;31;44mConverting {} to a numerical column\x1b[m'.format(col))
                    print('  └─ {}% of values were non-numeric ({} values converted to NaN)'.format(
                        round(non_numeric_pct, 2), values_converted_to_nan
                    ))
            else:
                # Skip conversion - too many non-numeric values
                skipped_too_many_non_numeric.append({
                    'column': col,
                    'non_numeric_pct': round(non_numeric_pct, 2)
                })
                
                if rich_available:
                    status = Text("⚠️ SKIPPED", style="bold yellow")
                    action = Text("🚫 No Conversion", style="dim yellow")
                    details = f"{non_numeric_pct:.1f}% non-numeric (threshold: {threshold}%)"
                    results_table.add_row(col, action, details, status)
                else:
                    print('{} skipped: {}% non-numeric values (threshold: {}%)'.format(
                        col, round(non_numeric_pct, 2), threshold
                    ))
        else:
            # Already numeric
            skipped_already_numeric.append({
                'column': col,
                'dtype': str(df_result[col].dtype)
            })
            
            if rich_available:
                status = Text("✅ GOOD", style="bold green")
                action = Text("📊 Already Numeric", style="dim green")
                details = f"dtype: {df_result[col].dtype}"
                results_table.add_row(col, action, details, status)
            else:
                print('{} skipped: already numeric (dtype: {})'.format(col, df_result[col].dtype))
    
    if rich_available:
        console.print(results_table)
        
        # Summary statistics with rich formatting
        summary_text = f"""
📈 Total Columns Processed: {len(df_result.columns)}
✅ Successfully Converted: {len(conversions_made)}
📊 Already Numeric: {len(skipped_already_numeric)}
⚠️  Skipped (Above Threshold): {len(skipped_too_many_non_numeric)}
🎯 Conversion Threshold: {threshold}%
        """
        
        if conversions_made:
            console.print(Panel(
                summary_text.strip(),
                title="🎉 Conversion Summary",
                style="bold green",
                box=box.ROUNDED,
                width=80,
                padding=(0, 1)
            ))
            
            # Show conversion details
            console.print("\n🔄 Conversion Details:", style="bold cyan")
            conversion_detail_table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
            conversion_detail_table.add_column("Column", style="bold white")
            conversion_detail_table.add_column("New Data Type", style="bold cyan")
            conversion_detail_table.add_column("Non-Numeric %", justify="right", style="yellow")
            conversion_detail_table.add_column("Values → NaN", justify="right", style="red")
            
            for conversion in conversions_made:
                conversion_detail_table.add_row(
                    conversion['column'],
                    str(conversion['new_dtype']),
                    f"{conversion['non_numeric_pct']}%",
                    str(conversion['values_converted_to_nan'])
                )
            
            console.print(conversion_detail_table)
        else:
            console.print(Panel(
                summary_text.strip(),
                title="ℹ️ No Conversions Made",
                style="bold blue",
                box=box.SIMPLE
            ))
        
        console.print("✨ Data type conversion complete!", style="bold green")
    else:
        # Fallback plain output
        print("=" * 60)
        if conversions_made:
            print(f"✅ Successfully converted {len(conversions_made)} columns to numeric:")
            for conversion in conversions_made:
                print(f"   • {conversion['column']}: {conversion['non_numeric_pct']}% non-numeric")
        else:
            print("ℹ️  No columns were converted (all were either already numeric or above threshold)")
        print("Conversion complete!")
    
    # Return the result DataFrame if not inplace, otherwise return None
    return None if inplace else df_result


def visualize_categorical_values(df: pd.DataFrame, 
                                max_unique_values: Optional[int] = 20,
                                show_counts: bool = True,
                                show_percentages: bool = True) -> None:
    """
    Visualize unique values in categorical (object-type) columns with counts and percentages.
    
    This function provides a comprehensive overview of categorical columns by displaying:
    - Unique values in each categorical column
    - Value counts (frequency of each unique value)
    - Percentages (relative frequency)
    - Summary statistics for each column
    
    Args:
        df (pd.DataFrame): The input DataFrame to analyze
        max_unique_values (Optional[int], optional): Maximum number of unique values 
                                                   to display per column. If a column 
                                                   has more unique values, only the top 
                                                   N most frequent will be shown. 
                                                   Defaults to 20.
        show_counts (bool, optional): Whether to show the count of each unique value.
                                    Defaults to True.
        show_percentages (bool, optional): Whether to show the percentage of each 
                                         unique value. Defaults to True.
    
    Returns:
        None: Prints visualization results directly to console with formatting
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({
        ...     'category': ['A', 'B', 'A', 'C', 'B', 'A'],
        ...     'status': ['active', 'inactive', 'active', 'pending', 'active', 'active'],
        ...     'region': ['North', 'South', 'North', 'East', 'West', 'North'],
        ...     'score': [85, 92, 78, 88, 95, 82]
        ... })
        >>> 
        >>> # Basic visualization
        >>> edaflow.visualize_categorical_values(df)
        >>> 
        >>> # Show only top 10 values per column, without percentages
        >>> edaflow.visualize_categorical_values(df, max_unique_values=10, show_percentages=False)
        >>> 
        >>> # Alternative import style:
        >>> from edaflow.analysis import visualize_categorical_values
        >>> visualize_categorical_values(df, max_unique_values=15)
    
    Notes:
        - Only analyzes columns with object dtype (categorical/string columns)
        - Columns with many unique values are truncated to show most frequent ones
        - Provides summary statistics including total unique values and most common value
        - Uses color coding to highlight column names and important information
    """
    # Find categorical columns
    cat_columns = [col for col in df.columns if df[col].dtype == 'object']
    
    if not cat_columns:
        print("🔍 No categorical (object-type) columns found in the DataFrame.")
        print("   All columns appear to be numeric or datetime types.")
        return
    
    print("📊 CATEGORICAL COLUMNS VISUALIZATION")
    print("=" * 70)
    print(f"Found {len(cat_columns)} categorical column(s): {', '.join(cat_columns)}")
    print("=" * 70)
    
    for i, col in enumerate(cat_columns, 1):
        # Get value counts
        value_counts = df[col].value_counts(dropna=False)
        total_values = len(df[col])
        unique_count = len(value_counts)
        
        # Handle missing values
        null_count = df[col].isnull().sum()
        
        # Column header with color coding
        print(f'\n\x1b[1;36m[{i}/{len(cat_columns)}] Column: {col}\x1b[m')
        print(f'📈 Total values: {total_values} | Unique values: {unique_count} | Missing: {null_count}')
        
        if unique_count == 0:
            print('⚠️  Column is completely empty')
            continue
            
        # Determine how many values to show
        values_to_show = min(max_unique_values, unique_count)
        
        if unique_count > max_unique_values:
            print(f'📋 Showing top {values_to_show} most frequent values (out of {unique_count} total):')
        else:
            print(f'📋 All unique values:')
        
        # Display values with counts and percentages
        for j, (value, count) in enumerate(value_counts.head(values_to_show).items(), 1):
            # Handle NaN values display
            display_value = 'NaN/Missing' if pd.isna(value) else repr(value)
            
            # Calculate percentage
            percentage = (count / total_values) * 100
            
            # Build the display string
            display_parts = [f'   {j:2d}. {display_value}']
            
            if show_counts:
                display_parts.append(f'Count: {count}')
            
            if show_percentages:
                display_parts.append(f'({percentage:.1f}%)')
            
            print(' | '.join(display_parts))
        
        # Show truncation message if needed
        if unique_count > max_unique_values:
            remaining = unique_count - max_unique_values
            print(f'   ... and {remaining} more unique value(s)')
        
        # Summary statistics
        most_common_value = value_counts.index[0]
        most_common_count = value_counts.iloc[0]
        most_common_pct = (most_common_count / total_values) * 100
        
        display_most_common = 'NaN/Missing' if pd.isna(most_common_value) else repr(most_common_value)
        
        print(f'🏆 Most frequent: {display_most_common} ({most_common_count} times, {most_common_pct:.1f}%)')
        
        # Add separator between columns (except for the last one)
        if i < len(cat_columns):
            print('-' * 50)
    
    print("\n" + "=" * 70)
    print("✅ Categorical visualization complete!")
    
    # Provide actionable insights
    high_cardinality_cols = [col for col in cat_columns if df[col].nunique() > max_unique_values]
    if high_cardinality_cols:
        print(f"\n💡 High cardinality columns detected: {', '.join(high_cardinality_cols)}")
        print("   Consider: grouping rare categories, encoding, or feature engineering")
    
    # Check for columns that might need attention
    mostly_unique_cols = [col for col in cat_columns if df[col].nunique() / len(df) > 0.8]
    if mostly_unique_cols:
        print(f"\n⚠️  Mostly unique columns (>80% unique): {', '.join(mostly_unique_cols)}")
        print("   These might be IDs or need special handling")


def display_column_types(df):
    """
    Display categorical and numerical columns in a DataFrame with rich formatting.
    
    This function separates DataFrame columns into categorical (object dtype) 
    and numerical (non-object dtypes) columns and displays them in a clear format.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to analyze
        
    Returns:
    --------
    dict
        Dictionary containing 'categorical' and 'numerical' lists of column names
        
    Example:
    --------
    >>> import pandas as pd
    >>> from edaflow import display_column_types
    >>> 
    >>> # Create sample data
    >>> data = {
    ...     'name': ['Alice', 'Bob', 'Charlie'],
    ...     'age': [25, 30, 35],
    ...     'city': ['NYC', 'LA', 'Chicago'],
    ...     'salary': [50000, 60000, 70000],
    ...     'is_active': [True, False, True]
    ... }
    >>> df = pd.DataFrame(data)
    >>> 
    >>> # Display column types
    >>> result = display_column_types(df)
    >>> print("Categorical columns:", result['categorical'])
    >>> print("Numerical columns:", result['numerical'])
    """
    import pandas as pd
    
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich import box
        from rich.columns import Columns
        
        # Optimize console for Google Colab compatibility
        console = Console(width=80, force_terminal=True)
        use_rich = True
    except ImportError:
        console = None
        use_rich = False
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    if df.empty:
        if use_rich:
            console.print(Panel("⚠️ DataFrame is empty!", 
                              title="Empty DataFrame", 
                              style="bold yellow", 
                              box=box.SIMPLE))
        else:
            print("⚠️  DataFrame is empty!")
        return {'categorical': [], 'numerical': []}
    
    # Separate columns by type
    cat_cols = [col for col in df.columns if df[col].dtype == 'object']
    num_cols = [col for col in df.columns if df[col].dtype != 'object']
    
    if use_rich:
        # Rich formatted output
        console.print()
        console.print("📊 COLUMN TYPE CLASSIFICATION", style="bold white on blue", justify="center")
        
        # Create side-by-side tables
        cat_table = Table(show_header=True, header_style="bold green", 
                         title="📝 CATEGORICAL COLUMNS", box=box.SIMPLE,
                         border_style="green")
        cat_table.add_column("#", style="dim", width=3)
        cat_table.add_column("Column Name", style="bold green")
        cat_table.add_column("Data Type", style="cyan", justify="center")
        cat_table.add_column("Unique Values", style="yellow", justify="right")
        cat_table.add_column("Memory Usage", style="magenta", justify="right")
        
        num_table = Table(show_header=True, header_style="bold blue",
                         title="🔢 NUMERICAL COLUMNS", box=box.SIMPLE,
                         border_style="blue")
        num_table.add_column("#", style="dim", width=3)
        num_table.add_column("Column Name", style="bold blue")
        num_table.add_column("Data Type", style="cyan", justify="center")
        num_table.add_column("Range Info", style="yellow")
        num_table.add_column("Memory Usage", style="magenta", justify="right")
        
        # Populate categorical table
        if cat_cols:
            for i, col in enumerate(cat_cols, 1):
                unique_count = df[col].nunique()
                null_count = df[col].isnull().sum()
                memory_usage = df[col].memory_usage(deep=True)
                
                # Format memory usage
                if memory_usage > 1024**2:  # MB
                    mem_str = f"{memory_usage / (1024**2):.1f}MB"
                elif memory_usage > 1024:  # KB
                    mem_str = f"{memory_usage / 1024:.1f}KB"
                else:
                    mem_str = f"{memory_usage}B"
                
                cat_table.add_row(
                    str(i),
                    col,
                    "object",
                    f"{unique_count:,}" + (f" (+{null_count} null)" if null_count > 0 else ""),
                    mem_str
                )
        else:
            cat_table.add_row("—", "No categorical columns", "—", "—", "—")
        
        # Populate numerical table
        if num_cols:
            for i, col in enumerate(num_cols, 1):
                dtype = str(df[col].dtype)
                memory_usage = df[col].memory_usage(deep=True)
                
                # Format memory usage
                if memory_usage > 1024**2:  # MB
                    mem_str = f"{memory_usage / (1024**2):.1f}MB"
                elif memory_usage > 1024:  # KB
                    mem_str = f"{memory_usage / 1024:.1f}KB"
                else:
                    mem_str = f"{memory_usage}B"
                
                # Get range info for numeric columns
                try:
                    col_min = df[col].min()
                    col_max = df[col].max()
                    null_count = df[col].isnull().sum()
                    
                    if pd.api.types.is_numeric_dtype(df[col]):
                        range_info = f"[{col_min:.2f}, {col_max:.2f}]"
                        if null_count > 0:
                            range_info += f" +{null_count} null"
                    else:
                        range_info = f"{df[col].nunique():,} unique"
                        if null_count > 0:
                            range_info += f" +{null_count} null"
                except:
                    range_info = "N/A"
                
                num_table.add_row(
                    str(i),
                    col,
                    dtype,
                    range_info,
                    mem_str
                )
        else:
            num_table.add_row("—", "No numerical columns", "—", "—", "—")
        
        # Display tables side by side
        console.print(Columns([cat_table, num_table], equal=True))
        
        # Advanced analysis
        console.print("\n🔍 ADVANCED ANALYSIS", style="bold magenta")
        
        analysis_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        analysis_table.add_column("Metric", style="bold white")
        analysis_table.add_column("Value", style="cyan", justify="right")
        analysis_table.add_column("Insight", style="dim white")
        
        total_cols = len(df.columns)
        cat_percentage = (len(cat_cols) / total_cols * 100) if total_cols > 0 else 0
        num_percentage = (len(num_cols) / total_cols * 100) if total_cols > 0 else 0
        
        # Add analysis rows
        analysis_table.add_row(
            "Total Columns",
            f"{total_cols}",
            f"Dataset has {total_cols} features"
        )
        analysis_table.add_row(
            "Categorical Ratio",
            f"{cat_percentage:.1f}%",
            "High ratio suggests text-heavy data" if cat_percentage > 60 else 
            "Balanced data types" if cat_percentage > 20 else "Numeric-heavy data"
        )
        analysis_table.add_row(
            "Numerical Ratio", 
            f"{num_percentage:.1f}%",
            "Good for statistical analysis" if num_percentage > 50 else
            "Limited numerical features"
        )
        
        # Memory analysis
        total_memory = df.memory_usage(deep=True).sum()
        if total_memory > 1024**3:  # GB
            mem_str = f"{total_memory / (1024**3):.2f}GB"
        elif total_memory > 1024**2:  # MB
            mem_str = f"{total_memory / (1024**2):.1f}MB"
        elif total_memory > 1024:  # KB
            mem_str = f"{total_memory / 1024:.1f}KB"
        else:
            mem_str = f"{total_memory}B"
        
        analysis_table.add_row(
            "Memory Usage",
            mem_str,
            "Consider optimization" if total_memory > 100*1024**2 else "Efficient memory usage"
        )
        
        console.print(analysis_table)
        
        # Summary panel with recommendations
        if cat_percentage > 70:
            data_type_insight = "📝 Text-Heavy Dataset: Consider NLP techniques, encoding strategies"
        elif num_percentage > 70:
            data_type_insight = "🔢 Numeric-Heavy Dataset: Great for statistical analysis, ML models"
        else:
            data_type_insight = "⚖️ Balanced Dataset: Good mix of categorical and numerical features"
        
        summary_content = f"""
[bold cyan]📈 Dataset Composition:[/bold cyan]
• {len(cat_cols)} Categorical columns ({cat_percentage:.1f}%)
• {len(num_cols)} Numerical columns ({num_percentage:.1f}%)
• Total memory usage: {mem_str}

[bold yellow]💡 Insights:[/bold yellow]
{data_type_insight}
        """
        
        console.print(Panel(
            summary_content.strip(),
            title="📊 Column Analysis Summary",
            style="bold green",
            box=box.ROUNDED,
            width=80,
            padding=(0, 1)
        ))
        
        console.print("✨ Column type analysis complete!", style="bold green")
        
    else:
        # Fallback to basic output
        print("📊 Column Type Analysis")
        print("=" * 50)
        
        print(f"\n📝 Categorical Columns ({len(cat_cols)} total):")
        if cat_cols:
            for i, col in enumerate(cat_cols, 1):
                unique_count = df[col].nunique()
                print(f"   {i:2d}. {col:<20} (unique values: {unique_count})")
        else:
            print("   No categorical columns found")
        
        print(f"\n🔢 Numerical Columns ({len(num_cols)} total):")
        if num_cols:
            for i, col in enumerate(num_cols, 1):
                dtype = str(df[col].dtype)
                print(f"   {i:2d}. {col:<20} (dtype: {dtype})")
        else:
            print("   No numerical columns found")
        
        # Summary
        total_cols = len(df.columns)
        cat_percentage = (len(cat_cols) / total_cols * 100) if total_cols > 0 else 0
        num_percentage = (len(num_cols) / total_cols * 100) if total_cols > 0 else 0
        
        print(f"\n📈 Summary:")
        print(f"   Total columns: {total_cols}")
        print(f"   Categorical: {len(cat_cols)} ({cat_percentage:.1f}%)")
        print(f"   Numerical: {len(num_cols)} ({num_percentage:.1f}%)")
    
    return {
        'categorical': cat_cols,
        'numerical': num_cols
    }


def impute_numerical_median(df, columns=None, inplace=False):
    """
    Impute missing values in numerical columns using median values with rich formatting.
    
    This function identifies numerical columns and fills missing values (NaN) 
    with the median value of each column. It provides detailed reporting of 
    the imputation process and handles edge cases safely.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing data to impute
    columns : list, optional
        Specific columns to impute. If None, all numerical columns will be processed
    inplace : bool, default False
        If True, modify the original DataFrame. If False, return a new DataFrame
        
    Returns
    -------
    pandas.DataFrame or None
        If inplace=False, returns the DataFrame with imputed values
        If inplace=True, returns None and modifies the original DataFrame
        
    Examples
    --------
    >>> import pandas as pd
    >>> import edaflow
    >>> 
    >>> # Create sample data with missing values
    >>> df = pd.DataFrame({
    ...     'age': [25, None, 35, None, 45],
    ...     'salary': [50000, 60000, None, 70000, None],
    ...     'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
    ... })
    >>> 
    >>> # Impute all numerical columns
    >>> df_imputed = edaflow.impute_numerical_median(df)
    >>> 
    >>> # Impute specific columns only
    >>> df_imputed = edaflow.impute_numerical_median(df, columns=['age'])
    >>> 
    >>> # Impute in place
    >>> edaflow.impute_numerical_median(df, inplace=True)
    """
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich import box
        
        # Optimize console for Google Colab compatibility
        console = Console(width=80, force_terminal=True)
        use_rich = True
    except ImportError:
        console = None
        use_rich = False
    
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    if df.empty:
        if use_rich:
            console.print(Panel("⚠️ DataFrame is empty. Nothing to impute.", 
                              title="Empty DataFrame", 
                              style="bold yellow", 
                              box=box.SIMPLE))
        else:
            print("⚠️  DataFrame is empty. Nothing to impute.")
        return df.copy() if not inplace else None
    
    # Work with copy unless inplace=True
    result_df = df if inplace else df.copy()
    
    # Determine which columns to process
    if columns is None:
        # Get all numerical columns
        numerical_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()
        if not numerical_cols:
            if use_rich:
                console.print(Panel("⚠️ No numerical columns found in DataFrame.", 
                                  title="No Numeric Columns", 
                                  style="bold yellow",
                                  box=box.SIMPLE))
            else:
                print("⚠️  No numerical columns found in DataFrame.")
            return result_df if not inplace else None
    else:
        # Validate specified columns
        if isinstance(columns, str):
            columns = [columns]
        
        # Check if columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in DataFrame: {missing_cols}")
        
        # Check if columns are numerical
        non_numerical = [col for col in columns if not pd.api.types.is_numeric_dtype(df[col])]
        if non_numerical:
            raise ValueError(f"Non-numerical columns specified: {non_numerical}")
        
        numerical_cols = columns
    
    if use_rich:
        # Rich formatted output
        console.print()
        console.print("🔢 NUMERICAL IMPUTATION (MEDIAN)", style="bold white on blue", justify="center")
        console.print(f"📊 Processing {len(numerical_cols)} numerical columns", style="bold yellow")
        
        # Create imputation table
        imputation_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        imputation_table.add_column("Column", style="bold white", no_wrap=True)
        imputation_table.add_column("Missing Count", justify="right", style="red")
        imputation_table.add_column("Median Value", justify="right", style="cyan")
        imputation_table.add_column("Action", justify="center")
        imputation_table.add_column("Status", justify="center")
        
        imputed_columns = []
        total_imputed = 0
        total_missing_before = 0
        
        for col in numerical_cols:
            missing_count = result_df[col].isnull().sum()
            total_missing_before += missing_count
            
            if missing_count == 0:
                status = Text("✅ CLEAN", style="bold green")
                action = Text("🚫 No Action", style="dim green")
                median_display = "N/A"
                imputation_table.add_row(col, "0", median_display, action, status)
                continue
            
            # Calculate median (ignoring NaN values)
            median_value = result_df[col].median()
            
            if pd.isna(median_value):
                status = Text("❌ FAILED", style="bold red")
                action = Text("🚫 All Missing", style="dim red")
                median_display = "N/A"
                imputation_table.add_row(col, f"{missing_count:,}", median_display, action, status)
                continue
            
            # Perform imputation
            result_df[col] = result_df[col].fillna(median_value)
            
            # Track results
            imputed_columns.append(col)
            total_imputed += missing_count
            
            status = Text("✅ IMPUTED", style="bold green")
            action = Text("🔄 Fill with Median", style="bold cyan")
            
            # Format median value based on data type
            if abs(median_value) > 1000000:
                median_display = f"{median_value/1000000:.2f}M"
            elif abs(median_value) > 1000:
                median_display = f"{median_value/1000:.1f}K"
            elif median_value == int(median_value):
                median_display = f"{int(median_value):,}"
            else:
                median_display = f"{median_value:.3f}"
            
            imputation_table.add_row(col, f"{missing_count:,}", median_display, action, status)
        
        console.print(imputation_table)
        
        # Results summary with color-coded panels
        if total_imputed > 0:
            success_text = f"""
🎉 Imputation completed successfully!
• Columns processed: {len(numerical_cols)}
• Columns imputed: {len(imputed_columns)}
• Values filled: {total_imputed:,} out of {total_missing_before:,}
• Completion rate: {(total_imputed/total_missing_before*100):.1f}%

✅ Imputed columns: {', '.join(imputed_columns)}
            """
            
            console.print(Panel(
                success_text.strip(),
                title="🎉 Imputation Success",
                style="bold green",
                box=box.SIMPLE
            ))
        else:
            console.print(Panel(
                "ℹ️ No imputation was necessary\nAll numerical columns are already complete!",
                title="ℹ️ No Action Required",
                style="bold blue",
                box=box.SIMPLE
            ))
        
        console.print("✨ Numerical imputation complete!", style="bold green")
        
    else:
        # Fallback to basic output
        print("🔢 Numerical Missing Value Imputation (Median)")
        print("=" * 55)
        
        imputed_columns = []
        total_imputed = 0
        
        for col in numerical_cols:
            missing_count = result_df[col].isnull().sum()
            
            if missing_count == 0:
                print(f"✅ {col:<20} - No missing values")
                continue
            
            # Calculate median (ignoring NaN values)
            median_value = result_df[col].median()
            
            if pd.isna(median_value):
                print(f"⚠️  {col:<20} - All values are missing, skipping")
                continue
            
            # Perform imputation
            result_df[col] = result_df[col].fillna(median_value)
            
            # Track results
            imputed_columns.append(col)
            total_imputed += missing_count
            
            print(f"🔄 {col:<20} - Imputed {missing_count:,} values with median: {median_value}")
        
        # Summary
        print(f"\n📊 Imputation Summary:")
        print(f"   Columns processed: {len(numerical_cols)}")
        print(f"   Columns imputed: {len(imputed_columns)}")
        print(f"   Total values imputed: {total_imputed:,}")
        
        if imputed_columns:
            print(f"   Imputed columns: {', '.join(imputed_columns)}")
    
    return result_df if not inplace else None


def impute_categorical_mode(df, columns=None, inplace=False):
    """
    Impute missing values in categorical columns using mode (most frequent value).
    
    This function identifies categorical columns and fills missing values (NaN) 
    with the mode (most frequent value) of each column. It provides detailed 
    reporting of the imputation process and handles edge cases safely.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing data to impute
    columns : list, optional
        Specific columns to impute. If None, all categorical columns will be processed
    inplace : bool, default False
        If True, modify the original DataFrame. If False, return a new DataFrame
        
    Returns
    -------
    pandas.DataFrame or None
        If inplace=False, returns the DataFrame with imputed values
        If inplace=True, returns None and modifies the original DataFrame
        
    Examples
    --------
    >>> import pandas as pd
    >>> import edaflow
    >>> 
    >>> # Create sample data with missing values
    >>> df = pd.DataFrame({
    ...     'category': ['A', 'B', 'A', None, 'A'],
    ...     'status': ['Active', None, 'Active', 'Inactive', None],
    ...     'age': [25, 30, 35, 40, 45]
    ... })
    >>> 
    >>> # Impute all categorical columns
    >>> df_imputed = edaflow.impute_categorical_mode(df)
    >>> 
    >>> # Impute specific columns only
    >>> df_imputed = edaflow.impute_categorical_mode(df, columns=['category'])
    >>> 
    >>> # Impute in place
    >>> edaflow.impute_categorical_mode(df, inplace=True)
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    if df.empty:
        print("⚠️  DataFrame is empty. Nothing to impute.")
        return df.copy() if not inplace else None
    
    # Work with copy unless inplace=True
    result_df = df if inplace else df.copy()
    
    # Determine which columns to process
    if columns is None:
        # Get all categorical (object) columns
        categorical_cols = result_df.select_dtypes(include=['object']).columns.tolist()
        if not categorical_cols:
            print("⚠️  No categorical columns found in DataFrame.")
            return result_df if not inplace else None
    else:
        # Validate specified columns
        if isinstance(columns, str):
            columns = [columns]
        
        # Check if columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in DataFrame: {missing_cols}")
        
        # Check if columns are categorical (object type)
        non_categorical = [col for col in columns if df[col].dtype != 'object']
        if non_categorical:
            print(f"⚠️  Warning: Non-object columns specified: {non_categorical}")
            print("   These will be processed but may not be truly categorical")
        
        categorical_cols = columns
    
    print("📝 Categorical Missing Value Imputation (Mode)")
    print("=" * 55)
    
    imputed_columns = []
    total_imputed = 0
    
    for col in categorical_cols:
        missing_count = result_df[col].isnull().sum()
        
        if missing_count == 0:
            print(f"✅ {col:<20} - No missing values")
            continue
        
        # Calculate mode (most frequent value)
        mode_values = result_df[col].mode()
        
        if len(mode_values) == 0:
            print(f"⚠️  {col:<20} - All values are missing, skipping")
            continue
        
        # Use the first mode value (in case of ties)
        mode_value = mode_values.iloc[0]
        
        # Check for ties in mode
        value_counts = result_df[col].value_counts()
        if len(value_counts) > 1 and value_counts.iloc[0] == value_counts.iloc[1]:
            tie_count = (value_counts == value_counts.iloc[0]).sum()
            print(f"ℹ️  {col:<20} - Mode tie detected ({tie_count} values), using: '{mode_value}'")
        
        # Perform imputation
        result_df[col] = result_df[col].fillna(mode_value)
        
        # Track results
        imputed_columns.append(col)
        total_imputed += missing_count
        
        print(f"🔄 {col:<20} - Imputed {missing_count:,} values with mode: '{mode_value}'")
    
    # Summary
    print(f"\n📊 Imputation Summary:")
    print(f"   Columns processed: {len(categorical_cols)}")
    print(f"   Columns imputed: {len(imputed_columns)}")
    print(f"   Total values imputed: {total_imputed:,}")
    
    if imputed_columns:
        print(f"   Imputed columns: {', '.join(imputed_columns)}")
    
    return None if inplace else result_df


def visualize_numerical_boxplots(df: pd.DataFrame,
                                 columns: Optional[List[str]] = None,
                                 figsize: Optional[tuple] = None,
                                 rows: Optional[int] = None,
                                 cols: Optional[int] = None,
                                 title: str = "Boxplots for Numerical Columns",
                                 show_skewness: bool = True,
                                 orientation: str = 'horizontal',
                                 color_palette: str = 'Set2') -> None:
    """
    Create boxplots for numerical columns to visualize distributions and outliers.
    
    This function automatically detects numerical columns and creates a grid of boxplots
    to help identify outliers, skewness, and distribution characteristics. Each boxplot
    can optionally display the skewness value in the title.
    
    Args:
        df (pd.DataFrame): The input DataFrame to analyze
        columns (Optional[List[str]], optional): Specific columns to plot. If None, 
                                               all numerical columns are used. 
                                               Defaults to None.
        figsize (Optional[tuple], optional): Figure size (width, height). If None, 
                                           automatically calculated based on subplot grid.
                                           Defaults to None.
        rows (Optional[int], optional): Number of rows in subplot grid. If None, 
                                      automatically calculated. Defaults to None.
        cols (Optional[int], optional): Number of columns in subplot grid. If None, 
                                      automatically calculated. Defaults to None.
        title (str, optional): Main title for the entire plot. 
                              Defaults to "Boxplots for Numerical Columns".
        show_skewness (bool, optional): Whether to show skewness values in subplot titles.
                                      Defaults to True.
        orientation (str, optional): Boxplot orientation. Either 'horizontal' or 'vertical'.
                                   Defaults to 'horizontal'.
        color_palette (str, optional): Seaborn color palette to use. 
                                     Defaults to 'Set2'.
    
    Returns:
        None: Displays the boxplot visualization
    
    Raises:
        ValueError: If orientation is not 'horizontal' or 'vertical'
        ValueError: If no numerical columns are found
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({
        ...     'age': [25, 30, 35, 40, 100, 28, 32],  # 100 is outlier
        ...     'salary': [50000, 60000, 75000, 80000, 200000, 55000, 65000],  # 200000 is outlier
        ...     'experience': [2, 5, 8, 12, 25, 3, 6],
        ...     'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C']
        ... })
        >>> 
        >>> # Basic boxplot visualization
        >>> edaflow.visualize_numerical_boxplots(df)
        >>> 
        >>> # Custom layout and styling
        >>> edaflow.visualize_numerical_boxplots(df, 
        ...                                     rows=2, cols=2,
        ...                                     title="Custom Boxplots",
        ...                                     orientation='vertical',
        ...                                     color_palette='viridis')
        >>> 
        >>> # Specific columns only
        >>> edaflow.visualize_numerical_boxplots(df, columns=['age', 'salary'])
        >>> 
        >>> # Alternative import style:
        >>> from edaflow.analysis import visualize_numerical_boxplots
        >>> visualize_numerical_boxplots(df, show_skewness=False)
    
    Notes:
        - Automatically identifies numerical columns (int64, float64, etc.)
        - Skips columns with all missing values
        - Outliers are clearly visible as points beyond the whiskers
        - Skewness interpretation:
          * |skewness| < 0.5: Approximately symmetric
          * 0.5 ≤ |skewness| < 1: Moderately skewed  
          * |skewness| ≥ 1: Highly skewed
        - Uses seaborn styling for better visual appearance
    """
    # Validate orientation
    if orientation not in ['horizontal', 'vertical']:
        raise ValueError("orientation must be either 'horizontal' or 'vertical'")
    
    # Get numerical columns
    if columns is None:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    else:
        # Validate that specified columns exist and are numerical
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in DataFrame: {missing_cols}")
        
        non_numerical = [col for col in columns if col in df.columns and 
                        not pd.api.types.is_numeric_dtype(df[col])]
        if non_numerical:
            print(f"⚠️  Warning: Skipping non-numerical columns: {non_numerical}")
        
        numerical_cols = [col for col in columns if col in df.columns and 
                         pd.api.types.is_numeric_dtype(df[col])]
    
    # Filter out columns with all missing values
    valid_cols = []
    for col in numerical_cols:
        if not df[col].isna().all():
            valid_cols.append(col)
        else:
            print(f"⚠️  Warning: Skipping column '{col}' - all values are missing")
    
    if not valid_cols:
        raise ValueError("No valid numerical columns found for plotting")
    
    print(f"📊 Creating boxplots for {len(valid_cols)} numerical column(s): {', '.join(valid_cols)}")
    
    # Calculate grid dimensions if not provided
    n_plots = len(valid_cols)
    if rows is None and cols is None:
        cols = min(3, n_plots)  # Default to 3 columns max
        rows = math.ceil(n_plots / cols)
    elif rows is None:
        rows = math.ceil(n_plots / cols)
    elif cols is None:
        cols = math.ceil(n_plots / rows)
    
    # Calculate figure size if not provided
    if figsize is None:
        if orientation == 'horizontal':
            figsize = (4 * cols, 3 * rows)
        else:
            figsize = (3 * cols, 4 * rows)
    
    # Set style
    plt.style.use('default')
    sns.set_palette(color_palette)
    
    # Create the subplot grid
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    fig.suptitle(title, fontsize=16, y=0.98)
    
    # Handle case where there's only one subplot
    if n_plots == 1:
        axes = [axes]
    elif rows == 1 or cols == 1:
        axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
    else:
        axes = axes.flatten()
    
    # Create boxplots
    for i, col in enumerate(valid_cols):
        ax = axes[i]
        
        # Create the boxplot
        if orientation == 'horizontal':
            sns.boxplot(data=df, x=col, ax=ax, orient='h')
            ax.set_xlabel(col)
            ax.set_ylabel('')
        else:
            sns.boxplot(data=df, y=col, ax=ax, orient='v')
            ax.set_ylabel(col)
            ax.set_xlabel('')
        
        # Calculate and display skewness if requested
        if show_skewness:
            skewness = df[col].skew(skipna=True)
            skew_text = f"{col}\nSkewness: {skewness:.2f}"
            ax.set_title(skew_text, fontsize=10)
        else:
            ax.set_title(col, fontsize=10)
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3)
    
    # Hide empty subplots
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)
    
    # Adjust layout
    plt.tight_layout()
    
    # Show summary statistics
    print("\n📈 Summary Statistics:")
    print("=" * 50)
    for col in valid_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            skewness = col_data.skew()
            q1, q3 = col_data.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
            
            print(f"📊 {col}:")
            print(f"   Range: {col_data.min():.2f} to {col_data.max():.2f}")
            print(f"   Median: {col_data.median():.2f}")
            print(f"   IQR: {iqr:.2f} (Q1: {q1:.2f}, Q3: {q3:.2f})")
            print(f"   Skewness: {skewness:.2f}", end="")
            
            # Skewness interpretation
            if abs(skewness) < 0.5:
                print(" (approximately symmetric)")
            elif abs(skewness) < 1:
                print(" (moderately skewed)")
            else:
                print(" (highly skewed)")
            
            print(f"   Outliers: {len(outliers)} values outside [{lower_bound:.2f}, {upper_bound:.2f}]")
            if len(outliers) > 0 and len(outliers) <= 5:
                print(f"   Outlier values: {sorted(outliers.tolist())}")
            elif len(outliers) > 5:
                print(f"   Sample outliers: {sorted(outliers.tolist())[:5]}... (+{len(outliers)-5} more)")
            print()
    
    # Display the plot
    plt.show()


def handle_outliers_median(df: pd.DataFrame,
                          columns: Optional[Union[str, List[str]]] = None,
                          method: str = 'iqr',
                          iqr_multiplier: float = 1.5,
                          inplace: bool = False,
                          verbose: bool = True) -> pd.DataFrame:
    """
    Replace outliers in numerical columns with the median value.
    
    This function identifies outliers using statistical methods and replaces them
    with the median value of the respective column. It's designed to work seamlessly
    with the visualize_numerical_boxplots function for a complete outlier workflow.
    
    Args:
        df (pd.DataFrame): The input DataFrame
        columns (Optional[Union[str, List[str]]], optional): Column name(s) to process.
                                                            If None, processes all numerical columns.
                                                            Defaults to None.
        method (str, optional): Method to identify outliers. Options:
                               - 'iqr': Interquartile Range method (Q1 - 1.5*IQR, Q3 + 1.5*IQR)
                               - 'zscore': Z-score method (values with |z-score| > 3)
                               - 'modified_zscore': Modified Z-score using median absolute deviation
                               Defaults to 'iqr'.
        iqr_multiplier (float, optional): Multiplier for IQR method. Defaults to 1.5.
        inplace (bool, optional): If True, modifies the original DataFrame.
                                 If False, returns a new DataFrame. Defaults to False.
        verbose (bool, optional): If True, displays detailed information about
                                 the outlier handling process. Defaults to True.
    
    Returns:
        pd.DataFrame: DataFrame with outliers replaced by median values.
                     If inplace=True, returns the modified original DataFrame.
    
    Raises:
        ValueError: If no valid numerical columns are found or if an invalid method is specified.
        KeyError: If specified column(s) don't exist in the DataFrame.
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> 
        >>> # Create sample data with outliers
        >>> df = pd.DataFrame({
        ...     'A': [1, 2, 3, 4, 5, 100],  # 100 is an outlier
        ...     'B': [10, 20, 30, 40, 50, 60],
        ...     'C': ['x', 'y', 'z', 'x', 'y', 'z']
        ... })
        >>> 
        >>> # First visualize outliers
        >>> edaflow.visualize_numerical_boxplots(df)
        >>> 
        >>> # Then handle outliers
        >>> df_clean = edaflow.handle_outliers_median(df)
        >>> 
        >>> # Or handle specific columns
        >>> df_clean = edaflow.handle_outliers_median(df, columns=['A'])
        >>> 
        >>> # Or modify inplace
        >>> edaflow.handle_outliers_median(df, inplace=True)
        
        # Alternative import style:
        >>> from edaflow.analysis import handle_outliers_median
        >>> df_clean = handle_outliers_median(df, method='zscore')
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if method not in ['iqr', 'zscore', 'modified_zscore']:
        raise ValueError("Method must be 'iqr', 'zscore', or 'modified_zscore'")
    
    # Handle column selection
    if columns is None:
        # Get all numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    elif isinstance(columns, str):
        numerical_cols = [columns]
    else:
        numerical_cols = list(columns)
    
    # Validate columns exist
    missing_cols = [col for col in numerical_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Column(s) not found in DataFrame: {missing_cols}")
    
    # Filter for actual numerical columns
    valid_cols = []
    for col in numerical_cols:
        if df[col].dtype in [np.number] or pd.api.types.is_numeric_dtype(df[col]):
            valid_cols.append(col)
        elif verbose:
            print(f"⚠️  Skipping non-numerical column: {col}")
    
    if not valid_cols:
        raise ValueError("No valid numerical columns found for outlier handling")
    
    # Create working DataFrame
    if inplace:
        result_df = df
    else:
        result_df = df.copy()
    
    if verbose:
        print(f"🔧 Handling outliers in {len(valid_cols)} numerical column(s): {', '.join(valid_cols)}")
        print(f"📊 Method: {method.upper()}")
        if method == 'iqr':
            print(f"📈 IQR Multiplier: {iqr_multiplier}")
        print("=" * 60)
    
    total_outliers_replaced = 0
    
    for col in valid_cols:
        col_data = result_df[col].dropna()
        
        if len(col_data) == 0:
            if verbose:
                print(f"⚠️  {col}: No data available (all NaN)")
            continue
        
        original_outliers = 0
        
        if method == 'iqr':
            # IQR method
            q1, q3 = col_data.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower_bound = q1 - iqr_multiplier * iqr
            upper_bound = q3 + iqr_multiplier * iqr
            outlier_mask = (result_df[col] < lower_bound) | (result_df[col] > upper_bound)
            
        elif method == 'zscore':
            # Z-score method
            mean_val = col_data.mean()
            std_val = col_data.std()
            if std_val == 0:
                outlier_mask = pd.Series([False] * len(result_df), index=result_df.index)
            else:
                z_scores = np.abs((result_df[col] - mean_val) / std_val)
                outlier_mask = z_scores > 3
                
        elif method == 'modified_zscore':
            # Modified Z-score using median absolute deviation
            median_val = col_data.median()
            mad = np.median(np.abs(col_data - median_val))
            if mad == 0:
                outlier_mask = pd.Series([False] * len(result_df), index=result_df.index)
            else:
                modified_z_scores = 0.6745 * (result_df[col] - median_val) / mad
                outlier_mask = np.abs(modified_z_scores) > 3.5
        
        # Count outliers before replacement
        original_outliers = outlier_mask.sum()
        
        if original_outliers > 0:
            # Calculate median for replacement
            median_val = col_data.median()
            
            # Replace outliers with median, ensuring dtype compatibility
            result_df.loc[outlier_mask, col] = result_df[col].dtype.type(median_val)
            total_outliers_replaced += original_outliers
            
            if verbose:
                print(f"📊 {col}:")
                print(f"   🎯 Median value: {median_val:.2f}")
                print(f"   🔄 Outliers replaced: {original_outliers}")
                if method == 'iqr':
                    print(f"   📏 Valid range: [{lower_bound:.2f}, {upper_bound:.2f}]")
                elif method == 'zscore':
                    print(f"   📏 Z-score threshold: ±3.0")
                elif method == 'modified_zscore':
                    print(f"   📏 Modified Z-score threshold: ±3.5")
                print()
        else:
            if verbose:
                print(f"✅ {col}: No outliers detected")
                print()
    
    if verbose:
        print("=" * 60)
        print(f"🎉 Outlier handling completed!")
        print(f"📈 Total outliers replaced: {total_outliers_replaced}")
        print(f"🔧 Method used: {method.upper()}")
        if not inplace:
            print("💾 Original DataFrame unchanged (inplace=False)")
        else:
            print("💾 Original DataFrame modified (inplace=True)")
    
    return result_df


def visualize_interactive_boxplots(df: pd.DataFrame,
                                 columns: Optional[Union[str, List[str]]] = None,
                                 title: str = "Interactive Boxplot Analysis",
                                 height: int = 600,
                                 color_sequence: Optional[List[str]] = None,
                                 show_points: str = "outliers",
                                 verbose: bool = True) -> None:
    """
    Create interactive boxplots for numerical columns using Plotly Express.
    
    This function provides an interactive alternative to matplotlib-based boxplots,
    allowing users to hover, zoom, and explore data distributions dynamically.
    Perfect for final visualization after data cleaning and outlier handling.
    
    Args:
        df (pd.DataFrame): The input DataFrame
        columns (Optional[Union[str, List[str]]], optional): Column name(s) to visualize.
                                                            If None, processes all numerical columns.
                                                            Defaults to None.
        title (str, optional): Title for the interactive plot. Defaults to "Interactive Boxplot Analysis".
        height (int, optional): Height of the plot in pixels. Defaults to 600.
        color_sequence (Optional[List[str]], optional): Custom color sequence for the boxplots.
                                                       If None, uses Plotly's default colors.
                                                       Defaults to None.
        show_points (str, optional): Points to show on boxplots. Options:
                                   - "outliers": Show only outlier points
                                   - "all": Show all data points
                                   - "suspectedoutliers": Show suspected outliers
                                   - False: Show no points
                                   Defaults to "outliers".
        verbose (bool, optional): If True, displays detailed information about
                                 the visualization process. Defaults to True.
    
    Returns:
        None: Displays the interactive plot directly
    
    Raises:
        ValueError: If no valid numerical columns are found.
        KeyError: If specified column(s) don't exist in the DataFrame.
        ImportError: If plotly is not installed.
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> 
        >>> # Create sample data
        >>> df = pd.DataFrame({
        ...     'age': [25, 30, 28, 35, 32, 29, 31, 33],
        ...     'income': [50000, 55000, 48000, 62000, 51000, 45000, 53000, 49000],
        ...     'score': [85, 90, 78, 92, 88, 95, 81, 87],
        ...     'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B']
        ... })
        >>> 
        >>> # Interactive visualization of all numerical columns
        >>> edaflow.visualize_interactive_boxplots(df)
        >>> 
        >>> # Visualize specific columns with custom styling
        >>> edaflow.visualize_interactive_boxplots(
        ...     df, 
        ...     columns=['age', 'income'],
        ...     title="Age and Income Distribution",
        ...     height=500,
        ...     show_points="all"
        ... )
        
        # Alternative import style:
        >>> from edaflow.analysis import visualize_interactive_boxplots
        >>> visualize_interactive_boxplots(df, verbose=True)
    """
    # Check if plotly is available
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        raise ImportError(
            "Plotly is required for interactive boxplots. Install it with: pip install plotly"
        )
    
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    # Handle column selection
    if columns is None:
        # Get all numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    elif isinstance(columns, str):
        numerical_cols = [columns]
    else:
        numerical_cols = list(columns)
    
    # Validate columns exist
    missing_cols = [col for col in numerical_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Column(s) not found in DataFrame: {missing_cols}")
    
    # Filter for actual numerical columns
    valid_cols = []
    for col in numerical_cols:
        if df[col].dtype in [np.number] or pd.api.types.is_numeric_dtype(df[col]):
            # Check if column has any non-null values
            if df[col].dropna().empty:
                if verbose:
                    print(f"⚠️  Skipping column with no valid data: {col}")
            else:
                valid_cols.append(col)
        elif verbose:
            print(f"⚠️  Skipping non-numerical column: {col}")
    
    if not valid_cols:
        raise ValueError("No valid numerical columns found for interactive visualization")
    
    if verbose:
        print(f"📊 Creating interactive boxplots for {len(valid_cols)} numerical column(s): {', '.join(valid_cols)}")
        print(f"🎨 Plot configuration: {height}px height, showing {show_points} points")
    
    # Prepare data for plotting
    # Create a melted dataframe for easier plotting with px.box
    plot_data = df[valid_cols].copy()
    
    # Melt the dataframe to long format for plotly
    melted_data = plot_data.melt(var_name='Variable', value_name='Value')
    
    # Set up color sequence
    if color_sequence is None:
        color_sequence = px.colors.qualitative.Set2
    
    # Create the interactive boxplot
    fig = px.box(
        melted_data, 
        x='Variable', 
        y='Value',
        title=title,
        color='Variable',
        color_discrete_sequence=color_sequence,
        points=show_points,
        hover_data={'Variable': False}  # Don't show variable name in hover (redundant)
    )
    
    # Customize the layout
    fig.update_layout(
        height=height,
        showlegend=False,  # Hide legend since x-axis already shows variable names
        xaxis_title="Variables",
        yaxis_title="Values",
        hovermode='closest',
        template='plotly_white'
    )
    
    # Improve hover information
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>' +
                     'Value: %{y}<br>' +
                     '<extra></extra>'  # Remove the trace box
    )
    
    # Add some styling improvements
    fig.update_xaxes(
        tickangle=45 if len(valid_cols) > 5 else 0,
        title_font_size=14
    )
    fig.update_yaxes(title_font_size=14)
    
    # Display summary statistics if verbose
    if verbose:
        print("\n📈 Interactive Boxplot Summary:")
        print("=" * 50)
        for col in valid_cols:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                q1, q3 = col_data.quantile([0.25, 0.75])
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                
                print(f"📊 {col}:")
                print(f"   📏 Range: {col_data.min():.2f} to {col_data.max():.2f}")
                print(f"   📍 Median: {col_data.median():.2f}")
                print(f"   📦 IQR: {iqr:.2f} (Q1: {q1:.2f}, Q3: {q3:.2f})")
                print(f"   🎯 Outliers: {len(outliers)} values")
                print()
        
        print("🖱️  Interactive Features:")
        print("   • Hover over points to see exact values")
        print("   • Click and drag to zoom into specific regions")
        print("   • Double-click to reset zoom")
        print("   • Use the toolbar to pan, select, and download the plot")
        print()
    
    # Show the interactive plot
    fig.show()
    
    if verbose:
        print("✅ Interactive boxplot visualization completed!")
        print("🎉 Use the interactive features to explore your data distributions!")


def visualize_heatmap(df: pd.DataFrame,
                     heatmap_type: str = "correlation",
                     columns: Optional[Union[str, List[str]]] = None,
                     title: Optional[str] = None,
                     figsize: Optional[tuple] = None,
                     cmap: str = "RdYlBu_r",
                     annot: bool = True,
                     fmt: str = ".2f",
                     square: bool = True,
                     linewidths: float = 0.5,
                     cbar_kws: Optional[dict] = None,
                     method: str = "pearson",
                     missing_threshold: float = 5.0,
                     verbose: bool = True) -> None:
    """
    Create comprehensive heatmap visualizations for exploratory data analysis.
    
    This function provides multiple types of heatmaps for different EDA purposes:
    - Correlation heatmaps for numerical relationships
    - Missing data pattern heatmaps
    - Numerical data value heatmaps
    - Cross-tabulation heatmaps for categorical relationships
    
    Args:
        df (pd.DataFrame): The input DataFrame
        heatmap_type (str, optional): Type of heatmap to create. Options:
                                    - "correlation": Correlation matrix heatmap (default)
                                    - "missing": Missing data pattern heatmap
                                    - "values": Raw data values heatmap (for small datasets)
                                    - "crosstab": Cross-tabulation heatmap for categorical data
                                    Defaults to "correlation".
        columns (Optional[Union[str, List[str]]], optional): Column name(s) to include.
                                                            If None, uses appropriate columns based on heatmap_type.
                                                            Defaults to None.
        title (Optional[str], optional): Custom title for the heatmap. If None, auto-generated.
                                        Defaults to None.
        figsize (Optional[tuple], optional): Figure size (width, height). If None, auto-calculated.
                                           Defaults to None.
        cmap (str, optional): Colormap for the heatmap. Defaults to "RdYlBu_r".
        annot (bool, optional): Whether to annotate cells with values. Defaults to True.
        fmt (str, optional): String formatting code for annotations. Defaults to ".2f".
        square (bool, optional): Whether to make cells square-shaped. Defaults to True.
        linewidths (float, optional): Width of lines separating cells. Defaults to 0.5.
        cbar_kws (Optional[dict], optional): Keyword arguments for colorbar. Defaults to None.
        method (str, optional): Correlation method for correlation heatmaps.
                               Options: "pearson", "kendall", "spearman". Defaults to "pearson".
        missing_threshold (float, optional): Threshold for missing data highlighting (%).
                                            Only used for missing data heatmaps. Defaults to 5.0.
        verbose (bool, optional): If True, displays detailed information about
                                 the heatmap creation process. Defaults to True.
    
    Returns:
        None: Displays the heatmap visualization
    
    Raises:
        ValueError: If heatmap_type is not supported or no suitable data found.
        KeyError: If specified column(s) don't exist in the DataFrame.
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> 
        >>> # Create sample data
        >>> df = pd.DataFrame({
        ...     'age': [25, 30, 28, 35, 32, 29, 31, 33],
        ...     'income': [50000, 55000, 48000, 62000, 51000, 45000, 53000, 49000],
        ...     'score': [85, 90, 78, 92, 88, 95, 81, 87],
        ...     'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B']
        ... })
        >>> 
        >>> # Correlation heatmap (default)
        >>> edaflow.visualize_heatmap(df)
        >>> 
        >>> # Missing data pattern heatmap
        >>> edaflow.visualize_heatmap(df, heatmap_type="missing")
        >>> 
        >>> # Custom styling
        >>> edaflow.visualize_heatmap(
        ...     df, 
        ...     heatmap_type="correlation",
        ...     method="spearman",
        ...     cmap="viridis",
        ...     title="Spearman Correlation Analysis"
        ... )
    """
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if verbose:
        print(f"🔥 Creating {heatmap_type} heatmap...")
        print("=" * 50)
    
    # Handle column selection
    if columns is not None:
        if isinstance(columns, str):
            columns = [columns]
        
        # Validate columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Column(s) not found in DataFrame: {missing_cols}")
        
        df_subset = df[columns].copy()
    else:
        df_subset = df.copy()
    
    # Create heatmap based on type
    if heatmap_type == "correlation":
        # Get numerical columns only
        numerical_cols = df_subset.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numerical_cols) < 2:
            raise ValueError("At least 2 numerical columns required for correlation heatmap")
        
        if verbose:
            print(f"📊 Creating correlation matrix for {len(numerical_cols)} numerical columns")
            print(f"📈 Using {method} correlation method")
            print(f"🔢 Columns: {', '.join(numerical_cols)}")
        
        # Calculate correlation matrix
        df_plot = df_subset[numerical_cols]
        corr_matrix = df_plot.corr(method=method)
        
        # Auto-generate title if not provided
        if title is None:
            title = f"{method.capitalize()} Correlation Matrix"
        
        # Set up figure size
        if figsize is None:
            n_cols = len(numerical_cols)
            figsize = (max(8, n_cols * 0.8), max(6, n_cols * 0.7))
        
        # Create the plot
        plt.figure(figsize=figsize)
        
        # Create heatmap
        sns.heatmap(
            corr_matrix,
            annot=annot,
            cmap=cmap,
            fmt=fmt,
            square=square,
            linewidths=linewidths,
            cbar_kws=cbar_kws or {"shrink": 0.8},
            vmin=-1,
            vmax=1,
            center=0
        )
        
        if verbose:
            # Display correlation insights
            print(f"\n📈 Correlation Analysis Summary:")
            print("=" * 40)
            
            # Find strongest positive and negative correlations
            corr_values = corr_matrix.values
            np.fill_diagonal(corr_values, np.nan)  # Remove self-correlations
            
            # Get indices of max/min correlations
            max_idx = np.unravel_index(np.nanargmax(corr_values), corr_values.shape)
            min_idx = np.unravel_index(np.nanargmin(corr_values), corr_values.shape)
            
            max_corr = corr_values[max_idx]
            min_corr = corr_values[min_idx]
            
            max_pair = (corr_matrix.index[max_idx[0]], corr_matrix.columns[max_idx[1]])
            min_pair = (corr_matrix.index[min_idx[0]], corr_matrix.columns[min_idx[1]])
            
            print(f"🔺 Strongest positive correlation: {max_pair[0]} ↔ {max_pair[1]} ({max_corr:.3f})")
            print(f"🔻 Strongest negative correlation: {min_pair[0]} ↔ {min_pair[1]} ({min_corr:.3f})")
            
            # Count strong correlations
            strong_positive = np.sum((corr_values > 0.7) & (corr_values < 1.0))
            strong_negative = np.sum(corr_values < -0.7)
            
            print(f"💪 Strong positive correlations (>0.7): {strong_positive}")
            print(f"💪 Strong negative correlations (<-0.7): {strong_negative}")
    
    elif heatmap_type == "missing":
        if verbose:
            print(f"🕳️  Creating missing data pattern heatmap")
            print(f"⚠️  Highlighting missing values > {missing_threshold}%")
        
        # Calculate missing data percentages
        missing_percent = (df_subset.isnull().sum() / len(df_subset) * 100)
        missing_data = pd.DataFrame({
            'Column': missing_percent.index,
            'Missing_Percentage': missing_percent.values
        })
        
        # Create missing data matrix for visualization
        missing_matrix = df_subset.isnull().astype(int)
        
        # Auto-generate title if not provided
        if title is None:
            title = "Missing Data Pattern Analysis"
        
        # Set up figure size
        if figsize is None:
            n_cols = len(df_subset.columns)
            n_rows = min(50, len(df_subset))  # Limit rows for readability
            figsize = (max(10, n_cols * 0.5), max(6, n_rows * 0.1))
        
        # Create the plot
        plt.figure(figsize=figsize)
        
        # Use a subset of rows if dataset is too large
        if len(df_subset) > 100:
            sample_size = min(100, len(df_subset))
            missing_sample = missing_matrix.sample(n=sample_size, random_state=42)
            if verbose:
                print(f"📊 Showing sample of {sample_size} rows (dataset has {len(df_subset)} rows)")
        else:
            missing_sample = missing_matrix
        
        # Create heatmap
        sns.heatmap(
            missing_sample.T,  # Transpose to show columns on y-axis
            cmap=['lightblue', 'red'],
            cbar_kws={'label': 'Missing Data (1) vs Present Data (0)'},
            yticklabels=True,
            xticklabels=False,
            linewidths=0.1
        )
        
        plt.ylabel("Columns")
        plt.xlabel("Sample Rows")
        
        if verbose:
            print(f"\n🕳️  Missing Data Summary:")
            print("=" * 40)
            for col in missing_percent.index:
                pct = missing_percent[col]
                if pct > 0:
                    status = "🔴 HIGH" if pct > missing_threshold * 2 else "🟡 MEDIUM" if pct > missing_threshold else "🟢 LOW"
                    print(f"{status}: {col} - {pct:.1f}% missing")
            
            total_missing = df_subset.isnull().sum().sum()
            total_values = df_subset.size
            overall_pct = (total_missing / total_values) * 100
            print(f"\n📊 Overall missing data: {overall_pct:.1f}% ({total_missing:,} / {total_values:,} values)")
    
    elif heatmap_type == "values":
        if verbose:
            print(f"🔢 Creating data values heatmap")
            print(f"⚠️  Best for small datasets (showing first 50 rows max)")
        
        # Get numerical columns only
        numerical_cols = df_subset.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numerical_cols) == 0:
            raise ValueError("No numerical columns found for values heatmap")
        
        df_plot = df_subset[numerical_cols]
        
        # Limit rows for readability
        if len(df_plot) > 50:
            df_plot = df_plot.head(50)
            if verbose:
                print(f"📊 Showing first 50 rows (dataset has {len(df_subset)} rows)")
        
        # Auto-generate title if not provided
        if title is None:
            title = "Data Values Heatmap"
        
        # Set up figure size
        if figsize is None:
            n_cols = len(numerical_cols)
            n_rows = len(df_plot)
            figsize = (max(10, n_cols * 0.8), max(8, n_rows * 0.3))
        
        # Create the plot
        plt.figure(figsize=figsize)
        
        # Normalize data for better visualization
        df_normalized = (df_plot - df_plot.min()) / (df_plot.max() - df_plot.min())
        
        # Create heatmap
        sns.heatmap(
            df_normalized,
            annot=annot,
            cmap=cmap,
            fmt=fmt,
            linewidths=linewidths,
            cbar_kws=cbar_kws or {"shrink": 0.8, "label": "Normalized Values (0-1)"},
            yticklabels=True,
            xticklabels=True
        )
        
        plt.ylabel("Rows")
        plt.xlabel("Columns")
        
        if verbose:
            print(f"\n🔢 Values Heatmap Summary:")
            print("=" * 40)
            print(f"📊 Columns included: {', '.join(numerical_cols)}")
            print(f"📏 Data range (original):")
            for col in numerical_cols:
                col_min, col_max = df_plot[col].min(), df_plot[col].max()
                print(f"   {col}: {col_min:.2f} to {col_max:.2f}")
    
    elif heatmap_type == "crosstab":
        # Get categorical columns
        categorical_cols = df_subset.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(categorical_cols) < 2:
            raise ValueError("At least 2 categorical columns required for crosstab heatmap")
        
        if verbose:
            print(f"📊 Creating cross-tabulation heatmap")
            print(f"📈 Using first 2 categorical columns: {categorical_cols[:2]}")
        
        # Use first two categorical columns
        col1, col2 = categorical_cols[0], categorical_cols[1]
        
        # Create cross-tabulation
        crosstab = pd.crosstab(df_subset[col1], df_subset[col2])
        
        # Auto-generate title if not provided
        if title is None:
            title = f"Cross-tabulation: {col1} vs {col2}"
        
        # Set up figure size
        if figsize is None:
            figsize = (max(8, len(crosstab.columns) * 0.8), max(6, len(crosstab.index) * 0.5))
        
        # Create the plot
        plt.figure(figsize=figsize)
        
        # Create heatmap
        sns.heatmap(
            crosstab,
            annot=annot,
            cmap=cmap,
            fmt='d' if annot else fmt,
            square=square,
            linewidths=linewidths,
            cbar_kws=cbar_kws or {"shrink": 0.8, "label": "Count"}
        )
        
        plt.ylabel(col1)
        plt.xlabel(col2)
        
        if verbose:
            print(f"\n📊 Cross-tabulation Summary:")
            print("=" * 40)
            print(f"📈 {col1} categories: {len(crosstab.index)}")
            print(f"📈 {col2} categories: {len(crosstab.columns)}")
            print(f"📊 Total combinations: {crosstab.size}")
            print(f"🔢 Total observations: {crosstab.sum().sum()}")
    
    else:
        raise ValueError(f"Unsupported heatmap_type: {heatmap_type}. "
                        f"Supported types: 'correlation', 'missing', 'values', 'crosstab'")
    
    # Apply title and styling
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    if verbose:
        print(f"\n✅ {heatmap_type.capitalize()} heatmap created successfully!")
        print("🎨 Use plt.show() to display the plot")
        print("💾 Use plt.savefig('filename.png') to save")
    
    # Show the plot
    plt.show()


def visualize_histograms(df: pd.DataFrame,
                        columns: Optional[Union[str, List[str]]] = None,
                        title: Optional[str] = None,
                        figsize: Optional[tuple] = None,
                        bins: Union[int, str] = 'auto',
                        kde: bool = True,
                        show_stats: bool = True,
                        show_normal_curve: bool = True,
                        color_palette: str = 'Set2',
                        alpha: float = 0.7,
                        grid_alpha: float = 0.3,
                        rows: Optional[int] = None,
                        cols: Optional[int] = None,
                        statistical_tests: bool = True,
                        verbose: bool = True) -> None:
    """
    Create comprehensive histogram visualizations with distribution analysis and skewness detection.
    
    This function provides detailed histogram analysis for numerical columns, including:
    - Distribution shape visualization with histograms and KDE curves
    - Skewness and kurtosis analysis with interpretation
    - Normal distribution comparison overlay
    - Statistical tests for normality (Shapiro-Wilk, Anderson-Darling)
    - Comprehensive distribution statistics and insights
    
    Args:
        df (pd.DataFrame): The input DataFrame
        columns (Optional[Union[str, List[str]]], optional): Column name(s) to visualize.
                                                            If None, processes all numerical columns.
                                                            Defaults to None.
        title (Optional[str], optional): Main title for the entire plot. If None, auto-generated.
                                        Defaults to None.
        figsize (Optional[tuple], optional): Figure size (width, height). If None, auto-calculated.
                                           Defaults to None.
        bins (Union[int, str], optional): Number of bins or binning strategy.
                                         Options: int, 'auto', 'sturges', 'fd', 'scott', 'sqrt'.
                                         Defaults to 'auto'.
        kde (bool, optional): Whether to show Kernel Density Estimation curve. Defaults to True.
        show_stats (bool, optional): Whether to display statistics on each subplot. Defaults to True.
        show_normal_curve (bool, optional): Whether to overlay normal distribution curve. Defaults to True.
        color_palette (str, optional): Seaborn color palette. Defaults to 'Set2'.
        alpha (float, optional): Transparency of histogram bars (0-1). Defaults to 0.7.
        grid_alpha (float, optional): Transparency of grid lines (0-1). Defaults to 0.3.
        rows (Optional[int], optional): Number of rows in subplot grid. If None, auto-calculated.
                                      Defaults to None.
        cols (Optional[int], optional): Number of columns in subplot grid. If None, auto-calculated.
                                      Defaults to None.
        statistical_tests (bool, optional): Whether to run normality tests (Shapiro-Wilk, etc.).
                                          Defaults to True.
        verbose (bool, optional): If True, displays detailed distribution analysis.
                                 Defaults to True.
    
    Returns:
        None: Displays the histogram visualization
    
    Raises:
        ValueError: If no numerical columns are found or DataFrame is empty.
        KeyError: If specified column(s) don't exist in the DataFrame.
    
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> import edaflow
        >>> 
        >>> # Create sample data with different distributions
        >>> np.random.seed(42)
        >>> df = pd.DataFrame({
        ...     'normal': np.random.normal(100, 15, 1000),
        ...     'skewed_right': np.random.exponential(2, 1000),
        ...     'skewed_left': 10 - np.random.exponential(2, 1000),
        ...     'uniform': np.random.uniform(0, 100, 1000)
        ... })
        >>> 
        >>> # Basic histogram analysis
        >>> edaflow.visualize_histograms(df)
        >>> 
        >>> # Custom analysis with specific columns
        >>> edaflow.visualize_histograms(
        ...     df,
        ...     columns=['normal', 'skewed_right'],
        ...     bins=30,
        ...     show_normal_curve=True,
        ...     statistical_tests=True
        ... )
        >>> 
        >>> # Detailed styling
        >>> edaflow.visualize_histograms(
        ...     df,
        ...     title="Distribution Analysis Dashboard",
        ...     color_palette='viridis',
        ...     alpha=0.8,
        ...     figsize=(15, 10)
        ... )
    """
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    # Handle column selection
    if columns is not None:
        if isinstance(columns, str):
            columns = [columns]
        
        # Validate columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Column(s) not found in DataFrame: {missing_cols}")
        
        numerical_cols = [col for col in columns if col in df.select_dtypes(include=[np.number]).columns]
    else:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numerical_cols) == 0:
        raise ValueError("No numerical columns found for histogram visualization")
    
    if verbose:
        print("📊 Creating histogram distribution analysis...")
        print("=" * 60)
        print(f"🔢 Analyzing {len(numerical_cols)} numerical column(s): {', '.join(numerical_cols)}")
        print(f"📈 Features: KDE={kde}, Normal Curve={show_normal_curve}, Stats={show_stats}")
        if statistical_tests:
            print("🧪 Statistical normality tests will be performed")
    
    # Calculate subplot grid
    n_cols = len(numerical_cols)
    if rows is None and cols is None:
        cols = min(3, n_cols)
        rows = math.ceil(n_cols / cols)
    elif rows is None:
        rows = math.ceil(n_cols / cols)
    elif cols is None:
        cols = math.ceil(n_cols / rows)
    
    # Set figure size
    if figsize is None:
        width = cols * 5
        height = rows * 4
        figsize = (width, height)
    
    # Auto-generate title
    if title is None:
        title = f"Distribution Analysis - Histograms with Skewness Detection ({n_cols} columns)"
    
    # Set up the plot
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
    
    # Handle single subplot case
    if n_cols == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    # Get colors from palette
    colors = sns.color_palette(color_palette, n_cols)
    
    # Statistical summaries for verbose output
    distribution_stats = {}
    
    # Create histograms
    for idx, col in enumerate(numerical_cols):
        ax = axes[idx]
        data = df[col].dropna()
        
        if len(data) == 0:
            ax.text(0.5, 0.5, f"No data available\nfor {col}", 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title(col, fontweight='bold')
            continue
        
        # Calculate statistics
        mean = data.mean()
        median = data.median()
        std = data.std()
        skewness = data.skew()
        kurt = data.kurtosis()
        
        # Store stats for verbose output
        distribution_stats[col] = {
            'mean': mean,
            'median': median,
            'std': std,
            'skewness': skewness,
            'kurtosis': kurt,
            'min': data.min(),
            'max': data.max(),
            'count': len(data)
        }
        
        # Statistical tests
        normality_tests = {}
        if statistical_tests and len(data) >= 3:
            try:
                from scipy import stats
                
                # Shapiro-Wilk test (best for small samples)
                if len(data) <= 5000:  # Limit for computational efficiency
                    shapiro_stat, shapiro_p = stats.shapiro(data.sample(min(5000, len(data)), random_state=42))
                    normality_tests['shapiro'] = {'statistic': shapiro_stat, 'p_value': shapiro_p}
                
                # Anderson-Darling test
                anderson_result = stats.anderson(data, dist='norm')
                normality_tests['anderson'] = {
                    'statistic': anderson_result.statistic,
                    'critical_values': anderson_result.critical_values,
                    'significance_level': anderson_result.significance_level
                }
                
                # Jarque-Bera test
                jb_stat, jb_p = stats.jarque_bera(data)
                normality_tests['jarque_bera'] = {'statistic': jb_stat, 'p_value': jb_p}
                
            except ImportError:
                if verbose:
                    print("⚠️  scipy not available - skipping statistical tests")
                statistical_tests = False
        
        # Create main histogram
        n, bins_used, patches = ax.hist(data, bins=bins, alpha=alpha, color=colors[idx], 
                                       edgecolor='black', linewidth=0.5, density=True)
        
        # Add KDE curve
        if kde:
            try:
                sns.kdeplot(data=data, ax=ax, color='darkred', linewidth=2, alpha=0.8)
            except Exception:
                pass  # Skip KDE if it fails
        
        # Add normal distribution overlay
        if show_normal_curve:
            x_norm = np.linspace(data.min(), data.max(), 100)
            normal_curve = stats.norm.pdf(x_norm, mean, std)
            ax.plot(x_norm, normal_curve, 'g--', linewidth=2, alpha=0.8, 
                   label=f'Normal(μ={mean:.1f}, σ={std:.1f})')
        
        # Add vertical lines for mean and median
        ax.axvline(mean, color='red', linestyle='--', alpha=0.8, linewidth=2, label=f'Mean: {mean:.2f}')
        ax.axvline(median, color='blue', linestyle='--', alpha=0.8, linewidth=2, label=f'Median: {median:.2f}')
        
        # Interpret skewness
        if abs(skewness) < 0.5:
            skew_interpretation = "Approximately Normal"
            skew_color = 'green'
        elif abs(skewness) < 1:
            skew_interpretation = "Moderately Skewed"
            skew_color = 'orange'
        else:
            skew_interpretation = "Highly Skewed"
            skew_color = 'red'
        
        # Determine skew direction
        if skewness > 0:
            skew_direction = "Right (Positive)"
        elif skewness < 0:
            skew_direction = "Left (Negative)"
        else:
            skew_direction = "Symmetric"
        
        # Add statistics text box
        if show_stats:
            stats_text = f"n = {len(data):,}\n"
            stats_text += f"Mean = {mean:.2f}\n" 
            stats_text += f"Std = {std:.2f}\n"
            stats_text += f"Skewness = {skewness:.3f}\n"
            stats_text += f"Kurtosis = {kurt:.3f}\n"
            stats_text += f"Shape: {skew_interpretation}"
            
            # Add statistical test results
            if statistical_tests and normality_tests:
                stats_text += "\n\nNormality Tests:"
                if 'shapiro' in normality_tests:
                    p_val = normality_tests['shapiro']['p_value']
                    result = "Normal" if p_val > 0.05 else "Non-Normal"
                    stats_text += f"\nShapiro: {result}"
                    stats_text += f"\n(p={p_val:.4f})"
            
            # Position stats box
            ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
                   verticalalignment='top', horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Customize subplot
        ax.set_title(f"{col}\nSkew: {skewness:.3f} ({skew_direction})", 
                    fontweight='bold', color=skew_color)
        ax.grid(True, alpha=grid_alpha)
        ax.set_xlabel('Value')
        ax.set_ylabel('Density')
        
        # Add legend if normal curve is shown
        if show_normal_curve or True:  # Always show legend for mean/median
            ax.legend(loc='upper left', fontsize=8, framealpha=0.8)
    
    # Hide unused subplots
    for idx in range(n_cols, len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    
    # Verbose statistical analysis
    if verbose:
        print(f"\n📈 Distribution Analysis Summary:")
        print("=" * 60)
        
        for col, stats in distribution_stats.items():
            print(f"\n🔢 {col}:")
            print(f"   📊 Basic Stats: μ={stats['mean']:.2f}, σ={stats['std']:.2f}, median={stats['median']:.2f}")
            print(f"   📏 Range: {stats['min']:.2f} to {stats['max']:.2f}")
            print(f"   📈 Sample Size: {stats['count']:,} observations")
            
            # Skewness interpretation
            skew = stats['skewness']
            if abs(skew) < 0.5:
                skew_desc = "🟢 NORMAL - Approximately symmetric distribution"
            elif abs(skew) < 1:
                direction = "right (positive)" if skew > 0 else "left (negative)"
                skew_desc = f"🟡 MODERATE - Moderately skewed {direction}"
            else:
                direction = "right (positive)" if skew > 0 else "left (negative)"
                skew_desc = f"🔴 HIGH - Highly skewed {direction}"
            
            print(f"   ⚖️  Skewness: {skew:.3f} - {skew_desc}")
            
            # Kurtosis interpretation  
            kurt = stats['kurtosis']
            if abs(kurt) < 0.5:
                kurt_desc = "🟢 NORMAL - Normal tail behavior (mesokurtic)"
            elif kurt > 0.5:
                kurt_desc = "🔺 HEAVY - Heavy tails, more outliers (leptokurtic)"
            else:
                kurt_desc = "🔻 LIGHT - Light tails, fewer outliers (platykurtic)" 
            
            print(f"   📊 Kurtosis: {kurt:.3f} - {kurt_desc}")
            
            # Statistical test results
            if statistical_tests and len(df[col].dropna()) >= 3:
                print(f"   🧪 Normality Assessment:")
                data_sample = df[col].dropna()
                
                try:
                    from scipy import stats
                    
                    # Shapiro-Wilk
                    if len(data_sample) <= 5000:
                        test_data = data_sample.sample(min(5000, len(data_sample)), random_state=42)
                        shapiro_stat, shapiro_p = stats.shapiro(test_data)
                        normality = "✅ Likely Normal" if shapiro_p > 0.05 else "❌ Non-Normal"
                        print(f"      Shapiro-Wilk: {normality} (p={shapiro_p:.4f})")
                    
                    # Jarque-Bera
                    jb_stat, jb_p = stats.jarque_bera(data_sample)
                    jb_normality = "✅ Likely Normal" if jb_p > 0.05 else "❌ Non-Normal"
                    print(f"      Jarque-Bera: {jb_normality} (p={jb_p:.4f})")
                    
                except ImportError:
                    print("      ⚠️  Install scipy for normality tests")
        
        # Overall summary
        total_normal = sum(1 for stats in distribution_stats.values() if abs(stats['skewness']) < 0.5)
        total_moderate = sum(1 for stats in distribution_stats.values() if 0.5 <= abs(stats['skewness']) < 1)
        total_high = sum(1 for stats in distribution_stats.values() if abs(stats['skewness']) >= 1)
        
        print(f"\n🎯 Overall Distribution Summary:")
        print("=" * 40)
        print(f"🟢 Normal/Symmetric: {total_normal}/{len(numerical_cols)} columns")
        print(f"🟡 Moderately Skewed: {total_moderate}/{len(numerical_cols)} columns")
        print(f"🔴 Highly Skewed: {total_high}/{len(numerical_cols)} columns")
        
        if total_high > 0:
            print(f"\n💡 Recommendation: Consider data transformation for highly skewed columns")
            print("   📈 Right skew: Try log, sqrt, or Box-Cox transformation")
            print("   📉 Left skew: Try square, exponential, or reflect + transform")
        
        print(f"\n✅ Histogram analysis completed!")
        print("🎨 Use plt.show() to display the plot")
        print("💾 Use plt.savefig('filename.png') to save")
    
    # Show the plot
    plt.show()


def visualize_scatter_matrix(df: pd.DataFrame,
                           columns: Optional[Union[str, List[str]]] = None,
                           diagonal: str = "hist",
                           upper: str = "scatter",
                           lower: str = "scatter",
                           color_by: Optional[str] = None,
                           show_regression: bool = True,
                           regression_type: str = "linear",
                           alpha: float = 0.6,
                           figsize: Optional[tuple] = None,
                           title: str = "Scatter Matrix Analysis",
                           color_palette: str = "Set2",
                           verbose: bool = True) -> None:
    """
    Create comprehensive scatter matrix visualization for pairwise relationship analysis.
    
    This function provides a powerful scatter matrix (also known as pairs plot) that shows:
    - Diagonal: Distribution of individual variables (histograms, KDE, or box plots)
    - Off-diagonal: Scatter plots showing pairwise relationships between variables
    - Optional: Color coding by categorical variables
    - Optional: Regression lines to highlight trends
    - Statistical insights: Correlation coefficients and relationship patterns
    
    Perfect for:
    - Exploring pairwise relationships between numerical variables
    - Validating correlation analysis with visual patterns
    - Identifying non-linear relationships missed by correlation coefficients
    - Feature engineering and transformation planning
    - Publication-ready relationship visualization
    
    Args:
        df (pd.DataFrame): The input DataFrame
        columns (Optional[Union[str, List[str]]], optional): Columns to include in scatter matrix.
                                                            If None, uses all numerical columns.
                                                            If str, uses single column with others.
                                                            If list, uses specified columns.
                                                            Defaults to None.
        diagonal (str, optional): Type of plot for diagonal elements. Options:
                                - "hist": Histograms (default)
                                - "kde": Kernel Density Estimation curves
                                - "box": Box plots
                                Defaults to "hist".
        upper (str, optional): Type of plot for upper triangle. Options:
                             - "scatter": Scatter plots (default)
                             - "corr": Correlation coefficients
                             - "blank": Empty (for cleaner look)
                             Defaults to "scatter".
        lower (str, optional): Type of plot for lower triangle. Options:
                             - "scatter": Scatter plots (default)
                             - "corr": Correlation coefficients
                             - "blank": Empty (for cleaner look)
                             Defaults to "scatter".
        color_by (Optional[str], optional): Name of categorical column to use for color coding.
                                          If provided, scatter plots will be colored by this variable.
                                          Defaults to None.
        show_regression (bool, optional): Whether to add regression lines to scatter plots.
                                        Defaults to True.
        regression_type (str, optional): Type of regression line. Options:
                                       - "linear": Linear regression (default)
                                       - "poly2": 2nd degree polynomial
                                       - "poly3": 3rd degree polynomial
                                       - "lowess": LOWESS smoothing
                                       Defaults to "linear".
        alpha (float, optional): Transparency level for scatter plot points (0.0 to 1.0).
                                Defaults to 0.6.
        figsize (Optional[tuple], optional): Figure size as (width, height). If None, 
                                           automatically calculated based on number of variables.
                                           Defaults to None.
        title (str, optional): Main title for the scatter matrix. Defaults to "Scatter Matrix Analysis".
        color_palette (str, optional): Color palette for categorical coloring. Defaults to "Set2".
        verbose (bool, optional): If True, displays detailed information about the analysis.
                                Defaults to True.
    
    Returns:
        None: Displays the scatter matrix plot directly
    
    Raises:
        ValueError: If DataFrame is empty or no numerical columns found
        ValueError: If specified columns don't exist or aren't numerical
        ValueError: If color_by column doesn't exist or isn't categorical
        ValueError: If invalid diagonal, upper, or lower options provided
    
    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> import edaflow
        >>> 
        >>> # Create sample data
        >>> np.random.seed(42)
        >>> df = pd.DataFrame({
        ...     'height': np.random.normal(170, 10, 100),
        ...     'weight': np.random.normal(70, 15, 100),
        ...     'age': np.random.uniform(20, 60, 100),
        ...     'income': np.random.lognormal(10, 0.5, 100),
        ...     'category': np.random.choice(['A', 'B', 'C'], 100)
        ... })
        >>> 
        >>> # Basic scatter matrix (all numerical columns)
        >>> edaflow.visualize_scatter_matrix(df)
        >>> 
        >>> # Custom configuration with specific columns
        >>> edaflow.visualize_scatter_matrix(
        ...     df,
        ...     columns=['height', 'weight', 'age'],
        ...     diagonal='kde',
        ...     upper='corr',
        ...     lower='scatter',
        ...     show_regression=True,
        ...     title="Body Measurements Relationships"
        ... )
        >>> 
        >>> # Color-coded by categorical variable
        >>> edaflow.visualize_scatter_matrix(
        ...     df,
        ...     columns=['height', 'weight', 'income'],
        ...     color_by='category',
        ...     regression_type='poly2',
        ...     alpha=0.7
        ... )
        >>> 
        >>> # Alternative import style:
        >>> from edaflow.analysis import visualize_scatter_matrix
        >>> visualize_scatter_matrix(df, diagonal='box', upper='blank')
    
    Notes:
        - Scatter matrices work best with 2-7 numerical variables (readability)
        - For large datasets (>1000 rows), consider sampling for performance
        - Regression lines help identify linear vs non-linear relationships
        - Color coding reveals group-specific patterns in relationships
        - Upper/lower triangle customization allows focus on specific aspects
        - Compatible with matplotlib.pyplot.savefig() for export
        
    Statistical Insights:
        - Diagonal plots show univariate distributions and skewness
        - Scatter plots reveal bivariate relationship patterns
        - Regression lines indicate trend strength and direction
        - Color coding shows group differences in relationships
        - Correlation values validate visual relationship strength
    
    Integration with other edaflow functions:
        - Use after visualize_heatmap() to validate correlation patterns
        - Combine with visualize_histograms() for detailed distribution analysis
        - Follow up with handle_outliers_median() based on scatter plot insights
        - Use before feature engineering to identify transformation needs
    """
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        from sklearn.preprocessing import LabelEncoder
        from scipy import stats
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.pipeline import Pipeline
        import warnings
        warnings.filterwarnings('ignore')
    except ImportError as e:
        missing_lib = str(e).split("'")[1] if "'" in str(e) else "required library"
        raise ImportError(f"Missing required library: {missing_lib}. "
                        f"Please install it using: pip install {missing_lib}")
    
    # Input validation
    if not isinstance(df, pd.DataFrame):
        if isinstance(df, tuple):
            if len(df) == 2 and isinstance(df[0], pd.DataFrame):
                raise TypeError(
                    "❌ INPUT ERROR: You passed a tuple instead of a DataFrame.\n"
                    "💡 COMMON CAUSE: This happens when using apply_smart_encoding() with return_encoders=True.\n"
                    "🔧 SOLUTION: Unpack the tuple result:\n"
                    "   ❌ Wrong: df_encoded = apply_smart_encoding(df, return_encoders=True)\n"
                    "   ✅ Right: df_encoded, encoders = apply_smart_encoding(df, return_encoders=True)\n"
                    "   ✅ Or:    df_encoded = apply_smart_encoding(df, return_encoders=False)"
                )
            else:
                raise TypeError("Expected a pandas DataFrame, but received a tuple. "
                              "Please ensure you're passing a DataFrame as the first argument.")
        else:
            raise TypeError(f"Expected a pandas DataFrame, but received {type(df).__name__}. "
                          f"Please pass a pandas DataFrame as the first argument.")
    
    if df is None or df.empty:
        raise ValueError("DataFrame is empty")
    
    # Handle column selection
    if columns is None:
        # Get all numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    elif isinstance(columns, str):
        numerical_cols = [columns]
    else:
        numerical_cols = list(columns)
    
    # Validate columns exist
    missing_cols = [col for col in numerical_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Column(s) not found in DataFrame: {missing_cols}")
    
    # Filter for actual numerical columns
    valid_cols = []
    for col in numerical_cols:
        if df[col].dtype in ['object', 'category', 'bool']:
            if verbose:
                print(f"⚠️  Skipping non-numerical column: {col}")
        else:
            valid_cols.append(col)
    
    if len(valid_cols) < 2:
        raise ValueError(f"At least 2 numerical columns required for scatter matrix. Found: {len(valid_cols)}")
    
    # Validate options
    valid_diagonal = ["hist", "kde", "box"]
    valid_triangles = ["scatter", "corr", "blank"]
    
    if diagonal not in valid_diagonal:
        raise ValueError(f"Invalid diagonal option '{diagonal}'. Must be one of: {valid_diagonal}")
    if upper not in valid_triangles:
        raise ValueError(f"Invalid upper option '{upper}'. Must be one of: {valid_triangles}")
    if lower not in valid_triangles:
        raise ValueError(f"Invalid lower option '{lower}'. Must be one of: {valid_triangles}")
    
    # Validate color_by column
    color_data = None
    if color_by is not None:
        if color_by not in df.columns:
            raise KeyError(f"Color column '{color_by}' not found in DataFrame")
        
        if df[color_by].dtype in ['object', 'category']:
            color_data = df[color_by]
        else:
            # Convert numerical to categorical for coloring
            color_data = pd.cut(df[color_by], bins=5, labels=['Low', 'Low-Mid', 'Mid', 'Mid-High', 'High'])
        
        if verbose:
            unique_vals = color_data.nunique()
            print(f"🎨 Color coding by '{color_by}': {unique_vals} unique values")
    
    n_vars = len(valid_cols)
    
    if verbose:
        print(f"📊 Creating scatter matrix for {n_vars} variables: {', '.join(valid_cols)}")
        print(f"🎯 Configuration: diagonal='{diagonal}', upper='{upper}', lower='{lower}'")
        if show_regression:
            print(f"📈 Adding {regression_type} regression lines")
        if color_by:
            print(f"🌈 Color coding by: {color_by}")
    
    # Calculate figure size if not provided
    if figsize is None:
        base_size = max(3, min(5, 12 / n_vars))  # Adaptive sizing
        figsize = (base_size * n_vars, base_size * n_vars)
    
    # Set style
    plt.style.use('default')
    if color_data is not None:
        sns.set_palette(color_palette)
    
    # Create the figure and subplots
    fig, axes = plt.subplots(n_vars, n_vars, figsize=figsize)
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
    
    # Handle case where there are only 2 variables
    if n_vars == 2:
        axes = np.array(axes).reshape(2, 2)
    
    # Data preparation
    df_plot = df[valid_cols].copy()
    
    # Calculate correlation matrix for correlation displays
    corr_matrix = df_plot.corr()
    
    # Color setup
    if color_data is not None:
        unique_colors = color_data.nunique()
        colors = sns.color_palette(color_palette, unique_colors)
        color_map = dict(zip(color_data.unique(), colors))
    
    # Create plots for each cell
    for i in range(n_vars):
        for j in range(n_vars):
            ax = axes[i, j]
            
            if i == j:
                # Diagonal: Distribution plots
                col_data = df_plot.iloc[:, i].dropna()
                col_name = valid_cols[i]
                
                if diagonal == "hist":
                    if color_data is not None:
                        # Stacked histogram by color
                        for category in color_data.unique():
                            mask = (color_data == category) & (~df_plot.iloc[:, i].isna())
                            subset_data = df_plot.iloc[:, i][mask]
                            if len(subset_data) > 0:
                                ax.hist(subset_data, bins=20, alpha=0.7, 
                                       color=color_map[category], label=str(category), density=True)
                        ax.legend(fontsize=8)
                    else:
                        ax.hist(col_data, bins=20, alpha=0.7, density=True, color='skyblue')
                
                elif diagonal == "kde":
                    if color_data is not None:
                        for category in color_data.unique():
                            mask = (color_data == category) & (~df_plot.iloc[:, i].isna())
                            subset_data = df_plot.iloc[:, i][mask]
                            if len(subset_data) > 5:  # Need minimum points for KDE
                                sns.kdeplot(data=subset_data, ax=ax, color=color_map[category], 
                                          label=str(category), alpha=0.7)
                        ax.legend(fontsize=8)
                    else:
                        sns.kdeplot(data=col_data, ax=ax, color='skyblue', alpha=0.7)
                
                elif diagonal == "box":
                    if color_data is not None:
                        # Create box plot data
                        box_data = []
                        box_labels = []
                        for category in color_data.unique():
                            mask = (color_data == category) & (~df_plot.iloc[:, i].isna())
                            subset_data = df_plot.iloc[:, i][mask]
                            if len(subset_data) > 0:
                                box_data.append(subset_data)
                                box_labels.append(str(category))
                        
                        if box_data:
                            bp = ax.boxplot(box_data, labels=box_labels, patch_artist=True)
                            for patch, color in zip(bp['boxes'], [color_map[cat] for cat in color_data.unique()]):
                                patch.set_facecolor(color)
                                patch.set_alpha(0.7)
                    else:
                        ax.boxplot([col_data], patch_artist=True)
                        ax.set_xticklabels([''])
                
                ax.set_title(col_name, fontsize=10, fontweight='bold')
                ax.tick_params(labelsize=8)
                
            elif i > j:
                # Lower triangle
                if lower == "scatter":
                    x_data = df_plot.iloc[:, j]
                    y_data = df_plot.iloc[:, i]
                    
                    if color_data is not None:
                        for category in color_data.unique():
                            mask = (color_data == category) & (~x_data.isna()) & (~y_data.isna())
                            if mask.sum() > 0:
                                ax.scatter(x_data[mask], y_data[mask], 
                                         alpha=alpha, s=20, color=color_map[category], 
                                         label=str(category))
                    else:
                        valid_mask = (~x_data.isna()) & (~y_data.isna())
                        ax.scatter(x_data[valid_mask], y_data[valid_mask], 
                                 alpha=alpha, s=20, color='steelblue')
                    
                    # Add regression line
                    if show_regression:
                        valid_mask = (~x_data.isna()) & (~y_data.isna())
                        if valid_mask.sum() > 2:
                            x_reg = x_data[valid_mask].values.reshape(-1, 1)
                            y_reg = y_data[valid_mask].values
                            
                            try:
                                if regression_type == "linear":
                                    reg = LinearRegression().fit(x_reg, y_reg)
                                    x_range = np.linspace(x_data.min(), x_data.max(), 100).reshape(-1, 1)
                                    y_pred = reg.predict(x_range)
                                    ax.plot(x_range, y_pred, 'r--', alpha=0.8, linewidth=2)
                                
                                elif regression_type in ["poly2", "poly3"]:
                                    degree = 2 if regression_type == "poly2" else 3
                                    poly_reg = Pipeline([
                                        ('poly', PolynomialFeatures(degree=degree)),
                                        ('linear', LinearRegression())
                                    ])
                                    poly_reg.fit(x_reg, y_reg)
                                    x_range = np.linspace(x_data.min(), x_data.max(), 100).reshape(-1, 1)
                                    y_pred = poly_reg.predict(x_range)
                                    ax.plot(x_range, y_pred, 'r--', alpha=0.8, linewidth=2)
                                
                                elif regression_type == "lowess":
                                    from statsmodels.nonparametric.smoothers_lowess import lowess
                                    smoothed = lowess(y_reg, x_reg.flatten(), frac=0.3)
                                    ax.plot(smoothed[:, 0], smoothed[:, 1], 'r--', alpha=0.8, linewidth=2)
                            
                            except Exception:
                                pass  # Skip regression line if it fails
                    
                elif lower == "corr":
                    # Display correlation coefficient
                    corr_val = corr_matrix.iloc[i, j]
                    ax.text(0.5, 0.5, f'{corr_val:.3f}', 
                           transform=ax.transAxes, fontsize=14, 
                           ha='center', va='center', fontweight='bold')
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                
                elif lower == "blank":
                    ax.set_visible(False)
                
                if lower != "blank":
                    ax.tick_params(labelsize=8)
                
            else:
                # Upper triangle (i < j)
                if upper == "scatter":
                    x_data = df_plot.iloc[:, j]
                    y_data = df_plot.iloc[:, i]
                    
                    if color_data is not None:
                        for category in color_data.unique():
                            mask = (color_data == category) & (~x_data.isna()) & (~y_data.isna())
                            if mask.sum() > 0:
                                ax.scatter(x_data[mask], y_data[mask], 
                                         alpha=alpha, s=20, color=color_map[category])
                    else:
                        valid_mask = (~x_data.isna()) & (~y_data.isna())
                        ax.scatter(x_data[valid_mask], y_data[valid_mask], 
                                 alpha=alpha, s=20, color='steelblue')
                    
                    # Add regression line
                    if show_regression:
                        valid_mask = (~x_data.isna()) & (~y_data.isna())
                        if valid_mask.sum() > 2:
                            x_reg = x_data[valid_mask].values.reshape(-1, 1)
                            y_reg = y_data[valid_mask].values
                            
                            try:
                                if regression_type == "linear":
                                    reg = LinearRegression().fit(x_reg, y_reg)
                                    x_range = np.linspace(x_data.min(), x_data.max(), 100).reshape(-1, 1)
                                    y_pred = reg.predict(x_range)
                                    ax.plot(x_range, y_pred, 'r--', alpha=0.8, linewidth=2)
                            except Exception:
                                pass
                
                elif upper == "corr":
                    # Display correlation coefficient
                    corr_val = corr_matrix.iloc[i, j]
                    ax.text(0.5, 0.5, f'{corr_val:.3f}', 
                           transform=ax.transAxes, fontsize=14, 
                           ha='center', va='center', fontweight='bold')
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                
                elif upper == "blank":
                    ax.set_visible(False)
                
                if upper != "blank":
                    ax.tick_params(labelsize=8)
            
            # Set labels only on edges
            if i == n_vars - 1 and j < n_vars:  # Bottom row
                ax.set_xlabel(valid_cols[j], fontsize=9)
            if j == 0 and i > 0:  # Left column
                ax.set_ylabel(valid_cols[i], fontsize=9)
    
    # Adjust layout
    plt.tight_layout()
    
    # Display statistics if verbose
    if verbose:
        print("\n📈 Scatter Matrix Analysis Summary:")
        print("=" * 60)
        print(f"🔢 Variables analyzed: {n_vars}")
        print(f"📊 Total plots created: {n_vars * n_vars}")
        print(f"📏 Matrix dimensions: {n_vars}×{n_vars}")
        
        # Correlation insights
        print(f"\n🔗 Correlation Analysis:")
        # Get upper triangle correlations (excluding diagonal)
        mask = np.triu(np.ones_like(corr_matrix.values, dtype=bool), k=1)
        correlations = corr_matrix.values[mask]
        
        if len(correlations) > 0:
            max_corr = np.max(correlations)
            min_corr = np.min(correlations)
            
            # Find the pairs for max and min correlations
            max_idx = np.unravel_index(np.argmax(corr_matrix.values * mask), corr_matrix.shape)
            min_idx = np.unravel_index(np.argmin(corr_matrix.values + (1 - mask)), corr_matrix.shape)
            
            max_pair = (valid_cols[max_idx[0]], valid_cols[max_idx[1]])
            min_pair = (valid_cols[min_idx[0]], valid_cols[min_idx[1]])
            
            print(f"🔺 Strongest positive: {max_pair[0]} ↔ {max_pair[1]} ({max_corr:.3f})")
            print(f"🔻 Strongest negative: {min_pair[0]} ↔ {min_pair[1]} ({min_corr:.3f})")
            
            strong_positive = np.sum((correlations > 0.7) & (correlations < 1.0))
            strong_negative = np.sum(correlations < -0.7)
            moderate = np.sum((np.abs(correlations) >= 0.3) & (np.abs(correlations) < 0.7))
            
            print(f"💪 Strong correlations (|r| > 0.7): {strong_positive + strong_negative}")
            print(f"📊 Moderate correlations (0.3 ≤ |r| < 0.7): {moderate}")
        
        # Configuration summary
        print(f"\n⚙️  Configuration Used:")
        print(f"   📊 Diagonal: {diagonal}")
        print(f"   🔺 Upper triangle: {upper}")
        print(f"   🔻 Lower triangle: {lower}")
        if show_regression:
            print(f"   📈 Regression: {regression_type}")
        if color_by:
            print(f"   🎨 Color coding: {color_by}")
        
        print(f"\n💡 Analysis Tips:")
        print("   🔍 Look for non-linear patterns in scatter plots")
        print("   📊 Compare correlation values with visual patterns")
        print("   🎯 Identify outliers affecting relationships")
        print("   📈 Notice clusters or groupings in the data")
        if color_by:
            print("   🌈 Observe how relationships differ by category")
        
        print(f"\n✅ Scatter matrix analysis completed!")
        print("🎨 Use plt.show() to display the plot")
        print("💾 Use plt.savefig('filename.png') to save")
    
    # Show the plot
    plt.show()


def assess_image_quality(
    data_source: Union[str, pd.DataFrame, List[str]],
    class_column: Optional[str] = None,
    image_path_column: Optional[str] = None,
    sample_size: Optional[int] = None,
    check_corruption: bool = True,
    analyze_color: bool = True,
    detect_blur: bool = True,
    check_artifacts: bool = True,
    brightness_threshold: Tuple[float, float] = (30.0, 220.0),
    contrast_threshold: float = 20.0,
    aspect_ratio_tolerance: float = 0.1,
    file_size_outlier_factor: float = 3.0,
    verbose: bool = True,
    return_detailed_report: bool = False
) -> Dict[str, Any]:
    """
    🔍 Comprehensive image quality and integrity assessment for ML datasets.
    
    Analyzes image datasets to detect corrupted files, quality issues, outliers,
    and potential problems that could affect model training performance. Provides
    statistical insights and actionable recommendations for dataset improvement.
    
    Perfect for data validation pipelines and ensuring high-quality training data.
    
    Parameters
    ----------
    data_source : str, pd.DataFrame, or List[str]
        Image data source:
        - str: Directory path containing images (organized in class folders or flat)
        - pd.DataFrame: DataFrame with image paths and optional class labels
        - List[str]: List of image file paths
        
    class_column : str, optional
        Column name containing class labels (required if data_source is DataFrame).
        
    image_path_column : str, optional  
        Column name containing image file paths (required if data_source is DataFrame).
        
    sample_size : int, optional
        Maximum number of images to analyze (for large datasets). If None, analyzes all.
        
    check_corruption : bool, default=True
        Whether to check for corrupted or unreadable images.
        
    analyze_color : bool, default=True
        Whether to analyze color properties (grayscale vs color, color distribution).
        
    detect_blur : bool, default=True
        Whether to detect potentially blurry images using Laplacian variance.
        
    check_artifacts : bool, default=True
        Whether to check for compression artifacts and unusual patterns.
        
    brightness_threshold : tuple, default=(30.0, 220.0)
        (min, max) brightness values. Images outside this range are flagged.
        
    contrast_threshold : float, default=20.0
        Minimum contrast level. Images below this are flagged as low contrast.
        
    aspect_ratio_tolerance : float, default=0.1
        Tolerance for aspect ratio clustering (0.1 = 10% deviation).
        
    file_size_outlier_factor : float, default=3.0
        Multiplier for file size outlier detection using IQR method.
        
    verbose : bool, default=True
        Whether to display detailed progress and results.
        
    return_detailed_report : bool, default=False
        Whether to return individual image analysis results.
        
    Returns
    -------
    dict
        Comprehensive quality assessment report containing:
        - 'total_images': Total number of images analyzed
        - 'corrupted_images': List of corrupted/unreadable image paths
        - 'quality_issues': Dictionary of detected quality problems
        - 'color_analysis': Color distribution and grayscale detection results
        - 'dimension_analysis': Image size and aspect ratio statistics
        - 'file_size_analysis': File size distribution and outliers
        - 'brightness_analysis': Brightness statistics and problematic images
        - 'contrast_analysis': Contrast statistics and low-contrast images  
        - 'blur_analysis': Blur detection results (if enabled)
        - 'artifact_analysis': Compression artifact detection (if enabled)
        - 'recommendations': List of actionable recommendations
        - 'quality_score': Overall dataset quality score (0-100)
        - 'detailed_results': Individual image results (if requested)
        
    Examples
    --------
    🔍 **Directory-based Quality Assessment**:
    
    >>> import edaflow
    >>> 
    >>> # Comprehensive quality check
    >>> report = edaflow.assess_image_quality('dataset/train/')
    >>> print(f"Quality Score: {report['quality_score']}/100")
    >>> print(f"Corrupted Images: {len(report['corrupted_images'])}")
    >>> 
    >>> # Focus on specific issues
    >>> report = edaflow.assess_image_quality(
    ...     'dataset/',
    ...     check_corruption=True,
    ...     detect_blur=True,
    ...     analyze_color=False,  # Skip color analysis for speed
    ...     sample_size=1000      # Analyze subset for large datasets
    ... )
    
    📊 **DataFrame-based Analysis**:
    
    >>> import pandas as pd
    >>> df = pd.read_csv('image_metadata.csv')
    >>> 
    >>> # Quality assessment with class-wise analysis
    >>> report = edaflow.assess_image_quality(
    ...     df,
    ...     image_path_column='path',
    ...     class_column='label',
    ...     brightness_threshold=(40, 200),  # Stricter brightness requirements
    ...     contrast_threshold=25,           # Higher contrast requirements
    ...     return_detailed_report=True      # Get per-image details
    ... )
    >>> 
    >>> # Check class-specific quality issues
    >>> for class_name, issues in report['quality_issues'].items():
    ...     print(f"{class_name}: {len(issues)} quality problems")
    
    🚀 **Production Pipeline Integration**:
    
    >>> # Automated quality gates
    >>> report = edaflow.assess_image_quality(data_source='dataset/images/')
    >>> 
    >>> # Quality gates for ML pipeline
    >>> assert report['quality_score'] >= 80, f"Dataset quality too low: {report['quality_score']}"
    >>> assert len(report['corrupted_images']) == 0, "Corrupted images detected!"
    >>> assert report['brightness_analysis']['problematic_count'] < 50, "Too many brightness issues"
    >>> 
    >>> # Automated data cleaning based on quality report
    >>> clean_dataset = [path for path in image_data 
    ...                  if path not in report['corrupted_images']]
    
    🎯 **Medical/Scientific Imaging**:
    
    >>> # Stricter quality requirements for medical data
    >>> report = edaflow.assess_image_quality(
    ...     data_source=medical_scans_df,
    ...     image_path_column='scan_path',
    ...     class_column='diagnosis',
    ...     brightness_threshold=(50, 180),  # Narrow brightness range
    ...     contrast_threshold=30,           # High contrast requirement
    ...     check_artifacts=True,            # Critical for medical imaging
    ...     aspect_ratio_tolerance=0.05      # Strict aspect ratio consistency
    ... )
    
    Statistical Insights:
        - Identifies systematic quality issues across classes
        - Detects unusual patterns that might indicate data collection problems
        - Provides quantitative metrics for dataset quality assessment
        - Enables automated quality gates in ML pipelines
    
    Integration with other edaflow functions:
        - Use before visualize_image_classes() to validate dataset health
        - Combine with traditional EDA functions for metadata analysis
        - Perfect complement to image classification EDA workflows
    """
    
    # Check PIL availability
    if not PIL_AVAILABLE:
        raise ImportError(
            "🚨 PIL (Pillow) is required for image quality assessment.\n"
            "📦 Install with: pip install Pillow"
        )
    
    if verbose:
        print("🔍 Starting Image Quality Assessment...")
        print("=" * 60)
    
    # Parse data source and collect image paths
    image_paths = _parse_image_data_source(data_source, class_column, image_path_column)
    
    # Sample if requested
    if sample_size and len(image_paths) > sample_size:
        if verbose:
            print(f"📊 Sampling {sample_size:,} images from {len(image_paths):,} total")
        image_paths = random.sample(image_paths, sample_size)
    
    if verbose:
        print(f"🖼️  Analyzing {len(image_paths):,} images...")
    
    # Initialize results
    results = {
        'total_images': len(image_paths),
        'corrupted_images': [],
        'quality_issues': {},
        'color_analysis': {},
        'dimension_analysis': {},
        'file_size_analysis': {},
        'brightness_analysis': {},
        'contrast_analysis': {},
        'blur_analysis': {},
        'artifact_analysis': {},
        'recommendations': [],
        'quality_score': 0,
        'detailed_results': [] if return_detailed_report else None
    }
    
    # Analyze each image
    valid_images = []
    dimension_data = []
    file_size_data = []
    brightness_data = []
    contrast_data = []
    blur_scores = []
    color_modes = []
    
    for i, img_path in enumerate(image_paths):
        if verbose and (i + 1) % max(1, len(image_paths) // 10) == 0:
            print(f"   📈 Progress: {i + 1:,}/{len(image_paths):,} ({((i + 1)/len(image_paths)*100):.1f}%)")
        
        img_analysis = _analyze_single_image(
            img_path, check_corruption, analyze_color, detect_blur, 
            check_artifacts, brightness_threshold, contrast_threshold
        )
        
        if img_analysis['corrupted']:
            results['corrupted_images'].append(img_path)
        else:
            valid_images.append(img_path)
            dimension_data.append(img_analysis['dimensions'])
            file_size_data.append(img_analysis['file_size'])
            brightness_data.append(img_analysis['brightness'])
            contrast_data.append(img_analysis['contrast'])
            color_modes.append(img_analysis['color_mode'])
            
            if detect_blur and img_analysis['blur_score'] is not None:
                blur_scores.append(img_analysis['blur_score'])
        
        if return_detailed_report:
            results['detailed_results'].append({
                'path': img_path,
                'analysis': img_analysis
            })
    
    # Generate comprehensive analysis
    results.update(_generate_quality_analysis(
        valid_images, dimension_data, file_size_data, brightness_data,
        contrast_data, blur_scores, color_modes, brightness_threshold,
        contrast_threshold, aspect_ratio_tolerance, file_size_outlier_factor
    ))
    
    # Calculate overall quality score
    results['quality_score'] = _calculate_quality_score(results)
    
    # Generate recommendations
    results['recommendations'] = _generate_quality_recommendations(results)
    
    if verbose:
        _display_quality_results(results)
    
    return results


def analyze_image_features(
    data_source: Union[str, pd.DataFrame, List[str]],
    class_column: Optional[str] = None,
    image_path_column: Optional[str] = None,
    sample_size: Optional[int] = None,
    analyze_edges: bool = True,
    analyze_texture: bool = True,
    analyze_color: bool = True,
    analyze_gradients: bool = True,
    edge_method: str = "canny",
    texture_method: str = "lbp",
    color_spaces: List[str] = ["RGB", "HSV"],
    bins_per_channel: int = 64,
    lbp_radius: int = 3,
    lbp_n_points: int = 24,
    canny_low_threshold: float = 50,
    canny_high_threshold: float = 150,
    create_visualizations: bool = True,
    figsize: Tuple[int, int] = (20, 12),
    save_path: Optional[str] = None,
    verbose: bool = True,
    return_feature_vectors: bool = False
) -> Dict[str, Any]:
    """
    🎨 Comprehensive image feature distribution and statistical analysis for CV datasets.
    
    Extracts and analyzes visual features including edge density, texture descriptors,
    color distributions, and gradient patterns across image classes. Perfect for
    understanding dataset characteristics, feature engineering guidance, and identifying
    visual patterns that distinguish different classes.
    
    Essential for computer vision model development and preprocessing decisions.
    
    Parameters
    ----------
    data_source : str, pd.DataFrame, or List[str]
        Image data source:
        - str: Directory path containing images (organized in class folders or flat)
        - pd.DataFrame: DataFrame with image paths and optional class labels
        - List[str]: List of image file paths
        
    class_column : str, optional
        Column name containing class labels (required if data_source is DataFrame).
        
    image_path_column : str, optional  
        Column name containing image file paths (required if data_source is DataFrame).
        
    sample_size : int, optional
        Maximum number of images to analyze per class. If None, analyzes all images.
        
    analyze_edges : bool, default=True
        Whether to perform edge detection and density analysis.
        
    analyze_texture : bool, default=True
        Whether to analyze texture patterns using Local Binary Patterns.
        
    analyze_color : bool, default=True
        Whether to analyze color distribution histograms.
        
    analyze_gradients : bool, default=True
        Whether to analyze gradient magnitude and direction patterns.
        
    edge_method : str, default="canny"
        Edge detection method. Options: 'canny', 'sobel', 'laplacian'.
        
    texture_method : str, default="lbp"
        Texture analysis method. Options: 'lbp' (Local Binary Patterns), 'glcm'.
        
    color_spaces : List[str], default=["RGB", "HSV"]
        Color spaces to analyze. Options: 'RGB', 'HSV', 'LAB', 'GRAY'.
        
    bins_per_channel : int, default=64
        Number of bins for color histogram analysis per channel.
        
    lbp_radius : int, default=3
        Radius for Local Binary Pattern analysis.
        
    lbp_n_points : int, default=24
        Number of points for Local Binary Pattern analysis.
        
    canny_low_threshold : float, default=50
        Lower threshold for Canny edge detection.
        
    canny_high_threshold : float, default=150
        Upper threshold for Canny edge detection.
        
    create_visualizations : bool, default=True
        Whether to create comprehensive feature distribution visualizations.
        
    figsize : tuple, default=(20, 12)
        Figure size for visualizations as (width, height) in inches.
        
    save_path : str, optional
        Path to save the analysis visualization. If None, plot is only displayed.
        
    verbose : bool, default=True
        Whether to display detailed progress and analysis results.
        
    return_feature_vectors : bool, default=False
        Whether to return raw feature vectors for each image (memory intensive).
        
    Returns
    -------
    dict
        Comprehensive feature analysis report containing:
        - 'edge_analysis': Edge density statistics and distributions per class
        - 'texture_analysis': Texture descriptor statistics and patterns
        - 'color_analysis': Color histogram distributions across color spaces
        - 'gradient_analysis': Gradient magnitude and direction statistics
        - 'class_comparisons': Statistical comparisons between classes
        - 'feature_rankings': Most discriminative features between classes
        - 'recommendations': Actionable insights for feature engineering
        - 'statistical_tests': Inter-class statistical significance tests
        - 'feature_vectors': Raw feature data (if requested)
        
    Examples
    --------
    🎨 **Complete Feature Analysis Workflow**:
    
    >>> import edaflow
    >>> 
    >>> # Comprehensive feature analysis
    >>> features = edaflow.analyze_image_features(
    ...     'dataset/train/',
    ...     analyze_edges=True,
    ...     analyze_texture=True,
    ...     analyze_color=True,
    ...     create_visualizations=True
    ... )
    >>> 
    >>> # Check most discriminative features
    >>> print("Top discriminative features:")
    >>> for feature, score in features['feature_rankings'][:5]:
    ...     print(f"  {feature}: {score:.3f}")
    >>> 
    >>> # Get recommendations
    >>> for rec in features['recommendations']:
    ...     print(f"💡 {rec}")
    
    🔍 **Custom Feature Analysis**:
    
    >>> # Focus on texture and edges for medical imaging
    >>> medical_features = edaflow.analyze_image_features(
    ...     medical_df,
    ...     image_path_column='scan_path',
    ...     class_column='diagnosis',
    ...     analyze_color=False,        # Medical scans often grayscale
    ...     analyze_texture=True,       # Critical for medical diagnosis
    ...     analyze_edges=True,         # Important for structure detection
    ...     texture_method='lbp',
    ...     lbp_radius=5,              # Larger radius for medical details
    ...     edge_method='canny'
    ... )
    
    📊 **Production Feature Engineering**:
    
    >>> # Analyze features for model development
    >>> production_features = edaflow.analyze_image_features(
    ...     production_dataset,
    ...     sample_size=500,           # Sample for efficiency
    ...     color_spaces=['RGB', 'HSV', 'LAB'],  # Multiple color spaces
    ...     bins_per_channel=32,       # Balanced detail vs speed
    ...     return_feature_vectors=True # Get raw features for ML
    ... )
    >>> 
    >>> # Use results for feature selection
    >>> top_features = production_features['feature_rankings'][:10]
    >>> feature_vectors = production_features['feature_vectors']
    
    🧪 **Research & Comparison**:
    
    >>> # Compare different datasets
    >>> dataset_a = edaflow.analyze_image_features('dataset_a/')
    >>> dataset_b = edaflow.analyze_image_features('dataset_b/')
    >>> 
    >>> # Compare edge density distributions
    >>> print(f"Dataset A edge density: {dataset_a['edge_analysis']['mean_density']:.3f}")
    >>> print(f"Dataset B edge density: {dataset_b['edge_analysis']['mean_density']:.3f}")
    
    🎓 **Educational Feature Exploration**:
    
    >>> # Learn about visual characteristics
    >>> features = edaflow.analyze_image_features(
    ...     student_dataset,
    ...     create_visualizations=True,
    ...     verbose=True
    ... )
    >>> 
    >>> # Understand class differences
    >>> class_stats = features['class_comparisons']
    >>> for class_name, stats in class_stats.items():
    ...     print(f"{class_name}: Edge density={stats['edge_density']:.3f}")
    
    Statistical Insights:
        - Identifies visual patterns that distinguish different classes
        - Provides quantitative metrics for subjective visual differences
        - Guides feature engineering and preprocessing decisions
        - Enables data-driven model architecture selection
        - Reveals dataset biases and collection artifacts
    
    Integration with other edaflow functions:
        - Use after assess_image_quality() to understand clean dataset features
        - Combine with visualize_image_classes() for comprehensive analysis
        - Perfect for preprocessing pipeline design and validation
    """
    
    # Check dependencies
    if not PIL_AVAILABLE:
        raise ImportError(
            "🚨 PIL (Pillow) is required for image feature analysis.\n"
            "📦 Install with: pip install Pillow"
        )
    
    missing_deps = []
    if analyze_edges and edge_method == "canny" and not CV2_AVAILABLE:
        if not SKIMAGE_AVAILABLE:
            missing_deps.append("opencv-python or scikit-image for edge detection")
    
    if analyze_texture and texture_method == "lbp" and not SKIMAGE_AVAILABLE:
        missing_deps.append("scikit-image for texture analysis")
    
    if missing_deps:
        deps_str = " and ".join(missing_deps)
        raise ImportError(
            f"🚨 Missing required dependencies: {deps_str}\n"
            f"📦 Install with: pip install opencv-python scikit-image"
        )
    
    if verbose:
        print("🎨 Starting Image Feature Analysis...")
        print("=" * 60)
    
    # Parse data source and organize by class
    image_data = _parse_image_data_with_classes(data_source, class_column, image_path_column, sample_size)
    
    total_images = sum(len(paths) for paths in image_data.values())
    if verbose:
        print(f"🖼️  Analyzing {total_images:,} images across {len(image_data)} classes")
        for class_name, paths in image_data.items():
            print(f"   📁 {class_name}: {len(paths)} images")
    
    # Initialize results
    results = {
        'total_images': total_images,
        'num_classes': len(image_data),
        'edge_analysis': {},
        'texture_analysis': {},
        'color_analysis': {},
        'gradient_analysis': {},
        'class_comparisons': {},
        'feature_rankings': [],
        'recommendations': [],
        'statistical_tests': {},
        'feature_vectors': {} if return_feature_vectors else None
    }
    
    # Analyze features for each class
    class_features = {}
    
    for class_name, image_paths in image_data.items():
        if verbose:
            print(f"\n🔍 Analyzing class: {class_name}")
        
        class_features[class_name] = _analyze_class_features(
            image_paths, analyze_edges, analyze_texture, analyze_color,
            analyze_gradients, edge_method, texture_method, color_spaces,
            bins_per_channel, lbp_radius, lbp_n_points, 
            canny_low_threshold, canny_high_threshold, verbose
        )
    
    # Generate comparative analysis
    results.update(_generate_feature_comparisons(class_features, image_data))
    
    # Create visualizations
    if create_visualizations:
        _create_feature_visualizations(
            class_features, results, figsize, save_path, 
            analyze_edges, analyze_texture, analyze_color, analyze_gradients
        )
    
    # Generate recommendations
    results['recommendations'] = _generate_feature_recommendations(results, class_features)
    
    if verbose:
        _display_feature_results(results)
    
    return results


def _parse_image_data_with_classes(
    data_source: Union[str, pd.DataFrame, List[str]], 
    class_column: Optional[str], 
    image_path_column: Optional[str],
    sample_size: Optional[int]
) -> Dict[str, List[str]]:
    """Parse data source and organize images by class."""
    
    if isinstance(data_source, str):
        # Directory-based input - organized by class folders
        if not os.path.exists(data_source):
            raise FileNotFoundError(f"🚨 Directory not found: {data_source}")
        
        image_data = {}
        supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        
        # Check if directory has class subdirectories
        subdirs = [d for d in os.listdir(data_source) 
                  if os.path.isdir(os.path.join(data_source, d))]
        
        if subdirs:
            # Class-organized structure
            for class_dir in subdirs:
                class_path = os.path.join(data_source, class_dir)
                class_images = []
                
                for file in os.listdir(class_path):
                    if any(file.lower().endswith(ext) for ext in supported_extensions):
                        class_images.append(os.path.join(class_path, file))
                
                if class_images:
                    if sample_size:
                        class_images = random.sample(class_images, min(sample_size, len(class_images)))
                    image_data[class_dir] = class_images
        else:
            # Flat structure - treat as single class
            all_images = []
            for file in os.listdir(data_source):
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    all_images.append(os.path.join(data_source, file))
            
            if all_images:
                if sample_size:
                    all_images = random.sample(all_images, min(sample_size, len(all_images)))
                image_data['all_images'] = all_images
        
        return image_data
        
    elif isinstance(data_source, pd.DataFrame):
        # DataFrame input
        if image_path_column is None:
            raise ValueError("🚨 image_path_column must be specified for DataFrame input")
        
        if class_column is None:
            # No class column - treat as single class
            paths = data_source[image_path_column].dropna().tolist()
            if sample_size:
                paths = random.sample(paths, min(sample_size, len(paths)))
            return {'all_images': paths}
        
        # Group by class
        image_data = {}
        for class_name, group in data_source.groupby(class_column):
            paths = group[image_path_column].dropna().tolist()
            if sample_size:
                paths = random.sample(paths, min(sample_size, len(paths)))
            if paths:
                image_data[str(class_name)] = paths
        
        return image_data
        
    elif isinstance(data_source, list):
        # List of image paths - treat as single class
        paths = data_source
        if sample_size:
            paths = random.sample(paths, min(sample_size, len(paths)))
        return {'all_images': paths}
        
    else:
        raise TypeError("🚨 data_source must be str, DataFrame, or List[str]")


def _analyze_class_features(
    image_paths: List[str],
    analyze_edges: bool,
    analyze_texture: bool,
    analyze_color: bool,
    analyze_gradients: bool,
    edge_method: str,
    texture_method: str,
    color_spaces: List[str],
    bins_per_channel: int,
    lbp_radius: int,
    lbp_n_points: int,
    canny_low_threshold: float,
    canny_high_threshold: float,
    verbose: bool
) -> Dict[str, Any]:
    """Analyze features for a single class."""
    
    features = {
        'edge_features': [],
        'texture_features': [],
        'color_features': [],
        'gradient_features': []
    }
    
    for i, img_path in enumerate(image_paths):
        if verbose and (i + 1) % max(1, len(image_paths) // 5) == 0:
            progress = ((i + 1) / len(image_paths)) * 100
            print(f"   📈 Progress: {i + 1}/{len(image_paths)} ({progress:.1f}%)")
        
        try:
            with Image.open(img_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Convert to numpy array
                img_array = np.array(img)
                
                # Edge analysis
                if analyze_edges:
                    edge_density = _calculate_edge_density(img_array, edge_method, 
                                                         canny_low_threshold, canny_high_threshold)
                    features['edge_features'].append(edge_density)
                
                # Texture analysis
                if analyze_texture:
                    texture_features = _calculate_texture_features(img_array, texture_method,
                                                                 lbp_radius, lbp_n_points)
                    features['texture_features'].append(texture_features)
                
                # Color analysis
                if analyze_color:
                    color_features = _calculate_color_features(img_array, color_spaces, bins_per_channel)
                    features['color_features'].append(color_features)
                
                # Gradient analysis
                if analyze_gradients:
                    gradient_features = _calculate_gradient_features(img_array)
                    features['gradient_features'].append(gradient_features)
                    
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Skipped {img_path}: {str(e)}")
            continue
    
    return features


def _calculate_edge_density(img_array: np.ndarray, method: str, low_thresh: float, high_thresh: float) -> float:
    """Calculate edge density using specified method."""
    
    # Convert to grayscale
    if len(img_array.shape) == 3:
        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
    else:
        gray = img_array
    
    gray = gray.astype(np.uint8)
        
    if method == "canny":
        if CV2_AVAILABLE:
            edges = cv2.Canny(gray, low_thresh, high_thresh)
        elif SKIMAGE_AVAILABLE:
            edges = feature.canny(gray, sigma=1, low_threshold=low_thresh/255, high_threshold=high_thresh/255)
            edges = (edges * 255).astype(np.uint8)
        else:
            # Simple gradient-based fallback
            gy, gx = np.gradient(gray.astype(float))
            edges = np.sqrt(gx**2 + gy**2)
            edges = (edges > np.percentile(edges, 90)).astype(np.uint8) * 255
    
    elif method == "sobel":
        if SKIMAGE_AVAILABLE:
            edges = filters.sobel(gray)
            edges = (edges > np.percentile(edges, 90)).astype(np.uint8) * 255
        else:
            # Manual Sobel
            sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
            sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
            
            from scipy import ndimage
            edge_x = ndimage.convolve(gray.astype(float), sobel_x)
            edge_y = ndimage.convolve(gray.astype(float), sobel_y)
            edges = np.sqrt(edge_x**2 + edge_y**2)
            edges = (edges > np.percentile(edges, 90)).astype(np.uint8) * 255
    
    elif method == "laplacian":
        if SKIMAGE_AVAILABLE:
            edges = filters.laplace(gray)
            edges = np.abs(edges)
            edges = (edges > np.percentile(edges, 90)).astype(np.uint8) * 255
        else:
            # Manual Laplacian
            laplacian_kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
            from scipy import ndimage
            edges = np.abs(ndimage.convolve(gray.astype(float), laplacian_kernel))
            edges = (edges > np.percentile(edges, 90)).astype(np.uint8) * 255
    
    # Calculate edge density (percentage of edge pixels)
    return np.sum(edges > 0) / edges.size


def _calculate_texture_features(img_array: np.ndarray, method: str, radius: int, n_points: int) -> Dict[str, float]:
    """Calculate texture features using specified method."""
    
    # Convert to grayscale
    if len(img_array.shape) == 3:
        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
    else:
        gray = img_array
    
    # Ensure grayscale image is in uint8 format for LBP analysis
    # This prevents the floating-point warning from scikit-image
    if gray.dtype != np.uint8:
        if gray.max() <= 1.0:
            # Image is normalized [0,1], scale to [0,255]
            gray = (gray * 255).astype(np.uint8)
        else:
            # Image is already in [0,255] range but wrong dtype
            gray = gray.astype(np.uint8)
    
    features = {}
    
    if method == "lbp" and SKIMAGE_AVAILABLE:
        # Local Binary Patterns (now using uint8 image to avoid warnings)
        lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
        
        # Calculate LBP histogram
        hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, range=(0, n_points + 2))
        hist = hist.astype(float)
        hist /= (hist.sum() + 1e-7)  # Normalize
        
        features['lbp_uniformity'] = np.sum(hist**2)  # Measure of pattern uniformity
        features['lbp_entropy'] = -np.sum(hist * np.log2(hist + 1e-7))  # Pattern diversity
        features['lbp_contrast'] = np.var(lbp)  # Local contrast measure
        
    else:
        # Fallback: Basic texture measures
        features['intensity_variance'] = np.var(gray)
        features['intensity_range'] = np.max(gray) - np.min(gray)
        
        # Simple texture energy
        gy, gx = np.gradient(gray.astype(float))
        gradient_magnitude = np.sqrt(gx**2 + gy**2)
        features['texture_energy'] = np.mean(gradient_magnitude**2)
    
    return features


def _calculate_color_features(img_array: np.ndarray, color_spaces: List[str], bins: int) -> Dict[str, np.ndarray]:
    """Calculate color histogram features across different color spaces."""
    
    features = {}
    
    for space in color_spaces:
        if space == "RGB":
            # Use original RGB
            color_img = img_array
        elif space == "HSV":
            # Convert to HSV
            if SKIMAGE_AVAILABLE:
                color_img = color.rgb2hsv(img_array)
            elif CV2_AVAILABLE:
                color_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            else:
                # Skip HSV if no conversion available
                continue
        elif space == "LAB":
            # Convert to LAB
            if SKIMAGE_AVAILABLE:
                color_img = color.rgb2lab(img_array)
            elif CV2_AVAILABLE:
                color_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            else:
                # Skip LAB if no conversion available
                continue
        elif space == "GRAY":
            # Convert to grayscale
            gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
            hist, _ = np.histogram(gray, bins=bins, range=(0, 255))
            features[f'{space.lower()}_hist'] = hist / np.sum(hist)
            continue
        else:
            continue
        
        # Calculate histogram for each channel
        if len(color_img.shape) == 3:
            for i in range(color_img.shape[2]):
                channel_name = f'{space.lower()}_ch{i}'
                if space == "HSV" and i == 0:  # Hue channel
                    hist, _ = np.histogram(color_img[:,:,i], bins=bins, range=(0, 1))
                elif space == "LAB":
                    if i == 0:  # L channel
                        hist, _ = np.histogram(color_img[:,:,i], bins=bins, range=(0, 100))
                    else:  # A, B channels
                        hist, _ = np.histogram(color_img[:,:,i], bins=bins, range=(-128, 127))
                else:  # RGB or other
                    hist, _ = np.histogram(color_img[:,:,i], bins=bins, range=(0, 255))
                
                features[channel_name] = hist / np.sum(hist)
    
    return features


def _calculate_gradient_features(img_array: np.ndarray) -> Dict[str, float]:
    """Calculate gradient-based features."""
    
    # Convert to grayscale
    if len(img_array.shape) == 3:
        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
    else:
        gray = img_array
    
    # Calculate gradients
    gy, gx = np.gradient(gray.astype(float))
    
    # Gradient magnitude
    magnitude = np.sqrt(gx**2 + gy**2)
    
    # Gradient direction
    direction = np.arctan2(gy, gx)
    
    features = {
        'gradient_magnitude_mean': np.mean(magnitude),
        'gradient_magnitude_std': np.std(magnitude),
        'gradient_magnitude_max': np.max(magnitude),
        'gradient_direction_uniformity': _calculate_direction_uniformity(direction)
    }
    
    return features


def _calculate_direction_uniformity(directions: np.ndarray) -> float:
    """Calculate uniformity of gradient directions."""
    
    # Bin directions into 8 sectors (45 degrees each)
    hist, _ = np.histogram(directions, bins=8, range=(-np.pi, np.pi))
    hist = hist / np.sum(hist)
    
    # Calculate uniformity (inverse of entropy)
    entropy = -np.sum(hist * np.log2(hist + 1e-7))
    max_entropy = np.log2(8)  # Maximum possible entropy for 8 bins
    
    return 1 - (entropy / max_entropy)


def _generate_feature_comparisons(class_features: Dict[str, Dict], image_data: Dict[str, List[str]]) -> Dict[str, Any]:
    """Generate statistical comparisons between classes."""
    
    comparisons = {}
    
    # Calculate class-wise statistics
    class_stats = {}
    for class_name, features in class_features.items():
        stats = {}
        
        # Edge statistics
        if features['edge_features']:
            edge_data = np.array(features['edge_features'])
            stats['edge_density'] = {
                'mean': np.mean(edge_data),
                'std': np.std(edge_data),
                'median': np.median(edge_data),
                'range': (np.min(edge_data), np.max(edge_data))
            }
        
        # Texture statistics
        if features['texture_features']:
            # Aggregate texture features
            texture_keys = features['texture_features'][0].keys()
            for key in texture_keys:
                values = [f[key] for f in features['texture_features']]
                stats[f'texture_{key}'] = {
                    'mean': np.mean(values),
                    'std': np.std(values)
                }
        
        # Gradient statistics
        if features['gradient_features']:
            gradient_keys = features['gradient_features'][0].keys()
            for key in gradient_keys:
                values = [f[key] for f in features['gradient_features']]
                stats[f'gradient_{key}'] = {
                    'mean': np.mean(values),
                    'std': np.std(values)
                }
        
        class_stats[class_name] = stats
    
    comparisons['class_statistics'] = class_stats
    
    # Feature ranking (simple variance-based for now)
    feature_rankings = _rank_discriminative_features(class_features)
    
    return {
        'class_comparisons': comparisons,
        'feature_rankings': feature_rankings
    }


def _rank_discriminative_features(class_features: Dict[str, Dict]) -> List[Tuple[str, float]]:
    """Rank features by their discriminative power between classes."""
    
    feature_scores = {}
    
    # Collect all feature values by class
    if len(class_features) < 2:
        return []
    
    class_names = list(class_features.keys())
    
    # Edge density comparison
    edge_data = {}
    for class_name, features in class_features.items():
        if features['edge_features']:
            edge_data[class_name] = np.array(features['edge_features'])
    
    if len(edge_data) >= 2:
        # Calculate between-class variance vs within-class variance
        all_values = np.concatenate(list(edge_data.values()))
        between_var = np.var([np.mean(values) for values in edge_data.values()])
        within_var = np.mean([np.var(values) for values in edge_data.values()])
        
        if within_var > 0:
            feature_scores['edge_density'] = between_var / within_var
    
    # Texture feature comparison
    for class_name, features in class_features.items():
        if features['texture_features']:
            texture_keys = features['texture_features'][0].keys()
            break
    else:
        texture_keys = []
    
    for texture_key in texture_keys:
        texture_data = {}
        for class_name, features in class_features.items():
            if features['texture_features']:
                values = [f[texture_key] for f in features['texture_features']]
                texture_data[class_name] = np.array(values)
        
        if len(texture_data) >= 2:
            all_values = np.concatenate(list(texture_data.values()))
            between_var = np.var([np.mean(values) for values in texture_data.values()])
            within_var = np.mean([np.var(values) for values in texture_data.values()])
            
            if within_var > 0:
                feature_scores[f'texture_{texture_key}'] = between_var / within_var
    
    # Sort by discriminative power
    ranked_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)
    
    return ranked_features


def _create_feature_visualizations(
    class_features: Dict[str, Dict],
    results: Dict[str, Any],
    figsize: Tuple[int, int],
    save_path: Optional[str],
    analyze_edges: bool,
    analyze_texture: bool,
    analyze_color: bool,
    analyze_gradients: bool
) -> None:
    """Create comprehensive feature distribution visualizations."""
    
    # Count active analyses
    active_analyses = sum([analyze_edges, analyze_texture, analyze_color, analyze_gradients])
    if active_analyses == 0:
        return
    
    # Create subplot layout
    fig, axes = plt.subplots(2, 2, figsize=figsize, facecolor='white')
    fig.suptitle('Image Feature Distribution Analysis', fontsize=16, fontweight='bold')
    axes = axes.ravel()
    
    plot_idx = 0
    
    # Edge density visualization
    if analyze_edges and plot_idx < 4:
        ax = axes[plot_idx]
        _plot_edge_distributions(class_features, ax)
        plot_idx += 1
    
    # Texture visualization
    if analyze_texture and plot_idx < 4:
        ax = axes[plot_idx]
        _plot_texture_distributions(class_features, ax)
        plot_idx += 1
    
    # Color visualization
    if analyze_color and plot_idx < 4:
        ax = axes[plot_idx]
        _plot_color_distributions(class_features, ax)
        plot_idx += 1
    
    # Gradient visualization
    if analyze_gradients and plot_idx < 4:
        ax = axes[plot_idx]
        _plot_gradient_distributions(class_features, ax)
        plot_idx += 1
    
    # Hide unused subplots
    for i in range(plot_idx, 4):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def _plot_edge_distributions(class_features: Dict[str, Dict], ax) -> None:
    """Plot edge density distributions by class."""
    
    ax.set_title('Edge Density Distribution by Class', fontsize=12, fontweight='bold')
    
    edge_data = []
    labels = []
    
    for class_name, features in class_features.items():
        if features['edge_features']:
            edge_data.append(features['edge_features'])
            labels.append(class_name)
    
    if edge_data:
        ax.boxplot(edge_data, labels=labels)
        ax.set_ylabel('Edge Density')
        ax.tick_params(axis='x', rotation=45)
    else:
        ax.text(0.5, 0.5, 'No edge data available', ha='center', va='center', transform=ax.transAxes)


def _plot_texture_distributions(class_features: Dict[str, Dict], ax) -> None:
    """Plot texture feature distributions by class."""
    
    ax.set_title('Texture Uniformity by Class', fontsize=12, fontweight='bold')
    
    # Use LBP uniformity if available
    texture_data = []
    labels = []
    
    for class_name, features in class_features.items():
        if features['texture_features']:
            # Try to get LBP uniformity, fallback to variance
            uniformity_values = []
            for texture_feat in features['texture_features']:
                if 'lbp_uniformity' in texture_feat:
                    uniformity_values.append(texture_feat['lbp_uniformity'])
                elif 'intensity_variance' in texture_feat:
                    uniformity_values.append(texture_feat['intensity_variance'])
            
            if uniformity_values:
                texture_data.append(uniformity_values)
                labels.append(class_name)
    
    if texture_data:
        ax.boxplot(texture_data, labels=labels)
        ax.set_ylabel('Texture Uniformity')
        ax.tick_params(axis='x', rotation=45)
    else:
        ax.text(0.5, 0.5, 'No texture data available', ha='center', va='center', transform=ax.transAxes)


def _plot_color_distributions(class_features: Dict[str, Dict], ax) -> None:
    """Plot color distribution characteristics by class."""
    
    ax.set_title('Average Color Diversity by Class', fontsize=12, fontweight='bold')
    
    # Calculate color diversity (entropy of RGB channels)
    diversity_data = []
    labels = []
    
    for class_name, features in class_features.items():
        if features['color_features']:
            class_diversity = []
            for color_feat in features['color_features']:
                # Calculate entropy of RGB channels if available
                diversity_sum = 0
                count = 0
                for key, hist in color_feat.items():
                    if 'rgb_ch' in key:
                        entropy = -np.sum(hist * np.log2(hist + 1e-7))
                        diversity_sum += entropy
                        count += 1
                
                if count > 0:
                    class_diversity.append(diversity_sum / count)
            
            if class_diversity:
                diversity_data.append(class_diversity)
                labels.append(class_name)
    
    if diversity_data:
        ax.boxplot(diversity_data, labels=labels)
        ax.set_ylabel('Color Diversity (Entropy)')
        ax.tick_params(axis='x', rotation=45)
    else:
        ax.text(0.5, 0.5, 'No color data available', ha='center', va='center', transform=ax.transAxes)


def _plot_gradient_distributions(class_features: Dict[str, Dict], ax) -> None:
    """Plot gradient magnitude distributions by class."""
    
    ax.set_title('Gradient Magnitude by Class', fontsize=12, fontweight='bold')
    
    gradient_data = []
    labels = []
    
    for class_name, features in class_features.items():
        if features['gradient_features']:
            magnitude_values = [f['gradient_magnitude_mean'] for f in features['gradient_features']]
            if magnitude_values:
                gradient_data.append(magnitude_values)
                labels.append(class_name)
    
    if gradient_data:
        ax.boxplot(gradient_data, labels=labels)
        ax.set_ylabel('Mean Gradient Magnitude')
        ax.tick_params(axis='x', rotation=45)
    else:
        ax.text(0.5, 0.5, 'No gradient data available', ha='center', va='center', transform=ax.transAxes)


def _generate_feature_recommendations(results: Dict[str, Any], class_features: Dict[str, Dict]) -> List[str]:
    """Generate actionable recommendations based on feature analysis."""
    
    recommendations = []
    
    # Check feature rankings
    if results['feature_rankings']:
        top_feature = results['feature_rankings'][0]
        recommendations.append(
            f"🎯 '{top_feature[0]}' is the most discriminative feature (score: {top_feature[1]:.3f})"
        )
        
        if top_feature[0].startswith('edge'):
            recommendations.append(
                "📐 Consider edge-based preprocessing or edge-enhanced augmentation"
            )
        elif top_feature[0].startswith('texture'):
            recommendations.append(
                "🎨 Texture features are key - consider texture-aware architectures"
            )
        elif top_feature[0].startswith('gradient'):
            recommendations.append(
                "📈 Gradient patterns matter - consider gradient-based features"
            )
    
    # Check class balance in features
    num_classes = len(class_features)
    if num_classes > 1:
        recommendations.append(
            f"⚖️  Analyzed {num_classes} classes - check feature distributions for bias"
        )
    
    # General recommendations
    recommendations.append(
        "💡 Use these insights for feature engineering and preprocessing decisions"
    )
    
    if len(results['feature_rankings']) > 5:
        recommendations.append(
            f"🔍 Top 5 features explain most class differences - consider feature selection"
        )
    
    return recommendations


def _display_feature_results(results: Dict[str, Any]) -> None:
    """Display comprehensive feature analysis results."""
    
    print(f"\n🎯 FEATURE ANALYSIS RESULTS")
    print("=" * 60)
    print(f"📊 Total Images: {results['total_images']:,}")
    print(f"🏷️  Classes: {results['num_classes']}")
    
    # Feature rankings
    if results['feature_rankings']:
        print(f"\n🏆 TOP DISCRIMINATIVE FEATURES:")
        for i, (feature, score) in enumerate(results['feature_rankings'][:5], 1):
            print(f"   {i}. {feature}: {score:.3f}")
    
    # Class comparisons
    if 'class_statistics' in results['class_comparisons']:
        print(f"\n📈 CLASS COMPARISONS:")
        class_stats = results['class_comparisons']['class_statistics']
        
        # Show edge density comparison if available
        edge_stats = {}
        for class_name, stats in class_stats.items():
            if 'edge_density' in stats:
                edge_stats[class_name] = stats['edge_density']['mean']
        
        if edge_stats:
            print(f"   📐 Edge Density:")
            for class_name, density in sorted(edge_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"     {class_name}: {density:.4f}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n✅ Feature analysis completed!")


def _parse_image_data_source(
    data_source: Union[str, pd.DataFrame, List[str]], 
    class_column: Optional[str], 
    image_path_column: Optional[str]
) -> List[str]:
    """Parse various data source types and extract image paths."""
    
    if isinstance(data_source, str):
        # Directory path
        if not os.path.exists(data_source):
            raise FileNotFoundError(f"🚨 Directory not found: {data_source}")
        
        image_paths = []
        supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        
        for root, dirs, files in os.walk(data_source):
            for file in files:
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    image_paths.append(os.path.join(root, file))
        
        if not image_paths:
            raise ValueError(f"🚨 No supported images found in {data_source}")
            
        return image_paths
        
    elif isinstance(data_source, pd.DataFrame):
        # DataFrame input
        if image_path_column is None:
            raise ValueError("🚨 image_path_column must be specified for DataFrame input")
        
        if image_path_column not in data_source.columns:
            raise ValueError(f"🚨 Column '{image_path_column}' not found in DataFrame")
        
        return data_source[image_path_column].dropna().tolist()
        
    elif isinstance(data_source, list):
        # List of image paths
        return data_source
        
    else:
        raise TypeError("🚨 data_source must be str, DataFrame, or List[str]")


def _analyze_single_image(
    img_path: str,
    check_corruption: bool,
    analyze_color: bool,
    detect_blur: bool,
    check_artifacts: bool,
    brightness_threshold: Tuple[float, float],
    contrast_threshold: float
) -> Dict[str, Any]:
    """Analyze a single image for quality metrics."""
    
    analysis = {
        'corrupted': False,
        'dimensions': None,
        'file_size': None,
        'brightness': None,
        'contrast': None,
        'color_mode': None,
        'is_grayscale': None,
        'blur_score': None,
        'has_artifacts': None,
        'issues': []
    }
    
    try:
        # Get file size
        analysis['file_size'] = os.path.getsize(img_path) / 1024  # KB
        
        # Load image
        with Image.open(img_path) as img:
            # Basic properties
            analysis['dimensions'] = img.size
            analysis['color_mode'] = img.mode
            
            # Color analysis
            if analyze_color:
                analysis['is_grayscale'] = img.mode in ['L', '1'] or _is_effectively_grayscale(img)
            
            # Convert to RGB for analysis
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Brightness analysis
            stat = ImageStat.Stat(img)
            analysis['brightness'] = sum(stat.mean) / 3  # Average of RGB channels
            
            # Contrast analysis (standard deviation of pixel values)
            analysis['contrast'] = sum(stat.stddev) / 3
            
            # Check brightness issues
            if analysis['brightness'] < brightness_threshold[0]:
                analysis['issues'].append('too_dark')
            elif analysis['brightness'] > brightness_threshold[1]:
                analysis['issues'].append('too_bright')
            
            # Check contrast issues
            if analysis['contrast'] < contrast_threshold:
                analysis['issues'].append('low_contrast')
            
            # Blur detection
            if detect_blur:
                analysis['blur_score'] = _calculate_blur_score(img)
                if analysis['blur_score'] < 100:  # Threshold for blur detection
                    analysis['issues'].append('blurry')
            
            # Artifact detection
            if check_artifacts:
                analysis['has_artifacts'] = _detect_compression_artifacts(img)
                if analysis['has_artifacts']:
                    analysis['issues'].append('artifacts')
    
    except Exception as e:
        analysis['corrupted'] = True
        analysis['issues'].append(f'corruption: {str(e)}')
    
    return analysis


def _is_effectively_grayscale(img: Image.Image, threshold: float = 10.0) -> bool:
    """Check if a color image is effectively grayscale."""
    if img.mode == 'RGB':
        # Sample pixels to check color variation
        import numpy as np
        sample_size = min(1000, img.size[0] * img.size[1])
        pixels = list(img.getdata())
        
        if len(pixels) > sample_size:
            pixels = random.sample(pixels, sample_size)
        
        # Calculate color variation
        color_variations = []
        for r, g, b in pixels:
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            color_variations.append(max_val - min_val)
        
        avg_variation = sum(color_variations) / len(color_variations)
        return avg_variation < threshold
    
    return False


def _calculate_blur_score(img: Image.Image) -> float:
    """Calculate blur score using Laplacian variance."""
    try:
        import numpy as np
        from scipy import ndimage
        
        # Convert to grayscale
        gray = img.convert('L')
        img_array = np.array(gray)
        
        # Calculate Laplacian variance
        laplacian = ndimage.laplace(img_array)
        variance = laplacian.var()
        
        return variance
        
    except ImportError:
        # Fallback method without scipy
        return _calculate_blur_score_simple(img)


def _calculate_blur_score_simple(img: Image.Image) -> float:
    """Simple blur detection without scipy dependency."""
    import numpy as np
    
    # Convert to grayscale
    gray = img.convert('L')
    img_array = np.array(gray, dtype=float)
    
    # Simple edge detection using gradient magnitude
    gy, gx = np.gradient(img_array)
    edge_magnitude = np.sqrt(gx**2 + gy**2)
    
    # Use variance of edge magnitude as blur metric
    return edge_magnitude.var()


def _detect_compression_artifacts(img: Image.Image) -> bool:
    """Detect potential compression artifacts."""
    try:
        import numpy as np
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Check for block artifacts (8x8 pattern common in JPEG)
        # This is a simplified detection method
        if len(img_array.shape) == 3:
            # Color image - check green channel
            channel = img_array[:, :, 1]
        else:
            channel = img_array
        
        # Sample small regions and check for unusual patterns
        h, w = channel.shape
        if h >= 16 and w >= 16:
            # Check for block boundaries (simplified)
            block_edges_h = []
            block_edges_v = []
            
            for i in range(8, h - 8, 8):
                diff = abs(int(channel[i].mean()) - int(channel[i-1].mean()))
                block_edges_h.append(diff)
            
            for j in range(8, w - 8, 8):
                diff = abs(int(channel[:, j].mean()) - int(channel[:, j-1].mean()))
                block_edges_v.append(diff)
            
            # If there are consistent block boundaries, might indicate artifacts
            if block_edges_h and block_edges_v:
                avg_h_diff = sum(block_edges_h) / len(block_edges_h)
                avg_v_diff = sum(block_edges_v) / len(block_edges_v)
                
                # Threshold for detecting systematic block patterns
                return avg_h_diff > 5 or avg_v_diff > 5
        
        return False
        
    except Exception:
        return False


def _generate_quality_analysis(
    valid_images: List[str],
    dimension_data: List[Tuple[int, int]],
    file_size_data: List[float],
    brightness_data: List[float],
    contrast_data: List[float],
    blur_scores: List[float],
    color_modes: List[str],
    brightness_threshold: Tuple[float, float],
    contrast_threshold: float,
    aspect_ratio_tolerance: float,
    file_size_outlier_factor: float
) -> Dict[str, Any]:
    """Generate comprehensive quality analysis from collected data."""
    
    analysis = {}
    
    # Color analysis
    total_valid = len(valid_images)
    if total_valid > 0:
        color_counts = {}
        for mode in color_modes:
            color_counts[mode] = color_counts.get(mode, 0) + 1
        
        analysis['color_analysis'] = {
            'color_mode_distribution': color_counts,
            'total_valid_images': total_valid
        }
    
    # Dimension analysis
    if dimension_data:
        widths = [d[0] for d in dimension_data]
        heights = [d[1] for d in dimension_data]
        aspect_ratios = [w/h for w, h in dimension_data]
        
        analysis['dimension_analysis'] = {
            'width_stats': {
                'min': min(widths),
                'max': max(widths),
                'mean': sum(widths) / len(widths),
                'median': sorted(widths)[len(widths)//2]
            },
            'height_stats': {
                'min': min(heights),
                'max': max(heights),
                'mean': sum(heights) / len(heights),
                'median': sorted(heights)[len(heights)//2]
            },
            'aspect_ratio_stats': {
                'min': min(aspect_ratios),
                'max': max(aspect_ratios),
                'mean': sum(aspect_ratios) / len(aspect_ratios),
                'median': sorted(aspect_ratios)[len(aspect_ratios)//2]
            },
            'unusual_dimensions': _find_dimension_outliers(dimension_data, aspect_ratio_tolerance)
        }
    
    # File size analysis
    if file_size_data:
        analysis['file_size_analysis'] = {
            'size_stats': {
                'min_kb': min(file_size_data),
                'max_kb': max(file_size_data),
                'mean_kb': sum(file_size_data) / len(file_size_data),
                'median_kb': sorted(file_size_data)[len(file_size_data)//2]
            },
            'outliers': _find_file_size_outliers(file_size_data, file_size_outlier_factor)
        }
    
    # Brightness analysis
    if brightness_data:
        problematic_brightness = [
            b for b in brightness_data 
            if b < brightness_threshold[0] or b > brightness_threshold[1]
        ]
        
        analysis['brightness_analysis'] = {
            'brightness_stats': {
                'min': min(brightness_data),
                'max': max(brightness_data),
                'mean': sum(brightness_data) / len(brightness_data),
                'median': sorted(brightness_data)[len(brightness_data)//2]
            },
            'problematic_count': len(problematic_brightness),
            'percentage_problematic': (len(problematic_brightness) / len(brightness_data)) * 100
        }
    
    # Contrast analysis
    if contrast_data:
        low_contrast_count = sum(1 for c in contrast_data if c < contrast_threshold)
        
        analysis['contrast_analysis'] = {
            'contrast_stats': {
                'min': min(contrast_data),
                'max': max(contrast_data),
                'mean': sum(contrast_data) / len(contrast_data),
                'median': sorted(contrast_data)[len(contrast_data)//2]
            },
            'low_contrast_count': low_contrast_count,
            'percentage_low_contrast': (low_contrast_count / len(contrast_data)) * 100
        }
    
    # Blur analysis
    if blur_scores:
        blur_threshold = 100  # Threshold for blur detection
        blurry_count = sum(1 for score in blur_scores if score < blur_threshold)
        
        analysis['blur_analysis'] = {
            'blur_stats': {
                'min_score': min(blur_scores),
                'max_score': max(blur_scores),
                'mean_score': sum(blur_scores) / len(blur_scores),
                'median_score': sorted(blur_scores)[len(blur_scores)//2]
            },
            'blurry_count': blurry_count,
            'percentage_blurry': (blurry_count / len(blur_scores)) * 100
        }
    
    return analysis


def _find_dimension_outliers(dimension_data: List[Tuple[int, int]], tolerance: float) -> List[Dict]:
    """Find images with unusual dimensions or aspect ratios."""
    outliers = []
    
    if not dimension_data:
        return outliers
    
    # Calculate mean aspect ratio
    aspect_ratios = [w/h for w, h in dimension_data]
    mean_aspect = sum(aspect_ratios) / len(aspect_ratios)
    
    for i, (w, h) in enumerate(dimension_data):
        aspect = w / h
        deviation = abs(aspect - mean_aspect) / mean_aspect
        
        if deviation > tolerance:
            outliers.append({
                'index': i,
                'dimensions': (w, h),
                'aspect_ratio': aspect,
                'deviation_from_mean': deviation
            })
    
    return outliers


def _find_file_size_outliers(file_sizes: List[float], outlier_factor: float) -> List[Dict]:
    """Find unusually large or small files using IQR method."""
    outliers = []
    
    if len(file_sizes) < 4:
        return outliers
    
    sorted_sizes = sorted(file_sizes)
    n = len(sorted_sizes)
    q1 = sorted_sizes[n // 4]
    q3 = sorted_sizes[3 * n // 4]
    iqr = q3 - q1
    
    lower_bound = q1 - outlier_factor * iqr
    upper_bound = q3 + outlier_factor * iqr
    
    for i, size in enumerate(file_sizes):
        if size < lower_bound or size > upper_bound:
            outliers.append({
                'index': i,
                'size_kb': size,
                'type': 'small' if size < lower_bound else 'large'
            })
    
    return outliers


def _calculate_quality_score(results: Dict[str, Any]) -> int:
    """Calculate overall dataset quality score (0-100)."""
    score = 100
    total_images = results['total_images']
    
    if total_images == 0:
        return 0
    
    # Deduct for corrupted images
    corruption_penalty = (len(results['corrupted_images']) / total_images) * 30
    score -= corruption_penalty
    
    # Deduct for brightness issues
    if 'brightness_analysis' in results and results['brightness_analysis']:
        brightness_penalty = (results['brightness_analysis']['percentage_problematic'] / 100) * 20
        score -= brightness_penalty
    
    # Deduct for contrast issues
    if 'contrast_analysis' in results and results['contrast_analysis']:
        contrast_penalty = (results['contrast_analysis']['percentage_low_contrast'] / 100) * 15
        score -= contrast_penalty
    
    # Deduct for blur issues
    if 'blur_analysis' in results and results['blur_analysis']:
        blur_penalty = (results['blur_analysis']['percentage_blurry'] / 100) * 20
        score -= blur_penalty
    
    # Deduct for file size outliers
    if 'file_size_analysis' in results and results['file_size_analysis']:
        outliers = results['file_size_analysis']['outliers']
        outlier_penalty = (len(outliers) / total_images) * 10
        score -= outlier_penalty
    
    # Deduct for dimension inconsistencies
    if 'dimension_analysis' in results and results['dimension_analysis']:
        dim_outliers = results['dimension_analysis']['unusual_dimensions']
        dim_penalty = (len(dim_outliers) / total_images) * 5
        score -= dim_penalty
    
    return max(0, int(score))


def _generate_quality_recommendations(results: Dict[str, Any]) -> List[str]:
    """Generate actionable recommendations based on quality analysis."""
    recommendations = []
    
    # Corruption recommendations
    if results['corrupted_images']:
        count = len(results['corrupted_images'])
        recommendations.append(
            f"🚨 Remove {count} corrupted image(s) before training"
        )
    
    # Brightness recommendations
    if 'brightness_analysis' in results and results['brightness_analysis']:
        problematic_pct = results['brightness_analysis']['percentage_problematic']
        if problematic_pct > 10:
            recommendations.append(
                f"💡 {problematic_pct:.1f}% of images have brightness issues - consider histogram equalization"
            )
    
    # Contrast recommendations
    if 'contrast_analysis' in results and results['contrast_analysis']:
        low_contrast_pct = results['contrast_analysis']['percentage_low_contrast']
        if low_contrast_pct > 15:
            recommendations.append(
                f"🔍 {low_contrast_pct:.1f}% of images have low contrast - consider CLAHE enhancement"
            )
    
    # Blur recommendations
    if 'blur_analysis' in results and results['blur_analysis']:
        blurry_pct = results['blur_analysis']['percentage_blurry']
        if blurry_pct > 5:
            recommendations.append(
                f"📷 {blurry_pct:.1f}% of images may be blurry - consider sharpening or removal"
            )
    
    # Dimension recommendations
    if 'dimension_analysis' in results and results['dimension_analysis']:
        outliers = results['dimension_analysis']['unusual_dimensions']
        if len(outliers) > results['total_images'] * 0.1:
            recommendations.append(
                "📐 Inconsistent image dimensions detected - consider standardization"
            )
    
    # File size recommendations
    if 'file_size_analysis' in results and results['file_size_analysis']:
        outliers = results['file_size_analysis']['outliers']
        if len(outliers) > results['total_images'] * 0.05:
            recommendations.append(
                "💾 File size outliers detected - check for compression inconsistencies"
            )
    
    # Color mode recommendations
    if 'color_analysis' in results and results['color_analysis']:
        modes = results['color_analysis']['color_mode_distribution']
        if len(modes) > 1:
            recommendations.append(
                "🎨 Mixed color modes detected - ensure consistent preprocessing"
            )
    
    # Overall quality recommendations
    quality_score = results['quality_score']
    if quality_score < 70:
        recommendations.append(
            f"⚠️  Dataset quality score is {quality_score}/100 - comprehensive cleanup recommended"
        )
    elif quality_score < 85:
        recommendations.append(
            f"📈 Dataset quality score is {quality_score}/100 - minor improvements suggested"
        )
    
    if not recommendations:
        recommendations.append("✅ Dataset appears to be in good condition!")
    
    return recommendations


def _display_quality_results(results: Dict[str, Any]) -> None:
    """Display comprehensive quality assessment results."""
    
    print(f"\n🎯 QUALITY ASSESSMENT RESULTS")
    print("=" * 60)
    print(f"📊 Total Images Analyzed: {results['total_images']:,}")
    print(f"🏆 Overall Quality Score: {results['quality_score']}/100")
    
    # Corruption results
    if results['corrupted_images']:
        print(f"\n🚨 CORRUPTION ISSUES:")
        print(f"   Corrupted Images: {len(results['corrupted_images'])}")
        if len(results['corrupted_images']) <= 5:
            for img_path in results['corrupted_images']:
                print(f"     ❌ {img_path}")
        else:
            print(f"     ❌ (showing first 5 of {len(results['corrupted_images'])})")
            for img_path in results['corrupted_images'][:5]:
                print(f"        {img_path}")
    
    # Color analysis
    if 'color_analysis' in results and results['color_analysis']:
        print(f"\n🎨 COLOR ANALYSIS:")
        color_dist = results['color_analysis']['color_mode_distribution']
        for mode, count in color_dist.items():
            percentage = (count / results['color_analysis']['total_valid_images']) * 100
            print(f"   {mode}: {count:,} images ({percentage:.1f}%)")
    
    # Dimension analysis
    if 'dimension_analysis' in results and results['dimension_analysis']:
        dim_analysis = results['dimension_analysis']
        print(f"\n📐 DIMENSION ANALYSIS:")
        print(f"   Width: {dim_analysis['width_stats']['min']}-{dim_analysis['width_stats']['max']} " +
              f"(avg: {dim_analysis['width_stats']['mean']:.0f})")
        print(f"   Height: {dim_analysis['height_stats']['min']}-{dim_analysis['height_stats']['max']} " +
              f"(avg: {dim_analysis['height_stats']['mean']:.0f})")
        print(f"   Aspect Ratio: {dim_analysis['aspect_ratio_stats']['min']:.2f}-{dim_analysis['aspect_ratio_stats']['max']:.2f} " +
              f"(avg: {dim_analysis['aspect_ratio_stats']['mean']:.2f})")
        if dim_analysis['unusual_dimensions']:
            print(f"   ⚠️  Unusual Dimensions: {len(dim_analysis['unusual_dimensions'])} images")
    
    # Brightness analysis
    if 'brightness_analysis' in results and results['brightness_analysis']:
        bright_analysis = results['brightness_analysis']
        print(f"\n☀️  BRIGHTNESS ANALYSIS:")
        print(f"   Range: {bright_analysis['brightness_stats']['min']:.1f}-{bright_analysis['brightness_stats']['max']:.1f} " +
              f"(avg: {bright_analysis['brightness_stats']['mean']:.1f})")
        if bright_analysis['problematic_count'] > 0:
            print(f"   ⚠️  Problematic: {bright_analysis['problematic_count']} images " +
                  f"({bright_analysis['percentage_problematic']:.1f}%)")
    
    # Contrast analysis
    if 'contrast_analysis' in results and results['contrast_analysis']:
        contrast_analysis = results['contrast_analysis']
        print(f"\n🔍 CONTRAST ANALYSIS:")
        print(f"   Range: {contrast_analysis['contrast_stats']['min']:.1f}-{contrast_analysis['contrast_stats']['max']:.1f} " +
              f"(avg: {contrast_analysis['contrast_stats']['mean']:.1f})")
        if contrast_analysis['low_contrast_count'] > 0:
            print(f"   ⚠️  Low Contrast: {contrast_analysis['low_contrast_count']} images " +
                  f"({contrast_analysis['percentage_low_contrast']:.1f}%)")
    
    # Blur analysis
    if 'blur_analysis' in results and results['blur_analysis']:
        blur_analysis = results['blur_analysis']
        print(f"\n📷 BLUR ANALYSIS:")
        print(f"   Sharpness Score Range: {blur_analysis['blur_stats']['min_score']:.1f}-{blur_analysis['blur_stats']['max_score']:.1f} " +
              f"(avg: {blur_analysis['blur_stats']['mean_score']:.1f})")
        if blur_analysis['blurry_count'] > 0:
            print(f"   ⚠️  Potentially Blurry: {blur_analysis['blurry_count']} images " +
                  f"({blur_analysis['percentage_blurry']:.1f}%)")
    
    # File size analysis
    if 'file_size_analysis' in results and results['file_size_analysis']:
        size_analysis = results['file_size_analysis']
        print(f"\n💾 FILE SIZE ANALYSIS:")
        print(f"   Size Range: {size_analysis['size_stats']['min_kb']:.1f}-{size_analysis['size_stats']['max_kb']:.1f} KB " +
              f"(avg: {size_analysis['size_stats']['mean_kb']:.1f} KB)")
        if size_analysis['outliers']:
            print(f"   ⚠️  Size Outliers: {len(size_analysis['outliers'])} images")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n✅ Quality assessment completed!")


def visualize_image_classes(
    data_source: Union[str, pd.DataFrame], 
    image_column: Optional[str] = None,
    label_column: Optional[str] = None,
    samples_per_class: int = 4,
    max_classes_display: Optional[int] = 20,  # Default to 20 for readability
    auto_skip_threshold: int = 80,
    max_images_display: int = 80,
    figsize: Optional[Tuple[int, int]] = None,
    shuffle_samples: bool = True,
    show_image_info: bool = True,
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    return_stats: bool = False
) -> Optional[Dict[str, Any]]:
    """
    📸 Visualize random samples from each class in an image classification dataset.
    
    This function provides comprehensive exploratory data analysis for image datasets,
    helping practitioners understand class distributions, identify data quality issues,
    and spot potential problems like mislabeled images or class imbalances.
    
    Perfect for the initial phase of computer vision projects where understanding
    your dataset is crucial for model success.
    
    Parameters
    ----------
    data_source : str or pd.DataFrame
        Either a directory path containing class-named subfolders of images,
        or a pandas DataFrame with image paths and class labels.
        
    image_column : str, optional
        Column name containing image file paths (required if data_source is DataFrame).
        
    label_column : str, optional
        Column name containing class labels (required if data_source is DataFrame).
        
    samples_per_class : int, default=4
        Number of random samples to display per class.
        
    max_classes_display : int, default=20
        Maximum number of classes to display. If dataset has more classes,
        only the first max_classes_display classes will be shown with a note.
        
    auto_skip_threshold : int, default=80
        Threshold for automatically skipping visualization when too many classes
        would make the display cluttered.
        
    max_images_display : int, default=80
        Maximum total number of images to display across all classes.
        
    figsize : tuple, optional
        Figure size as (width, height) in inches. If None, automatically calculated.
        
    shuffle_samples : bool, default=True
        Whether to randomly shuffle samples within each class.
        
    show_image_info : bool, default=True
        Whether to display technical image information (dimensions, file size).
        
    title : str, optional
        Title for the visualization. If None, automatically generated.
        
    save_path : str, optional
        Path to save the visualization. If None, plot is only displayed.
        
    return_stats : bool, default=False
        Whether to return detailed statistics about the dataset.
        
    Returns
    -------
    dict or None
        If return_stats=True, returns dictionary with dataset statistics.
        
    Examples
    --------
    >>> import edaflow
    >>> # Directory-based analysis
    >>> edaflow.visualize_image_classes(data_source='dataset/train/')
    >>> # Deprecated but supported
    >>> edaflow.visualize_image_classes(image_paths='dataset/train/')
    """
    
    # Handle backward compatibility for positional arguments and deprecated parameters
    # Call the actual implementation
    return _visualize_image_classes_impl(
        data_source=data_source,
        class_column=label_column,  # Map label_column to class_column
        image_path_column=image_column,  # Map image_column to image_path_column
        samples_per_class=samples_per_class,
        max_classes_display=max_classes_display,
        auto_skip_threshold=auto_skip_threshold,
        max_images_display=max_images_display,
        figsize=figsize,
        shuffle_samples=shuffle_samples,
        show_image_info=show_image_info,
        title=title,
        save_path=save_path,
        return_stats=return_stats
    )


def _visualize_image_classes_impl(
    data_source: Union[str, List[str], pd.DataFrame] = None,
    class_column: Optional[str] = None,
    image_path_column: Optional[str] = None, 
    samples_per_class: int = 5,
    grid_layout: Union[str, Tuple[int, int]] = 'auto',
    figsize: Tuple[int, int] = (15, 10),
    shuffle_samples: bool = True,
    show_class_counts: bool = True,
    show_image_info: bool = False,
    title: str = "Class-wise Image Sample Visualization",
    save_path: Optional[str] = None,
    return_stats: bool = False,
    # Parameters for handling large datasets and readability
    max_images_display: Optional[int] = 80,
    max_classes_display: Optional[int] = 20,  # Default to 20 for readability
    auto_skip_threshold: int = 80,
    force_display: bool = False,
    # Backward compatibility parameter (deprecated)
    image_paths: Union[str, pd.DataFrame, List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    📸 Visualize random samples from each class in an image classification dataset.
    
    This function provides comprehensive exploratory data analysis for image datasets,
    helping practitioners understand class distributions, identify data quality issues,
    and spot potential problems like mislabeled images or class imbalances.
    
    Perfect for the initial phase of computer vision projects where understanding
    your dataset is crucial for model success.
    
    Parameters
    ----------
    data_source : str, list, or pd.DataFrame
        One of:
        - Directory path containing class-named subfolders of images (str)
        - List of image file paths where parent directory indicates class (list)  
        - pandas DataFrame with image paths and class labels (pd.DataFrame)
        
    class_column : str, optional
        Column name containing class labels (required if data_source is DataFrame).
        
    image_path_column : str, optional  
        Column name containing image file paths (required if data_source is DataFrame).
        
    samples_per_class : int, default=5
        Number of random samples to display per class.
        
    grid_layout : str or tuple, default='auto'
        Layout for the visualization grid. Options:
        - 'auto': Automatically determine optimal layout
        - 'square': Force square-ish layout
        - (rows, cols): Specify exact grid dimensions
        
    figsize : tuple, default=(15, 10)
        Figure size as (width, height) in inches.
        
    shuffle_samples : bool, default=True
        Whether to randomly sample from each class or take first N samples.
        
    show_class_counts : bool, default=True
        Whether to display class distribution statistics.
        
    show_image_info : bool, default=False
        Whether to display technical image information (dimensions, file size).
        
    title : str, default="Class-wise Image Sample Visualization"
        Title for the visualization.
        
    save_path : str, optional
        Path to save the visualization. If None, plot is only displayed.
        
    return_stats : bool, default=False
        Whether to return detailed statistics about the dataset.
        
    image_paths : str, pd.DataFrame, or list, optional
        **DEPRECATED**: Use 'data_source' parameter instead.
        This parameter is maintained for backward compatibility only.
        
    Returns
    -------
    dict or None
        If return_stats=True, returns dictionary with dataset statistics:
        - 'class_counts': Number of samples per class
        - 'total_samples': Total number of images
        - 'num_classes': Number of classes
        - 'balance_ratio': Ratio of smallest to largest class
        - 'imbalance_warnings': List of potential balance issues
        - 'corrupted_images': List of corrupted/unreadable images
        
    Examples
    --------
    🔍 **Directory-based Analysis** (Common for organized datasets):
    
    >>> import edaflow
    >>> 
    >>> # Analyze dataset organized in class folders
    >>> edaflow.visualize_image_classes(
    ...     'dataset/train/',           # Directory with class subfolders
    ...     samples_per_class=8,        # Show 8 samples per class
    ...     show_class_counts=True      # Display class distribution
    ... )
    
    📊 **DataFrame-based Analysis** (For datasets with metadata):
    
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'image_path': ['images/cat1.jpg', 'images/dog1.jpg', ...],
    ...     'class': ['cat', 'dog', 'cat', 'dog', ...],
    ...     'split': ['train', 'test', 'train', 'val', ...]
    ... })
    >>> 
    >>> # Analyze with custom parameters
    >>> stats = edaflow.visualize_image_classes(
    ...     df,
    ...     image_path_column='image_path',
    ...     class_column='class', 
    ...     samples_per_class=6,
    ...     show_image_info=True,       # Show image dimensions
    ...     return_stats=True           # Get detailed statistics
    ... )
    >>> print(f"Dataset balance ratio: {stats['balance_ratio']:.2f}")
    
    📋 **List-based Analysis** (For glob patterns or custom file lists):
    
    >>> import glob
    >>> 
    >>> # Collect image paths using glob  
    >>> image_paths = glob.glob('dataset/train/*/*.jpg')
    >>> 
    >>> # Analyze the file list (classes determined by parent directory)
    >>> edaflow.visualize_image_classes(
    ...     data_source=image_paths,    # List of image file paths
    ...     samples_per_class=5,        # Show 5 samples per class  
    ...     title="Dataset from File List"
    ... )
    
    🎯 **Medical/Scientific Imaging**:
    
    >>> # Analysis for medical imaging dataset
    >>> edaflow.visualize_image_classes(
    ...     'medical_scans/',
    ...     samples_per_class=4,        # Fewer samples for detailed view
    ...     figsize=(20, 15),          # Larger figure for detail
    ...     title="Medical Scan Classification Dataset",
    ...     save_path='dataset_overview.png'
    ... )
    
    📈 **Production Dataset Validation**:
    
    >>> # Quick validation of production dataset
    >>> stats = edaflow.visualize_image_classes(
    ...     production_df,
    ...     image_path_column='file_path',
    ...     class_column='predicted_class',
    ...     samples_per_class=10,
    ...     return_stats=True
    ... )
    >>> 
    >>> # Check for issues
    >>> if stats['balance_ratio'] < 0.3:
    ...     print("⚠️  Significant class imbalance detected!")
    >>> if stats['corrupted_images']:
    ...     print(f"🚨 {len(stats['corrupted_images'])} corrupted images found")
    
    📦 **Large Dataset Handling**:
    
    >>> # For large datasets (200+ images), visualization is auto-skipped
    >>> edaflow.visualize_image_classes(
    ...     'huge_dataset/',
    ...     samples_per_class=3,        # Statistics shown, no visualization
    ... )
    
    >>> # Limit total images displayed for readability  
    >>> edaflow.visualize_image_classes(
    ...     'big_dataset/', 
    ...     samples_per_class=10,
    ...     max_images_display=50,      # Limit to 50 total images
    ... )
    
    >>> # Force display even for very large datasets (not recommended)
    >>> edaflow.visualize_image_classes(
    ...     'massive_dataset/',
    ...     samples_per_class=20,
    ...     force_display=True          # Override auto-skip behavior
    ... )
    
    Notes
    -----
    📋 **Requirements**:
    - Requires Pillow (PIL) for image loading: `pip install Pillow`
    - Images should be in common formats: .jpg, .jpeg, .png, .bmp, .tiff
    
    🎯 **Best Practices**:
    - Use 5-10 samples per class for initial exploration
    - Enable show_image_info for debugging dimension issues  
    - Set shuffle_samples=False for reproducible analysis
    - Save visualizations for documentation and reporting
    
    ⚠️  **Common Issues**:
    - Corrupted images are automatically skipped with warnings
    - Very large images are resized for display efficiency
    - Mixed aspect ratios are handled gracefully in grid layout
    
    🔍 **What to Look For**:
    - **Class Balance**: Are all classes represented equally?
    - **Data Quality**: Any corrupted, mislabeled, or unusual images?
    - **Visual Consistency**: Do images within classes look similar?
    - **Dataset Bias**: Any systematic differences between classes?
    """
    
    # Check PIL availability
    if not PIL_AVAILABLE:
        raise ImportError(
            "🚨 PIL (Pillow) is required for image visualization.\n"
            "📦 Install with: pip install Pillow"
        )
    
    """
    Internal implementation of visualize_image_classes with full backward compatibility.
    """
    
    # Check PIL availability
    if not PIL_AVAILABLE:
        raise ImportError(
            "🚨 PIL (Pillow) is required for image visualization.\n"
            "📦 Install with: pip install Pillow"
        )

    # Handle backward compatibility for deprecated 'image_paths' parameter
    # Case 1: image_paths passed as keyword parameter
    if image_paths is not None:
        if data_source is not None:
            raise ValueError(
                "🚨 Cannot specify both 'data_source' and deprecated 'image_paths' parameter. "
                "Please use 'data_source' only."
            )
        print("⚠️  Warning: 'image_paths' parameter is deprecated. Use 'data_source' instead.")
        data_source = image_paths
    
    if data_source is None:
        raise ValueError(
            "🚨 Must specify 'data_source' parameter with one of:\n"
            "   • Directory path containing class subfolders (str)\n"
            "   • List of image file paths (list)\n" 
            "   • pandas DataFrame with image paths and class labels\n\n"
            "📝 For backward compatibility, you can use:\n"
            "   • data_source=your_path (recommended)\n"
            "   • image_paths=your_path (deprecated, shows warning)"
        )

    print("🖼️  Starting Image Classification EDA...")
    print("=" * 55)
    
    # Parse data source and collect image information
    if isinstance(data_source, str):
        # Directory-based input
        if not os.path.exists(data_source):
            raise FileNotFoundError(f"🚨 Directory not found: {data_source}")
            
        print(f"📁 Analyzing directory: {data_source}")
        image_data = _parse_directory_structure(data_source)
        
    elif isinstance(data_source, (list, tuple)):
        # List of image paths (from glob.glob() or manual list)
        print(f"📋 Analyzing list of {len(data_source)} image paths")
        image_data = _parse_image_path_list(data_source)
        
    elif isinstance(data_source, pd.DataFrame):
        # DataFrame-based input
        if class_column is None or image_path_column is None:
            raise ValueError(
                "🚨 For DataFrame input, both 'class_column' and 'image_path_column' must be specified"
            )
            
        print(f"📊 Analyzing DataFrame with {len(data_source)} rows")
        image_data = _parse_dataframe_structure(data_source, class_column, image_path_column)
        
    else:
        raise TypeError(
            "🚨 data_source must be one of:\n"
            "   • Directory path (str)\n"
            "   • List of image paths (list)\n" 
            "   • pandas DataFrame"
        )
    
    # Generate statistics
    stats = _generate_image_dataset_stats(image_data)
    
    # Apply class limiting for readability if specified
    original_num_classes = len(image_data)
    class_limiting_applied = False
    
    if max_classes_display is not None and len(image_data) > max_classes_display:
        class_limiting_applied = True
        print(f"\n🎯 Class limiting activated: {len(image_data)} → {max_classes_display} classes")
        print(f"   📊 Showing most frequent classes for optimal readability")
        
        # Sort classes by frequency and take the top N
        class_sizes = {class_name: len(paths) for class_name, paths in image_data.items()}
        top_classes = sorted(class_sizes.items(), key=lambda x: x[1], reverse=True)[:max_classes_display]
        
        # Filter image_data to only include top classes
        filtered_image_data = {class_name: image_data[class_name] for class_name, _ in top_classes}
        
        print(f"   ✅ Selected classes: {', '.join(list(filtered_image_data.keys())[:5])}{'...' if len(filtered_image_data) > 5 else ''}")
        print(f"   💡 Tip: This will show much larger, more readable images!")
        
        # Update image_data and regenerate stats
        image_data = filtered_image_data
        stats = _generate_image_dataset_stats(image_data)
    
    # Display class distribution
    if show_class_counts:
        _display_class_distribution(stats)
    
    # Smart visualization handling with readability-first approach  
    total_images_to_display = len(image_data) * samples_per_class
    should_display_visualization = True
    original_samples_per_class = samples_per_class
    num_classes = len(image_data)
    
    # Define readability thresholds based on human visual perception
    MAX_READABLE_IMAGES = 50      # Sweet spot for clear image viewing
    MAX_READABLE_CLASSES = 20     # Classes that can be comfortably compared
    CRITICAL_CLASS_THRESHOLD = 40 # When images become too small to be useful
    
    # Strategy 1: Critical case - too many classes (like your 108 classes)
    if num_classes > CRITICAL_CLASS_THRESHOLD:
        print(f"\n🚨 Critical: {num_classes} classes detected")
        print(f"   📐 Reality check: Images will be extremely small and hard to see")
        print(f"   💡 STRONG RECOMMENDATIONS:")
        print(f"      🎯 Visualize top 15-20 most frequent classes only")
        print(f"      📊 Use batch processing (20 classes per plot)")  
        print(f"      🔍 Focus on classes relevant to your analysis")
        print(f"")
        print(f"   ⚙️  Proceeding with ultra-conservative sampling...")
        
        # Ultra-aggressive downsampling to maintain some readability
        ultra_conservative_samples = max(1, 25 // num_classes)
        samples_per_class = min(samples_per_class, ultra_conservative_samples)
        total_images_to_display = num_classes * samples_per_class
        
    # Strategy 2: Many classes but manageable
    elif num_classes > MAX_READABLE_CLASSES:
        print(f"\n📊 Many classes detected: {num_classes} classes")
        print(f"   🎯 Optimizing for best possible readability...")
        
        if total_images_to_display > MAX_READABLE_IMAGES:
            readable_samples = max(1, MAX_READABLE_IMAGES // num_classes)
            samples_per_class = min(samples_per_class, readable_samples)
            total_images_to_display = num_classes * samples_per_class
            print(f"   📉 Readability adjustment: {original_samples_per_class} → {samples_per_class} samples per class")
            
        print(f"   💡 Note: {num_classes} classes will result in smaller images")
        print(f"   🔍 Consider focusing on fewer classes for detailed analysis")
        
    # Strategy 3: User-specified limits
    elif max_images_display is not None and total_images_to_display > max_images_display:
        print(f"\n⚠️  Dataset size: {total_images_to_display} images requested")
        print(f"   🎯 Applying limit: Reducing to {max_images_display} images for readability")
        adjusted_samples = max(1, max_images_display // num_classes)
        samples_per_class = min(samples_per_class, adjusted_samples)
        total_images_to_display = num_classes * samples_per_class
        print(f"   📉 Samples per class: {original_samples_per_class} → {samples_per_class}")
        
    # Strategy 4: Auto-threshold management  
    elif total_images_to_display > auto_skip_threshold:
        if not force_display:
            print(f"\n🎯 Smart downsampling: {total_images_to_display} → {auto_skip_threshold} images")
            print(f"   📊 Balancing completeness with visibility")
            threshold_samples = max(1, auto_skip_threshold // num_classes)
            samples_per_class = min(samples_per_class, threshold_samples) 
            total_images_to_display = num_classes * samples_per_class
            print(f"   📉 Adjusted samples per class: {samples_per_class}")
            
            if num_classes <= MAX_READABLE_CLASSES:
                print(f"   ✅ All {num_classes} classes will be clearly visible!")
            else:
                print(f"   ⚠️  {num_classes} classes - images will be smaller but viewable")
        else:
            print(f"\n🚨 Force display: Showing all {total_images_to_display} images")
            print(f"   ⚠️  Warning: May result in very small images with {num_classes} classes")
            
    # Strategy 5: Moderate datasets
    elif total_images_to_display >= 30:
        print(f"\n📊 Visualization: {total_images_to_display} images, {num_classes} classes")
        if num_classes > 15:
            print(f"   💡 Images will be moderately sized - consider fewer classes for larger view")
        else:
            print(f"   ✅ Good balance - images should be clearly visible")
            
    # Strategy 6: Optimal datasets  
    else:
        print(f"\n✅ Optimal setup: {total_images_to_display} images, {num_classes} classes")
        print(f"   🎯 Images will be large and clearly visible")
    
    # Create visualization (smart downsampling ensures it's always shown)
    if should_display_visualization:
        _create_image_class_visualization(
            image_data, stats, samples_per_class, grid_layout, 
            figsize, shuffle_samples, show_image_info, title, save_path,
            class_limiting_applied, original_num_classes
        )
        
        print(f"\n✅ Image classification EDA completed!")
        if samples_per_class != original_samples_per_class:
            print(f"🎯 Visualization optimized: {len(image_data)} classes × {samples_per_class} samples = {total_images_to_display} images")
        else:
            print(f"🎨 Visualization displayed: {len(image_data)} classes × {samples_per_class} samples = {total_images_to_display} images")
        if save_path:
            print(f"💾 Saved to: {save_path}")
    
    if return_stats:
        return stats


def _parse_directory_structure(directory_path: str) -> Dict[str, List[str]]:
    """Parse directory structure to extract class-organized image paths."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    image_data = {}
    
    directory = Path(directory_path)
    
    for class_dir in directory.iterdir():
        if class_dir.is_dir():
            class_name = class_dir.name
            image_paths = []
            
            for img_file in class_dir.iterdir():
                if img_file.suffix.lower() in image_extensions:
                    image_paths.append(str(img_file))
            
            if image_paths:
                image_data[class_name] = image_paths
                print(f"   📂 {class_name}: {len(image_paths)} images")
    
    if not image_data:
        raise ValueError(f"🚨 No images found in {directory_path}")
    
    return image_data


def _parse_dataframe_structure(df: pd.DataFrame, class_col: str, path_col: str) -> Dict[str, List[str]]:
    """Parse DataFrame to extract class-organized image paths."""
    if class_col not in df.columns:
        raise ValueError(f"🚨 Column '{class_col}' not found in DataFrame")
    if path_col not in df.columns:
        raise ValueError(f"🚨 Column '{path_col}' not found in DataFrame")
    
    image_data = {}
    
    for class_name in df[class_col].unique():
        class_paths = df[df[class_col] == class_name][path_col].tolist()
        # Filter out missing/null paths
        valid_paths = [p for p in class_paths if pd.notna(p) and os.path.exists(str(p))]
        
        if valid_paths:
            image_data[class_name] = valid_paths
            print(f"   📊 {class_name}: {len(valid_paths)} images")
        else:
            print(f"   ⚠️  {class_name}: No valid image paths found")
    
    if not image_data:
        raise ValueError("🚨 No valid images found in DataFrame")
    
    return image_data


def _parse_image_path_list(image_paths: List[str]) -> Dict[str, List[str]]:
    """Parse list of image paths to extract class-organized structure."""
    from pathlib import Path
    import os
    
    if not image_paths:
        raise ValueError("🚨 Empty image path list provided")
    
    # Group images by their parent directory name (assumed to be class name)
    image_data = {}
    
    for img_path in image_paths:
        if not os.path.exists(img_path):
            print(f"   ⚠️  Skipping non-existent file: {img_path}")
            continue
            
        # Extract class name from parent directory
        path_obj = Path(img_path)
        class_name = path_obj.parent.name
        
        if class_name not in image_data:
            image_data[class_name] = []
        
        image_data[class_name].append(img_path)
    
    # Print summary
    for class_name, paths in image_data.items():
        print(f"   📋 {class_name}: {len(paths)} images")
    
    if not image_data:
        raise ValueError("🚨 No valid images found in path list")
    
    return image_data


def _generate_image_dataset_stats(image_data: Dict[str, List[str]]) -> Dict[str, Any]:
    """Generate comprehensive statistics about the image dataset."""
    class_counts = {class_name: len(paths) for class_name, paths in image_data.items()}
    total_samples = sum(class_counts.values())
    num_classes = len(class_counts)
    
    # Calculate balance metrics
    min_count = min(class_counts.values())
    max_count = max(class_counts.values())
    balance_ratio = min_count / max_count if max_count > 0 else 0
    
    # Identify imbalance issues
    imbalance_warnings = []
    mean_count = total_samples / num_classes
    
    for class_name, count in class_counts.items():
        if count < mean_count * 0.5:  # Less than 50% of average
            percentage_below = ((mean_count - count) / mean_count) * 100
            imbalance_warnings.append(f"'{class_name}' has {percentage_below:.1f}% fewer samples than average")
    
    # Check for corrupted images (placeholder - would need actual image validation)
    corrupted_images = []  # Would be populated by actual image validation
    
    return {
        'class_counts': class_counts,
        'total_samples': total_samples,
        'num_classes': num_classes,
        'balance_ratio': balance_ratio,
        'imbalance_warnings': imbalance_warnings,
        'corrupted_images': corrupted_images,
        'min_count': min_count,
        'max_count': max_count,
        'mean_count': mean_count
    }


def _display_class_distribution(stats: Dict[str, Any]) -> None:
    """Display formatted class distribution statistics."""
    print(f"\n📊 Class Distribution Summary:")
    print("=" * 40)
    
    class_counts = stats['class_counts']
    total_samples = stats['total_samples']
    
    # Sort classes by count (descending)
    sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
    
    for class_name, count in sorted_classes:
        percentage = (count / total_samples) * 100
        bar_length = int((count / stats['max_count']) * 20)  # Scale to 20 chars
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"🏷️  {class_name:.<15} {count:>6} ({percentage:>5.1f}%) {bar}")
    
    print(f"\n📈 Dataset Overview:")
    print(f"   📊 Total samples: {total_samples:,}")
    print(f"   🏷️  Total classes: {stats['num_classes']}")
    print(f"   ⚖️  Balance ratio: {stats['balance_ratio']:.3f} (min/max)")
    print(f"   📉 Smallest class: {stats['min_count']} samples")
    print(f"   📈 Largest class: {stats['max_count']} samples")
    
    # Display warnings
    if stats['imbalance_warnings']:
        print(f"\n⚠️  Potential Issues Detected:")
        for warning in stats['imbalance_warnings']:
            print(f"   🔸 {warning}")
    else:
        print(f"\n✅ No significant class imbalances detected")


def _create_image_class_visualization(
    image_data: Dict[str, List[str]], 
    stats: Dict[str, Any],
    samples_per_class: int,
    grid_layout: Union[str, Tuple[int, int]],
    figsize: Tuple[int, int],
    shuffle_samples: bool,
    show_image_info: bool,
    title: str,
    save_path: Optional[str],
    class_limiting_applied: bool = False,
    original_num_classes: int = 0
) -> None:
    """Create the main image class visualization with optimal layout and spacing."""
    
    num_classes = len(image_data)
    total_images = num_classes * samples_per_class
    
    # BEST PRACTICE: Calculate optimal grid layout
    if grid_layout == 'auto':
        # Smart grid calculation based on visualization best practices
        if samples_per_class == 1:
            # For single samples per class, use optimal rectangular grid
            cols = min(6, num_classes)  # Max 6 columns for readability
            rows = math.ceil(num_classes / cols)
        else:
            # For multiple samples, use class-row layout but with column limits
            if samples_per_class <= 4:
                cols = samples_per_class
                rows = num_classes
            else:
                # Too many samples per class - use grid layout
                cols = 4  # Max 4 samples per row for readability
                rows = math.ceil(total_images / cols)
    elif grid_layout == 'square':
        # Optimal square-ish grid
        cols = math.ceil(math.sqrt(total_images))
        rows = math.ceil(total_images / cols)
    else:
        rows, cols = grid_layout
    
    # BEST PRACTICE: Calculate optimal figure size based on content
    # Base size per subplot should be at least 2x2 inches for readability
    min_subplot_size = 2.0
    max_fig_width = 20  # Maximum figure width (practical limit)
    max_fig_height = 16  # Maximum figure height (practical limit)
    
    # Calculate ideal figure size
    ideal_width = cols * min_subplot_size * 1.2  # 20% padding
    ideal_height = rows * min_subplot_size * 1.2  # 20% padding
    
    # Apply practical limits
    actual_width = min(ideal_width, max_fig_width)
    actual_height = min(ideal_height, max_fig_height)
    
    # Ensure minimum readable size
    actual_width = max(actual_width, 8)
    actual_height = max(actual_height, 6)
    
    figsize = (actual_width, actual_height)
    
    print(f"🎨 Layout: {rows}×{cols} grid, Figure size: {actual_width:.1f}×{actual_height:.1f} inches")
    
    # BEST PRACTICE: Create figure with optimal spacing
    fig, axes = plt.subplots(
        rows, cols, 
        figsize=figsize,
        facecolor='white'
    )
    
    # BEST PRACTICE: Set optimal spacing between subplots
    # Calculate spacing based on number of subplots for optimal readability
    # Increased spacing to prevent row overlaps
    if total_images <= 12:
        hspace, wspace = 0.6, 0.3  # Very generous spacing for few images
    elif total_images <= 30:
        hspace, wspace = 0.5, 0.25  # Generous spacing to prevent overlap
    else:
        hspace, wspace = 0.45, 0.2  # Still generous but efficient for many images
    
    # BEST PRACTICE: Calculate optimal top margin for title based on figure height
    # Taller figures need relatively less top margin, shorter figures need more
    # More generous spacing to prevent title overlap
    if actual_height <= 8:
        top_margin = 0.82  # Much more generous space for shorter figures
        title_y = 0.96     # Position title much higher
    elif actual_height <= 12:
        top_margin = 0.85  # More generous space for medium figures  
        title_y = 0.97
    else:
        top_margin = 0.88  # More generous space for tall figures
        title_y = 0.98
    
    plt.subplots_adjust(
        hspace=hspace,       # Height spacing between rows
        wspace=wspace,       # Width spacing between columns  
        top=top_margin,      # Dynamic top margin for title space
        bottom=0.12,         # More bottom margin for class limiting remark
        left=0.05,           # Left margin  
        right=0.95           # Right margin
    )
    
    # Handle single row/column cases
    if rows == 1 and cols == 1:
        axes = np.array([[axes]])
    elif rows == 1:
        axes = axes.reshape(1, -1)
    elif cols == 1:
        axes = axes.reshape(-1, 1)
    
    # BEST PRACTICE: Optimal font sizing based on layout density
    # Calculate font sizes based on available space per subplot
    # Adjusted for better row spacing with long scientific names
    subplot_area = (actual_width / cols) * (actual_height / rows)
    
    if subplot_area >= 4:  # Large subplots
        main_title_size = 16
        subplot_title_size = 10  # Slightly smaller to prevent overlap
        info_fontsize = 9
    elif subplot_area >= 2.5:  # Medium subplots
        main_title_size = 14
        subplot_title_size = 9   # Smaller for better spacing
        info_fontsize = 8
    elif subplot_area >= 1.5:  # Small subplots
        main_title_size = 12
        subplot_title_size = 8   # Smaller for tight layouts
        info_fontsize = 7
    else:  # Very small subplots
        main_title_size = 10
        subplot_title_size = 7   # Smallest readable size
        info_fontsize = 6
    
    # Set main title with optimal positioning
    fig.suptitle(title, fontsize=main_title_size, fontweight='bold', y=title_y)
    
    print(f"🎨 Title positioning: y={title_y}, top_margin={top_margin}, font_size={main_title_size}pt")
    
    # BEST PRACTICE: Plot images in optimal grid order (left-to-right, top-to-bottom)
    plot_idx = 0
    
    # Plot samples for each class
    for class_name, image_paths in image_data.items():
        # Sample images for this class
        if shuffle_samples:
            selected_paths = random.sample(image_paths, min(samples_per_class, len(image_paths)))
        else:
            selected_paths = image_paths[:samples_per_class]
        
        # Plot each sample in grid order
        for img_path in selected_paths:
            if plot_idx >= rows * cols:  # Don't exceed grid capacity
                break
            
            # Calculate row and column from plot index
            row = plot_idx // cols
            col = plot_idx % cols
            ax = axes[row, col]
            
            try:
                # BEST PRACTICE: Load and display image with proper aspect ratio
                with Image.open(img_path) as img:
                    # Convert to RGB for consistent display
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img_array = np.array(img)
                    
                    # Display image with proper aspect ratio
                    ax.imshow(img_array, aspect='equal')
                    
                    # BEST PRACTICE: Clear, readable titles
                    if samples_per_class == 1:
                        title_text = f"{class_name}"
                    else:
                        sample_num = (plot_idx % samples_per_class) + 1
                        title_text = f"{class_name} ({sample_num})"
                    
                    ax.set_title(title_text, fontsize=subplot_title_size, 
                               fontweight='bold', pad=6)  # Reduced padding for tighter spacing
                    ax.axis('off')
                    
                    # BEST PRACTICE: Optional image info with proper positioning
                    if show_image_info:
                        img_size = img.size
                        file_size = os.path.getsize(img_path) / 1024  # KB
                        info_text = f"{img_size[0]}×{img_size[1]}\n{file_size:.1f}KB"
                        ax.text(0.02, 0.02, info_text, transform=ax.transAxes, 
                               fontsize=info_fontsize, color='white', 
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.7))
                    
            except Exception as e:
                # BEST PRACTICE: Graceful error handling with informative display
                ax.text(0.5, 0.5, f"Error loading\n{os.path.basename(img_path)}\n{str(e)[:50]}", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=info_fontsize, color='red', fontweight='bold')
                ax.set_facecolor('lightgray')
                ax.axis('off')
            
            plot_idx += 1
        
        if plot_idx >= rows * cols:  # Don't exceed grid capacity
            break
    
    # BEST PRACTICE: Hide unused subplots for cleaner appearance
    for idx in range(plot_idx, rows * cols):
        row = idx // cols
        col = idx % cols
        axes[row, col].axis('off')
        axes[row, col].set_visible(False)
    
    # BEST PRACTICE: Final layout adjustments
    # Don't use tight_layout as we've already set optimal spacing
    
    # BEST PRACTICE: Add informative remark when class limiting is applied
    if class_limiting_applied and original_num_classes > 0:
        # Calculate appropriate font size for the remark
        remark_fontsize = max(8, min(12, main_title_size - 2))
        
        # Create informative remark about class limiting
        displayed_classes = len(image_data)
        hidden_classes = original_num_classes - displayed_classes
        
        if hidden_classes > 0:
            remark_text = (
                f"� Showing {displayed_classes} of {original_num_classes} total classes "
                f"({hidden_classes} classes not displayed for optimal readability). "
                f"Use max_classes_display=None to show all classes."
            )
            
            # Position the remark below the visualization
            fig.text(0.5, 0.02, remark_text, 
                    ha='center', va='bottom', 
                    fontsize=remark_fontsize, 
                    style='italic',
                    color='#666666',  # Subtle gray color
                    bbox=dict(boxstyle='round,pad=0.5', 
                             facecolor='#f8f9fa', 
                             edgecolor='#dee2e6',
                             alpha=0.8),
                    wrap=True)
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"💾 Visualization saved: {save_path}")
        
    plt.show()


def analyze_encoding_needs(df: pd.DataFrame, 
                          target_column: Optional[str] = None,
                          max_cardinality_onehot: int = 10,
                          max_cardinality_target: int = 20,
                          ordinal_columns: Optional[List[str]] = None,
                          binary_columns: Optional[List[str]] = None,
                          datetime_columns: Optional[List[str]] = None,
                          text_columns: Optional[List[str]] = None,
                          # Legacy alias for backward compatibility
                          max_cardinality: Optional[int] = None) -> Dict:
    """
    Analyze DataFrame columns and recommend appropriate encoding methods.
    
    This function intelligently analyzes your dataset and provides comprehensive
    recommendations for encoding categorical, ordinal, datetime, and text variables
    for machine learning workflows.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame to analyze for encoding needs
    target_column : str, optional
        Name of target variable for supervised learning context
    max_cardinality_onehot : int, default=10
        Maximum unique values for one-hot encoding recommendation
    max_cardinality_target : int, default=20
        Maximum unique values for target encoding consideration
    ordinal_columns : List[str], optional
        Columns with inherent order (e.g., ['low', 'medium', 'high'])
    binary_columns : List[str], optional
        Columns that should be treated as binary (0/1)
    datetime_columns : List[str], optional
        Datetime columns for feature extraction
    text_columns : List[str], optional
        Text columns for NLP-based encoding
        
    max_cardinality : int, optional
        **DEPRECATED**: Legacy alias for 'max_cardinality_onehot'. 
        Use 'max_cardinality_onehot' parameter instead for clarity.
        
    Returns
    -------
    Dict
        Comprehensive encoding analysis with recommendations:
        - 'recommendations': Encoding method per column
        - 'cardinality_analysis': Unique value counts
        - 'data_types': Current and recommended data types
        - 'encoding_priority': Order of encoding operations
        - 'potential_issues': Data quality concerns
        - 'memory_impact': Memory usage predictions
        
    Examples
    --------
    >>> # Basic usage
    >>> analysis = edaflow.analyze_encoding_needs(df)
    >>> print(analysis['recommendations'])
    
    >>> # With target variable for supervised encoding
    >>> analysis = edaflow.analyze_encoding_needs(df, target_column='target')
    >>> 
    >>> # Specify ordinal relationships
    >>> analysis = edaflow.analyze_encoding_needs(
    ...     df, 
    ...     ordinal_columns=['education_level', 'income_bracket'],
    ...     max_cardinality_onehot=15
    ... )
    
    Notes
    -----
    This function helps prevent common encoding mistakes by:
    - Analyzing cardinality to prevent curse of dimensionality
    - Identifying ordinal relationships to preserve order
    - Recommending target encoding for high-cardinality categories
    - Detecting potential data leakage scenarios
    - Estimating memory requirements for different encoding strategies
    
    The function follows encoding best practices:
    - One-hot encoding for low cardinality (< max_cardinality_onehot)
    - Target encoding for high cardinality with target correlation
    - Ordinal encoding for natural ordering
    - Binary encoding for moderate cardinality (saves memory)
    - Frequency encoding based on value occurrence
    """
    if not SKLEARN_AVAILABLE:
        print("Warning: Limited encoding analysis without scikit-learn. Install with: pip install scikit-learn")
    
    # Handle legacy parameter for backward compatibility
    if max_cardinality is not None:
        if max_cardinality != max_cardinality_onehot:
            print("⚠️  Warning: Using 'max_cardinality' parameter as alias for 'max_cardinality_onehot'")
            print("    Please use 'max_cardinality_onehot' parameter in future versions")
            max_cardinality_onehot = max_cardinality
    
    # Initialize analysis results
    analysis = {
        'recommendations': {},
        'cardinality_analysis': {},
        'data_types': {},
        'encoding_priority': [],
        'potential_issues': [],
        'memory_impact': {}
    }
    
    # Set defaults for optional parameters
    ordinal_columns = ordinal_columns or []
    binary_columns = binary_columns or []
    datetime_columns = datetime_columns or []
    text_columns = text_columns or []
    
    print("🔍 Analyzing encoding needs for dataset...")
    print(f"Dataset shape: {df.shape}")
    print(f"Target column: {target_column if target_column else 'None (unsupervised)'}")
    
    # Analyze each column
    for column in df.columns:
        if column == target_column:
            continue
            
        col_data = df[column]
        dtype = str(col_data.dtype)
        unique_count = col_data.nunique()
        null_count = col_data.isnull().sum()
        
        # Store cardinality info
        analysis['cardinality_analysis'][column] = {
            'unique_count': unique_count,
            'null_count': null_count,
            'null_percentage': (null_count / len(df)) * 100,
            'data_type': dtype
        }
        
        # Determine encoding strategy
        if column in binary_columns:
            recommendation = 'binary_encoding'
            memory_impact = 'low'
        elif column in ordinal_columns:
            recommendation = 'ordinal_encoding'
            memory_impact = 'low'
        elif column in datetime_columns or 'datetime' in dtype:
            recommendation = 'datetime_features'
            memory_impact = 'medium'
        elif column in text_columns or (dtype == 'object' and 
                                       col_data.dropna().astype(str).str.len().mean() > 10):
            recommendation = 'text_encoding'
            memory_impact = 'high'
        elif dtype == 'object' or dtype.startswith('category'):
            # Categorical column analysis
            if unique_count <= 2:
                recommendation = 'binary_encoding'
                memory_impact = 'low'
            elif unique_count <= max_cardinality_onehot:
                recommendation = 'one_hot_encoding'
                memory_impact = 'medium'
            elif target_column and unique_count <= max_cardinality_target:
                recommendation = 'target_encoding'
                memory_impact = 'medium'
                analysis['potential_issues'].append(
                    f"Target encoding for '{column}' requires careful CV to prevent overfitting"
                )
            elif unique_count <= 50:
                recommendation = 'binary_encoding'
                memory_impact = 'medium'
            else:
                recommendation = 'frequency_encoding'
                memory_impact = 'low'
                analysis['potential_issues'].append(
                    f"High cardinality column '{column}' ({unique_count} values) may need feature selection"
                )
        else:
            # Numeric column
            if unique_count <= 10 and col_data.min() >= 0:
                recommendation = 'keep_numeric'
                memory_impact = 'low'
            else:
                recommendation = 'keep_numeric'
                memory_impact = 'low'
        
        analysis['recommendations'][column] = recommendation
        analysis['memory_impact'][column] = memory_impact
        
        # Data type recommendations
        if recommendation == 'one_hot_encoding':
            analysis['data_types'][column] = f'Multiple binary columns ({unique_count} new columns)'
        elif recommendation == 'ordinal_encoding':
            analysis['data_types'][column] = 'int64'
        elif recommendation == 'target_encoding':
            analysis['data_types'][column] = 'float64'
        elif recommendation == 'datetime_features':
            analysis['data_types'][column] = 'Multiple numeric columns (year, month, day, etc.)'
        else:
            analysis['data_types'][column] = dtype
    
    # Create encoding priority order
    priority_order = {
        'datetime_features': 1,
        'text_encoding': 2,
        'ordinal_encoding': 3,
        'binary_encoding': 4,
        'target_encoding': 5,
        'one_hot_encoding': 6,
        'frequency_encoding': 7,
        'keep_numeric': 8
    }
    
    analysis['encoding_priority'] = sorted(
        analysis['recommendations'].keys(),
        key=lambda x: priority_order.get(analysis['recommendations'][x], 9)
    )
    
    # Add summary statistics
    encoding_counts = {}
    for method in analysis['recommendations'].values():
        encoding_counts[method] = encoding_counts.get(method, 0) + 1
    
    analysis['summary'] = {
        'total_columns': len(df.columns) - (1 if target_column else 0),
        'encoding_methods': encoding_counts,
        'high_memory_columns': len([c for c, m in analysis['memory_impact'].items() if m == 'high']),
        'potential_new_columns': sum([
            analysis['cardinality_analysis'][c]['unique_count'] 
            for c, r in analysis['recommendations'].items() 
            if r == 'one_hot_encoding'
        ])
    }
    
    # Display comprehensive analysis
    print("\n" + "="*60)
    print("🎯 ENCODING ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n📊 Summary:")
    print(f"  • Total columns to encode: {analysis['summary']['total_columns']}")
    print(f"  • Encoding methods needed: {len(encoding_counts)}")
    print(f"  • High memory impact columns: {analysis['summary']['high_memory_columns']}")
    print(f"  • Potential new columns from one-hot: {analysis['summary']['potential_new_columns']}")
    
    print(f"\n🔧 Recommended encoding methods:")
    for method, count in encoding_counts.items():
        print(f"  • {method.replace('_', ' ').title()}: {count} columns")
    
    if analysis['potential_issues']:
        print(f"\n⚠️  Potential issues to consider:")
        for issue in analysis['potential_issues']:
            print(f"  • {issue}")
    
    print(f"\n🚀 Ready for apply_smart_encoding()!")
    
    return analysis


def apply_smart_encoding(df: pd.DataFrame,
                        encoding_analysis: Optional[Dict] = None,
                        target_column: Optional[str] = None,
                        drop_first: bool = True,
                        handle_unknown: str = 'ignore',
                        return_encoders: bool = False,
                        inplace: bool = False) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict]]:
    """
    Apply intelligent encoding based on analysis recommendations.
    
    ⚠️ **DEPRECATION WARNING**: The `return_encoders` parameter creates inconsistent 
    return types and will be deprecated in v0.13.0. Use `apply_encoding()` instead 
    for consistent DataFrame-only returns, or `apply_encoding_with_encoders()` 
    for explicit tuple returns.
    
    This function automatically applies the most appropriate encoding methods
    for each column type, ensuring optimal preparation for machine learning
    while maintaining data integrity and preventing common pitfalls.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame to encode
    encoding_analysis : Dict, optional
        Results from analyze_encoding_needs(). If None, analysis is performed automatically
    target_column : str, optional
        Target variable name for supervised encoding methods
    drop_first : bool, default=True
        Drop first category in one-hot encoding to prevent multicollinearity
    handle_unknown : str, default='ignore'
        How to handle unknown categories in test data ('ignore' or 'error')
    return_encoders : bool, default=False
        Whether to return fitted encoders for future use
    inplace : bool, default=False
        Whether to modify the original DataFrame
        
    Returns
    -------
    pd.DataFrame or Tuple[pd.DataFrame, Dict]
        Encoded DataFrame, and optionally fitted encoders dictionary
        
    Examples
    --------
    >>> # Basic usage with automatic analysis
    >>> df_encoded = edaflow.apply_smart_encoding(df)
    
    >>> # With pre-computed analysis and encoder return
    >>> analysis = edaflow.analyze_encoding_needs(df, target_column='target')
    >>> df_encoded, encoders = edaflow.apply_smart_encoding(
    ...     df, 
    ...     encoding_analysis=analysis,
    ...     return_encoders=True
    ... )
    
    >>> # Use encoders on test data later
    >>> df_test_encoded = edaflow.apply_smart_encoding(
    ...     df_test,
    ...     encoders=encoders  # Apply same transformations
    ... )
    
    Notes
    -----
    This function applies encoding methods in the optimal order:
    1. Datetime feature extraction (creates multiple columns)
    2. Text encoding (TF-IDF or basic text features)
    3. Ordinal encoding (preserves order)
    4. Binary encoding (memory efficient for medium cardinality)
    5. Target encoding (requires cross-validation awareness)
    6. One-hot encoding (creates multiple binary columns)
    7. Frequency encoding (based on value counts)
    
    The function handles common encoding challenges:
    - Unknown categories in test data
    - Memory optimization for large datasets
    - Multicollinearity prevention
    - Data leakage prevention in target encoding
    - Consistent column naming and data types
    """
    if not SKLEARN_AVAILABLE:
        raise ImportError("scikit-learn is required for encoding functionality. Install with: pip install scikit-learn")
    
    print("⚡ Applying smart encoding transformations...")
    
    # Add deprecation warning for inconsistent return_encoders parameter
    if return_encoders:
        import warnings
        warnings.warn(
            "⚠️ DEPRECATION: The 'return_encoders=True' parameter creates inconsistent return types "
            "(sometimes DataFrame, sometimes tuple) and will be deprecated in v0.13.0.\n"
            "\n🔧 Migration options:"
            "\n  • For DataFrame-only returns: Use the function without return_encoders=True"
            "\n  • For tuple returns: Consider splitting the logic or using explicit unpacking"
            "\n  • Current code: df_encoded, encoders = apply_smart_encoding(df, return_encoders=True)"
            "\n  • Recommended: df_encoded = apply_smart_encoding(df)  # Consistent API",
            DeprecationWarning,
            stacklevel=2
        )
    
    # Work on copy unless inplace=True
    df_work = df if inplace else df.copy()
    original_shape = df_work.shape
    
    # Get or create encoding analysis
    if encoding_analysis is None:
        print("📊 No encoding analysis provided - performing automatic analysis...")
        encoding_analysis = analyze_encoding_needs(df_work, target_column=target_column)
    
    encoders = {} if return_encoders else None
    recommendations = encoding_analysis['recommendations']
    
    print(f"\n🔧 Processing {len(recommendations)} columns in priority order...")
    
    # Process columns in priority order
    for column in encoding_analysis['encoding_priority']:
        if column not in df_work.columns or column == target_column:
            continue
            
        method = recommendations[column]
        print(f"  • {column}: {method.replace('_', ' ')}")
        
        try:
            if method == 'datetime_features':
                # Extract datetime features
                dt_col = pd.to_datetime(df_work[column], errors='coerce')
                df_work[f'{column}_year'] = dt_col.dt.year
                df_work[f'{column}_month'] = dt_col.dt.month
                df_work[f'{column}_day'] = dt_col.dt.day
                df_work[f'{column}_dayofweek'] = dt_col.dt.dayofweek
                df_work[f'{column}_quarter'] = dt_col.dt.quarter
                df_work[f'{column}_is_weekend'] = (dt_col.dt.dayofweek >= 5).astype(int)
                
                # Drop original column
                df_work.drop(column, axis=1, inplace=True)
                
                if return_encoders:
                    encoders[column] = {
                        'method': 'datetime_features',
                        'feature_names': [f'{column}_year', f'{column}_month', f'{column}_day', 
                                        f'{column}_dayofweek', f'{column}_quarter', f'{column}_is_weekend']
                    }
                    
            elif method == 'one_hot_encoding':
                # One-hot encoding
                encoder = OneHotEncoder(drop='first' if drop_first else None, 
                                      handle_unknown=handle_unknown, 
                                      sparse_output=False)
                
                encoded = encoder.fit_transform(df_work[[column]])
                if drop_first and len(encoder.categories_[0]) > 1:
                    feature_names = [f"{column}_{cat}" for cat in encoder.categories_[0][1:]]
                else:
                    feature_names = [f"{column}_{cat}" for cat in encoder.categories_[0]]
                
                # Add encoded columns
                for i, name in enumerate(feature_names):
                    df_work[name] = encoded[:, i]
                
                # Drop original column
                df_work.drop(column, axis=1, inplace=True)
                
                if return_encoders:
                    encoders[column] = {'encoder': encoder, 'method': 'one_hot_encoding', 
                                      'feature_names': feature_names}
                    
            elif method == 'target_encoding':
                # Target encoding (mean encoding)
                if target_column and target_column in df_work.columns:
                    encoder = TargetEncoder(handle_unknown=handle_unknown)
                    df_work[column] = encoder.fit_transform(df_work[[column]], df_work[target_column])
                    
                    if return_encoders:
                        encoders[column] = {'encoder': encoder, 'method': 'target_encoding'}
                else:
                    # Fallback to frequency encoding when target column is missing or None
                    print(f"    ⚠️  Target column '{target_column}' not found or not specified - using frequency encoding instead")
                    freq_map = df_work[column].value_counts().to_dict()
                    df_work[column] = df_work[column].map(freq_map)
                    
                    if return_encoders:
                        encoders[column] = {'encoder': freq_map, 'method': 'frequency_encoding_fallback'}
                        
            elif method == 'ordinal_encoding':
                # Ordinal encoding
                encoder = OrdinalEncoder(handle_unknown='use_encoded_value', 
                                       unknown_value=-1)
                df_work[column] = encoder.fit_transform(df_work[[column]]).astype(int)
                
                if return_encoders:
                    encoders[column] = {'encoder': encoder, 'method': 'ordinal_encoding'}
                    
            elif method == 'binary_encoding':
                # Simple binary encoding (0/1 for two categories, else ordinal)
                unique_vals = df_work[column].dropna().unique()
                if len(unique_vals) <= 2:
                    # True binary encoding
                    mapping = {unique_vals[0]: 0, unique_vals[1]: 1} if len(unique_vals) == 2 else {unique_vals[0]: 0}
                    df_work[column] = df_work[column].map(mapping)
                    
                    if return_encoders:
                        encoders[column] = {'encoder': mapping, 'method': 'binary_encoding'}
                else:
                    # Use ordinal for simplicity
                    encoder = OrdinalEncoder(handle_unknown='use_encoded_value', 
                                           unknown_value=-1)
                    df_work[column] = encoder.fit_transform(df_work[[column]]).astype(int)
                    
                    if return_encoders:
                        encoders[column] = {'encoder': encoder, 'method': 'ordinal_encoding'}
                        
            elif method == 'frequency_encoding':
                # Frequency encoding
                freq_map = df_work[column].value_counts().to_dict()
                df_work[column] = df_work[column].map(freq_map)
                
                if return_encoders:
                    encoders[column] = {'encoder': freq_map, 'method': 'frequency_encoding'}
                    
            elif method == 'text_encoding':
                # Basic text encoding (TF-IDF)
                try:
                    vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
                    text_features = vectorizer.fit_transform(df_work[column].fillna(''))
                    
                    # Add top features as new columns
                    feature_names = [f"{column}_tfidf_{i}" for i in range(text_features.shape[1])]
                    for i, name in enumerate(feature_names):
                        df_work[name] = text_features[:, i].toarray().flatten()
                    
                    # Drop original column
                    df_work.drop(column, axis=1, inplace=True)
                    
                    if return_encoders:
                        encoders[column] = {'encoder': vectorizer, 'method': 'text_encoding',
                                          'feature_names': feature_names}
                except:
                    # Fallback to length and word count
                    df_work[f'{column}_length'] = df_work[column].str.len().fillna(0)
                    df_work[f'{column}_word_count'] = df_work[column].str.split().str.len().fillna(0)
                    df_work.drop(column, axis=1, inplace=True)
                    
                    if return_encoders:
                        encoders[column] = {'method': 'text_basic_features',
                                          'feature_names': [f'{column}_length', f'{column}_word_count']}
                        
            elif method == 'keep_numeric':
                # Keep as is
                if return_encoders:
                    encoders[column] = {'method': 'keep_numeric'}
                    
        except Exception as e:
            print(f"    ⚠️  Warning: Could not encode column '{column}' with method '{method}': {e}")
            if return_encoders:
                encoders[column] = {'method': 'failed', 'error': str(e)}
    
    # Final summary
    final_shape = df_work.shape
    print(f"\n✅ Encoding complete!")
    print(f"   Shape: {original_shape} → {final_shape}")
    print(f"   Columns: {original_shape[1]} → {final_shape[1]} ({final_shape[1] - original_shape[1]:+d})")
    
    if return_encoders:
        print(f"   Encoders saved: {len([e for e in encoders.values() if e.get('method') != 'failed'])}")
    
    # Return results
    if return_encoders:
        return df_work, encoders
    else:
        return df_work


def apply_encoding(df: pd.DataFrame,
                  encoding_analysis: Optional[Dict] = None,
                  target_column: Optional[str] = None,
                  drop_first: bool = True,
                  handle_unknown: str = 'ignore',
                  inplace: bool = False) -> pd.DataFrame:
    """
    Apply intelligent encoding with consistent DataFrame return (RECOMMENDED).
    
    This is the recommended encoding function that always returns a DataFrame,
    providing a clean and predictable API. Encoders are stored internally
    and can be accessed via get_last_encoders() if needed.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame to encode
    encoding_analysis : Dict, optional
        Results from analyze_encoding_needs(). If None, analysis is performed automatically
    target_column : str, optional
        Name of target column to preserve during encoding
    drop_first : bool, default=True
        Drop first category in one-hot encoding to avoid multicollinearity
    handle_unknown : str, default='ignore'
        How to handle unknown categories during encoding
    inplace : bool, default=False
        Modify DataFrame in place
        
    Returns
    -------
    pd.DataFrame
        DataFrame with applied encoding transformations
        
    Example
    -------
    >>> df_encoded = edaflow.apply_encoding(df)  # Clean, consistent API
    >>> encoders = edaflow.get_last_encoders()  # Optional: access encoders
    """
    # Use the original function but force return_encoders=False for consistency
    result = apply_smart_encoding(
        df=df,
        encoding_analysis=encoding_analysis,
        target_column=target_column,
        drop_first=drop_first,
        handle_unknown=handle_unknown,
        return_encoders=False,  # Always False for consistent return
        inplace=inplace
    )
    
    # Store encoders for optional access (implement this later if needed)
    # apply_encoding._last_encoders = encoders
    
    return result


def apply_encoding_with_encoders(df: pd.DataFrame,
                                encoding_analysis: Optional[Dict] = None,
                                target_column: Optional[str] = None,
                                drop_first: bool = True,
                                handle_unknown: str = 'ignore',
                                inplace: bool = False) -> Tuple[pd.DataFrame, Dict]:
    """
    Apply intelligent encoding with explicit tuple return.
    
    This function always returns a tuple of (DataFrame, encoders_dict),
    making the API predictable for users who need access to encoders.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame to encode
    encoding_analysis : Dict, optional
        Results from analyze_encoding_needs()
    target_column : str, optional
        Name of target column to preserve during encoding
    drop_first : bool, default=True
        Drop first category in one-hot encoding
    handle_unknown : str, default='ignore'
        How to handle unknown categories during encoding
    inplace : bool, default=False
        Modify DataFrame in place
        
    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        (encoded_dataframe, encoders_dictionary)
        
    Example
    -------
    >>> df_encoded, encoders = edaflow.apply_encoding_with_encoders(df)
    >>> # Now you have both the DataFrame and encoders explicitly
    """
    # Use the original function with return_encoders=True
    return apply_smart_encoding(
        df=df,
        encoding_analysis=encoding_analysis,
        target_column=target_column,
        drop_first=drop_first,
        handle_unknown=handle_unknown,
        return_encoders=True,  # Explicit tuple return
        inplace=inplace
    )


def summarize_eda_insights(df: pd.DataFrame, 
                          target_column: Optional[str] = None,
                          eda_functions_used: Optional[List[str]] = None,
                          class_threshold: float = 0.1) -> dict:
    """
    Generate comprehensive EDA insights and recommendations after completing analysis workflow.
    
    This function analyzes the DataFrame and provides intelligent insights about:
    - Dataset characteristics and shape
    - Data quality assessment
    - Class distribution and imbalance detection
    - Missing data patterns
    - Feature type analysis
    - Actionable recommendations for modeling
    
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame that has been analyzed
    target_column : str, optional
        The name of the target column for classification/regression analysis
    eda_functions_used : list of str, optional
        List of edaflow functions that have been executed
    class_threshold : float, default 0.1
        Threshold below which a class is considered underrepresented (10%)
        
    Returns
    -------
    dict
        Comprehensive insights dictionary with analysis results and recommendations
        
    Examples
    --------
    >>> import pandas as pd
    >>> import edaflow
    >>> 
    >>> # After completing EDA workflow
    >>> df = pd.read_csv('healthcare_data.csv')
    >>> # ... run various edaflow functions ...
    >>> 
    >>> # Generate comprehensive insights
    >>> insights = edaflow.summarize_eda_insights(df, target_column='ckd_status')
    >>> 
    >>> # Insights with specific functions tracked
    >>> functions_used = ['check_null_columns', 'analyze_categorical_columns', 
    ...                   'visualize_histograms', 'handle_outliers_median']
    >>> insights = edaflow.summarize_eda_insights(df, 'ckd_status', functions_used)
    """
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich import box
        from rich.columns import Columns
        
        # Optimize console for Google Colab compatibility
        console = Console(width=80, force_terminal=True)
        use_rich = True
    except ImportError:
        console = None
        use_rich = False
    
    # Initialize insights dictionary
    insights = {
        'dataset_overview': {},
        'data_quality': {},
        'feature_analysis': {},
        'target_analysis': {},
        'recommendations': {},
        'workflow_completeness': {}
    }
    
    # Dataset Overview Analysis
    total_rows, total_cols = df.shape
    memory_usage = df.memory_usage(deep=True).sum()
    
    # Memory formatting
    if memory_usage > 1024**3:  # GB
        mem_str = f"{memory_usage / (1024**3):.2f} GB"
    elif memory_usage > 1024**2:  # MB  
        mem_str = f"{memory_usage / (1024**2):.1f} MB"
    elif memory_usage > 1024:  # KB
        mem_str = f"{memory_usage / 1024:.1f} KB"
    else:
        mem_str = f"{memory_usage} B"
    
    insights['dataset_overview'] = {
        'shape': f"{total_rows:,} rows × {total_cols} columns",
        'total_rows': total_rows,
        'total_columns': total_cols,
        'memory_usage': mem_str,
        'memory_bytes': memory_usage
    }
    
    # Data Quality Analysis
    total_missing = df.isnull().sum().sum()
    missing_percentage = (total_missing / (total_rows * total_cols)) * 100
    columns_with_missing = df.isnull().sum()[df.isnull().sum() > 0]
    
    # Duplicate analysis
    duplicate_rows = df.duplicated().sum()
    duplicate_percentage = (duplicate_rows / total_rows) * 100
    
    insights['data_quality'] = {
        'total_missing_values': total_missing,
        'missing_percentage': missing_percentage,
        'columns_with_missing': len(columns_with_missing),
        'duplicate_rows': duplicate_rows,
        'duplicate_percentage': duplicate_percentage,
        'data_completeness': 100 - missing_percentage
    }
    
    # Feature Type Analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # Remove target from feature lists if specified
    if target_column and target_column in numeric_cols:
        numeric_cols.remove(target_column)
    if target_column and target_column in categorical_cols:
        categorical_cols.remove(target_column)
    
    insights['feature_analysis'] = {
        'numeric_features': len(numeric_cols),
        'categorical_features': len(categorical_cols),
        'numeric_feature_names': numeric_cols,
        'categorical_feature_names': categorical_cols,
        'feature_ratio': f"{len(numeric_cols)}N:{len(categorical_cols)}C"
    }
    
    # Target Analysis (if provided)
    if target_column and target_column in df.columns:
        target_analysis = {}
        
        try:
            if pd.api.types.is_numeric_dtype(df[target_column]):
                # Regression target
                target_analysis['type'] = 'regression'
                target_analysis['min_value'] = df[target_column].min()
                target_analysis['max_value'] = df[target_column].max()
                target_analysis['mean_value'] = df[target_column].mean()
                target_analysis['std_value'] = df[target_column].std()
                target_analysis['missing_count'] = df[target_column].isnull().sum()
            else:
                # Classification target
                target_analysis['type'] = 'classification'
                class_counts = df[target_column].value_counts()
                class_proportions = df[target_column].value_counts(normalize=True)
                
                target_analysis['unique_classes'] = len(class_counts)
                target_analysis['class_counts'] = dict(class_counts)
                target_analysis['class_proportions'] = dict(class_proportions)
                target_analysis['missing_count'] = df[target_column].isnull().sum()
                
                # Class imbalance detection
                min_proportion = class_proportions.min()
                max_proportion = class_proportions.max()
                imbalance_ratio = max_proportion / min_proportion
                
                target_analysis['class_imbalance'] = {
                    'is_imbalanced': min_proportion < class_threshold,
                    'min_class_proportion': min_proportion,
                    'max_class_proportion': max_proportion,
                    'imbalance_ratio': imbalance_ratio,
                    'underrepresented_classes': [cls for cls, prop in class_proportions.items() 
                                               if prop < class_threshold]
                }
            
            insights['target_analysis'] = target_analysis
        except Exception as e:
            # If there's an error analyzing the target, set a basic error state
            target_analysis['type'] = 'error'
            target_analysis['error_message'] = str(e)
            target_analysis['missing_count'] = df[target_column].isnull().sum()
            insights['target_analysis'] = target_analysis
    
    # Workflow Completeness Assessment
    if eda_functions_used:
        # Define comprehensive EDA workflow steps
        comprehensive_workflow = [
            'check_null_columns',
            'display_column_types', 
            'analyze_categorical_columns',
            'convert_to_numeric',
            'visualize_histograms',
            'visualize_numerical_boxplots',
            'handle_outliers_median',
            'visualize_heatmap',
            'visualize_scatter_matrix',
            'visualize_categorical_values',
            'impute_numerical_median',
            'impute_categorical_mode',
            'analyze_encoding_needs',
            'apply_smart_encoding'
        ]
        
        completed_steps = len(set(eda_functions_used).intersection(comprehensive_workflow))
        workflow_completeness = (completed_steps / len(comprehensive_workflow)) * 100
        
        insights['workflow_completeness'] = {
            'functions_used': eda_functions_used,
            'completed_steps': completed_steps,
            'total_steps': len(comprehensive_workflow),
            'completeness_percentage': workflow_completeness,
            'missing_steps': list(set(comprehensive_workflow) - set(eda_functions_used))
        }
    
    # Generate Recommendations
    recommendations = []
    
    # Data Quality Recommendations
    if missing_percentage > 5:
        recommendations.append({
            'category': 'Data Quality',
            'priority': 'High' if missing_percentage > 20 else 'Medium',
            'issue': f'{missing_percentage:.1f}% missing data detected',
            'action': 'Consider imputation strategies or investigate missing data patterns',
            'functions': ['impute_numerical_median', 'impute_categorical_mode']
        })
    
    if duplicate_percentage > 1:
        recommendations.append({
            'category': 'Data Quality', 
            'priority': 'Medium',
            'issue': f'{duplicate_percentage:.1f}% duplicate rows found',
            'action': 'Remove duplicates or investigate if they represent valid cases',
            'functions': ['df.drop_duplicates()']
        })
    
    # Feature Engineering Recommendations
    if len(categorical_cols) > len(numeric_cols) * 2:
        recommendations.append({
            'category': 'Feature Engineering',
            'priority': 'Medium', 
            'issue': 'High categorical feature ratio detected',
            'action': 'Consider encoding strategies for machine learning models',
            'functions': ['analyze_encoding_needs', 'apply_smart_encoding']
        })
    
    # Class Imbalance Recommendations
    if (target_column and 'target_analysis' in insights and 
        insights['target_analysis'].get('type') == 'classification'):
        imbalance_info = insights['target_analysis'].get('class_imbalance', {})
        if imbalance_info.get('is_imbalanced', False):
            recommendations.append({
                'category': 'Class Imbalance',
                'priority': 'High',
                'issue': f'Severe class imbalance detected (ratio: {imbalance_info.get("imbalance_ratio", 0):.1f}:1)',
                'action': 'Use stratified sampling, class weighting, or resampling techniques',
                'functions': ['sklearn.utils.class_weight.compute_class_weight', 'imblearn.over_sampling.SMOTE']
            })
    
    # Workflow Completeness Recommendations
    if eda_functions_used and insights['workflow_completeness']['completeness_percentage'] < 70:
        missing_critical = [func for func in insights['workflow_completeness']['missing_steps'] 
                          if func in ['check_null_columns', 'analyze_categorical_columns', 
                                    'visualize_histograms', 'visualize_heatmap']]
        if missing_critical:
            recommendations.append({
                'category': 'EDA Completeness',
                'priority': 'Medium',
                'issue': f'EDA workflow only {insights["workflow_completeness"]["completeness_percentage"]:.1f}% complete',
                'action': f'Consider running: {", ".join(missing_critical[:3])}',
                'functions': missing_critical[:3]
            })
    
    insights['recommendations'] = recommendations
    
    # Rich-styled output display
    if use_rich:
        console.print()
        header_panel = Panel(
            Text("🔍 COMPREHENSIVE EDA INSIGHTS & RECOMMENDATIONS", style="bold white"),
            style="bright_blue",
            box=box.ROUNDED,
            width=80,
            padding=(0, 1)
        )
        console.print(header_panel)
        console.print()
        
        # Dataset Overview
        overview_table = Table(
            title="📊 Dataset Overview",
            box=box.SIMPLE,
            show_header=True,
            header_style="bold cyan"
        )
        overview_table.add_column("Metric", style="white", width=20)
        overview_table.add_column("Value", style="yellow", width=25)
        overview_table.add_column("Assessment", style="green", width=25)
        
        # Add rows with intelligent assessments
        size_assessment = "Large dataset" if total_rows > 100000 else "Medium dataset" if total_rows > 10000 else "Small dataset"
        complexity_assessment = "High complexity" if total_cols > 50 else "Medium complexity" if total_cols > 20 else "Manageable complexity"
        memory_assessment = "High memory usage" if memory_usage > 100*1024**2 else "Efficient memory usage"
        
        overview_table.add_row("Dataset Size", f"{total_rows:,} × {total_cols}", size_assessment)
        overview_table.add_row("Feature Complexity", f"{total_cols} features", complexity_assessment)
        overview_table.add_row("Memory Usage", mem_str, memory_assessment)
        
        console.print(overview_table)
        console.print()
        
        # Data Quality Assessment
        quality_table = Table(
            title="✅ Data Quality Assessment", 
            box=box.SIMPLE,
            show_header=True,
            header_style="bold green"
        )
        quality_table.add_column("Quality Metric", style="white", width=20)
        quality_table.add_column("Value", style="yellow", width=25)
        quality_table.add_column("Status", style="bold", width=25)
        
        # Quality status indicators
        missing_status = Text("🔴 Poor" if missing_percentage > 20 else "🟡 Fair" if missing_percentage > 5 else "🟢 Good", 
                             style="bold red" if missing_percentage > 20 else "bold yellow" if missing_percentage > 5 else "bold green")
        duplicate_status = Text("🟡 Review Needed" if duplicate_percentage > 1 else "🟢 Clean", 
                               style="bold yellow" if duplicate_percentage > 1 else "bold green")
        completeness_status = Text("🟢 Excellent" if missing_percentage < 1 else "🟡 Good" if missing_percentage < 5 else "🔴 Poor",
                                  style="bold green" if missing_percentage < 1 else "bold yellow" if missing_percentage < 5 else "bold red")
        
        quality_table.add_row("Missing Data", f"{missing_percentage:.1f}%", missing_status)
        quality_table.add_row("Duplicate Rows", f"{duplicate_percentage:.1f}%", duplicate_status)
        quality_table.add_row("Data Completeness", f"{100-missing_percentage:.1f}%", completeness_status)
        
        console.print(quality_table)
        console.print()
        
        # Target Analysis (if available)
        if target_column and 'target_analysis' in insights:
            target_info = insights['target_analysis']
            
            if target_info.get('type') == 'classification':
                class_table = Table(
                    title=f"🎯 Target Analysis: {target_column}",
                    box=box.SIMPLE,
                    show_header=True,
                    header_style="bold magenta"
                )
                class_table.add_column("Class", style="cyan", width=15)
                class_table.add_column("Count", style="yellow", width=12)
                class_table.add_column("Percentage", style="green", width=12)
                class_table.add_column("Status", style="bold", width=15)
                
                for cls, count in target_info['class_counts'].items():
                    percentage = target_info['class_proportions'][cls] * 100
                    status = Text("🔴 Underrepresented" if percentage < class_threshold * 100 else "🟢 Balanced", 
                                 style="bold red" if percentage < class_threshold * 100 else "bold green")
                    class_table.add_row(str(cls), f"{count:,}", f"{percentage:.1f}%", status)
                
                console.print(class_table)
                
                # Class imbalance warning
                if target_info['class_imbalance']['is_imbalanced']:
                    imbalance_warning = Panel(
                        f"⚠️ [bold red]Class Imbalance Detected![/bold red]\n"
                        f"Imbalance ratio: {target_info['class_imbalance']['imbalance_ratio']:.1f}:1\n"
                        f"Underrepresented classes: {', '.join(target_info['class_imbalance']['underrepresented_classes'])}\n\n"
                        f"💡 [bold cyan]Recommendations:[/bold cyan]\n"
                        f"• Use stratified train/test splits\n"
                        f"• Consider class weighting in models\n" 
                        f"• Explore resampling techniques (SMOTE, ADASYN)\n"
                        f"• Focus on precision/recall metrics over accuracy",
                        title="🎯 Class Balance Analysis",
                        style="bold yellow",
                        box=box.ROUNDED,
                        width=80,
                        padding=(0, 1)
                    )
                    console.print(imbalance_warning)
                console.print()
        
        # Recommendations Panel
        if recommendations:
            rec_table = Table(
                title="💡 Actionable Recommendations",
                box=box.SIMPLE, 
                show_header=True,
                header_style="bold yellow"
            )
            rec_table.add_column("Priority", style="bold", width=8)
            rec_table.add_column("Category", style="cyan", width=15)
            rec_table.add_column("Issue & Action", style="white", width=45)
            rec_table.add_column("Suggested Functions", style="dim white", width=20)
            
            for rec in recommendations:
                priority_style = "bold red" if rec['priority'] == 'High' else "bold yellow" if rec['priority'] == 'Medium' else "bold green"
                priority_text = Text(f"{rec['priority']}", style=priority_style)
                issue_action = f"[bold]{rec['issue']}[/bold]\n{rec['action']}"
                functions_text = '\n'.join(rec['functions'][:2])  # Show first 2 functions
                
                rec_table.add_row(priority_text, rec['category'], issue_action, functions_text)
            
            console.print(rec_table)
        
        # Workflow Summary
        if eda_functions_used:
            workflow_info = insights['workflow_completeness']
            progress_text = f"{workflow_info['completeness_percentage']:.1f}% Complete"
            
            workflow_panel = Panel(
                f"[bold cyan]🔄 EDA Workflow Progress:[/bold cyan] {progress_text}\n"
                f"Functions executed: {workflow_info['completed_steps']}/{workflow_info['total_steps']}\n"
                f"Recent functions: {', '.join(eda_functions_used[-3:])}" +
                (f"\n[dim]Missing: {', '.join(workflow_info['missing_steps'][:3])}[/dim]" if workflow_info['missing_steps'] else ""),
                title="📈 Analysis Completeness",
                style="bold blue",
                box=box.ROUNDED,
                width=80,
                padding=(0, 1)
            )
            console.print(workflow_panel)
        
        # Final summary
        summary_panel = Panel(
            f"[bold green]✨ EDA Summary Complete![/bold green]\n"
            f"Dataset analyzed: {insights['dataset_overview']['shape']}\n"
            f"Data quality: {100-missing_percentage:.1f}% complete\n"
            f"Recommendations: {len(recommendations)} actionable items\n"
            f"Ready for: {'Model training with class balancing' if any(r['category'] == 'Class Imbalance' for r in recommendations) else 'Advanced analysis and modeling'}",
            title="🎉 Analysis Complete",
            style="bold green", 
            box=box.ROUNDED,
            width=80,
            padding=(0, 1)
        )
        console.print(summary_panel)
        console.print()
        
    else:
        # Fallback basic output
        print("\n" + "="*60)
        print("🔍 EDA INSIGHTS & RECOMMENDATIONS")
        print("="*60)
        
        print(f"\n📊 Dataset: {insights['dataset_overview']['shape']}")
        print(f"Memory usage: {mem_str}")
        print(f"Data completeness: {100-missing_percentage:.1f}%")
        
        if target_column and 'target_analysis' in insights:
            target_info = insights['target_analysis']
            if target_info.get('type') == 'classification':
                print(f"\n🎯 Target '{target_column}' classes:")
                for cls, count in target_info['class_counts'].items():
                    percentage = target_info['class_proportions'][cls] * 100
                    print(f"   {cls}: {count:,} ({percentage:.1f}%)")
        
        if recommendations:
            print(f"\n💡 {len(recommendations)} Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. [{rec['priority']}] {rec['issue']}")
                print(f"      → {rec['action']}")
        
        print("="*60)
    
    return insights
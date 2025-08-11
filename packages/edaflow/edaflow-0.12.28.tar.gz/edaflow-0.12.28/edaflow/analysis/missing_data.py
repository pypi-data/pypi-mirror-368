"""
Missing data analysis functions for edaflow package.
"""

import pandas as pd
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box


def check_null_columns(df, detailed=False):
    """
    Analyze missing data in DataFrame columns.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to analyze for missing data
    detailed : bool, default False
        If True, shows detailed statistics for each column with missing data
        
    Returns:
    --------
    dict
        Dictionary containing missing data statistics
    """
    console = Console()
    
    # Calculate missing data statistics
    total_rows = len(df)
    missing_counts = df.isnull().sum()
    missing_percentages = (missing_counts / total_rows) * 100
    
    # Filter to columns with missing data
    columns_with_missing = missing_counts[missing_counts > 0].sort_values(ascending=False)
    
    if len(columns_with_missing) == 0:
        console.print("✅ [bold green]No missing data found![/bold green]")
        return {
            'total_columns': len(df.columns),
            'columns_with_missing': 0,
            'missing_data_summary': {}
        }
    
    # Create summary statistics
    stats = {
        'total_columns': len(df.columns),
        'columns_with_missing': len(columns_with_missing),
        'total_missing_values': missing_counts.sum(),
        'missing_data_summary': {}
    }
    
    # Display results
    console.print()
    
    # Create header panel
    header_text = Text("📊 MISSING DATA ANALYSIS", style="bold white")
    header_panel = Panel(
        header_text,
        style="bright_blue",
        padding=(0, 1)
    )
    console.print(header_panel)
    console.print()
    
    # Create summary table
    summary_table = Table(
        title="🔍 Missing Data Summary",
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan"
    )
    
    summary_table.add_column("Metric", style="white", width=25)
    summary_table.add_column("Value", style="yellow", justify="right", width=15)
    
    summary_table.add_row("Total Columns", str(stats['total_columns']))
    summary_table.add_row("Columns with Missing Data", str(stats['columns_with_missing']))
    summary_table.add_row("Total Missing Values", f"{stats['total_missing_values']:,}")
    summary_table.add_row("Overall Missing Rate", f"{(stats['total_missing_values']/(total_rows*len(df.columns))*100):.2f}%")
    
    console.print(summary_table)
    console.print()
    
    if detailed:
        # Detailed column analysis
        detail_table = Table(
            title="📋 Detailed Column Analysis",
            box=box.SIMPLE,
            show_header=True,
            header_style="bold magenta"
        )
        
        detail_table.add_column("Column", style="cyan", width=20)
        detail_table.add_column("Missing Count", style="red", justify="right", width=15)
        detail_table.add_column("Missing %", style="yellow", justify="right", width=12)
        detail_table.add_column("Data Type", style="green", width=15)
        detail_table.add_column("Non-null Count", style="blue", justify="right", width=15)
        
        for col in columns_with_missing.index:
            missing_count = missing_counts[col]
            missing_pct = missing_percentages[col]
            non_null_count = total_rows - missing_count
            dtype = str(df[col].dtype)
            
            # Store in summary
            stats['missing_data_summary'][col] = {
                'missing_count': int(missing_count),
                'missing_percentage': float(missing_pct),
                'non_null_count': int(non_null_count),
                'data_type': dtype
            }
            
            detail_table.add_row(
                col,
                str(missing_count),
                f"{missing_pct:.1f}%",
                dtype,
                str(non_null_count)
            )
        
        console.print(detail_table)
    else:
        # Simple column listing
        simple_table = Table(
            title="📋 Columns with Missing Data",
            box=box.SIMPLE,
            show_header=True,
            header_style="bold red"
        )
        
        simple_table.add_column("Column", style="cyan", width=25)
        simple_table.add_column("Missing Count", style="red", justify="right", width=15)
        simple_table.add_column("Missing %", style="yellow", justify="right", width=12)
        
        for col in columns_with_missing.index:
            missing_count = missing_counts[col]
            missing_pct = missing_percentages[col]
            
            # Store in summary
            stats['missing_data_summary'][col] = {
                'missing_count': int(missing_count),
                'missing_percentage': float(missing_pct)
            }
            
            simple_table.add_row(
                col,
                str(missing_count),
                f"{missing_pct:.1f}%"
            )
        
        console.print(simple_table)
    
    console.print()
    
    return stats


def analyze_missing_patterns(df):
    """
    Analyze patterns in missing data across DataFrame.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to analyze for missing data patterns
        
    Returns:
    --------
    dict
        Dictionary containing missing data pattern analysis
    """
    console = Console()
    
    # Find missing data patterns
    missing_matrix = df.isnull()
    
    # Count unique missing patterns
    pattern_counts = missing_matrix.value_counts()
    
    console.print()
    console.print("[bold blue]📈 Missing Data Patterns Analysis[/bold blue]")
    console.print()
    
    if len(pattern_counts) == 1:
        console.print("✅ [green]Single missing data pattern found[/green]")
    else:
        console.print(f"🔍 [yellow]{len(pattern_counts)} unique missing data patterns found[/yellow]")
        
        # Show top patterns
        table = Table(title="🎭 Top Missing Data Patterns", show_header=True, header_style="bold cyan")
        table.add_column("Pattern Rank", style="white")
        table.add_column("Row Count", style="yellow")
        table.add_column("Percentage", style="green")
        
        for i, (pattern, count) in enumerate(pattern_counts.head(10).items(), 1):
            percentage = (count / len(df)) * 100
            table.add_row(f"#{i}", str(count), f"{percentage:.1f}%")
        
        console.print(table)
    
    console.print()
    
    return {
        'unique_patterns': len(pattern_counts),
        'pattern_distribution': dict(pattern_counts.head(10))
    }


def suggest_missing_data_strategies(df):
    """
    Suggest strategies for handling missing data based on data analysis.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to analyze and provide suggestions for
        
    Returns:
    --------
    dict
        Dictionary containing suggested strategies for each column
    """
    console = Console()
    suggestions = {}
    
    missing_counts = df.isnull().sum()
    total_rows = len(df)
    
    console.print()
    console.print("[bold blue]💡 Missing Data Strategy Suggestions[/bold blue]")
    console.print()
    
    table = Table(title="🎯 Recommended Strategies", show_header=True, header_style="bold green")
    table.add_column("Column", style="cyan", width=20)
    table.add_column("Missing %", style="red", width=12)
    table.add_column("Data Type", style="blue", width=15)
    table.add_column("Recommended Strategy", style="green", width=35)
    
    for col in df.columns:
        if missing_counts[col] > 0:
            missing_pct = (missing_counts[col] / total_rows) * 100
            dtype = df[col].dtype
            
            # Determine strategy based on missing percentage and data type
            if missing_pct > 50:
                strategy = "🗑️ Consider dropping column (>50% missing)"
            elif pd.api.types.is_numeric_dtype(df[col]):
                if missing_pct < 5:
                    strategy = "📊 Mean/median imputation"
                elif missing_pct < 20:
                    strategy = "🔄 Interpolation or forward/backward fill"
                else:
                    strategy = "🎲 Multiple imputation (MICE)"
            elif pd.api.types.is_categorical_dtype(df[col]) or dtype == 'object':
                if missing_pct < 5:
                    strategy = "🏷️ Mode imputation"
                elif missing_pct < 20:
                    strategy = "🆕 'Unknown' category"
                else:
                    strategy = "🤖 Predictive imputation"
            else:
                strategy = "🔍 Manual review recommended"
            
            suggestions[col] = {
                'missing_percentage': missing_pct,
                'data_type': str(dtype),
                'strategy': strategy
            }
            
            table.add_row(col, f"{missing_pct:.1f}%", str(dtype), strategy)
    
    console.print(table)
    console.print()
    
    return suggestions

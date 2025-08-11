"""
Tests for the main edaflow module
"""
import pytest
import pandas as pd
import numpy as np
import edaflow
from edaflow.analysis import check_null_columns, analyze_categorical_columns, convert_to_numeric, visualize_categorical_values, display_column_types, visualize_numerical_boxplots


def test_hello_function():
    """Test the hello function returns expected message"""
    result = edaflow.hello()
    assert isinstance(result, str)
    assert "Hello from edaflow" in result
    assert "exploratory data analysis" in result


def test_version_exists():
    """Test that version is defined"""
    assert hasattr(edaflow, '__version__')
    assert isinstance(edaflow.__version__, str)


def test_author_exists():
    """Test that author information is defined"""
    assert hasattr(edaflow, '__author__')
    assert isinstance(edaflow.__author__, str)


def test_email_exists():
    """Test that email information is defined"""
    assert hasattr(edaflow, '__email__')
    assert isinstance(edaflow.__email__, str)


def test_check_null_columns_import_from_main():
    """Test check_null_columns imported from main edaflow module"""
    # Create test DataFrame
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],  # No nulls
        'B': [1, 2, None, 4, 5],  # 20% nulls
    })
    
    result = edaflow.check_null_columns(df, threshold=10)
    
    # Check that result is a styled DataFrame
    assert hasattr(result, 'data')  # Styled DataFrame has .data attribute
    
    # Check the underlying data
    data = result.data
    assert len(data) == 2  # Should have 2 rows (one per column)
    assert list(data.columns) == ['Column', 'Null_Count', 'Null_Percentage']


def test_check_null_columns_import_from_analysis():
    """Test check_null_columns imported directly from analysis module"""
    # Create test DataFrame
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],  # No nulls
        'B': [1, 2, None, 4, 5],  # 20% nulls
        'C': [None, None, None, None, None],  # 100% nulls
        'D': [1, None, 3, None, 5]  # 40% nulls
    })
    
    result = check_null_columns(df, threshold=10)
    
    # Check that result is a styled DataFrame
    assert hasattr(result, 'data')  # Styled DataFrame has .data attribute
    
    # Check the underlying data
    data = result.data
    assert len(data) == 4  # Should have 4 rows (one per column)
    assert list(data.columns) == ['Column', 'Null_Count', 'Null_Percentage']
    
    # Check null percentages
    expected_percentages = [0.0, 20.0, 100.0, 40.0]
    actual_percentages = data['Null_Percentage'].tolist()
    assert actual_percentages == expected_percentages


def test_check_null_columns_custom_threshold():
    """Test check_null_columns with custom threshold"""
    df = pd.DataFrame({
        'A': [1, 2, None, 4, 5],  # 20% nulls
        'B': [1, 2, 3, 4, 5]  # 0% nulls
    })
    
    result = check_null_columns(df, threshold=25)
    data = result.data
    
    assert data['Null_Percentage'].tolist() == [20.0, 0.0]


def test_check_null_columns_no_nulls():
    """Test check_null_columns with DataFrame containing no nulls"""
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['a', 'b', 'c'],
        'C': [1.1, 2.2, 3.3]
    })
    
    result = check_null_columns(df)
    data = result.data
    
    assert all(data['Null_Percentage'] == 0.0)
    assert all(data['Null_Count'] == 0)


def test_analyze_categorical_columns_import():
    """Test that analyze_categorical_columns can be imported"""
    from edaflow import analyze_categorical_columns
    assert callable(analyze_categorical_columns)


def test_analyze_categorical_columns_mixed_data(capsys):
    """Test analyze_categorical_columns with mixed data types"""
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],  # Truly categorical
        'age_str': ['25', '30', '35'],        # Numeric stored as string
        'mixed': ['1', '2', 'three'],         # Mixed numeric/text (33% non-numeric)
        'numbers': [1, 2, 3],                 # Already numeric
        'categories': ['A', 'B', 'A']         # Categorical
    })
    
    # Import and test the function
    from edaflow import analyze_categorical_columns
    
    # Call the function (it prints to stdout)
    analyze_categorical_columns(df, threshold=35)
    
    # Capture the printed output
    captured = capsys.readouterr()
    output = captured.out
    
    # Check that it identifies potentially numeric columns in the new format
    assert 'age_str' in output and '0.0%' in output  # age_str should be 0% non-numeric
    assert 'numbers   int64' in output  # numbers should be in non-object section
    # Mixed should be flagged as potentially numeric since 33% < 35% threshold
    assert 'mixed' in output and '33.3%' in output  # mixed should show 33.3% non-numeric
    # Name and categories should be in categorical columns section
    assert 'name' in output and '100.0%' in output  # name should be 100% non-numeric
    assert 'categories' in output and '100.0%' in output  # categories should be 100% non-numeric


def test_analyze_categorical_columns_all_numeric_strings(capsys):
    """Test analyze_categorical_columns with all numeric strings"""
    df = pd.DataFrame({
        'numeric_col': ['10', '20', '30', '40', '50']
    })
    
    from edaflow import analyze_categorical_columns
    analyze_categorical_columns(df, threshold=35)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should identify this as potentially numeric in the new format
    assert 'numeric_col' in output and '0.0%' in output  # Should show 0% non-numeric
    assert "'10', '20', '30', '40', '50'" in output or "10', '20', '30'" in output  # Sample values should be shown


def test_analyze_categorical_columns_all_text(capsys):
    """Test analyze_categorical_columns with all text data"""
    df = pd.DataFrame({
        'text_col': ['apple', 'banana', 'cherry', 'date', 'elderberry']
    })
    
    from edaflow import analyze_categorical_columns
    analyze_categorical_columns(df, threshold=35)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should identify this as truly categorical in the new format
    assert 'text_col' in output and '100.0%' in output  # Should show 100% non-numeric in categorical section


def test_convert_to_numeric_import():
    """Test that convert_to_numeric can be imported"""
    from edaflow import convert_to_numeric
    assert callable(convert_to_numeric)


def test_convert_to_numeric_basic_conversion(capsys):
    """Test convert_to_numeric with basic string-to-numeric conversion"""
    df = pd.DataFrame({
        'numeric_str': ['10', '20', '30', '40', '50'],  # Should convert (0% non-numeric)
        'mixed': ['1', '2', 'text', '4', '5'],          # Should convert (20% < 35% threshold)
        'text_col': ['apple', 'banana', 'cherry', 'date', 'elderberry'],  # Should not convert (100% non-numeric)
        'already_numeric': [1, 2, 3, 4, 5]             # Already numeric
    })
    
    # Test with default threshold (35%)
    result_df = edaflow.convert_to_numeric(df, threshold=35)
    
    # Capture printed output
    captured = capsys.readouterr()
    output = captured.out
    
    # Check that the right columns were converted in the new format
    assert 'numeric_str' in output and '✅ CONVERTED' in output  # numeric_str should be converted
    assert 'mixed' in output and '✅ CONVERTED' in output  # mixed should also convert since 20% < 35%
    assert 'text_col' in output and '⚠️ SKIPPED' in output  # text_col should be skipped
    assert 'already_numeric' in output and '✅ GOOD' in output  # already numeric should show as good
    
    # Check that the DataFrame was properly modified
    assert result_df['numeric_str'].dtype in ['int64', 'float64']
    assert result_df['mixed'].dtype in ['int64', 'float64']  # Should be converted
    assert result_df['text_col'].dtype == 'object'  # Should remain object
    assert result_df['already_numeric'].dtype in ['int64', 'float64']
    
    # Check that original DataFrame is unchanged
    assert df['numeric_str'].dtype == 'object'
    assert df['mixed'].dtype == 'object'


def test_convert_to_numeric_inplace(capsys):
    """Test convert_to_numeric with inplace=True"""
    df = pd.DataFrame({
        'price': ['100', '200', '300'],
        'category': ['A', 'B', 'C']
    })
    
    original_id = id(df)
    
    # Test inplace conversion
    result = edaflow.convert_to_numeric(df, threshold=35, inplace=True)
    
    # Should return None when inplace=True
    assert result is None
    
    # Original DataFrame should be modified
    assert id(df) == original_id  # Same object
    assert df['price'].dtype in ['int64', 'float64']  # Should be converted
    assert df['category'].dtype == 'object'  # Should remain object


def test_convert_to_numeric_with_nans():
    """Test convert_to_numeric handles conversion to NaN correctly"""
    df = pd.DataFrame({
        'mixed_col': ['10', '20', 'invalid', '40'],  # 25% non-numeric
    })
    
    result_df = edaflow.convert_to_numeric(df, threshold=30)
    
    # Should convert since 25% < 30%
    assert result_df['mixed_col'].dtype in ['int64', 'float64']
    
    # Should have 1 NaN value where 'invalid' was
    assert result_df['mixed_col'].isnull().sum() == 1
    assert result_df['mixed_col'].notna().sum() == 3
    
    # Values that could be converted should be numeric
    numeric_values = result_df['mixed_col'].dropna().tolist()
    expected_values = [10.0, 20.0, 40.0]  # Will be float due to NaN presence
    assert numeric_values == expected_values


def test_convert_to_numeric_custom_threshold(capsys):
    """Test convert_to_numeric with custom threshold"""
    df = pd.DataFrame({
        'col1': ['1', '2', 'text1', 'text2'],  # 50% non-numeric
        'col2': ['10', '20', '30', '40']       # 0% non-numeric
    })
    
    # Test with strict threshold (40%)
    result_df = edaflow.convert_to_numeric(df, threshold=40)
    captured = capsys.readouterr()
    output = captured.out
    
    # col1 should be skipped (50% > 40%), col2 should be converted in new format
    assert 'col1' in output and '⚠️ SKIPPED' in output and '50.0%' in output  # col1 skipped due to threshold
    assert 'col2' in output and '✅ CONVERTED' in output  # col2 should be converted
    
    assert result_df['col1'].dtype == 'object'
    assert result_df['col2'].dtype in ['int64', 'float64']


def test_convert_to_numeric_no_conversions(capsys):
    """Test convert_to_numeric when no conversions are possible"""
    df = pd.DataFrame({
        'text_only': ['apple', 'banana', 'cherry'],
        'already_int': [1, 2, 3],
        'already_float': [1.1, 2.2, 3.3]
    })
    
    result_df = edaflow.convert_to_numeric(df, threshold=35)
    captured = capsys.readouterr()
    output = captured.out
    
    # Should indicate no conversions were made in the new format
    assert 'ℹ️ No Conversions Made' in output or 'Successfully Converted: 0' in output
    
    # DataFrame should be unchanged in terms of data types
    assert result_df['text_only'].dtype == 'object'
    assert result_df['already_int'].dtype in ['int64', 'float64']
    assert result_df['already_float'].dtype in ['int64', 'float64']


def test_visualize_categorical_values_import():
    """Test that visualize_categorical_values can be imported"""
    from edaflow import visualize_categorical_values
    assert callable(visualize_categorical_values)


def test_visualize_categorical_values_basic(capsys):
    """Test visualize_categorical_values with basic categorical data"""
    df = pd.DataFrame({
        'category': ['A', 'B', 'A', 'C', 'B', 'A'],
        'status': ['active', 'inactive', 'active', 'pending', 'active', 'active'],
        'numeric_col': [1, 2, 3, 4, 5, 6]  # Should be ignored
    })
    
    # Test the function
    edaflow.visualize_categorical_values(df)
    
    # Capture printed output
    captured = capsys.readouterr()
    output = captured.out
    
    # Check that it found the right columns
    assert 'Found 2 categorical column(s): category, status' in output
    assert 'Column: category' in output
    assert 'Column: status' in output
    
    # Check that it shows values and counts
    assert "'A'" in output  # Category A
    assert "'B'" in output  # Category B
    assert "'active'" in output  # Status active
    assert 'Count:' in output  # Should show counts by default
    assert 'Most frequent:' in output  # Should show most frequent value


def test_visualize_categorical_values_no_categorical_columns(capsys):
    """Test visualize_categorical_values with no categorical columns"""
    df = pd.DataFrame({
        'numbers': [1, 2, 3, 4, 5],
        'floats': [1.1, 2.2, 3.3, 4.4, 5.5],
        'integers': [10, 20, 30, 40, 50]
    })
    
    edaflow.visualize_categorical_values(df)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should indicate no categorical columns found
    assert 'No categorical (object-type) columns found' in output


def test_visualize_categorical_values_with_missing(capsys):
    """Test visualize_categorical_values with missing values"""
    df = pd.DataFrame({
        'category_with_nulls': ['A', 'B', None, 'A', None, 'B'],
        'complete_category': ['X', 'Y', 'X', 'Y', 'X', 'Y']
    })
    
    edaflow.visualize_categorical_values(df)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should handle missing values
    assert 'Missing: 2' in output  # category_with_nulls has 2 NaN
    assert 'Missing: 0' in output  # complete_category has 0 NaN
    assert 'NaN/Missing' in output  # Should show NaN values


def test_visualize_categorical_values_high_cardinality(capsys):
    """Test visualize_categorical_values with high cardinality column"""
    # Create a column with many unique values
    df = pd.DataFrame({
        'high_cardinality': [f'value_{i}' for i in range(25)],  # 25 unique values
        'normal_category': ['A'] * 10 + ['B'] * 10 + ['C'] * 5
    })
    
    # Test with max_unique_values=10
    edaflow.visualize_categorical_values(df, max_unique_values=10)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should truncate high cardinality column
    assert 'Showing top 10 most frequent values (out of 25 total)' in output
    assert '... and 15 more unique value(s)' in output
    
    # Should provide insights about high cardinality
    assert 'High cardinality columns detected: high_cardinality' in output


def test_visualize_categorical_values_custom_options(capsys):
    """Test visualize_categorical_values with custom options"""
    df = pd.DataFrame({
        'category': ['A', 'B', 'A', 'C'],
        'status': ['active', 'inactive', 'active', 'pending']
    })
    
    # Test with counts but no percentages
    edaflow.visualize_categorical_values(df, show_percentages=False, show_counts=True)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should show counts but not percentages
    assert 'Count:' in output
    assert '(50.0%)' not in output and '(25.0%)' not in output  # No percentages


def test_visualize_categorical_values_mostly_unique(capsys):
    """Test visualize_categorical_values with mostly unique column"""
    # Create a column where most values are unique (like IDs)
    df = pd.DataFrame({
        'mostly_unique': [f'id_{i}' for i in range(20)] + ['duplicate'] * 2,  # 20/22 are unique (>80%)
        'normal_category': ['A'] * 11 + ['B'] * 11
    })
    
    edaflow.visualize_categorical_values(df)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should detect mostly unique columns
    assert 'Mostly unique columns (>80% unique): mostly_unique' in output
    assert 'These might be IDs or need special handling' in output


# Tests for display_column_types function

def test_display_column_types_basic():
    """Test display_column_types with mixed data types"""
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['NYC', 'LA', 'Chicago'],
        'salary': [50000, 60000, 70000],
        'is_active': [True, False, True]
    })
    
    result = display_column_types(df)
    
    # Check return type
    assert isinstance(result, dict)
    assert 'categorical' in result
    assert 'numerical' in result
    
    # Check categorical columns (object dtype)
    assert 'name' in result['categorical']
    assert 'city' in result['categorical']
    assert len(result['categorical']) == 2
    
    # Check numerical columns (non-object dtype)
    assert 'age' in result['numerical']
    assert 'salary' in result['numerical']
    assert 'is_active' in result['numerical']
    assert len(result['numerical']) == 3


def test_display_column_types_only_categorical():
    """Test display_column_types with only categorical columns"""
    df = pd.DataFrame({
        'category1': ['A', 'B', 'C'],
        'category2': ['X', 'Y', 'Z'],
        'category3': ['P', 'Q', 'R']
    })
    
    result = display_column_types(df)
    
    assert len(result['categorical']) == 3
    assert len(result['numerical']) == 0
    assert all(col in result['categorical'] for col in ['category1', 'category2', 'category3'])


def test_display_column_types_only_numerical():
    """Test display_column_types with only numerical columns"""
    df = pd.DataFrame({
        'int_col': [1, 2, 3],
        'float_col': [1.1, 2.2, 3.3],
        'bool_col': [True, False, True]
    })
    
    result = display_column_types(df)
    
    assert len(result['categorical']) == 0
    assert len(result['numerical']) == 3
    assert all(col in result['numerical'] for col in ['int_col', 'float_col', 'bool_col'])


def test_display_column_types_empty_dataframe():
    """Test display_column_types with empty DataFrame"""
    df = pd.DataFrame()
    
    result = display_column_types(df)
    
    assert result['categorical'] == []
    assert result['numerical'] == []


def test_display_column_types_invalid_input():
    """Test display_column_types with invalid input"""
    try:
        display_column_types("not a dataframe")
        assert False, "Should raise TypeError"
    except TypeError as e:
        assert "Input must be a pandas DataFrame" in str(e)


def test_display_column_types_import_from_main():
    """Test display_column_types imported from main edaflow module"""
    df = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [25, 30]
    })
    
    result = edaflow.display_column_types(df)
    
    assert isinstance(result, dict)
    assert 'categorical' in result
    assert 'numerical' in result
    assert 'name' in result['categorical']
    assert 'age' in result['numerical']


def test_display_column_types_output_format(capsys):
    """Test display_column_types output format"""
    df = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [25, 30],
        'city': ['NYC', 'LA']
    })
    
    result = display_column_types(df)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Check for key output elements in the new format
    assert '📊 COLUMN TYPE CLASSIFICATION' in output or 'Column Analysis Summary' in output
    assert 'CATEGORICAL COLUMNS' in output or 'Categorical columns' in output
    assert 'NUMERICAL COLUMNS' in output or 'Numerical columns' in output
    assert 'Summary:' in output or 'Dataset Composition:' in output
    assert 'Total' in output and '3' in output  # Should mention total of 3 columns


# =============================================================================
# Tests for impute_numerical_median function
# =============================================================================

def test_impute_numerical_median_import():
    """Test that impute_numerical_median can be imported from main package"""
    from edaflow import impute_numerical_median
    assert callable(impute_numerical_median)


def test_impute_numerical_median_basic():
    """Test basic numerical imputation with median"""
    from edaflow.analysis.core import impute_numerical_median
    
    df = pd.DataFrame({
        'age': [25, None, 35, None, 45],
        'salary': [50000, 60000, None, 70000, None],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
    })
    
    result = impute_numerical_median(df)
    
    # Check that numerical columns are imputed
    assert result['age'].isnull().sum() == 0
    assert result['salary'].isnull().sum() == 0
    
    # Check median values (age median: 35, salary median: 60000)
    assert result['age'].tolist() == [25, 35, 35, 35, 45]
    assert result['salary'].tolist() == [50000, 60000, 60000, 70000, 60000]
    
    # Check that categorical column is unchanged
    assert result['name'].equals(df['name'])


def test_impute_numerical_median_inplace():
    """Test inplace imputation"""
    from edaflow.analysis.core import impute_numerical_median
    
    df = pd.DataFrame({
        'age': [20, None, 40],
        'score': [80, 90, None]
    })
    
    original_id = id(df)
    result = impute_numerical_median(df, inplace=True)
    
    # Check that function returns None for inplace operation
    assert result is None
    
    # Check that original dataframe is modified
    assert id(df) == original_id
    assert df['age'].isnull().sum() == 0
    assert df['score'].isnull().sum() == 0


def test_impute_numerical_median_specific_columns():
    """Test imputation of specific columns only"""
    from edaflow.analysis.core import impute_numerical_median
    
    df = pd.DataFrame({
        'age': [25, None, 35],
        'salary': [50000, None, 70000],
        'score': [80, None, 90]
    })
    
    result = impute_numerical_median(df, columns=['age', 'score'])
    
    # Check that specified columns are imputed
    assert result['age'].isnull().sum() == 0
    assert result['score'].isnull().sum() == 0
    
    # Check that non-specified column still has missing values
    assert result['salary'].isnull().sum() == 1


def test_impute_numerical_median_no_missing():
    """Test with DataFrame that has no missing values"""
    from edaflow.analysis.core import impute_numerical_median
    
    df = pd.DataFrame({
        'age': [25, 30, 35],
        'salary': [50000, 60000, 70000]
    })
    
    result = impute_numerical_median(df)
    
    # Should return identical DataFrame
    pd.testing.assert_frame_equal(result, df)


def test_impute_numerical_median_all_missing():
    """Test with column that has all missing values"""
    from edaflow.analysis.core import impute_numerical_median
    
    df = pd.DataFrame({
        'age': [25, 30, 35],
        'empty_col': [None, None, None]
    })
    
    result = impute_numerical_median(df)
    
    # Age should be unchanged, empty_col should remain all NaN
    assert result['age'].equals(df['age'])
    assert result['empty_col'].isnull().all()


def test_impute_numerical_median_empty_dataframe():
    """Test with empty DataFrame"""
    from edaflow.analysis.core import impute_numerical_median
    
    df = pd.DataFrame()
    result = impute_numerical_median(df)
    
    assert result.empty


def test_impute_numerical_median_invalid_input():
    """Test with invalid input"""
    from edaflow.analysis.core import impute_numerical_median
    
    with pytest.raises(ValueError, match="Input must be a pandas DataFrame"):
        impute_numerical_median("not a dataframe")


def test_impute_numerical_median_invalid_columns():
    """Test with invalid column specifications"""
    from edaflow.analysis.core import impute_numerical_median
    
    df = pd.DataFrame({
        'age': [25, None, 35],
        'name': ['Alice', 'Bob', 'Charlie']
    })
    
    # Test non-existent column
    with pytest.raises(ValueError, match="Columns not found"):
        impute_numerical_median(df, columns=['nonexistent'])
    
    # Test non-numerical column
    with pytest.raises(ValueError, match="Non-numerical columns"):
        impute_numerical_median(df, columns=['name'])


# =============================================================================
# Tests for impute_categorical_mode function
# =============================================================================

def test_impute_categorical_mode_import():
    """Test that impute_categorical_mode can be imported from main package"""
    from edaflow import impute_categorical_mode
    assert callable(impute_categorical_mode)


def test_impute_categorical_mode_basic():
    """Test basic categorical imputation with mode"""
    from edaflow.analysis.core import impute_categorical_mode
    
    df = pd.DataFrame({
        'category': ['A', 'B', 'A', None, 'A'],
        'status': ['Active', None, 'Active', 'Inactive', None],
        'age': [25, 30, 35, 40, 45]
    })
    
    result = impute_categorical_mode(df)
    
    # Check that categorical columns are imputed
    assert result['category'].isnull().sum() == 0
    assert result['status'].isnull().sum() == 0
    
    # Check mode values (category mode: 'A', status mode: 'Active')
    assert result['category'].tolist() == ['A', 'B', 'A', 'A', 'A']
    assert result['status'].tolist() == ['Active', 'Active', 'Active', 'Inactive', 'Active']
    
    # Check that numerical column is unchanged
    assert result['age'].equals(df['age'])


def test_impute_categorical_mode_inplace():
    """Test inplace imputation"""
    from edaflow.analysis.core import impute_categorical_mode
    
    df = pd.DataFrame({
        'category': ['X', None, 'X'],
        'status': ['Yes', 'No', None]
    })
    
    original_id = id(df)
    result = impute_categorical_mode(df, inplace=True)
    
    # Check that function returns None for inplace operation
    assert result is None
    
    # Check that original dataframe is modified
    assert id(df) == original_id
    assert df['category'].isnull().sum() == 0
    assert df['status'].isnull().sum() == 0


def test_impute_categorical_mode_specific_columns():
    """Test imputation of specific columns only"""
    from edaflow.analysis.core import impute_categorical_mode
    
    df = pd.DataFrame({
        'category': ['A', None, 'A'],
        'status': ['Yes', None, 'Yes'],
        'type': ['X', None, 'Y']
    })
    
    result = impute_categorical_mode(df, columns=['category', 'type'])
    
    # Check that specified columns are imputed
    assert result['category'].isnull().sum() == 0
    assert result['type'].isnull().sum() == 0
    
    # Check that non-specified column still has missing values
    assert result['status'].isnull().sum() == 1


def test_impute_categorical_mode_no_missing():
    """Test with DataFrame that has no missing values"""
    from edaflow.analysis.core import impute_categorical_mode
    
    df = pd.DataFrame({
        'category': ['A', 'B', 'C'],
        'status': ['Active', 'Inactive', 'Pending']
    })
    
    result = impute_categorical_mode(df)
    
    # Should return identical DataFrame
    pd.testing.assert_frame_equal(result, df)


def test_impute_categorical_mode_all_missing():
    """Test with column that has all missing values"""
    from edaflow.analysis.core import impute_categorical_mode
    
    df = pd.DataFrame({
        'category': ['A', 'B', 'C'],
        'empty_col': [None, None, None]
    })
    
    result = impute_categorical_mode(df)
    
    # Category should be unchanged, empty_col should remain all NaN
    assert result['category'].equals(df['category'])
    assert result['empty_col'].isnull().all()


def test_impute_categorical_mode_mode_ties():
    """Test with mode ties (multiple values with same frequency)"""
    from edaflow.analysis.core import impute_categorical_mode
    
    df = pd.DataFrame({
        'category': ['A', 'B', 'A', 'B', None]  # A and B both appear twice
    })
    
    result = impute_categorical_mode(df)
    
    # Should pick one of the tied values ('A' or 'B')
    assert result['category'].isnull().sum() == 0
    assert result['category'].iloc[-1] in ['A', 'B']


def test_impute_categorical_mode_empty_dataframe():
    """Test with empty DataFrame"""
    from edaflow.analysis.core import impute_categorical_mode
    
    df = pd.DataFrame()
    result = impute_categorical_mode(df)
    
    assert result.empty


def test_impute_categorical_mode_invalid_input():
    """Test with invalid input"""
    from edaflow.analysis.core import impute_categorical_mode
    
    with pytest.raises(ValueError, match="Input must be a pandas DataFrame"):
        impute_categorical_mode("not a dataframe")


def test_impute_categorical_mode_invalid_columns():
    """Test with invalid column specifications"""
    from edaflow.analysis.core import impute_categorical_mode
    
    df = pd.DataFrame({
        'category': ['A', None, 'B'],
        'age': [25, 30, 35]
    })
    
    # Test non-existent column
    with pytest.raises(ValueError, match="Columns not found"):
        impute_categorical_mode(df, columns=['nonexistent'])


def test_impute_categorical_mode_no_categorical_columns():
    """Test with DataFrame that has no categorical columns"""
    from edaflow.analysis.core import impute_categorical_mode
    
    df = pd.DataFrame({
        'age': [25, 30, 35],
        'salary': [50000, 60000, 70000]
    })
    
    result = impute_categorical_mode(df)
    
    # Should return identical DataFrame
    pd.testing.assert_frame_equal(result, df)


def test_impute_categorical_mode_from_main_package():
    """Test importing and using impute_categorical_mode from main package"""
    import edaflow
    
    df = pd.DataFrame({
        'category': ['A', None, 'A', 'B'],
        'status': ['Yes', 'No', None, 'Yes']
    })
    
    result = edaflow.impute_categorical_mode(df)
    
    assert result['category'].isnull().sum() == 0
    assert result['status'].isnull().sum() == 0


def test_impute_numerical_median_from_main_package():
    """Test importing and using impute_numerical_median from main package"""
    import edaflow
    
    df = pd.DataFrame({
        'age': [25, None, 35],
        'salary': [50000, None, 70000]
    })
    
    result = edaflow.impute_numerical_median(df)
    
    assert result['age'].isnull().sum() == 0
    assert result['salary'].isnull().sum() == 0


# Tests for visualize_numerical_boxplots function
def test_visualize_numerical_boxplots_import():
    """Test importing visualize_numerical_boxplots from both locations"""
    from edaflow.analysis import visualize_numerical_boxplots
    from edaflow import visualize_numerical_boxplots as main_boxplots
    
    assert visualize_numerical_boxplots is not None
    assert main_boxplots is not None
    assert visualize_numerical_boxplots == main_boxplots


def test_visualize_numerical_boxplots_basic(monkeypatch):
    """Test basic functionality of visualize_numerical_boxplots"""
    # Mock plt.show() to prevent displaying plots during testing
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda: None)
    
    df = pd.DataFrame({
        'age': [20, 25, 30, 35, 40, 100],  # Contains outlier
        'salary': [30000, 40000, 50000, 60000, 70000, 200000],  # Contains outlier
        'experience': [1, 3, 5, 7, 10, 25],
        'category': ['A', 'B', 'C', 'A', 'B', 'C']  # Non-numerical
    })
    
    # This should work without raising exceptions
    try:
        edaflow.visualize_numerical_boxplots(df)
    except Exception as e:
        pytest.fail(f"visualize_numerical_boxplots raised an exception: {e}")


def test_visualize_numerical_boxplots_custom_parameters(monkeypatch):
    """Test visualize_numerical_boxplots with custom parameters"""
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda: None)
    
    df = pd.DataFrame({
        'value1': [1, 2, 3, 4, 5, 100],
        'value2': [10, 20, 30, 40, 50, 1000],
        'value3': [5, 10, 15, 20, 25, 500]
    })
    
    # Test with custom parameters
    try:
        edaflow.visualize_numerical_boxplots(
            df, 
            rows=2, 
            cols=2, 
            title="Custom Title",
            show_skewness=False,
            orientation='vertical',
            color_palette='viridis'
        )
    except Exception as e:
        pytest.fail(f"visualize_numerical_boxplots with custom parameters raised an exception: {e}")


def test_visualize_numerical_boxplots_specific_columns(monkeypatch):
    """Test visualize_numerical_boxplots with specific columns"""
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda: None)
    
    df = pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': [10, 20, 30, 40, 50],
        'col3': [100, 200, 300, 400, 500],
        'text_col': ['A', 'B', 'C', 'D', 'E']
    })
    
    # Test with specific columns
    try:
        edaflow.visualize_numerical_boxplots(df, columns=['col1', 'col2'])
    except Exception as e:
        pytest.fail(f"visualize_numerical_boxplots with specific columns raised an exception: {e}")


def test_visualize_numerical_boxplots_invalid_orientation():
    """Test visualize_numerical_boxplots with invalid orientation"""
    df = pd.DataFrame({
        'value': [1, 2, 3, 4, 5]
    })
    
    with pytest.raises(ValueError, match="orientation must be either 'horizontal' or 'vertical'"):
        edaflow.visualize_numerical_boxplots(df, orientation='diagonal')


def test_visualize_numerical_boxplots_no_numerical_columns():
    """Test visualize_numerical_boxplots with no numerical columns"""
    df = pd.DataFrame({
        'text1': ['A', 'B', 'C'],
        'text2': ['X', 'Y', 'Z']
    })
    
    with pytest.raises(ValueError, match="No valid numerical columns found for plotting"):
        edaflow.visualize_numerical_boxplots(df)


def test_visualize_numerical_boxplots_missing_columns():
    """Test visualize_numerical_boxplots with missing columns"""
    df = pd.DataFrame({
        'value1': [1, 2, 3],
        'value2': [4, 5, 6]
    })
    
    with pytest.raises(ValueError, match="Columns not found in DataFrame"):
        edaflow.visualize_numerical_boxplots(df, columns=['value1', 'nonexistent'])


def test_visualize_numerical_boxplots_mixed_column_types(monkeypatch, capsys):
    """Test visualize_numerical_boxplots with mixed column types"""
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda: None)
    
    df = pd.DataFrame({
        'numerical': [1, 2, 3, 4, 5],
        'text': ['A', 'B', 'C', 'D', 'E']
    })
    
    # This should work and show a warning
    edaflow.visualize_numerical_boxplots(df, columns=['numerical', 'text'])
    
    # Check that warning was printed
    captured = capsys.readouterr()
    assert "Warning: Skipping non-numerical columns: ['text']" in captured.out


def test_visualize_numerical_boxplots_all_missing_values(monkeypatch, capsys):
    """Test visualize_numerical_boxplots with columns containing all missing values"""
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda: None)
    
    df = pd.DataFrame({
        'good_col': [1, 2, 3, 4, 5],
        'all_nan': [np.nan, np.nan, np.nan, np.nan, np.nan]  # Use np.nan for numerical column
    })
    
    # This should work and show a warning about the all-NaN column
    edaflow.visualize_numerical_boxplots(df)
    
    # Check that warning was printed
    captured = capsys.readouterr()
    assert "Warning: Skipping column 'all_nan' - all values are missing" in captured.out


def test_visualize_numerical_boxplots_single_column(monkeypatch):
    """Test visualize_numerical_boxplots with single column"""
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda: None)
    
    df = pd.DataFrame({
        'single_col': [1, 2, 3, 4, 5, 100]  # Contains outlier
    })
    
    try:
        edaflow.visualize_numerical_boxplots(df)
    except Exception as e:
        pytest.fail(f"visualize_numerical_boxplots with single column raised an exception: {e}")


def test_visualize_numerical_boxplots_large_dataset(monkeypatch):
    """Test visualize_numerical_boxplots with many columns"""
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda: None)
    
    # Create DataFrame with many numerical columns
    data = {}
    for i in range(10):
        data[f'col_{i}'] = [j + i for j in range(20)]
    df = pd.DataFrame(data)
    
    try:
        edaflow.visualize_numerical_boxplots(df)
    except Exception as e:
        pytest.fail(f"visualize_numerical_boxplots with large dataset raised an exception: {e}")


def test_visualize_numerical_boxplots_from_main_package(monkeypatch):
    """Test importing and using visualize_numerical_boxplots from main package"""
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda: None)
    
    import edaflow
    
    df = pd.DataFrame({
        'test_col': [1, 2, 3, 4, 5, 100]
    })
    
    try:
        edaflow.visualize_numerical_boxplots(df)
    except Exception as e:
        pytest.fail(f"visualize_numerical_boxplots from main package raised an exception: {e}")


def test_visualize_numerical_boxplots_with_custom_figsize(monkeypatch):
    """Test visualize_numerical_boxplots with custom figure size"""
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda: None)
    
    df = pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': [10, 20, 30, 40, 50]
    })
    
    try:
        edaflow.visualize_numerical_boxplots(df, figsize=(12, 8))
    except Exception as e:
        pytest.fail(f"visualize_numerical_boxplots with custom figsize raised an exception: {e}")

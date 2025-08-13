import pandas as pd
import pytest
import numpy as np
from validata import (
    check_min_length,
    check_max_length,
    check_date_format,
    check_email,
    check_numeric,
    check_numeric_range,
    check_allowed_values,
    check_disallowed_values,
    check_duplicate_rows,
    check_regex_pattern,
    check_leading_trailing_spaces,
    check_case_format,
    check_constant_column,
    check_special_characters,
    check_blank_spaces_only,
    check_non_numeric_in_numeric_column,
    check_column_names,
    check_data_type,
    check_list_of_values,
    check_all_alphabetic,
    check_all_alphanumeric,
    check_column_dependency,
    check_null_percentage
)

def test_check_min_length():
    s = pd.Series(["abc", "a", "abcd"])
    result = check_min_length(2)(s)
    assert not result["passed"]
    assert len(result["failed_rows"]) == 1

def test_check_max_length():
    s = pd.Series(["abc", "abcdef", "ab"])
    result = check_max_length(3)(s)
    assert not result["passed"]
    assert 1 in result["failed_rows"]

def test_check_date_format_valid():
    s = pd.Series(["2024-01-01", "2024-12-31"])
    result = check_date_format("%Y-%m-%d")(s)
    assert result["passed"]

def test_check_date_format_invalid():
    s = pd.Series(["2024/01/01", "not a date"])
    result = check_date_format("%Y-%m-%d")(s)
    assert not result["passed"]

def test_check_email():
    s = pd.Series(["test@example.com", "invalid-email"])
    result = check_email()(s)
    assert not result["passed"]

def test_check_numeric():
    s = pd.Series(["123", "45.6", "abc"])
    result = check_numeric()(s)
    assert not result["passed"]

def test_check_numeric_range():
    s = pd.Series([1, 5, 10])
    result = check_numeric_range(min_value=2, max_value=8)(s)
    assert not result["passed"]
    assert 0 in result["failed_rows"]

def test_check_allowed_values():
    s = pd.Series(["A", "B", "C"])
    result = check_allowed_values(["A", "B"])(s)
    assert not result["passed"]

def test_check_disallowed_values():
    s = pd.Series(["A", "X", "B"])
    result = check_disallowed_values(["X"])(s)
    assert not result["passed"]

def test_check_duplicate_rows():
    df = pd.DataFrame({"col": [1, 1, 2]})
    result = check_duplicate_rows(df)
    assert not result["passed"]

def test_check_regex_pattern():
    s = pd.Series(["abc123", "xyz!"])
    result = check_regex_pattern(r"^[a-z0-9]+$", "Alphanumeric lowercase")(s)
    assert not result["passed"]

def test_check_leading_trailing_spaces():
    s = pd.Series(["abc", " abc ", "def"])
    result = check_leading_trailing_spaces()(s)
    assert not result["passed"]

def test_check_case_format():
    s = pd.Series(["abc", "ABC"])
    result = check_case_format("lower")(s)
    assert not result["passed"]

def test_check_constant_column():
    s = pd.Series([1, 1, 1])
    result = check_constant_column()(s)
    assert not result["passed"]

def test_check_special_characters():
    s = pd.Series(["abc!", "xyz"])
    result = check_special_characters(allowed=False)(s)
    assert not result["passed"]

def test_check_blank_spaces_only():
    s = pd.Series(["   ", "abc"])
    result = check_blank_spaces_only()(s)
    assert not result["passed"]

def test_check_non_numeric_in_numeric_column():
    s = pd.Series(["123", "abc"])
    result = check_non_numeric_in_numeric_column()(s)
    assert not result["passed"]

def test_check_column_names():
    df = pd.DataFrame({"A": [1], "B": [2]})
    result = check_column_names(["A", "B", "C"])(df)
    assert not result["passed"]

def test_check_data_type():
    df = pd.DataFrame({"A": [1], "B": ["text"]})
    result = check_data_type({"A": "int64", "B": "int64"})(df)
    assert not result["passed"]

def test_check_list_of_values():
    s = pd.Series(["Red", "Blue", "Yellow"])
    result = check_list_of_values(["Red", "Blue"])(s)
    assert not result["passed"]

def test_check_all_alphabetic():
    s = pd.Series(["abc", "123"])
    result = check_all_alphabetic()(s)
    assert not result["passed"]

def test_check_all_alphanumeric():
    s = pd.Series(["abc123", "abc!", "xyz"])
    result = check_all_alphanumeric()(s)
    assert not result["passed"]

def test_check_column_dependency():
    df = pd.DataFrame({"A": [5, 10], "B": [1, 20]})
    result = check_column_dependency(df, "A", "B", lambda a, b: a <= b)
    assert not result["passed"]
    result = check_column_dependency(df, "A", "B", lambda a, b: a > b)
    assert not result["passed"]

def test_min_length_empty_series():
    s = pd.Series([])
    result = check_min_length(2)(s)
    assert result["passed"], "Empty series should pass because no violations"

def test_max_length_exact_boundary():
    s = pd.Series(["abc", "xyz"])
    result = check_max_length(3)(s)
    assert result["passed"], "Values exactly at max length should pass"

def test_date_format_mixed_valid_invalid():
    s = pd.Series(["2024-01-01", "invalid-date"])
    result = check_date_format("%Y-%m-%d")(s)
    assert not result["passed"]
    assert "invalid-date" in s[result["failed_rows"]].values

def test_email_all_valid():
    s = pd.Series(["a@b.com", "x@y.org"])
    result = check_email()(s)
    assert result["passed"]

def test_numeric_with_leading_zeros():
    s = pd.Series(["00123", "0456"])
    result = check_numeric()(s)
    assert result["passed"]

def test_numeric_range_boundary():
    s = pd.Series([5, 10])
    result = check_numeric_range(min_value=5, max_value=10)(s)
    assert result["passed"]

def test_allowed_values_case_sensitive():
    s = pd.Series(["A", "a"])
    result = check_allowed_values(["A"])(s)
    assert not result["passed"]

def test_disallowed_values_no_match():
    s = pd.Series(["A", "B"])
    result = check_disallowed_values(["X"])(s)
    assert result["passed"]

def test_duplicate_rows_empty_df():
    df = pd.DataFrame({"col": []})
    result = check_duplicate_rows(df)
    assert result["passed"]

def test_regex_pattern_no_match():
    s = pd.Series(["!!!", "@@@"])
    result = check_regex_pattern(r"^[a-zA-Z]+$", "Only alphabets")(s)
    assert not result["passed"]

def test_leading_trailing_spaces_valid():
    s = pd.Series(["abc", "def"])
    result = check_leading_trailing_spaces()(s)
    assert result["passed"]

def test_case_format_uppercase():
    s = pd.Series(["ABC", "XYZ"])
    result = check_case_format("upper")(s)
    assert result["passed"]

def test_constant_column_with_variation():
    s = pd.Series([1, 2, 3])
    result = check_constant_column()(s)
    assert result["passed"], "Non-constant column should pass"

def test_special_characters_allowed():
    s = pd.Series(["abc!", "xyz!"])
    result = check_special_characters(allowed=True)(s)
    assert result["passed"]

def test_blank_spaces_only_pass():
    s = pd.Series(["abc", "def"])
    result = check_blank_spaces_only()(s)
    assert result["passed"]

def test_non_numeric_in_numeric_column_empty():
    s = pd.Series([])
    result = check_non_numeric_in_numeric_column()(s)
    assert result["passed"]

def test_column_names_all_present():
    df = pd.DataFrame({"A": [1], "B": [2]})
    result = check_column_names(["A", "B"])(df)
    assert result["passed"]

def test_data_type_mixed_fail():
    df = pd.DataFrame({"A": [1, "two"]})
    result = check_data_type({"A": "int64"})(df)
    assert not result["passed"]

def test_list_of_values_pass():
    s = pd.Series(["Red", "Blue"])
    result = check_list_of_values(["Red", "Blue", "Yellow"])(s)
    assert result["passed"]

def test_all_alphabetic_empty():
    s = pd.Series([])
    result = check_all_alphabetic()(s)
    assert result["passed"]

def test_all_alphanumeric_mixed():
    s = pd.Series(["abc123", "abc", "123"])
    result = check_all_alphanumeric()(s)
    assert result["passed"]

def test_column_dependency_fail():
    df = pd.DataFrame({"A": [10], "B": [5]})
    result = check_column_dependency(df, "A", "B", lambda a, b: a <= b)
    assert not result["passed"]

def test_min_length_with_nulls():
    s = pd.Series(["abc", None, "de"])
    result = check_min_length(2)(s)
    assert not result["passed"]
    assert any(pd.isnull(x) or len(str(x)) < 2 for x in s[result["failed_rows"]])

def test_max_length_with_nan_values():
    s = pd.Series(["abcd", np.nan, "ef"])
    result = check_max_length(3)(s)
    assert not result["passed"]

def test_date_format_with_blank_values():
    s = pd.Series(["2024-01-01", "", None])
    result = check_date_format("%Y-%m-%d")(s)
    assert not result["passed"]

def test_email_with_subdomain():
    s = pd.Series(["user@mail.example.com"])
    result = check_email()(s)
    assert result["passed"]

def test_numeric_with_currency_symbols():
    s = pd.Series(["$100", "200"])
    result = check_numeric()(s)
    assert not result["passed"]

def test_numeric_range_negative_values():
    s = pd.Series([-5, -10, 0])
    result = check_numeric_range(min_value=-10, max_value=0)(s)
    assert result["passed"]

def test_allowed_values_with_extra_whitespace():
    s = pd.Series([" A ", "B"])
    result = check_allowed_values(["A", "B"])(s)
    assert not result["passed"]

def test_disallowed_values_with_nulls():
    s = pd.Series([None, "X"])
    result = check_disallowed_values(["X"])(s)
    assert not result["passed"]

def test_duplicate_rows_with_multiple_columns():
    df = pd.DataFrame({"col1": [1, 1], "col2": [2, 2]})
    result = check_duplicate_rows(df)
    assert not result["passed"]

def test_regex_pattern_partial_match():
    s = pd.Series(["abc123", "123"])
    result = check_regex_pattern(r"^\d+$", "Digits only")(s)
    assert not result["passed"]

def test_case_format_lowercase_fail():
    s = pd.Series(["ABC", "def"])
    result = check_case_format("lower")(s)
    assert not result["passed"]

def test_constant_column_fail():
    s = pd.Series([1, 2, 1])
    result = check_constant_column()(s)
    assert result["passed"], "Non-constant column should pass"

def test_special_characters_blocked():
    s = pd.Series(["abc!", "xyz"])
    result = check_special_characters(allowed=False)(s)
    assert not result["passed"]

def test_blank_spaces_only_fail():
    s = pd.Series([" ", "\t"])
    result = check_blank_spaces_only()(s)
    assert not result["passed"]

def test_non_numeric_in_numeric_column_mixed():
    s = pd.Series([123, "abc", 456])
    result = check_non_numeric_in_numeric_column()(s)
    assert not result["passed"]

def test_column_names_missing_column():
    df = pd.DataFrame({"A": [1]})
    result = check_column_names(["A", "B"])(df)
    assert not result["passed"]

def test_data_type_float_as_int():
    df = pd.DataFrame({"A": [1.0, 2.0]})
    result = check_data_type({"A": "float64"})(df)
    assert result["passed"]

def test_list_of_values_extra_value():
    s = pd.Series(["Green", "Purple"])
    result = check_list_of_values(["Green", "Blue"])(s)
    assert not result["passed"]

def test_all_alphabetic_fail_on_numbers():
    s = pd.Series(["abc", "123"])
    result = check_all_alphabetic()(s)
    assert not result["passed"]

def test_all_alphanumeric_fail_on_symbols():
    s = pd.Series(["abc123", "abc!"])
    result = check_all_alphanumeric()(s)
    assert not result["passed"]

def test_column_dependency_pass_equal():
    df = pd.DataFrame({"A": [10], "B": [10]})
    result = check_column_dependency(df, "A", "B", lambda a, b: a <= b)
    assert result["passed"]

def test_check_null_percentage_pass():
    s = pd.Series([1, 2, None, 4, 5])  # 20% null
    result = check_null_percentage(30)(s)
    assert result["passed"]
    assert result["null_percentage"] == 20.0
    assert result["failed_rows"] == [2]
    assert "within limit" in result["message"]

def test_check_null_percentage_fail():
    s = pd.Series([None, None, 3, 4, 5])  # 40% null
    result = check_null_percentage(30)(s)
    assert not result["passed"]
    assert result["null_percentage"] == 40.0
    assert set(result["failed_rows"]) == {0, 1}
    assert "exceeds limit" in result["message"]

def test_check_null_percentage_no_nulls():
    s = pd.Series([1, 2, 3, 4, 5])  # 0% null
    result = check_null_percentage(10)(s)
    assert result["passed"]
    assert result["null_percentage"] == 0.0
    assert result["failed_rows"] == []
    assert "within limit" in result["message"]

def test_check_null_percentage_all_nulls():
    s = pd.Series([None, None, None])  # 100% null
    result = check_null_percentage(50)(s)
    assert not result["passed"]
    assert result["null_percentage"] == 100.0
    assert set(result["failed_rows"]) == {0, 1, 2}

def test_check_null_percentage_threshold_exact_pass():
    s = pd.Series([None, 2, 3, None, 5])  # 40% null
    result = check_null_percentage(40)(s)
    assert result["passed"]  # Equal threshold should pass
    assert result["null_percentage"] == 40.0

def test_check_null_percentage_empty_series():
    s = pd.Series([])  # No rows
    result = check_null_percentage(10)(s)
    assert result["passed"]
    assert result["null_percentage"] == 0.0
    assert result["failed_rows"] == []

def test_check_null_percentage_non_numeric_nulls():
    s = pd.Series(["a", None, "b", None])  # 50% null
    result = check_null_percentage(40)(s)
    assert not result["passed"]
    assert result["null_percentage"] == 50.0
    assert set(result["failed_rows"]) == {1, 3}

def test_check_null_percentage_message_format_pass():
    s = pd.Series([1, 2, None])  # 33.33% null
    result = check_null_percentage(50)(s)
    assert "Null percentage 33.33% within limit" in result["message"]

def test_check_null_percentage_message_format_fail():
    s = pd.Series([None, None])  # 100% null
    result = check_null_percentage(50)(s)
    assert "Null percentage 100.00% exceeds limit of 50%" in result["message"]
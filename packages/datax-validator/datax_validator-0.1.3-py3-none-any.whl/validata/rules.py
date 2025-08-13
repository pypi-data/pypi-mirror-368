import pandas as pd
import re
import numpy as np
from datetime import datetime

def check_no_nulls():
    """
    Creates a validation function to check for null (missing) values in a column.

    Failure Condition:
        - Fails if one or more null values are present in the column.

    Returns:
        function: A function that accepts a pandas Series and returns:
            dict:
                {
                    "name": "No Nulls",
                    "passed": bool,                # True if no nulls, False otherwise
                    "message": str,               # Description of the result
                    "failed_rows": list[int]      # Indexes of rows where nulls were found
                }
    """
    def _check(series: pd.Series):
        failed = series[series.isnull()].index.tolist()
        return {
            "name": "No Nulls",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} null values found" if failed else "No null values",
            "failed_rows": failed
        }
    return _check

def check_null_percentage(max_null_pct):
    """
    Creates a validation function to ensure the percentage of null (missing) values 
    does not exceed a given threshold.

    Args:
        max_null_pct (float): Maximum allowed percentage of null values (0–100).

    Failure Condition:
        - Fails if the percentage of null values in the column is greater than max_null_pct.

    Returns:
        function: A function that accepts a pandas Series and returns:
            dict:
                {
                    "name": "Null Percentage <= {max_null_pct}%",
                    "passed": bool,                  # True if null % is within limit
                    "message": str,                  # Description with actual null percentage
                    "failed_rows": list[int],        # Indexes of rows with null values
                    "null_percentage": float         # Actual percentage of null values
                }
    """
    def _check(series: pd.Series):
        total = len(series)
        null_count = series.isnull().sum()
        null_percentage = (null_count / total * 100) if total > 0 else 0

        failed = series[series.isnull()].index.tolist()

        return {
            "name": f"Null Percentage <= {max_null_pct}%",
            "passed": null_percentage <= max_null_pct,
            "message": (f"Null percentage {null_percentage:.2f}% exceeds limit of {max_null_pct}%"
                        if null_percentage > max_null_pct else
                        f"Null percentage {null_percentage:.2f}% within limit"),
            "failed_rows": failed,
            "null_percentage": null_percentage
        }

    return _check



def check_unique():
    """
    Creates a validation function to ensure values in a column are unique.

    Failure Condition:
        - Fails if any duplicate values exist in the column.

    Returns:
        function: A function that accepts a pandas Series and returns:
            dict:
                {
                    "name": "Unique Values",
                    "passed": bool,                # True if all values are unique
                    "message": str,               # Count of duplicates or success message
                    "failed_rows": list[int]      # Indexes of rows with duplicate values
                }
    """
    def _check(series: pd.Series):
        duplicates = series[series.duplicated(keep=False)].index.tolist()
        return {
            "name": "Unique Values",
            "passed": len(duplicates) == 0,
            "message": f"{len(duplicates)} duplicate values" if duplicates else "All unique values",
            "failed_rows": duplicates
        }
    return _check


def check_min_max(min_val, max_val):
    """
    Creates a validation function to ensure values fall within a specified range.

    Args:
        min_val (numeric): Minimum allowed value (inclusive).
        max_val (numeric): Maximum allowed value (inclusive).

    Failure Condition:
        - Fails if any value is less than `min_val` or greater than `max_val`.

    Returns:
        function: A function that accepts a pandas Series and returns:
            dict:
                {
                    "name": "Range {min_val}-{max_val}",
                    "passed": bool,                # True if all values are in range
                    "message": str,               # Description of out-of-range values
                    "failed_rows": list[int]      # Indexes of out-of-range values
                }
    """
    def _check(series: pd.Series):
        failed = series[(series < min_val) | (series > max_val)].index.tolist()
        return {
            "name": f"Range {min_val}-{max_val}",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} out-of-range values" if failed else "All values in range",
            "failed_rows": failed
        }
    return _check


def check_positive():
    """
    Creates a validation function to ensure all values are positive.

    Failure Condition:
        - Fails if any value is less than 0.

    Returns:
        function: A function that accepts a pandas Series and returns:
            dict:
                {
                    "name": "Positive Values",
                    "passed": bool,                # True if all values are positive
                    "message": str,               # Count of negative values or success message
                    "failed_rows": list[int]      # Indexes of rows with negative values
                }
    """
    def _check(series: pd.Series):
        failed = series[series < 0].index.tolist()
        return {
            "name": "Positive Values",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} negative values" if failed else "All positive values",
            "failed_rows": failed
        }
    return _check


def check_regex(pattern):
    """
    Creates a validation function to ensure values match a given regex pattern.

    Args:
        pattern (str): Regex pattern that all values must match.

    Failure Condition:
        - Fails if any value does not match the regex pattern.

    Returns:
        function: A function that accepts a pandas Series and returns:
            dict:
                {
                    "name": "Regex Match",
                    "passed": bool,                # True if all values match the pattern
                    "message": str,               # Count of invalid values or success message
                    "failed_rows": list[int]      # Indexes of rows with invalid formats
                }
    """
    regex = re.compile(pattern)
    def _check(series: pd.Series):
        failed = series[~series.astype(str).str.match(regex)].index.tolist()
        return {
            "name": "Regex Match",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} invalid formats" if failed else "All values match regex",
            "failed_rows": failed
        }
    return _check


def check_allowed_values(allowed_values):
    """
    Creates a validation function to ensure column values are in a predefined set.

    Args:
        allowed_values (list): List of allowed values.

    Failure Condition:
        - Fails if any value is not in the allowed set.

    Returns:
        function: A function that accepts a pandas Series and returns:
            dict:
                {
                    "name": "Allowed Values",
                    "passed": bool,                # True if all values are allowed
                    "message": str,               # Count of invalid values or success message
                    "failed_rows": list[int]      # Indexes of rows with invalid values
                }
    """
    def _check(series: pd.Series):
        failed = series[~series.isin(allowed_values)].index.tolist()
        return {
            "name": "Allowed Values",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} invalid values not in {allowed_values}" if failed else "All values allowed",
            "failed_rows": failed
        }
    return _check



def check_outliers_zscore(threshold=3):
    def _check(series: pd.Series):
        numeric_series = pd.to_numeric(series, errors="coerce")

        # Drop NaNs for mean/std calculation
        valid_values = numeric_series.dropna()

        if valid_values.empty or valid_values.std() == 0:
            failed = []
        else:
            z_scores = ((numeric_series - valid_values.mean()).abs() / valid_values.std())
            failed = z_scores[z_scores > threshold].index.tolist()

        return {
            "name": f"Outlier Z-Score ({threshold})",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} outliers detected" if failed else "No outliers detected",
            "failed_rows": failed
        }

    return _check


def check_min_length(min_len):
    """
    Creates a validation function that checks if each value in a Pandas Series meets a minimum length.

    Parameters:
        min_len (int): The minimum required length for each value.

    Returns:
        function: A function that accepts a Pandas Series and returns a dict with:
            - name (str): Validation name
            - passed (bool): True if all values meet the minimum length, else False
            - message (str): Summary of validation result
            - failed_rows (list): Indices of rows that failed the check

    Fails When:
        - Any value in the series has a string length shorter than `min_len`.
    """
   
    def _check(series: pd.Series):
        # Convert to string, replace NaN/None with empty string
        lengths = series.fillna("").astype(str).str.len()
        failed = series[lengths < min_len].index.tolist()

        return {
            "name": f"Min Length {min_len}",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} values shorter than {min_len}" if failed else "All values meet minimum length",
            "failed_rows": failed
        }
    return _check

def check_max_length(max_len):
    """
    Creates a validation function that checks if each value in a Pandas Series does not exceed a maximum length.

    Parameters:
        max_len (int): The maximum allowed length for each value.

    Returns:
        function: A function that accepts a Pandas Series and returns a dict with:
            - name, passed, message, failed_rows

    Fails When:
        - Any value in the series has a string length greater than `max_len`.
    """
    def _check(series: pd.Series):
        failed = series[series.astype(str).str.len() > max_len].index.tolist()
        return {
            "name": f"Max Length {max_len}",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} values longer than {max_len}" if failed else "All values meet maximum length",
            "failed_rows": failed
        }
    return _check

def check_date_format(fmt):
    def _check(series: pd.Series):
        parsed = pd.to_datetime(series, format=fmt, errors="coerce")
        failed = parsed[parsed.isna()].index.tolist()
        return {
            "name": f"Date Format {fmt}",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} invalid dates" if failed else "All dates valid",
            "failed_rows": failed
        }
    return _check

# ✅ NEW: Email Validation Check
def check_email():
    """
    Validates if each value in a Pandas Series is in a valid email format.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value does not match the email regex pattern.
    """
    email_regex = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
    def _check(series: pd.Series):
        failed = series[~series.astype(str).str.match(email_regex)].index.tolist()
        return {
            "name": "Valid Email",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} invalid emails" if failed else "All emails valid",
            "failed_rows": failed
        }
    return _check

# ✅ NEW: Check if numeric
def check_numeric():
    """
    Validates if each value in a Pandas Series is numeric.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value is not numeric (after removing one decimal point).
    """
    def _check(series: pd.Series):
        failed = series[~series.astype(str).str.replace('.', '', 1).str.isnumeric()].index.tolist()
        return {
            "name": "Numeric Check",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} non-numeric values" if failed else "All values are numeric",
            "failed_rows": failed
        }
    return _check


def check_numeric_range(min_value=None, max_value=None):
    """
    Validates if numeric values fall within a specified range.

    Parameters:
        min_value (float|None): Minimum allowed value (optional).
        max_value (float|None): Maximum allowed value (optional).

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value is smaller than min_value or larger than max_value.
    """
    def _check(series: pd.Series):
        failed = series[
            ((min_value is not None) & (series < min_value)) |
            ((max_value is not None) & (series > max_value))
        ].index.tolist()
        return {
            "name": f"Numeric Range {min_value} - {max_value}",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} values out of range" if failed else "All values within range",
            "failed_rows": failed
        }
    return _check

def check_allowed_values(allowed_values):
    """
    Validates if each value in a Pandas Series is among the allowed values.

    Parameters:
        allowed_values (list): List of acceptable values.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value is not present in allowed_values.
    """
    def _check(series: pd.Series):
        failed = series[~series.isin(allowed_values)].index.tolist()
        return {
            "name": "Allowed Values",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} invalid values not in {allowed_values}" if failed else "All values allowed",
            "failed_rows": failed
        }
    return _check

def check_disallowed_values(disallowed_values):
    """
    Validates if none of the values in a Pandas Series are in the disallowed list.

    Parameters:
        disallowed_values (list): List of forbidden values.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value is found in disallowed_values.
    """
    def _check(series: pd.Series):
        failed = series[series.isin(disallowed_values)].index.tolist()
        return {
            "name": "Disallowed Values",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} disallowed values found" if failed else "No disallowed values",
            "failed_rows": failed
        }
    return _check

def check_duplicate_rows(df: pd.DataFrame):
    """
    Checks if there are duplicate rows in a DataFrame.

    Parameters:
        df (pd.DataFrame): The DataFrame to check.

    Returns:
        dict: A result dictionary with:
            - name, passed, message, failed_rows (row indices).

    Fails When:
        - Any duplicate rows exist in the DataFrame.
    """
    duplicate_indices = df[df.duplicated()].index.tolist()
    return {
        "name": "Duplicate Rows",
        "passed": len(duplicate_indices) == 0,
        "message": f"{len(duplicate_indices)} duplicate rows found" if duplicate_indices else "No duplicates",
        "failed_rows": duplicate_indices
    }

def check_regex_pattern(pattern, description="Regex Pattern"):
    """
    Validates if each value in a Pandas Series matches a regex pattern.

    Parameters:
        pattern (str): Regular expression.
        description (str): Name for the check (default: "Regex Pattern").

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value does not match the given regex.
    """
    regex = re.compile(pattern)
    def _check(series: pd.Series):
        failed = series[~series.astype(str).str.match(regex)].index.tolist()
        return {
            "name": description,
            "passed": len(failed) == 0,
            "message": f"{len(failed)} values failed regex match" if failed else "All values match regex",
            "failed_rows": failed
        }
    return _check

def check_leading_trailing_spaces():
    """
    Checks if any value in a Pandas Series contains leading or trailing spaces.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value starts or ends with a space.
    """
    def _check(series: pd.Series):
        failed = series[series.astype(str).str.match(r"^\s|\s$")].index.tolist()
        return {
            "name": "Leading/Trailing Spaces",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} values with leading/trailing spaces" if failed else "No extra spaces",
            "failed_rows": failed
        }
    return _check

def check_case_format(case_type="lower"):
    """
    Validates if values in a Pandas Series match a specific case format.

    Parameters:
        case_type (str): "lower", "upper", or "title".

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value does not match the specified case type.
    """
    def _check(series: pd.Series):
        failed = []
        for idx, val in series.items():
            if pd.notnull(val):
                if case_type == "lower" and str(val) != str(val).lower():
                    failed.append(idx)
                elif case_type == "upper" and str(val) != str(val).upper():
                    failed.append(idx)
                elif case_type == "title" and str(val) != str(val).title():
                    failed.append(idx)
        return {
            "name": f"Case Format ({case_type})",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} values not in {case_type} case" if failed else "All values match case format",
            "failed_rows": failed
        }
    return _check

def check_constant_column():
    """
    Checks if a column contains only one unique value.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - The column has no variability (only one unique value).
    """
    def _check(series: pd.Series):
        if series.nunique() <= 1:
            return {
                "name": "Constant Column",
                "passed": False,
                "message": "Column has constant value for all rows",
                "failed_rows": series.index.tolist()
            }
        return {
            "name": "Constant Column",
            "passed": True,
            "message": "Column has variability",
            "failed_rows": []
        }
    return _check

def check_special_characters(allowed=True):
    """
    Checks for special characters in a Pandas Series.

    Parameters:
        allowed (bool): If True, the check is skipped (special characters allowed).

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Special characters are found and allowed=False.
    """
    def _check(series: pd.Series):
        regex = r"[^\w\s]"  # Matches special chars
        if allowed:
            return {"name": "Special Characters Allowed", "passed": True, "message": "Not enforced", "failed_rows": []}
        failed = series[series.astype(str).str.contains(regex, regex=True)].index.tolist()
        return {
            "name": "No Special Characters",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} values contain special characters" if failed else "No special characters",
            "failed_rows": failed
        }
    return _check

def check_blank_spaces_only():
    """
    Checks if any value in a Pandas Series contains only blank spaces.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value is composed entirely of spaces.
    """
    def _check(series: pd.Series):
        failed = series[series.astype(str).str.match(r"^\s+$")].index.tolist()
        return {
            "name": "Blank Spaces Only",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} values contain only spaces" if failed else "No blank-only values",
            "failed_rows": failed
        }
    return _check

def check_non_numeric_in_numeric_column():
    """
    Checks for non-numeric values in a numeric column.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value contains non-numeric characters.
    """
    def _check(series: pd.Series):
        failed = series[~series.astype(str).str.match(r"^-?\d+(\.\d+)?$")].index.tolist()
        return {
            "name": "Non-Numeric in Numeric Column",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} non-numeric values found" if failed else "All values numeric",
            "failed_rows": failed
        }
    return _check

def check_column_dependency(df: pd.DataFrame, col1, col2, condition_func):
    """
    Validates a dependency between two columns using a custom condition.

    Parameters:
        df (pd.DataFrame): DataFrame to check.
        col1 (str): First column name.
        col2 (str): Second column name.
        condition_func (function): A function that takes two values and returns True if valid.

    Returns:
        dict: Validation result (name, passed, message, failed_rows).

    Fails When:
        - The condition function returns False for any row.
    """
    failed = []
    for idx, row in df.iterrows():
        try:
            if not condition_func(row[col1], row[col2]):
                failed.append(idx)
        except Exception:
            failed.append(idx)
    return {
        "name": f"Column Dependency: {col1} vs {col2}",
        "passed": len(failed) == 0,
        "message": f"{len(failed)} rows failed dependency check" if failed else "All dependencies satisfied",
        "failed_rows": failed
    }

def check_column_names(expected_columns):
    """
    Validates if DataFrame has exactly the expected column names.

    Parameters:
        expected_columns (list): List of required column names.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any required column is missing OR extra columns are found.
    """
    def _check(df: pd.DataFrame):
        missing = [col for col in expected_columns if col not in df.columns]
        extra = [col for col in df.columns if col not in expected_columns]
        return {
            "name": "Column Names",
            "passed": len(missing) == 0 and len(extra) == 0,
            "message": (
                f"Missing: {missing}, Extra: {extra}" 
                if missing or extra else "All column names match"
            ),
            "failed_rows": []  # schema-level check, not row-specific
        }
    return _check

def check_data_type(expected_types: dict):
    """
    Validates if DataFrame columns match the expected data types.

    Parameters:
        expected_types (dict): Mapping of column names to expected data types.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any column's dtype does not match the expected type.
    """
    def _check(df: pd.DataFrame):
        mismatched = {}
        for col, expected_type in expected_types.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if expected_type != actual_type:
                    mismatched[col] = {"expected": expected_type, "actual": actual_type}
        return {
            "name": "Data Types",
            "passed": len(mismatched) == 0,
            "message": f"Mismatched: {mismatched}" if mismatched else "All data types match",
            "failed_rows": []  # schema-level check
        }
    return _check

def check_list_of_values(allowed_values, case_insensitive=False):
    """
    Validates if each value in a Series belongs to a predefined list.

    Parameters:
        allowed_values (list): List of acceptable values.
        case_insensitive (bool): Whether to ignore case during validation.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value is not in allowed_values.
    """
    def _check(series: pd.Series):
        if case_insensitive:
            series_check = series.astype(str).str.lower()
            allowed = [v.lower() for v in allowed_values]
        else:
            series_check = series
            allowed = allowed_values
        failed = series[~series_check.isin(allowed)].index.tolist()
        return {
            "name": "List of Values",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} invalid values not in {allowed_values}" if failed else "All values match allowed list",
            "failed_rows": failed
        }
    return _check

def check_all_alphabetic():
    """
    Validates if all values in a Series contain only alphabetic characters.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value contains non-alphabetic characters.
    """
    def _check(series: pd.Series):
        failed = series[~series.astype(str).str.match(r"^[A-Za-z]+$")].index.tolist()
        return {
            "name": "Alphabetic Only",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} values contain non-alphabetic characters" if failed else "All values are alphabetic",
            "failed_rows": failed
        }
    return _check

def check_all_alphanumeric():
    """
    Validates if all values in a Series contain only alphanumeric characters.

    Returns:
        function: Validation function returning dict (name, passed, message, failed_rows).

    Fails When:
        - Any value contains characters other than letters and digits.
    """
    def _check(series: pd.Series):
        failed = series[~series.astype(str).str.match(r"^[A-Za-z0-9]+$")].index.tolist()
        return {
            "name": "Alphanumeric Only",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} values contain non-alphanumeric characters" if failed else "All values are alphanumeric",
            "failed_rows": failed
        }
    return _check

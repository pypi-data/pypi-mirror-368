"""
Data Quality Package

This package provides:
- Core rules (basic validations: length, format, numeric, allowed/disallowed values, etc.)
- Advanced rules (integrity, statistical, semantic, and time-series checks)

Usage:
    from validata import check_min_length, advanced_rules
    result = check_min_length(5)(df["name"])
    print(result)

    from validata.advanced_rules import check_primary_key
    result = check_primary_key(df, "id")
"""

from .rules import (
    # Core validation checks
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
    check_no_nulls,
    check_null_percentage
)

# Expose the advanced rules as a submodule
from . import advanced_rules
from .checker import DataQualityChecker

__all__ = [
    # Core rules
    "check_min_length",
    "check_max_length",
    "check_date_format",
    "check_email",
    "check_numeric",
    "check_numeric_range",
    "check_allowed_values",
    "check_disallowed_values",
    "check_duplicate_rows",
    "check_regex_pattern",
    "check_leading_trailing_spaces",
    "check_case_format",
    "check_constant_column",
    "check_special_characters",
    "check_blank_spaces_only",
    "check_non_numeric_in_numeric_column",
    "check_column_names",
    "check_data_type",
    "check_list_of_values",
    "check_all_alphabetic",
    "check_all_alphanumeric",
    "check_column_dependency",

    # Advanced rules namespace
    "advanced_rules"
]

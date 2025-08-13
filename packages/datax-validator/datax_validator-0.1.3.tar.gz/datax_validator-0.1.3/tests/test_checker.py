import pandas as pd
import pytest
from src.validata.checker import DataQualityChecker
from src.validata.rules import check_min_length, check_numeric, check_date_format, check_outliers_zscore

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "name": ["Alice", "Bo", "Charles", ""],
        "age": [25, "NaN", 40, 200],
        "dob": ["1990-01-01", "not-a-date", "1985-05-12", "2000-13-01"]
    })

def test_min_length_check(sample_df):
    rules = {
        "name": [check_min_length(3)]
    }
    checker = DataQualityChecker(sample_df)
    checker.run(rules)
    report = checker.results["name"][0]

    assert report["name"] == "Min Length 3"
    assert not report["passed"]          # Should fail for "Bo" and ""
    assert len(report["failed_rows"]) == 2

def test_numeric_check(sample_df):
    rules = {
        "age": [check_numeric()]
    }
    checker = DataQualityChecker(sample_df)
    checker.run(rules)
    report = checker.results["age"][0]

    assert report["name"] == "Numeric Check"
    assert not report["passed"]          # Should fail for "NaN" (string)
    assert len(report["failed_rows"]) == 1

def test_date_format_check(sample_df):
    rules = {
        "dob": [check_date_format("%Y-%m-%d")]
    }
    checker = DataQualityChecker(sample_df)
    checker.run(rules)
    report = checker.results["dob"][0]

    assert report["name"] == "Date Format %Y-%m-%d"
    assert not report["passed"]          # Should fail for "not-a-date" and "2000-13-01"
    assert len(report["failed_rows"]) == 2

def test_outlier_check(sample_df):
    rules = {
        "age": [check_outliers_zscore(1)]
    }
    checker = DataQualityChecker(sample_df)
    checker.run(rules)
    report = checker.results["age"][0]

    assert report["name"] == "Outlier Z-Score (1)"
    assert not report["passed"]          # 200 is an outlier
    assert len(report["failed_rows"]) == 1

def test_multiple_rules_on_same_column(sample_df):
    rules = {
        "age": [check_numeric(), check_outliers_zscore(2)]
    }
    checker = DataQualityChecker(sample_df)
    checker.run(rules)

    assert len(checker.results["age"]) == 2
    assert checker.results["age"][0]["name"] == "Numeric Check"
    assert checker.results["age"][1]["name"].startswith("Outlier Z-Score")

def test_missing_column_error(sample_df):
    rules = {
        "salary": [check_numeric()]
    }
    checker = DataQualityChecker(sample_df)

    with pytest.raises(ValueError, match="Column 'salary' not found"):
        checker.run(rules)

def test_failed_examples_are_recorded(sample_df):
    rules = {
        "dob": [check_date_format("%Y-%m-%d")]
    }
    checker = DataQualityChecker(sample_df)
    checker.run(rules)
    report = checker.results["dob"][0]

    assert "failed_examples" in report
    assert len(report["failed_examples"]) > 0
    assert "index" in report["failed_examples"][0]

def test_generate_report_string(sample_df):
    rules = {
        "name": [check_min_length(3)]
    }
    checker = DataQualityChecker(sample_df)
    checker.run(rules)
    report_str = checker.generate_report()

    assert "DATA QUALITY REPORT" in report_str
    assert "Column: name" in report_str
    assert "❌ FAIL" in report_str or "✅ PASS" in report_str

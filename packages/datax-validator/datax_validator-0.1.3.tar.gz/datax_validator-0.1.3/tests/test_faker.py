import pandas as pd
import pytest
import numpy as np
from faker import Faker
from src.validata.checker import DataQualityChecker
from src.validata.rules import (
    check_min_length,
    check_numeric,
    check_date_format,
    check_outliers_zscore

)

fake = Faker()

@pytest.fixture
def random_df():
    np.random.seed(42)

    # Generate valid and invalid names
    names = [fake.first_name() if i % 3 else "" for i in range(50)]
    ages = [np.random.randint(18, 90) if i % 5 else "NaN" for i in range(50)]
    dobs = [
        fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d") if i % 4
        else "invalid-date"
        for i in range(50)
    ]
    return pd.DataFrame({
        "name": names,
        "age": ages,
        "dob": dobs
    })

def test_random_min_length(random_df):
    rules = {"name": [check_min_length(3)]}
    checker = DataQualityChecker(random_df)
    checker.run(rules)
    result = checker.results["name"][0]
    assert isinstance(result["failed_rows"], list)
    assert "Min Length 3" in result["name"]

def test_random_numeric_check(random_df):
    rules = {"age": [check_numeric()]}
    checker = DataQualityChecker(random_df)
    checker.run(rules)
    result = checker.results["age"][0]
    assert isinstance(result["failed_rows"], list)
    assert result["name"] == "Numeric Check"

def test_random_date_format(random_df):
    rules = {"dob": [check_date_format("%Y-%m-%d")]}
    checker = DataQualityChecker(random_df)
    checker.run(rules)
    result = checker.results["dob"][0]
    assert isinstance(result["failed_rows"], list)
    assert "Date Format" in result["name"]

def test_random_outliers_zscore(random_df):
    rules = {"age": [check_outliers_zscore(2)]}
    checker = DataQualityChecker(random_df)
    checker.run(rules)
    result = checker.results["age"][0]
    assert "Outlier Z-Score" in result["name"]

@pytest.mark.parametrize("iteration", range(5))
def test_fuzz_quality_checker(iteration):
    df = pd.DataFrame({
        "name": [fake.first_name() if i % 4 else "" for i in range(30)],
        "age": [np.random.randint(18, 90) if i % 3 else "NaN" for i in range(30)],
        "dob": [fake.date_of_birth().strftime("%Y-%m-%d") if i % 5 else "bad-date" for i in range(30)]
    })

    rules = {
        "name": [check_min_length(2)],
        "age": [check_numeric(), check_outliers_zscore(2)],
        "dob": [check_date_format("%Y-%m-%d")]
    }

    checker = DataQualityChecker(df)
    results = checker.run(rules)

    for col, checks in results.items():
        for res in checks:
            assert "name" in res
            assert "passed" in res
            assert "failed_rows" in res



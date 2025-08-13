# Validata: A tool for data quality checks
A Python package to validate data quality for pandas DataFrames with flexible, configurable rules.

---

## Features
- Validate columns for numeric, date, string length, and outlier checks  
- Automatically generate a **data quality report** with examples of failures  
- Export results to CSV  
- Plug-and-play rule configuration for each column  
- Support for custom rules  
- Includes **fuzz testing with Faker** for robust testing 

## Rules
- check for null (missing) values in a column
- ensure the percentage of null (missing) values does not exceed a given threshold
- ensure values in a column are unique
- ensure values fall within a specified range
- ensure all values are positive
- ensure values match a given regex pattern
- ensure column values are in a predefined set
- ensure each value meets a minimum length
- ensure each value does not exceed a maximum length
- ensure valid email format
- ensure that each value is numeric
- ensure that value is among the specified values.
- ensure that none of the values are in the disallowed list.
- check if there are duplicate rows in the dataframe
- check if any value contains leading or trailing spaces
- check if values match a specific case format
- check if a column contain only one unique value
- check if values contain any special characters
- check if a value contains only blank spaces
- check for non-numeric values in a numeric column
- Validates a dependency between two columns using a custom condition
- check if DataFrame has exactly the expected column names
- validate if columns match the expected data types.
- validate if all values are alphabetic
- validate if column values contain only alphanumeric characters


---

## Installation
   Clone this repository:
   ```bash
   git clone https://github.com/your-username/validata.git
   cd validata
   ```
## Install dependencies:

  ```bash
  pip install -r requirements.txt

  (Optional) Install the package locally in editable mode:

  pip install -e .
  ```
## Project Structure
```bash
validata/
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── README.md
├── src/
│   └── validata/
│       ├── __init__.py
│       ├── checker.py
│       └── rules.py
└── tests/
    ├── test_checker.py
    ├── test_rules.py
    └── test_faker.py
```


# Usage

## Import the package 
```bash
import pandas as pd
from src.validata.checker import DataQualityChecker
from src.validata.rules import check_min_length, check_numeric, check_date_format, check_outliers_zscore
```


## Prepare your dataframe
```bash
df = pd.DataFrame({
    "name": ["Alice", "Bo", "Charles", ""],
    "age": [25, "NaN", 40, 200],
    "dob": ["1990-01-01", "not-a-date", "1985-05-12", "2000-13-01"]
})
```

## Define rules
```bash
rules = {
    "name": [check_min_length(3)],
    "age": [check_numeric(), check_outliers_zscore(2)],
    "dob": [check_date_format("%Y-%m-%d")]
}
```
## Run the Checker
```bash
checker = DataQualityChecker(df)
results = checker.run(rules)

print(results)
```


## Generate a Report 
```bash
print(checker.generate_report())
```

# Example Report 
```
=== DATA QUALITY REPORT ===

Column: name
  - Min Length (3): FAIL | 2 values shorter than 3
    Examples of failures:
      Row 1: name = Bo
      Row 3: name = 

Column: age
  - Numeric Check: FAIL | 1 non-numeric value
    Examples of failures:
      Row 1: age = NaN
  - Outlier Z-Score (2): FAIL | 1 outlier detected
    Examples of failures:
      Row 3: age = 200

Column: dob
  - Date Format (%Y-%m-%d): FAIL | 2 invalid dates
    Examples of failures:
      Row 1: dob = not-a-date
      Row 3: dob = 2000-13-01
```
## checker.export_report("validata_report.csv")
```bash
checker.export_report("validata_report.csv")
```

# Testing

Run the full test suite
```bash
pytest -v
```

Run only rule test
```bash
pytest tests/test_rules.py -v or python -m pytest tests/test_rules.py -v


pytest tests/test_faker.py -v or python -m pytest tests/test_faker.py
```


# Advanced Usage


Add a custom rule
You can easily define a custom rule:
```bash
def check_no_nulls():
    def _check(series):
        failed = series[series.isnull()].index.tolist()
        return {
            "name": "No Nulls",
            "passed": len(failed) == 0,
            "message": f"{len(failed)} null values" if failed else "No nulls found",
            "failed_rows": failed
        }
    return _check

rules = {
    "name": [check_no_nulls()]
}
```
# Development
Update dependencies in requirements.txt.

Add new rules in src/validata/rules.py.

Add tests in tests/.

Update README.md with new features.


Quick Start: ETL Pipeline Integration:

You can easily integrate DataqualityChecker into an ETL (Extract-Transform-Load) pipeline:
```bash
import pandas as pd
from src.validata.checker import DataQualityChecker
from src.validata.rules import check_min_length, check_numeric, check_date_format

def extract_data():
    # Example: Load from CSV
    return pd.read_csv("data/raw/customers.csv")

def transform_data(df):
    # Example: Clean column names and trim spaces
    df.columns = [c.strip().lower() for c in df.columns]
    return df

def validate_data(df):
    rules = {
        "name": [check_min_length(3)],
        "age": [check_numeric()],
        "dob": [check_date_format("%Y-%m-%d")]
    }

    checker = DataQualityChecker(df)
    checker.run(rules)

    print(checker.generate_report())

    # If any check fails, raise an error to stop the pipeline
    if any(not r["passed"] for results in checker.results.values() for r in results):
        raise ValueError("Data quality checks failed. See report above.")

    return df

def load_data(df):
    # Example: Save to processed folder
    df.to_csv("data/processed/customers_clean.csv", index=False)

if __name__ == "__main__":
    df = extract_data()
    df = transform_data(df)
    df = validate_data(df)
    load_data(df)

```
This structure allows:

Automatic validation before loading data

Integration with CI/CD pipelines

Failing fast if data quality issues are detected



# Bad Data Example:
```bash
df = pd.DataFrame({
    "name": ["", "A", None],
    "age": ["NaN", "invalid", 9999],
    "dob": ["31-12-2020", "bad-date", None]
})

rules = {
    "name": [check_min_length(3)],
    "age": [check_numeric(), check_outliers_zscore(2)],
    "dob": [check_date_format("%Y-%m-%d")]
}

checker = DataQualityChecker(df)
checker.run(rules)
print(checker.generate_report())

if any(not r["passed"] for results in checker.results.values() for r in results):
    raise ValueError("Data quality validation failed.")

```
Output

=== DATA QUALITY REPORT ===

Column: name
  - Min Length (3): FAIL | 3 values shorter than 3
    Examples of failures:
      Row 0: name =
      Row 1: name = A
      Row 2: name = None

Column: age
  - Numeric Check: FAIL | 2 non-numeric values
    Examples of failures:
      Row 0: age = NaN
      Row 1: age = invalid
  - Outlier Z-Score (2): FAIL | 1 outlier detected
    Examples of failures:
      Row 2: age = 9999

Column: dob
  - Date Format (%Y-%m-%d): FAIL | 3 invalid dates
    Examples of failures:
      Row 0: dob = 31-12-2020
      Row 1: dob = bad-date
      Row 2: dob = None

ETL pipeline terminated due to data quality errors.



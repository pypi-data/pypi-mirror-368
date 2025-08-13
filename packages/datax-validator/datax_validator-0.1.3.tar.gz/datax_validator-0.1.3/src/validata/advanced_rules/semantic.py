import pandas as pd

def check_column_dependency(df: pd.DataFrame, col1, col2, condition_func):
    """
    Check if a dependency between two columns holds true.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the columns.
    col1 : str
        First column name.
    col2 : str
        Second column name.
    condition_func : callable
        Function taking (val1, val2) and returning True if condition is satisfied.

    Returns
    -------
    dict
        {
            "name": "Column Dependency",
            "passed": bool,
            "message": str,
            "failed_rows": list of indices
        }

    Fails When
    ----------
    - Any row violates the condition function.
    """
    failed = [idx for idx, row in df.iterrows() if not condition_func(row[col1], row[col2])]
    return {
        "name": f"Column Dependency: {col1} vs {col2}",
        "passed": len(failed) == 0,
        "message": f"{len(failed)} dependency violations" if failed else "All dependencies satisfied",
        "failed_rows": failed
    }

import pandas as pd

def check_primary_key(df: pd.DataFrame, key_columns):
    """
    Validate that the specified columns form a unique primary key.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to check.
    key_columns : list of str
        List of columns expected to form a unique primary key.

    Returns
    -------
    dict
        {
            "name": "Primary Key Check",
            "passed": bool,
            "message": str,
            "failed_rows": list of indices
        }

    Fails When
    ----------
    - Duplicates exist across the specified key columns.
    """
    duplicates = df[df.duplicated(subset=key_columns)].index.tolist()
    return {
        "name": "Primary Key Check",
        "passed": len(duplicates) == 0,
        "message": f"{len(duplicates)} duplicate primary key rows" if duplicates else "Primary key is unique",
        "failed_rows": duplicates
    }

def check_foreign_key(df: pd.DataFrame, foreign_col, ref_df: pd.DataFrame, ref_col):
    """
    Validate that all values in a foreign key column exist in the reference table.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the foreign key column.
    foreign_col : str
        The column name representing the foreign key.
    ref_df : pd.DataFrame
        The reference DataFrame containing valid values.
    ref_col : str
        The column in the reference DataFrame to validate against.

    Returns
    -------
    dict
        {
            "name": "Foreign Key Check",
            "passed": bool,
            "message": str,
            "failed_rows": list of indices
        }

    Fails When
    ----------
    - Any value in `foreign_col` does not exist in `ref_col`.
    """
    invalid = df[~df[foreign_col].isin(ref_df[ref_col])].index.tolist()
    return {
        "name": "Foreign Key Check",
        "passed": len(invalid) == 0,
        "message": f"{len(invalid)} invalid foreign key values" if invalid else "All foreign keys valid",
        "failed_rows": invalid
    }

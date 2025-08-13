import pandas as pd
import numpy as np

def check_outliers(series: pd.Series, method="zscore", threshold=3):
    """
    Detect outliers in a numeric column.

    Parameters
    ----------
    series : pd.Series
        The numeric column to check.
    method : str
        'zscore' or 'iqr' (interquartile range method).
    threshold : float
        The cutoff for detecting outliers.

    Returns
    -------
    dict
        {
            "name": "Outlier Check",
            "passed": bool,
            "message": str,
            "failed_rows": list of indices
        }

    Fails When
    ----------
    - Any values exceed the z-score or IQR threshold.
    """
    failed = []
    if method == "zscore":
        z_scores = (series - series.mean()) / series.std()
        failed = series[abs(z_scores) > threshold].index.tolist()
    elif method == "iqr":
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        failed = series[(series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)].index.tolist()

    return {
        "name": "Outlier Check",
        "passed": len(failed) == 0,
        "message": f"{len(failed)} outliers detected" if failed else "No outliers",
        "failed_rows": failed
    }

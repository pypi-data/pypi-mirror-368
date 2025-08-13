import pandas as pd

def check_missing_dates(series: pd.Series, freq="D"):
    """
    Check for missing dates in a time series column.

    Parameters
    ----------
    series : pd.Series
        The date column to check.
    freq : str
        The expected frequency (e.g., "D" for daily, "M" for monthly).

    Returns
    -------
    dict
        {
            "name": "Missing Dates Check",
            "passed": bool,
            "message": str,
            "failed_rows": list of missing dates
        }

    Fails When
    ----------
    - Any expected dates are missing from the series.
    """
    dates = pd.to_datetime(series.dropna())
    all_dates = pd.date_range(dates.min(), dates.max(), freq=freq)
    missing = sorted(set(all_dates) - set(dates))
    return {
        "name": "Missing Dates Check",
        "passed": len(missing) == 0,
        "message": f"{len(missing)} missing dates" if missing else "All dates present",
        "failed_rows": missing
    }

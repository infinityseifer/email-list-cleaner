"""I/O helpers for reading and writing CSV files used by the app.

These utilities keep I/O logic separate from UI and validation so they can
be unit tested independently.
"""
from __future__ import annotations

import pandas as pd


def read_csv_any(path_or_buf) -> pd.DataFrame:
    """Read a CSV file into a DataFrame with all values as strings.

    Args:
        path_or_buf: File path or file-like object (e.g., Streamlit uploader).

    Returns:
        DataFrame with dtype=str and empty values preserved (no NaN casting).
    """
    return pd.read_csv(path_or_buf, dtype=str, keep_default_na=False)


def write_csv(df: pd.DataFrame) -> bytes:
    """Encode a DataFrame as UTF-8 CSV for browser download.

    Args:
        df: DataFrame to serialize.

    Returns:
        CSV content as UTF-8 bytes suitable for a download button.
    """
    return df.to_csv(index=False).encode("utf-8")
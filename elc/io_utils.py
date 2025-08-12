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

# --- v1.1 helper: build ZIP bytes for Streamlit downloads ---
import io
import zipfile
from typing import Dict

def make_zip_from_bytes(files: Dict[str, bytes], compresslevel: int = 9) -> bytes:
    """Create a ZIP archive (bytes) from a mapping of {filename: content_bytes}.

    Args:
        files: Dict of filename -> bytes (each value must be bytes or str).
        compresslevel: ZIP_DEFLATED compression level (0-9).

    Returns:
        ZIP file content as raw bytes, ready for st.download_button(data=...).
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(
        buf, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=compresslevel
    ) as z:
        for name, content in files.items():
            if isinstance(content, str):
                content = content.encode("utf-8")
            z.writestr(name, content or b"")
    buf.seek(0)
    return buf.getvalue()


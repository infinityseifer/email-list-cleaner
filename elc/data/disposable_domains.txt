"""Simple summary metrics for the cleaning flow."""
from __future__ import annotations


def summarize(total: int, cleaned: int, invalid: int) -> dict:
    """Produce a consistent dictionary of summary statistics.

    Args:
        total: Number of input rows.
        cleaned: Count of rows considered valid after cleaning.
        invalid: Count of rows rejected by validation.

    Returns:
        Dict containing counts and the valid percentage rounded to 2 decimals.
    """
    return {
        "total_rows": total,
        "cleaned_valid": cleaned,
        "rejected": invalid,
        "valid_rate_pct": round((cleaned / total) * 100, 2) if total else 0.0,
    }
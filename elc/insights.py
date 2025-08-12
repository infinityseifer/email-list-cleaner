"""Insights & KPI helpers for Email List Cleaner v1.1.

This module provides small, focused utilities for summarizing pipeline outputs:
- Aggregating rejection reasons into a histogram with percentages.
- Building a standard KPI dict for the UI and optional CSV export.

Design notes:
- These functions are pure (no I/O) to keep them easy to test.
- Percentages are computed over rows that contain *any* reason string.
"""
from __future__ import annotations

from collections import Counter
from typing import Iterable, Dict, Any
import pandas as pd


def reasons_histogram(df: pd.DataFrame, reason_col: str = "reasons") -> pd.DataFrame:
    """Compute counts and percentages for rejection reasons.

    The `reason_col` is expected to contain semicolon-separated reason codes,
    e.g. ``"invalid_syntax;no_mx_record"``. Empty or missing values are ignored.

    Args:
        df: A DataFrame that includes a column with rejection reasons.
        reason_col: Name of the column containing reason strings.

    Returns:
        A DataFrame with columns ``['reason', 'count', 'percent']`` sorted by count desc.
        Percent is computed over the number of rows that had *any* reason present.
    """
    if reason_col not in df.columns or df.empty:
        return pd.DataFrame(columns=["reason", "count", "percent"])

    reasons_counter: Counter[str] = Counter()
    rows_with_reasons = 0

    for raw in df[reason_col].astype(str):
        s = (raw or "").strip()
        if not s:
            continue
        rows_with_reasons += 1
        parts = [p.strip() for p in s.split(";") if p.strip()]
        reasons_counter.update(parts)

    if rows_with_reasons == 0:
        return pd.DataFrame(columns=["reason", "count", "percent"])

    items = [
        {
            "reason": reason,
            "count": count,
            "percent": round((count / rows_with_reasons) * 100, 2),
        }
        for reason, count in reasons_counter.most_common()
    ]
    return pd.DataFrame(items, columns=["reason", "count", "percent"])


def summary_kpis(total: int, valid: int, rejected: int, duration_s: float | None = None) -> Dict[str, Any]:
    """Assemble standard summary KPIs for display or CSV export.

    Args:
        total: Number of input rows provided to the pipeline.
        valid: Count of rows considered valid after cleaning.
        rejected: Count of rows rejected by validation.
        duration_s: Optional runtime in seconds for the operation.

    Returns:
        Dict with totals, percentages, and optional runtime key.
    """
    valid_rate = round((valid / total) * 100, 2) if total else 0.0
    metrics: Dict[str, Any] = {
        "total_rows": total,
        "valid_rows": valid,
        "rejected_rows": rejected,
        "valid_rate_pct": valid_rate,
    }
    if duration_s is not None:
        metrics["duration_s"] = round(float(duration_s), 3)
    return metrics

from __future__ import annotations
"""Insights helpers for Email List Cleaner (v1.2+).

Provides:
- reasons_histogram(...)    → table of reason counts (includes "suppressed")
- summary_kpis(...)         → consistent KPI dict for UI display
- combine_for_insights(...) → merges rejected & suppressed for one chart
"""
from typing import Optional
import pandas as pd


def _split_reasons(series: pd.Series, reason_col: str = "reasons") -> pd.DataFrame:
    """Explode a reasons column (semicolon-separated) into one row per reason."""
    if series is None or series.empty:
        return pd.DataFrame({reason_col: []})

    s = series.astype(str).str.strip()
    s = s[s.ne("") & s.ne("nan")]  # drop blanks and literal "nan"
    exploded = s.str.split(";", expand=False).explode().dropna()
    exploded = exploded.astype(str).str.strip()
    exploded = exploded[exploded.ne("")]
    return pd.DataFrame({reason_col: exploded})


def reasons_histogram(
    df: pd.DataFrame,
    *,
    reason_col: str = "reasons",
    sort_desc: bool = True,
    include_pct: bool = True,
) -> pd.DataFrame:
    """Return a histogram (counts and optional percentages) of rejection reasons."""
    cols = ["reason", "count", "percent"] if include_pct else ["reason", "count"]
    if df is None or df.empty or reason_col not in df.columns:
        return pd.DataFrame(columns=cols)

    exploded = _split_reasons(df[reason_col], reason_col=reason_col)
    if exploded.empty:
        return pd.DataFrame(columns=cols)

    counts = exploded.value_counts(subset=[reason_col]).reset_index(name="count")
    counts = counts.rename(columns={reason_col: "reason"})

    if sort_desc:
        counts = counts.sort_values("count", ascending=False, kind="stable")

    if include_pct:
        total = counts["count"].sum() or 1
        counts["percent"] = (counts["count"] / total * 100).round(2)

    return counts.reset_index(drop=True)


def combine_for_insights(
    rejected_df: Optional[pd.DataFrame],
    suppressed_df: Optional[pd.DataFrame],
    *,
    reason_col: str = "reasons",
) -> pd.DataFrame:
    """Combine rejected + suppressed rows for a unified 'Why excluded or rejected?' view."""
    parts: list[pd.DataFrame] = []
    if isinstance(rejected_df, pd.DataFrame) and not rejected_df.empty:
        parts.append(rejected_df)
    if isinstance(suppressed_df, pd.DataFrame) and not suppressed_df.empty:
        parts.append(suppressed_df)

    if not parts:
        return pd.DataFrame(columns=[reason_col])

    fixed: list[pd.DataFrame] = []
    for part in parts:
        if reason_col in part.columns:
            fixed.append(part)
        else:
            p = part.copy()
            p[reason_col] = ""
            fixed.append(p)

    return pd.concat(fixed, ignore_index=True)


def summary_kpis(
    *,
    total: int,
    valid: int,
    rejected: int,
    duration_s: float,
) -> dict:
    """Produce a consistent dict of high-level KPIs for UI."""
    total = int(total or 0)
    valid = int(valid or 0)
    rejected = int(rejected or 0)
    duration_s = float(duration_s or 0.0)

    return {
        "total_rows": total,
        "valid_rows": valid,
        "rejected_rows": rejected,
        "valid_rate_pct": round((valid / total) * 100, 2) if total else 0.0,
        "duration_s": round(duration_s, 3),
    }

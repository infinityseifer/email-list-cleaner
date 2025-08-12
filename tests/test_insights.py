"""Unit tests for insights helpers."""
from __future__ import annotations

import pandas as pd
from elc.insights import reasons_histogram, summary_kpis


def test_reasons_histogram_basic() -> None:
    """Histogram should count individual reason tokens and compute percent over rows with any reason."""
    df = pd.DataFrame({
        "email": ["a@x.com", "b@x.com", "c@x.com", "d@x.com"],
        "reasons": ["invalid_syntax;no_mx_record", "invalid_syntax", "", "disposable_domain;invalid_syntax"],
    })
    hist = reasons_histogram(df)
    rows_with_reasons = (df["reasons"].astype(str) != "").sum()
    assert rows_with_reasons == 3
    invalid_row = hist[hist["reason"] == "invalid_syntax"].iloc[0]
    assert invalid_row["count"] == 3
    assert invalid_row["percent"] == 100.0  # 3 occurrences across 3 rows with reasons


def test_summary_kpis_fields() -> None:
    """KPI dict should include counts, valid rate, and optional duration."""
    d = summary_kpis(total=10, valid=7, rejected=3, duration_s=1.23456)
    assert d["total_rows"] == 10
    assert d["valid_rows"] == 7
    assert d["rejected_rows"] == 3
    assert d["valid_rate_pct"] == 70.0
    assert d["duration_s"] == 1.235

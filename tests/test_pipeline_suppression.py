"""Suppression flow tests (v1.2 PR-1)."""
from __future__ import annotations

import pandas as pd
from elc.suppression import to_suppression_set, _canonical_for_match


def test_suppression_set_basic() -> None:
    df = pd.DataFrame({"email": ["A@x.com ", "  ", "b@x.com", None]})
    s = to_suppression_set(df, "email")
    # Canonical form is lowercase, trimmed, non-empty
    assert "a@x.com" in s
    assert "b@x.com" in s
    assert "" not in s


def test_pipeline_excludes_suppressed_case_insensitive() -> None:
    main = pd.DataFrame({"email": ["a@x.com", "b@x.com", "c@x.com"]})
    suppression = pd.DataFrame({"email": ["B@X.COM"]})  # different case on purpose
    supp = to_suppression_set(suppression, "email")
    assert "b@x.com" in supp  # canonicalized

    mask_supp = main["email"].astype(str).map(_canonical_for_match).isin(supp)
    suppressed_df = main.loc[mask_supp].copy()
    cleaned_df = main.loc[~mask_supp].copy()

    assert suppressed_df["email"].tolist() == ["b@x.com"]
    assert cleaned_df["email"].tolist() == ["a@x.com", "c@x.com"]

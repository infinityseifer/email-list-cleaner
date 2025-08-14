"""Suppression list helpers (v1.2 PR-1).

Converts an uploaded suppression CSV into a normalized set of emails so the
pipeline can exclude those addresses before validation.

Matching is case-insensitive (canonicalized to lower-case after normalize).
"""
from __future__ import annotations

from typing import Set
import pandas as pd

from elc.cleaning import normalize_email


def _canonical_for_match(e: str) -> str:
    """Case-insensitive canonical form used for suppression matching.

    Returns:
        Normalized, lower-cased email string ('' if missing).
    """
    e = normalize_email(e)
    return e.lower()


def to_suppression_set(df: pd.DataFrame, email_col: str) -> Set[str]:
    """Build a set of canonical emails from a suppression DataFrame.

    Args:
        df: Suppression CSV loaded as a DataFrame.
        email_col: Column that contains email addresses.

    Returns:
        A set of normalized, lower-cased email strings.
    """
    if df is None or df.empty or email_col not in df.columns:
        return set()
    col = df[email_col].astype(str).map(_canonical_for_match)
    # Treat empty strings as absent
    return {e for e in col if e}

"""Cleaning utilities for email addresses.

Functions here normalize individual email strings and prepare DataFrames by
removing blank or duplicate email rows.
"""
from __future__ import annotations

from typing import Tuple
import pandas as pd


def normalize_email(e: str) -> str:
    """Normalize a single email string.

    Strips surrounding whitespace and removes interior spaces.

    Args:
        e: Raw email value which may not be a string.

    Returns:
        Normalized email string, or empty string if input is not a valid str.
    """
    if not isinstance(e, str):
        return ""
    e = e.strip().replace(" ", "")
    return e


def split_local_domain(email: str) -> Tuple[str, str]:
    """Split an email into local part and domain, lowercasing the domain.

    Args:
        email: Normalized email string.

    Returns:
        (local, domain) tuple; domain is lowercased.
    """
    if "@" not in email:
        return email, ""
    local, domain = email.rsplit("@", 1)
    return local, domain.lower()


def dedupe_and_drop_blanks(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Remove blank emails and duplicates in place-safe manner.

    Args:
        df: Input DataFrame with an email column.
        col: Name of the email column.

    Returns:
        A shallow-copied DataFrame with blanks removed and duplicates dropped.
    """
    df = df.copy()
    df[col] = df[col].astype(str).map(normalize_email)
    df = df[df[col] != ""]
    df = df.drop_duplicates(subset=[col])
    return df
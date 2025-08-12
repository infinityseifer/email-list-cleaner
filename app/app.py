"""Streamlit UI for the Email List Cleaner.

This module wires the user interface to the core library functions in `elc/`.
It handles:
- CSV upload and preview
- Option toggles (safe mode, MX checks)
- Calling the cleaning/validation pipeline
- Rendering summary metrics and download buttons

All processing is performed in-memory for privacy and simplicity.
"""
from __future__ import annotations

import io
import zipfile
from typing import Iterable

import pandas as pd
import streamlit as st

import sys
from pathlib import Path
# Ensure project root is on sys.path before importing `elc`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import core logic from the elc package
import elc.io_utils as io_utils
from elc.cleaning import dedupe_and_drop_blanks, split_local_domain
from elc.validate import is_rfc_valid, is_disposable, has_mx_record
from elc.suggest import suggest_domain, COMMON_FIXES

st.set_page_config(page_title="Email List Cleaner", page_icon="✅")


def _load_sets() -> tuple[set[str], list[str]]:
    """Load disposable and common domains from local data files."""
    with open("elc/data/disposable_domains.txt", encoding="utf-8") as f:
        disposable = {d.strip() for d in f if d.strip() and not d.startswith("#")}
    with open("elc/data/common_domains.txt", encoding="utf-8") as f:
        common = [d.strip() for d in f if d.strip() and not d.startswith("#")]
    return disposable, common


@st.cache_resource(show_spinner=False)
def get_domain_sets() -> tuple[set[str], list[str]]:
    """Cached accessor for domain lists to avoid re-reading files on reruns."""
    return _load_sets()


def _clean_and_validate(
    df: pd.DataFrame,
    email_col: str,
    disposable_set: set[str],
    common_domains: Iterable[str],
    *,
    mx_check: bool = False,
    safe_mode: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Run the cleaning and validation pipeline over a DataFrame."""
    total = len(df)
    df = dedupe_and_drop_blanks(df, email_col)

    valid_rows: list[pd.Series] = []
    rejected_rows: list[pd.Series] = []

    for _, row in df.iterrows():
        email = str(row[email_col])
        local, domain = split_local_domain(email)

        rfc_ok = is_rfc_valid(email)
        disposable = is_disposable(domain, disposable_set)

        mx_ok = True
        if mx_check and domain:
            mx_ok = has_mx_record(domain)

        fix = COMMON_FIXES.get(domain) or suggest_domain(domain, list(common_domains))

        reasons: list[str] = []
        if not rfc_ok:
            reasons.append("invalid_syntax")
        if disposable:
            reasons.append("disposable_domain")
        if mx_check and not mx_ok:
            reasons.append("no_mx_record")

        borderline = (rfc_ok and not disposable and (not mx_check or mx_ok) and bool(fix))

        if (not reasons) or (safe_mode and borderline):
            # Apply safe domain fix (do not modify local part)
            if fix and not disposable and domain:
                email = f"{local}@{fix}"
                row[email_col] = email
            valid_rows.append(row)
        else:
            r = row.copy()
            r["reasons"] = ";".join(reasons)
            r["suggested_domain"] = fix or ""
            rejected_rows.append(r)

    valid_df = pd.DataFrame(valid_rows)
    rejected_df = pd.DataFrame(rejected_rows)

    summary = {
        "total_rows": total,
        "processed_rows": len(df),
        "valid": len(valid_df),
        "rejected": len(rejected_df),
        "valid_rate_pct": round((len(valid_df) / total) * 100, 2) if total else 0.0,
    }
    return valid_df, rejected_df, summary


# UI — header and instructions
st.title("Email List Cleaner")
st.caption(
    "Upload a CSV, choose your email column, and export a cleaned list. "
    "All processing happens in-memory."
)

# Options and uploads
file = st.file_uploader("Upload CSV", type=["csv"], help="Upload your email list as a CSV file (UTF-8)")
col1, col2 = st.columns(2)
mx_check = col1.toggle(
    "Enable MX checks (slower)",
    value=False,
    help="Verify that recipient domains have mail servers (DNS MX records).",
)
safe_mode = col2.toggle(
    "Safe mode (fix/flag borderline)",
    value=True,
    help="Avoid aggressive rejections by keeping rows that can be safely fixed.",
)

if file:
    disposable_set, common_domains = get_domain_sets()

    # Use io_utils.* names
    df = io_utils.read_csv_any(file)
    st.write("### File Preview", df.head(10))

    email_col = st.selectbox("Select email column", options=df.columns.tolist())

    if st.button("Clean & Validate", type="primary"):
        valid_df, rejected_df, summary = _clean_and_validate(
            df,
            email_col,
            disposable_set,
            common_domains,
            mx_check=mx_check,
            safe_mode=safe_mode,
        )

        st.success(
            f"Processed {summary['total_rows']} rows → "
            f"{summary['valid']} valid, {summary['rejected']} rejected."
        )

        c1, c2 = st.columns(2)
        with c1:
            if not valid_df.empty:
                st.download_button(
                    "⬇️ Download Cleaned CSV",
                    data=io_utils.write_csv(valid_df),
                    file_name="cleaned_emails.csv",
                    mime="text/csv",
                )
        with c2:
            if not rejected_df.empty:
                st.download_button(
                    "⬇️ Download Rejected CSV",
                    data=io_utils.write_csv(rejected_df),
                    file_name="rejected_emails.csv",
                    mime="text/csv",
                )

        if not valid_df.empty or not rejected_df.empty:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                if not valid_df.empty:
                    z.writestr("cleaned_emails.csv", io_utils.write_csv(valid_df))
                if not rejected_df.empty:
                    z.writestr("rejected_emails.csv", io_utils.write_csv(rejected_df))
            st.download_button(
                "⬇️ Download both as ZIP",
                data=buf.getvalue(),
                file_name="results.zip",
                mime="application/zip",
            )

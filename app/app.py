"""Streamlit UI for the Email List Cleaner (v1.1).

What this file does:
- CSV upload & preview
- Sidebar settings (Safe mode, MX checks, MX timeout)
- Cleaning & validation pipeline wiring
- Insights: "Why rejected?" histogram + CSV
- Reliable ZIP download (Cleaned, Rejected, Insights)

Notes:
- All processing remains in-memory (privacy-friendly).
- MX timeouts are surfaced as 'mx_unknown' (not an auto-fail).
"""
from __future__ import annotations

import io
import time
from typing import Iterable

import pandas as pd
import streamlit as st

# --- Make 'elc' package importable when running `streamlit run app/app.py` locally ---
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# --- Core project imports ---
from elc import config
from elc.io_utils import read_csv_any, write_csv, make_zip_from_bytes
from elc.cleaning import dedupe_and_drop_blanks, split_local_domain
from elc.validate import is_rfc_valid, is_disposable, has_mx_record
from elc.suggest import suggest_domain, COMMON_FIXES
from elc.insights import reasons_histogram, summary_kpis

st.set_page_config(page_title="Email List Cleaner", page_icon="✅")


def _load_sets() -> tuple[set[str], list[str]]:
    """Load disposable and common domains from local data files.

    Returns:
        (disposable_set, common_domains)
    """
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
    mx_timeout: float = config.DNS_TIMEOUT,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Run the cleaning & validation pipeline over a DataFrame.

    Args:
        df: Input DataFrame containing at least an email column.
        email_col: Name of the column with email addresses.
        disposable_set: Set of domains considered disposable/temporary.
        common_domains: Iterable of known legit domains for typo suggestions.
        mx_check: If True, check MX DNS records (slower).
        safe_mode: If True, keep borderline rows and apply safe fixes.
        mx_timeout: Per-domain MX query timeout in seconds.

    Returns:
        (valid_df, rejected_df, summary)
            valid_df: Rows that passed checks; email may be auto-fixed.
            rejected_df: Rows that failed checks, with 'reasons' and 'suggested_domain'.
            summary: Dict with totals and percentages.
    """
    total = len(df)
    df = dedupe_and_drop_blanks(df, email_col)

    valid_rows: list[pd.Series] = []
    rejected_rows: list[pd.Series] = []

    for _, row in df.iterrows():
        email = str(row[email_col])
        local, domain = split_local_domain(email)

        rfc_ok = is_rfc_valid(email)
        disposable = is_disposable(domain, disposable_set)

        mx_status: bool | None = True
        if mx_check and domain:
            # has_mx_record returns:
            #   True  -> has MX
            #   False -> definitely no MX
            #   None  -> timeout/unknown error
            mx_status = has_mx_record(domain, timeout=mx_timeout)

        fix = COMMON_FIXES.get(domain) or suggest_domain(domain, list(common_domains))

        reasons: list[str] = []
        if not rfc_ok:
            reasons.append("invalid_syntax")
        if disposable:
            reasons.append("disposable_domain")
        if mx_check:
            if mx_status is False:
                reasons.append("no_mx_record")
            elif mx_status is None:
                reasons.append("mx_unknown")

        # Borderline means: syntactically OK, not disposable, MX not failing,
        # and we *have* a domain fix suggestion.
        borderline = (
            rfc_ok
            and not disposable
            and (not mx_check or (mx_status is True))
            and bool(fix)
        )

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


# === UI ===
st.title("Email List Cleaner")
st.caption("Upload a CSV, choose your email column, and export a cleaned list. All processing happens in-memory.")

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    safe_mode = st.toggle(
        "Safe mode (fix/flag borderline)",
        value=True,
        help="Avoid aggressive rejections by keeping rows that can be safely fixed.",
    )
    mx_check = st.toggle(
        "Enable MX checks",
        value=False,
        help="Verify that recipient domains have mail servers (DNS MX records).",
    )
    mx_timeout = st.slider(
        "MX timeout (seconds)",
        min_value=0.5, max_value=5.0, value=float(config.DNS_TIMEOUT), step=0.5,
        help="Per-domain DNS query timeout. Longer timeouts may be slower.",
    )
    st.divider()
    st.markdown(
        "_v1.1 UI: MX timeout & insights. All data stays in-memory; nothing is stored._"
    )

# Upload
file = st.file_uploader("Upload CSV", type=["csv"], help="Upload your email list as a CSV file (UTF-8)")

if file:
    # Optional guardrail: file size limit (if provided by uploader)
    if hasattr(file, "size") and file.size and file.size > config.MAX_FILE_MB * 1024 * 1024:
        st.error(f"File is larger than {config.MAX_FILE_MB} MB. Please upload a smaller CSV.")
        st.stop()

    disposable_set, common_domains = get_domain_sets()

    # Read & preview
    df = read_csv_any(file)
    st.write("### File Preview", df.head(10))
    st.caption(f"Rows: {len(df):,} • Columns: {len(df.columns)}")

    email_col = st.selectbox("Select email column", options=df.columns.tolist())

    if st.button("Clean & Validate", type="primary"):
        start = time.perf_counter()
        valid_df, rejected_df, summary = _clean_and_validate(
            df,
            email_col,
            disposable_set,
            common_domains,
            mx_check=mx_check,
            safe_mode=safe_mode,
            mx_timeout=mx_timeout,
        )
        dur = time.perf_counter() - start

        kpis = summary_kpis(
            total=summary["total_rows"],
            valid=summary["valid"],
            rejected=summary["rejected"],
            duration_s=dur,
        )

        st.success(
            f"Processed {kpis['total_rows']:,} rows in {kpis['duration_s']:.3f}s → "
            f"{kpis['valid_rows']:,} valid, {kpis['rejected_rows']:,} rejected "
            f"({kpis['valid_rate_pct']}% valid)."
        )

        # Downloads: individual CSVs
        c1, c2 = st.columns(2)
        with c1:
            if not valid_df.empty:
                st.download_button(
                    "⬇️ Download Cleaned CSV",
                    data=write_csv(valid_df),
                    file_name="cleaned_emails.csv",
                    mime="text/csv",
                )
        with c2:
            if not rejected_df.empty:
                st.download_button(
                    "⬇️ Download Rejected CSV",
                    data=write_csv(rejected_df),
                    file_name="rejected_emails.csv",
                    mime="text/csv",
                )

        # Insights: Why rejected?
        insights_csv_bytes: bytes | None = None
        if not rejected_df.empty and "reasons" in rejected_df.columns:
            st.subheader("Why were emails rejected?")
            hist = reasons_histogram(rejected_df, reason_col="reasons")
            if not hist.empty:
                st.dataframe(hist, use_container_width=True)
                insights_csv_bytes = hist.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Insights CSV",
                    data=insights_csv_bytes,
                    file_name="rejection_insights.csv",
                    mime="text/csv",
                )
            else:
                st.info("No rejection reasons to summarize.")

        # Bundle ZIP (Cleaned, Rejected, Insights if present)
        files_for_zip: dict[str, bytes] = {}
        if not valid_df.empty:
            files_for_zip["cleaned_emails.csv"] = write_csv(valid_df)
        if not rejected_df.empty:
            files_for_zip["rejected_emails.csv"] = write_csv(rejected_df)
        if insights_csv_bytes:
            files_for_zip["rejection_insights.csv"] = insights_csv_bytes

        if files_for_zip:
            zip_bytes = make_zip_from_bytes(files_for_zip, compresslevel=9)
            st.download_button(
                "📦 Download all as ZIP",
                data=zip_bytes,
                file_name="results.zip",
                mime="application/zip",
                type="secondary",
                use_container_width=True,
            )

        # Optional: quick previews
        if not valid_df.empty:
            st.write("#### Cleaned (top 10)")
            st.dataframe(valid_df.head(10), use_container_width=True)
        if not rejected_df.empty:
            st.write("#### Rejected (top 10)")
            st.dataframe(rejected_df.head(10), use_container_width=True)
else:
    st.info("Upload a CSV to get started.")

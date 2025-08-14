"""Streamlit UI for the Email List Cleaner (v1.1 + suppression wiring).

What this file does:
- CSV upload & preview
- Sidebar settings (Safe mode, MX checks, MX timeout)
- Optional suppression CSV (exclude those emails before validation)
- Cleaning & validation pipeline wiring
- Insights: "Why excluded/rejected?" histogram + CSV
- Reliable ZIP download (Cleaned, Rejected, Suppressed, Insights)

Notes:
- All processing remains in-memory (privacy-friendly).
- MX timeouts are surfaced as 'mx_unknown' (not an auto-fail).
"""
from __future__ import annotations

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
from elc.cleaning import dedupe_and_drop_blanks, split_local_domain, normalize_email
from elc.io_utils import read_csv_any, write_csv
from elc.validate import is_rfc_valid, is_disposable, has_mx_record
from elc.suggest import suggest_domain, COMMON_FIXES
from elc.insights import reasons_histogram, summary_kpis, combine_for_insights
from elc.suppression import to_suppression_set

# Optional: if make_zip_from_bytes isn't in io_utils yet, define a local fallback
try:
    from elc.io_utils import make_zip_from_bytes  # type: ignore
except Exception:
    import io, zipfile
    def make_zip_from_bytes(files: dict[str, bytes], compresslevel: int = 9) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=compresslevel) as z:
            for name, data in files.items():
                z.writestr(name, data)
        return buf.getvalue()

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
    """Run the cleaning & validation pipeline over a DataFrame."""
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
            # True  -> has MX
            # False -> no MX
            # None  -> timeout/unknown
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

        borderline = (
            rfc_ok
            and not disposable
            and (not mx_check or (mx_status is True))
            and bool(fix)
        )

        if (not reasons) or (safe_mode and borderline):
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
    st.markdown("_v1.1 UI: MX timeout & insights. All data stays in-memory; nothing is stored._")

    # Suppression controls
    st.subheader("Suppression (optional)")
    suppression_file = st.file_uploader(
        "Upload suppression CSV",
        type=["csv"],
        key="supp_csv",
        help="Rows whose email appears in this list will be excluded and labeled 'suppressed'.",
    )
    suppression_df = None
    suppression_email_col = None
    if suppression_file:
        suppression_df = read_csv_any(suppression_file)
        st.caption(f"Suppression rows: {len(suppression_df):,}")
        suppression_email_col = st.selectbox(
            "Suppression email column",
            options=suppression_df.columns.tolist(),
            key="supp_email_col",
        )

# Upload
file = st.file_uploader("Upload CSV", type=["csv"], help="Upload your email list as a CSV file (UTF-8)")

if file:
    # Optional guardrail: size limit (if provided by uploader)
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

        # 1) Build suppression set (canonicalized), if provided
        suppression_set: set[str] = set()
        suppressed_df = pd.DataFrame()
        if suppression_df is not None and suppression_email_col:
            suppression_set = to_suppression_set(suppression_df, suppression_email_col)

        # 2) Split out suppressed BEFORE validation (case-insensitive)
        working_df = df.copy()
        if suppression_set:
            canonical_series = working_df[email_col].astype(str).map(lambda e: normalize_email(e).lower())
            mask_supp = canonical_series.isin(suppression_set)
            if mask_supp.any():
                suppressed_df = working_df.loc[mask_supp].copy()
                suppressed_df["reasons"] = "suppressed"
                working_df = working_df.loc[~mask_supp].copy()

        # 3) Run the pipeline on the remaining rows
        valid_df, rejected_df, summary = _clean_and_validate(
            working_df,
            email_col,
            disposable_set,
            common_domains,
            mx_check=mx_check,
            safe_mode=safe_mode,
            mx_timeout=mx_timeout,
        )
        dur = time.perf_counter() - start

        # 4) KPIs based on original input total
        total_input = len(df)
        kpis = summary_kpis(
            total=total_input,
            valid=len(valid_df),
            rejected=len(rejected_df),
            duration_s=dur,
        )
        suppressed_count = len(suppressed_df)
        if suppressed_count:
            kpis["suppressed_rows"] = suppressed_count
            st.info(f"Suppressed {suppressed_count:,} rows based on your suppression list.")

        suppressed_str = f", {kpis['suppressed_rows']:,} suppressed" if suppressed_count else ""
        st.success(
            f"Processed {kpis['total_rows']:,} rows in {kpis['duration_s']:.3f}s → "
            f"{kpis['valid_rows']:,} valid, {kpis['rejected_rows']:,} rejected"
            f"{suppressed_str} ({kpis['valid_rate_pct']}% valid)."
        )

        # 5) Insights over rejected + suppressed
        insights_csv_bytes: bytes | None = None
        insights_source = combine_for_insights(rejected_df, suppressed_df, reason_col="reasons")
        if not insights_source.empty and "reasons" in insights_source.columns:
            st.subheader("Why were emails excluded or rejected?")
            hist = reasons_histogram(insights_source, reason_col="reasons")
            if not hist.empty:
                st.dataframe(hist, use_container_width=True)
                # Quick bar chart for counts
                st.bar_chart(hist.set_index("reason")["count"])
                insights_csv_bytes = hist.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Insights CSV",
                    data=insights_csv_bytes,
                    file_name="rejection_insights.csv",
                    mime="text/csv",
                )
            else:
                st.info("No reasons to summarize.")
        else:
            st.info("No rejected or suppressed rows to analyze.")

        # 6) Downloads: individual CSVs
        col_left, col_right = st.columns(2)
        with col_left:
            if not valid_df.empty:
                st.download_button(
                    "⬇️ Download Cleaned CSV",
                    data=write_csv(valid_df),
                    file_name="cleaned_emails.csv",
                    mime="text/csv",
                )
        with col_right:
            if not rejected_df.empty:
                st.download_button(
                    "⬇️ Download Rejected CSV",
                    data=write_csv(rejected_df),
                    file_name="rejected_emails.csv",
                    mime="text/csv",
                )
        if not suppressed_df.empty:
            st.download_button(
                "⬇️ Download Suppressed CSV",
                data=write_csv(suppressed_df),
                file_name="suppressed_emails.csv",
                mime="text/csv",
            )

        # 7) ZIP bundle (Cleaned, Rejected, Suppressed, Insights)
        files_for_zip: dict[str, bytes] = {}
        if not valid_df.empty:
            files_for_zip["cleaned_emails.csv"] = write_csv(valid_df)
        if not rejected_df.empty:
            files_for_zip["rejected_emails.csv"] = write_csv(rejected_df)
        if not suppressed_df.empty:
            files_for_zip["suppressed_emails.csv"] = write_csv(suppressed_df)
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

        # 8) Optional previews
        if not valid_df.empty:
            st.write("#### Cleaned (top 10)")
            st.dataframe(valid_df.head(10), use_container_width=True)
        if not rejected_df.empty:
            st.write("#### Rejected (top 10)")
            st.dataframe(rejected_df.head(10), use_container_width=True)
        if not suppressed_df.empty:
            st.write("#### Suppressed (top 10)")
            st.dataframe(suppressed_df.head(10), use_container_width=True)
else:
    st.info("Upload a CSV to get started.")

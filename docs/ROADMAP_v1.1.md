# Email List Cleaner – v1.1 Roadmap

## Goals
- Faster MX checks (parallel, timeout) with progress.
- Rejection insights (histograms + filter view).
- Guardrails (file size/encoding).
- Stronger domain intelligence (expanded disposables + smarter typo fix).
- Optional in-session analytics (no PII, opt-in).

## Feature Set & Acceptance Criteria
### Parallel MX Checks + Timeout
- Threaded lookups with per-domain timeout; `mx_unknown` on timeout.
- 50k rows ≤ 20s typical (network permitting).
- Progress indicator shows % complete.

### Rejection Insights (Histograms)
- Counts/% for `invalid_syntax`, `disposable_domain`, `no_mx_record`, `mx_unknown`.
- Click a reason to filter preview table.
- Export insights as CSV.

### File Size & Encoding Guardrails
- Hard cap 20MB (configurable); friendly error message.
- Latin‑1 fallback path covered in tests.

### Domain Intelligence Upgrade
- Expand `disposable_domains.txt` and implement merger script.
- Dedup, lowercase, sort; deterministic output.

### Typo-Fix Enhancements
- Threshold scales by domain length; explicit fixes preferred.

### Lightweight Analytics (Opt‑in)
- Counters only: rows, valid %, runtime, MX on/off.
- Display-only; no persistence or network calls.

## Architecture Changes
- Use `concurrent.futures.ThreadPoolExecutor` for MX checks.
- Central config in `elc/config.py`.
- New `elc/insights.py` for histograms & KPI summaries.

## Testing
- Unit tests for histogram aggregation & summary KPIs.
- MX concurrency tests (mock resolver + timeouts).
- Large file boundary tests.

## Versioning
- Branch: `release/v1.1.0`
- Bump `__version__ = "1.1.0-dev"` in `elc/__init__.py`.



🎯 What It Does (MVP)  
[**Open the MVP App**](https://email-list-cleaner-v1-0-0-mvp.streamlit.app/) | [**Try v1.1 Preview**](https://email-list-cleaner-v1-1-preview.streamlit.app/)
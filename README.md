📧 Email List Cleaner (MVP)
A Streamlit app and Python package to clean and validate email lists quickly, safely, and entirely in memory — no data is stored.

# 1) Create venv
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the app
streamlit run app/app.py

🎯 What It Does (MVP)
Upload a .csv file (UTF-8, ≤ 20MB) containing email addresses

Preview the first 10 rows before processing

Select which column contains emails

Clean & validate:

Trim whitespace

Remove blanks & duplicates

Validate syntax (RFC)

Flag disposable domains

(Optional) check MX records

(Optional) auto-fix common domain typos

Safe Mode ON by default: borderline rows are fixed or flagged, not dropped

Download:

cleaned_emails.csv

rejected_emails.csv

or both as a .zip

📄 See [""](docs/PRODUCT.md) for full user stories and acceptance criteria.

📋 Goals & Non-Goals
Goal: Clean uploaded email lists quickly & safely, producing clear “cleaned” vs. “rejected” outputs.
Non-Goals (MVP):

No login/authentication

No CRM/API integrations

No payments

No background jobs

🖥 Core User Stories
See [""](docs/PRODUCT.md) → User Stories for full details.

🔄 Data Flow & Architecture
See [""](docs/ARCHITECTURE.md) for diagrams and flow details.

Pipeline Steps (simplified):

Upload CSV → read_csv_any() → DataFrame

Normalize emails (trim, lowercase domains)

Drop blanks & duplicates

Validate syntax (RFC)

Flag disposable domains

(Optional) Check MX records

Suggest typo fixes

Split into valid & rejected

Output CSVs + summary

✅ Validation Rules
See [""](docs/VALIDATION.md) for the exact rules.

⚠ Edge Cases Handled
See [""](docs/EDGE_CASES.md) for the full list.

🎨 UI/UX Flow
File uploader with preview

Column selector for emails

Toggles: Safe Mode (ON), MX checks (OFF)

Results section:

Summary KPIs

Two preview tables (valid/rejected)

Download buttons (Cleaned, Rejected, ZIP)

Footer: version info, docs link, contact

📄 See [""](docs/UI_UX.md) for details.

📂 File Formats
See [""](docs/FILE_FORMATS.md)

📈 Performance Targets
50k rows < 10s without MX

< 60s with MX (DNS-dependent)

See [""](docs/PERFORMANCE.md)

🔒 Security & Privacy
All processing is in-memory

No logs of email content

One job per session

See [""](docs/SECURITY_PRIVACY.md)

⚙ Config & Resources
elc/data/disposable_domains.txt — disposable domains list

elc/data/common_domains.txt — common valid domains list

Config constants in [""](docs/CONFIG.md)

🚫 Error Handling
User-friendly messages for bad CSVs, missing columns, DNS failures, and empty results.

See [""](docs/ERRORS.md)

🧪 Testing
Unit tests in tests/* cover validation, cleaning, suggestion logic, and the full pipeline.

See [""](docs/TESTING.md)

📊 Observability
Console logs behind DEBUG flag

Summary metrics to user

See [""](docs/OBSERVABILITY.md)

🌍 Deployment
Streamlit Cloud:

Connect GitHub repo

Set entrypoint: app/app.py

Render/Fly:

bash
Copy code
streamlit run app/app.py --server.port $PORT --server.address 0.0.0.0

🗂 Quick File Map
app/app.py                    # Streamlit UI
elc/cleaning.py               # Normalization & deduplication
elc/validate.py               # Syntax, disposable, MX checks
elc/suggest.py                # Domain typo suggestions
elc/io_utils.py               # CSV read/write helpers
elc/data/*.txt                 # Domain lists
.streamlit/config.toml        # UI theme/config
requirements.txt              # Dependencies
tests/*                       # Unit tests
docs/*.md                     # Detailed documentation

## Documentation

- [What it does (MVP)](docs/PRODUCT.md)
- [MVP Data Flow](docs/ARCHITECTURE.md)
- [Validation Rules](docs/VALIDATION.md)
- [Edge Cases](docs/EDGE_CASES.md)
- [UI/UX Flow](docs/UI_UX.md)
- [File Formats](docs/FILE_FORMATS.md)
- [Performance Targets](docs/PERFORMANCE.md)
- [Security & Privacy](docs/SECURITY_PRIVACY.md)
- [Config & Resources](docs/CONFIG.md)
- [Error Handling](docs/ERRORS.md)
- [Testing Plan](docs/TESTING.md)
- [Observability](docs/OBSERVABILITY.md)
- [Deployment](docs/DEPLOYMENT.md)

Quick File Map
App UI: app/app.py

Core logic: elc/cleaning.py, elc/validate.py, elc/suggest.py, elc/io_utils.py, elc/metrics.py

Data resources: elc/data/disposable_domains.txt, elc/data/common_domains.txt

Config/theme: .streamlit/config.toml

Requirements: requirements.txt

Tests: tests/*, sample CSV at tests/samples/sample_emails.csv

Docs: docs/*.md

📌 Version: v1.0.0 (MVP) — Changelog
📧 Contact: infinityabsllc@gmail.com





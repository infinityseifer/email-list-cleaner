📧 Email List Cleaner (MVP)
A Streamlit app and Python package to clean and validate email lists quickly, safely, and entirely in memory — no data is stored.

# 1) Create venv
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the app
streamlit run app/app.py

🎯 What It Does (MVP)

- Upload a `.csv` file (UTF-8, ≤ 20MB) containing email addresses  
- Preview the first 10 rows before processing  
- Select which column contains emails  
- Clean & validate:  
  - Trim whitespace  
  - Remove blanks & duplicates  
  - Validate syntax (RFC)  
  - Flag disposable domains  
  - (Optional) check MX records  
  - (Optional) auto-fix common domain typos  
- **Safe Mode ON** by default: borderline rows are fixed or flagged, not dropped  
- Download:  
  - `cleaned_emails.csv`  
  - `rejected_emails.csv`  
  - Or both as a `.zip`  

📄 See [What it does (MVP)](docs/PRODUCT.md) for full user stories and acceptance criteria.

---

📋 **Goals & Non-Goals**  
Goal: Clean uploaded email lists quickly & safely, producing clear “cleaned” vs. “rejected” outputs.  
Non-Goals (MVP): No login/authentication, CRM/API integrations, payments, or background jobs.

---

🖥 **Core User Stories**  
See [User Stories](docs/PRODUCT.md) for full details.

---

🔄 **Data Flow & Architecture**  
See [MVP Data Flow](docs/ARCHITECTURE.md) for diagrams and flow details.

---

✅ **Validation Rules**  
See [Validation Rules](docs/VALIDATION.md) for the exact rules.

---

⚠ **Edge Cases Handled**  
See [Edge Cases](docs/EDGE_CASES.md) for the full list.

---

🎨 **UI/UX Flow**  
See [UI/UX Flow](docs/UI_UX.md) for details.

---

📂 **File Formats**  
See [File Formats](docs/FILE_FORMATS.md)

---

📈 **Performance Targets**  
See [Performance Targets](docs/PERFORMANCE.md)

---

🔒 **Security & Privacy**  
See [Security & Privacy](docs/SECURITY_PRIVACY.md)

---

⚙ **Config & Resources**  
See [Config & Resources](docs/CONFIG.md)

---

🚫 **Error Handling**  
See [Error Handling](docs/ERRORS.md)

---

🧪 **Testing**  
See [Testing Plan](docs/TESTING.md)

---

📊 **Observability**  
See [Observability](docs/OBSERVABILITY.md)

---

🌍 **Deployment**  
See [Deployment](docs/DEPLOYMENT.md)

---

📂 **Quick File Map**  
- `app/app.py` — Streamlit UI  
- `elc/cleaning.py` — Normalization & deduplication  
- `elc/validate.py` — Syntax, disposable, MX checks  
- `elc/suggest.py` — Domain typo suggestions  
- `elc/io_utils.py` — CSV read/write helpers  
- `elc/data/*.txt` — Domain lists  
- `.streamlit/config.toml` — UI theme/config  
- `requirements.txt` — Dependencies  
- `tests/*` — Unit tests  
- `docs/*.md` — Detailed documentation  

📌 **Version:** v1.0.0 (MVP) — Changelog  
📧 **Contact:** infinityabsllc@gmail.com



# Changelog

## v1.0.0 – MVP Release
**Release Date:** 2025-08-12

### ✨ Features
- Upload and preview CSV files (UTF-8, ≤ 20MB) with email lists.
- Select which column contains email addresses.
- Clean and validate email lists:
  - Trim whitespace.
  - Remove blanks and duplicates.
  - Validate syntax (RFC).
  - Flag disposable domains.
  - *(Optional)* Check MX records.
  - *(Optional)* Auto-fix common domain typos.
- “Safe Mode” (default ON) to fix/flag borderline cases instead of dropping.
- Summary metrics: total rows, valid rows, rejected rows, valid rate %.
- Download results as:
  - `cleaned_emails.csv`
  - `rejected_emails.csv` (with reasons & suggested domains)
  - Combined `.zip` containing both files.
- Fully in-memory processing for privacy — no data stored.

### 📄 Documentation
- Added detailed docs in `docs/` covering:
  - Product overview & user stories
  - Architecture & data flow
  - Validation rules
  - Edge cases
  - UI/UX flow
  - File formats
  - Performance targets
  - Security & privacy
  - Config & resources
  - Error handling
  - Testing plan
  - Observability
  - Deployment

### 🛠 Technical
- Core modules:  
  - `elc/cleaning.py` – normalization & deduplication  
  - `elc/validate.py` – syntax, disposable, MX checks  
  - `elc/suggest.py` – domain typo suggestions  
  - `elc/io_utils.py` – CSV read/write helpers  
  - `elc/metrics.py` – basic metrics  
- Streamlit frontend in `app/app.py` wired to core logic.
- Configurable constants for MX DNS timeout, Levenshtein threshold, file size limit.
- Domain lists in `elc/data/`.

---

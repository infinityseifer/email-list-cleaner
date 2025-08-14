# Product Overview

This file contains detailed product goals, non-goals, and user stories for the MVP.


🎯 What It Does (MVP)  
[**Open the MVP App**](https://email-list-cleaner-v1-0-0-mvp.streamlit.app/) | [**Try v1.1 Preview**](https://email-list-cleaner-v1-1-0.streamlit.app/)

New in PR2 — Column Mapping Presets (v1.2)

Presets in Sidebar
Added a “Column Mapping Preset” selector in the sidebar with predefined mappings:

Generic CSV (no default)

Mailchimp Export → Email Address

HubSpot Export → Email

Auto-Selection Logic

If the preset’s email column exists in the uploaded CSV, it is auto-selected.

If the user has previously selected an email column during this session, that choice takes precedence over the preset.

If neither applies, the first column is selected by default.

User Session Memory

The app remembers the last chosen email column for the duration of the Streamlit session.

No Breaking Changes

All existing cleaning, validation, MX checks, and export features from v1.1 remain unchanged.

📌 Example Workflow with Presets

Upload CSV
The app previews the first 10 rows.

Select Preset
If “Mailchimp Export” is chosen and the file has an Email Address column, it’s preselected automatically.

Confirm or Change Email Column
The user can override the auto-selection at any time.

Run Cleaning & Validation
The pipeline executes with the chosen column.

📜 Changelog
PR2 — v1.2.0

Date: YYYY-MM-DD
Summary: Introduced Column Mapping Presets feature to streamline email column selection for known CSV formats.

Added presets: Generic CSV, Mailchimp Export, HubSpot Export.

Implemented auto-selection logic with session memory.

Maintained backward compatibility with v1.1 cleaning/validation features.

PR1 — v1.1.0

Date: YYYY-MM-DD
Summary: Introduced insights and MX timeout controls.

Added “Why rejected?” insights table and CSV export.

Added MX DNS record verification toggle.

Adjustable MX timeout slider.

Improved in-memory processing performance.
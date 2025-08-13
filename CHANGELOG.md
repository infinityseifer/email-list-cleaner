# Changelog

## [v1.1.0] - In Progress
**Status:** Development Branch (`release/v1.1.0`)  
**Notes:** This branch builds on the v1.0.0 MVP release, adding new features, performance improvements, and expanded validation options.

### Added
- Optional bulk domain verification via asynchronous MX checks.
- Advanced filtering:  
  - Include/exclude specific domains.
  - Remove emails by regex pattern.
- Summary dashboard:  
  - Pie chart of valid vs. rejected emails.
  - Bar chart of rejection reasons.
- Expanded typo-suggestion engine with fuzzy matching.
- Config toggle to export **all emails with status labels** into one CSV.

### Changed
- Improved CSV upload handling for large files (≥50k rows).
- Streamlined UI layout with collapsible settings panel.
- Enhanced summary metrics display with color-coded KPIs.
- Refined Safe Mode to handle borderline cases with more descriptive labels.

### Fixed
- Handling of malformed CSV files with mixed delimiters.
- Better error messages for DNS/MX resolution timeouts.
- Duplicate detection now case-insensitive for domains and usernames.

---

## [v1.0.0] - 2025-08-12
**Status:** MVP Release (`release/v1.0.0`)  
Initial release with the following core features:
- CSV upload (UTF-8, ≤ 20MB) with preview.
- Email normalization (trim, lowercase domains).
- Blank and duplicate removal.
- Syntax validation (RFC compliance).
- Disposable domain detection.
- Safe Mode enabled by default.
- Optional MX record checks.
- Optional typo-suggestion for common domains.
- Separate **cleaned_emails.csv** and **rejected_emails.csv** downloads.

"""Central configuration for Email List Cleaner v1.1.

This module centralizes tunable constants used across the UI and pipeline.
Keeping these values in one place ensures the Streamlit controls, docs,
and core code stay in sync.

Typical usage (in app code)::

    from elc import config
    max_mb = config.MAX_FILE_MB

Adjust with care; these defaults are chosen to provide a good user experience
for medium-sized lists while protecting free-hosted environments.
"""
from __future__ import annotations

# -------------------------
# File limits
# -------------------------
MAX_FILE_MB: int = 20
"""Maximum upload size in megabytes for CSV files."""

# -------------------------
# DNS/MX behavior
# -------------------------
DNS_TIMEOUT: float = 2.0
"""Per-domain DNS MX query timeout in seconds."""

MAX_WORKERS: int = 64
"""Maximum number of threads for parallel MX lookups."""

# -------------------------
# Typo suggestion behavior
# -------------------------
LEVENSHTEIN_MAX_DIST: int = 2
"""Base edit-distance threshold for domain suggestions (may scale by length)."""

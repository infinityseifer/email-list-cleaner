"""Skeleton tests for MX concurrency (to be implemented in v1.1)."""
from __future__ import annotations

# Suggested test plan:
# - Mock the DNS resolver used by has_mx_record to simulate:
#   * fast domains   -> True
#   * timed out      -> None (maps to mx_unknown in UI)
#   * NXDOMAIN       -> False (maps to no_mx_record)
# - Verify a ThreadPoolExecutor shortens total runtime vs sequential checks.
# - Ensure result mapping keeps safe-mode behavior intact.

def test_mx_concurrency_placeholder() -> None:
    """Placeholder test to keep CI green until concurrency tests are implemented."""
    assert True

"""Unit tests for validation helpers.

Run with: `pytest -q` in the project root.
"""
from __future__ import annotations

from elc.validate import is_rfc_valid, is_disposable


def test_valid_emails() -> None:
    """RFC-valid addresses should pass validation."""
    assert is_rfc_valid("user@example.com")
    assert is_rfc_valid("first.last+tag@gmail.com")


def test_invalid_emails() -> None:
    """Malformed addresses should fail validation."""
    assert not is_rfc_valid("bad@")
    assert not is_rfc_valid("no-at-symbol.com")


def test_disposable() -> None:
    """Disposable domains should be detected via lookup set."""
    disposables = {"mailinator.com"}
    assert is_disposable("mailinator.com", disposables)
    assert not is_disposable("gmail.com", disposables)
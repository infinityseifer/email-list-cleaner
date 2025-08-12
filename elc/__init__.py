"""Email List Cleaner package.

This package provides reusable functions for:
- Normalizing and deduplicating email addresses (`cleaning`)
- Validating email syntax and domains (`validate`)
- Suggesting domain corrections (`suggest`)
- Reading/writing CSV files (`io_utils`)
- Producing simple metrics (`metrics`)
"""

__all__ = [
    "cleaning",
    "validate",
    "suggest",
    "io_utils",
    "metrics",
]
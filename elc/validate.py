"""Validation utilities for email addresses and domains.

Includes RFC syntax validation, disposable domain checks, and (optional)
DNS MX record lookups to verify that a domain accepts mail.
"""
from __future__ import annotations

from email_validator import validate_email, EmailNotValidError
import dns.resolver


def is_rfc_valid(email: str) -> bool:
    """Return True if email passes RFC-compliant syntax checks.

    Args:
        email: The candidate email string.

    Returns:
        True if the email conforms to RFC syntax rules; False otherwise.
    """
    try:
        validate_email(email, allow_smtputf8=True, allow_empty_local=False)
        return True
    except EmailNotValidError:
        return False


def is_disposable(domain: str, disposable_set: set[str]) -> bool:
    """Check if a domain is known to be disposable/temporary.

    Args:
        domain: Domain portion of an email address.
        disposable_set: Set of disposable domains.

    Returns:
        True if the domain is in the disposable list; False otherwise.
    """
    return bool(domain) and domain in disposable_set


def has_mx_record(domain: str, timeout: float = 2.0) -> bool:
    """Check whether the domain has MX (mail server) DNS records.

    Args:
        domain: Domain to check.
        timeout: Seconds allowed for the DNS query.

    Returns:
        True if at least one MX record is found; False otherwise.
    """
    if not domain:
        return False
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=timeout)
        return len(answers) > 0
    except Exception:
        return False
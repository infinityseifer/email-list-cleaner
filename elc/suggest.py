"""Domain typo detection and suggestion helpers.

Provides explicit common fixes and a fuzzy-matching based suggestion
for mapping mistyped domains to common, legitimate providers.
"""
from __future__ import annotations

from rapidfuzz.distance import Levenshtein

# Explicit common misspellings mapped to intended domains
COMMON_FIXES = {
    "gmal.com": "gmail.com",
    "gmial.com": "gmail.com",
    "gmaill.com": "gmail.com",
    "yaho.com": "yahoo.com",
    "hotnail.com": "hotmail.com",
}


def suggest_domain(domain: str, common_domains: list[str], threshold: int = 2) -> str | None:
    """Suggest a likely domain correction using edit distance.

    Args:
        domain: The input (possibly mistyped) domain to evaluate.
        common_domains: List of common, legitimate domains to compare with.
        threshold: Maximum Levenshtein distance to allow for a suggestion.

    Returns:
        The best-matching domain within `threshold`, otherwise None.
    """
    if not domain:
        return None
    best: str | None = None
    best_dist: int = 10 ** 9
    for cd in common_domains:
        d = Levenshtein.distance(domain, cd)
        if d < best_dist:
            best, best_dist = cd, d
    return best if best_dist <= threshold else None
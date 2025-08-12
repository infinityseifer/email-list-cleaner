"""Update the disposable domain list (v1.1-ready).

This script merges multiple sources (local files or raw strings), normalizes,
de-duplicates, sorts, and writes to `elc/data/disposable_domains.txt`.

Network fetching is intentionally omitted for MVP friendliness. In v1.1,
you can extend `load_sources` to support URLs (e.g., with `requests`).

Usage:
    python -m scripts.update_blocklist --in extra1.txt --in extra2.txt --out elc/data/disposable_domains.txt
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence


def normalize_domain(s: str) -> str:
    """Normalize a candidate domain string.

    Strips whitespace, ignores comments/blank lines, and lowercases.
    Returns an empty string for lines that should be omitted.
    """
    s = (s or "").strip()
    if not s or s.startswith("#"):
        return ""
    return s.lower()


def load_sources(sources: Iterable[Path | str]) -> list[str]:
    """Load lines from a sequence of file paths or raw text blocks.

    Args:
        sources: Iterable of path-like or raw text strings.

    Returns:
        List of raw lines (unnormalized). Comments are preserved for now.
    """
    lines: list[str] = []
    for src in sources:
        p = Path(src)
        if p.exists() and p.is_file():
            lines.extend(p.read_text(encoding="utf-8").splitlines())
        else:
            lines.extend(str(src).splitlines())
    return lines


def merge_and_write(output_path: Path, sources: Sequence[Path | str]) -> int:
    """Merge input sources and write a normalized, sorted blocklist.

    Args:
        output_path: Destination file path (e.g., elc/data/disposable_domains.txt).
        sources: Iterable of files or raw text blocks to merge.

    Returns:
        Number of unique domains written.
    """
    raw_lines = load_sources(sources)
    domains = {normalize_domain(s) for s in raw_lines}
    domains.discard("")

    sorted_domains = sorted(domains)  # stable sort for clean diffs

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(sorted_domains) + "\n", encoding="utf-8")
    return len(sorted_domains)


def main() -> None:
    """CLI entrypoint for merging lists.

    Example:
        python -m scripts.update_blocklist \

            --in extra1.txt --in extra2.txt \

            --out elc/data/disposable_domains.txt
    """
    import argparse
    ap = argparse.ArgumentParser(description="Merge disposable domain lists")
    ap.add_argument("--in", dest="inputs", action="append", default=[], help="Input file or raw text")
    ap.add_argument("--out", dest="output", required=True, help="Output path for merged list")
    args = ap.parse_args()

    count = merge_and_write(Path(args.output), args.inputs)
    print(f"Wrote {count} unique domains to {args.output}")


if __name__ == "__main__":
    main()

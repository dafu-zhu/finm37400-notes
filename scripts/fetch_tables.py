"""One-shot scraper: read scripts/table_manifest.yml, fetch each unique
notebook URL once from Mark's site, extract the Nth <table>, write to
cached_tables/<figure_name>.html.

Idempotent — skips entries whose cached HTML is already present unless
--force is passed. Skips entries with kind: skip.
"""
from __future__ import annotations
import argparse
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

BASE = "https://markhendricks.github.io/finm-fixedincome/"
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "scripts" / "table_manifest.yml"
OUT_DIR = ROOT / "cached_tables"


def extract_table(html: str, index: int) -> str:
    """Return the 1-based index-th <table> as a string. Raises IndexError."""
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    if index < 1 or index > len(tables):
        raise IndexError(
            f"table_index {index} out of range (page has {len(tables)} tables)"
        )
    return str(tables[index - 1])


def fetch_page(url_rel: str) -> str:
    full = BASE + urllib.parse.quote(url_rel, safe="/.")
    with urllib.request.urlopen(full, timeout=30) as r:
        return r.read().decode("utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true",
                   help="Refetch and overwrite existing cached entries.")
    args = p.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}

    page_cache: dict[str, str] = {}
    n_written = n_skipped = n_errors = 0

    for fig_name, entry in sorted(manifest.items()):
        if entry.get("kind") == "skip":
            n_skipped += 1
            continue
        out = OUT_DIR / f"{fig_name}.html"
        if out.exists() and not args.force:
            n_skipped += 1
            continue
        url = entry["url"]
        idx = entry["table_index"]
        if url not in page_cache:
            print(f"  fetch {url}")
            page_cache[url] = fetch_page(url)
        try:
            html = extract_table(page_cache[url], idx)
        except IndexError as e:
            print(f"  ERROR {fig_name}: {e}", file=sys.stderr)
            n_errors += 1
            continue
        out.write_text(html, encoding="utf-8")
        print(f"  wrote cached_tables/{fig_name}.html  (table {idx})")
        n_written += 1

    print(f"done: {n_written} written, {n_skipped} skipped, {n_errors} errors")
    if n_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()

"""Tests for scripts/fetch_tables.py pure helpers.

Run from repo root: python -m pytest scripts/tests/test_fetch_tables.py -v
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fetch_tables  # noqa: E402


HTML_TWO_TABLES = """
<html><body>
<p>before</p>
<table id="t1"><tr><td>A</td></tr></table>
<p>middle</p>
<table id="t2"><tr><td>B</td></tr></table>
<p>after</p>
</body></html>
"""


def test_extract_table_returns_first():
    out = fetch_tables.extract_table(HTML_TWO_TABLES, 1)
    assert 'id="t1"' in out
    assert 'id="t2"' not in out


def test_extract_table_returns_second():
    out = fetch_tables.extract_table(HTML_TWO_TABLES, 2)
    assert 'id="t2"' in out
    assert 'id="t1"' not in out


def test_extract_table_raises_on_zero():
    with pytest.raises(IndexError):
        fetch_tables.extract_table(HTML_TWO_TABLES, 0)


def test_extract_table_raises_on_too_high():
    with pytest.raises(IndexError):
        fetch_tables.extract_table(HTML_TWO_TABLES, 3)


def test_extract_table_returns_str_not_bs_tag():
    out = fetch_tables.extract_table(HTML_TWO_TABLES, 1)
    assert isinstance(out, str)


def test_extract_table_empty_html_raises():
    with pytest.raises(IndexError):
        fetch_tables.extract_table("<html><body></body></html>", 1)

"""Unit tests for scripts/convert.py pure functions.

Run from repo root: python -m pytest scripts/tests/ -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import convert  # noqa: E402


def test_remove_checkpoint_blocks_strips_basic():
    src = "before\n\\begin{checkpoint}\nignored\n\\end{checkpoint}\nafter"
    assert convert.remove_checkpoint_blocks(src) == "before\n\nafter"


def test_remove_checkpoint_blocks_handles_multiple():
    src = (
        "a\n\\begin{checkpoint}x\\end{checkpoint}\nb\n"
        "\\begin{checkpoint}y\\end{checkpoint}\nc"
    )
    out = convert.remove_checkpoint_blocks(src)
    assert "checkpoint" not in out
    assert out.count("\n\n") >= 1


def test_remove_checkpoint_blocks_strips_nested_tikz():
    """A TikZ block inside a checkpoint must vanish with the checkpoint."""
    src = (
        "before\n\\begin{checkpoint}\n"
        "\\begin{tikzpicture}foo\\end{tikzpicture}\n"
        "\\end{checkpoint}\nafter"
    )
    out = convert.remove_checkpoint_blocks(src)
    assert "tikzpicture" not in out


def test_convert_color_blocks_keyblock():
    src = "\\begin{keyblock}\nbody\n\\end{keyblock}"
    out = convert.convert_color_blocks(src)
    assert ":::{.callout-important" in out
    assert "Key concept" in out
    assert out.endswith(":::")


def test_convert_color_blocks_all_four():
    src = "".join(
        f"\\begin{{{e}}}x\\end{{{e}}}\n"
        for e in ("keyblock", "exerciseblock", "noteblock", "tipblock")
    )
    out = convert.convert_color_blocks(src)
    for cls in ("important", "caution", "note", "tip"):
        assert f".callout-{cls}" in out


def test_replace_tikz_blocks_counts_and_substitutes():
    src = (
        "a \\begin{tikzpicture}p\\end{tikzpicture} b "
        "\\begin{tikzpicture}q\\end{tikzpicture} c"
    )
    out, n = convert.replace_tikz_blocks(src, lecture_num=8)
    assert n == 2
    assert "L8_tikz_1.png" in out
    assert "L8_tikz_2.png" in out
    assert "tikzpicture" not in out


def test_extract_part_title():
    src = "\\part*{Lecture 3: STIR Futures and SOFR}\n\\beginlecture{03}"
    n, title = convert.extract_part_title(src)
    assert n == 3
    assert title == "STIR Futures and SOFR"


def test_strip_lecture_macros_removes_known_commands():
    src = (
        "\\beginlecture{05}\n"
        "\\addcontentsline{toc}{part}{Lecture 5}\n"
        "x\\textperiodcentered{}y"
    )
    out = convert.strip_lecture_macros(src)
    assert "beginlecture" not in out
    assert "addcontentsline" not in out
    assert "x·y" in out


def test_wrap_with_yaml_includes_title_and_warning():
    out = convert.wrap_with_yaml("body", "Spot Curve", 1)
    assert out.startswith("---\n")
    assert 'title: "Lecture 1: Spot Curve"' in out
    assert "AUTO-GENERATED" in out
    assert "body" in out

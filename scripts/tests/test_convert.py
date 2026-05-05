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


def test_convert_color_blocks_inserts_sentinels():
    src = "\\begin{keyblock}\nbody\n\\end{keyblock}"
    out = convert.convert_color_blocks(src)
    assert convert.SENTINEL_OPEN["keyblock"] in out
    assert convert.SENTINEL_CLOSE in out
    assert "\\begin{keyblock}" not in out
    assert "\\end{keyblock}" not in out


def test_convert_color_blocks_all_four_envs_sentineled():
    src = "".join(
        f"\\begin{{{e}}}x\\end{{{e}}}\n"
        for e in ("keyblock", "exerciseblock", "noteblock", "tipblock")
    )
    out = convert.convert_color_blocks(src)
    for env in ("keyblock", "exerciseblock", "noteblock", "tipblock"):
        assert convert.SENTINEL_OPEN[env] in out
    assert out.count(convert.SENTINEL_CLOSE) == 4


def test_restore_callout_sentinels_keyblock():
    src = (
        "before\n" + convert.SENTINEL_OPEN["keyblock"] +
        "\nbody\n" + convert.SENTINEL_CLOSE + "\nafter"
    )
    out = convert.restore_callout_sentinels(src)
    assert ':::{.callout-important title="Key concept"}' in out
    assert "\n:::\n" in out
    assert "§§" not in out


def test_restore_callout_sentinels_all_four():
    src = "".join(
        convert.SENTINEL_OPEN[e] + "x" + convert.SENTINEL_CLOSE
        for e in ("keyblock", "exerciseblock", "noteblock", "tipblock")
    )
    out = convert.restore_callout_sentinels(src)
    for cls, title in [
        ("important", "Key concept"),
        ("caution", "Exercise"),
        ("note", "Note"),
        ("tip", "Filling the gap"),
    ]:
        assert f':::{{.callout-{cls} title="{title}"}}' in out
    assert out.count(":::") == 8  # 4 opens + 4 closes
    assert "§§" not in out


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


def test_clean_pandoc_output_rewrites_figure_paths():
    md = "Text\n![](figures/foo.png)\nmore\n![alt](figures/bar.png)\n"
    out = convert.clean_pandoc_output(md)
    assert "../figures/foo.png" in out
    assert "../figures/bar.png" in out
    assert "(figures/" not in out  # nothing left without ../


def test_clean_pandoc_output_preserves_already_relative_paths():
    md = "![](../figures/L8_tikz_1.png)"
    out = convert.clean_pandoc_output(md)
    assert out.count("../figures/") == 1   # not double-prefixed
    assert "../../figures/" not in out


def test_clean_pandoc_output_unescapes_underscores_in_image_paths():
    md = "![](../figures/L1\\_1\\_compounding.png)"
    out = convert.clean_pandoc_output(md)
    assert "../figures/L1_1_compounding.png" in out


def test_replace_figures_with_cached_tables_swaps_when_cached(tmp_path, monkeypatch):
    cache = tmp_path / "cached_tables"
    cache.mkdir()
    (cache / "L1_1_c02_load_quotes.html").write_text(
        "<table><tr><td>x</td></tr></table>", encoding="utf-8"
    )
    monkeypatch.setattr(convert, "CACHE_DIR", cache)
    md = "before\n![](../figures/L1_1_c02_load_quotes.png)\nafter"
    out = convert.replace_figures_with_cached_tables(md)
    assert "```{=html}" in out
    assert '<div class="table-scroll">' in out
    assert "<table>" in out
    assert "L1_1_c02_load_quotes.png" not in out


def test_replace_figures_with_cached_tables_leaves_uncached_alone(tmp_path, monkeypatch):
    monkeypatch.setattr(convert, "CACHE_DIR", tmp_path / "empty")
    md = "![](../figures/L1_1_c50_ols.png)"
    out = convert.replace_figures_with_cached_tables(md)
    assert out == md

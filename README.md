# FINM 37400: Fixed Income — Lecture Notes

Public site: <https://dafu-zhu.github.io/finm37400-notes/>

Source notes (LaTeX): `D:/GitHub/good-student-note/notes/finm37400`.

## Local preview

```bash
quarto preview
```

## Regenerate from source

When source `.tex` changes upstream:

```bash
# 1. Snapshot the latest source files
cp ../good-student-note/notes/finm37400/src/*.tex source-tex/
cp ../good-student-note/notes/finm37400/src/*.sty source-tex/
cp ../good-student-note/notes/finm37400/src/references.bib source-tex/
cp ../good-student-note/notes/finm37400/src/figures/*.png figures/

# 2. Re-render TikZ replacements (only needed if scripts changed)
python scripts/render_tikz.py

# 3. Convert .tex → .qmd
python scripts/convert.py

# 4. Preview, commit, push
quarto preview
```

## One-time GitHub Pages setup (after first push)

GitHub repo Settings → **Pages** → **Source: GitHub Actions**.
The `publish.yml` workflow handles builds from then on.

## Repo layout

See `docs/superpowers/specs/2026-05-05-finm37400-website-design.md`.

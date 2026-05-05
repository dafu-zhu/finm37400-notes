# FINM 37400 Notes Website — Design

**Date**: 2026-05-05
**Author**: Dafu Zhu (with Claude)
**Status**: Approved — ready for implementation planning

## Goal

Publish UChicago FINM 37400 (Fixed Income) lecture notes as a public,
math-rich, navigable static website on GitHub Pages. Source is the existing
LaTeX project at `D:\GitHub\good-student-note\notes\finm37400`. The site
must preserve all mathematical content, figures, and the pedagogical
structure of color-coded callouts, while replacing the print-format
`mdframed` blocks with web-native callout components.

## Non-goals

- No executable code blocks. The original `.tex` describes Jupyter cells
  but does not embed runnable code; the site mirrors that.
- No multi-course portal. This repo is FINM 37400 only; future courses
  get their own repos.
- No PDF generation from this repo. The PDF lives in the source repo
  (`good-student-note`) and is the canonical print artifact.
- No automated re-conversion in CI. `.qmd` files are committed source
  artifacts; conversion is a deliberate developer action.

## Source inventory

- `notes/finm37400/src/lec01.tex` … `lec08.tex` — eight lecture files,
  ~9.4k lines total.
- `notes/finm37400/src/SimpleArticle.sty` — shared preamble (math macros,
  theorem envs, 5 `mdframed` color blocks).
- `notes/finm37400/src/main.tex` — top-level `\include` driver.
- `notes/finm37400/src/figures/*.png` — 56 figure images.
- `notes/finm37400/src/references.bib` — bibliography.
- `C:/Users/dafuz/Downloads/finm37400_learning_map.html` — self-contained
  interactive chapter dependency map (custom CSS, dark-mode aware,
  hover-to-trace dependency arrows via SVG/JS).

Counts:
- TikZ blocks: 4 (all in lec08; lec07's only TikZ block is inside a
  `checkpoint` and disappears with it).
- `\begin{checkpoint}` blocks: 48 — dropped entirely.
- Other color blocks: ~270 across `keyblock`, `exerciseblock`,
  `noteblock`, `tipblock` — converted to Quarto callouts.

## Toolchain

- **Quarto** (pinned at 1.5.57) — site generator, math rendering,
  callouts, citations, theorem cross-references.
- **Pandoc 3.9** — already installed; bundled inside Quarto on CI.
- **Python 3.11** + matplotlib + numpy — TikZ replacement scripts and
  conversion driver.
- **GitHub Actions** — `quarto-actions/setup`, `actions/setup-python`,
  `actions/upload-pages-artifact`, `actions/deploy-pages`.
- **gh CLI** — repo creation (already authed as `dafu-zhu`).

## Color block mapping

Five LaTeX `mdframed` blocks → four Quarto callouts; one dropped:

| LaTeX block       | Quarto callout                              | Title              | Original semantic    |
|-------------------|---------------------------------------------|--------------------|----------------------|
| `keyblock`        | `:::{.callout-important}`                   | "Key concept"      | Cell text + summary  |
| `exerciseblock`   | `:::{.callout-caution}`                     | "Exercise"         | Homework / problem   |
| `noteblock`       | `:::{.callout-note}`                        | "Note"             | Side note            |
| `tipblock`        | `:::{.callout-tip}`                         | "Filling the gap"  | Lecturer elaboration |
| `checkpoint`      | (dropped — content removed)                 | —                  | Self-quiz            |

Callout style: Quarto `default` (full-bleed background, icon + label
header, rounded corners). `custom.scss` slightly de-saturates backgrounds
and tightens label typography so long pages don't feel boxy.

## Repo layout

```
D:\GitHub\finm37400-notes\
├── _quarto.yml                       # site config
├── index.qmd                         # homepage with embedded map + lecture index
├── lectures\
│   └── lec01.qmd ... lec08.qmd       # generated from source-tex/
├── figures\                          # 56 PNGs from source + 5 generated TikZ replacements
├── assets\
│   └── finm37400_learning_map.html   # iframe-embedded on index
├── styles\
│   └── custom.scss                   # theme tweaks
├── source-tex\                       # snapshot of original .tex (read-only reference)
│   ├── lec01.tex ... lec08.tex
│   ├── SimpleArticle.sty
│   ├── main.tex
│   └── references.bib
├── scripts\
│   ├── convert.py                    # tex → qmd
│   ├── render_tikz.py                # driver for TikZ replacements
│   └── tikz_replacements\
│       ├── lec08_01.py               # vol smile (3 curves)
│       ├── lec08_02.py               # 1-period stock binomial
│       ├── lec08_03.py               # 1-period rate binomial
│       └── lec08_04.py               # multiperiod CRR tree (depth 3)
├── references.bib                    # used by Quarto citeproc (canonical for site; snapshot copy also in source-tex/)
├── docs\superpowers\specs\
│   └── 2026-05-05-finm37400-website-design.md  # this file
├── .github\workflows\
│   └── publish.yml                   # GH Pages deploy
├── .gitignore                        # _site/ .quarto/ __pycache__/
└── README.md
```

## Conversion pipeline

`scripts/convert.py` runs three stages per lecture:

### Stage 1 — Pre-pass (regex on raw .tex)

- Remove `\begin{checkpoint}…\end{checkpoint}` blocks (multiline,
  non-greedy match).
- Replace each color block with Quarto fenced div syntax:
  - `\begin{keyblock}…\end{keyblock}` → `:::{.callout-important title="Key concept"}\n…\n:::`
  - `\begin{exerciseblock}` → `:::{.callout-caution title="Exercise"}`
  - `\begin{noteblock}`     → `:::{.callout-note title="Note"}`
  - `\begin{tipblock}`      → `:::{.callout-tip title="Filling the gap"}`
- For each `\begin{tikzpicture}…\end{tikzpicture}` block (in document
  order within a file): replace with `![](../figures/L{N}_tikz_{i}.png)`
  where `N` is the lecture number and `i` is the 1-indexed occurrence.
  If the corresponding `scripts/tikz_replacements/lec{NN}_{ii}.py` is
  missing, write a stub file embedding the original TikZ source as a
  comment and emit a build warning.
- Strip `\beginlecture{NN}` (Quarto numbers per page).
- Strip `\addcontentsline{toc}{part}{…}`.
- Extract `\part*{Lecture N: <title>}` → store for Stage 4 YAML;
  remove from body.
- Replace `\textperiodcentered{}` → U+00B7 middle dot.

### Stage 2 — Pandoc conversion

```
pandoc <input>.tex -f latex -t markdown --wrap=preserve --katex
```

Pandoc handles: `\section`, `\subsection`, `\subsubsection` →
Markdown headings; `\textbf` → `**`; `\emph` → `*`; `\texttt` →
backticks; `\includegraphics` → `![](path)`; inline `$…$` and display
`\[…\]` math passed through unchanged for KaTeX; theorem environments
(`theorem`, `lemma`, `proposition`, `corollary`, `definition`,
`example`, `remark`) → `:::{.theorem}` divs with auto-numbered titles;
`\cite{…}` / `\citet{…}` / `\citep{…}` → Quarto citation syntax
(`@key`, `[@key]`).

### Stage 3 — Post-pass

- Idempotent cleanup of pandoc artifacts (escaped underscores in URLs,
  smart-quote noise inside math, etc.).
- Verify all custom math macros from `SimpleArticle.sty` are declared
  in the `_quarto.yml` KaTeX `macros` block (warn on first unknown).

### Stage 4 — Wrap with YAML

```yaml
---
title: "Lecture N: <extracted title>"
number-sections: true
---
```

Write to `lectures/lec0N.qmd`.

### Idempotence

`convert.py` overwrites `lectures/*.qmd` from `source-tex/*.tex` on
every run. No manual edits to generated `.qmd` files (enforced by
header comment: `<!-- AUTO-GENERATED by scripts/convert.py — do not edit. -->`).

## TikZ replacements

Four matplotlib scripts in `scripts/tikz_replacements/`. Each:
- Imports `matplotlib.pyplot`, sets a sensible figsize.
- Recreates the diagram from the original TikZ coordinates and labels.
- Uses LaTeX-rendered text via `text(usetex=False)` with `mathtext`
  fallback (so CI doesn't need a TeX install).
- Saves to `figures/L{N}_tikz_{i}.png` at 200 DPI.
- Is fully deterministic (no RNG, no time-dependent inputs).

`scripts/render_tikz.py` discovers and runs every `lec*_*.py` file in
`scripts/tikz_replacements/`. Idempotent.

## Math macros

`SimpleArticle.sty` defines ~30 custom macros (`\R`, `\E`, `\P`, `\cF`,
`\cN`, ..., `\Var`, `\Cov`, `\Tr`, `\rank`, `\norm`, `\inner`, `\set`,
`\dd`, `\dv`, `\pdv`, `\given`, `\iid`, `\indep`, etc.). All declared
in `_quarto.yml`'s KaTeX `macros` config so source `.qmd` math reads
identically to the source `.tex`.

`\bm{x}` (bold-math) → mapped to `\boldsymbol{x}` for KaTeX
compatibility.

Theorem-style commands stay as Quarto theorem divs and inherit
auto-numbering per page.

## Index page (`index.qmd`)

Sections:

1. **Title + subtitle + 2-paragraph intro** — what the course is, who
   the lecturer is, link to the source course site
   (markhendricks.github.io/finm-fixedincome).
2. **Chapter dependency map** — H2 heading + iframe embedding
   `assets/finm37400_learning_map.html` (width 100%, height 780px,
   `border:0`, `border-radius:8px`, `loading="lazy"`). Map's CSS is
   isolated by the iframe boundary so dark-mode handling stays
   independent.
3. **Lecture index table** — markdown table with lecture number, topic
   summary (extracted from source `\part*{…}`), link to each
   `lectures/lecNN.qmd`.
4. **How to read these notes** — short legend explaining the four
   callout colors, math rendering, code-cell references.
5. **Source & PDF** — links to GitHub repo and PDF location.

`toc: false` on this page (it's a landing page, not a reading page).

## Site theme

`_quarto.yml` highlights:

- `theme.light: [cosmo, styles/custom.scss]`
- `theme.dark: [darkly, styles/custom.scss]`
- `toc: true; toc-depth: 3; toc-location: right` on lecture pages.
- `number-sections: true`, per-page numbering.
- `code-copy: true`, `smooth-scroll: true`, `citations-hover: true`.
- `html-math-method.method: katex` with `macros` for SimpleArticle commands.
- `bibliography: references.bib` (Quarto's default citation style; CSL
  override deferred until needed).

`styles/custom.scss`:
- Body font stack `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` (matches the dependency-map font for visual continuity).
- Callout title size reduced ~10%; backgrounds de-saturated ~15%.
- Figure `max-width: 90%`, centered, with margin spacing.

Top navbar: Home, Lectures dropdown (1–8), GitHub icon (right).
Left sidebar: docked, lists all 8 lectures.

## Deployment

`.github/workflows/publish.yml`:

- Trigger: `push` on `main`, plus `workflow_dispatch`.
- Permissions: `contents: read`, `pages: write`, `id-token: write`.
- `concurrency: pages` (queue, don't cancel in-flight).
- Build job: checkout → setup Quarto 1.5.57 → setup Python 3.11 →
  `pip install matplotlib numpy` → `python scripts/render_tikz.py` →
  `quarto render` → upload `_site` artifact.
- Deploy job: `actions/deploy-pages@v4` on `github-pages` environment.

**One-time manual step after first push**: enable Pages in repo
Settings → Pages → Source = "GitHub Actions". Documented in `README.md`.

`convert.py` is **not** run in CI. Generated `.qmd` files are
committed; conversion is treated as source authoring, not build. This
keeps PRs reviewable (the actual published markdown appears in diffs)
and protects against pandoc version drift on the runner.

## Implementation phases

1. **Repo bootstrap** — install Quarto; create dir, `git init`,
   scaffold; write `_quarto.yml`, `.gitignore`, `README.md`,
   `styles/custom.scss`; `gh repo create dafu-zhu/finm37400-notes
   --public --source . --remote origin`; first push; manually enable
   Pages.
2. **Snapshot source** — copy `.tex`, `.sty`, `.bib`, `figures/*.png`
   from `good-student-note/notes/finm37400/src/` into `source-tex/`
   and `figures/`. Copy learning map to `assets/`.
3. **TikZ replacements** — write 4 matplotlib scripts + driver; verify
   each PNG visually against source PDF. Pre-pass note: checkpoint
   removal must run before TikZ scanning so the lec07 TikZ block (inside
   a checkpoint) is correctly elided.
4. **Build the converter** — write `scripts/convert.py`; run on all 8
   lectures → `lectures/*.qmd`; hand-author `index.qmd` (intro,
   iframe, lecture table populated from titles extracted by
   `convert.py`, legend); `quarto render` succeeds with no errors.
5. **Style + math polish** — `quarto preview`, click through every
   page, fix unknown KaTeX macros, tune SCSS, verify map iframe.
6. **Deploy** — add `publish.yml`, commit, push to main; watch CI;
   verify `https://dafu-zhu.github.io/finm37400-notes/` renders.

Estimated total: 3–4 hours focused work. Highest-risk: Phase 4
(custom converter); Phase 5 is the biggest variability (depends on
pandoc output quality on first pass).

## Verification per phase

- **P1**: `quarto --version` returns; repo visible on github.com.
- **P2**: `git status` shows expected untracked files; counts match
  source (8 .tex, 1 .sty, 1 .bib, 56 figures, 1 map).
- **P3**: each PNG opens, layout resembles source PDF page.
- **P4**: `quarto render` exits 0; spot-check 2–3 `.qmd` files for
  block conversion, math, figure paths.
- **P5**: every page renders cleanly in browser, no red KaTeX errors,
  callouts display with icons, map iframe shows hover behavior.
- **P6**: deployed URL loads; cross-page links work; math + map
  function as in local preview.

## Risk register

| Risk                                          | Likelihood | Mitigation                                                                 |
|-----------------------------------------------|------------|----------------------------------------------------------------------------|
| Custom macro KaTeX miss                       | Medium     | Declare all in `_quarto.yml`; iterate during P5.                           |
| Pandoc mangles a specific construct           | Low-Med    | Edit the snapshot `.tex` in `source-tex/` to use a friendlier construct, then re-run `convert.py`. Generated `.qmd` stays auto-only. |
| TikZ replacement looks visually different     | Medium     | Manual visual review against source PDF; iterate.                          |
| Map iframe height awkward at narrow viewports | Low        | Tune in P5; consider responsive aspect-ratio container.                    |
| Pages not enabled, deploy fails               | Low        | Documented one-time manual step in README.                                 |
| GH Actions Quarto version drift               | Low        | Pin `version: "1.5.57"` in workflow.                                       |

## Open questions

None at design time. Implementation may surface specific KaTeX macro
or pandoc-quirk decisions; resolve inline.

## Out of scope (potential follow-ups)

- Search (Quarto has built-in lunr.js search; can enable later if useful).
- Per-lecture PDF download links (Quarto can render `.qmd` to PDF; would
  duplicate the canonical PDF in `good-student-note`).
- Comments/discussion (Giscus, etc.).
- Cross-course navigation (would require multi-repo or moving to a
  monorepo site).

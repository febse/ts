# Repository Guide for Agents

A template repository for courses built with [Quarto](https://quarto.org/) books and
Jupyter notebooks, using [uv](https://docs.astral.sh/uv/) for Python dependency
management and GitHub Actions for CI build checks and GitHub Pages publishing.

## Using this template

1. Click "Use this template" on GitHub to create a new repository from this one.
2. Update `_variables.yml` with the new repository's URL and GitHub links.
3. Update `_quarto.yml` (title, author) and `pyproject.toml` / `environment.yml`
   (project name).
4. Use `uv run` to run Python commands.
5. Use the conda environment defined in `environment.yml` for running R
   notebooks (if any). The default is Python, R code must not be added unless explicitly requested by the user.
6. Add course notebooks/`.qmd` chapters and list them under `book.chapters` in
   `_quarto.yml`.
7. Run `uv sync` to install dependencies, then `uv run quarto render .` to build
   locally.

## Structure

- `index.qmd` — book landing page.
- `_quarto.yml` — Quarto book configuration.
- `_variables.yml` — reusable Quarto variables (site URL, repo links).
- `references.qmd` / `references.bib` — bibliography.
- `.github/workflows/pr-build.yml` — renders the book on every PR to `main` as a build check.
- `.github/workflows/publish.yml` — renders and publishes the book to GitHub Pages on push to `main`.
- `pyproject.toml` / `environment.yml` — Python dependencies (uv / conda).

## Project Rules

These rules define a lightweight standard for working in courses created from this template.

### 1) Scope and intent

- This repo is for course materials (Quarto + Jupyter notebooks).
- Keep changes educational, reproducible, and easy for students to follow.

### 2) File and naming conventions

- Prefix content files with a chapter number (e.g., `11-Continuous-Distributions.ipynb`).
- Use descriptive, stable file names; avoid renaming files unless necessary.
- Put generated outputs in `_site/`; do not hand-edit generated HTML.

### 3) Notebook authoring rules

- Use clear section headers and short explanatory markdown between code cells.
- Use display math with `$$ ... $$` for multi-line equations.
- Use `$` for inline math.
- Keep notation consistent within each notebook.
- Ensure examples are deterministic when possible (set random seeds in simulation cells).

### 4) Code style in notebooks

- Keep cells focused: one concept/step per cell.
- Avoid hidden state assumptions; cells should run top-to-bottom.
- Use readable variable names (no one-letter names except standard math indices).
- Add brief comments only when they improve learning clarity.

### 5) Mathematical content quality

- State assumptions explicitly before formulas/theorems.
- Distinguish theorem statement vs. proof vs. approximation notes.
- For approximations, include validity conditions.
- Prefer standard symbols/functions.

### 6) Quarto and rendering

- Keep `_quarto.yml` as source of truth for build configuration.
- Use markdown/MyST syntax compatible with Quarto.
- Verify rendering of math and theorem blocks before publishing.

### 7) Reproducibility and environment

- Use the project environment (`environment.yml` / `.venv`) when running notebooks.
- Add any new required dependency to the environment definition.
- Avoid OS-specific commands in notebook examples unless noted.

### 8) Contribution workflow

- Make minimal, targeted changes tied to one topic.
- Do not modify unrelated notebooks/content in the same change.
- Keep prose concise and pedagogically clear.
- Run/preview affected notebook(s) before finalizing edits.

### 9) Content safety checks before merge

- No broken LaTeX math blocks.
- No stale references to removed sections/files.
- No execution errors in modified notebook cells.
- No edits to generated artifacts except via normal render process.

### 10) Optional PR checklist

- [ ] Notebook runs top-to-bottom without errors.
- [ ] Math renders correctly in Quarto output.
- [ ] Theorem statements and proofs are clearly separated.
- [ ] Any approximation includes assumptions/conditions.
- [ ] No unrelated files were changed.

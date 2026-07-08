# Convert ts2025 to R, with Quarto/R CI (modeled on febse/stat)

## Context

This repo (`febse/ts2025`) is a Quarto book of Jupyter notebooks teaching time
series analysis, currently written entirely in Python (pandas, statsmodels,
arch, statsforecast, matplotlib/seaborn/plotly). The user wants the teaching
content converted to R, using the CI/tooling setup on `febse/stat`'s
`fix/notebook-cleanup` branch as a template — but adapted for a conda+R stack
instead of that repo's `uv`+Python stack, since this repo already carries a
partially-prepped `environment.yml` with R packages (tidyverse, fable,
fabletools, tsibble, forecast, tseries, urca, quantmod, irkernel) and an
R-oriented `.gitignore`, suggesting an R migration was already anticipated.

Confirmed with the user:
- Auxiliary Python-only scripts (`videos/*.py` Manim scenes,
  `sine_wave_circle_app.py` Dash app, `setup.py` QR helper) stay in Python —
  out of scope for conversion.
- GARCH notebook (`08-GARCH.ipynb`) will use **rugarch** (closest parity with
  Python's `arch`).
- Conversion cadence: convert **one flagship notebook first**
  (`05-ARMA-Fitting.ipynb`), stop and show it for review, then apply the same
  translation patterns to the rest without further per-notebook pauses.
- Conda env: consolidate onto **conda-forge** with version floors (drop exact
  `defaults`-channel build hashes and the `environment_win64.yml` /
  `environment_hist.yml` variants), dropping Python packages no longer needed
  once notebooks are R.

## Scope: files to convert

Book chapters (referenced in `_quarto.yml`):
`index.ipynb`, `01-Introduction.ipynb`, `02-Linear-Difference-Equations.ipynb`,
`03-Statistics-Review.ipynb`, `04-ARMA.ipynb`, `05-ARMA-Fitting.ipynb`,
`06-ARIMA-Forecasting.ipynb`, `07-Unit-Root-Tests.ipynb`, `08-GARCH.ipynb`,
`09-Seasonality.ipynb` (`references.qmd`/`Homework.qmd` have no code, leave
as-is; `lecture_problems.qmd` is already R).

Supplementary/class notebooks (used via direct Colab links, not in the
compiled book, still Python today — convert too since "all code" applies):
`00-ETS.ipynb`, `01-Introduction-Class.ipynb`, `01-A-Introduction-Class.ipynb`,
`02-Linear-Difference-Equations-Class.ipynb`, `04-ARMA-Class.ipynb`,
`04-A-Complex-Multiplication.ipynb`, `05-ARMA-Fitting-Class.ipynb`,
`basics/Complex-Numbers.ipynb`, `complex/fourier.ipynb`.

Left untouched: `videos/*.py`, `sine_wave_circle_app.py`, `setup.py`,
`arima.R` (standalone scratch file, not wired into the book),
`Homework.qmd`, `references.qmd`, `lecture_problems.qmd`, presentation
schedule/figures.

## Package mapping (Python → R)

| Python | R replacement |
|---|---|
| numpy / pandas | base R, tibble/dplyr |
| matplotlib / seaborn (static plots) | ggplot2 |
| plotly.graph_objects (interactive: 02, 04-A, 09) | plotly (R) — `plot_ly`/`add_trace`, keeps interactivity |
| statsmodels ARIMA / arma_generate_sample | `stats::arima.sim`, `stats::arima`/`forecast::Arima` |
| statsmodels plot_acf/plot_pacf | `forecast::ggAcf`/`ggPacf` (or `stats::acf`) |
| statsmodels adfuller / kpss | `urca::ur.df`, `tseries::adf.test`/`kpss.test` |
| statsmodels DeterministicProcess/Fourier | `forecast::fourier()` as regressors |
| arch.arch_model (GARCH) | `rugarch::ugarchspec` + `ugarchfit` |
| statsforecast (Naive) | `fable::NAIVE` over a `tsibble`, consistent with the already-installed tidyverts stack |
| yfinance | `quantmod::getSymbols` |
| IPython.display.Audio (09-Seasonality) | write a `.wav` via `tuneR` and embed with an HTML `<audio>` tag in the qmd/ipynb markdown |
| `!wget` shell cells | `download.file()` |

## Infrastructure changes

1. **`environment.yml`** — rebuild on `conda-forge`, keep `r-irkernel` (already
   present) plus the existing tidyverts/forecast/tseries/urca/quantmod stack,
   add `r-rugarch` and `r-plotly` and `r-tuner`. Drop Python packages no
   longer used by any notebook (pandas, statsmodels, arch, seaborn,
   statsforecast, scikit-learn stubs, yfinance, eurostatapiclient, openpyxl —
   none of these are used outside the notebooks being converted). Delete
   `environment_win64.yml` and `environment_hist.yml`.

2. **`pyproject.toml`** — trim to only what the retained Python scripts need:
   `manim`, `dash`, `plotly`, `numpy`, `qrcode`, `pyyaml`. Regenerate
   `uv.lock` isn't strictly needed since CI will use conda, not uv, for the
   book build — but keep `pyproject.toml` for local use of `videos/`/
   `sine_wave_circle_app.py`/`setup.py`.

3. **GitHub Actions** (mirroring `febse/stat`'s two-workflow pattern, swapping
   the Python/uv steps for conda/R):
   - `.github/workflows/pr-build.yml` (new): triggers on `pull_request` to
     `main`, sets up conda env from `environment.yml` via
     `conda-incubator/setup-miniconda@v3`, sets up Quarto
     (`quarto-dev/quarto-actions/setup@v2`), runs `quarto render .` as a
     build-only check (no deploy).
   - `.github/workflows/publish.yml` (rewrite existing): same conda/Quarto
     setup, `quarto render .`, then `actions/upload-pages-artifact@v3` +
     `actions/deploy-pages@v4` on push to `main`, as it does today.

4. **Pre-commit / git hygiene** (adopt from `febse/stat`):
   - `.pre-commit-config.yaml` with `nbstripout` (`--keep-output
     --extra-keys metadata.language_info`) so committed notebooks keep
     outputs but not volatile metadata.
   - `.gitattributes` with `*.ipynb filter=nbstripout` and `*.ipynb
     diff=ipynb`.

5. **`.vscode/extensions.json`** already recommends R extensions — no change
   needed. `.vscode/settings.json` cSpell word list will get updated if the
   typo scan turns up recurring domain terms worth whitelisting.

6. **`_quarto.yml`** — no structural change expected; execution engine for
   `.ipynb` with an R/IRkernel kernelspec is handled automatically by Quarto's
   Jupyter engine, so `execute: echo: false` stays valid.

## Colab compatibility pattern

For every converted notebook:
- Set `metadata.kernelspec` to `{"display_name": "R", "language": "R", "name":
  "ir"}` and `language_info.name` to `"R"`, so the existing "Open in Colab"
  badge provisions an R runtime.
- First code cell installs only the packages that notebook actually uses,
  e.g.:
  ```r
  required <- c("tidyverse", "forecast", "urca")
  missing <- required[!required %in% rownames(installed.packages())]
  if (length(missing)) install.packages(missing)
  invisible(lapply(required, library, character.only = TRUE))
  ```

## Conversion process

1. Convert `05-ARMA-Fitting.ipynb` first (ARIMA fitting, ACF/PACF, simulation
   — representative of the translation patterns needed elsewhere). Stop and
   present it for review before continuing.
2. On approval, apply the same patterns across the remaining chapters in
   book order (01 → 09), then the supplementary/class notebooks and
   `basics/complex` notebooks, then `index.ipynb`.
3. Track progress per-notebook with TaskCreate/TaskUpdate so partial progress
   survives context compaction.
4. After all notebooks are converted, do a separate pass scanning markdown
   prose (in the converted notebooks and the `.qmd` files) for typos and
   possible content/factual errors, and present the list of proposed fixes
   for confirmation before applying them (per the user's request) — this is
   independent of the code conversion itself.

## Verification

- `quarto render .` locally (quarto 1.9.37, R 4.5.2, and conda are already
  available in this environment) after the flagship notebook and again after
  the full conversion, to confirm the book builds and each R chunk executes
  without errors.
- Spot-check that interactive plotly outputs and the GARCH/ARIMA model
  outputs render sensibly (not just "no error"), since these are the highest
  fidelity-risk conversions.
- Once GitHub Actions files are in place, open a PR to confirm `pr-build.yml`
  runs a clean build (no deploy) before merging to `main`, where
  `publish.yml` deploys to Pages.

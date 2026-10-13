# econ2025

## Pre-commit

Install the project dependencies and configure Git to use the repository hook:

```bash
uv sync
git config core.hooksPath .githooks
```

The hook removes machine-specific notebook metadata, regenerates the stripped class notebooks, and stages both updates with the commit.

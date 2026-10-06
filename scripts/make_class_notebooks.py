"""Create stripped class versions of all notebooks in the root folder and of
the notebooks listed in _quarto.yml.

Only code cells whose first line starts with ``#ex-class``, the headings
(titles) and the ``:::{.ex-class}`` fenced divs of markdown cells are kept. The results are
written to ./class under the original file names. Relative figure paths are
replaced by raw URLs on the main branch of the repository in _variables.yml.
"""
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "class"

OPEN_DIV = re.compile(r"^\s*:{3,}\s*\{.*\}\s*$|^\s*:{3,}\s*\S+\s*$")
CLOSE_DIV = re.compile(r"^\s*:{3,}\s*$")
EX_CLASS_DIV = re.compile(r"^\s*:{3,}\s*\{[^}]*\.ex-class[^}]*\}\s*$")


IMAGE = re.compile(r"(!\[[^\]]*\]\()([^)\s]+)")
HTML_SRC = re.compile(r"""(<img\b[^>]*?\bsrc=["'])([^"']+)""")
SCHEME = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//|#)")


def raw_base_url():
    variables = yaml.safe_load((ROOT / "_variables.yml").read_text(encoding="utf-8"))
    return variables["github"].rstrip("/") + "/raw/main/"


def absolutize_figures(text, base_url, notebook_dir):
    def repl(match):
        target = match.group(2)
        if SCHEME.match(target):
            return match.group(0)
        rel = (notebook_dir / target).resolve().relative_to(ROOT).as_posix()
        return match.group(1) + base_url + rel

    return HTML_SRC.sub(repl, IMAGE.sub(repl, text))


def source_text(cell):
    src = cell["source"]
    return "".join(src) if isinstance(src, list) else src


def to_source_lines(text):
    lines = text.splitlines(keepends=True)
    return lines


HEADING = re.compile(r"^#{1,6}\s+\S")
FENCE = re.compile(r"^\s*(```|~~~)")


def extract_kept_parts(text):
    """Return headings and ex-class fenced divs (with fences) in document order."""
    parts, current, depth, in_code, other = [], None, 0, False, 0
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        if current is None:
            if FENCE.match(stripped):
                in_code = not in_code
            elif in_code:
                continue
            elif EX_CLASS_DIV.match(stripped):
                current, depth = [line], 1
            elif CLOSE_DIV.match(stripped):
                other = max(other - 1, 0)
            elif OPEN_DIV.match(stripped):
                other += 1
            elif HEADING.match(stripped) and other == 0:
                parts.append(stripped + "\n")
            continue
        current.append(line)
        if CLOSE_DIV.match(stripped):
            depth -= 1
            if depth == 0:
                parts.append("".join(current).rstrip("\n") + "\n")
                current = None
        elif OPEN_DIV.match(stripped):
            depth += 1
    return parts


def is_ex_class_code(cell):
    first = source_text(cell).lstrip().split("\n", 1)[0]
    return re.match(r"#\s*ex-class\b", first) is not None


def strip_notebook(nb, base_url, notebook_dir):
    cells = []
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            if is_ex_class_code(cell):
                cells.append(cell)
        elif cell["cell_type"] == "markdown":
            blocks = extract_kept_parts(source_text(cell))
            if blocks:
                cell = dict(cell)
                text = absolutize_figures("\n".join(blocks).rstrip("\n"), base_url, notebook_dir)
                cell["source"] = to_source_lines(text)
                cells.append(cell)
    return {**nb, "cells": cells}


def notebooks_from_quarto():
    config = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf-8"))
    chapters = config.get("book", {}).get("chapters", [])

    def walk(items):
        for item in items:
            if isinstance(item, str):
                yield item
            elif isinstance(item, dict):
                if "file" in item:
                    yield item["file"]
                yield from walk(item.get("chapters", []))

    return [ROOT / p for p in walk(chapters) if p.endswith(".ipynb")]


def all_notebooks():
    found = {p.resolve() for p in ROOT.glob("*.ipynb")}
    found.update(p.resolve() for p in notebooks_from_quarto())
    return sorted(found)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    base_url = raw_base_url()
    for path in all_notebooks():
        nb = json.loads(path.read_text(encoding="utf-8"))
        stripped = strip_notebook(nb, base_url, path.parent)
        out = OUT_DIR / path.name
        out.write_text(json.dumps(stripped, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{path.name}: kept {len(stripped['cells'])} of {len(nb['cells'])} cells -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

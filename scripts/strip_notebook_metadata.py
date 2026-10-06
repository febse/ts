"""Strip execution counters and machine-specific metadata from notebooks in place."""
import json
import sys

# Notebook-level metadata that varies between machines (kernelspec is kept).
NB_META_DROP = {"widgets", "vscode", "colab"}
LANG_INFO_DROP = {"version", "file_extension", "mimetype", "pygments_lexer", "codemirror_mode", "nbconvert_exporter"}
# Cell-level metadata written by Jupyter/VS Code during execution.
CELL_META_DROP = {"execution", "collapsed", "scrolled", "ExecuteTime", "vscode", "papermill", "tags_runtime"}


def clean(nb):
    meta = nb.get("metadata", {})
    for key in NB_META_DROP:
        meta.pop(key, None)
    lang = meta.get("language_info")
    if lang:
        for key in LANG_INFO_DROP:
            lang.pop(key, None)
    kernelspec = meta.get("kernelspec")
    if kernelspec:
        kernelspec.pop("display_name", None)

    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            cell["execution_count"] = None
            for out in cell.get("outputs", []):
                if "execution_count" in out:
                    out["execution_count"] = None
        for key in CELL_META_DROP:
            cell.get("metadata", {}).pop(key, None)
    return nb


def main(paths):
    for path in paths:
        with open(path, encoding="utf-8") as f:
            original = f.read()
        nb = clean(json.loads(original))
        result = json.dumps(nb, indent=1, ensure_ascii=False) + "\n"
        if result != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"stripped {path}")


if __name__ == "__main__":
    main(sys.argv[1:])

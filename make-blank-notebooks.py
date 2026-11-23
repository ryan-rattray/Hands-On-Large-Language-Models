"""
Make blank type-in copies of the Hands-On LLMs chapter notebooks.

Run this from the repo root (the folder containing chapter01 ... chapter12):

    python make-blank-notebooks.py

For every chapter notebook it creates a sibling file named
"<original name> - blank.ipynb" where:

  - Markdown cells are kept as-is (they are the lesson prompts).
  - Install / shell setup code cells are kept as-is
    (a cell counts as setup if it contains "pip install" or its first
    real line starts with "!").
  - Every other code cell is emptied (source cleared, outputs cleared),
    ready for you to type into.

Originals are never modified. Re-running is safe: blank copies are
skipped, so fresh originals pulled later can be blanked the same way.

Uses only the Python standard library.
"""

import json
from pathlib import Path

BLANK_SUFFIX = " - blank"


def is_setup_cell(source_text: str) -> bool:
    """True for install / shell setup cells, which stay untouched."""
    if "pip install" in source_text:
        return True
    for line in source_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        return stripped.startswith("!")
    return False


def blank_notebook(path: Path) -> Path:
    with path.open("r", encoding="utf-8") as f:
        nb = json.load(f)

    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source_text = "".join(cell.get("source", []))
        if not source_text.strip():
            continue
        if is_setup_cell(source_text):
            continue
        cell["source"] = []
        cell["outputs"] = []
        cell["execution_count"] = None

    out_path = path.with_name(path.stem + BLANK_SUFFIX + path.suffix)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    return out_path


def main() -> None:
    root = Path(__file__).resolve().parent
    made, skipped = 0, 0
    for nb_path in sorted(root.rglob("*.ipynb")):
        if ".venv" in nb_path.parts or ".git" in nb_path.parts:
            continue
        if nb_path.stem.endswith(BLANK_SUFFIX):
            skipped += 1
            continue
        out = blank_notebook(nb_path)
        made += 1
        print(f"blanked: {out.relative_to(root)}")
    print(f"\nDone. {made} blank copies created, {skipped} already blank.")


if __name__ == "__main__":
    main()

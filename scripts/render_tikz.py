"""Run all matplotlib TikZ replacement scripts.

Discovers every scripts/tikz_replacements/lec*_*.py and calls its render()
function. Idempotent.
"""
import importlib
import sys
from pathlib import Path

REPL_DIR = Path(__file__).resolve().parent / "tikz_replacements"

def main():
    sys.path.insert(0, str(REPL_DIR))
    scripts = sorted(REPL_DIR.glob("lec*_*.py"))
    if not scripts:
        print("no tikz replacement scripts found", file=sys.stderr)
        sys.exit(1)
    for path in scripts:
        mod_name = path.stem
        print(f"render {mod_name}")
        mod = importlib.import_module(mod_name)
        mod.render()
    print(f"done: {len(scripts)} scripts")

if __name__ == "__main__":
    main()

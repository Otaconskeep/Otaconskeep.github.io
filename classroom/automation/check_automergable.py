#!/usr/bin/env python3
"""CLI: exit 0 if changed paths are auto-merge eligible; else exit 1."""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

# Import module file directly to avoid lib/__init__.py heavy deps (filelock, etc.).
_MOD = Path(__file__).resolve().parent / "lib" / "automergable_paths.py"
_spec = importlib.util.spec_from_file_location("automergable_paths", _MOD)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["automergable_paths"] = _mod
assert _spec.loader is not None
_spec.loader.exec_module(_mod)
evaluate_paths = _mod.evaluate_paths


def changed_files(base: str, head: str) -> list[str]:
    out = subprocess.check_output(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        text=True,
    )
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--paths-file", help="Optional file listing paths (one per line)")
    args = ap.parse_args()
    if args.paths_file:
        paths = [ln.strip() for ln in Path(args.paths_file).read_text().splitlines() if ln.strip()]
    else:
        paths = changed_files(args.base, args.head)
    result = evaluate_paths(paths)
    payload = {
        "automergable": result.automergable,
        "allowed": result.allowed,
        "denied": result.denied,
        "reason": result.reason,
        "paths": paths,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(result.reason)
        if result.denied:
            print("denied:")
            for p in result.denied:
                print(f"  - {p}")
    return 0 if result.automergable else 1


if __name__ == "__main__":
    raise SystemExit(main())

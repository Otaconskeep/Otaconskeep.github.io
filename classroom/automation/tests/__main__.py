"""python -m tests entrypoint."""
from __future__ import annotations

from .run_tests import run_tests

if __name__ == "__main__":
    raise SystemExit(run_tests())

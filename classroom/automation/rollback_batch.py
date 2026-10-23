#!/usr/bin/env python3
"""Rollback helper for the latest automation batch (operator command).

Dry-run safe: operates on recorded known-good commit refs in state; does not force-push.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import load_config


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", help="publish/dry-run report JSON with known_good commit")
    ap.add_argument("--demonstrate-fixture", action="store_true")
    args = ap.parse_args()
    cfg = load_config()

    if args.demonstrate_fixture:
        # Disposable fixture rollback demo — does not touch classroom pack
        demo = Path("/tmp/otaconskeep-classroom-dryrun/rollback_demo")
        demo.mkdir(parents=True, exist_ok=True)
        good = demo / "good.txt"
        bad = demo / "live.txt"
        good.write_text("GOOD\n", encoding="utf-8")
        bad.write_text("BAD\n", encoding="utf-8")
        # rollback
        bad.write_text(good.read_text(encoding="utf-8"), encoding="utf-8")
        assert bad.read_text(encoding="utf-8") == "GOOD\n"
        print(json.dumps({"ok": True, "demo": str(demo), "result": "restored_good"}))
        return 0

    if not args.report:
        print("Provide --report or --demonstrate-fixture", file=sys.stderr)
        return 2
    rep = json.loads(Path(args.report).read_text(encoding="utf-8"))
    commit = rep.get("known_good") or rep.get("known_good_commit")
    if not commit:
        print(json.dumps({"ok": False, "error": "no known_good in report; refuse guess"}))
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "action": "manual_revert_required",
                "known_good": commit,
                "commands": [
                    f"git -C {cfg.site_repo} revert --no-edit <bad_merge_commit>",
                    "Do not force-push. Open PR for revert if branch protections enabled.",
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

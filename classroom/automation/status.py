#!/usr/bin/env python3
"""Operator status CLI for classroom automation."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import load_config
from lib.curriculum import discover_existing_classes, load_manifest, next_core_batch, reconcile_manifest


def cmd_status(cfg) -> int:
    try:
        man = reconcile_manifest(cfg)
    except Exception:
        man = load_manifest(cfg)
    existing = discover_existing_classes(cfg.pack_dir)
    pending = next_core_batch(cfg)
    print(
        json.dumps(
            {
                "existing_count": len(existing),
                "existing_max": max(existing) if existing else None,
                "pending_next": pending,
                "core_complete": man.get("core_complete"),
                "dry_run": cfg.dry_run,
                "generator_backend": cfg.generator_backend,
                "state_dir": str(cfg.state_dir),
            },
            indent=2,
        )
    )
    return 0


def cmd_timers() -> int:
    for unit in (
        "otaconskeep-classroom-core-am.timer",
        "otaconskeep-classroom-core-late.timer",
        "otaconskeep-classroom-news.timer",
    ):
        p = subprocess.run(["systemctl", "is-enabled", unit], text=True, capture_output=True)
        q = subprocess.run(["systemctl", "is-active", unit], text=True, capture_output=True)
        print(f"{unit}: enabled={p.stdout.strip() or p.stderr.strip()} active={q.stdout.strip() or q.stderr.strip()}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="classroom-status")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("status")
    sp.add_parser("pending")
    sp.add_parser("timers")
    sp.add_parser("last")
    p_logs = sp.add_parser("logs")
    p_logs.add_argument("-n", type=int, default=50)
    sp.add_parser("pause")
    sp.add_parser("resume")
    args = ap.parse_args()
    cfg = load_config()
    # dry-run path fallbacks
    if not cfg.state_dir.exists():
        alt = Path("/tmp/otaconskeep-classroom-dryrun/state")
        if alt.exists():
            cfg.state_dir = alt

    if args.cmd == "status":
        return cmd_status(cfg)
    if args.cmd == "pending":
        print(json.dumps(next_core_batch(cfg), indent=2))
        return 0
    if args.cmd == "timers":
        return cmd_timers()
    if args.cmd == "last":
        man = load_manifest(cfg)
        print(json.dumps({"last_successful_batch": man.get("last_successful_batch"), "last_failed_batch": man.get("last_failed_batch")}, indent=2))
        return 0
    if args.cmd == "logs":
        log_dir = cfg.log_dir if cfg.log_dir.exists() else Path("/tmp/otaconskeep-classroom-dryrun/logs")
        files = sorted(log_dir.glob("*.jsonl"))[-1:]
        if not files:
            print("no logs")
            return 0
        lines = files[-1].read_text(encoding="utf-8").splitlines()[-args.n :]
        print("\n".join(lines))
        return 0
    if args.cmd == "pause":
        flag = cfg.state_dir / "PAUSED"
        cfg.state_dir.mkdir(parents=True, exist_ok=True)
        flag.write_text("paused\n", encoding="utf-8")
        print(f"wrote {flag}")
        return 0
    if args.cmd == "resume":
        flag = cfg.state_dir / "PAUSED"
        if flag.exists():
            flag.unlink()
        print("resumed")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

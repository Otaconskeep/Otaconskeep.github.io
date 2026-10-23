#!/usr/bin/env python3
"""Operator notifications — never log webhook URLs or secrets."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import load_config, redact_secrets


def notify_discord(webhook: str, content: str) -> None:
    if not webhook:
        raise RuntimeError("DISCORD_WEBHOOK_URL not set")
    data = json.dumps({"content": content[:1800]}).encode()
    req = urllib.request.Request(
        webhook,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "otaconskeep-classroom-notify/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        resp.read()


def notify_otaconskeep(script: Path, title: str, body: str) -> None:
    # Prefer writing a simple status file beside notifications for operators
    out = Path("/tmp/otaconskeep-classroom-notify.txt")
    out.write_text(redact_secrets(f"{title}\n\n{body}\n"), encoding="utf-8")
    print(f"wrote {out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = load_config()
    body = Path(args.body_file).read_text(encoding="utf-8")
    body = redact_secrets(body)
    if args.dry_run or cfg.dry_run:
        print(redact_secrets(f"[dry-run notify] {args.title}\n{body[:500]}"))
        return 0
    if cfg.notify_backend == "discord":
        notify_discord(cfg.discord_webhook, f"**{args.title}**\n{body}")
    else:
        notify_otaconskeep(cfg.notify_script or Path("."), args.title, body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

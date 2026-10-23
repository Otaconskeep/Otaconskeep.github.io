#!/usr/bin/env python3
"""Sync published classroom surfaces to Otaconskeep.github.io (public address).

Does not migrate domains or set redirects. Call after main-site content is approved.
Excludes classroom/automation runtime.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True, check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="/root/otaconskeep-site")
    ap.add_argument("--pages", default="/root/Otaconskeep.github.io")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    site = Path(args.site) / "classroom"
    pages = Path(args.pages) / "classroom"
    if not site.is_dir() or not pages.parent.is_dir():
        print("missing site or pages repo", file=sys.stderr)
        return 2
    cmd = [
        "rsync",
        "-a",
        "--delete",
        "--exclude",
        "automation/",
        "--exclude",
        "__pycache__/",
        "--exclude",
        "*.pyc",
        f"{site}/",
        f"{pages}/",
    ]
    if args.dry_run:
        cmd.insert(1, "-n")
        cmd.insert(2, "-i")
    print(" ".join(cmd))
    p = subprocess.run(cmd, text=True, capture_output=True)
    print(p.stdout[-2000:] if p.stdout else "")
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        return p.returncode
    if args.push and not args.dry_run:
        repo = Path(args.pages)
        run(["git", "add", "classroom"], cwd=repo)
        st = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(repo))
        if st.returncode == 0:
            print("nothing to commit")
            return 0
        run(
            [
                "git",
                "-c",
                "user.name=Antonio G. Garcia",
                "-c",
                "user.email=230031249+Otaconskeep@users.noreply.github.com",
                "commit",
                "-m",
                "Sync classroom from otaconskeep-site (deployment parity).",
            ],
            cwd=repo,
        )
        run(["git", "push", "origin", "HEAD"], cwd=repo)
        print("pushed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

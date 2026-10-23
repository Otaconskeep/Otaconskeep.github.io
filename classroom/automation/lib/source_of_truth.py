#!/usr/bin/env python3
"""Canonical source-of-truth: otaconskeep-site publishes; Classroom is one-way mirror."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
import os

CANONICAL = "otaconskeep-site"
# Prefer env / repo-relative discovery so CI runners work without /root paths.
SITE = Path(os.environ["CLASSROOM_SITE_REPO"]).resolve() if os.environ.get("CLASSROOM_SITE_REPO") else Path(__file__).resolve().parents[3]
MIRROR = Path(os.environ.get("CLASSROOM_UPSTREAM_REPO", "/root/Classroom"))



def _pack_fingerprint(root: Path) -> str:
    if (root / "classroom" / "pack" / "classes").is_dir():
        classes = root / "classroom" / "pack" / "classes"
    else:
        classes = root / "pack" / "classes"
    if not classes.is_dir():
        return "missing"
    h = hashlib.sha256()
    for p in sorted(classes.glob("*.md")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def _exists_dir(path: Path) -> bool:
    try:
        return path.is_dir()
    except OSError:
        return False


def detect_divergence() -> dict:
    """Fail closed if both sides have unpublished local pack edits vs each other without sync marker."""
    site_fp = _pack_fingerprint(SITE) if _exists_dir(SITE) else "missing"
    mirror_fp = _pack_fingerprint(MIRROR) if _exists_dir(MIRROR) else "missing"
    site_dirty = False
    mirror_dirty = False
    if _exists_dir(SITE) and (SITE / ".git").exists():
        site_dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain", "classroom/pack"],
                cwd=SITE,
                text=True,
                capture_output=True,
            ).stdout.strip()
        )
    if _exists_dir(MIRROR) and (MIRROR / ".git").exists():
        mirror_dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain", "pack"],
                cwd=MIRROR,
                text=True,
                capture_output=True,
            ).stdout.strip()
        )
    both_dirty = site_dirty and mirror_dirty
    status = "ok"
    if site_fp == "missing":
        status = "canonical_path_missing"
    elif mirror_fp == "missing":
        status = "mirror_absent_ok"  # CI / single-repo hosts
    elif site_fp != mirror_fp and both_dirty:
        status = "fail_closed_dual_write"
    elif site_fp != mirror_fp:
        status = "diverged_mirror_stale_or_ahead"
    return {
        "canonical": CANONICAL,
        "site_fingerprint": site_fp,
        "mirror_fingerprint": mirror_fp,
        "site_pack_dirty": site_dirty,
        "mirror_pack_dirty": mirror_dirty,
        "status": status,
        "sync_direction": "otaconskeep-site -> Classroom (via _gen_from_pack.sync_github only after approved publish)",
    }

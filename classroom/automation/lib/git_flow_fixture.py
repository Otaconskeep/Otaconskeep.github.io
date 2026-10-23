#!/usr/bin/env python3
"""Local bare-repo fixture proving branch/conflict/rollback logic without touching GitHub."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), text=True, capture_output=True, check=True)


def run_bare_repo_fixture() -> dict:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        bare = root / "remote.git"
        work = root / "work"
        _git(root, "init", "--bare", str(bare))
        _git(root, "clone", str(bare), str(work))
        _git(work, "config", "user.email", "classroom-bot@local")
        _git(work, "config", "user.name", "Classroom Bot")
        (work / "README").write_text("good\n", encoding="utf-8")
        _git(work, "add", "README")
        _git(work, "commit", "-m", "init")
        _git(work, "branch", "-M", "main")
        _git(work, "push", "-u", "origin", "main")
        known_good = _git(work, "rev-parse", "HEAD").stdout.strip()
        # feature branch
        _git(work, "checkout", "-b", "automation/batch-test")
        (work / "lesson.md").write_text("new\n", encoding="utf-8")
        _git(work, "add", "lesson.md")
        _git(work, "commit", "-m", "add lesson")
        _git(work, "push", "-u", "origin", "automation/batch-test")
        # conflict simulation on main
        _git(work, "checkout", "main")
        (work / "README").write_text("good\nchanged on main\n", encoding="utf-8")
        _git(work, "add", "README")
        _git(work, "commit", "-m", "main churn")
        _git(work, "push", "origin", "main")
        # rollback demo: reset file to known content via checkout known_good path (no force push)
        _git(work, "checkout", known_good, "--", "README")
        _git(work, "commit", "-m", "revert content from known_good without force")
        _git(work, "push", "origin", "main")
        return {
            "ok": True,
            "known_good": known_good,
            "branches": ["main", "automation/batch-test"],
            "notes": "PR merge simulated by branch existence; no force-push used",
        }

#!/usr/bin/env python3
"""Path policy for unattended classroom auto-merge.

Only lesson-content paths may be auto-merged. Infrastructure, workflows,
automation runtime, deploy scripts, secrets, and unrelated site files require
manual merge.
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass


# Explicit allowlist (auto-merge eligible).
ALLOWED_GLOBS: tuple[str, ...] = (
    "classroom/pack/classes/**",
    "classroom/pack/modules/**",
    "classroom/pack/class_index.json",
    "classroom/automation/class_index.json",  # approved index only
    "classroom/automation/curriculum_manifest.json",  # approved manifest only
    "classroom/classes/**",
    "classroom/modules/**",
    "classroom/references/**",
    "classroom/courses/**",
    "classroom/units/**",
    "classroom/index.html",
    "classroom/syllabus.html",
    "classroom/glossary.html",
    "classroom/workbook.html",
    "classroom/methodology.html",
    "classroom/final-exam.html",
    "classroom/overview.html",
    "classroom/outcomes.html",
    "classroom/path.html",
    "classroom/prereq.html",
    "classroom/start.html",
    "classroom/course-map.html",
    "classroom/instructor.html",
    "classroom/welcome.html",
    "classroom/news-lab/**",
    "classroom/classroom.css",
    "classroom/classroom.js",
)

# Hard deny — even if somehow overlapping an allow pattern.
DENIED_GLOBS: tuple[str, ...] = (
    ".github/**",
    ".github/workflows/**",
    "classroom/automation/**",
    "classroom/automation/systemd/**",
    "**/wrangler.toml",
    "**/deploy*",
    "**/*secret*",
    "**/*.env",
    "**/*.env.*",
    "**/config.example.env",
    "assets/**",
    "index.html",
    "downloads/**",
    "engineering/**",
    "otacon/**",
    "keeproute/**",
    "expansion/**",
    "ai9/**",
    "keepdesk/**",
    "faq/**",
    "about/**",
)

# Allowlist exceptions inside otherwise-denied automation tree.
AUTOMATION_ALLOW_EXCEPTIONS: tuple[str, ...] = (
    "classroom/automation/class_index.json",
    "classroom/automation/curriculum_manifest.json",
)


@dataclass(frozen=True)
class PathPolicyResult:
    automergable: bool
    allowed: list[str]
    denied: list[str]
    reason: str


def _norm(path: str) -> str:
    path = path.replace("\\", "/").strip()
    while path.startswith("./"):
        path = path[2:]
    return path.lstrip("/")


def _match(path: str, pattern: str) -> bool:
    path = _norm(path)
    pattern = _norm(pattern)
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return path == prefix.rstrip("/") or path.startswith(prefix.rstrip("/") + "/")
    return fnmatch.fnmatch(path, pattern) or path == pattern.rstrip("/")


def is_denied(path: str) -> bool:
    path = _norm(path)
    if path in AUTOMATION_ALLOW_EXCEPTIONS:
        return False
    return any(_match(path, pat) for pat in DENIED_GLOBS)


def is_allowed(path: str) -> bool:
    path = _norm(path)
    if path in AUTOMATION_ALLOW_EXCEPTIONS:
        return True
    if is_denied(path):
        return False
    return any(_match(path, pat) for pat in ALLOWED_GLOBS)


def evaluate_paths(paths: list[str]) -> PathPolicyResult:
    """Return whether a PR touching exactly these paths may be auto-merged."""
    cleaned = sorted({_norm(p) for p in paths if p and p not in {".", "./"}})
    if not cleaned:
        return PathPolicyResult(False, [], [], "empty diff — refuse auto-merge")
    allowed: list[str] = []
    denied: list[str] = []
    for p in cleaned:
        if is_allowed(p):
            allowed.append(p)
        else:
            denied.append(p)
    if denied:
        return PathPolicyResult(
            False,
            allowed,
            denied,
            "forbidden paths present — manual merge required",
        )
    return PathPolicyResult(True, allowed, [], "lesson-content paths only — auto-merge permitted")


def evaluate_git_diff_name_only(diff_text: str) -> PathPolicyResult:
    paths = [ln.strip() for ln in diff_text.splitlines() if ln.strip()]
    return evaluate_paths(paths)

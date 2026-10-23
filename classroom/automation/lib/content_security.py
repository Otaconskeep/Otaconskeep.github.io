"""Unattended-content security gates for classroom HTML/Markdown.

Fail closed: any finding blocks PR/publication.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

# Dangerous patterns in generated lesson HTML/MD.
_EVAL_JS = re.compile(r"\beval\s*\(|new\s+Function\s*\(|document\.write\s*\(", re.I)
_INLINE_HANDLER = re.compile(r"\son\w+\s*=", re.I)
_EXTERNAL_SCRIPT = re.compile(
    r"<script[^>]+src\s*=\s*[\"'](?!/|https://otaconskeep\.github\.io/|https://otaconskeep-site\.otaconskeep\.workers\.dev/)[^\"']+[\"']",
    re.I,
)
_HIDDEN_FETCH = re.compile(r"\bfetch\s*\(|XMLHttpRequest|navigator\.sendBeacon|WebSocket\s*\(", re.I)
_UNSAFE_IFRAME = re.compile(r"<iframe\b", re.I)
_CURL_PIPE = re.compile(
    r"(?m)^\s*(?:\$\s*)?(?:sudo\s+)?(?:curl|wget)\b[^\n|]*\|\s*(?:ba)?sh\b",
    re.I,
)
_SECRETISH = re.compile(
    r"(?i)(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?(?!YOUR_|REPLACE|CHANGEME|<|\$)[A-Za-z0-9_\-]{20,}"
    r"|ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}"
)
_DANGEROUS_RM = re.compile(r"\brm\s+(-[a-zA-Z]*f[a-zA-Z]*|--force).*[/\*]|\bmkfs\b|\bdd\s+if=", re.I)
# Allowed script src prefixes (same-origin relative or known site assets).
_ALLOWED_WIDGET_MARKERS = (
    "data-os=",  # existing OS command toggles in classroom chrome
    "help_widget",
    "cr-osbar",
    "classroom.js",
)


def scan_text(text: str, *, path: str = "") -> list[str]:
    fails: list[str] = []
    if _EVAL_JS.search(text):
        fails.append(f"SEC_EVAL:{path}")
    if _INLINE_HANDLER.search(text):
        fails.append(f"SEC_INLINE_HANDLER:{path}")
    if _EXTERNAL_SCRIPT.search(text):
        fails.append(f"SEC_EXTERNAL_SCRIPT:{path}")
    # Hidden network only when embedded in <script> blocks outside vetted classroom.js
    for m in re.finditer(r"<script\b[^>]*>(.*?)</script>", text, re.I | re.S):
        body = m.group(1)
        if _HIDDEN_FETCH.search(body) and "classroom.js" not in path:
            fails.append(f"SEC_HIDDEN_NETWORK:{path}")
    if _UNSAFE_IFRAME.search(text):
        fails.append(f"SEC_IFRAME:{path}")
    if _CURL_PIPE.search(text):
        fails.append(f"SEC_CURL_PIPE_SHELL:{path}")
    if _SECRETISH.search(text):
        fails.append(f"SEC_SECRET_EXPOSURE:{path}")
    # Broad destructive patterns are enforced in validate_lessons with controlled
    # dangerous_commands exceptions; content_security focuses on injection/exfil.
    return fails


def scan_paths(paths: Iterable[Path]) -> list[str]:
    fails: list[str] = []
    for p in paths:
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".html", ".md", ".js"}:
            continue
        # Skip generator/tooling
        if "automation/" in str(p).replace("\\", "/") and p.suffix == ".py":
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            fails.append(f"SEC_UNREADABLE:{p}")
            continue
        fails.extend(scan_text(text, path=str(p)))
    return fails


def scan_bundle_fields(bundle: dict) -> list[str]:
    """Scan curated/LLM lesson JSON fields before render."""
    fails: list[str] = []
    for key in (
        "teaching",
        "lab",
        "homework",
        "security",
        "rollback",
        "quiz",
        "required_reading",
        "objectives",
    ):
        val = bundle.get(key)
        if val is None:
            continue
        text = val if isinstance(val, str) else str(val)
        for f in scan_text(text, path=f"bundle.{key}"):
            fails.append(f)
    return fails


def assert_html_matches_regen(classroom_dir: Path, regenerated: Path) -> list[str]:
    """Compare approved generated HTML against a fresh regen of key pages."""
    fails: list[str] = []
    for rel in ("index.html", "welcome.html"):
        a = classroom_dir / rel
        b = regenerated / rel
        if not a.is_file() or not b.is_file():
            # welcome may be static; index must exist
            if rel == "index.html":
                fails.append(f"SEC_REGEN_MISSING:{rel}")
            continue
        if a.read_bytes() != b.read_bytes():
            fails.append(f"SEC_REGEN_MISMATCH:{rel}")
    return fails

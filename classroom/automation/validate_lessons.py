#!/usr/bin/env python3
"""Deterministic hard gates for lesson bundles and rendered pack files."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from lib import Config, load_config
from lib.curriculum import discover_existing_classes, load_roadmap
from lib.content_security import scan_bundle_fields

DANGEROUS_PATTERNS = [
    (r"\brm\s+(-[^\s]*r[^\s]*f|-[^\s]*f[^\s]*r)", "rm -rf style deletion"),
    (r"\bdd\s+", "dd"),
    (r"\bmkfs\b", "mkfs"),
    (r"\b(fdisk|parted)\b", "partition editor"),
    (r"chmod\s+(-R\s+)?777\b", "chmod 777"),
    (r"chown\s+-R\s+[^\n]*/(\s|$)", "recursive chown on broad path"),
    (r"curl\s+[^\n|]*\|\s*(ba)?sh", "curl pipe to shell"),
    (r"wget\s+[^\n|]*\|\s*(ba)?sh", "wget pipe to shell"),
    (r"\b(ufw|iptables|nft)\b", "firewall change"),
    (r"sshd_config", "SSH daemon config"),
    (r"userdel\b", "user deletion"),
    (r"docker\s+system\s+prune", "docker prune"),
    (r"\s/\s*$|chown\s+-R\s+[^\n]*\s+/\s*$", "targeting /"),
]


class GateFailure(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def load_schema(cfg: Config) -> dict[str, Any]:
    return json.loads(cfg.schema_path.read_text(encoding="utf-8"))


def validate_bundle(cfg: Config, bundle: dict[str, Any], *, existing_titles: set[str]) -> list[str]:
    """Return list of hard-gate failure strings (empty = pass)."""
    fails: list[str] = []
    schema = load_schema(cfg)
    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(bundle), key=lambda e: list(e.path)):
        fails.append(f"SCHEMA: {list(err.path)}: {err.message}")

    title = str(bundle.get("title", "")).strip().lower()
    for t in existing_titles:
        if t.strip().lower() == title:
            fails.append(f"DUP_TOPIC: title matches existing '{t}'")

    # superficial teaching
    teaching = str(bundle.get("teaching") or "")
    if len(re.findall(r"\b(TODO|TBD|placeholder|lorem ipsum)\b", teaching, re.I)):
        fails.append("PLACEHOLDER: teaching contains placeholder markers")
    if len(teaching) < 800:
        fails.append("THIN_TEACHING: teaching too short")

    quiz = bundle.get("quiz") or []
    answers = bundle.get("answer_key") or []
    if len(answers) < len(quiz):
        fails.append("QUIZ_KEY: answer_key shorter than quiz")

    lab = str(bundle.get("lab") or "")
    teaching = str(bundle.get("teaching") or "")
    rollback = str(bundle.get("rollback") or "")
    verification = bundle.get("verification") or []
    verif_parts: list[str] = []
    for item in verification:
        if isinstance(item, str):
            verif_parts.append(item)
        elif isinstance(item, dict):
            verif_parts.append(" ".join(str(v) for v in item.values()))
        else:
            verif_parts.append(str(item))
    if not verification:
        fails.append("VERIFY: missing verification checkpoints")
    elif not any(p.strip() for p in verif_parts):
        fails.append("VERIFY: empty verification checkpoints")
    if len(rollback) < 80:
        fails.append("ROLLBACK: rollback too thin")

    # dangerous command patterns in lab/teaching require a controlled dangerous_commands entry
    blob = "\n".join([lab, teaching, rollback])
    controlled = [
        d
        for d in (bundle.get("dangerous_commands") or [])
        if d.get("warning") and d.get("verification") and d.get("rollback") and d.get("failure_mode")
    ]
    for pat, name in DANGEROUS_PATTERNS:
        if re.search(pat, blob, re.I) and not controlled:
            fails.append(f"DANGER_UNCONTROLLED: detected {name} without controlled dangerous_commands entry")

    # secrets
    if re.search(r"(?i)(api[_-]?key|password|secret)\s*[:=]\s*['\"]?[^\s'\"]{8,}", blob):
        fails.append("SECRET: possible credential in lesson content")
    if "discord.com/api/webhooks/" in blob:
        fails.append("SECRET: webhook URL in lesson")

    # Unattended-content security gates (eval, curl|sh, iframes, etc.)
    fails.extend(scan_bundle_fields(bundle))

    # references non-empty; fake example.com manufactured claims
    for ref in bundle.get("references") or []:
        if "example.invalid" in ref or "fakereference.local" in ref:
            fails.append(f"FAKE_REF: {ref}")

    return fails


def validate_batch(
    cfg: Config,
    bundles: list[dict[str, Any]],
    *,
    expected_ids: list[int],
) -> dict[str, Any]:
    existing = discover_existing_classes(cfg.pack_dir)
    existing_titles = {m["title"] for m in existing.values()}
    fails: list[str] = []

    ids = [int(b["class_id"]) for b in bundles]
    if ids != expected_ids:
        fails.append(f"BATCH_IDS: got {ids} expected {expected_ids}")
    if len(ids) != len(set(ids)):
        fails.append("BATCH_UNIQUE: duplicate class ids in batch")
    for i in ids:
        if i in existing:
            fails.append(f"OVERWRITE: class {i} already exists in repository")

    # sequential relative to expected
    if expected_ids and ids and ids != sorted(ids):
        fails.append("BATCH_ORDER: class ids not sorted/sequential as expected")

    per: dict[str, list[str]] = {}
    for b in bundles:
        f = validate_bundle(cfg, b, existing_titles=existing_titles)
        per[str(b["class_id"])] = f
        fails.extend([f"class {b['class_id']}: {x}" for x in f])
        existing_titles.add(str(b.get("title")))

    return {"ok": not fails, "failures": fails, "per_class": per}


def validate_rendered_nav(cfg: Config, class_ids: list[int], staging_pack: Path) -> list[str]:
    fails: list[str] = []
    for n in class_ids:
        matches = list((staging_pack / "classes").glob(f"{n:02d}_*.md"))
        if len(matches) != 1:
            fails.append(f"RENDER: expected one class file for {n}, found {len(matches)}")
    return fails


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--bundles", required=True, help="JSON file with list of bundles")
    ap.add_argument("--expected", required=True, help="comma-separated class ids")
    args = ap.parse_args()
    cfg = load_config()
    bundles = json.loads(Path(args.bundles).read_text(encoding="utf-8"))
    expected = [int(x) for x in args.expected.split(",") if x.strip()]
    report = validate_batch(cfg, bundles, expected_ids=expected)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

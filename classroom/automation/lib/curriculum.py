#!/usr/bin/env python3
"""Curriculum discovery: repository is authoritative over stale manifest state."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

from . import Config, atomic_write_json, utc_now


CLASS_FILE_RE = re.compile(r"^(\d{2})_([A-Z0-9_]+)\.md$")
TITLE_RE = re.compile(r"^#\s+Class\s+(\d+)\s+[—\-]\s+(.+)$", re.I | re.M)


def load_roadmap(cfg: Config) -> dict[str, Any]:
    return yaml.safe_load(cfg.roadmap_path.read_text(encoding="utf-8"))


def discover_existing_classes(pack_dir: Path) -> dict[int, dict[str, Any]]:
    """Scan pack/classes for published class markdown. Repo wins."""
    classes_dir = pack_dir / "classes"
    found: dict[int, dict[str, Any]] = {}
    if not classes_dir.is_dir():
        return found
    for path in sorted(classes_dir.glob("*.md")):
        m = CLASS_FILE_RE.match(path.name)
        if not m:
            continue
        num = int(m.group(1))
        text = path.read_text(encoding="utf-8", errors="replace")
        tm = TITLE_RE.search(text)
        title = tm.group(2).strip() if tm else path.stem
        found[num] = {
            "class_id": num,
            "title": title,
            "source_filename": path.name,
            "path": str(path),
            "checksum": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "status": "published",
        }
    return found


def load_manifest(cfg: Config) -> dict[str, Any]:
    if not cfg.manifest_path.is_file():
        return {
            "schema_version": "1.0",
            "updated_at": None,
            "core_complete": False,
            "entries": {},
            "last_successful_batch": None,
            "last_failed_batch": None,
        }
    return json.loads(cfg.manifest_path.read_text(encoding="utf-8"))


def reconcile_manifest(cfg: Config) -> dict[str, Any]:
    """Repository is authoritative if manifest disagrees."""
    roadmap = load_roadmap(cfg)
    existing = discover_existing_classes(cfg.pack_dir)
    man = load_manifest(cfg)
    entries = man.setdefault("entries", {})
    # drop manifest claims for missing files
    for key in list(entries.keys()):
        if key.startswith("NEWS-"):
            continue
        try:
            n = int(key)
        except ValueError:
            continue
        if n not in existing and entries[key].get("status") == "published":
            entries[key]["status"] = "missing_from_repo"
            entries[key]["note"] = "Manifest claimed published but file absent; repo authoritative"
    for num, meta in existing.items():
        key = str(num)
        ent = entries.get(key, {})
        ent.update(
            {
                "class_id": num,
                "canonical_topic": meta["title"],
                "status": "published",
                "source_filename": meta["source_filename"],
                "content_checksum": meta["checksum"],
                "published_url": f"/classroom/classes/{num:02d}.html",
                "lesson_schema_version": ent.get("lesson_schema_version", "1.0"),
            }
        )
        # prefer roadmap title only for unpublished; keep published title from repo
        entries[key] = ent
    # ensure roadmap placeholders for missing
    for num, title in sorted((int(k), v) for k, v in roadmap.get("classes", {}).items()):
        key = str(num)
        if key not in entries:
            entries[key] = {
                "class_id": num,
                "canonical_topic": title,
                "status": "pending",
                "source_filename": None,
                "published_url": None,
                "content_checksum": None,
            }
        elif entries[key].get("status") != "published":
            entries[key]["canonical_topic"] = title
    man["updated_at"] = utc_now()
    man["core_complete"] = all(
        entries.get(str(n), {}).get("status") == "published" for n in range(1, int(roadmap["core_final_class"]) + 1)
        if n in existing or n >= 16 or n <= 15
    )
    # stricter: 1..15 must exist; 16..121 must be published
    core_ok = all(n in existing for n in range(1, 16)) and all(
        entries.get(str(n), {}).get("status") == "published" for n in range(16, int(roadmap["core_final_class"]) + 1)  # through 123 after remap
    )
    man["core_complete"] = core_ok
    return man


def _roadmap_title(roadmap: dict, n: int) -> str | None:
    classes = roadmap.get("classes", {})
    return classes.get(n) or classes.get(str(n))


def next_core_batch(cfg: Config, batch_size: int | None = None) -> list[dict[str, Any]]:
    roadmap = load_roadmap(cfg)
    size = batch_size or int(roadmap.get("batch_size", 6))
    existing = discover_existing_classes(cfg.pack_dir)
    final = int(roadmap["core_final_class"])
    missing: list[dict[str, Any]] = []
    for n in range(1, final + 1):
        if n in existing:
            continue
        title = _roadmap_title(roadmap, n)
        if not title:
            # numbers 1-15 without roadmap entries are historical; if missing it's a blocker
            if n <= 15:
                raise RuntimeError(f"Critical: historical class {n} missing from repository")
            continue
        missing.append({"class_id": n, "title": title})
        if len(missing) >= size:
            break
    return missing


def module_for_class(roadmap: dict[str, Any], class_id: int) -> dict[str, Any] | None:
    for slug, mod in roadmap.get("modules", {}).items():
        if class_id in mod.get("classes", []):
            return {"slug": slug, **mod}
    return None


def save_manifest(cfg: Config, man: dict[str, Any]) -> None:
    atomic_write_json(cfg.manifest_path, man)


def topic_slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return "-".join(s.split("-")[:6])[:48]

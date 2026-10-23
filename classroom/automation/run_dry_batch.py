#!/usr/bin/env python3
"""Non-destructive dry run: generate+validate+review+stage+preview-build. No git push, no timers."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("GENERATOR_BACKEND", "curated")
os.environ.setdefault("DRY_RUN", "1")
os.environ.setdefault("CLASSROOM_STATE_DIR", "/tmp/otaconskeep-classroom-dryrun/state")
os.environ.setdefault("CLASSROOM_LOG_DIR", "/tmp/otaconskeep-classroom-dryrun/logs")
os.environ.setdefault("CLASSROOM_STAGING_DIR", "/tmp/otaconskeep-classroom-dryrun/staging")
os.environ.setdefault("CLASSROOM_ARTIFACT_DIR", "/tmp/otaconskeep-classroom-dryrun/artifacts")
os.environ.setdefault("CLASSROOM_LOCK_FILE", "/tmp/otaconskeep-classroom-dryrun/classroom.publish.lock")

from lib import load_config, atomic_write_json, utc_now
from lib.curriculum import next_core_batch, discover_existing_classes
from generate_lessons import generate_one
from lib import JsonLogger, new_run_id, publication_lock
from validate_lessons import validate_batch
from review_lessons import heuristic_review
from render_lessons import write_bundle_to_pack
from validate_lessons import validate_rendered_nav
from publish_lessons import make_zip


def preview_build(cfg, staging_pack: Path, run_id: str) -> dict:
    """Copy classroom tree to temp, merge staged pack, run generator without sync_github."""
    preview = Path("/tmp/otaconskeep-classroom-dryrun") / run_id / "preview_site_classroom"
    if preview.exists():
        shutil.rmtree(preview)
    shutil.copytree(
        cfg.classroom_dir,
        preview,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"),
    )
    # merge staged pack files
    for src in staging_pack.rglob("*"):
        if src.is_file():
            rel = src.relative_to(staging_pack)
            dst = preview / "pack" / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    # write class_index for redirects
    idx = {"classes": {}, "updated_at": utc_now()}
    for mod_root in (staging_pack / "modules").glob("*"):
        pass
    # build redirect map from staging module topics by reading write paths via class files
    from lib.curriculum import load_roadmap, module_for_class, topic_slug
    import re
    roadmap = load_roadmap(cfg)
    for class_md in (staging_pack / "classes").glob("*.md"):
        m = re.match(r"^(\d{2})_", class_md.name)
        if not m:
            continue
        n = int(m.group(1))
        title_line = class_md.read_text(encoding="utf-8").splitlines()[0]
        title = title_line.split("—", 1)[-1].strip() if "—" in title_line else title_line
        mod = module_for_class(roadmap, n)
        if not mod:
            continue
        classes = mod.get("classes", [])
        i = classes.index(n) + 1
        tslug = topic_slug(title)
        # find actual topic dir
        topics = list((staging_pack / "modules" / mod["slug"] / "topics").glob(f"{i:02d}-*"))
        if topics:
            rel = f"{mod['slug']}/topics/{topics[0].name}/lesson.html"
            idx["classes"][str(n)] = {"redirect": rel, "title": title}
    atomic_write_json(preview / "automation" / "class_index.json", idx)

    # Patch preview generator SITE path
    code = f"""
import runpy, sys, pathlib
sys.path.insert(0, {str(preview)!r})
import importlib.util
spec = importlib.util.spec_from_file_location('gen', {str(preview / '_gen_from_pack.py')!r})
g = importlib.util.module_from_spec(spec)
# Override SITE/PACK to preview
import types
spec.loader.exec_module(g)
g.SITE = pathlib.Path({str(preview)!r})
g.PACK = g.SITE / 'pack'
g.CLASSES_DIR = g.SITE / 'classes'
g.sync_github = lambda: print('skip sync_github dry-run')
# merge dynamic class meta + redirects if helpers exist
if hasattr(g, 'load_dynamic_class_extensions'):
    g.load_dynamic_class_extensions()
if hasattr(g, 'discover_extra_modules'):
    g.discover_extra_modules()
g.gen_hub()
g.gen_modules()
g.gen_classes()
g.class_to_module_redirects()
print('PREVIEW_BUILD_OK')
"""
    p = subprocess.run([sys.executable, "-c", code], text=True, capture_output=True)
    return {
        "ok": p.returncode == 0 and "PREVIEW_BUILD_OK" in (p.stdout or ""),
        "stdout": (p.stdout or "")[-3000:],
        "stderr": (p.stderr or "")[-3000:],
        "preview_path": str(preview),
    }


def main() -> int:
    cfg = load_config()
    for d in (cfg.state_dir, cfg.log_dir, cfg.staging_dir, cfg.artifact_dir):
        d.mkdir(parents=True, exist_ok=True)
    run_id = new_run_id("dry")
    logger = JsonLogger(cfg.log_dir / f"{run_id}.jsonl", run_id, "dry_run")
    existing_before = discover_existing_classes(cfg.pack_dir)
    try:
        with publication_lock(cfg, logger):
            batch = next_core_batch(cfg)
            if len(batch) < 6:
                logger.event("blocked", message=f"expected 6 missing classes, got {len(batch)}", batch=batch)
                # still proceed if some missing for partial evidence
            expected = [b["class_id"] for b in batch[:6]]
            if len(expected) != 6:
                print(json.dumps({"ok": False, "error": "need six missing classes", "pending": batch}, indent=2))
                return 1
            bundles = []
            for item in batch[:6]:
                bundles.append(generate_one(cfg, item["class_id"], item["title"], logger))
            validation = validate_batch(cfg, bundles, expected_ids=expected)
            reviews = [heuristic_review(b) for b in bundles]
            review = {
                "ok": all(r["pass"] for r in reviews) and all(r["average"] >= cfg.critic_min for r in reviews),
                "reviews": reviews,
                "min_score": cfg.critic_min,
            }
            staging = cfg.staging_dir / run_id / "pack"
            if staging.exists():
                shutil.rmtree(staging)
            staging.mkdir(parents=True)
            redirects = {}
            for b in bundles:
                paths = write_bundle_to_pack(cfg, b, staging)
                if "redirect" in paths:
                    redirects[str(b["class_id"])] = paths["redirect"]
            nav = validate_rendered_nav(cfg, expected, staging)
            zpath = make_zip(cfg.artifact_dir, run_id, staging, bundles, validation, review)
            build = preview_build(cfg, staging, run_id)
            existing_after = discover_existing_classes(cfg.pack_dir)
            live_unchanged = existing_before == existing_after
            # page checks on preview
            page_fails = []
            preview = Path(build["preview_path"])
            for n in expected:
                # module lesson html should exist after gen_modules
                red = redirects.get(str(n))
                if red:
                    target = preview / "modules" / Path(red)
                    # red includes .html under modules/
                    p = preview / "modules" / red
                    if not p.is_file():
                        page_fails.append(f"missing preview page {p}")
                css = (preview / "classroom.css").read_text(encoding="utf-8", errors="replace")
                if "pre" not in css:
                    page_fails.append("css")
            report = {
                "ok": validation["ok"] and review["ok"] and not nav and build["ok"] and live_unchanged and not page_fails,
                "run_id": run_id,
                "expected_class_ids": expected,
                "titles": [b["title"] for b in bundles],
                "validation": validation,
                "review_scores": [{"class_id": r["class_id"] if "class_id" in r else reviews[i] , **reviews[i]} for i, r in enumerate(reviews)],
                "redirects_would_be": redirects,
                "zip": str(zpath),
                "preview_build": {"ok": build["ok"], "path": build["preview_path"], "stderr_tail": build["stderr"][-500:]},
                "page_checks": {"ok": not page_fails, "failures": page_fails},
                "live_classroom_unchanged": live_unchanged,
                "existing_class_count": len(existing_after),
                "disposition": "dry_run_complete",
                "ts": utc_now(),
            }
            # attach class_ids on reviews
            for i, b in enumerate(bundles):
                reviews[i]["class_id"] = b["class_id"]
            report["review_scores"] = reviews
            atomic_write_json(cfg.staging_dir / run_id / "DRY_RUN_REPORT.json", report)
            logger.event("complete", disposition=report["disposition"], ok=report["ok"])
            print(json.dumps(report, indent=2))
            return 0 if report["ok"] else 1
    finally:
        logger.close()


if __name__ == "__main__":
    raise SystemExit(main())

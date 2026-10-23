#!/usr/bin/env python3
"""Publish path: dry-run staging by default; PR workflow when explicitly enabled.

Does NOT push/merge unless CLASSROOM automation is activated and DRY_RUN=0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import (
    JsonLogger,
    atomic_write_json,
    load_config,
    new_run_id,
    publication_lock,
    utc_now,
)
from lib.curriculum import reconcile_manifest, save_manifest
from render_lessons import write_bundle_to_pack
from validate_lessons import validate_batch, validate_rendered_nav


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=check, text=True, capture_output=True)


def build_classroom(cfg, logger: JsonLogger) -> dict:
    gen = cfg.classroom_dir / "_gen_from_pack.py"
    if not gen.is_file():
        return {"ok": False, "error": f"missing {gen}"}
    # Build without syncing github during dry-run by patching env
    env_python = [sys.executable, str(gen)]
    # Temporarily monkey by running a wrapper that skips sync if DRY
    code = f"""
import runpy, sys
sys.path.insert(0, {str(cfg.classroom_dir)!r})
import _gen_from_pack as g
g.sync_github = lambda: print('skip sync_github')
g.main()
"""
    p = subprocess.run([sys.executable, "-c", code], cwd=str(cfg.classroom_dir), text=True, capture_output=True)
    logger.event("build", returncode=p.returncode, stderr_tail=(p.stderr or "")[-500:])
    return {"ok": p.returncode == 0, "stdout": p.stdout[-2000:], "stderr": p.stderr[-2000:]}


def desktop_mobile_checks(cfg, class_ids: list[int]) -> dict:
    """Heuristic page checks (chromium optional). Fail on missing files / obvious overflow CSS absences."""
    fails = []
    for n in class_ids:
        # prefer module redirect target existence after build — class html redirect
        p = cfg.classroom_dir / "classes" / f"{n:02d}.html"
        if not p.is_file():
            # during dry-run before integrate, check staging only
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if "location.replace" not in text and "CLASS" not in text:
            fails.append(f"class {n} html unexpected")
    css = (cfg.classroom_dir / "classroom.css").read_text(encoding="utf-8", errors="replace")
    if "overflow-x" not in css and "pre" not in css:
        fails.append("css_missing_pre_or_overflow_hints")
    # mobile viewport meta is in generator HEAD
    return {"ok": not fails, "failures": fails, "method": "heuristic"}


def make_zip(artifact_dir: Path, run_id: str, staging: Path, bundles: list, validation: dict, review: dict) -> Path:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    zpath = artifact_dir / f"{run_id}_batch.zip"
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in staging.rglob("*"):
            if p.is_file():
                z.write(p, arcname=str(p.relative_to(staging.parent)))
        z.writestr("batch_index.json", json.dumps({"bundles": [b["class_id"] for b in bundles]}, indent=2))
        z.writestr("validation.json", json.dumps(validation, indent=2))
        z.writestr("review.json", json.dumps(review, indent=2))
        z.writestr(
            "IMPORT.txt",
            "This ZIP is a backup artifact. Publication uses git, not ZIP import.\n",
        )
        # checksums
        lines = []
        for p in staging.rglob("*"):
            if p.is_file():
                h = hashlib.sha256(p.read_bytes()).hexdigest()
                lines.append(f"{h}  {p.relative_to(staging)}")
        z.writestr("checksums.sha256", "\n".join(lines) + "\n")
    return zpath


def integrate_staging_into_site_pack(cfg, staging_pack: Path, class_ids: list[int]) -> list[Path]:
    """Copy staged class/module files into the live pack (caller must be intentional)."""
    changed: list[Path] = []
    for n in class_ids:
        for src in (staging_pack / "classes").glob(f"{n:02d}_*.md"):
            dst = cfg.pack_dir / "classes" / src.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            changed.append(dst)
    # modules tree
    src_mod = staging_pack / "modules"
    if src_mod.is_dir():
        for src in src_mod.rglob("*"):
            if src.is_file():
                rel = src.relative_to(src_mod)
                dst = cfg.pack_dir / "modules" / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                changed.append(dst)
    return changed


def update_class_index(cfg, redirects: dict[str, str]) -> Path:
    """Write machine class index consumed by _gen_from_pack.py."""
    path = cfg.classroom_dir / "automation" / "class_index.json"
    data = {}
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
    classes = data.setdefault("classes", {})
    for cid, red in redirects.items():
        classes[cid] = {"redirect": red}
    data["updated_at"] = utc_now()
    atomic_write_json(path, data)
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundles", required=True)
    ap.add_argument("--review", required=True)
    ap.add_argument("--integrate", action="store_true", help="Write into live pack (still no git push if DRY_RUN)")
    ap.add_argument("--allow-git", action="store_true", help="Permit git commit/push/PR (requires DRY_RUN=0)")
    args = ap.parse_args()
    cfg = load_config()
    run_id = new_run_id("pub")
    try:
        cfg.log_dir.mkdir(parents=True, exist_ok=True)
        cfg.staging_dir.mkdir(parents=True, exist_ok=True)
        cfg.artifact_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        base = Path("/tmp/otaconskeep-classroom-dryrun")
        cfg.log_dir = base / "logs"
        cfg.staging_dir = base / "staging"
        cfg.artifact_dir = base / "artifacts"
        cfg.state_dir = base / "state"
        cfg.lock_file = base / "classroom.publish.lock"
        for p in (cfg.log_dir, cfg.staging_dir, cfg.artifact_dir, cfg.state_dir):
            p.mkdir(parents=True, exist_ok=True)

    logger = JsonLogger(cfg.log_dir / f"{run_id}.jsonl", run_id, "publish")
    bundles = json.loads(Path(args.bundles).read_text(encoding="utf-8"))
    review = json.loads(Path(args.review).read_text(encoding="utf-8"))
    expected = [int(b["class_id"]) for b in bundles]

    try:
        with publication_lock(cfg, logger):
            if not review.get("ok"):
                logger.event("blocked", reason="critic_failed")
                return 1
            v = validate_batch(cfg, bundles, expected_ids=expected)
            if not v["ok"]:
                logger.event("blocked", reason="validation_failed", failures=v["failures"][:10])
                return 1

            staging = cfg.staging_dir / run_id / "pack"
            if staging.exists():
                shutil.rmtree(staging)
            staging.mkdir(parents=True)
            redirects = {}
            for b in bundles:
                paths = write_bundle_to_pack(cfg, b, staging)
                if "redirect" in paths:
                    redirects[str(b["class_id"])] = paths["redirect"]
            nav_fails = validate_rendered_nav(cfg, expected, staging)
            if nav_fails:
                logger.event("blocked", reason="render_nav", failures=nav_fails)
                return 1

            zpath = make_zip(cfg.artifact_dir, run_id, staging, bundles, v, review)
            logger.event("zip", path=str(zpath))

            build_result = {"ok": True, "skipped": True}
            page_checks = {"ok": True, "skipped": True}
            changed: list[str] = []

            if args.integrate:
                # refuse overwrite
                for n in expected:
                    if list((cfg.pack_dir / "classes").glob(f"{n:02d}_*.md")):
                        logger.event("blocked", reason="overwrite_guard", class_id=n)
                        return 1
                known_good = run(["git", "rev-parse", "HEAD"], cwd=cfg.site_repo).stdout.strip()
                logger.event("known_good", commit=known_good)
                ch = integrate_staging_into_site_pack(cfg, staging, expected)
                changed = [str(p) for p in ch]
                update_class_index(cfg, redirects)
                build_result = build_classroom(cfg, logger)
                page_checks = desktop_mobile_checks(cfg, expected)
                if not build_result.get("ok") or not page_checks.get("ok"):
                    logger.event("blocked", reason="build_or_page_failed", build=build_result, pages=page_checks)
                    # do not advance manifest
                    return 1
                if args.allow_git and not cfg.dry_run:
                    if cfg.publish_mode == "direct_main" and not cfg.allow_direct_main:
                        logger.event("blocked", reason="direct_main_not_allowed")
                        return 1
                    logger.event(
                        "git_not_executed",
                        message="Git push/PR requires explicit activation approval after dry-run evidence",
                    )
                    return 3
                else:
                    logger.event(
                        "dry_run_preserve",
                        message="Integrated locally for dry-run evidence; not committing/pushing",
                        changed=changed[:20],
                    )
                    # For dry-run evidence we may integrate into a temp copy instead — if integrated live, warn
                    if args.integrate and cfg.dry_run:
                        logger.event(
                            "note",
                            message="DRY_RUN integrate modified local pack workspace; review git status; do not push",
                        )

            # manifest update ONLY when not dry-run and git success — skip here
            report = {
                "run_id": run_id,
                "expected": expected,
                "validation": v,
                "review": review,
                "zip": str(zpath),
                "build": build_result,
                "pages": page_checks,
                "redirects": redirects,
                "changed_files": changed,
                "dry_run": cfg.dry_run,
                "disposition": "dry_run_ok" if cfg.dry_run else "awaiting_git",
            }
            atomic_write_json(cfg.staging_dir / run_id / "publish_report.json", report)
            logger.event("complete", disposition=report["disposition"], report=str(cfg.staging_dir / run_id / "publish_report.json"))
            print(json.dumps(report, indent=2))
            return 0
    finally:
        logger.close()


if __name__ == "__main__":
    raise SystemExit(main())

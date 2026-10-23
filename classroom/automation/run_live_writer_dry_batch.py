#!/usr/bin/env python3
"""Full dry-run using production writer (codex) + critic (grok). No git/timer/deploy."""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["GENERATOR_BACKEND"] = "llm"
os.environ["WRITER_MODEL"] = "codex/gpt-5.6-sol-medium"
os.environ["CRITIC_MODEL"] = "gc/grok-4.6"
os.environ["ALLOW_WEAK_MODELS"] = "0"
os.environ["DRY_RUN"] = "1"
os.environ.setdefault("CLASSROOM_STATE_DIR", "/tmp/otaconskeep-classroom-dryrun/state")
os.environ.setdefault("CLASSROOM_LOG_DIR", "/tmp/otaconskeep-classroom-dryrun/logs")
os.environ.setdefault("CLASSROOM_STAGING_DIR", "/tmp/otaconskeep-classroom-dryrun/staging")
os.environ.setdefault("CLASSROOM_ARTIFACT_DIR", "/tmp/otaconskeep-classroom-dryrun/artifacts")
os.environ.setdefault("CLASSROOM_LOCK_FILE", "/tmp/otaconskeep-classroom-dryrun/classroom.publish.lock")
os.environ.setdefault("LLM_TIMEOUT_SEC", "1200")
os.environ.setdefault("LLM_MAX_REPAIR_ATTEMPTS", "3")

from lib import load_config, JsonLogger, new_run_id, publication_lock, atomic_write_json, utc_now
from lib.curriculum import next_core_batch, discover_existing_classes
from lib.models import chat, extract_json_object, ModelError, WeakModelError
from validate_lessons import validate_batch, validate_bundle
from review_lessons import llm_review
from render_lessons import write_bundle_to_pack
from validate_lessons import validate_rendered_nav
from publish_lessons import make_zip
from run_dry_batch import preview_build
from generate_lessons import WRITER_PROMPT, normalize_bundle

EXPECTED_TITLES = [
    "Linux Filesystem and Navigation",
    "Shell Pipes and Redirection",
    "Users, Groups, Permissions, and Least Privilege",
    "Processes, Signals, and systemd",
    "Logs and journalctl",
    "SSH Keys and Safe Hardening",
]


def generate_one(cfg, class_id, title, logger, attempt=0, prior_errors: str = ""):
    logger.event("generate", class_id=class_id, attempt=attempt, model=cfg.writer_model)
    repair_note = ""
    if prior_errors:
        repair_note = (
            "\nPrevious attempt failed validation. Fix these issues and keep enums exact:\n"
            f"{prior_errors}\n"
            "difficulty must be exactly one of: beginner|intermediate|advanced (lowercase).\n"
            "lab_risk must be exactly one of: low|medium|high (lowercase single word).\n"
        )
    content, resolved = chat(
        cfg,
        model=cfg.writer_model,
        messages=[
            {
                "role": "system",
                "content": "You write rigorous Homelab Academy lessons as pure JSON matching the schema. No markdown fences.",
            },
            {"role": "user", "content": WRITER_PROMPT.format(class_id=class_id, title=title) + repair_note},
        ],
        temperature=0.2,
        max_tokens=12000,
    )
    if any(w in resolved.lower() for w in cfg.weak_prefixes):
        raise WeakModelError(f"resolved weak model {resolved}")
    logger.event("generate_resolved", class_id=class_id, resolved_model=resolved)
    bundle = normalize_bundle(extract_json_object(content))
    bundle["class_id"] = class_id
    bundle["title"] = title
    bundle["schema_version"] = "1.0"
    bundle["_meta"] = {
        "writer_requested": cfg.writer_model,
        "writer_resolved": resolved,
        "attempt": attempt,
    }
    return bundle


def main():
    cfg = load_config()
    for d in (cfg.state_dir, cfg.log_dir, cfg.staging_dir, cfg.artifact_dir):
        d.mkdir(parents=True, exist_ok=True)
    run_id = os.environ.get("LIVE_DRY_RUN_ID") or new_run_id("live_dry")
    logger = JsonLogger(cfg.log_dir / f"{run_id}.jsonl", run_id, "live_writer_dry")
    before = discover_existing_classes(cfg.pack_dir)
    evidence = Path("/tmp/otaconskeep-classroom-dryrun/evidence") / run_id
    evidence.mkdir(parents=True, exist_ok=True)
    drafts_dir = evidence / "drafts"
    drafts_dir.mkdir(parents=True, exist_ok=True)
    try:
        with publication_lock(cfg, logger):
            batch = next_core_batch(cfg)
            expected = [b["class_id"] for b in batch]
            titles = [b["title"] for b in batch]
            assert expected == [16, 17, 18, 19, 20, 21], expected
            assert titles == EXPECTED_TITLES, titles
            bundles = []
            for item in batch:
                draft_path = drafts_dir / f"class_{item['class_id']:02d}.json"
                if draft_path.is_file() and os.environ.get("LIVE_DRY_RESUME", "1") == "1":
                    try:
                        b = normalize_bundle(json.loads(draft_path.read_text(encoding="utf-8")))
                        fails = validate_bundle(cfg, b, existing_titles={m["title"] for m in before.values()})
                        if not fails and int(b["class_id"]) == item["class_id"] and b["title"] == item["title"]:
                            logger.event("resume_draft", class_id=item["class_id"], path=str(draft_path))
                            bundles.append(b)
                            continue
                    except Exception as e:
                        logger.event("resume_draft_invalid", class_id=item["class_id"], error=str(e)[:200])
                last_err = None
                prior = ""
                for attempt in range(cfg.max_repair + 1):
                    try:
                        b = generate_one(cfg, item["class_id"], item["title"], logger, attempt, prior_errors=prior)
                        atomic_write_json(drafts_dir / f"class_{item['class_id']:02d}.raw.json", b)
                        fails = validate_bundle(cfg, b, existing_titles={m["title"] for m in before.values()})
                        if fails:
                            atomic_write_json(drafts_dir / f"class_{item['class_id']:02d}.invalid.json", {"fails": fails, "bundle": b})
                            prior = "; ".join(fails[:12])
                            raise ModelError("validation: " + prior)
                        atomic_write_json(draft_path, b)
                        bundles.append(b)
                        last_err = None
                        break
                    except (ModelError, WeakModelError, json.JSONDecodeError, TypeError, ValueError) as e:
                        last_err = e
                        logger.event("repair", class_id=item["class_id"], error=str(e)[:300])
                        time.sleep(2)
                if last_err:
                    raise last_err
            v = validate_batch(cfg, bundles, expected_ids=expected)
            if not v["ok"]:
                raise ModelError("batch validation failed: " + "; ".join(v.get("failures", [])[:12]))
            reviews = []
            for b in bundles:
                rev = llm_review(cfg, b)
                critic = str(rev.get("critic") or rev.get("resolved_model") or "")
                if any(w in critic.lower() for w in cfg.weak_prefixes):
                    raise WeakModelError(f"critic weak: {critic}")
                rev["class_id"] = b["class_id"]
                reviews.append(rev)
                logger.event(
                    "critic_done",
                    class_id=b["class_id"],
                    pass_=bool(rev.get("pass")),
                    average=rev.get("average"),
                    critic=critic,
                )
            review = {
                "ok": all(r.get("pass") and r.get("average", 0) >= cfg.critic_min for r in reviews),
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
            from lib.module06 import write_complete_module06

            write_complete_module06(staging, bundles)
            nav = validate_rendered_nav(cfg, expected, staging)
            zpath = make_zip(cfg.artifact_dir, run_id, staging, bundles, v, review)
            build = preview_build(cfg, staging, run_id)
            after = discover_existing_classes(cfg.pack_dir)
            report = {
                "ok": v["ok"] and review["ok"] and not nav and build["ok"] and before == after,
                "run_id": run_id,
                "expected_class_ids": expected,
                "titles": [b["title"] for b in bundles],
                "writer": {
                    "requested": cfg.writer_model,
                    "base_url": cfg.omni_base,
                    "resolved": [b.get("_meta", {}).get("writer_resolved") for b in bundles],
                },
                "critic": {
                    "requested": cfg.critic_model,
                    "resolved": [r.get("critic") for r in reviews],
                    "independent": "gc/grok-4.6 (Grok) critic is a separate provider route from codex/gpt-5.6 writer",
                },
                "validation": v,
                "review": review,
                "nav_failures": nav,
                "redirects_would_be": redirects,
                "zip": str(zpath),
                "preview_build": {"ok": build["ok"], "path": build.get("preview_path")},
                "live_classroom_unchanged": before == after,
                "existing_class_count": len(after),
                "evidence_dir": str(evidence),
                "ts": utc_now(),
            }
            atomic_write_json(evidence / "DRY_RUN_REPORT.json", report)
            atomic_write_json(cfg.staging_dir / run_id / "DRY_RUN_REPORT.json", report)
            atomic_write_json(evidence / "bundles.json", bundles)
            print(
                json.dumps(
                    {
                        k: report[k]
                        for k in (
                            "ok",
                            "run_id",
                            "titles",
                            "writer",
                            "critic",
                            "live_classroom_unchanged",
                            "zip",
                            "preview_build",
                        )
                    },
                    indent=2,
                )
            )
            return 0 if report["ok"] else 1
    finally:
        logger.close()


if __name__ == "__main__":
    raise SystemExit(main())

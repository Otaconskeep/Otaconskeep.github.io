#!/usr/bin/env python3
"""Resume live dry-run from saved drafts: critic → pack → module06 → preview → zip."""
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

from lib import load_config, JsonLogger, publication_lock, atomic_write_json, utc_now
from lib.curriculum import discover_existing_classes
from lib.models import ModelError, WeakModelError, chat, extract_json_object
from validate_lessons import validate_batch, validate_bundle, validate_rendered_nav
from render_lessons import write_bundle_to_pack
from publish_lessons import make_zip
from run_dry_batch import preview_build
from generate_lessons import normalize_bundle
from review_lessons import RUBRIC_KEYS

RUN_ID = os.environ.get("LIVE_DRY_RUN_ID", "live_dry_20260922T161500Z_remap")
EXPECTED = [
    (16, "Linux Filesystem and Navigation"),
    (17, "Shell Pipes and Redirection"),
    (18, "Users, Groups, Permissions, and Least Privilege"),
    (19, "Processes, Signals, and systemd"),
    (20, "Logs and journalctl"),
    (21, "SSH Keys and Safe Hardening"),
]


def critic_one(cfg, bundle: dict, logger, attempt: int = 0) -> dict:
    slim = {
        k: bundle.get(k)
        for k in (
            "class_id",
            "title",
            "purpose",
            "learning_objectives",
            "teaching",
            "lab",
            "verification",
            "rollback",
            "security",
            "feynman",
            "quiz",
            "answer_key",
            "dangerous_commands",
        )
    }
    # Truncate teaching/lab for critic if huge
    for k in ("teaching", "lab"):
        if isinstance(slim.get(k), str) and len(slim[k]) > 6000:
            slim[k] = slim[k][:6000] + "\n…[truncated for critic]"
    prompt = (
        "Score this Homelab Academy lesson JSON on 0-100 for: "
        + ", ".join(RUBRIC_KEYS)
        + ". Return JSON {scores:{}, average:number, pass:boolean, repairs:[{section,reason}]}. "
        "Hard fail if placeholders, missing rollback, or unsafe undocumented commands."
    )
    logger.event("critic", class_id=bundle["class_id"], attempt=attempt, model=cfg.critic_model)
    content, resolved = chat(
        cfg,
        model=cfg.critic_model,
        messages=[
            {"role": "system", "content": "You are a strict curriculum critic. JSON only."},
            {"role": "user", "content": prompt + "\n\n" + json.dumps(slim)[:18000]},
        ],
        temperature=0,
        max_tokens=2000,
    )
    if any(w in resolved.lower() for w in cfg.weak_prefixes):
        raise WeakModelError(f"critic weak {resolved}")
    data = extract_json_object(content)
    data["critic"] = resolved
    logger.event(
        "critic_done",
        class_id=bundle["class_id"],
        pass_=bool(data.get("pass")),
        average=data.get("average"),
        critic=resolved,
    )
    return data


def main() -> int:
    cfg = load_config()
    cfg.llm_timeout = int(os.environ.get("LLM_TIMEOUT_SEC", "1200"))
    evidence = Path("/tmp/otaconskeep-classroom-dryrun/evidence") / RUN_ID
    drafts = evidence / "drafts"
    logger = JsonLogger(cfg.log_dir / f"{RUN_ID}.jsonl", RUN_ID, "live_writer_dry_finish")
    before = discover_existing_classes(cfg.pack_dir)
    try:
        with publication_lock(cfg, logger):
            bundles = []
            for cid, title in EXPECTED:
                path = drafts / f"class_{cid:02d}.json"
                if not path.is_file():
                    raise SystemExit(f"missing draft {path}")
                b = normalize_bundle(json.loads(path.read_text(encoding="utf-8")))
                b["class_id"] = cid
                b["title"] = title
                fails = validate_bundle(cfg, b, existing_titles={m["title"] for m in before.values()})
                if fails:
                    raise ModelError(f"class {cid} invalid: " + "; ".join(fails[:8]))
                bundles.append(b)
            v = validate_batch(cfg, bundles, expected_ids=[c for c, _ in EXPECTED])
            if not v["ok"]:
                raise ModelError("batch: " + "; ".join(v.get("failures", [])[:12]))
            reviews = []
            for b in bundles:
                last = None
                for attempt in range(4):
                    try:
                        rev = critic_one(cfg, b, logger, attempt)
                        reviews.append(rev)
                        last = None
                        break
                    except (ModelError, WeakModelError, json.JSONDecodeError) as e:
                        last = e
                        logger.event("critic_repair", class_id=b["class_id"], error=str(e)[:200])
                        time.sleep(3)
                if last:
                    raise last
            review = {
                "ok": all(r.get("pass") and float(r.get("average", 0)) >= cfg.critic_min for r in reviews),
                "reviews": reviews,
                "min_score": cfg.critic_min,
            }
            staging = cfg.staging_dir / RUN_ID / "pack"
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
            nav = validate_rendered_nav(cfg, [c for c, _ in EXPECTED], staging)
            zpath = make_zip(cfg.artifact_dir, RUN_ID, staging, bundles, v, review)
            build = preview_build(cfg, staging, RUN_ID)
            after = discover_existing_classes(cfg.pack_dir)
            report = {
                "ok": bool(v["ok"] and review["ok"] and not nav and build["ok"] and before == after),
                "run_id": RUN_ID,
                "expected_class_ids": [c for c, _ in EXPECTED],
                "titles": [b["title"] for b in bundles],
                "writer": {
                    "requested": cfg.writer_model,
                    "base_url": cfg.omni_base,
                    "resolved": [b.get("_meta", {}).get("writer_resolved") for b in bundles],
                    "note": "drafts produced by codex/gpt-5.6-sol-medium via OmniRoute :20128",
                },
                "critic": {
                    "requested": cfg.critic_model,
                    "resolved": [r.get("critic") for r in reviews],
                    "independent": "gc/grok-4.6 critic is a separate provider route from codex writer",
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
            atomic_write_json(cfg.staging_dir / RUN_ID / "DRY_RUN_REPORT.json", report)
            atomic_write_json(evidence / "bundles.json", bundles)
            print(json.dumps({k: report[k] for k in ("ok", "run_id", "titles", "writer", "critic", "live_classroom_unchanged", "zip", "preview_build")}, indent=2))
            return 0 if report["ok"] else 1
    finally:
        logger.close()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate lesson bundles via curated corpus or OmniRoute LLM (fail-closed)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# allow running from automation dir
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import JsonLogger, load_config, new_run_id, publication_lock, atomic_write_json
from lib.curated import get_curated
from lib.curriculum import next_core_batch
from lib.models import ModelError, WeakModelError, chat, extract_json_object
from validate_lessons import validate_batch


WRITER_PROMPT = """You are a Homelab Academy curriculum author for OtaconsKeep.
Return ONLY a JSON object matching the lesson schema fields.
No markdown fences. No placeholders. No fabricated benchmarks.
Class {class_id}: {title}
Required keys: schema_version(=1.0), class_id, title, track, difficulty, estimated_minutes,
lab_risk, purpose, prerequisites, learning_objectives, required_reading, terminology,
teaching (>=800 chars), architecture, lab, expected_results, verification, troubleshooting,
security, rollback, feynman, homework, quiz (>=5), answer_key, video_narration, references,
last_reviewed (YYYY-MM-DD), compatibility, dangerous_commands (array).
Array typing rules (strict):
- expected_results, verification, quiz, answer_key, required_reading, references: arrays of STRINGS only
- terminology: array of {{term, meaning}} objects
- troubleshooting: array of {{symptom, likely_cause, fix}} objects
- dangerous_commands: array of objects with command, warning, verification, rollback, failure_mode
- difficulty: exactly one of beginner|intermediate|advanced (lowercase single word)
- lab_risk: exactly one of low|medium|high (lowercase single word)
If the lesson mentions sshd_config, rm -rf, chmod 777, firewall tools, or curl|sh, include a complete
dangerous_commands entry for each controlled use. Labs mutate ONLY /opt/lab-classroom/class{class_id}/.
"""


def normalize_bundle(bundle: dict) -> dict:
    """Coerce common LLM shape drift into schema-compatible types."""

    def as_str(val) -> str:
        if val is None:
            return ""
        if isinstance(val, str):
            return val
        if isinstance(val, dict):
            # Prefer markdown-ish composition of values
            parts = []
            for k, v in val.items():
                if isinstance(v, (list, dict)):
                    parts.append(f"### {k}\n{as_str(v)}")
                else:
                    parts.append(f"### {k}\n{v}")
            return "\n\n".join(parts)
        if isinstance(val, list):
            return "\n".join(as_str(x) for x in val)
        return str(val)

    def as_str_list(val):
        out = []
        for item in val or []:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                for k in ("text", "check", "command", "item", "step", "q", "question", "a", "answer"):
                    if k in item and item[k]:
                        out.append(str(item[k]))
                        break
                else:
                    out.append(" — ".join(str(v) for v in item.values() if v))
            else:
                out.append(str(item))
        return out

    for key in (
        "title",
        "track",
        "purpose",
        "teaching",
        "architecture",
        "lab",
        "security",
        "rollback",
        "feynman",
        "homework",
        "video_narration",
        "compatibility",
    ):
        if key in bundle:
            bundle[key] = as_str(bundle.get(key))

    for key in (
        "expected_results",
        "verification",
        "quiz",
        "answer_key",
        "required_reading",
        "prerequisites",
        "learning_objectives",
        "references",
    ):
        if key in bundle:
            bundle[key] = as_str_list(bundle.get(key))

    # Enum / scalar drift
    diff = str(bundle.get("difficulty") or "").strip().lower()
    for cand in ("beginner", "intermediate", "advanced"):
        if cand in diff:
            bundle["difficulty"] = cand
            break
    risk = str(bundle.get("lab_risk") or "").strip().lower()
    for cand in ("high", "medium", "low"):  # high first so "low ... high" doesn't win wrongly — prefer exact token
        pass
    if re_search := __import__("re").search(r"\b(low|medium|high)\b", risk):
        bundle["lab_risk"] = re_search.group(1)
    if "estimated_minutes" in bundle:
        try:
            bundle["estimated_minutes"] = int(bundle["estimated_minutes"])
        except Exception:
            bundle["estimated_minutes"] = 75
    if "last_reviewed" in bundle:
        lr = str(bundle["last_reviewed"])
        m = __import__("re").search(r"(\d{4}-\d{2}-\d{2})", lr)
        if m:
            bundle["last_reviewed"] = m.group(1)
    return bundle


def generate_one(cfg, class_id: int, title: str, logger: JsonLogger) -> dict:
    if cfg.generator_backend == "curated":
        logger.event("generate", class_id=class_id, backend="curated")
        return get_curated(class_id)
    if cfg.generator_backend != "llm":
        raise RuntimeError(f"Unknown GENERATOR_BACKEND={cfg.generator_backend}")
    logger.event("generate", class_id=class_id, backend="llm", model=cfg.writer_model)
    content, resolved = chat(
        cfg,
        model=cfg.writer_model,
        messages=[
            {"role": "system", "content": "You write rigorous homelab lessons as pure JSON."},
            {"role": "user", "content": WRITER_PROMPT.format(class_id=class_id, title=title)},
        ],
        temperature=0.2,
        max_tokens=12000,
    )
    logger.event("generate_resolved", class_id=class_id, resolved_model=resolved)
    bundle = normalize_bundle(extract_json_object(content))
    bundle["class_id"] = class_id
    bundle["title"] = title
    bundle["schema_version"] = "1.0"
    bundle["_meta"] = {"writer_requested": cfg.writer_model, "writer_resolved": resolved}
    return bundle


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate next core lesson batch into staging JSON")
    ap.add_argument("--batch-type", default="core_am", choices=["core_am", "core_late", "manual"])
    ap.add_argument("--out", help="output bundles JSON path")
    ap.add_argument("--backend", help="override GENERATOR_BACKEND")
    ap.add_argument("--dry-run-config", action="store_true", help="force DRY_RUN semantics for paths")
    args = ap.parse_args()

    cfg = load_config()
    if args.backend:
        cfg.generator_backend = args.backend
    run_id = new_run_id("gen")
    log_path = cfg.log_dir / f"{run_id}.jsonl"
    # for uninstalled dry runs, fall back under /tmp
    try:
        cfg.log_dir.mkdir(parents=True, exist_ok=True)
        cfg.staging_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        cfg.log_dir = Path("/tmp/otaconskeep-classroom-dryrun/logs")
        cfg.staging_dir = Path("/tmp/otaconskeep-classroom-dryrun/staging")
        cfg.state_dir = Path("/tmp/otaconskeep-classroom-dryrun/state")
        cfg.artifact_dir = Path("/tmp/otaconskeep-classroom-dryrun/artifacts")
        cfg.lock_file = Path("/tmp/otaconskeep-classroom-dryrun/classroom.publish.lock")
        cfg.log_dir.mkdir(parents=True, exist_ok=True)
        cfg.staging_dir.mkdir(parents=True, exist_ok=True)

    logger = JsonLogger(log_path if log_path.parent.exists() else cfg.log_dir / f"{run_id}.jsonl", run_id, args.batch_type)
    try:
        with publication_lock(cfg, logger):
            batch = next_core_batch(cfg)
            if not batch:
                logger.event("complete", disposition="core_complete_noop", message="No missing core classes")
                return 0
            expected = [b["class_id"] for b in batch]
            logger.event("batch_selected", expected=expected, titles=[b["title"] for b in batch])
            bundles = []
            for item in batch:
                try:
                    bundles.append(generate_one(cfg, item["class_id"], item["title"], logger))
                except (WeakModelError, ModelError, KeyError) as e:
                    logger.event("generate_failed", class_id=item["class_id"], error=str(e), disposition="fail_closed")
                    return 2
            report = validate_batch(cfg, bundles, expected_ids=expected)
            out = Path(args.out) if args.out else cfg.staging_dir / run_id / "bundles.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_json(out, bundles)
            atomic_write_json(out.parent / "validation.json", report)
            logger.event("validated", ok=report["ok"], failures=report["failures"][:20])
            if not report["ok"]:
                logger.event("complete", disposition="validation_failed")
                return 1
            logger.event("complete", disposition="generated_ok", out=str(out))
            print(out)
            return 0
    except RuntimeError as e:
        if "lock busy" in str(e):
            return 75
        raise
    finally:
        logger.close()


if __name__ == "__main__":
    raise SystemExit(main())

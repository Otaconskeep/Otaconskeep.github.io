#!/usr/bin/env python3
"""Production core batch: writer → critic → validate → render → PR → wait → deploy verify.

Invoked only from run_scheduled_batch when DRY_RUN=0 and ACTIVATION_APPROVED is present.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib import (
    JsonLogger,
    atomic_write_json,
    load_config,
    new_run_id,
    utc_now,
)
from lib.content_security import scan_bundle_fields, scan_paths
from lib.curriculum import discover_existing_classes, next_core_batch, reconcile_manifest, save_manifest
from lib.models import ModelError, WeakModelError, chat, extract_json_object
from lib.publish_control import (
    mark_pr_open,
    record_deploy_verified,
    resume_or_create_batch,
    save_slot_state,
    verify_live_deploy,
    with_bounded_retries,
    RetryPolicy,
)
from generate_lessons import WRITER_PROMPT, normalize_bundle
from review_lessons import llm_review, heuristic_review
from render_lessons import write_bundle_to_pack
from validate_lessons import validate_batch, validate_bundle, validate_rendered_nav
from publish_lessons import update_class_index


GIT_AUTHOR_NAME = "Antonio G. Garcia"
GIT_AUTHOR_EMAIL = "230031249+Otaconskeep@users.noreply.github.com"


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = GIT_AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = GIT_AUTHOR_EMAIL
    env["GIT_COMMITTER_NAME"] = GIT_AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = GIT_AUTHOR_EMAIL
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True, check=check, env=env)


def activation_ok(cfg) -> tuple[bool, dict]:
    path = cfg.state_dir / "ACTIVATION_APPROVED"
    if not path.is_file():
        return False, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {"raw": path.read_text(encoding="utf-8")[:500]}
    return True, data if isinstance(data, dict) else {"raw": data}


def bundle_complete_enough(bundle: dict) -> list[str]:
    """Extra completeness gates beyond schema (catch truncated LLM JSON)."""
    fails: list[str] = []
    quiz = bundle.get("quiz") or []
    key = bundle.get("answer_key") or []
    if len(quiz) < 5:
        fails.append("COMPLETE: quiz < 5")
    if len(key) < len(quiz):
        fails.append("COMPLETE: answer_key shorter than quiz")
    for i, a in enumerate(key):
        if not str(a).strip() or str(a).strip().endswith(("Record re", "mid-", "...")):
            fails.append(f"COMPLETE: answer_key[{i}] thin/truncated")
    teaching = str(bundle.get("teaching") or "")
    if len(teaching) < 800:
        fails.append("COMPLETE: teaching too short")
    if teaching.rstrip().endswith(("Record re", " the", " a", " an", " to", " of", " and")):
        fails.append("COMPLETE: teaching looks truncated")
    for field in ("lab", "rollback", "security", "feynman", "homework"):
        val = str(bundle.get(field) or "")
        if len(val) < 80:
            fails.append(f"COMPLETE: {field} too short")
    return fails


def generate_one(cfg, class_id: int, title: str, logger: JsonLogger) -> dict:
    max_attempts = max(1, int(cfg.max_repair) + 2)
    prior = ""
    last_err = ""
    for attempt in range(max_attempts):
        logger.event("generate", class_id=class_id, attempt=attempt, model=cfg.writer_model)
        repair = ""
        if prior:
            repair = (
                "\nPrevious attempt failed validation. Fix these issues:\n"
                f"{prior}\n"
                "Return ONE complete JSON object. Every string field must be finished.\n"
                "quiz >= 5 strings; answer_key length MUST equal quiz length; no truncated sentences.\n"
                "difficulty beginner|intermediate|advanced; lab_risk low|medium|high.\n"
            )
        content, resolved = chat(
            cfg,
            model=cfg.writer_model,
            messages=[
                {
                    "role": "system",
                    "content": "You write rigorous Homelab Academy lessons as pure JSON matching the schema. No markdown fences. Never truncate fields.",
                },
                {"role": "user", "content": WRITER_PROMPT.format(class_id=class_id, title=title) + repair},
            ],
            temperature=0.2,
            max_tokens=16000,
        )
        if any(w in resolved.lower() for w in cfg.weak_prefixes):
            raise WeakModelError(f"resolved weak model {resolved}")
        try:
            bundle = normalize_bundle(extract_json_object(content))
        except Exception as e:
            prior = f"JSON_PARSE: {e}"
            last_err = prior
            logger.event("generate_parse_failed", class_id=class_id, error=str(e)[:200])
            continue
        bundle["class_id"] = class_id
        bundle["title"] = title
        bundle["schema_version"] = "1.0"
        bundle["_meta"] = {"writer_requested": cfg.writer_model, "writer_resolved": resolved}
        fails = validate_bundle(cfg, bundle, existing_titles=set())
        fails.extend(scan_bundle_fields(bundle))
        fails.extend(bundle_complete_enough(bundle))
        if not fails:
            return bundle
        prior = "; ".join(fails[:12])
        last_err = prior
        logger.event("generate_repair", class_id=class_id, failures=fails[:12])
    raise ModelError(f"class {class_id} failed validation after repairs: {last_err}")


def build_classroom_html(cfg, logger: JsonLogger) -> None:
    gen = cfg.classroom_dir / "_gen_from_pack.py"
    code = f"""
import runpy, sys
sys.path.insert(0, {str(cfg.classroom_dir)!r})
import _gen_from_pack as g
g.sync_github = lambda: print('skip sync_github')
g.main()
"""
    p = subprocess.run([sys.executable, "-c", code], cwd=str(cfg.classroom_dir), text=True, capture_output=True)
    logger.event("build_html", returncode=p.returncode, stderr_tail=(p.stderr or "")[-800:])
    if p.returncode != 0:
        raise RuntimeError(f"classroom HTML build failed: {(p.stderr or p.stdout)[-500:]}")


def prepare_lesson_branch(cfg, class_ids: list[int], logger: JsonLogger, state) -> str:
    site = Path(cfg.site_repo)
    branch = state.branch or f"automation/classroom-lessons-{class_ids[0]}-{class_ids[-1]}"
    run(["git", "fetch", "origin", "main"], cwd=site)
    run(["git", "checkout", "main"], cwd=site)
    run(["git", "reset", "--hard", "origin/main"], cwd=site)
    run(["git", "checkout", "-B", branch], cwd=site)
    state.branch = branch
    save_slot_state(cfg, state)
    logger.event("branch_ready", branch=branch)
    return branch


def create_or_resume_pr(cfg, class_ids: list[int], logger: JsonLogger, state) -> dict:
    site = Path(cfg.site_repo)
    branch = state.branch or f"automation/classroom-lessons-{class_ids[0]}-{class_ids[-1]}"
    if state.status == "pr_open" and state.pr_number:
        logger.event("resume_pr", pr=state.pr_number, branch=state.branch)
        return {"pr_number": state.pr_number, "pr_url": state.pr_url, "branch": state.branch, "resumed": True}

    paths = [
        "classroom/pack/classes",
        "classroom/pack/modules",
        "classroom/classes",
        "classroom/modules",
        "classroom/index.html",
        "classroom/automation/class_index.json",
    ]
    for p in paths:
        if (site / p).exists():
            run(["git", "add", "-A", p], cwd=site, check=False)

    st = run(["git", "status", "--porcelain"], cwd=site, check=False)
    if not st.stdout.strip():
        raise RuntimeError("no lesson files staged for PR")

    msg = f"Publish Homelab Academy Classes {class_ids[0]}–{class_ids[-1]}."
    run(["git", "commit", "-m", msg], cwd=site)
    run(["git", "push", "-u", "origin", "HEAD", "--force-with-lease"], cwd=site)

    body = f"""## Summary
- Controlled production canary: Classes {class_ids[0]}–{class_ids[-1]}
- Writer + critic + validation + security gates
- Lesson-content paths only (auto-merge eligible)

## Test plan
- [ ] classroom-validate
- [ ] classroom-preview
- [ ] Path-scoped auto-merge
- [ ] Cloudflare + GitHub Pages parity
"""
    pr = run(
        [
            "gh",
            "pr",
            "create",
            "--base",
            "main",
            "--head",
            branch,
            "--title",
            f"Publish Homelab Academy Classes {class_ids[0]}–{class_ids[-1]}",
            "--body",
            body,
        ],
        cwd=site,
    )
    url = pr.stdout.strip().splitlines()[-1].strip()
    num = int(url.rstrip("/").split("/")[-1])
    mark_pr_open(cfg, state, branch=branch, pr_number=num, pr_url=url)
    run(["gh", "pr", "merge", str(num), "--auto", "--merge"], cwd=site, check=False)
    logger.event("pr_opened", pr_number=num, pr_url=url, branch=branch)
    return {"pr_number": num, "pr_url": url, "branch": branch, "resumed": False}


def wait_for_merge(pr_number: int, logger: JsonLogger, timeout_sec: int = 3600) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        p = subprocess.run(
            ["gh", "pr", "view", str(pr_number), "--json", "state,mergedAt,statusCheckRollup"],
            text=True,
            capture_output=True,
        )
        if p.returncode != 0:
            time.sleep(20)
            continue
        data = json.loads(p.stdout)
        if data.get("state") == "MERGED":
            logger.event("pr_merged", pr=pr_number, at=data.get("mergedAt"))
            return True
        # Fail closed if required checks failed and not pending
        checks = data.get("statusCheckRollup") or []
        names = {c.get("name"): c for c in checks if isinstance(c, dict)}
        for req in ("classroom-validate", "classroom-preview"):
            c = names.get(req)
            if c and c.get("conclusion") == "FAILURE":
                logger.event("pr_checks_failed", pr=pr_number, check=req)
                return False
        time.sleep(25)
    logger.event("pr_merge_timeout", pr=pr_number)
    return False


def wait_cloudflare_deploy(head_sha: str, logger: JsonLogger, timeout_sec: int = 900) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        p = subprocess.run(
            [
                "gh",
                "run",
                "list",
                "--workflow=deploy-cloudflare.yml",
                "--branch=main",
                "--limit",
                "5",
                "--json",
                "databaseId,conclusion,status,headSha,url",
            ],
            text=True,
            capture_output=True,
        )
        if p.returncode == 0:
            for row in json.loads(p.stdout or "[]"):
                if row.get("headSha", "").startswith(head_sha[:7]) or row.get("headSha") == head_sha:
                    if row.get("status") == "completed" and row.get("conclusion") == "success":
                        logger.event("cloudflare_deploy_ok", url=row.get("url"), sha=head_sha)
                        return True
                    if row.get("conclusion") == "failure":
                        logger.event("cloudflare_deploy_failed", url=row.get("url"))
                        return False
        time.sleep(15)
    # Fallback: latest main deploy success after merge time
    p = subprocess.run(
        [
            "gh",
            "run",
            "list",
            "--workflow=deploy-cloudflare.yml",
            "--branch=main",
            "--limit",
            "1",
            "--json",
            "conclusion,status,url,headSha",
        ],
        text=True,
        capture_output=True,
    )
    if p.returncode == 0:
        rows = json.loads(p.stdout or "[]")
        if rows and rows[0].get("conclusion") == "success":
            logger.event("cloudflare_deploy_ok_latest", **rows[0])
            return True
    return False


def sync_github_pages(logger: JsonLogger) -> None:
    script = ROOT / "sync_public_pages.py"
    p = subprocess.run(
        [sys.executable, str(script), "--push"],
        text=True,
        capture_output=True,
    )
    logger.event("pages_sync", returncode=p.returncode, out=(p.stdout or "")[-500:], err=(p.stderr or "")[-500:])
    if p.returncode != 0:
        raise RuntimeError(f"GitHub Pages sync failed: {p.stderr or p.stdout}")


def run_production_batch(cfg, slot: str, logger: JsonLogger) -> int:
    ok, approval = activation_ok(cfg)
    if not ok:
        logger.event("blocked", disposition="missing_activation_approved")
        return 2
    if cfg.dry_run:
        logger.event("blocked", disposition="dry_run_blocks_schedule")
        return 0

    pending = next_core_batch(cfg)
    if not pending:
        logger.event("complete", disposition="core_complete_noop")
        return 0
    class_ids = [int(b["class_id"]) for b in pending]
    allowed = approval.get("canary_range") or approval.get("allowed_class_range")
    if allowed and class_ids != list(allowed):
        # Only enforce when approval scopes a canary range
        if set(class_ids) != set(int(x) for x in allowed):
            logger.event("blocked", disposition="outside_activation_scope", class_ids=class_ids, allowed=allowed)
            return 3

    state = resume_or_create_batch(cfg, slot, class_ids, logger=logger)
    if state.status == "deployed" and state.batch_ids == class_ids:
        logger.event("complete", disposition="already_deployed")
        return 0

    site = Path(cfg.site_repo)
    staging = cfg.staging_dir / f"{slot}_{class_ids[0]}_{class_ids[-1]}"
    staging.mkdir(parents=True, exist_ok=True)

    # Resume existing open PR
    if state.status == "pr_open" and state.pr_number:
        logger.event("resume_wait_merge", pr=state.pr_number)
        if not wait_for_merge(state.pr_number, logger):
            return 4
    else:
        state.status = "generating"
        save_slot_state(cfg, state)
        prepare_lesson_branch(cfg, class_ids, logger, state)

        bundles_path = staging / "bundles.json"
        bundles: list[dict] = []
        if bundles_path.is_file():
            try:
                bundles = json.loads(bundles_path.read_text(encoding="utf-8"))
                if [int(b["class_id"]) for b in bundles] != class_ids:
                    bundles = []
                else:
                    logger.event("resume_bundles", count=len(bundles))
            except Exception:
                bundles = []

        if not bundles:
            for item in pending:
                try:
                    bundles.append(generate_one(cfg, item["class_id"], item["title"], logger))
                except (ModelError, WeakModelError) as e:
                    logger.event("writer_failed", error=str(e)[:400], disposition="fail_closed")
                    state.status = "failed"
                    save_slot_state(cfg, state)
                    return 5
            atomic_write_json(bundles_path, bundles)

        # Critic with per-class repair (same class numbers — never skip ahead)
        reviews = []
        for i, b in enumerate(list(bundles)):
            attempts = 0
            while True:
                attempts += 1
                try:
                    rev = llm_review(cfg, b)
                except Exception as e:
                    logger.event("critic_llm_fallback", error=str(e)[:200], class_id=b["class_id"])
                    rev = heuristic_review(b)
                avg = float(rev.get("average") or 0)
                min_score = float(cfg.critic_min)
                if "pass" not in rev:
                    rev["pass"] = avg >= min_score
                if avg < min_score:
                    rev["pass"] = False
                if rev.get("pass"):
                    reviews.append(rev)
                    bundles[i] = b
                    break
                logger.event(
                    "critic_rejected",
                    class_id=b["class_id"],
                    attempt=attempts,
                    review=rev,
                    disposition="repair" if attempts <= cfg.max_repair else "fail_closed",
                )
                if attempts > cfg.max_repair:
                    state.status = "failed"
                    save_slot_state(cfg, state)
                    atomic_write_json(staging / "reviews.json", reviews + [rev])
                    return 6
                # Regenerate same class_id with critic repair notes
                repair_notes = json.dumps(rev.get("repairs") or rev, ensure_ascii=False)[:2500]
                try:
                    # inject prior errors into generate_one via temporary monkey by calling chat path
                    from generate_lessons import WRITER_PROMPT as _WP

                    prior = repair_notes
                    content, resolved = chat(
                        cfg,
                        model=cfg.writer_model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You write rigorous Homelab Academy lessons as pure JSON. No markdown fences.",
                            },
                            {
                                "role": "user",
                                "content": _WP.format(class_id=b["class_id"], title=b["title"])
                                + "\nCritic rejected previous draft. Fix ALL of these:\n"
                                + prior
                                + "\nEnsure answer_key has one entry per quiz question; no truncated fields.\n",
                            },
                        ],
                        temperature=0.2,
                        max_tokens=12000,
                    )
                    nb = normalize_bundle(extract_json_object(content))
                    nb["class_id"] = b["class_id"]
                    nb["title"] = b["title"]
                    nb["schema_version"] = "1.0"
                    fails = validate_bundle(cfg, nb, existing_titles=set())
                    fails.extend(scan_bundle_fields(nb))
                    if fails:
                        logger.event("repair_validation_failed", class_id=b["class_id"], failures=fails[:12])
                        continue
                    b = nb
                    bundles[i] = b
                    atomic_write_json(bundles_path, bundles)
                except Exception as e:
                    logger.event("repair_failed", class_id=b["class_id"], error=str(e)[:300])
                    continue
        atomic_write_json(staging / "reviews.json", reviews)
        atomic_write_json(bundles_path, bundles)

        v = validate_batch(cfg, bundles, expected_ids=class_ids)
        if not v["ok"]:
            logger.event("validation_failed", failures=v["failures"][:20], disposition="fail_closed")
            state.status = "failed"
            save_slot_state(cfg, state)
            return 7

        redirects = {}
        for b in bundles:
            paths = write_bundle_to_pack(cfg, b, cfg.pack_dir)
            if paths.get("redirect"):
                redirects[str(b["class_id"])] = paths["redirect"]
        nav = validate_rendered_nav(cfg, class_ids, cfg.pack_dir)
        if nav:
            logger.event("render_nav_failed", failures=nav)
            return 8
        update_class_index(cfg, redirects)
        build_classroom_html(cfg, logger)

        scan_roots = []
        for n in class_ids:
            scan_roots.extend((cfg.pack_dir / "classes").glob(f"{n:02d}_*.md"))
        scan_roots.extend((cfg.classroom_dir / "classes").glob("*.html"))
        sec = scan_paths(scan_roots)
        if sec:
            logger.event("security_failed", failures=sec[:20], disposition="fail_closed")
            return 9

        pr = create_or_resume_pr(cfg, class_ids, logger, state)
        if not wait_for_merge(int(pr["pr_number"]), logger):
            return 4

    # Refresh main after merge
    run(["git", "fetch", "origin", "main"], cwd=site)
    run(["git", "checkout", "main"], cwd=site)
    run(["git", "reset", "--hard", "origin/main"], cwd=site)
    sha = run(["git", "rev-parse", "HEAD"], cwd=site).stdout.strip()
    state.status = "deploy_pending"
    save_slot_state(cfg, state)

    if not wait_cloudflare_deploy(sha, logger):
        logger.event("blocked", disposition="cloudflare_deploy_failed")
        return 10

    sync_github_pages(logger)

    evidence = verify_live_deploy(
        urls=[
            "https://otaconskeep-site.otaconskeep.workers.dev/classroom/",
            "https://otaconskeep.github.io/classroom/",
        ],
        expect_class_min=class_ids[-1],
        logger=logger,
        policy=RetryPolicy(max_attempts=8, base_delay_sec=5.0),
    )
    if not evidence.get("ok"):
        logger.event("blocked", disposition="deploy_verify_failed", evidence=evidence)
        return 11

    record_deploy_verified(cfg, class_ids, evidence)
    state.status = "deployed"
    save_slot_state(cfg, state)

    man = reconcile_manifest(cfg)
    for n in class_ids:
        man.setdefault("entries", {})[str(n)] = {"status": "published", "at": utc_now(), "slot": slot}
    man["last_successful_batch"] = {"ids": class_ids, "slot": slot, "at": utc_now()}
    save_manifest(cfg, man)

    logger.event(
        "complete",
        disposition="published",
        class_ids=class_ids,
        pr=state.pr_url,
        sha=sha,
    )
    print(json.dumps({"disposition": "published", "class_ids": class_ids, "pr": state.pr_url, "sha": sha}, indent=2))
    return 0

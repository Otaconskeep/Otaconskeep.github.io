#!/usr/bin/env python3
"""Scheduled entrypoint — global lock; resume existing PR; production when activated.

AM and late share the same lock with news. Duplicate same-slot starts resume one batch/PR.
Numbering does not advance until deploy verification is recorded.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib import load_config, JsonLogger, new_run_id, publication_lock
from lib.curriculum import next_core_batch, reconcile_manifest, discover_existing_classes
from lib.publish_control import (
    load_slot_state,
    may_advance_numbering,
    next_expected_batches,
    resume_or_create_batch,
    save_slot_state,
)
from run_production_batch import activation_ok, run_production_batch


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", choices=["am", "late"], required=True)
    args = ap.parse_args()
    cfg = load_config()
    run_id = new_run_id(f"sched_{args.slot}")
    logger = JsonLogger(cfg.log_dir / f"{run_id}.jsonl", run_id, f"core_{args.slot}")
    try:
        with publication_lock(cfg, logger):
            man = reconcile_manifest(cfg)
            if man.get("core_complete"):
                logger.event("complete", disposition="core_complete_noop")
                return 0
            pending = next_core_batch(cfg)
            if not pending:
                logger.event("complete", disposition="core_complete_noop")
                return 0
            class_ids = [int(b["class_id"]) for b in pending]
            existing = discover_existing_classes(cfg.pack_dir)
            expected = next_expected_batches(max(existing) if existing else 0)
            logger.event("expected_batches", **expected)

            prior = load_slot_state(cfg, args.slot)
            if prior.status in {"merged", "deploy_pending"} and prior.batch_ids and prior.batch_ids != class_ids:
                if not may_advance_numbering(cfg, last_batch_ids=prior.batch_ids, logger=logger):
                    logger.event(
                        "blocked",
                        disposition="awaiting_prior_deploy_verify",
                        prior=prior.batch_ids,
                    )
                    return 0

            state = resume_or_create_batch(cfg, args.slot, class_ids, logger=logger)
            if state.status == "deployed" and state.fingerprint == f"batch:{','.join(map(str, class_ids))}":
                logger.event("complete", disposition="already_deployed", batch_ids=class_ids)
                print(json.dumps({"disposition": "already_deployed", "batch_ids": class_ids}, indent=2))
                return 0

            if cfg.dry_run:
                logger.event(
                    "blocked",
                    disposition="dry_run_blocks_schedule",
                    message="DRY_RUN=1 — scheduled publish disabled.",
                    batch_ids=class_ids,
                )
                save_slot_state(cfg, state)
                print(json.dumps({"disposition": "dry_run_blocks_schedule", "batch_ids": class_ids}, indent=2))
                return 0

            ok, approval = activation_ok(cfg)
            if not ok:
                logger.event(
                    "blocked",
                    disposition="activation_required",
                    message="Set DRY_RUN=0 and ACTIVATION_APPROVED before scheduled publish is permitted.",
                    batch_ids=class_ids,
                )
                print(json.dumps({"disposition": "activation_required", "batch_ids": class_ids}, indent=2))
                return 0

            logger.event("activation_present", approval_keys=list(approval.keys())[:12])
            # Production path (writer→critic→PR→deploy). Lock already held.
            return run_production_batch(cfg, args.slot, logger)
    except RuntimeError as e:
        if "lock busy" in str(e):
            print(json.dumps({"disposition": "lock_busy", "slot": args.slot}))
            return 75
        raise
    finally:
        logger.close()


if __name__ == "__main__":
    raise SystemExit(main())

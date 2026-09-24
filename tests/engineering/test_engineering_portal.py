#!/usr/bin/env python3
"""Automated tests for the OtaconsKeep Engineering portal (static site)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENG = ROOT / "engineering" / "index.html"
DATA = ROOT / "data" / "engineering"
VALIDATE = ROOT / "scripts" / "validate-engineering.py"


class EngineeringPortalTests(unittest.TestCase):
    def test_route_files_exist(self):
        self.assertTrue(ENG.is_file(), "engineering/index.html missing")
        self.assertTrue((ROOT / "assets" / "engineering.js").is_file())
        self.assertTrue((ROOT / "assets" / "engineering.css").is_file())

    def test_navigation_contains_engineering(self):
        html = ENG.read_text(encoding="utf-8")
        self.assertIn('href="/engineering/"', html)
        self.assertIn("OtaconsKeep System Engineering", html)
        self.assertIn("System Lifecycle, Architecture, Verification &amp; Validation", html)
        self.assertNotIn("AtaconsKeep", html)

    def test_home_nav_includes_engineering(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("/engineering/", home)

    def test_requirements_render_data(self):
        reqs = json.loads((DATA / "requirements.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(reqs["requirements"]), 5)
        ids = [r["id"] for r in reqs["requirements"]]
        self.assertTrue(any(i.startswith("REQ-SYS-") for i in ids))

    def test_risk_records(self):
        risks = json.loads((DATA / "risks.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(risks["risks"]), 3)
        for r in risks["risks"]:
            self.assertTrue(r["id"].startswith("RSK-"))

    def test_vcrm_inputs(self):
        tests = json.loads((DATA / "tests.json").read_text(encoding="utf-8"))
        self.assertTrue(any(t["id"].startswith("ST-") for t in tests["tests"]))

    def test_broken_xref_detection(self):
        # validator must fail if we inject a bad ref into a temp copy: unit-level check here
        reqs = json.loads((DATA / "requirements.json").read_text(encoding="utf-8"))
        linked = []
        for r in reqs["requirements"]:
            linked.extend(r.get("linked_tests") or [])
        tests = {t["id"] for t in json.loads((DATA / "tests.json").read_text())["tests"]}
        for tid in linked:
            self.assertIn(tid, tests, f"missing test ref {tid}")

    def test_missing_requirement_ref_detection(self):
        tests = json.loads((DATA / "tests.json").read_text(encoding="utf-8"))
        req_ids = {r["id"] for r in json.loads((DATA / "requirements.json").read_text())["requirements"]}
        for t in tests["tests"]:
            for rid in t.get("requirements") or []:
                self.assertIn(rid, req_ids, f"test {t['id']} refs missing {rid}")

    def test_no_fake_pass_without_evidence(self):
        tests = json.loads((DATA / "tests.json").read_text(encoding="utf-8"))
        for t in tests["tests"]:
            if re.match(r"(?i)^pass$", str(t.get("result") or "").strip()):
                self.assertTrue(t.get("evidence"), f"{t['id']} PASS without evidence")

    def test_benchmarks_empty_honest(self):
        b = json.loads((DATA / "benchmarks.json").read_text(encoding="utf-8"))
        self.assertEqual(b.get("benchmarks"), [])

    def test_behavioral_models_from_source(self):
        bm = json.loads((DATA / "behavioral_models.json").read_text(encoding="utf-8"))
        ids = {m["id"] for m in bm["models"]}
        self.assertIn("MOD-EMO-001", ids)
        self.assertIn("MOD-REL-001", ids)
        emo = next(m for m in bm["models"] if m["id"] == "MOD-EMO-001")
        names = {v["name"] for v in emo["state_variables"]}
        self.assertTrue({"jealousy", "trust", "attachment"} <= names)

    def test_no_private_secrets_in_public_data(self):
        blob = ""
        for p in DATA.glob("*.json"):
            blob += p.read_text(encoding="utf-8")
        self.assertNotRegex(blob, r"\b192\.168\.\d+\.\d+\b")
        self.assertNotRegex(blob, r"AtaconsKeep")
        self.assertNotIn("BEGIN PRIVATE KEY", blob)

    def test_validator_script_passes(self):
        r = subprocess.run([sys.executable, str(VALIDATE)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK:", r.stdout)

    def test_diagrams_present(self):
        d = json.loads((DATA / "diagrams.json").read_text(encoding="utf-8"))
        types = {x["type"] for x in d["diagrams"]}
        for needed in ("bdd", "ibd", "sequence", "activity", "state", "vmodel", "context"):
            self.assertIn(needed, types)

    def test_js_has_filters_and_search(self):
        js = (ROOT / "assets" / "engineering.js").read_text(encoding="utf-8")
        self.assertIn("eng-search", js)
        self.assertIn("matchFilters", js)
        self.assertIn("computeMetrics", js)


if __name__ == "__main__":
    unittest.main()

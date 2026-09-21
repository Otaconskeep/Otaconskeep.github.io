#!/usr/bin/env python3
"""Validate OtaconsKeep public engineering data package.

Checks:
  - required files present
  - unique IDs
  - cross-references resolve
  - status vocabulary
  - forbidden secret patterns (private IPs, tokens, etc.)
  - product spelling: no AtaconsKeep
  - no fabricated PASS results in production JSON (PASS only allowed with evidence)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "engineering"

REQUIRED = [
    "meta.json",
    "overview.json",
    "requirements.json",
    "architecture.json",
    "interfaces.json",
    "risks.json",
    "tests.json",
    "evidence.json",
    "benchmarks.json",
    "releases.json",
    "issues.json",
    "models.json",
    "baselines.json",
    "hardware.json",
    "behavioral_models.json",
    "diagrams.json",
    "math.json",
    "analysis.json",
]

FORBIDDEN = [
    re.compile(r"AtaconsKeep", re.I),
    re.compile(r"\b192\.168\.\d+\.\d+\b"),
    re.compile(r"\b10\.\d+\.\d+\.\d+\b"),
    re.compile(r"\b172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+\b"),
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (RSA |OPENSSH )?PRIVATE KEY-----"),
]

STATUS_OK = {
    "Draft",
    "Design Intent",
    "Implemented",
    "Verification Pending",
    "Verified",
    "Failed",
    "Blocked",
    "Deprecated",
    "Open",
    "Mitigating",
    "Accepted",
    "Closed",
    "Monitoring",
    "Development",
    "Qualification",
    "Release Candidate",
    "Qualified",
    "Released",
    "Not yet published",
    "No data",
    "No engineering record has been published for this category.",
    "Design Intent / Implemented path",
    "Implemented path",
    "Implemented path (chat); creative optional",
    "Not a Lite guarantee",
}


def load_all():
    data = {}
    for name in REQUIRED:
        path = DATA / name
        if not path.is_file():
            raise SystemExit(f"MISSING {path}")
        data[name] = json.loads(path.read_text(encoding="utf-8"))
    return data


def collect_ids(data):
    ids = {}

    def add(i, kind, where):
        if not i:
            return
        if i in ids:
            raise AssertionError(f"duplicate ID {i} ({ids[i]} and {kind} in {where})")
        ids[i] = kind

    for r in data["requirements.json"].get("requirements", []):
        add(r["id"], "requirement", "requirements")
    for r in data["architecture.json"].get("elements", []):
        add(r["id"], "architecture", "architecture")
    for r in data["interfaces.json"].get("interfaces", []):
        add(r["id"], "interface", "interfaces")
    for r in data["risks.json"].get("risks", []):
        add(r["id"], "risk", "risks")
    for r in data["tests.json"].get("tests", []):
        add(r["id"], "test", "tests")
    for r in data["evidence.json"].get("evidence", []):
        add(r["id"], "evidence", "evidence")
    for r in data["issues.json"].get("issues", []):
        add(r["id"], "issue", "issues")
    for r in data["models.json"].get("models", []):
        add(r["id"], "model", "models")
    for r in data["baselines.json"].get("baselines", []):
        add(r["id"], "baseline", "baselines")
    for r in data["releases.json"].get("releases", []):
        add(r["id"], "release", "releases")
    for r in data["behavioral_models.json"].get("models", []):
        add(r["id"], "behavioral_model", "behavioral_models")
    for r in data["diagrams.json"].get("diagrams", []):
        add(r["id"], "diagram", "diagrams")
    for r in data.get("math.json", {}).get("worked_examples", []) or []:
        add(r["id"], "math_trace", "math")
    for r in data.get("analysis.json", {}).get("datasets", []) or []:
        add(r["id"], "dataset", "analysis")
    # overview EXT / ACT ids may overlap with interfaces intentionally — allow without uniqueness
    return ids


def resolve(ids, ref, ctx):
    if not ref:
        return
    if ref not in ids:
        # Allow overview context node ids and informal subsystem labels
        if ref.startswith(("EXT-", "ACT-", "DEP-", "TIER-", "HW-", "PAR-", "MOD-PROV")):
            return
        if ref in {"Creative Systems", "Public Expansion docs", "Engineering portal", "V&V", "Expansion", "Web UI"}:
            return
        raise AssertionError(f"unknown reference {ref!r} from {ctx}")


def check_xrefs(data, ids):
    for r in data["requirements.json"]["requirements"]:
        for a in r.get("linked_architecture") or []:
            resolve(ids, a, r["id"])
        for a in r.get("linked_risks") or []:
            resolve(ids, a, r["id"])
        for a in r.get("linked_tests") or []:
            resolve(ids, a, r["id"])
        for a in r.get("linked_models") or []:
            resolve(ids, a, r["id"])
        resolve(ids, r.get("allocated_subsystem"), r["id"])
        resolve(ids, r.get("parent"), r["id"])
        st = r.get("status")
        if st and st not in STATUS_OK and not st.startswith("Implemented"):
            # allow soft statuses already listed
            if st not in STATUS_OK:
                raise AssertionError(f"invalid status {st!r} on {r['id']}")

    for t in data["tests.json"]["tests"]:
        for a in t.get("requirements") or []:
            resolve(ids, a, t["id"])
        for a in t.get("risks") or []:
            resolve(ids, a, t["id"])
        for a in t.get("evidence") or []:
            resolve(ids, a, t["id"])
        result = str(t.get("result") or "")
        if re.search(r"^\s*PASS\s*$", result, re.I):
            if not (t.get("evidence") or []):
                raise AssertionError(f"{t['id']} claims PASS without evidence")

    for r in data["risks.json"]["risks"]:
        for a in r.get("linked_requirements") or []:
            resolve(ids, a, r["id"])
        for a in r.get("linked_tests") or []:
            resolve(ids, a, r["id"])

    for e in data["evidence.json"]["evidence"]:
        resolve(ids, e.get("associated_test"), e["id"])
        resolve(ids, e.get("associated_requirement"), e["id"])


def check_secrets(data):
    blob = json.dumps(data, ensure_ascii=False)
    for pat in FORBIDDEN:
        m = pat.search(blob)
        if m:
            raise AssertionError(f"forbidden pattern {pat.pattern!r} matched: {m.group(0)!r}")


def check_benchmarks_honest(data):
    benches = data["benchmarks.json"].get("benchmarks") or []
    if benches:
        for b in benches:
            if not b.get("result") and b.get("mean") is not None:
                raise AssertionError("benchmark has mean without result metadata")


def main():
    data = load_all()
    ids = collect_ids(data)
    check_xrefs(data, ids)
    check_secrets(data)
    check_benchmarks_honest(data)

    # Product name check on portal HTML
    html = (ROOT / "engineering" / "index.html").read_text(encoding="utf-8")
    if "AtaconsKeep" in html:
        raise AssertionError("AtaconsKeep spelling found in engineering/index.html")
    if "OtaconsKeep System Engineering" not in html:
        raise AssertionError("Expected portal title missing")

    print(f"OK: {len(REQUIRED)} files, {len(ids)} unique IDs, cross-refs valid, secrets clean")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as e:
        print("FAIL:", e, file=sys.stderr)
        sys.exit(1)

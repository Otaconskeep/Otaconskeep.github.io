#!/usr/bin/env python3
"""Normalize requirements to MBSE/SysML style: levels, shall-statements, V&V + risk fields."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "data" / "engineering" / "requirements.json"
RISK = ROOT / "data" / "engineering" / "risks.json"

METHOD_APPROACH = {
    "Test": "Execute documented procedure; compare results to acceptance criteria (G/W/T).",
    "Demonstration": "Operator walkthrough on representative hardware; record steps and outcome.",
    "Inspection": "Review configuration, UI, docs, or published artifacts against the shall-statement.",
    "Analysis": "Model, calculation, or design analysis mapped to the requirement; no fabricated PASS.",
}

# Prefixes that are typically L1 (system) when parent is null
L1_IDS = {
    "REQ-SYS-001",
    "REQ-FUNC-001",
    "REQ-HW-001",
    "REQ-PERF-001",
    "REQ-SEC-001",
    "REQ-DATA-001",
    "REQ-NET-001",
    "REQ-AI-001",
    "REQ-SW-001",
    "REQ-AVAIL-001",
}


def to_shall(text: str, title: str) -> str:
    t = (text or "").strip()
    if not t:
        return f"The system shall provide {title.lower()}."
    low = t.lower()
    if low.startswith("the system shall "):
        return "The system shall " + t[len("The system shall ") :]
    # Rewrite other actors into system shall
    for prefix in (
        "the installer shall ",
        "a soft-update shall ",
        "the expansion installer shall ",
        "codec shall ",
        "codec replies shall ",
        "voice input/output shall ",
        "when model routing fails, codec shall ",
        "when continuity modules are enabled, codec reply assembly shall ",
        "browser hard-refresh shall ",
        "conversation history shall ",
        "agent a's memory artifacts shall ",
        "on memory store read failure, the system shall ",
        "public docs shall ",
        "advanced operators shall ",
        "long conversation transcripts shall ",
        "emotional continuity state variables shall ",
        "hostile accrual and repair shall ",
        "idle time shall ",
        "repeated comparison events shall ",
        "each continuity-enabled agent shall ",
        "relationship edges shall ",
        "continuity state shall ",
        "public engineering and product copy shall ",
        "when emotion labels are displayed, selection shall ",
        "per-cycle or per-event affect deltas shall ",
        "adaptive output blend shall ",
        "teaching/synthetic continuity traces published on engineering shall ",
        "discrete emotional stage transitions may be analyzed",
        "model/capability routing shall ",
        "default model path shall ",
        "the default model path shall ",
        "if the selected backend is unreachable, routing shall ",
        "keeproute shall ",
        "automatic model pulls shall ",
        "public engineering benchmarks shall ",
        "when stt is enabled, backend selection shall ",
        "when tts is enabled, backend selection shall ",
        "engineering overview shall ",
        "published engineering data files shall ",
        "integrations requiring third-party credentials shall ",
        "premium seat sharing policy shall ",
        "services shall ",
        "public evid packs shall ",
        "release notes shall ",
        "default web ui cors/origin policy shall ",
        "public materials shall ",
        "expansion foundation shall ",
        "genome/video studio paths shall ",
        "foundation ready / degraded / failed meanings shall ",
        "expansion-gated features shall ",
        "expansion reruns shall ",
        "cold start duration shall ",
        "time-to-first-token shall ",
        "lite shall ",
        "behavioral verification tests shall ",
        "measured benchmark rows shall ",
        "benchmark plan shall ",
        "core shall ",
        "model runtime integration shall ",
        "installer os feature operations shall ",
        "discord integration shall ",
        "home assistant integration shall ",
        "api documentation shall ",
        "realtime channels, if any, shall ",
        "after unexpected process stop, restarting the core service shall ",
        "installer failures shall ",
        "service logs shall ",
        "with local model runtime available, codec text chat shall ",
        "engineering portal shall ",
        "vcrm shall ",
        "engineering json shall ",
        "engineering math shall ",
        "published risks shall ",
        "analysis datasets that are synthetic shall ",
        "requirements shall ",
        "engineering meta shall ",
        "requirements package shall ",
        "engineering shall ",
        "agent tool execution shall ",
        "public lite claims shall ",
        "when rex is in scope for a deployment, proposal states shall ",
        "a public discord invite for support shall ",
        "faq shall ",
        "about measurable-emotion section shall ",
        "home page shall ",
        "expansion status page shall ",
        "about shall ",
        "public models & data shall ",
        "continuity-enabled agents shall ",
        "docs shall ",
        "default sampling parameters shall ",
        "optional wan features (providers, discord) shall ",
        "corporate proxy/tls interception notes shall ",
        "design intent: local api should eventually support",
        "clamp and blend helpers shall ",
        "repository shall ",
        "requirement and risk statuses shall ",
        "public engineering site shall ",
        "sysml diagrams shall ",
        "default lite path shall ",
        "a discrete nvidia gpu shall ",
        "public materials shall ",
        "only gpus actually measured may",
        "expansion shall ",
        "agents shall ",
        "lite docs shall ",
        "command center shall ",
        "deleting an agent shall ",
        "fresh lite install shall ",
        "destructive tools shall ",
        "releases shall ",
        "system models shall ",
        "primary codec input shall ",
        "engineering portal text shall ",
        "site topnav shall ",
        "switching the active agent in codec shall ",
        "the default codec/command center endpoint shall ",
    ):
        if low.startswith(prefix):
            rest = t[len(prefix) :]
            # special cases already starting mid-sentence
            if prefix.startswith("design intent"):
                return "The system shall document " + rest[0].lower() + rest[1:] if rest else t
            if prefix.startswith("only gpus"):
                return "The system shall ensure " + t[0].lower() + t[1:]
            if prefix.startswith("discrete emotional"):
                return "The system shall allow " + t[0].lower() + t[1:]
            if not rest:
                return f"The system shall satisfy {title}."
            return "The system shall " + rest[0].lower() + rest[1:]
    if " shall " in low:
        # e.g. "Engineering Model Provenance shall state..."
        idx = low.index(" shall ")
        rest = t[idx + len(" shall ") :]
        return "The system shall " + rest[0].lower() + rest[1:]
    if low.startswith("design intent:"):
        return "The system shall support the following design intent: " + t.split(":", 1)[1].strip()
    # Generic wrap
    body = t[0].lower() + t[1:] if t[0].isupper() else t
    if not body.endswith("."):
        body += "."
    return "The system shall ensure that " + body


def risk_level_label(score: int | None) -> str:
    if score is None:
        return "None"
    if score >= 15:
        return "Critical"
    if score >= 9:
        return "High"
    if score >= 6:
        return "Medium"
    if score >= 3:
        return "Low"
    return "Negligible"


def main() -> None:
    data = json.loads(REQ.read_text(encoding="utf-8"))
    risks = {r["id"]: r for r in json.loads(RISK.read_text(encoding="utf-8"))["risks"]}
    by_id = {r["id"]: r for r in data["requirements"]}

    # Ensure L1 parents exist for orphaned mid-level families
    family_l1 = {
        "INST": "REQ-SYS-001",
        "CODEC": "REQ-FUNC-001",
        "MEM": "REQ-DATA-001",
        "BEH": "REQ-FUNC-001",
        "ROUTE": "REQ-FUNC-001",
        "SEC": "REQ-SEC-001",
        "EXP": "REQ-FUNC-001",
        "PERF": "REQ-PERF-001",
        "IF": "REQ-SYS-001",
        "REL": "REQ-SYS-001",
        "ENG": "REQ-SW-001",
        "TOOL": "REQ-FUNC-001",
        "OPS": "REQ-SYS-001",
        "AI": "REQ-AI-001",
        "NET": "REQ-NET-001",
        "SW": "REQ-SW-001",
        "DATA": "REQ-DATA-001",
        "HW": "REQ-HW-001",
        "FUNC": "REQ-SYS-001",
        "AVAIL": "REQ-AVAIL-001",
        "MAINT": "REQ-SW-001",
        "USAB": "REQ-FUNC-001",
        "SYS": None,
    }

    for r in data["requirements"]:
        rid = r["id"]
        parts = rid.split("-")
        fam = parts[1] if len(parts) >= 2 else ""
        parent = r.get("parent")
        if parent and parent not in by_id:
            parent = None
            r["parent"] = None

        if rid in L1_IDS or (not parent and fam == "SYS"):
            level = 1
        elif not parent:
            # attach to family L1
            suggested = family_l1.get(fam)
            if suggested and suggested in by_id and suggested != rid:
                r["parent"] = suggested
                parent = suggested
                level = 2
            else:
                level = 2
        else:
            # depth from parent
            depth = 1
            walk = parent
            seen = set()
            while walk and walk in by_id and walk not in seen:
                seen.add(walk)
                depth += 1
                walk = by_id[walk].get("parent")
            level = min(3, depth)
            if level < 2:
                level = 2
            # if parent is L1, this is L2; if parent is L2, L3
            p = by_id.get(parent)
            if p and p.get("level") == 1:
                level = 2
            elif p and (p.get("level") == 2 or (p.get("parent") and p["parent"] in L1_IDS)):
                level = 3

        r["level"] = level
        r["text"] = to_shall(r.get("text", ""), r.get("title", "capability"))
        # Force L1 ids
        if rid in L1_IDS:
            r["level"] = 1
            r["parent"] = None

    # Second pass: fix levels from final parents
    for r in data["requirements"]:
        if r["id"] in L1_IDS:
            r["level"] = 1
            r["parent"] = None
            continue
        parent = r.get("parent")
        if not parent:
            r["level"] = 2
            continue
        p = by_id.get(parent)
        if not p:
            r["level"] = 2
            continue
        if p.get("level") == 1 or p["id"] in L1_IDS:
            r["level"] = 2
        else:
            r["level"] = 3

    for r in data["requirements"]:
        method = r.get("verification_method") or "Inspection"
        r["verification_method"] = method
        r["verification_approach"] = r.get("verification_approach") or METHOD_APPROACH.get(
            method, METHOD_APPROACH["Inspection"]
        )
        verified = str(r.get("status", "")).lower() == "verified"
        r["verified"] = "Yes" if verified else "No"
        if not r.get("verification_planned"):
            r["verification_planned"] = f"PROC-{r['id']}"
        if r.get("verification_executed") in (None, "", ", "):
            r["verification_executed"] = "Not executed"
        # Risk roll-up from first linked risk
        linked = r.get("linked_risks") or []
        if linked and linked[0] in risks:
            rk = risks[linked[0]]
            r["risk"] = rk["id"]
            r["risk_level"] = risk_level_label(rk.get("residual_risk"))
            r["risk_rationale"] = rk.get("residual_rationale") or rk.get("description") or rk.get("scenario") or ""
        else:
            r["risk"] = "None"
            r["risk_level"] = "None"
            r["risk_rationale"] = "No residual risk allocated to this requirement in the public risk register."
        # Verification rationale
        if verified:
            r["verification_rationale"] = (
                "Marked Verified because executed evidence is attached and acceptance criteria are met."
            )
        elif r.get("status") == "Implemented":
            r["verification_rationale"] = (
                "Implementation exists, but verification is not complete. Planned procedure has not produced Verified evidence."
            )
        elif r.get("status") == "Design Intent":
            r["verification_rationale"] = (
                "Design Intent only. No claim of implementation or verification until procedure and evidence exist."
            )
        elif r.get("status") == "Verification Pending":
            r["verification_rationale"] = (
                "Verification Pending. Procedure is planned; executed result and evidence are not yet attached."
            )
        else:
            r["verification_rationale"] = (
                f"Status is {r.get('status')}. Verification remains incomplete until evidence is attached."
            )

    # Sort: level, then id
    data["requirements"].sort(key=lambda x: (x.get("level", 9), x["id"]))
    data["baseline_id"] = "BL-REQ-0004"
    data["baseline_status"] = "Draft"
    data["methodology"] = "MBSE / SysML-aligned requirements hierarchy (Level 1 system, Level 2 subsystem, Level 3 component)"
    data["notes"] = (
        f"MBSE requirements baseline BL-REQ-0004 ({len(data['requirements'])} shall-statements). "
        "Level 1 = system, Level 2 = subsystem/capability, Level 3 = component/detail. "
        "All statements use 'The system shall'. Verified=Yes only with evidence. "
        "Columns include verification approach, planned/executed, risk level, and rationales."
    )
    REQ.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # stats
    levels = {}
    shall = 0
    for r in data["requirements"]:
        levels[r["level"]] = levels.get(r["level"], 0) + 1
        if r["text"].lower().startswith("the system shall"):
            shall += 1
    print("levels", levels, "shall", shall, "/", len(data["requirements"]))


if __name__ == "__main__":
    main()

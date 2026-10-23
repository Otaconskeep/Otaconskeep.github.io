#!/usr/bin/env python3
"""Critic/reviewer pass — structured rubric; hard gates cannot be overridden."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import load_config
from lib.models import ModelError, WeakModelError, chat, extract_json_object

RUBRIC_KEYS = [
    "technical_correctness",
    "completeness",
    "beginner_clarity",
    "lab_usefulness",
    "verification_quality",
    "rollback_quality",
    "security_quality",
    "feynman_quality",
    "quiz_alignment",
    "format_compliance",
]


def heuristic_review(bundle: dict) -> dict:
    scores = {}
    # deterministic baseline critic used when LLM critic unavailable/weak
    scores["technical_correctness"] = 90 if len(bundle.get("teaching", "")) > 800 else 50
    scores["completeness"] = 92 if all(bundle.get(k) for k in ("lab", "rollback", "quiz", "answer_key", "feynman")) else 40
    scores["beginner_clarity"] = 88 if "WARNING" in bundle.get("lab", "") or bundle.get("lab_risk") == "low" else 80
    scores["lab_usefulness"] = 90 if "/opt/lab-classroom/" in bundle.get("lab", "") else 55
    scores["verification_quality"] = 90 if len(bundle.get("verification") or []) >= 3 else 50
    scores["rollback_quality"] = 90 if len(bundle.get("rollback") or "") >= 80 else 45
    scores["security_quality"] = 88 if len(bundle.get("security") or "") >= 80 else 45
    scores["feynman_quality"] = 90 if "Explain" in bundle.get("feynman", "") else 50
    scores["quiz_alignment"] = 90 if len(bundle.get("answer_key") or []) >= len(bundle.get("quiz") or []) else 40
    scores["format_compliance"] = 90 if bundle.get("schema_version") == "1.0" else 30
    avg = sum(scores.values()) / len(scores)
    repairs = []
    if scores["lab_usefulness"] < 70:
        repairs.append({"section": "lab", "reason": "Lab must use disposable /opt/lab-classroom paths"})
    return {
        "scores": scores,
        "average": round(avg, 2),
        "pass": avg >= 85 and min(scores.values()) >= 70,
        "repairs": repairs,
        "critic": "heuristic",
    }


def llm_review(cfg, bundle: dict) -> dict:
    prompt = (
        "Score this Homelab Academy lesson JSON on 0-100 for: "
        + ", ".join(RUBRIC_KEYS)
        + ". Return JSON {scores:{}, average:number, pass:boolean, repairs:[{section,reason}]}. "
        "Hard fail if placeholders, missing rollback, or unsafe undocument commands."
    )
    content, resolved = chat(
        cfg,
        model=cfg.critic_model,
        messages=[
            {"role": "system", "content": "You are a strict curriculum critic. JSON only."},
            {"role": "user", "content": prompt + "\n\n" + json.dumps(bundle, ensure_ascii=False)[:100000]},
        ],
        temperature=0,
        max_tokens=2000,
    )
    data = extract_json_object(content)
    data["critic"] = resolved
    return data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundles", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--heuristic-only", action="store_true")
    args = ap.parse_args()
    cfg = load_config()
    bundles = json.loads(Path(args.bundles).read_text(encoding="utf-8"))
    reviews = []
    overall_pass = True
    for b in bundles:
        if args.heuristic_only or cfg.generator_backend == "curated":
            rev = heuristic_review(b)
        else:
            try:
                rev = llm_review(cfg, b)
            except (WeakModelError, ModelError):
                rev = heuristic_review(b)
                rev["note"] = "fell back to heuristic critic after model failure"
        rev["class_id"] = b["class_id"]
        if rev.get("average", 0) < cfg.critic_min or not rev.get("pass", False):
            overall_pass = False
        reviews.append(rev)
    out = {"ok": overall_pass, "min_score": cfg.critic_min, "reviews": reviews}
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": overall_pass, "count": len(reviews)}))
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

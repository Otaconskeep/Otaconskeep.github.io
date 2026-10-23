#!/usr/bin/env python3
"""Render lesson bundles into pack class markdown + module topic activity files."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from lib import Config, atomic_write_text, load_config, slugify
from lib.curriculum import load_roadmap, module_for_class, topic_slug


def _terms_table(terms: list[dict[str, str]]) -> str:
    lines = ["| Term | Meaning |", "|---|---|"]
    for t in terms:
        lines.append(f"| {t['term']} | {t['meaning']} |")
    return "\n".join(lines)


def _trouble_table(rows: list[dict[str, str]]) -> str:
    lines = ["| Symptom | Likely cause | Fix |", "|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['symptom']} | {r['likely_cause']} | {r['fix']} |")
    return "\n".join(lines)


def render_class_markdown(bundle: dict[str, Any]) -> str:
    n = int(bundle["class_id"])
    title = bundle["title"]
    obj = "; ".join(bundle["learning_objectives"])
    parts = [
        f"# Class {n} — {title}",
        "",
        f"**Learning objective:** {obj}",
        f"**Bloom level:** Understand / Apply",
        f"**Track:** {bundle['track']} · **Difficulty:** {bundle['difficulty']} · **Duration:** ~{bundle['estimated_minutes']} minutes · **Lab risk:** {bundle['lab_risk']}",
        f"**Build output:** {bundle['purpose']}",
        f"**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.",
        f"**Last reviewed:** {bundle['last_reviewed']}",
        f"**Compatibility:** {bundle['compatibility']}",
        "",
        "## Learning objective",
        "",
        *[f"- {x}" for x in bundle["learning_objectives"]],
        "",
        "## Why this matters",
        "",
        bundle["purpose"],
        "",
        "## Prerequisites",
        "",
        *[f"- {x}" for x in bundle["prerequisites"]],
        "",
        "## Required reading",
        "",
        *[f"- {x}" for x in bundle["required_reading"]],
        "",
        "## Prior-knowledge check",
        "",
        "Answer briefly before reading Instruction.",
        "",
        "1. What problem does this class prevent in a homelab?",
        "2. What disposable lab boundary will you use?",
        "3. What evidence will prove you succeeded?",
        "",
        "## Vocabulary",
        "",
        _terms_table(bundle["terminology"]),
        "",
        "## Instruction",
        "",
        bundle["teaching"],
        "",
        "## Architecture",
        "",
        bundle.get("architecture") or "_Not applicable beyond the process discussed in Instruction._",
        "",
        "## Worked example",
        "",
        "See the worked example embedded in Instruction; reproduce it on your disposable lab path.",
        "",
        "## Guided practice",
        "",
        "Complete the guided lab steps with hints allowed, then restate results in your own words.",
        "",
        "## Independent practice",
        "",
        bundle["homework"],
        "",
        "## Feynman teach-back",
        "",
        bundle["feynman"],
        "",
        "## Retrieval check",
        "",
        *[f"{i}. {q}" for i, q in enumerate(bundle["quiz"], 1)],
        "",
        "## Guided lab",
        "",
        bundle["lab"],
        "",
        "## Expected results",
        "",
        *[f"- {x}" for x in bundle["expected_results"]],
        "",
        "## Verification checkpoints",
        "",
        *[f"- [ ] {x}" for x in bundle["verification"]],
        "",
        "## Break/fix",
        "",
        _trouble_table(bundle["troubleshooting"]),
        "",
        "## Security considerations",
        "",
        bundle["security"],
        "",
        "## Rollback",
        "",
        bundle["rollback"],
        "",
        "## Video narration notes",
        "",
        bundle["video_narration"],
        "",
        "## References",
        "",
        *[f"- {x}" for x in bundle["references"]],
        "",
        "## Mastery gate",
        "",
        "- [ ] Objectives demonstrated with evidence",
        "- [ ] Feynman complete",
        "- [ ] Quiz self-scored ≥80%",
        "- [ ] Lab verification boxes checked",
        "- [ ] Rollback understood",
        "",
        "## Reflection",
        "",
        "1. What did I learn?",
        "2. What did I struggle with?",
        "3. How does this connect to earlier classes?",
        "",
        "## Spiral hook",
        "",
        "Return to this class whenever a later service fails for identity, process, log, remote access, update, or routing reasons covered here.",
        "",
    ]
    return "\n".join(parts)


def render_module_activities(bundle: dict[str, Any], module_title: str, topic_code: str) -> dict[str, str]:
    title = bundle["title"]
    objective = bundle["learning_objectives"][0]
    reading = "\n".join(
        [
            f"# Reading — {title}",
            "",
            f"**Module:** {module_title}",
            f"**Activity type:** Reading (Learn)",
            f"**Objective:** {objective}",
            "",
            "## Vocabulary",
            "",
            _terms_table(bundle["terminology"]),
            "",
            "## Instruction",
            "",
            bundle["teaching"],
            "",
            "## Architecture",
            "",
            bundle.get("architecture") or "",
            "",
            "## Required reading",
            "",
            *[f"- {x}" for x in bundle["required_reading"]],
            "",
            "## References",
            "",
            *[f"- {x}" for x in bundle["references"]],
            "",
        ]
    )
    lesson = "\n".join(
        [
            f"# Lesson {topic_code} — {title}",
            "",
            f"**Module:** {module_title}",
            f"**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)",
            f"**Learning objective:** {objective}",
            f"**Bloom level:** Understand / Apply",
            f"**Last reviewed:** {bundle['last_reviewed']}",
            "",
            "## Learning objective",
            "",
            objective,
            "",
            "## Why this matters",
            "",
            bundle["purpose"],
            "",
            "## Learn",
            "",
            "Complete the module reading first:",
            "",
            "- [Reading](./reading.md)",
            "",
            "## Feynman teach-back (required)",
            "",
            bundle["feynman"],
            "",
            "## Reflection",
            "",
            "1. What did I learn?",
            "2. What did I struggle with?",
            "3. How does this connect to earlier classes?",
            "",
            "## Topic path (do in order)",
            "",
            "| Step | Activity | Purpose |",
            "|---|---|---|",
            "| 1 | [Reading](./reading.md) | Learn |",
            "| 2 | This lesson (Feynman) | Explain |",
            "| 3 | [Lab](./lab.md) | Practice |",
            "| 4 | [Homework](./homework.md) | Apply |",
            "| 5 | [Quiz](./quiz.md) | Test |",
            "",
        ]
    )
    lab = "\n".join(
        [
            f"# Lab — {title}",
            "",
            f"**Module:** {module_title}",
            f"**Activity type:** Lab (Practice)",
            f"**Lab risk:** {bundle['lab_risk']}",
            f"**Objective:** {objective}",
            "",
            "## Before you start",
            "",
            *[f"- {x}" for x in bundle["prerequisites"]],
            "",
            "## Guided lab",
            "",
            bundle["lab"],
            "",
            "## Expected results",
            "",
            *[f"- {x}" for x in bundle["expected_results"]],
            "",
            "## Verification",
            "",
            *[f"- [ ] {x}" for x in bundle["verification"]],
            "",
            "## Break/fix",
            "",
            _trouble_table(bundle["troubleshooting"]),
            "",
            "## Security",
            "",
            bundle["security"],
            "",
            "## Rollback",
            "",
            bundle["rollback"],
            "",
        ]
    )
    homework = "\n".join(
        [
            f"# Homework — {title}",
            "",
            f"**Module:** {module_title}",
            f"**Activity type:** Homework / independent application",
            f"**Objective:** {objective}",
            "",
            "## Requirements",
            "",
            bundle["homework"],
            "",
            "## Submit / record",
            "",
            "- [ ] Evidence artifacts (secrets redacted)",
            "- [ ] Spiral connections written",
            "- [ ] Ready for topic quiz",
            "",
        ]
    )
    quiz = "\n".join(
        [
            f"# Quiz — {title}",
            "",
            f"**Module:** {module_title}",
            f"**Activity type:** Quiz / retrieval practice",
            f"**Target:** ≥80%",
            f"**Objective:** {objective}",
            "",
            "## Questions",
            "",
            *[f"{i}. {q}" for i, q in enumerate(bundle["quiz"], 1)],
            "",
            "## After scoring",
            "",
            "- Missed items → return to Reading → redo Feynman Retry → reattempt.",
            "",
            "<!-- answer key is maintained in instructor materials / automation batch report; not printed for students -->",
            "",
        ]
    )
    return {
        "reading.md": reading,
        "lesson.md": lesson,
        "lab.md": lab,
        "homework.md": homework,
        "quiz.md": quiz,
    }


def write_bundle_to_pack(cfg: Config, bundle: dict[str, Any], pack_root: Path) -> dict[str, str]:
    roadmap = load_roadmap(cfg)
    n = int(bundle["class_id"])
    fn = f"{n:02d}_{slugify(bundle['title'])}.md"
    class_path = pack_root / "classes" / fn
    atomic_write_text(class_path, render_class_markdown(bundle))

    mod = module_for_class(roadmap, n)
    paths = {"class_md": str(class_path)}
    if mod:
        slug = mod["slug"]
        # topic index within module
        classes = mod.get("classes", [])
        idx = classes.index(n) + 1 if n in classes else 1
        tslug = topic_slug(bundle["title"])
        topic_dir = pack_root / "modules" / slug / "topics" / f"{idx:02d}-{tslug}"
        topic_dir.mkdir(parents=True, exist_ok=True)
        acts = render_module_activities(bundle, mod["title"], f"{int(mod['id']):02d}.{idx:02d}")
        for name, text in acts.items():
            p = topic_dir / name
            atomic_write_text(p, text)
            paths[name] = str(p)
        # ensure MODULE.md stub exists / update topics list lightly
        module_md = pack_root / "modules" / slug / "MODULE.md"
        if not module_md.exists():
            atomic_write_text(
                module_md,
                "\n".join(
                    [
                        f"# Module {int(mod['id'])} — {mod['title']}",
                        "",
                        "**Design chain:** Backward Design → Bloom’s Taxonomy → Learn / Practice / Test / Reflect → Mastery → Spiral Review",
                        "**Feynman teach-back is required in every lesson.**",
                        "",
                        "## Topics",
                        "",
                        f"| ID | Topic |",
                        f"|---|---|",
                        f"| {int(mod['id']):02d}.{idx:02d} | [{bundle['title']}](topics/{idx:02d}-{tslug}/lesson.md) |",
                        "",
                    ]
                ),
            )
        # module assessment stubs (required for site builder when module is new)
        for act, heading in [
            ("project", "Module project"),
            ("module-quiz", "Module quiz"),
            ("exam", "Module exam"),
            ("remediation", "Remediation"),
        ]:
            ap = pack_root / "modules" / slug / f"{act}.md"
            if not ap.exists():
                atomic_write_text(
                    ap,
                    "\n".join(
                        [
                            f"# {heading} — {mod['title']}",
                            "",
                            f"**Module:** {mod['title']}",
                            "",
                            f"Complete after all topics in this module. Automation will enrich this {act.replace('-', ' ')} as the module matures.",
                            "",
                            "## Requirements",
                            "",
                            "- Demonstrate the module outcome with evidence",
                            "- Keep secrets out of screenshots",
                            "",
                        ]
                    ),
                )
        paths["module"] = slug
        paths["topic"] = f"{idx:02d}-{tslug}"
        paths["redirect"] = f"{slug}/topics/{idx:02d}-{tslug}/lesson.html"
    return paths


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--bundles", required=True)
    ap.add_argument("--out-pack", required=True)
    args = ap.parse_args()
    cfg = load_config()
    bundles = json.loads(Path(args.bundles).read_text(encoding="utf-8"))
    out = Path(args.out_pack)
    out.mkdir(parents=True, exist_ok=True)
    (out / "classes").mkdir(exist_ok=True)
    (out / "modules").mkdir(exist_ok=True)
    index = {}
    for b in bundles:
        index[str(b["class_id"])] = write_bundle_to_pack(cfg, b, out)
    print(json.dumps(index, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build true module curriculum from restructured class markdown.

Produces pack/modules/Mxx-name/ with:
  MODULE.md          — module hub (backward design, bloom, cycle, mastery, spiral)
  topics/Txx-slug/
    reading.md       — Learn (instruction + vocab + worked example)
    lesson.md        — Orient/Recall/Explain/Reflect (Feynman required)
    lab.md           — Practice (guided lab + break/fix)
    homework.md      — Apply (independent application)
    quiz.md          — Test (retrieval)
  project.md         — module integrated application
  module-quiz.md     — module retention quiz
  exam.md            — module mastery exam
  remediation.md     — re-teach weak areas
"""
from __future__ import annotations

import re
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
CLASSES = PACK / "classes"
MODULES = PACK / "modules"

MODULES_SPEC = [
    {
        "id": "01",
        "slug": "infrastructure",
        "title": "Infrastructure & Addressing",
        "outcome": "Student can virtualize a safe lab host, run persistent Compose services on isolated Docker networks, operate containers with update/rollback evidence, and read IPv4 address/mask/gateway to decide same-LAN vs via-gateway delivery.",
        "bloom_arc": "Remember/Understand (IPv4, VM basics) → Apply (Compose, ops) → Analyze (networking)",
        "spiral": "Every later module reuses Compose, networks, ops runbooks, and IP literacy when services cannot talk.",
        "gate": "Gate 1 — explain persistence, ports, DNS, logs, health, update/rollback, and basic IPv4 delivery with evidence.",
        "topics": [
            ("01", "01_PROXMOX_VIRTUALIZATION.md", "virtualization", "Virtual machines & Proxmox"),
            ("02", "02_DOCKER_COMPOSE.md", "compose", "Docker Compose & persistence"),
            ("03", "03_DOCKER_NETWORKING.md", "networking", "Docker networking"),
            ("04", "04_CONTAINER_OPERATIONS.md", "operations", "Container operations"),
            ("05", "15_IPV4_ADDRESSING.md", "ipv4", "IPv4 addresses & gateways"),
        ],
        "project": {
            "title": "Infrastructure foundation project",
            "task": "Deliver one Linux guest (or Proxmox VM) running a two-service Compose stack on an isolated user-defined network, with a one-page ops runbook (health/logs/update/rollback) and an IP worksheet (address, mask, gateway, same-LAN vs gateway decision for two sample hosts).",
            "evidence": "Screenshots/logs redacted; recreate-without-data-loss proof; DNS name call between services; IP math shown.",
        },
    },
    {
        "id": "02",
        "slug": "arr-media",
        "title": "ARR Media Automation",
        "outcome": "Student can connect Prowlarr to Sonarr/Radarr with service contracts, write and test a quality policy with Custom Formats, and automate profile sync with backup → dry-run → apply → drift → rollback — using authorized sources only.",
        "bloom_arc": "Apply (Prowlarr links) → Evaluate/Create (quality policy) → Evaluate (automation control loop)",
        "spiral": "Quality policy sentences and service contracts return whenever downloads mis-rank or sync drifts; networking/ops from Module 1 diagnose hop failures.",
        "gate": "Gate 2 — trace request→search→download→import; five-candidate ranking matches written policy; automation rollback proven.",
        "topics": [
            ("01", "05_PROWLARR_AND_ARR_FLOW.md", "prowlarr-flow", "Prowlarr & ARR request flow"),
            ("02", "06_TRASH_QUALITY_PROFILES.md", "trash-profiles", "TRaSH quality profiles"),
            ("03", "07_CONFIGURATION_AUTOMATION.md", "config-automation", "Configuration automation"),
        ],
        "project": {
            "title": "Media pipeline policy project",
            "task": "Stand up Prowlarr↔Sonarr/Radarr tests, write a household quality sentence, score five controlled candidates, then sync profiles through one authoritative automation path with dry-run and rollback evidence.",
            "evidence": "Service-contract table; candidate score sheet; dry-run output; rollback proof; legal boundary acknowledged.",
        },
    },
    {
        "id": "03",
        "slug": "home-assistant",
        "title": "Home Assistant & Secure Access",
        "outcome": "Student can model HA devices/entities/areas, build a testable trigger→condition→action automation with positive/negative cases, and provide authenticated remote access (or VPN) without publishing admin panels — with denial and backup/restore evidence.",
        "bloom_arc": "Apply (foundations) → Analyze/Create (automations) → Evaluate (threat model & remote access)",
        "spiral": "Entity names become voice targets in Module 4; remote-access boundary constrains n8n webhooks in Module 5.",
        "gate": "Gate 3 — backup/restore proven; automation traces exist; unauthorized remote admin denied.",
        "topics": [
            ("01", "08_HOME_ASSISTANT_FOUNDATIONS.md", "ha-foundations", "Home Assistant foundations"),
            ("02", "09_HOME_ASSISTANT_AUTOMATIONS.md", "ha-automations", "Home Assistant automations"),
            ("03", "10_SECURE_REMOTE_ACCESS.md", "secure-remote", "Secure remote access"),
        ],
        "project": {
            "title": "House logic + remote boundary project",
            "task": "Deploy HA with named entities/areas, one tested automation (positive + negative + restart), current backup with restore evidence, and a documented remote path that denies unauthorized clients.",
            "evidence": "Entity list; automation traces; backup artifact; denial test record; threat-model bullets.",
        },
    },
    {
        "id": "04",
        "slug": "local-voice",
        "title": "Local Voice Assistant",
        "outcome": "Student can instrument a local Assist pipeline stage-by-stage, deploy Whisper/Piper via Wyoming with measured tradeoffs, and prove wake→action→speech with the internet disconnected.",
        "bloom_arc": "Analyze (architecture) → Apply/Evaluate (STT/TTS) → Create/Evaluate (private speaker)",
        "spiral": "Uses HA entities/actions from Module 3 and Docker/network/ops from Module 1; failures must cite stage names forever after.",
        "gate": "Gate 4 — per-stage tests pass; disconnected end-to-end pass recorded.",
        "topics": [
            ("01", "11_LOCAL_VOICE_ARCHITECTURE.md", "voice-architecture", "Local voice architecture"),
            ("02", "12_WHISPER_PIPER_WYOMING.md", "whisper-piper", "Whisper, Piper & Wyoming"),
            ("03", "13_PRIVATE_SMART_SPEAKER.md", "private-speaker", "Private smart speaker"),
        ],
        "project": {
            "title": "Private speaker integration project",
            "task": "Complete progressive gates from mic/wake through STT, intent/action, TTS, and playback; then repeat the full path with WAN disconnected and attach stage evidence.",
            "evidence": "Stage test table; STT known-sentence; TTS known-phrase; disconnected pass artifact.",
        },
    },
    {
        "id": "05",
        "slug": "workflow-automation",
        "title": "Workflow Automation (n8n)",
        "outcome": "Student can run n8n on the lab network only, build an RSS digest that explains JSON item cardinality, and require human approval before any mutating agent/SSH action.",
        "bloom_arc": "Apply (workflow build) → Evaluate (approval boundaries & blast radius)",
        "spiral": "Depends on Module 1 networking/ops and Module 3 security boundaries; capstone reuses guarded automation evidence.",
        "gate": "Gate 5 — cardinality explained; credentials out of git; approval before mutation.",
        "topics": [
            ("01", "14_N8N_HOMELAB_AUTOMATION.md", "n8n-automation", "n8n homelab automation"),
        ],
        "project": {
            "title": "Guarded automation project",
            "task": "Ship an RSS digest workflow plus one mutate path that cannot run without explicit human approval; document item counts at each node and secret handling.",
            "evidence": "Workflow export (secrets stripped); approval screenshot/log; cardinality diagram; network exposure statement.",
        },
    },
]


def split_sections(md: str):
    lines = md.splitlines()
    title = ""
    i = 0
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        i = 1
        while i < len(lines) and not lines[i].strip():
            i += 1
    lead = []
    while i < len(lines) and not lines[i].startswith("## "):
        lead.append(lines[i])
        i += 1
    sections: dict[str, str] = {}
    order = []
    while i < len(lines):
        h2 = lines[i][3:].strip()
        i += 1
        body = []
        while i < len(lines) and not lines[i].startswith("## "):
            body.append(lines[i])
            i += 1
        sections[h2] = "\n".join(body).strip()
        order.append(h2)
    return title, "\n".join(lead).strip(), sections, order


def get(sections: dict[str, str], *names: str) -> str:
    lower = {k.lower(): v for k, v in sections.items()}
    for n in names:
        if n.lower() in lower:
            return lower[n.lower()]
    return ""


def meta_line(lead: str, key: str) -> str:
    for line in lead.splitlines():
        m = re.match(rf"\*\*{re.escape(key)}:\*\*\s*(.+)", line.strip(), re.I)
        if m:
            return m.group(1).strip()
    return ""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")
    print("wrote", path.relative_to(PACK))


def build_topic(mod: dict, topic_num: str, class_file: str, slug: str, topic_title: str, mod_dir: Path):
    raw = (CLASSES / class_file).read_text()
    title, lead, sections, _order = split_sections(raw)
    objective = meta_line(lead, "Learning objective") or get(sections, "Learning objective")
    bloom = meta_line(lead, "Bloom level") or "Apply"
    build = meta_line(lead, "Build output")
    why = get(sections, "Why this matters")
    prior = get(sections, "Prior-knowledge check")
    vocab = get(sections, "Vocabulary")
    instruction = get(sections, "Instruction")
    worked = get(sections, "Worked example")
    guided = get(sections, "Guided practice")
    independent = get(sections, "Independent practice")
    feynman = get(sections, "Feynman teach-back")
    retrieval = get(sections, "Retrieval check", "Knowledge check")
    lab = get(sections, "Guided lab")
    brk = get(sections, "Break / fix", "Break/fix")
    mistakes = get(sections, "Feedback / common mistakes", "Common mistakes")
    gate = get(sections, "Practical mastery gate", "Practical gate")
    reflect = get(sections, "Reflection")
    spiral = get(sections, "Spiral hook")
    correction = get(sections, "2026 correction")

    base = mod_dir / "topics" / f"{topic_num}-{slug}"
    rel_mod = f"Module {int(mod['id'])} — {mod['title']}"

    # READING — Learn
    reading = f"""# Reading — {topic_title}

**Module:** {rel_mod}  
**Topic:** {topic_num} — {topic_title}  
**Activity type:** Reading / reference (Learn)  
**Bloom focus:** {bloom}  
**Links to outcome:** {objective}

## Why this matters

{why}

## Vocabulary

{vocab}

## Core reading

{instruction}

## Worked example (study this)

{worked}
"""
    if correction:
        reading += f"\n## Current correction\n\n{correction}\n"
    reading += f"""
## Next

1. Open the **Lesson** for prior-knowledge check, guided practice, and **required Feynman teach-back**.
2. Then complete **Lab**, **Homework**, and **Quiz** for this topic.
"""
    write(base / "reading.md", reading)

    # LESSON — Orient / Recall / Demonstrate practice / Explain / Reflect
    lesson = f"""# Lesson {mod['id']}.{topic_num} — {topic_title}

**Module:** {rel_mod}  
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)  
**Learning objective:** {objective}  
**Bloom level:** {bloom}  
**Build output:** {build}  
**Mastery unlock for this topic:** reading done + Feynman complete + quiz ≥80% (when scored) + lab gate + homework submitted

## Learning objective

{objective}

## Why this matters

{why}

## Prior-knowledge check

{prior}

## Learn

Complete the module reading first:

- [Reading — {topic_title}](./reading.md)

Then review the worked example inside that reading (I do).

## Guided practice (We do)

{guided}

## Feynman teach-back (required)

{feynman}

## Reflection

{reflect}

## Spiral hook

{spiral}

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain / understand |
| 3 | [Lab](./lab.md) | Practice under guidance + break/fix |
| 4 | [Homework](./homework.md) | Independent apply |
| 5 | [Quiz](./quiz.md) | Test / retrieval |
"""
    write(base / "lesson.md", lesson)

    # LAB — Practice
    lab_md = f"""# Lab — {topic_title}

**Module:** {rel_mod}  
**Activity type:** Lab (Practice)  
**Objective:** {objective}

## Before you start

- Reading complete
- Lesson Feynman teach-back drafted (you may refine after the lab)

## Guided lab

{lab}

## Break / fix

{brk}

## Feedback / common mistakes

{mistakes}

## Lab gate

{gate}
"""
    write(base / "lab.md", lab_md)

    # HOMEWORK — Apply
    hw = f"""# Homework — {topic_title}

**Module:** {rel_mod}  
**Activity type:** Homework / independent application  
**Bloom move:** push from guided practice into independent Apply/Analyze  
**Objective:** {objective}

## Requirements

Complete **without** peeking at lab hints first. Then compare.

## Independent practice

{independent}

## Application task

1. Restate the learning objective as a checklist you can tick with evidence.
2. Produce the **build output** for this topic: {build or "see lesson build output"}
3. Attach workbook evidence (commands, redacted screenshots, tables).
4. Write three spiral connections: how this topic uses an earlier skill, and where a later module will reuse it.

## Submit / record

- [ ] Independent practice answers in workbook
- [ ] Evidence artifacts linked or pasted (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz
"""
    write(base / "homework.md", hw)

    # QUIZ — Test
    quiz = f"""# Quiz — {topic_title}

**Module:** {rel_mod}  
**Activity type:** Quiz / retrieval practice  
**Target:** ≥80% before topic mastery unlock  
**Objective:** {objective}

## Instructions

Close the reading. Write answers from memory. Then self-score.

## Questions

{retrieval}

## After scoring

- Missed items → return to **Reading** weak sections → redo **Feynman Retry** → reattempt missed questions.
- Passing score unlocks marking this topic complete on the module hub (still need lab gate + homework).
"""
    write(base / "quiz.md", quiz)


def module_quiz_questions(mod: dict) -> str:
    lines = [
        f"1. Restate the module outcome in your own words.",
        f"2. Name the Bloom progression for this module: {mod['bloom_arc']}",
        f"3. Which earlier module skill does this module spiral back to? Give one example.",
        f"4. What evidence unlocks the module mastery gate?",
        f"5. Describe one failure mode students hit in this module and how you diagnose it.",
    ]
    # add one per topic
    for i, (_n, _f, _s, title) in enumerate(mod["topics"], start=6):
        lines.append(f"{i}. What is the measurable learning objective of topic “{title}”?")
    return "\n".join(lines)


def build_module(mod: dict):
    mod_dir = MODULES / f"{mod['id']}-{mod['slug']}"
    if mod_dir.exists():
        # clean rebuild of generated tree
        import shutil

        shutil.rmtree(mod_dir)

    for topic_num, class_file, slug, topic_title in mod["topics"]:
        build_topic(mod, topic_num, class_file, slug, topic_title, mod_dir)

    topic_rows = "\n".join(
        f"| {mod['id']}.{t[0]} | {t[3]} | [Lesson](topics/{t[0]}-{t[2]}/lesson.md) · [Reading](topics/{t[0]}-{t[2]}/reading.md) · [Lab](topics/{t[0]}-{t[2]}/lab.md) · [Homework](topics/{t[0]}-{t[2]}/homework.md) · [Quiz](topics/{t[0]}-{t[2]}/quiz.md) |"
        for t in mod["topics"]
    )

    module_md = f"""# Module {int(mod['id'])} — {mod['title']}

**Design chain:** Backward Design → Bloom’s Taxonomy → Learn / Practice / Test / Reflect → Mastery → Spiral Review  
**Feynman teach-back is required in every lesson.**

## Backward design — module outcome

{mod['outcome']}

## Bloom arc

{mod['bloom_arc']}

## Module learning cycle

Orient → Recall → Learn (reading) → Demonstrate (worked example) → Guided practice → Independent practice / homework → **Feynman** → Lab → Quiz → Feedback → Module project → Module exam → Reflect

## Topics

| ID | Topic | Activities |
|---|---|---|
{topic_rows}

## Module assessments

| Activity | Purpose | Link |
|---|---|---|
| Module project | Integrated skill (Apply/Create) | [project.md](project.md) |
| Module quiz | Retention across topics | [module-quiz.md](module-quiz.md) |
| Module exam | Mastery verification | [exam.md](exam.md) |
| Remediation | Re-teach weak areas | [remediation.md](remediation.md) |

## Mastery gate (module unlock)

Do **not** unlock the next module because you clicked Next.

Required:

- [ ] Every topic reading completed
- [ ] Every topic **Feynman teach-back** completed
- [ ] Every topic quiz ≥80% (when scored) or remediated to pass
- [ ] Every topic lab gate checked with evidence
- [ ] Every topic homework recorded in workbook
- [ ] Module project submitted with evidence
- [ ] Module quiz passed
- [ ] Module exam passed (or instructor/self-check acceptance)
- [ ] Reflection written on module hub notes

**Stage gate statement:** {mod['gate']}

## Spiral review

{mod['spiral']}

## If you fail a gate

Feedback → targeted reading → new practice → redo Feynman Retry → reassessment (see [remediation.md](remediation.md)).
"""
    write(mod_dir / "MODULE.md", module_md)

    proj = mod["project"]
    write(
        mod_dir / "project.md",
        f"""# Module {int(mod['id'])} project — {proj['title']}

**Activity type:** Module project (integrated Apply/Create)  
**Module outcome:** {mod['outcome']}

## Task

{proj['task']}

## Evidence required

{proj['evidence']}

## Rubric (self-check)

| Criterion | Pass look-for |
|---|---|
| Tied to outcome | Deliverable clearly serves the module outcome |
| Bloom level | Shows Apply or higher — not copy/paste only |
| Spiral | Uses at least one prior-module skill explicitly |
| Evidence | Artifacts are reproducible and redacted |
| Honesty | Failures and fixes are documented |

## After submit

Take the [module quiz](module-quiz.md), then the [module exam](exam.md).
""",
    )

    write(
        mod_dir / "module-quiz.md",
        f"""# Module {int(mod['id'])} quiz — {mod['title']}

**Activity type:** Module quiz (retention / retrieval)  
**Target:** ≥80%

## Questions

{module_quiz_questions(mod)}
""",
    )

    exam_items = "\n".join(
        f"{i}. Perform or explain the objective for **{t[3]}** with evidence."
        for i, t in enumerate(mod["topics"], 1)
    )
    write(
        mod_dir / "exam.md",
        f"""# Module {int(mod['id'])} exam — {mod['title']}

**Activity type:** Module exam / practical mastery test  
**Outcome under test:** {mod['outcome']}

## Practical / written items

{exam_items}

{len(mod['topics']) + 1}. Complete or defend the [module project](project.md) under time-boxed review.
{len(mod['topics']) + 2}. Spiral item: show how a skill from an earlier module appears in your evidence.
{len(mod['topics']) + 3}. Feynman (module-level): explain the whole module outcome to a beginner; mark your weak spot; retry.

## Pass rule

All critical practical items pass with evidence; no unresolved critical safety/legal failures; Feynman module explanation complete.
""",
    )

    write(
        mod_dir / "remediation.md",
        f"""# Module {int(mod['id'])} remediation — {mod['title']}

**Activity type:** Review / remediation  
**Use when:** quiz <80%, lab gate failed, Feynman weak spot unresolved, or exam miss.

## Protocol

1. Name the failed objective (copy from the topic lesson).
2. Re-read only the weak reading sections.
3. Redo **Feynman Retry** for that topic.
4. Complete one new independent practice item (not the same answers copied).
5. Re-take the topic quiz or lab discriminating test.
6. Log what changed in the workbook.

## Spiral repair

{mod['spiral']}

If the failure was actually a prior-module skill, remediate that module topic first, then return here.
""",
    )


def write_index():
    rows = []
    for mod in MODULES_SPEC:
        rows.append(
            f"| {mod['id']} | [{mod['title']}]({mod['id']}-{mod['slug']}/MODULE.md) | {len(mod['topics'])} topics | {mod['gate'].split('—')[0].strip()} |"
        )
    write(
        MODULES / "README.md",
        f"""# Modules — Homelab Academy

This is the **authoritative course structure**.

Design chain: **Backward Design → Bloom’s Taxonomy → Learn / Practice / Test / Reflect → Mastery → Spiral Review**

Every **lesson** requires a **Feynman teach-back**.  
Every **topic** has separate **Reading · Lesson · Lab · Homework · Quiz**.  
Every **module** has **Project · Module quiz · Exam · Remediation**.

## Module list

| ID | Module | Topics | Gate |
|---|---|---|---|
{chr(10).join(rows)}
| — | [Capstone](../FINAL_CAPSTONE.md) | Course mastery | Final |

## How to move

1. Open the module `MODULE.md`
2. For each topic: Reading → Lesson (Feynman) → Lab → Homework → Quiz
3. Module project → module quiz → module exam
4. Only then unlock the next module
""",
    )


def main():
    MODULES.mkdir(parents=True, exist_ok=True)
    for mod in MODULES_SPEC:
        build_module(mod)
    write_index()
    print("DONE modules")


if __name__ == "__main__":
    main()

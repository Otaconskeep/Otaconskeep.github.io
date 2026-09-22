#!/usr/bin/env python3
"""Restructure every Homelab Academy class into the learning-system template.

Preserves original instructional/lab/quiz/gate content; inserts mandatory
pedagogy sections (objective, why, prior check, worked example, guided/
independent practice, Feynman, reflection, spiral).
"""
from __future__ import annotations

import re
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
CLASSES = PACK / "classes"

# Sections that stay as their own H2 (not folded into Instruction)
KEEP_AS_IS = {
    "vocabulary",
    "guided lab",
    "knowledge check",
    "practical gate",
    "2026 correction",
    "common mistakes",
}

LAB_ALIASES = re.compile(r"guided lab|lab —|lab -", re.I)
BREAK_ALIASES = re.compile(r"break|fix", re.I)
WHY_ALIASES = re.compile(r"why this|why you|mission|purpose|security objective|core principle", re.I)
OUTCOME_ALIASES = re.compile(r"what you will learn|outcomes|outcome", re.I)
VOCAB_ALIASES = re.compile(r"vocabulary|outcomes and vocabulary", re.I)
QUIZ_ALIASES = re.compile(r"knowledge check", re.I)
GATE_ALIASES = re.compile(r"practical gate", re.I)
MISTAKE_ALIASES = re.compile(r"common mistakes|troubleshooting", re.I)
CORRECTION_ALIASES = re.compile(r"2026 correction|correction", re.I)


PEDAGOGY = {
    "01": {
        "objective": "Given a host and a guest requirement, the learner can choose Type 1 vs Type 2 virtualization, create a working Linux guest (VirtualBox or Proxmox), and prove networking, DNS, and SSH with recorded evidence.",
        "bloom": "Apply",
        "why": "Without a safe practice machine, every later Docker, ARR, Home Assistant, and voice experiment risks your daily desktop. Virtualization is the sandboxed foundation the rest of the Academy builds on.",
        "prior": [
            "What is the difference between an operating system and an application?",
            "What does CPU, RAM, and disk do for a computer?",
            "Have you ever installed software that broke something on your main PC? What did you wish you had?",
        ],
        "worked": """**Bad approach:** Install experimental servers directly on your daily Windows/macOS desktop “to save time.”

**Better approach:** Create a disposable guest (Type 2 VirtualBox now, or Type 1 Proxmox on spare hardware), take a snapshot before risky changes, and prove SSH + DNS inside the guest before installing anything else.

**Why better:** Failure stays inside the guest. Snapshots give rollback. The host OS you use for school/work stays untouched.""",
        "guided": """With instructor/notes open, complete **one** of these (hints allowed):

1. Name whether VirtualBox on a laptop is Type 1 or Type 2 — and why.
2. List three pieces of evidence that prove a guest is useful for later Docker work (not “it boots”).
3. Sketch: Hardware → hypervisor → guest → network path to your LAN.""",
        "independent": """Without looking at the lesson, write:

1. Type 1 vs Type 2 in two sentences each.
2. When you would pick bridged networking vs NAT for a lab guest.
3. The exact evidence you will capture for the practical gate (commands or UI checks).""",
        "feynman_topic": "what a virtual machine is, and why hypervisors exist",
        "feynman_example_hint": "Explain a VM using an everyday analogy (for example: a playhouse in your backyard vs remodeling your only house).",
        "spiral": "You will reuse guests and snapshots in Class 2 (Docker inside a Linux VM), Class 3 (networks), Class 4 (ops), and every service class afterward. When voice or ARR “randomly breaks,” ask: did I change the guest, the bridge, or only the container?",
        "reflect_prompt": "Which virtualization path did you choose (VirtualBox vs Proxmox), what almost went wrong, and how does isolation protect later labs?",
    },
    "02": {
        "objective": "Given a multi-step `docker run` intent, the learner can write a Compose file with services, ports, environment, and persistent mounts, then recreate the stack without data loss.",
        "bloom": "Apply / Create",
        "why": "Shell history is not a system design. If your stack only exists as remembered commands, you cannot rebuild after failure — and every later ARR/HA/voice service will be fragile.",
        "prior": [
            "What is a container image versus a running container?",
            "Where should application data live if the container is deleted?",
            "Why might publishing a host port be both useful and dangerous?",
        ],
        "worked": """**Bad Compose intent:** No volumes; data lives in the container filesystem; recreate = wipe.

**Better:** Bind-mount or named volume for `/config` (or app data path), pin an image tag you can roll back, declare ports and env in YAML, and prove `docker compose down` + `up` keeps the data.""",
        "guided": "Convert one documented `docker run` (from the lesson) into Compose YAML with assistance. Check: service name, image, ports, env, volume, restart policy.",
        "independent": "Without hints, add a second service to the same Compose project that shares a network name and a documented volume path. Prove both survive recreate.",
        "feynman_topic": "why Docker Compose beats a long `docker run` for real systems",
        "feynman_example_hint": "Analogy: a recipe card (Compose) vs remembering a cooking performance (run commands).",
        "spiral": "Every later class assumes Compose + persistence. Class 3 adds networks; Class 4 adds update/rollback; Classes 5–14 drop more services into the same operational model.",
        "reflect_prompt": "Where did persistence almost fail, and what evidence proves recreate is safe?",
    },
    "03": {
        "objective": "Given two Compose services, the learner can place them on an isolated user-defined network, call one service by DNS name from the other, and explain host-port publish versus container-to-container traffic.",
        "bloom": "Analyze",
        "why": "Wrong networking is the #1 silent failure in ARR and Home Assistant stacks: ‘it works in the browser on the host’ but containers cannot see each other — or everything is published to the LAN by accident.",
        "prior": [
            "What does a port number identify?",
            "What is DNS used for?",
            "If two containers share a Docker network, do they need published host ports to talk to each other?",
        ],
        "worked": """**Bad:** Publish every container port to `0.0.0.0` on the host and point services at `localhost`.

**Better:** Put related services on `media_net` (or similar), use service DNS names for container-to-container calls, and publish host ports only for the UIs you intentionally open.""",
        "guided": "With the lesson open, trace one packet path: browser → host port → container A → DNS name → container B. Label each hop.",
        "independent": "Design a tiny two-service Compose network. Write the exact URL/hostname each side should use. Predict what breaks if you remove the shared network.",
        "feynman_topic": "Docker networks, DNS service discovery, and why localhost inside a container is not your PC",
        "feynman_example_hint": "Analogy: apartment intercoms (container DNS) vs listing your home phone number on a billboard (publishing ports).",
        "spiral": "Prowlarr→Sonarr (Class 5), HA add-ons (8–10), Wyoming voice (11–12), and n8n (14) all depend on this model. Class 15 (IPv4) explains same-LAN vs gateway when Docker networking meets your home router.",
        "reflect_prompt": "Where did you confuse host localhost with container localhost, and how will you check DNS next time?",
    },
    "04": {
        "objective": "Given a running Compose service, the learner can inspect health and logs, perform a controlled image update, and roll back to a known-good state with evidence.",
        "bloom": "Apply / Evaluate",
        "why": "Building once is easy. Operating for months — updates, failures, disk growth, bad tags — is where homelabs die. This class turns containers into a maintainable system.",
        "prior": [
            "What is the difference between desired state and observed state?",
            "Where do container logs go by default?",
            "Why is `:latest` risky for a service you care about?",
        ],
        "worked": """**Bad ops:** `docker compose pull && up -d` on Friday night with no backup and no pin.

**Better:** Record current image digest/tag → backup config volume → change one variable → observe health/logs → keep a rollback tag ready.""",
        "guided": "Walk the update checklist in the lab with notes open. Mark which step produces rollback evidence.",
        "independent": "Write a one-page runbook for *one* service: health check, log command, update steps, rollback steps, and when not to update.",
        "feynman_topic": "how to update a containerized service without gambling the whole lab",
        "feynman_example_hint": "Analogy: changing a tire with the spare already checked, versus swapping parts until the car starts.",
        "spiral": "You will use this runbook mindset for ARR profile changes (6–7), HA backups (8), remote access changes (10), voice model swaps (12), and n8n workflow edits (14).",
        "reflect_prompt": "What would you refuse to update without a backup, and what evidence proves your rollback works?",
    },
    "05": {
        "objective": "Given authorized indexer credentials and Compose networking, the learner can connect Prowlarr to Sonarr/Radarr, prove sync/tests, and trace a request through search → download client → import boundaries.",
        "bloom": "Apply / Analyze",
        "why": "Clicking through UIs without service contracts produces mystery failures. Prowlarr is the contract hub: if sync and tests are wrong, every later quality and automation class sits on sand.",
        "prior": [
            "Which Docker network will ARR apps use to reach each other?",
            "What evidence proves two apps are connected (not just ‘installed’)?",
            "What is the legal boundary for indexers and content in this course?",
        ],
        "worked": """**Bad:** Point Sonarr at Prowlarr using `localhost` from inside another container; skip indexer tests.

**Better:** Use the Compose DNS name + correct port, complete application sync, run indexer/app tests, and record pass/fail in the workbook before adding download clients.""",
        "guided": "Fill a service-contract row (URL, API key handling, network name, test button result) for Prowlarr→Sonarr with assistance.",
        "independent": "Trace one fictional request end-to-end on paper: Seerr/user → Sonarr → Prowlarr → indexer → download client → import path. Mark where hardlinks and categories matter.",
        "feynman_topic": "what Prowlarr does in the ARR flow and how service contracts prevent ‘it just works’ lies",
        "feynman_example_hint": "Analogy: a switchboard operator who must know each extension — not yelling names down a hallway.",
        "spiral": "Class 6 scores what Prowlarr finds; Class 7 automates those profiles; later troubleshooting always returns to ‘which hop failed?’",
        "reflect_prompt": "Which hop is hardest to prove, and what test button or log line is your evidence?",
    },
    "06": {
        "objective": "Given playback and storage constraints, the learner can write a plain-language quality policy, configure Custom Formats and cutoff/upgrade settings, and prove ranking on five controlled candidates.",
        "bloom": "Evaluate / Create",
        "why": "Installing Sonarr/Radarr is easy. Designing what they should prefer, reject, upgrade, and stop upgrading is the hard part — and wrong scores waste bandwidth, disk, and evenings.",
        "prior": [
            "What is a quality profile for?",
            "Why might the ‘highest resolution’ release be wrong for your TV?",
            "What should you back up before editing profiles?",
        ],
        "worked": """**Bad requirement:** “The library should look good.”

**Better requirement:** “Prefer 1080p WEB-DL or strong Blu-ray encodes; reject unwanted low-quality sources; prefer compatible surround audio; avoid DV-only releases on displays lacking DV; stop upgrading after target quality and CF score are reached.”

Now scoring can be tested against the sentence.""",
        "guided": "Score three sample release names together using a simple CF table (+/−). Explain the winner out loud.",
        "independent": "Write your household quality sentence. Score five candidates. Change exactly one rule and predict the new ranking before you click save.",
        "feynman_topic": "quality profiles vs Custom Formats vs cutoff/upgrade-until scores",
        "feynman_example_hint": "Analogy: ordering pizza — ‘make it good’ vs ‘large pepperoni, thin crust, ready in 20 minutes.’",
        "spiral": "Class 7 will automate these profiles. When automation drifts, you will re-test the same five-candidate table — the policy sentence remains the source of truth.",
        "reflect_prompt": "Which score almost violated your hardware constraints, and how did the five-candidate table catch it?",
    },
    "07": {
        "objective": "Given a known-good profile backup, the learner can choose one authoritative sync path, run dry-run/apply/rollback, and produce a drift report that matches the live apps.",
        "bloom": "Apply / Evaluate",
        "why": "Manual CF edits drift the moment you have two apps or two machines. Without an authoritative path and rollback, ‘automation’ becomes unexplainable chaos.",
        "prior": [
            "What is configuration drift?",
            "Why is a dry run required before apply?",
            "Where do secrets belong (and not belong)?",
        ],
        "worked": """**Bad:** Edit scores in the UI *and* in a sync tool with no single owner.

**Better:** Pick one authoritative path (for example Recyclarr *or* Notifiarr — not both fighting), backup → dry run → apply → verify → keep rollback.""",
        "guided": "Classify three changes as safe / review / dangerous with the lesson’s change table open.",
        "independent": "Write your control loop: backup → dry run → apply → verify → drift check → rollback trigger. Name the artifact you keep for each step.",
        "feynman_topic": "why ARR configuration needs an authoritative control loop",
        "feynman_example_hint": "Analogy: two people editing the same spreadsheet without track changes.",
        "spiral": "This control-loop pattern returns for HA dashboards/automations, reverse-proxy config, voice models, and n8n workflows — same discipline, different files.",
        "reflect_prompt": "What would drift look like in your lab tomorrow, and how would you detect it without guessing?",
    },
    "08": {
        "objective": "Given a Home Assistant install path, the learner can identify device/entity/area/integration, build a minimal dashboard, and prove backup + restore evidence.",
        "bloom": "Apply",
        "why": "Automations and voice are useless on a unnamed mess of entities. Foundations — objects, areas, backups — decide whether later classes are joyful or cursed.",
        "prior": [
            "What should you back up before experimenting?",
            "Why do friendly names matter for automations?",
            "What is an integration in plain language?",
        ],
        "worked": """**Bad:** Default entity ids everywhere (`sensor.temperature_3`) and no backup.

**Better:** Name by area + purpose, attach areas, create one dashboard card you can explain, and complete a backup you have actually restored once.""",
        "guided": "Map one physical device → integration → entity → area on paper with assistance.",
        "independent": "Rename/organize three entities and prove a backup artifact exists. Write the restore steps without powering off the wrong host.",
        "feynman_topic": "Home Assistant’s object model: device, entity, area, integration",
        "feynman_example_hint": "Analogy: a labeled breaker panel vs a box of mystery switches.",
        "spiral": "Class 9 automations target these entities. Classes 11–13 voice actions must speak the same names. Bad naming here becomes voice failure later.",
        "reflect_prompt": "Which naming choice will help future-you at 11pm, and did you actually test restore?",
    },
    "09": {
        "objective": "Given a plain-language automation requirement, the learner can implement trigger → condition → action logic and prove positive, negative, and failure cases with traces.",
        "bloom": "Analyze / Create",
        "why": "An automation that ‘usually works’ is a hazard. Testable logic — including when it must *not* fire — is how you trust the house.",
        "prior": [
            "What is a trigger vs a condition vs an action?",
            "Why might an automation fire twice?",
            "Where do you look when an automation misbehaves?",
        ],
        "worked": """**Bad requirement:** “Turn on the light when I’m home.”

**Better:** “When binary_sensor.front_door changes to on after sunset, if nobody is already marked home, turn on light.living_room and notify; do nothing if the light is already on; mode: single.”""",
        "guided": "Fill trigger/condition/action boxes for the lesson example together.",
        "independent": "Write positive test, negative test, and restart test for your automation. Capture a trace id or screenshot (secrets redacted).",
        "feynman_topic": "automations as testable logic, not magic",
        "feynman_example_hint": "Analogy: a vending machine — coin (trigger), ‘in stock’ (condition), dispense (action).",
        "spiral": "Voice (11–13) will call actions that must be safe under the same discipline. Monitoring hooks here feed later n8n digests (14).",
        "reflect_prompt": "Which negative test surprised you, and what did the trace reveal?",
    },
    "10": {
        "objective": "Given a threat model for admin UIs, the learner can choose VPN vs tunnel vs dangerous port-forward patterns, implement an authenticated remote path (or document VPN-only), and prove unauthorized denial plus rollback.",
        "bloom": "Evaluate / Apply",
        "why": "Exposing ARR, HA, or download admins to the public internet is how labs get owned. Remote access must be designed, not improvised.",
        "prior": [
            "What is authentication vs authorization?",
            "Why is a raw port-forward of an admin UI risky?",
            "What does ‘deny by default’ mean?",
        ],
        "worked": """**Bad:** Forward port 8123/8989 to the world because “I’ll use a strong password.”

**Better:** Prefer VPN or an authenticated tunnel pattern approved by the lesson; never expose download clients; prove an unauthorized client is denied; keep a rollback.""",
        "guided": "Compare VPN vs tunnel vs reverse-proxy using the lesson’s decision table with notes open.",
        "independent": "Write your threat model in five bullets and the denial test you will run. Execute the denial test and record evidence.",
        "feynman_topic": "why homelab admin panels must not be casually published to the internet",
        "feynman_example_hint": "Analogy: leaving your house keys in the front lawn vs a locked door with a known visitor process.",
        "spiral": "Voice satellites and n8n webhooks inherit this boundary. If Class 10 is weak, later ‘convenience’ features become attack surface.",
        "reflect_prompt": "What remote path did you choose, what did you explicitly refuse to expose, and what denial evidence do you have?",
    },
    "11": {
        "objective": "Given a voice request, the learner can draw the local Assist pipeline stages, instrument one test per stage, and isolate faults to mic, wake, STT, intent/action, TTS, or playback.",
        "bloom": "Analyze",
        "why": "End-to-end voice failures are opaque unless you can name the broken stage. Architecture-first debugging saves days of random reinstalls.",
        "prior": [
            "What does STT mean? TTS?",
            "Why test stages independently before the full pipeline?",
            "Which HA entities will voice actions target (from Class 8–9)?",
        ],
        "worked": """**Bad debug:** “Voice is broken” → reinstall everything.

**Better:** Stage table — mic level OK? wake fired? STT text correct? intent matched? action ran? TTS audio generated? speaker played? Fix the first failing stage only.""",
        "guided": "Fill the stage table for a sample phrase with assistance.",
        "independent": "Create your pipeline test record template with one pass/fail line per stage. Run it once on a known sentence.",
        "feynman_topic": "the local voice signal chain and fault isolation",
        "feynman_example_hint": "Analogy: a relay race — you must know which runner dropped the baton.",
        "spiral": "Classes 12–13 implement STT/TTS and the full speaker. Every failure report should cite a Class 11 stage name.",
        "reflect_prompt": "Which stage is hardest to observe, and what log or UI proves it?",
    },
    "12": {
        "objective": "Given CPU/RAM constraints, the learner can deploy local Whisper (STT) and Piper (TTS) via Wyoming, benchmark them separately, and record latency/quality tradeoffs before integration.",
        "bloom": "Apply / Evaluate",
        "why": "Voice feels ‘AI magic’ until a tiny host thrashes. Separate STT/TTS proof prevents false blame on Home Assistant or the satellite.",
        "prior": [
            "What network contract do Wyoming services need?",
            "Why might a larger Whisper model be a bad choice on a small NUC?",
            "What evidence proves STT alone works?",
        ],
        "worked": """**Bad:** Wire wake→STT→HA→TTS→speaker on day one with the biggest model.

**Better:** Prove STT with a known sentence; prove TTS with a known phrase; measure resource contention; only then integrate.""",
        "guided": "Run the STT known-sentence check with notes open; record text output.",
        "independent": "Benchmark two settings (or note why you cannot) and recommend one for your hardware with numbers.",
        "feynman_topic": "what Whisper, Piper, and Wyoming each contribute",
        "feynman_example_hint": "Analogy: ears (STT), mouth (TTS), and the headset cable standard (Wyoming).",
        "spiral": "Class 13 demands these providers still work with the internet disconnected. Keep the separate tests — you will reuse them under failure.",
        "reflect_prompt": "What latency/quality tradeoff did you accept, and what resource limit forced it?",
    },
    "13": {
        "objective": "Given working STT/TTS providers, the learner can integrate wake → action → spoken response and prove an internet-disconnected end-to-end pass with staged gates.",
        "bloom": "Create / Evaluate",
        "why": "A ‘local’ speaker that silently depends on the cloud is not local. The disconnected pass is the honesty test for the entire voice unit.",
        "prior": [
            "Which Class 11 stage tests already pass?",
            "What HA action will you trigger by voice?",
            "How will you prove the WAN is down during the test?",
        ],
        "worked": """**Bad acceptance:** “It worked once while Wi-Fi was up.”

**Better:** Progressive gates — wake only → STT → intent/action → TTS → full path — then repeat with internet disconnected and record the pass.""",
        "guided": "Execute the progressive integration gates in order with the checklist open.",
        "independent": "Run the disconnected exam. Document exact evidence (photos/logs redacted) for pass or the first failing stage.",
        "feynman_topic": "what ‘completely local smart speaker’ actually requires",
        "feynman_example_hint": "Analogy: a flashlight that still works when the power grid is down — vs one that needs a cloud app to turn on.",
        "spiral": "Capstone will ask for this evidence again. n8n (14) must not sneak cloud dependencies into the voice path without labeling them.",
        "reflect_prompt": "Did the disconnected test change your architecture confidence? What remains fragile?",
    },
    "14": {
        "objective": "Given a lab-only Docker network, the learner can run n8n, build an RSS digest workflow explaining item cardinality, and require human approval before any mutating Keep Agent / SSH action.",
        "bloom": "Apply / Evaluate",
        "why": "Automation without approval gates turns small mistakes into fast, wide damage — especially when agents can run commands.",
        "prior": [
            "What is a workflow node?",
            "Why might one RSS item become five messages?",
            "What must never be committed to git?",
        ],
        "worked": """**Bad:** Webhook → agent → shell mutate production with no approval.

**Better:** Digest/notify first; any mutate path requires explicit human approval; credentials stay out of git; explain JSON item cardinality before scaling.""",
        "guided": "Trace item count through a sample RSS → split → notify path with assistance.",
        "independent": "Draw your approval boundary on paper: which nodes may run unattended vs which need a human. Implement that boundary.",
        "feynman_topic": "why n8n automations need cardinality awareness and approval gates",
        "feynman_example_hint": "Analogy: a mail merge that accidentally sends 500 letters — vs a draft folder that waits for your stamp.",
        "spiral": "Capstone expects guarded automation evidence. Infrastructure classes (2–4) and security (10) are prerequisites for doing this safely.",
        "reflect_prompt": "Where could your workflow mutate something accidentally, and what gate stops it?",
    },
    "15": {
        "objective": "Given a host, the learner can read IPv4 address, mask, and gateway; explain network vs host bits; contrast classful charts with classless `/24` math; and decide same-LAN vs via-gateway delivery.",
        "bloom": "Understand / Apply",
        "why": "Every ‘why can’t these containers/hosts talk?’ ticket eventually becomes addressing. If you cannot read IP/mask/gateway, Docker and ARR networking stay superstition.",
        "prior": [
            "What does an IP address identify?",
            "What is a default gateway for?",
            "What is 127.0.0.1 used for?",
        ],
        "worked": """**Bad explanation:** “They’re on Wi-Fi so they can talk.”

**Better:** Compare address and mask; compute network ID; if same network → local delivery; else → send to gateway. Separate loopback and reserved ranges from LAN addresses.""",
        "guided": "Given two example IPs + `/24` mask, decide same-LAN vs needs-gateway together.",
        "independent": "On your lab host, record IP, mask, gateway. Compute usable hosts for your `/24` (or explain your real mask). Explain loopback in one sentence.",
        "feynman_topic": "IPv4 addresses, masks, gateways, and why classful charts are history — not how modern LANs work",
        "feynman_example_hint": "Analogy: street address + ZIP (network) vs apartment number (host), and the post office (gateway) for other ZIPs.",
        "spiral": "Use this whenever Class 3 Docker networks, Class 5 ARR URLs, Class 10 remote access, or Class 12 Wyoming hosts misbehave. Addressing is a permanent spiral skill.",
        "reflect_prompt": "Which addressing misconception did you personally hold, and what calculation corrected it?",
    },
}


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
    sections = []
    while i < len(lines):
        h2 = lines[i][3:].strip()
        i += 1
        body = []
        while i < len(lines) and not lines[i].startswith("## "):
            body.append(lines[i])
            i += 1
        sections.append((h2, "\n".join(body).strip()))
    return title, "\n".join(lead).strip(), sections


def parse_meta(lead: str):
    lecture = time = build = ""
    rest = []
    for line in lead.splitlines():
        s = line.strip()
        m = re.match(r"\*\*Lecture:\*\*\s*(.+)", s, re.I)
        if m:
            lecture = m.group(1).strip()
            continue
        m = re.match(r"\*\*Time:\*\*\s*(.+)", s, re.I)
        if m:
            time = m.group(1).strip()
            continue
        m = re.match(r"\*\*Build output:\*\*\s*(.+)", s, re.I)
        if m:
            build = m.group(1).strip()
            continue
        if s:
            rest.append(line)
    return lecture, time, build, "\n".join(rest).strip()


def classify(h2: str) -> str:
    low = h2.lower().strip()
    if VOCAB_ALIASES.search(low) and "outcome" in low:
        return "vocab_outcome"
    if VOCAB_ALIASES.search(low):
        return "vocab"
    if OUTCOME_ALIASES.search(low):
        return "outcome"
    if WHY_ALIASES.search(low):
        return "why"
    if LAB_ALIASES.search(low):
        return "lab"
    if BREAK_ALIASES.search(low):
        return "break"
    if QUIZ_ALIASES.search(low):
        return "quiz"
    if GATE_ALIASES.search(low):
        return "gate"
    if MISTAKE_ALIASES.search(low):
        return "mistakes"
    if CORRECTION_ALIASES.search(low):
        return "correction"
    if "example scoring" in low or low.startswith("example"):
        return "example"
    return "instruction"


def bullets(items: list[str]) -> str:
    return "\n".join(f"{i}. {q}" for i, q in enumerate(items, 1))


def feynman_block(topic: str, example_hint: str) -> str:
    return f"""### Explain
Describe **{topic}** in your own words. No copying the lesson verbatim.

### Simplify
Explain the same idea to a 12-year-old. If you use a technical word, define it.

### Example
{example_hint}

### Weak spot
What part was hard to explain? That is where your understanding is thin.

### Retry
Return to that part of **Instruction**, restudy it, then rewrite a clearer explanation below.

> Mastery note: a completed Feynman teach-back is required before the next class unlocks — “I get it” without explanation does not count.
"""


def rebuild(path: Path) -> None:
    cid = path.name[:2]
    ped = PEDAGOGY[cid]
    raw = path.read_text()
    title, lead, sections = split_sections(raw)
    lecture, time, build, lead_rest = parse_meta(lead)

    buckets = {
        "why": [],
        "outcome": [],
        "vocab": [],
        "instruction": [],
        "example": [],
        "lab": [],
        "break": [],
        "mistakes": [],
        "quiz": [],
        "gate": [],
        "correction": [],
    }
    for h2, body in sections:
        kind = classify(h2)
        if kind == "vocab_outcome":
            # Split tables as vocab; prose as outcome-ish instruction intro
            buckets["vocab"].append((h2, body))
        else:
            buckets[kind].append((h2, body))

    # Vocabulary body
    vocab_body = ""
    for h2, body in buckets["vocab"]:
        vocab_body = body if not vocab_body else vocab_body + "\n\n" + body
    if not vocab_body:
        vocab_body = "_Add terms as you encounter them in Instruction._"

    # Why
    why_body = ped["why"]
    for h2, body in buckets["why"]:
        if body.strip():
            why_body = body.strip()

    # Instruction: outcomes prose + all instruction sections + leftover examples folded with headers
    instr_parts = []
    if lead_rest.strip():
        instr_parts.append(lead_rest.strip())
    for h2, body in buckets["outcome"]:
        if body.strip():
            instr_parts.append(f"### Originally: {h2}\n\n{body.strip()}")
    for h2, body in buckets["instruction"]:
        instr_parts.append(f"### {h2}\n\n{body.strip()}" if h2.lower() not in {"lesson", "instruction"} else body.strip())
    instruction = "\n\n".join(p for p in instr_parts if p).strip()

    # Worked example
    worked = ped["worked"]
    if buckets["example"]:
        extra = "\n\n".join(f"### {h2}\n\n{body}" for h2, body in buckets["example"])
        worked = worked + "\n\n" + extra

    lab = "\n\n".join(f"### {h2}\n\n{body}" if not h2.lower().startswith("guided lab") else body for h2, body in buckets["lab"]).strip()
    if not lab:
        lab = "_Complete the guided lab steps for this class._"

    brk = "\n\n".join(f"### {h2}\n\n{body}" for h2, body in buckets["break"]).strip()
    if not brk:
        brk = "1. Break one intentional assumption from the lab.\n2. Observe the failure symptom.\n3. Fix using the lesson model and re-run evidence checks."

    mistakes = "\n\n".join(body for _, body in buckets["mistakes"]).strip()
    if not mistakes:
        mistakes = "- Skipping evidence and calling it done.\n- Changing multiple variables before retesting.\n- Moving on without completing Feynman teach-back."

    quiz = "\n\n".join(body for _, body in buckets["quiz"]).strip()
    gate = "\n\n".join(body for _, body in buckets["gate"]).strip()
    correction = "\n\n".join(body for _, body in buckets["correction"]).strip()

    meta_lines = []
    if lecture:
        meta_lines.append(f"**Lecture (optional):** {lecture}")
    if time:
        meta_lines.append(f"**Time:** {time}")
    meta_lines.append(f"**Learning objective:** {ped['objective']}")
    meta_lines.append(f"**Bloom level:** {ped['bloom']}")
    if build:
        meta_lines.append(f"**Build output:** {build}")
    meta_lines.append(
        "**Mastery unlock:** ≥80% retrieval target when scored + completed Feynman teach-back + independent practice + all practical gate boxes + workbook evidence."
    )

    out = []
    out.append(f"# {title}")
    out.append("")
    out.extend(meta_lines)
    out.append("")
    out.append("## Learning objective")
    out.append("")
    out.append(ped["objective"])
    out.append("")
    out.append("## Why this matters")
    out.append("")
    out.append(why_body)
    out.append("")
    out.append("## Prior-knowledge check")
    out.append("")
    out.append("Answer briefly before reading Instruction. Wrong answers are useful — they show what to review.")
    out.append("")
    out.append(bullets(ped["prior"]))
    out.append("")
    out.append("## Vocabulary")
    out.append("")
    out.append(vocab_body)
    out.append("")
    out.append("## Instruction")
    out.append("")
    out.append(instruction if instruction else "_See worked example and lab._")
    out.append("")
    out.append("## Worked example")
    out.append("")
    out.append("**I do** — study the reasoning, not just the final answer.")
    out.append("")
    out.append(worked)
    out.append("")
    out.append("## Guided practice")
    out.append("")
    out.append("**We do** — hints allowed. Check your reasoning against Instruction.")
    out.append("")
    out.append(ped["guided"])
    out.append("")
    out.append("## Independent practice")
    out.append("")
    out.append("**You do** — close the hints. Solve before opening the lab.")
    out.append("")
    out.append(ped["independent"])
    out.append("")
    out.append("## Feynman teach-back")
    out.append("")
    out.append("Required. Do not skip.")
    out.append("")
    out.append(feynman_block(ped["feynman_topic"], ped["feynman_example_hint"]))
    out.append("")
    out.append("## Retrieval check")
    out.append("")
    out.append("Active recall — write answers without rereading first. Target ≥80% before the gate.")
    out.append("")
    out.append(quiz if quiz else "1. Restate the learning objective as a task you can perform.\n2. Give one failure mode for this class.\n3. Name the evidence you will capture.")
    out.append("")
    out.append("## Guided lab")
    out.append("")
    out.append(lab)
    out.append("")
    out.append("## Break / fix")
    out.append("")
    out.append(brk)
    out.append("")
    out.append("## Feedback / common mistakes")
    out.append("")
    out.append(mistakes)
    out.append("")
    out.append("## Practical mastery gate")
    out.append("")
    out.append("All boxes must be true before the next class unlocks. If you fail: feedback → targeted review → new practice → reassess.")
    out.append("")
    # Ensure Feynman + practice appear on gate list
    gate_lines = gate.splitlines() if gate else []
    extra_checks = [
        "- [ ] Prior-knowledge check answered",
        "- [ ] Feynman teach-back completed (Explain, Simplify, Example, Weak spot, Retry)",
        "- [ ] Independent practice completed",
        "- [ ] Retrieval check attempted (target ≥80% when scored)",
        "- [ ] Evidence recorded in workbook / verification matrix",
    ]
    existing = "\n".join(gate_lines)
    merged = existing
    for c in extra_checks:
        if c.lower() not in existing.lower():
            merged = (merged + "\n" + c).strip() if merged else c
    out.append(merged)
    out.append("")
    out.append("## Reflection")
    out.append("")
    out.append(ped["reflect_prompt"])
    out.append("")
    out.append("Also answer:")
    out.append("")
    out.append("1. What did I learn?")
    out.append("2. What did I struggle with?")
    out.append("3. How does this connect to earlier classes?")
    out.append("")
    out.append("## Spiral hook")
    out.append("")
    out.append(ped["spiral"])
    out.append("")
    if correction:
        out.append("## 2026 correction")
        out.append("")
        out.append(correction)
        out.append("")

    path.write_text("\n".join(out).rstrip() + "\n")
    print("restructured", path.name)


def main():
    for path in sorted(CLASSES.glob("*.md")):
        rebuild(path)


if __name__ == "__main__":
    main()

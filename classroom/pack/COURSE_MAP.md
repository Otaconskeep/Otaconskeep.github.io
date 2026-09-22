# Course Map — Module Curriculum

**Authoritative structure:** [`modules/`](modules/README.md)  
**Design chain:** Backward Design → Bloom’s Taxonomy → Learn / Practice / Test / Reflect → Mastery → Spiral Review  
**Feynman teach-back is required in every lesson** (not optional).

## Backward design — course outcome

Student can design, build, operate, troubleshoot, and verify a private homelab (Dockerized services, authorized ARR automation, Home Assistant, local voice, guarded n8n) with evidence in a verification matrix.

## Modules

| Module | Outcome (capability) | Topics | Stage gate |
|---|---|---|---|
| [1 — Infrastructure & Addressing](modules/01-infrastructure/MODULE.md) | Virtualize, Compose, network, operate, read IPv4 | 5 | Gate 1 |
| [2 — ARR Media Automation](modules/02-arr-media/MODULE.md) | Prowlarr flow, quality policy, config automation | 3 | Gate 2 |
| [3 — Home Assistant & Secure Access](modules/03-home-assistant/MODULE.md) | Entities, testable automations, remote denial | 3 | Gate 3 |
| [4 — Local Voice](modules/04-local-voice/MODULE.md) | Stage diagnosis, STT/TTS, disconnected speaker | 3 | Gate 4 |
| [5 — Workflow Automation](modules/05-workflow-automation/MODULE.md) | n8n digests + approval before mutation | 1 | Gate 5 |
| [Capstone](FINAL_CAPSTONE.md) | Full-system verification + final Feynman | — | Course |

## How each topic is organized

Every topic is a mini learning system with **separate activities**:

| Activity | Folder file | Purpose in the chain |
|---|---|---|
| Reading | `reading.md` | Learn (instruction, vocab, worked example) |
| Lesson | `lesson.md` | Orient, prior check, guided practice, **Feynman**, reflect |
| Lab | `lab.md` | Practice (guided lab + break/fix + lab gate) |
| Homework | `homework.md` | Apply independently |
| Quiz | `quiz.md` | Test / retrieval (≥80% target) |

## How each module is organized

| Activity | File | Purpose |
|---|---|---|
| Module hub | `MODULE.md` | Outcome, Bloom arc, topic index, mastery unlock |
| Project | `project.md` | Integrated Apply/Create across topics |
| Module quiz | `module-quiz.md` | Cross-topic retention |
| Exam | `exam.md` | Module mastery verification |
| Remediation | `remediation.md` | Feedback → review → reassess |

## Topic index

### Module 1 — Infrastructure & Addressing
1. Virtualization & Proxmox  
2. Docker Compose & persistence  
3. Docker networking  
4. Container operations  
5. IPv4 addresses & gateways  

### Module 2 — ARR Media Automation
1. Prowlarr & ARR request flow  
2. TRaSH quality profiles  
3. Configuration automation  

### Module 3 — Home Assistant & Secure Access
1. Home Assistant foundations  
2. Home Assistant automations  
3. Secure remote access  

### Module 4 — Local Voice
1. Local voice architecture  
2. Whisper, Piper & Wyoming  
3. Private smart speaker  

### Module 5 — Workflow Automation
1. n8n homelab automation  

## Mastery unlock rules

**Topic unlock:** reading + Feynman + quiz target + lab gate + homework evidence  

**Module unlock:** all topics complete + project + module quiz + exam  

**Next module:** previous module mastery gate true — not “clicked Next”

## Spiral review

- Module 1 Compose/networks/ops/IP return in every later deploy and outage.
- Module 2 quality policy returns when automation drifts.
- Module 3 entity names return as voice actions; remote boundary constrains Module 5.
- Module 4 stage names are the permanent voice fault language.
- Capstone spirals all modules into one verification matrix.

## Legacy class files

`classes/01…15` remain as combined reference exports. **Teach and navigate from `modules/`.** Website class URLs redirect into the matching module topic lesson.

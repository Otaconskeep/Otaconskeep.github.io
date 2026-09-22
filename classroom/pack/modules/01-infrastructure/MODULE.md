# Module 1 — Infrastructure & Addressing

**Design chain:** Backward Design → Bloom’s Taxonomy → Learn / Practice / Test / Reflect → Mastery → Spiral Review  
**Feynman teach-back is required in every lesson.**

## Backward design — module outcome

Student can virtualize a safe lab host, run persistent Compose services on isolated Docker networks, operate containers with update/rollback evidence, and read IPv4 address/mask/gateway to decide same-LAN vs via-gateway delivery.

## Bloom arc

Remember/Understand (IPv4, VM basics) → Apply (Compose, ops) → Analyze (networking)

## Module learning cycle

Orient → Recall → Learn (reading) → Demonstrate (worked example) → Guided practice → Independent practice / homework → **Feynman** → Lab → Quiz → Feedback → Module project → Module exam → Reflect

## Topics

| ID | Topic | Activities |
|---|---|---|
| 01.01 | Virtual machines & Proxmox | [Lesson](topics/01-virtualization/lesson.md) · [Reading](topics/01-virtualization/reading.md) · [Lab](topics/01-virtualization/lab.md) · [Homework](topics/01-virtualization/homework.md) · [Quiz](topics/01-virtualization/quiz.md) |
| 01.02 | Docker Compose & persistence | [Lesson](topics/02-compose/lesson.md) · [Reading](topics/02-compose/reading.md) · [Lab](topics/02-compose/lab.md) · [Homework](topics/02-compose/homework.md) · [Quiz](topics/02-compose/quiz.md) |
| 01.03 | Docker networking | [Lesson](topics/03-networking/lesson.md) · [Reading](topics/03-networking/reading.md) · [Lab](topics/03-networking/lab.md) · [Homework](topics/03-networking/homework.md) · [Quiz](topics/03-networking/quiz.md) |
| 01.04 | Container operations | [Lesson](topics/04-operations/lesson.md) · [Reading](topics/04-operations/reading.md) · [Lab](topics/04-operations/lab.md) · [Homework](topics/04-operations/homework.md) · [Quiz](topics/04-operations/quiz.md) |
| 01.05 | IPv4 addresses & gateways | [Lesson](topics/05-ipv4/lesson.md) · [Reading](topics/05-ipv4/reading.md) · [Lab](topics/05-ipv4/lab.md) · [Homework](topics/05-ipv4/homework.md) · [Quiz](topics/05-ipv4/quiz.md) |

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

**Stage gate statement:** Gate 1 — explain persistence, ports, DNS, logs, health, update/rollback, and basic IPv4 delivery with evidence.

## Spiral review

Every later module reuses Compose, networks, ops runbooks, and IP literacy when services cannot talk.

## If you fail a gate

Feedback → targeted reading → new practice → redo Feynman Retry → reassessment (see [remediation.md](remediation.md)).

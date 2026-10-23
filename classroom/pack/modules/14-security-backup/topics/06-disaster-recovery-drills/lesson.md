# Lesson 14.06: Disaster-Recovery Drills

**Module:** Segmentation, Backup & Power
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Distinguish disaster recovery from backup creation, high availability, and routine incident response.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Distinguish disaster recovery from backup creation, high availability, and routine incident response.

## Why this matters

Practice a controlled disaster-recovery exercise that validates backup integrity, measures recovery time, confirms restored data, records evidence, and improves a recovery runbook without affecting workloads outside the classroom directory.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain disaster recovery to a new homelab operator using a notebook backup as the analogy. Your explanation must distinguish owning a copy from proving that the copy can restore useful work.

### model_explanation
A backup is like a photocopy of a notebook. Disaster recovery is the full plan for finding the right photocopy, obtaining a replacement notebook, copying the information back, checking that no pages are missing, and deciding that people may use it again. RPO says how much writing we are willing to lose because it happened after the photocopy. RTO says how long we are willing to wait before the notebook is usable. A drill measures what actually happens and reveals missing supplies or unclear instructions before a real emergency.

### self_check_questions
Can I explain why a successful backup job does not prove recoverability?
Can I state the difference between an objective and an observed result?
Can I describe at least one case where matching file hashes would still be insufficient?
Can I identify the failure domains this laboratory does not test?

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain |
| 3 | [Lab](./lab.md) | Practice |
| 4 | [Homework](./homework.md) | Apply |
| 5 | [Quiz](./quiz.md) | Test |

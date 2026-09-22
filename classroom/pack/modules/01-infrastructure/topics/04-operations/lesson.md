# Lesson 01.04 — Container operations

**Module:** Module 1 — Infrastructure & Addressing  
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)  
**Learning objective:** Given a running Compose service, the learner can inspect health and logs, perform a controlled image update, and roll back to a known-good state with evidence.  
**Bloom level:** Apply / Evaluate  
**Build output:** operational runbook for one containerized service  
**Mastery unlock for this topic:** reading done + Feynman complete + quiz ≥80% (when scored) + lab gate + homework submitted

## Learning objective

Given a running Compose service, the learner can inspect health and logs, perform a controlled image update, and roll back to a known-good state with evidence.

## Why this matters

The lecture demonstrates Docker's breadth. This class turns that inspiration into engineering discipline: selecting appropriate workloads, understanding state, observing health, updating safely, backing up configuration, and recovering from a failed change.

## Prior-knowledge check

Answer briefly before reading Instruction. Wrong answers are useful — they show what to review.

1. What is the difference between desired state and observed state?
2. Where do container logs go by default?
3. Why is `:latest` risky for a service you care about?

## Learn

Complete the module reading first:

- [Reading — Container operations](./reading.md)

Then review the worked example inside that reading (I do).

## Guided practice (We do)

**We do** — hints allowed. Check your reasoning against Instruction.

Walk the update checklist in the lab with notes open. Mark which step produces rollback evidence.

## Feynman teach-back (required)

Required. Do not skip.

### Explain
Describe **how to update a containerized service without gambling the whole lab** in your own words. No copying the lesson verbatim.

### Simplify
Explain the same idea to a 12-year-old. If you use a technical word, define it.

### Example
Analogy: changing a tire with the spare already checked, versus swapping parts until the car starts.

### Weak spot
What part was hard to explain? That is where your understanding is thin.

### Retry
Return to that part of **Instruction**, restudy it, then rewrite a clearer explanation below.

> Mastery note: a completed Feynman teach-back is required before the next class unlocks — “I get it” without explanation does not count.

## Reflection

What would you refuse to update without a backup, and what evidence proves your rollback works?

Also answer:

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

You will use this runbook mindset for ARR profile changes (6–7), HA backups (8), remote access changes (10), voice model swaps (12), and n8n workflow edits (14).

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain / understand |
| 3 | [Lab](./lab.md) | Practice under guidance + break/fix |
| 4 | [Homework](./homework.md) | Independent apply |
| 5 | [Quiz](./quiz.md) | Test / retrieval |

# Lesson 02.03 — Configuration automation

**Module:** Module 2 — ARR Media Automation  
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)  
**Learning objective:** Given a known-good profile backup, the learner can choose one authoritative sync path, run dry-run/apply/rollback, and produce a drift report that matches the live apps.  
**Bloom level:** Apply / Evaluate  
**Build output:** backed-up, repeatable profile sync with drift and rollback evidence  
**Mastery unlock for this topic:** reading done + Feynman complete + quiz ≥80% (when scored) + lab gate + homework submitted

## Learning objective

Given a known-good profile backup, the learner can choose one authoritative sync path, run dry-run/apply/rollback, and produce a drift report that matches the live apps.

## Why this matters

Manual clicking can create a correct profile once. Automation aims to keep declared policy synchronized over time. That introduces new hazards: upstream changes, destructive replacement, token exposure, and configuration drift. This class teaches controlled automation rather than blind synchronization.

## Prior-knowledge check

Answer briefly before reading Instruction. Wrong answers are useful — they show what to review.

1. What is configuration drift?
2. Why is a dry run required before apply?
3. Where do secrets belong (and not belong)?

## Learn

Complete the module reading first:

- [Reading — Configuration automation](./reading.md)

Then review the worked example inside that reading (I do).

## Guided practice (We do)

**We do** — hints allowed. Check your reasoning against Instruction.

Classify three changes as safe / review / dangerous with the lesson’s change table open.

## Feynman teach-back (required)

Required. Do not skip.

### Explain
Describe **why ARR configuration needs an authoritative control loop** in your own words. No copying the lesson verbatim.

### Simplify
Explain the same idea to a 12-year-old. If you use a technical word, define it.

### Example
Analogy: two people editing the same spreadsheet without track changes.

### Weak spot
What part was hard to explain? That is where your understanding is thin.

### Retry
Return to that part of **Instruction**, restudy it, then rewrite a clearer explanation below.

> Mastery note: a completed Feynman teach-back is required before the next class unlocks — “I get it” without explanation does not count.

## Reflection

What would drift look like in your lab tomorrow, and how would you detect it without guessing?

Also answer:

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

This control-loop pattern returns for HA dashboards/automations, reverse-proxy config, voice models, and n8n workflows — same discipline, different files.

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain / understand |
| 3 | [Lab](./lab.md) | Practice under guidance + break/fix |
| 4 | [Homework](./homework.md) | Independent apply |
| 5 | [Quiz](./quiz.md) | Test / retrieval |

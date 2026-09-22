# Lesson 02.01 — Prowlarr & ARR request flow

**Module:** Module 2 — ARR Media Automation  
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)  
**Learning objective:** Given authorized indexer credentials and Compose networking, the learner can connect Prowlarr to Sonarr/Radarr, prove sync/tests, and trace a request through search → download client → import boundaries.  
**Bloom level:** Apply / Analyze  
**Build output:** Prowlarr connected to Sonarr and Radarr with controlled tests  
**Mastery unlock for this topic:** reading done + Feynman complete + quiz ≥80% (when scored) + lab gate + homework submitted

## Learning objective

Given authorized indexer credentials and Compose networking, the learner can connect Prowlarr to Sonarr/Radarr, prove sync/tests, and trace a request through search → download client → import boundaries.

## Why this matters

Clicking through UIs without service contracts produces mystery failures. Prowlarr is the contract hub: if sync and tests are wrong, every later quality and automation class sits on sand.

## Prior-knowledge check

Answer briefly before reading Instruction. Wrong answers are useful — they show what to review.

1. Which Docker network will ARR apps use to reach each other?
2. What evidence proves two apps are connected (not just ‘installed’)?
3. What is the legal boundary for indexers and content in this course?

## Learn

Complete the module reading first:

- [Reading — Prowlarr & ARR request flow](./reading.md)

Then review the worked example inside that reading (I do).

## Guided practice (We do)

**We do** — hints allowed. Check your reasoning against Instruction.

Fill a service-contract row (URL, API key handling, network name, test button result) for Prowlarr→Sonarr with assistance.

## Feynman teach-back (required)

Required. Do not skip.

### Explain
Describe **what Prowlarr does in the ARR flow and how service contracts prevent ‘it just works’ lies** in your own words. No copying the lesson verbatim.

### Simplify
Explain the same idea to a 12-year-old. If you use a technical word, define it.

### Example
Analogy: a switchboard operator who must know each extension — not yelling names down a hallway.

### Weak spot
What part was hard to explain? That is where your understanding is thin.

### Retry
Return to that part of **Instruction**, restudy it, then rewrite a clearer explanation below.

> Mastery note: a completed Feynman teach-back is required before the next class unlocks — “I get it” without explanation does not count.

## Reflection

Which hop is hardest to prove, and what test button or log line is your evidence?

Also answer:

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Class 6 scores what Prowlarr finds; Class 7 automates those profiles; later troubleshooting always returns to ‘which hop failed?’

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain / understand |
| 3 | [Lab](./lab.md) | Practice under guidance + break/fix |
| 4 | [Homework](./homework.md) | Independent apply |
| 5 | [Quiz](./quiz.md) | Test / retrieval |

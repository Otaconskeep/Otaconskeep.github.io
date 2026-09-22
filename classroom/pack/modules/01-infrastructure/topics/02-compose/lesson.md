# Lesson 01.02 — Docker Compose & persistence

**Module:** Module 1 — Infrastructure & Addressing  
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)  
**Learning objective:** Given a multi-step `docker run` intent, the learner can write a Compose file with services, ports, environment, and persistent mounts, then recreate the stack without data loss.  
**Bloom level:** Apply / Create  
**Build output:** a repeatable Compose project that survives recreation  
**Mastery unlock for this topic:** reading done + Feynman complete + quiz ≥80% (when scored) + lab gate + homework submitted

## Learning objective

Given a multi-step `docker run` intent, the learner can write a Compose file with services, ports, environment, and persistent mounts, then recreate the stack without data loss.

## Why this matters

Shell history is not a system design. If your stack only exists as remembered commands, you cannot rebuild after failure — and every later ARR/HA/voice service will be fragile.

## Prior-knowledge check

Answer briefly before reading Instruction. Wrong answers are useful — they show what to review.

1. What is a container image versus a running container?
2. Where should application data live if the container is deleted?
3. Why might publishing a host port be both useful and dangerous?

## Learn

Complete the module reading first:

- [Reading — Docker Compose & persistence](./reading.md)

Then review the worked example inside that reading (I do).

## Guided practice (We do)

**We do** — hints allowed. Check your reasoning against Instruction.

Convert one documented `docker run` (from the lesson) into Compose YAML with assistance. Check: service name, image, ports, env, volume, restart policy.

## Feynman teach-back (required)

Required. Do not skip.

### Explain
Describe **why Docker Compose beats a long `docker run` for real systems** in your own words. No copying the lesson verbatim.

### Simplify
Explain the same idea to a 12-year-old. If you use a technical word, define it.

### Example
Analogy: a recipe card (Compose) vs remembering a cooking performance (run commands).

### Weak spot
What part was hard to explain? That is where your understanding is thin.

### Retry
Return to that part of **Instruction**, restudy it, then rewrite a clearer explanation below.

> Mastery note: a completed Feynman teach-back is required before the next class unlocks — “I get it” without explanation does not count.

## Reflection

Where did persistence almost fail, and what evidence proves recreate is safe?

Also answer:

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Every later class assumes Compose + persistence. Class 3 adds networks; Class 4 adds update/rollback; Classes 5–14 drop more services into the same operational model.

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain / understand |
| 3 | [Lab](./lab.md) | Practice under guidance + break/fix |
| 4 | [Homework](./homework.md) | Independent apply |
| 5 | [Quiz](./quiz.md) | Test / retrieval |

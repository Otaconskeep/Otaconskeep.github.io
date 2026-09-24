# Lesson 09.04 — Health Checks, Dependencies, and Restart Policies

**Module:** ARR Data Model & Compose
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain why a running process is not necessarily a healthy or ready service
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-20

## Learning objective

Explain why a running process is not necessarily a healthy or ready service

## Why this matters

Teach operators to distinguish process state from service health, model startup and runtime dependencies, and apply bounded restart behavior without creating restart loops or hiding real failures.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the lesson to a new operator using a restaurant analogy.

### model_explanation
A process is like a restaurant building with the lights on. Liveness asks whether staff are present and able to respond. Readiness asks whether the kitchen can actually serve customers now. A food delivery service is a dependency: opening the restaurant after the delivery truck arrives does not guarantee ingredients were unloaded and checked. A restart policy is like sending the manager home and bringing in a replacement when the manager fails. That may help after a temporary problem, but repeatedly replacing managers will not fix an empty pantry. Traffic should be paused when the restaurant is unready, while restarts should be reserved for failures that a fresh process can plausibly correct.

### self_check
If your explanation treats process existence, readiness, and liveness as the same condition, revise it until each signal has a distinct meaning and response.

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

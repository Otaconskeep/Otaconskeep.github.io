# Lesson 12.07: ARR Stack Health Monitoring

**Module:** Requests & Media Servers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Separate service reachability from application health state.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Separate service reachability from application health state.

## Why this matters

Build and verify a synthetic health exporter that converts ARR-style reachability, declared health, queue depth, and storage data into deterministic Prometheus text metrics without requiring access to a live Sonarr or Radarr instance.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the monitor to someone who knows only that Sonarr and Radarr are applications.

### model_explanation
The monitor asks two different questions. First, can it talk to the application? That answer becomes arr_monitor_up, using 1 for yes and 0 for no. Second, what condition is the application in? That becomes a state number: 2 healthy, 1 warning, or 0 critical. These questions must stay separate because an application can answer successfully while reporting a serious internal problem. Unreachable and declared critical conditions win over warnings. If neither critical condition exists, a queue over 25 or free space below 15 causes warning. Two applications multiplied by two metrics produces exactly four samples.

### self_check
Can you explain why reachable and healthy are not synonyms?
Can you state why reachable declared critical produces values 1 and 0 rather than 0 and 0?
Can you explain why queue depth 25 and free space 15 are healthy boundaries?
Can you account for all four expected samples without looking at the code?

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

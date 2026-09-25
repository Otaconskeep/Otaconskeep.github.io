# Lesson 10.07: Radarr Monitoring and Availability

**Module:** Sonarr & Radarr
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain why a running Radarr process does not prove that movie automation is working
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain why a running Radarr process does not prove that movie automation is working

## Why this matters

Teach operators how to distinguish Radarr process availability, HTTP reachability, application health, dependency health, and end-to-end functionality. The lab builds a local Radarr-like service and an availability probe without changing a production Radarr installation.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

Explain the monitoring model to another learner using a restaurant analogy. A lit sign is like a running process: it suggests the business exists but proves little. An unlocked door is like an open TCP port. A host greeting you is like a successful HTTP response. A working kitchen, available ingredients, and functioning payment system represent Radarr dependencies. Receiving the meal you ordered represents an end-to-end automation check. Then explain why each layer can succeed while the next layer fails, and identify which alert would help the operator act on each failure.

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

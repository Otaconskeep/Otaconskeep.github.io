# Lesson 14.08: UPS Monitoring and Safe Shutdown

**Module:** Segmentation, Backup & Power
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the roles of a UPS, UPS driver, monitoring daemon, client, and shutdown coordinator.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain the roles of a UPS, UPS driver, monitoring daemon, client, and shutdown coordinator.

## Why this matters

Teach operators how to interpret UPS state, design a conservative shutdown policy, prevent duplicate shutdown requests, and validate the policy with simulated Network UPS Tools data without changing host power settings or interacting with real UPS hardware.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the design to a family member using the idea of a phone battery and an unreliable battery indicator.

### model_explanation
A UPS is like a temporary battery for computers. The monitoring system should not turn everything off because one reading says the wall power flickered. It checks repeatedly to confirm that the battery is truly becoming critical. It also rejects old readings, because an old message does not describe what is happening now. Once it asks the computers to shut down, it remembers that request so it does not ask repeatedly. If wall power is confirmed to have returned, it clears that memory and waits for the next event.

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

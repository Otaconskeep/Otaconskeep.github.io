# Lesson 10.02 — Sonarr Series Monitoring and Availability

**Module:** Sonarr & Radarr
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Differentiate monitored state from missing, available, downloaded, and cutoff-unmet states
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Differentiate monitored state from missing, available, downloaded, and cutoff-unmet states

## Why this matters

Teach administrators how Sonarr monitoring, episode state, release availability, quality cutoffs, and search behavior interact. The lesson emphasizes predicting Sonarr's decisions before changing a production library.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain monitoring to a family member who thinks selecting a show means every episode will immediately download.

### model_explanation
Monitoring tells Sonarr which episodes it is allowed to care about. Sonarr still waits until an episode is considered available, looks for releases through an indexer, rejects releases that do not meet the rules, and asks a download client to transfer an accepted one. An old missing episode may also need a deliberate historical search because the normal feed mainly evaluates newly posted releases. A file can already exist and still be monitored for an upgrade if it has not reached the quality cutoff.

### self_check
Your explanation should separately mention intent, availability, searching, acceptance rules, downloading, and quality upgrades. If monitored and downloaded are used as synonyms, revise the explanation.

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

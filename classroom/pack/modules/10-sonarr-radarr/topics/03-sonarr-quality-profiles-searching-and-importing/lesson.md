# Lesson 10.03: Sonarr Quality Profiles, Searching, and Importing

**Module:** Sonarr & Radarr
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the difference between a quality definition, quality profile, custom format, and release score.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain the difference between a quality definition, quality profile, custom format, and release score.

## Why this matters

Teach administrators how Sonarr evaluates quality profiles, ranks search results, decides whether an episode is an upgrade, and imports a selected download into a series library. The lab uses a self-contained simulation so that students can inspect every decision without changing a production Sonarr database, download client, or media library.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain Sonarr's workflow to a new administrator without using the phrases quality magic or best release.

### model_explanation
Sonarr first needs permission to manage an episode, which is represented by monitoring. It discovers releases through recent-feed processing or an explicit search. It parses each release, checks whether the quality is allowed, applies custom-format scores and other restrictions, and rejects anything that violates the profile. If a release is selected, Sonarr asks the download client to retrieve it. After completion, Sonarr must be able to see the reported path and identify the episode file. It then places the file in the organized series directory by copying, moving, or hardlinking it. A hardlink is possible only when source and destination are on the same filesystem. The operator can understand a surprising decision by checking interactive-search rejection reasons, the activity queue, history, and logs.

### self_check
Can you explain why monitoring does not immediately search old indexer results?
Can you explain why an allowed quality may still be rejected?
Can you explain why a high custom-format score does not make a disallowed quality eligible?
Can you explain why matching inode numbers demonstrate a hardlink?
Can you explain how inconsistent container paths interrupt Completed Download Handling?

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

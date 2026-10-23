# Lesson 12.06: Bazarr and Subtitle Automation

**Module:** Requests & Media Servers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Describe Bazarr's role in a media automation architecture
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Describe Bazarr's role in a media automation architecture

## Why this matters

Explain how Bazarr integrates with Sonarr, Radarr, media storage, and subtitle providers, then build and validate a least-privilege deployment manifest without starting containers or changing an existing media stack.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

Explain Bazarr to a peer as a subtitle librarian that depends on two kinds of access. Sonarr and Radarr tell it which movies and episodes exist, which are monitored, and where their files should be. Filesystem mounts let it inspect those files and place matching subtitle sidecars beside them. If the API works but the paths do not match, Bazarr knows about a title but cannot reach its file. If the paths work but permissions are read-only, Bazarr can inspect the library but cannot save subtitles. Language profiles define what the household wants, providers offer candidates, and scoring helps avoid weak matches. A safe rollout begins with narrow permissions, consistent paths, one profile, one provider, and a small test set.

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

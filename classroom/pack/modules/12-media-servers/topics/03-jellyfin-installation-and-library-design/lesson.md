# Lesson 12.03: Jellyfin Installation and Library Design

**Module:** Requests & Media Servers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Describe the roles of Jellyfin configuration, cache, metadata, and media storage
**Bloom level:** Understand / Apply
**Last reviewed:** 2026-03-17

## Learning objective

Describe the roles of Jellyfin configuration, cache, metadata, and media storage

## Why this matters

Install an isolated Jellyfin server with containerized deployment, understand its configuration and cache boundaries, and design media libraries that support reliable identification, metadata retrieval, permissions, backup, and future growth.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the installation to a learner who understands folders but has never used containers. Your explanation must cover why Jellyfin sees /media instead of the longer host path, why config survives replacement of the container, and why media is read-only.

### model_explanation
The container is like a room with labeled windows into selected host folders. The host's class58/config folder appears through a window labeled /config, and the media folder appears through another window labeled /media. Jellyfin only knows the labels inside its room, so its library uses /media/Movies instead of the host's longer path. The container itself can be replaced, but the host config folder stays in place, so the new container reads the same accounts and library database. The media window is read-only: Jellyfin can inspect and stream files through it, but it cannot alter the originals.

### self_check
Can you identify which directory contains irreplaceable application state?
Can you explain why cache and configuration are separate?
Can you predict what happens if a host path is entered in the Jellyfin library wizard?
Can you explain how consistent movie and episode names reduce incorrect metadata matches?

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

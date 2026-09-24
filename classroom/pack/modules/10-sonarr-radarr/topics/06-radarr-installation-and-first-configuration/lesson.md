# Lesson 10.06 — Radarr Installation and First Configuration

**Module:** Sonarr & Radarr
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain Radarr's role in a media automation architecture
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain Radarr's role in a media automation architecture

## Why this matters

Install Radarr as a containerized service, create persistent application and media directories, complete the initial web configuration, and understand how Radarr coordinates movie monitoring, indexers, download clients, and media imports.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

Explain Radarr as if teaching someone who has never used media automation: Radarr is the coordinator, not the downloader. A user tells it which movie is wanted and what quality is acceptable. Radarr asks an indexer what releases exist, chooses an allowed release, and gives that request to a download client. When the download client finishes, Radarr needs to see the same completed file path so it can import the file into the organized movie library. In this lab, /config remembers Radarr's settings, /downloads is the staging area, and /movies is the final library. If /config is not persistent, Radarr forgets its setup. If /downloads is not consistently mapped, imports fail. If /movies is not writable, Radarr cannot organize the library.

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

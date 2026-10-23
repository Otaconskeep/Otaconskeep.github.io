# Lesson 12.04: Plex versus Jellyfin and Safe Migration

**Module:** Requests & Media Servers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Compare Plex and Jellyfin across licensing, account dependencies, remote access, plug-ins, client coverage, administration, and migration implications.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Compare Plex and Jellyfin across licensing, account dependencies, remote access, plug-ins, client coverage, administration, and migration implications.

## Why this matters

Compare Plex and Jellyfin using operational criteria, then practice a reversible migration that separates media from application state, verifies a backup by extraction, enforces read-only media access for a service identity, performs a simulated cutover, and restores Plex state during rollback.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the migration to a household member who understands files but not media-server databases.

### model_explanation
The movie files are like books, while Plex and Jellyfin each keep their own catalog cards, user records, and bookmarks. We leave the books in one read-only room and build Jellyfin a new catalog instead of handing it Plex's private catalog files. Before switching the sign on the door, we copy Plex's catalog, unpack that copy somewhere separate, and compare every file with a checksum list. We then test Jellyfin's catalog and change the sign. If the new catalog is unsuitable, we preserve the failed state, put the verified Plex catalog back, return the sign to Plex, and check the backup again.

### self_check_questions
Why is a successful archive-creation command insufficient evidence that recovery will work?
Why should the media directory and application-state directory have different permission policies?
Why can a watch-history mapping be reasonable while direct database copying is unsafe?
What evidence proves that rollback restored state rather than only changing a service label?

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

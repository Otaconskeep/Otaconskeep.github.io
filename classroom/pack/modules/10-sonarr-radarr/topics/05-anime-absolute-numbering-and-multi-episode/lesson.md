# Lesson 10.05 — Anime, Absolute Numbering, and Multi-Episode Files

**Module:** Sonarr & Radarr
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the difference between absolute, season-based, aired, DVD, and metadata-provider episode orderings.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-14

## Learning objective

Explain the difference between absolute, season-based, aired, DVD, and metadata-provider episode orderings.

## Why this matters

Teach administrators how to reconcile anime absolute numbering with season-based metadata, name multi-episode files predictably, and stage changes without exposing the production media library to destructive bulk renames.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the workflow to a friend who thinks absolute episode 027 can always be converted by dividing by a season length.

### model_explanation
Absolute 027 is only a label in one ordering system. Seasons may have different lengths, and specials or provider decisions can shift later numbers. I first choose the metadata provider and its order, then look up absolute 027 in a mapping table. If that table says it is season 2 episode 3, I can name it S02E03. If one file contains two adjacent mapped episodes, I can use a supported range such as S02E03-E04. The name helps the server associate records with the file, but it does not split the video or guarantee separate resume positions.

### self_check
Can the learner explain why arithmetic conversion is unsafe?
Can the learner distinguish an episode identity from a filename format?
Can the learner explain why one file may create multiple metadata records but still have one playback timeline?
Can the learner state why specials require explicit mapping?

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

# Lesson 11.06: Prowlarr Installation and Indexer Management

**Module:** Download Clients & Indexers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain why Prowlarr centralizes indexer definitions for compatible media-management applications.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain why Prowlarr centralizes indexer definitions for compatible media-management applications.

## Why this matters

Install Prowlarr as a self-contained application, isolate all persistent lab data under the class workspace, understand Prowlarr's role as an indexer manager, and practice adding, testing, and troubleshooting a legal local Torznab-compatible indexer without relying on public indexer services.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain Prowlarr to a learner who has configured the same search source independently in several media applications.

### model_explanation
Prowlarr is a central address book and translator for indexers. Instead of entering the same endpoint, key, categories, and limits in every compatible application, you define the indexer once in Prowlarr. Prowlarr tests how that source speaks, learns its capabilities, and can synchronize an appropriate definition to connected applications. It does not organize a media library and it does not download a selected item. If a test fails, first ask which layer failed: the service may be unreachable, credentials may be rejected, the selected protocol may not match, or categories may not overlap. This lab's local server proves those ideas with synthetic Torznab responses.

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

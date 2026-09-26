# Lesson 11.04: SABnzbd and Usenet Downloading

**Module:** Download Clients & Indexers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Describe the roles of a Usenet provider, an indexer, an NZB file, and SABnzbd.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Describe the roles of a Usenet provider, an indexer, an NZB file, and SABnzbd.

## Why this matters

Explain how SABnzbd processes NZB metadata, communicates securely with Usenet providers, verifies and repairs article sets, unpacks completed downloads, and hands categorized results to other homelab applications. The lab builds and validates an isolated SABnzbd deployment policy without contacting a provider, downloading external content, installing software, or modifying files outside the class workspace.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the workflow to someone who thinks an NZB file contains the requested download.

### model_explanation
An NZB is more like a manifest than a package. It lists identifiers for many Usenet articles. SABnzbd reads those identifiers, asks a provider for each article, decodes and joins the pieces in an incomplete workspace, checks whether the reconstructed data is intact, uses PAR2 recovery information if enough is available, and optionally extracts archives. Only after those stages succeed does the result move to a completed category directory. The indexer produced the map, the provider stores the pieces, and SABnzbd performs the retrieval and assembly.

### self_check
Can you explain why an indexer and provider are different services?
Can you explain why retention does not guarantee completion?
Can you explain why incomplete and completed directories must remain separate?
Can you explain why a backup provider should normally have lower priority?
Can you explain why verification does not prove that a downloaded file is safe?

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

# Lesson 11.05: Indexers, Trackers, and Usenet Providers

**Module:** Download Clients & Indexers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Differentiate a Usenet indexer, Usenet provider, torrent indexer, BitTorrent tracker, download client, and automation application.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Differentiate a Usenet indexer, Usenet provider, torrent indexer, BitTorrent tracker, download client, and automation application.

## Why this matters

Teach learners to distinguish content-discovery services from transfer infrastructure, understand how Usenet and BitTorrent components interact, evaluate provider and indexer requirements, and design a secure automation workflow without contacting real indexers, trackers, peers, or Usenet servers.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

Explain the system to a new administrator using a library analogy. The indexer is the searchable catalog, not the shelf holding the material. An NZB or torrent metadata result is like a retrieval slip describing what is needed. A Usenet provider is the infrastructure from which an NNTP client requests referenced articles. In BitTorrent, peers exchange pieces, while a tracker can help participants find one another. The automation application is the coordinator that searches the catalog and hands a selected result to the correct client. If your explanation claims that a tracker stores every payload, that an indexer performs all transfers, or that an NZB is the final payload, revise it until each responsibility and trust boundary is distinct.

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

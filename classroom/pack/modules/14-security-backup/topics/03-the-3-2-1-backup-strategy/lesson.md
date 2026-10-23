# Lesson 14.03: The 3-2-1 Backup Strategy

**Module:** Segmentation, Backup & Power
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain what each number in the 3-2-1 strategy represents.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-25

## Learning objective

Explain what each number in the 3-2-1 strategy represents.

## Why this matters

Teach learners how to design, document, test, and verify a 3-2-1 backup strategy: three copies of important data, stored using at least two independent storage media or failure domains, with at least one copy maintained off-site. The lab demonstrates the workflow inside a restricted classroom directory while clearly distinguishing that simulation from a production-quality implementation.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the 3-2-1 strategy to someone who believes three folders on one server are sufficient.

### model_explanation
I need three copies because one is the live data and two are recovery copies. I also need separation: if every copy is on one server or one disk, that hardware failure can destroy all three. At least one copy must be away from the primary site so a building-level event does not remove every option. Synchronization, RAID, and replication can improve availability, but they may copy deletion or corruption and may not preserve old versions. A backup plan is only credible when I can restore the data, verify its integrity, and meet the required recovery time.

### self_check
Did the explanation count the active data as one of the three copies?
Did it explain why separate folders are not separate media or failure domains?
Did it distinguish availability technologies from recoverable backup history?
Did it mention off-site protection and restore testing?
Could the listener identify at least one event that would defeat the proposed design?

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

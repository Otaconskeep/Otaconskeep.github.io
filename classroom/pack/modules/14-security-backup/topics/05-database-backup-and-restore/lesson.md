# Lesson 14.05: Database Backup and Restore

**Module:** Segmentation, Backup & Power
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Distinguish a file copy from a transactionally consistent database backup.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Distinguish a file copy from a transactionally consistent database backup.

## Why this matters

Teach learners how to create, validate, restore, and document a transactionally consistent database backup. The lab uses SQLite and Python's standard library so that backup principles can be practiced without requiring a separate database server. The same operational concepts—consistency, retention, integrity checking, isolated restoration, and recovery verification—apply to larger database platforms.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

Explain the exercise to another learner without using the phrase "it just copies the file." Describe why the database backup API is used, what recovery point the backup represents, why a digest is calculated, why the restore is placed in a separate directory, and why both integrity checks and application-level assertions are necessary. A strong explanation should note that the restored database intentionally lacks app01 and retains router01 as active because those changes happened after the backup. It should also explain why a successful backup job does not prove that production RPO and RTO requirements can be met.

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

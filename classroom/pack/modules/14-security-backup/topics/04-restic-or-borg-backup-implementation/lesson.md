# Lesson 14.04: Restic or Borg Backup Implementation

**Module:** Segmentation, Backup & Power
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Initialize and use a password-protected local Restic repository.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Initialize and use a password-protected local Restic repository.

## Why this matters

Implement a local Restic repository, create two encrypted snapshots, inspect snapshot metadata, restore the latest tagged snapshot, verify exact file contents and checksums at Restic's absolute-path restore location, test repository data integrity, and preview retention without deleting snapshots.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the workflow to someone who believes that a successful backup command alone proves recoverability.

### target_explanation
Restic encrypts and stores snapshots, but success during upload does not prove that an operator can locate and restore the intended version. Because the lab backed up an absolute path, Restic rebuilds that path under the restore target. We therefore verify the real restored directory, compare normalized checksums, assert exact expected contents, and read repository data with restic check --read-data. Retention is tested separately with a dry run, and its remove array is evidence of what would be deleted. The source is replaced only after a staged restore passes verification.

### self_check_questions
Why is the restored dataset nested beneath restore/opt/lab-classroom/class73/data?
Why are checksum commands run from inside each data directory?
What does --read-data add to restic check?
Why does a dry-run remove array not mean a snapshot was actually deleted?
Why is the active source not moved until the staged restore passes all checks?

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

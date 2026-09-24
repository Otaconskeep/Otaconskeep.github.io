# Lesson 09.02 — Hardlinks, Atomic Moves, and Import Efficiency

**Module:** ARR Data Model & Compose
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the relationship between a pathname, directory entry, inode, and file data.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain the relationship between a pathname, directory entry, inode, and file data.

## Why this matters

Teach learners how Linux hardlinks and same-filesystem atomic renames can support efficient, collision-resistant media and data import workflows without creating unnecessary duplicate file data.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the lesson to a teammate without using the words magic, duplicate, or instant.

### model_explanation
A directory stores names that point to filesystem records called inodes. A hardlink creates another name for the same inode, so both names reach the same bytes and share the inode's metadata. This is useful when a download client and a media library both need a name for one completed file. The names must be on the same filesystem because inode numbers only have meaning within that filesystem. To publish safely, an importer can create a temporary destination name after the content is complete and then rename that name to the final destination. The final rename changes what new path lookups see as one namespace operation. Programs that already opened the old file can continue reading its old inode. This publication behavior avoids a partially named result, but it does not replace content validation or crash-durability controls.

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

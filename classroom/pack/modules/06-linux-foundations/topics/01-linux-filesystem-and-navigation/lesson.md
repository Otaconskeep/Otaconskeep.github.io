# Lesson 06.01 — Linux Filesystem and Navigation

**Module:** Linux Foundations
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the difference between the filesystem root directory and the root user
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain the difference between the filesystem root directory and the root user

## Why this matters

Build a reliable mental model of the Linux filesystem and develop practical skill navigating directories, interpreting paths, inspecting file metadata, and safely manipulating files within a controlled lab workspace.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### exercise
Explain pathname resolution to a new administrator without using the words obvious or simply.

### prompts
Draw a tree beginning at / and place /opt/lab-classroom/class16 beneath it.
Explain how the same relative path can resolve differently when the working directory changes.
Describe why a filename and an inode are not the same thing.
Use README.txt and README.hard to explain why editing through one name changes what is read through the other.
Use README.link to explain why moving a symbolic link's target can leave the link dangling.
Explain why checking pwd and quoting "$LAB" reduce operational risk.

### success_criteria
A successful explanation distinguishes names, paths, directory entries, inodes, and data; compares hard links with symbolic links; and traces ../README.txt from the config directory to its final target.

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

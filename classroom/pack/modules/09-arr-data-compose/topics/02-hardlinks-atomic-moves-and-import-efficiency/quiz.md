# Quiz: Hardlinks, Atomic Moves, and Import Efficiency

**Module:** ARR Data Model & Compose
**Activity type:** Quiz / retrieval practice
**Target:** ≥80%
**Objective:** Explain the relationship between a pathname, directory entry, inode, and file data.

## Questions

1. What two stat values should match when two pathnames are hardlinks to the same regular file?
2. Why can a hardlink not normally be created between two different filesystems?
3. How does a hardlink differ from a symbolic link?
4. What happens to the other pathname when content is modified in place through one hardlinked pathname?
5. What does a reader with an already open file descriptor observe when the destination pathname is atomically replaced?
6. Why can a command described as a move behave differently across a filesystem boundary?
7. Does atomic rename by itself guarantee that data will survive a sudden power loss? Explain.
8. Why should a temporary publication name be created inside the destination directory?
9. Why is a hardlinked library file not an independent backup of its incoming counterpart?
10. Which checks provide stronger evidence of hardlink identity than matching filenames and file sizes?

## After scoring

- Missed items → return to Reading → redo Feynman Retry → reattempt.

<!-- answer key is maintained in instructor materials / automation batch report; not printed for students -->

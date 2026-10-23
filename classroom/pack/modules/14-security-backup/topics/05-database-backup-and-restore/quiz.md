# Quiz: Database Backup and Restore

**Module:** Segmentation, Backup & Power
**Activity type:** Quiz / retrieval practice
**Target:** ≥80%
**Objective:** Distinguish a file copy from a transactionally consistent database backup.

## Questions

1. 1. Why can copying an actively written database file with a generic file-copy tool produce an unreliable backup?
2. 2. What is the difference between RPO and RTO?
3. 3. Why is a matching SHA-256 digest insufficient to prove that a database backup is usable?
4. 4. Why does this lab restore the backup into an isolated path instead of immediately replacing the live database?
5. 5. Which two categories of checks are used to validate the restored database in this lesson?
6. 6. Why does the restored database contain three rows while the live database contains four rows?
7. 7. What additional artifacts are commonly required for point-in-time recovery beyond a base backup?
8. 8. Why is keeping the only backup on the same host and disk as the source database inadequate?
9. 9. What should an operator do if the backup digest does not match the recorded metadata?
10. 10. What does a successful backup job prove, and what does it not prove?

## After scoring

- Missed items → return to Reading → redo Feynman Retry → reattempt.

<!-- answer key is maintained in instructor materials / automation batch report; not printed for students -->

# Quiz: Configuration Backups and Recovery

**Module:** ARR Data Model & Compose
**Activity type:** Quiz / retrieval practice
**Target:** ≥80%
**Objective:** Explain why a configuration archive alone is not a complete recovery strategy.

## Questions

1. 1. Why is successful creation of a compressed configuration file insufficient proof that recovery will work?
2. 2. What is the difference between an archive checksum and semantic configuration validation?
3. 3. Why should a backup normally be restored into a candidate directory before it replaces active configuration?
4. 4. In the lab, why does the drifted app.json pass the Python validator but fail comparison with the backup manifest?
5. 5. What security limitation remains when an archive and its checksum are writable by the same compromised account?
6. 6. What is the purpose of retaining config.drifted and rollback/pre-recovery-config during promotion?
7. 7. Why should relative paths in a checksum manifest be verified from the intended package root?
8. 8. What does a successful configuration promotion fail to prove about a real application?

## After scoring

- Missed items → return to Reading → redo Feynman Retry → reattempt.

<!-- answer key is maintained in instructor materials / automation batch report; not printed for students -->

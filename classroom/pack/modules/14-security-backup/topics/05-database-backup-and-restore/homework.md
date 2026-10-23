# Homework: Database Backup and Restore

**Module:** Segmentation, Backup & Power
**Activity type:** Homework / independent application
**Objective:** Distinguish a file copy from a transactionally consistent database backup.

## Requirements

Write a backup policy for a fictional homelab inventory service. Define its RPO, RTO, retention periods, storage locations, encryption requirements, restore-test frequency, and responsible operator.
Extend the metadata record with the database schema version and a unique backup identifier. Keep all implementation files beneath /opt/lab-classroom/class74/ if you test the change.
Design three application-level restore assertions that would detect a structurally valid but operationally useless backup.
Compare the native backup and point-in-time recovery mechanisms of PostgreSQL, MariaDB, and SQLite. Identify which artifacts are needed for each platform.
Draft a quarterly restore-drill report containing backup identity, recovery point, start time, completion time, validation checks, observed problems, and remediation owners.
Explain how lost encryption keys could make intact backup files unrecoverable and propose a key-recovery test.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

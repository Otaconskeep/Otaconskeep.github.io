# Reading: Database Backup and Restore

**Module:** Segmentation, Backup & Power
**Activity type:** Reading (Learn)
**Objective:** Distinguish a file copy from a transactionally consistent database backup.

## Vocabulary

| Term | Meaning |
|---|---|
| Backup | A recoverable copy of database data and, when required, supporting metadata or logs, created for use after loss, corruption, or operator error. |
| Restore | The process of placing backup data into a database environment so that it can be inspected or used. |
| Recovery | The broader process of restoring data, applying any required logs, validating the result, and returning a service to an acceptable operational state. |
| Physical backup | A backup of database storage structures, such as data files, pages, or engine-native backup artifacts. |
| Logical backup | An export of logical objects such as schemas, tables, rows, and SQL statements rather than a direct copy of storage pages. |
| Consistent backup | A backup representing a valid database state from a defined point in transactional history, without partial transactions. |
| Recovery point objective | RPO: the maximum acceptable amount of recent data loss, usually expressed as time. |
| Recovery time objective | RTO: the target maximum time allowed to restore an acceptable level of service. |
| Point-in-time recovery | Recovery to a selected time or transaction position by combining a base backup with archived transaction logs. |
| Integrity digest | A cryptographic hash used to detect whether a backup artifact has changed. A digest detects change but does not prove that the database is logically correct. |
| Restore drill | A planned exercise that restores a backup and verifies the recovered data without waiting for a real incident. |
| Retention | The policy defining how long backups are kept and when they expire. |

## Instruction

A database backup is useful only when it can be restored into a valid and trusted state. Simply copying a database file while an application is writing to it may capture a mixture of old and new pages, omit related transaction-log files, or represent an undefined point in time. Database-aware tools avoid this problem by coordinating with the engine. In this lesson, Python calls SQLite's online backup API, which copies a consistent database snapshot while the source database remains open.

Backups are commonly described as physical or logical. A physical backup preserves engine-native storage structures and is often efficient for full-system recovery, but it may depend on a compatible database engine and version. A logical backup exports schemas and records into a portable representation such as SQL or a structured data format. Logical backups can be useful for selective recovery and migrations, but restoring a large export may require recreating indexes, constraints, and other objects. Neither form is universally superior; the format must match the recovery objective.

RPO and RTO turn vague expectations into engineering requirements. If backups are taken every 24 hours and no transaction logs are retained, a failure just before the next backup could lose almost 24 hours of changes. That design therefore cannot satisfy a one-hour RPO. RTO considers the complete recovery workflow: locating credentials, retrieving artifacts, provisioning capacity, restoring data, applying logs, validating the result, and reconnecting applications. A backup job completing successfully says little about the time required for those later steps.

A trustworthy workflow separates backup creation from backup verification. First, create a database-aware backup. Second, calculate and store an integrity digest with identifying metadata such as creation time, source name, tool, and format. Third, restore to an isolated destination. Fourth, run structural checks and application-level assertions. Structural checks can discover damaged database pages, while application-level checks confirm facts that matter to the service, such as the presence of expected records and valid relationships. Finally, record the outcome so operators can demonstrate when recovery was last tested.

A checksum is not a substitute for a restore test. A backup can retain the same hash while still being unusable because it was empty, encrypted with a lost key, created by an incompatible tool, or missing required transaction logs. Conversely, a changed checksum does not explain why the artifact changed; it only signals that investigation is required. Hash metadata must itself be protected because an attacker able to replace both the backup and its recorded digest can conceal tampering.

Restores should normally begin in an isolated location. Replacing a live database before examining the recovered copy can turn one incident into a larger outage. An isolated restore lets the operator check engine compatibility, integrity, row counts, constraints, timestamps, and critical business records. The operator can then decide whether to promote the recovered database, replay newer transactions, merge selected records, or reject the backup.

Backup policy must also account for correlated failure. A backup stored on the same disk and host as the source database may help with a mistaken edit, but it does not protect against disk loss, theft, ransomware, or destruction of the host. Production designs should use separate failure domains, restricted credentials, encryption, retention controls, and at least one copy that cannot be altered through normal production credentials. This lab intentionally keeps all files inside its classroom directory, so it demonstrates workflow rather than geographic or administrative separation.

## Architecture

### components
The live SQLite database at /opt/lab-classroom/class74/live/inventory.db.
A transactionally consistent backup at /opt/lab-classroom/class74/backups/inventory-backup.db.
Metadata containing the backup digest, creation timestamp, source path, and backup path at /opt/lab-classroom/class74/backups/inventory-backup.json.
An isolated restored database at /opt/lab-classroom/class74/restore/inventory-restored.db.
Python 3 and its standard-library sqlite3, hashlib, json, pathlib, and shutil modules.

### data_flow
Initial rows are committed to the live database.
SQLite's backup API copies a consistent snapshot from the live connection to the backup connection.
SHA-256 is calculated over the completed backup artifact and stored in a separate metadata file.
The live database is changed after the recovery point to demonstrate that a backup represents a particular time.
The backup is copied to an isolated restore destination.
The restored database is checked for digest agreement, structural integrity, expected row count, and expected row values.

### trust_boundaries
The live database, backup artifact, metadata, and restored database are separate files but remain in one classroom filesystem boundary.
The lab does not simulate off-host storage, immutable retention, key management, or remote access controls.
A production backup account should have only the permissions required by the engine and storage destination.

## Required reading

- SQLite Backup API documentation: https://www.sqlite.org/backup.html
- SQLite transaction documentation: https://www.sqlite.org/lang_transaction.html
- Python sqlite3 module documentation, including Connection.backup: https://docs.python.org/3/library/sqlite3.html
- NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/publications/detail/sp/800-34/rev-1/final

## References

- SQLite Online Backup API: https://www.sqlite.org/backup.html
- SQLite Transactions: https://www.sqlite.org/lang_transaction.html
- SQLite PRAGMA integrity_check: https://www.sqlite.org/pragma.html#pragma_integrity_check
- Python sqlite3 — DB-API 2.0 interface for SQLite databases: https://docs.python.org/3/library/sqlite3.html
- Python hashlib — Secure hashes and message digests: https://docs.python.org/3/library/hashlib.html
- NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/publications/detail/sp/800-34/rev-1/final
- PostgreSQL Backup and Restore documentation: https://www.postgresql.org/docs/current/backup.html
- MariaDB Backup and Restore Overview: https://mariadb.com/docs/server/server-usage/backing-up-and-restoring-databases

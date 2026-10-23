# Class 74: Database Backup and Restore

**Learning objective:** Distinguish a file copy from a transactionally consistent database backup.; Explain the differences among physical backups, logical backups, snapshots, and transaction-log-based recovery.; Create an online SQLite backup using the database backup API.; Record backup metadata and calculate a SHA-256 integrity digest.; Restore a backup into an isolated location rather than overwriting the live database immediately.; Verify structural integrity, expected row counts, application-level data, and recovery-point behavior.; Develop a backup policy using recovery point objective and recovery time objective requirements.; Recognize that an untested backup is not sufficient evidence of recoverability.
**Bloom level:** Understand / Apply
**Track:** Data Services and Reliability · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** medium
**Build output:** Teach learners how to create, validate, restore, and document a transactionally consistent database backup. The lab uses SQLite and Python's standard library so that backup principles can be practiced without requiring a separate database server. The same operational concepts—consistency, retention, integrity checking, isolated restoration, and recovery verification—apply to larger database platforms.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux distributions capable of running Python 3 and creating files beneath /opt/lab-classroom/class74/.

### software
Python 3.7 or newer is recommended because sqlite3.Connection.backup is available in supported modern Python releases.
Python must be compiled with SQLite support.
No standalone SQLite command-line client is required.

### database_scope
The executable lab is SQLite-specific. The policy concepts apply broadly, but PostgreSQL, MariaDB, MySQL, and other engines require their own native backup, log-retention, and recovery procedures.

### filesystem_scope
All lesson-created data remains beneath /opt/lab-classroom/class74/. The exercise does not demonstrate off-host, object-storage, tape, or immutable backup repositories.

### limitations
The lab does not demonstrate point-in-time log replay.
The lab does not benchmark backup speed, restore speed, compression, or storage consumption.
The lab does not provide production-grade encryption or key management.
The lab uses known sample rows so application-level validation can be deterministic.

## Learning objective

- Distinguish a file copy from a transactionally consistent database backup.
- Explain the differences among physical backups, logical backups, snapshots, and transaction-log-based recovery.
- Create an online SQLite backup using the database backup API.
- Record backup metadata and calculate a SHA-256 integrity digest.
- Restore a backup into an isolated location rather than overwriting the live database immediately.
- Verify structural integrity, expected row counts, application-level data, and recovery-point behavior.
- Develop a backup policy using recovery point objective and recovery time objective requirements.
- Recognize that an untested backup is not sufficient evidence of recoverability.

## Why this matters

Teach learners how to create, validate, restore, and document a transactionally consistent database backup. The lab uses SQLite and Python's standard library so that backup principles can be practiced without requiring a separate database server. The same operational concepts—consistency, retention, integrity checking, isolated restoration, and recovery verification—apply to larger database platforms.

## Prerequisites

- Comfort using a Linux shell and running Python 3 scripts.
- Basic understanding of tables, rows, primary keys, and SQL transactions.
- Permission to create files and directories beneath /opt/lab-classroom/class74/.
- At least 20 MB of free storage beneath /opt/lab-classroom/class74/.
- Python 3 with the standard-library sqlite3 module.

## Required reading

- SQLite Backup API documentation: https://www.sqlite.org/backup.html
- SQLite transaction documentation: https://www.sqlite.org/lang_transaction.html
- Python sqlite3 module documentation, including Connection.backup: https://docs.python.org/3/library/sqlite3.html
- NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/publications/detail/sp/800-34/rev-1/final

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

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

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Write a backup policy for a fictional homelab inventory service. Define its RPO, RTO, retention periods, storage locations, encryption requirements, restore-test frequency, and responsible operator.
Extend the metadata record with the database schema version and a unique backup identifier. Keep all implementation files beneath /opt/lab-classroom/class74/ if you test the change.
Design three application-level restore assertions that would detect a structurally valid but operationally useless backup.
Compare the native backup and point-in-time recovery mechanisms of PostgreSQL, MariaDB, and SQLite. Identify which artifacts are needed for each platform.
Draft a quarterly restore-drill report containing backup identity, recovery point, start time, completion time, validation checks, observed problems, and remediation owners.
Explain how lost encryption keys could make intact backup files unrecoverable and propose a key-recovery test.

## Feynman teach-back

Explain the exercise to another learner without using the phrase "it just copies the file." Describe why the database backup API is used, what recovery point the backup represents, why a digest is calculated, why the restore is placed in a separate directory, and why both integrity checks and application-level assertions are necessary. A strong explanation should note that the restored database intentionally lacks app01 and retains router01 as active because those changes happened after the backup. It should also explain why a successful backup job does not prove that production RPO and RTO requirements can be met.

## Retrieval check

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

## Guided lab

### scope
Every command in this lab creates or modifies content only beneath /opt/lab-classroom/class74/. The exercise does not stop services, change firewall rules, alter operating-system configuration, or overwrite a database outside the classroom directory.

### steps
### step
1

### title
Create the classroom directories and initial database

### command
python3 - <<'PY'
from pathlib import Path
import os
import sqlite3

root = Path('/opt/lab-classroom/class74')
if root.exists() and any(root.iterdir()):
    raise SystemExit('Safety stop: /opt/lab-classroom/class74 is not empty. Use the rollback procedure or inspect the existing work.')
for directory in (root, root / 'live', root / 'backups', root / 'restore'):
    directory.mkdir(parents=True, exist_ok=True)
    os.chmod(directory, 0o700)

db_path = root / 'live' / 'inventory.db'
with sqlite3.connect(db_path) as conn:
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('CREATE TABLE devices (id INTEGER PRIMARY KEY, hostname TEXT NOT NULL UNIQUE, role TEXT NOT NULL, state TEXT NOT NULL, updated_at TEXT NOT NULL)')
    conn.executemany(
        'INSERT INTO devices(id, hostname, role, state, updated_at) VALUES (?, ?, ?, ?, ?)',
        [
            (1, 'router01', 'router', 'active', '2025-01-15T10:00:00Z'),
            (2, 'nas01', 'storage', 'active', '2025-01-15T10:01:00Z'),
            (3, 'db01', 'database', 'maintenance', '2025-01-15T10:02:00Z')
        ]
    )
    conn.commit()
os.chmod(db_path, 0o600)
print(db_path)
PY
### step
2

### title
Inspect the live database before backup

### command
python3 - <<'PY'
import sqlite3
from pathlib import Path

path = Path('/opt/lab-classroom/class74/live/inventory.db')
with sqlite3.connect(path) as conn:
    rows = conn.execute('SELECT id, hostname, role, state, updated_at FROM devices ORDER BY id').fetchall()
for row in rows:
    print(row)
print('row_count=', len(rows))
PY
### step
3

### title
Create a consistent backup and its metadata

### command
python3 - <<'PY'
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import sqlite3

root = Path('/opt/lab-classroom/class74')
source = root / 'live' / 'inventory.db'
backup = root / 'backups' / 'inventory-backup.db'
metadata = root / 'backups' / 'inventory-backup.json'
if backup.exists() or metadata.exists():
    raise SystemExit('Safety stop: backup output already exists.')
with sqlite3.connect(source) as src, sqlite3.connect(backup) as dst:
    src.backup(dst)
with backup.open('rb') as handle:
    digest = hashlib.sha256(handle.read()).hexdigest()
record = {
    'format': 'SQLite database produced with sqlite3.Connection.backup',
    'source': str(source),
    'backup': str(backup),
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'sha256': digest
}
metadata.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
os.chmod(backup, 0o600)
os.chmod(metadata, 0o600)
print(json.dumps(record, indent=2))
PY
### step
4

### title
Make post-backup changes to the live database

### command
python3 - <<'PY'
from pathlib import Path
import sqlite3

path = Path('/opt/lab-classroom/class74/live/inventory.db')
with sqlite3.connect(path) as conn:
    conn.execute("UPDATE devices SET state = 'degraded', updated_at = '2025-01-15T11:00:00Z' WHERE hostname = 'router01'")
    conn.execute("INSERT INTO devices(id, hostname, role, state, updated_at) VALUES (4, 'app01', 'application', 'active', '2025-01-15T11:01:00Z')")
    conn.commit()
    rows = conn.execute('SELECT id, hostname, state FROM devices ORDER BY id').fetchall()
for row in rows:
    print(row)
print('live_row_count=', len(rows))
PY
### step
5

### title
Verify the stored backup digest before restoration

### command
python3 - <<'PY'
from pathlib import Path
import hashlib
import json

root = Path('/opt/lab-classroom/class74')
backup = root / 'backups' / 'inventory-backup.db'
metadata = json.loads((root / 'backups' / 'inventory-backup.json').read_text(encoding='utf-8'))
actual = hashlib.sha256(backup.read_bytes()).hexdigest()
print('recorded_sha256=', metadata['sha256'])
print('actual_sha256=', actual)
print('digest_match=', actual == metadata['sha256'])
if actual != metadata['sha256']:
    raise SystemExit('Backup digest mismatch; restoration is blocked.')
PY
### step
6

### title
Restore into an isolated database

### command
python3 - <<'PY'
from pathlib import Path
import os
import shutil

root = Path('/opt/lab-classroom/class74')
source = root / 'backups' / 'inventory-backup.db'
destination = root / 'restore' / 'inventory-restored.db'
if destination.exists():
    raise SystemExit('Safety stop: restore destination already exists.')
shutil.copy2(source, destination)
os.chmod(destination, 0o600)
print(destination)
PY
### step
7

### title
Validate structure and application-level data

### command
python3 - <<'PY'
from pathlib import Path
import sqlite3

path = Path('/opt/lab-classroom/class74/restore/inventory-restored.db')
expected = [
    (1, 'router01', 'router', 'active', '2025-01-15T10:00:00Z'),
    (2, 'nas01', 'storage', 'active', '2025-01-15T10:01:00Z'),
    (3, 'db01', 'database', 'maintenance', '2025-01-15T10:02:00Z')
]
with sqlite3.connect(path) as conn:
    integrity = conn.execute('PRAGMA integrity_check').fetchone()[0]
    rows = conn.execute('SELECT id, hostname, role, state, updated_at FROM devices ORDER BY id').fetchall()
print('integrity_check=', integrity)
print('restored_rows=', rows)
print('expected_rows_match=', rows == expected)
if integrity != 'ok':
    raise SystemExit('Restored database failed SQLite integrity checking.')
if rows != expected:
    raise SystemExit('Restored application data does not match the expected recovery point.')
print('RESTORE_VERIFIED')
PY
### step
8

### title
Compare live and restored recovery points

### command
python3 - <<'PY'
from pathlib import Path
import sqlite3

root = Path('/opt/lab-classroom/class74')
def read_rows(path):
    with sqlite3.connect(path) as conn:
        return conn.execute('SELECT id, hostname, state, updated_at FROM devices ORDER BY id').fetchall()
live = read_rows(root / 'live' / 'inventory.db')
restored = read_rows(root / 'restore' / 'inventory-restored.db')
print('live=', live)
print('restored=', restored)
print('live_count=', len(live))
print('restored_count=', len(restored))
PY

## Expected results

- The initial live database contains exactly three devices: router01, nas01, and db01.
- The backup metadata contains a SHA-256 digest and an ISO 8601 UTC creation timestamp.
- The recorded backup digest matches the digest recalculated before restoration.
- After the simulated post-backup activity, the live database contains four rows and router01 has the state degraded.
- The isolated restored database contains three rows because it represents the earlier recovery point.
- In the restored database, router01 has the state active and app01 is absent.
- SQLite PRAGMA integrity_check returns ok for the restored database.
- The final validation prints RESTORE_VERIFIED.

## Verification checkpoints

- [ ] Confirm that all lesson artifacts are beneath /opt/lab-classroom/class74/.
- [ ] Confirm that /opt/lab-classroom/class74/backups/inventory-backup.db exists and is not empty.
- [ ] Confirm that /opt/lab-classroom/class74/backups/inventory-backup.json contains source, backup, created_utc, format, and sha256 fields.
- [ ] Recalculate SHA-256 over the backup and confirm that it equals the metadata value.
- [ ] Run PRAGMA integrity_check against the restored database and require the exact result ok.
- [ ] Query the restored devices table and confirm that its ordered rows exactly match the three pre-backup records.
- [ ] Confirm that app01 exists in the live database but not in the restored database.
- [ ] Confirm that router01 is degraded in the live database and active in the restored database.
- [ ] Treat the restore as failed if any structural or application-level assertion differs from the expected recovery point.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Python reports that the sqlite3 module is unavailable. | The installed Python build lacks SQLite support or Python 3 is incomplete. | Use a Python 3 installation that includes the standard-library sqlite3 module. Verify with python3 -c "import sqlite3; print(sqlite3.sqlite_version)" before rerunning the lab. |
| The setup step stops because the classroom directory is not empty. | A previous attempt or unrelated file already exists within the lab directory. | Inspect /opt/lab-classroom/class74/, preserve any required evidence, and then use the explicit rollback procedure. Do not bypass the safety check without understanding the existing files. |
| Permission denied is reported when creating the classroom directory. | The current account cannot write beneath /opt/lab-classroom/. | Ask the lab administrator to create and assign the class74 directory to the learner. Do not redirect the exercise to an unapproved system path. |
| The digest verification reports digest_match=False. | The backup artifact or metadata changed after creation, or the wrong files are being compared. | Do not continue with the restore as though the artifact were trusted. Confirm the exact paths, inspect timestamps and access history, and recreate the backup from a known-good source if this is a classroom rerun. |
| The restore step says the destination already exists. | An earlier restore is still present. | Preserve the existing restored database if it is needed for investigation. Otherwise use the rollback procedure and restart the lab from step 1. |
| PRAGMA integrity_check does not return ok. | The backup or restored copy is damaged, incomplete, or not a valid SQLite database. | Reject the restored artifact, compare its digest with the expected backup digest, verify available storage, and create a fresh database-aware backup. |
| The restored database contains app01 or shows router01 as degraded. | The live database was copied after the simulated changes, or the verification script opened the live path instead of the restore path. | Check every source and destination path. The expected backup must be created before step 4, and validation must target /opt/lab-classroom/class74/restore/inventory-restored.db. |
| The backup operation reports that the database is locked. | Another process holds a conflicting transaction or the source is being used in an unexpected locking mode. | Identify the process using only the classroom database, allow its transaction to complete, and retry. Do not terminate unrelated production processes for this exercise. |

## Security considerations

Database backups frequently contain the same secrets, personal data, and operational records as the live database; protect them to the same or a stronger standard.
Use a dedicated backup identity with narrowly scoped database and storage permissions.
Encrypt backup data in transit and at rest in production. Store encryption keys separately from the backup artifacts and test key recovery.
Protect metadata and digests from unauthorized modification. A digest stored beside a backup is useful for accidental corruption detection but is not strong evidence against a malicious actor who can alter both files.
Keep at least one production backup copy in a failure domain separate from the database host.
Consider immutable or offline retention so compromised production credentials cannot silently destroy every recovery copy.
Audit backup creation, retrieval, expiration, restore attempts, and changes to retention policies.
Restore sensitive production data only into environments with equivalent access controls, logging, and data-handling rules.
Sanitize or synthesize data before using restored production databases in development or training environments.
Do not log database credentials in shell history, scripts, job output, or backup metadata.
The lab applies restrictive owner-only modes to its directories and files, but permissions alone do not provide encryption or host isolation.

## Rollback

### purpose
Remove only the known files and empty directories created by this lesson. The script refuses to operate unless the resolved root is exactly /opt/lab-classroom/class74.

### command
python3 - <<'PY'
from pathlib import Path

root = Path('/opt/lab-classroom/class74')
if root.resolve() != Path('/opt/lab-classroom/class74'):
    raise SystemExit('Safety stop: unexpected rollback path.')
files = [
    root / 'restore' / 'inventory-restored.db',
    root / 'backups' / 'inventory-backup.json',
    root / 'backups' / 'inventory-backup.db',
    root / 'live' / 'inventory.db'
]
for path in files:
    if path.exists():
        if not path.is_file():
            raise SystemExit(f'Safety stop: expected a regular file at {path}')
        path.unlink()
for directory in (root / 'restore', root / 'backups', root / 'live', root):
    if directory.exists():
        directory.rmdir()
print('Class 74 lab artifacts removed.')
PY

### validation
Confirm that /opt/lab-classroom/class74/ no longer exists. If removal stops because an unexpected file or non-empty directory is present, inspect it manually rather than broadening the deletion procedure.

## Video narration notes

Welcome to Class 74, Database Backup and Restore. In this lesson, we are not treating backup as a file-copy checkbox. We are treating it as one stage in a tested recovery process.

The lab begins by creating a small SQLite inventory database with three committed device records. We then inspect those rows so that the intended recovery point is clear. Next, Python opens the source and destination databases and invokes SQLite's backup API. This matters because the database engine, rather than a generic copy operation, creates the consistent snapshot.

After the backup finishes, the lab calculates a SHA-256 digest and writes metadata describing the artifact. The digest gives us a way to detect later byte-level changes. Remember that this is only one control. It does not tell us whether the database contains the right information or whether we possess everything needed for recovery.

We then change the live database. Router01 becomes degraded, and a fourth device named app01 is inserted. These changes occur after the backup, so they must not appear in the restored recovery point. This deliberate difference demonstrates why operators need to know exactly when a backup was taken.

Before restoration, we recalculate the digest and compare it with the metadata. If the values differ, the workflow stops. If they match, the backup is copied into the isolated restore directory. We do not overwrite the live database because the recovered artifact has not yet been validated.

Validation occurs at two levels. SQLite's integrity check examines the database structure. The application-level assertion then compares the rows with the exact records expected at backup time. A structurally valid database could still be empty, outdated, or logically wrong, so both categories are necessary.

At the end, compare the live and restored databases. The live database has four rows and shows router01 as degraded. The restored database has three rows and shows router01 as active. That difference is expected and proves that the restore represents the selected recovery point.

In production, expand this workflow with separate storage failure domains, encryption, protected keys, immutable retention, monitoring, documented ownership, and scheduled restore drills. Measure the full recovery process against RPO and RTO rather than measuring only whether a backup command completed.

## References

- SQLite Online Backup API: https://www.sqlite.org/backup.html
- SQLite Transactions: https://www.sqlite.org/lang_transaction.html
- SQLite PRAGMA integrity_check: https://www.sqlite.org/pragma.html#pragma_integrity_check
- Python sqlite3 — DB-API 2.0 interface for SQLite databases: https://docs.python.org/3/library/sqlite3.html
- Python hashlib — Secure hashes and message digests: https://docs.python.org/3/library/hashlib.html
- NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/publications/detail/sp/800-34/rev-1/final
- PostgreSQL Backup and Restore documentation: https://www.postgresql.org/docs/current/backup.html
- MariaDB Backup and Restore Overview: https://mariadb.com/docs/server/server-usage/backing-up-and-restoring-databases

## Mastery gate

- [ ] Objectives demonstrated with evidence
- [ ] Feynman complete
- [ ] Quiz self-scored ≥80%
- [ ] Lab verification boxes checked
- [ ] Rollback understood

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Return to this class whenever a later service fails for identity, process, log, remote access, update, or routing reasons covered here.

# Lab: Database Backup and Restore

**Module:** Segmentation, Backup & Power
**Activity type:** Lab (Practice)
**Lab risk:** medium
**Objective:** Distinguish a file copy from a transactionally consistent database backup.

## Before you start

- Comfort using a Linux shell and running Python 3 scripts.
- Basic understanding of tables, rows, primary keys, and SQL transactions.
- Permission to create files and directories beneath /opt/lab-classroom/class74/.
- At least 20 MB of free storage beneath /opt/lab-classroom/class74/.
- Python 3 with the standard-library sqlite3 module.

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

## Verification

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

## Security

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

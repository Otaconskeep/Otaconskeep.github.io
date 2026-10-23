# Lab: The 3-2-1 Backup Strategy

**Module:** Segmentation, Backup & Power
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain what each number in the 3-2-1 strategy represents.

## Before you start

- Basic familiarity with Linux paths, files, and directories.
- Ability to run commands in a shell and read command output.
- Basic understanding of storage devices, network storage, and file integrity.
- Python 3 available on the lab system.
- Permission to create and modify content under /opt/lab-classroom/class72/.

## Guided lab

### scope
Every operation that creates, changes, extracts, or deletes data is restricted to /opt/lab-classroom/class72/.

### steps
### step
1

### title
Create the primary data set and baseline manifest

### command
python3 - <<'PY'
from pathlib import Path
import hashlib
import json

root = Path('/opt/lab-classroom/class72').resolve()
primary = root / 'primary'
control = root / 'control'
primary.mkdir(parents=True, exist_ok=True)
control.mkdir(parents=True, exist_ok=True)

files = {
    'inventory.txt': 'router\nswitch\nserver\nbackup-target\n',
    'service-config.ini': '[service]\nname=academy-demo\nbackup_required=true\n',
    'recovery-notes.txt': 'Owner: Homelab Academy\nRestore priority: inventory, configuration, notes\n'
}
for relative_name, content in files.items():
    (primary / relative_name).write_text(content, encoding='utf-8')

def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

manifest = {path.name: sha256(path) for path in sorted(primary.iterdir()) if path.is_file()}
(control / 'primary-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(json.dumps(manifest, indent=2))
PY
### step
2

### title
Create the local backup and simulated off-site archive

### command
python3 - <<'PY'
from pathlib import Path
import json
import shutil
import tarfile

root = Path('/opt/lab-classroom/class72').resolve()
primary = root / 'primary'
local_backup = root / 'local-backup'
offsite = root / 'simulated-offsite'
control = root / 'control'

for directory in (local_backup, offsite, control):
    directory.mkdir(parents=True, exist_ok=True)

for source in sorted(primary.iterdir()):
    if source.is_file():
        shutil.copy2(source, local_backup / source.name)

archive = offsite / 'class72-primary-backup.tar.gz'
with tarfile.open(archive, 'w:gz') as bundle:
    for source in sorted(primary.iterdir()):
        if source.is_file():
            bundle.add(source, arcname=f'primary/{source.name}', recursive=False)

inventory = {
    'primary_copy': str(primary),
    'local_backup_copy': str(local_backup),
    'simulated_offsite_copy': str(archive),
    'physically_compliant_3_2_1': False,
    'reason': 'All lab copies share the same underlying classroom filesystem.'
}
(control / 'backup-inventory.json').write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')
print(json.dumps(inventory, indent=2))
PY
### step
3

### title
Verify the local backup against the baseline

### command
python3 - <<'PY'
from pathlib import Path
import hashlib
import json
import sys

root = Path('/opt/lab-classroom/class72').resolve()
manifest = json.loads((root / 'control/primary-manifest.json').read_text(encoding='utf-8'))
backup = root / 'local-backup'

def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

actual = {path.name: sha256(path) for path in sorted(backup.iterdir()) if path.is_file()}
if actual != manifest:
    print('FAIL: local backup differs from the baseline manifest')
    print(json.dumps({'expected': manifest, 'actual': actual}, indent=2))
    sys.exit(1)
print('PASS: local backup matches the baseline manifest')
PY
### step
4

### title
Restore the simulated off-site archive into an isolated directory

### command
python3 - <<'PY'
from pathlib import Path
import shutil
import tarfile

root = Path('/opt/lab-classroom/class72').resolve()
archive = root / 'simulated-offsite/class72-primary-backup.tar.gz'
restore = root / 'restore-test'
restore.mkdir(parents=True, exist_ok=True)

with tarfile.open(archive, 'r:gz') as bundle:
    members = bundle.getmembers()
    for member in members:
        target = (restore / member.name).resolve()
        if restore != target and restore not in target.parents:
            raise RuntimeError(f'Archive member escapes restore directory: {member.name}')
        if member.issym() or member.islnk():
            raise RuntimeError(f'Archive contains an unsupported link: {member.name}')
    for member in members:
        if member.isdir():
            (restore / member.name).mkdir(parents=True, exist_ok=True)
        elif member.isfile():
            destination = restore / member.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = bundle.extractfile(member)
            if source is None:
                raise RuntimeError(f'Unable to read archive member: {member.name}')
            with source, destination.open('wb') as output:
                shutil.copyfileobj(source, output)
print(f'Restored archive into {restore}')
PY
### step
5

### title
Validate the restored files

### command
python3 - <<'PY'
from pathlib import Path
import hashlib
import json
import sys

root = Path('/opt/lab-classroom/class72').resolve()
manifest = json.loads((root / 'control/primary-manifest.json').read_text(encoding='utf-8'))
restored = root / 'restore-test/primary'

def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

actual = {path.name: sha256(path) for path in sorted(restored.iterdir()) if path.is_file()}
if actual != manifest:
    print('FAIL: restored data differs from the baseline manifest')
    print(json.dumps({'expected': manifest, 'actual': actual}, indent=2))
    sys.exit(1)
print('PASS: restored files match the baseline manifest')
print('Restore test completed without overwriting the primary copy')
PY
### step
6

### title
Review the backup inventory and identify missing production controls

### command
python3 - <<'PY'
from pathlib import Path
import json

path = Path('/opt/lab-classroom/class72/control/backup-inventory.json')
record = json.loads(path.read_text(encoding='utf-8'))
print(json.dumps(record, indent=2))
print('\nProduction gaps to resolve: separate medium, separate failure domain, off-site placement, retention, encryption, monitoring, and scheduled restore testing.')
PY

## Expected results

- The primary directory contains inventory.txt, service-config.ini, and recovery-notes.txt.
- The control directory contains primary-manifest.json and backup-inventory.json.
- The local-backup directory contains a second copy of each primary file.
- The simulated-offsite directory contains class72-primary-backup.tar.gz.
- The local backup verification prints PASS and exits successfully.
- The restore operation creates restored files under /opt/lab-classroom/class72/restore-test/primary/ without overwriting the primary data.
- The restored-file verification prints PASS and confirms that the restored hashes match the baseline manifest.
- The inventory explicitly reports that the classroom layout is not physically compliant with 3-2-1 because all copies share one filesystem.

## Verification

- [ ] Run the local verification step again; it must print 'PASS: local backup matches the baseline manifest'.
- [ ] Run the restored-file verification step again; it must print 'PASS: restored files match the baseline manifest'.
- [ ] Confirm that /opt/lab-classroom/class72/control/primary-manifest.json lists exactly three files and a SHA-256 value for each file.
- [ ] Confirm that /opt/lab-classroom/class72/control/backup-inventory.json sets physically_compliant_3_2_1 to false.
- [ ] Confirm that the primary files still exist after restoration and were not used as the restore destination.
- [ ] Open the restored text files and confirm that their content is meaningful, because hash agreement alone does not prove application-level usability.
- [ ] For a real deployment, document evidence that the local backup and off-site backup use independent devices, credentials, and failure domains rather than relying only on different directory names.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Python reports PermissionError while creating the class directory. | The current account does not have permission to write under /opt/lab-classroom/. | Have the lab administrator pre-create /opt/lab-classroom/class72/ with appropriate ownership. Do not redirect the exercise into unrelated system paths. |
| The local backup verification reports different expected and actual hashes. | A source or backup file changed after the manifest was generated, a file was omitted, or an earlier lab run left inconsistent content. | Inspect the reported file names, regenerate the lab from a clean class72 directory if appropriate, recreate the backup, and repeat verification. |
| The restored-file verification reports a missing file. | The archive was created before all primary files existed, the archive is incomplete, or the restore operation did not complete. | Recreate the archive from the intended primary data, repeat the isolated restore, and compare the archive contents with the manifest. |
| Opening the archive raises a compressed-file or end-of-file error. | The archive is truncated, corrupted, or not actually a valid gzip-compressed tar archive. | Treat the archive as unusable, investigate storage or transfer errors, recreate it from a known-good copy, and repeat the restore test. |
| The hash verification passes, but the restored data does not work in the application. | File-level integrity does not guarantee application consistency, compatible software versions, complete dependencies, or a valid database transaction state. | Add application-aware backup procedures and recovery tests, including service configuration, database consistency checks, dependencies, credentials, and application startup validation. |
| A proposed production design has three copies but all are accessible through the same administrator account. | The design counts copies without separating administrative failure domains. | Use separately protected backup identities, minimal privileges, deletion controls, multifactor authentication where supported, and offline or immutable retention. |

## Security

### principles
Use a dedicated backup identity instead of normal interactive administrator credentials.
Grant backup writers only the access needed to create backups; separate backup deletion and retention administration where possible.
Encrypt backups in transit and at rest, and protect encryption keys separately from the data they unlock.
Maintain at least one offline, immutable, or strongly deletion-resistant recovery copy.
Prevent production systems from having unrestricted deletion rights over every retained backup generation.
Monitor failed jobs, missing recovery points, unusual deletion activity, unexpected backup size changes, and integrity failures.
Do not expose backup consoles or storage management interfaces directly to untrusted networks.
Treat restored data as potentially hostile until it has been scanned and validated, especially after a security incident.
Protect backup inventories because they reveal valuable systems, data locations, retention schedules, and recovery procedures.
Use safe archive extraction controls to reject path traversal and unexpected links.

### integrity_note
SHA-256 comparison detects whether the tested bytes differ from the recorded baseline. It does not establish that the original data was correct, safe, current, or free of malicious content.

### confidentiality_note
The classroom archive is not encrypted and contains only synthetic lesson data. Production backups containing sensitive information require approved encryption and key-management controls.

## Rollback

### scope
Rollback removes only the classroom directory after the learner confirms that no needed evidence remains inside it.

### command
python3 - <<'PY'
from pathlib import Path
import shutil

allowed = Path('/opt/lab-classroom/class72').resolve()
target = Path('/opt/lab-classroom/class72').resolve()
if target != allowed:
    raise RuntimeError('Refusing cleanup because the target is not the exact approved class72 path')
if target.exists():
    shutil.rmtree(target)
    print(f'Removed {target}')
else:
    print(f'Nothing to remove: {target} does not exist')
PY

### post_rollback_check
Use a read-only directory listing of /opt/lab-classroom/ and confirm that class72 is absent while unrelated class directories remain untouched.

### recovery_note
The cleanup is destructive. If lesson evidence must be retained, copy it to an approved backup destination before running rollback.

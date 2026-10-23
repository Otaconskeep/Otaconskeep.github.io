# Class 72: The 3-2-1 Backup Strategy

**Learning objective:** Explain what each number in the 3-2-1 strategy represents.; Distinguish a backup copy from synchronization, replication, snapshots, and redundant storage.; Identify correlated failure domains that can invalidate an otherwise convincing backup design.; Create a primary data set, a local backup copy, and a simulated off-site archive.; Generate and compare cryptographic hashes to detect corruption or incomplete copies.; Perform a test restoration without overwriting the primary data.; Document recovery objectives, retention expectations, encryption requirements, and backup ownership.; Evaluate whether a proposed design provides meaningful protection against hardware failure, mistakes, theft, ransomware, and site loss.
**Bloom level:** Understand / Apply
**Track:** Storage, Backup, and Disaster Recovery · **Difficulty:** beginner · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach learners how to design, document, test, and verify a 3-2-1 backup strategy: three copies of important data, stored using at least two independent storage media or failure domains, with at least one copy maintained off-site. The lab demonstrates the workflow inside a restricted classroom directory while clearly distinguishing that simulation from a production-quality implementation.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-25
**Compatibility:** ### operating_systems
Linux systems providing Python 3 and writable access to /opt/lab-classroom/class72/.

### python
Python 3.8 or later is recommended.

### privileges
The learner requires write permission only within /opt/lab-classroom/class72/. Elevated privileges are not inherently required when the directory has been prepared with suitable ownership.

### filesystem
The exercise uses ordinary files and directories and does not require snapshot, copy-on-write, or extended-attribute support.

### limitations
The lab does not test physical media separation, cloud-provider independence, geographic separation, immutable retention, encrypted backups, application-consistent database backup, or production-scale recovery.

## Learning objective

- Explain what each number in the 3-2-1 strategy represents.
- Distinguish a backup copy from synchronization, replication, snapshots, and redundant storage.
- Identify correlated failure domains that can invalidate an otherwise convincing backup design.
- Create a primary data set, a local backup copy, and a simulated off-site archive.
- Generate and compare cryptographic hashes to detect corruption or incomplete copies.
- Perform a test restoration without overwriting the primary data.
- Document recovery objectives, retention expectations, encryption requirements, and backup ownership.
- Evaluate whether a proposed design provides meaningful protection against hardware failure, mistakes, theft, ransomware, and site loss.

## Why this matters

Teach learners how to design, document, test, and verify a 3-2-1 backup strategy: three copies of important data, stored using at least two independent storage media or failure domains, with at least one copy maintained off-site. The lab demonstrates the workflow inside a restricted classroom directory while clearly distinguishing that simulation from a production-quality implementation.

## Prerequisites

- Basic familiarity with Linux paths, files, and directories.
- Ability to run commands in a shell and read command output.
- Basic understanding of storage devices, network storage, and file integrity.
- Python 3 available on the lab system.
- Permission to create and modify content under /opt/lab-classroom/class72/.

## Required reading

- CISA Stop Ransomware Guide, especially the recommendations for offline, encrypted, and regularly tested backups: https://www.cisa.gov/stopransomware/ransomware-guide
- NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/pubs/sp/800/34/r1/final
- Python hashlib documentation for understanding the SHA-256 integrity checks used in the lab: https://docs.python.org/3/library/hashlib.html
- Python tarfile documentation for understanding the archive and restore operations used in the lab: https://docs.python.org/3/library/tarfile.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| 3-2-1 backup strategy | A planning rule that calls for three copies of important data, stored across at least two independent media or failure domains, with at least one copy kept off-site. |
| Primary copy | The active data used by applications or users. It is one of the three copies, but it is not itself considered a backup. |
| Backup copy | A separately managed copy retained so data can be recovered after deletion, corruption, compromise, or infrastructure failure. |
| Failure domain | A set of components that can fail together because they share a dependency, such as one disk, host, power circuit, account, building, or administrative credential. |
| Off-site | Stored far enough from the primary location that a local disaster, theft, or facility outage is unlikely to destroy both copies. |
| Offline backup | A backup that is not continuously reachable or writable from production systems. |
| Immutable backup | A backup protected against modification or deletion for a defined retention period, including modification by compromised administrative credentials where the platform supports that guarantee. |
| Retention | The policy defining how many recovery versions are kept and how long each version remains available. |
| Recovery Point Objective | The maximum acceptable amount of data loss measured in time. It determines how frequently backups or recoverable versions should be created. |
| Recovery Time Objective | The target duration for restoring a service or data set after an interruption. |
| Restore test | A controlled recovery exercise that proves backup data can be read, reconstructed, and validated. |
| Checksum | A value calculated from data and used to detect accidental changes. This lab uses SHA-256 hashes as integrity evidence, not as proof that a file is trustworthy or malware-free. |

## Instruction

The 3-2-1 strategy begins with three copies: the active primary copy and two additional backup copies. Those copies must not merely be three directory names pointing to the same vulnerable storage. If all copies reside on one physical disk, one host, one power supply, or one administrative account, a single failure or compromise may destroy all of them. The second number therefore requires at least two independent storage media or meaningful failure domains. Examples include local server storage plus removable storage, a storage appliance plus object storage, or disk backup plus tape. The third number requires one copy to be off-site so a fire, flood, theft, electrical event, or building-wide outage does not eliminate every recovery option.

A backup is not the same thing as synchronization. Synchronization may quickly reproduce an accidental deletion or encrypted file across every replica. RAID and storage replication improve availability, but they usually preserve current state rather than a recoverable history. Snapshots can be valuable recovery points, yet snapshots stored and administered with the source may remain exposed to array failure, account compromise, or ransomware. These technologies can contribute to a backup architecture, but they do not automatically satisfy it.

A credible backup plan also includes retention, access control, encryption, monitoring, and restoration testing. The Recovery Point Objective determines how much recent work may be lost, while the Recovery Time Objective describes how quickly recovery should complete. Backup jobs must report failures, but a successful job report alone is insufficient. Operators should verify integrity, inspect expected files, and periodically restore into an isolated location. Recovery credentials and encryption keys must themselves be protected and recoverable.

This lab creates three logical copies under one classroom directory: a primary data set, a local backup copy, and a compressed archive representing an off-site transfer. Because all three remain on the same actual lab filesystem, the exercise demonstrates process and verification but does not physically satisfy the two-media or off-site requirements. A production implementation must place the backup destinations in genuinely independent failure domains. The final restore test extracts the archive into a separate restore directory and compares SHA-256 hashes with the original manifest. That test provides evidence that the selected files are present and unchanged, but it does not replace application-aware validation, malware scanning, database consistency checks, or a complete disaster-recovery exercise.

## Architecture

### production_pattern
Copy 1: active application data on primary storage.
Copy 2: versioned local backup on a separately managed storage device or system.
Copy 3: encrypted off-site backup in a separate facility, account, or provider failure domain.
At least one backup should be offline, immutable, or otherwise resistant to deletion through compromised production credentials.
Monitoring should alert on missed jobs, unexpected backup size changes, integrity failures, and approaching capacity limits.
Scheduled restore tests should validate both data and the documented recovery procedure.

### lab_topology
### primary
/opt/lab-classroom/class72/primary/

### local_backup
/opt/lab-classroom/class72/local-backup/

### simulated_offsite
/opt/lab-classroom/class72/simulated-offsite/

### restore_test
/opt/lab-classroom/class72/restore-test/

### control_data
/opt/lab-classroom/class72/control/

### important_limitation
The lab directories share one underlying filesystem and therefore represent logical roles only. They do not provide independent media, host, account, geographic, or disaster failure domains.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Design a 3-2-1 backup plan for one real or hypothetical homelab service, such as a password manager, photo library, media catalog, source-code service, or home automation controller.

### deliverables
Identify the primary data, including databases, uploaded files, configuration, secrets, and required encryption keys.
Describe the two backup copies and the distinct storage or failure domains used by each.
Explain how the off-site copy is protected from production credential compromise.
Define a Recovery Point Objective and Recovery Time Objective based on service importance.
Define backup frequency, retention periods, encryption, monitoring, and ownership.
Write a restore-test procedure that restores into an isolated location and verifies application usability.
List at least five failure scenarios and state which recovery copy handles each scenario.

### evaluation_criteria
The plan should identify correlated risks rather than merely counting copies. It should include practical restoration evidence, credential separation, retention, key recovery, and a clear explanation of any remaining single points of failure.

## Feynman teach-back

### prompt
Explain the 3-2-1 strategy to someone who believes three folders on one server are sufficient.

### model_explanation
I need three copies because one is the live data and two are recovery copies. I also need separation: if every copy is on one server or one disk, that hardware failure can destroy all three. At least one copy must be away from the primary site so a building-level event does not remove every option. Synchronization, RAID, and replication can improve availability, but they may copy deletion or corruption and may not preserve old versions. A backup plan is only credible when I can restore the data, verify its integrity, and meet the required recovery time.

### self_check
Did the explanation count the active data as one of the three copies?
Did it explain why separate folders are not separate media or failure domains?
Did it distinguish availability technologies from recoverable backup history?
Did it mention off-site protection and restore testing?
Could the listener identify at least one event that would defeat the proposed design?

## Retrieval check

1. 1. In the 3-2-1 strategy, what are the three copies?
2. 2. Why do three directories on one physical disk fail to provide a strong 3-2-1 design?
3. 3. Is RAID a complete substitute for backups? Explain briefly.
4. 4. What is the purpose of keeping at least one copy off-site?
5. 5. What is the difference between a Recovery Point Objective and a Recovery Time Objective?
6. 6. Why can file synchronization fail to protect against accidental deletion or ransomware?
7. 7. What does a successful SHA-256 comparison prove, and what does it not prove?
8. 8. Why should a restore test use a separate destination instead of immediately overwriting production data?
9. 9. Name two controls that can reduce the risk that ransomware deletes or encrypts every backup.
10. 10. Does the classroom lab physically satisfy 3-2-1? Why or why not?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

Begin by drawing three boxes: primary data, local backup, and off-site backup. Explain that the number three counts the active data plus two backup copies. Then draw a boundary around the primary and local systems and another boundary around the off-site system. Emphasize that directories are not failure domains: separate disks, hosts, accounts, facilities, and administrative controls matter. Contrast backups with RAID, replication, snapshots, and synchronization. These tools can be useful, but they do not automatically retain independently recoverable history. Walk through the lab topology and explicitly state that it is a simulation because every directory is on the same classroom filesystem. Create the synthetic primary files and record their SHA-256 hashes. Copy the files to the local backup role, build the simulated off-site archive, and inspect the inventory record that marks the layout as physically noncompliant. Verify the local copy, restore the archive into an isolated directory, and compare restored hashes with the baseline. Explain that restoration is the practical test of a backup: a completed job is only a claim until recovery succeeds. Close by reviewing Recovery Point Objective, Recovery Time Objective, retention, encryption, separate credentials, offline or immutable copies, monitoring, and application-aware validation. Ask learners to identify which single failures could still affect every copy in their own designs.

## References

- CISA, Stop Ransomware Guide: https://www.cisa.gov/stopransomware/ransomware-guide
- NIST Special Publication 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/pubs/sp/800/34/r1/final
- NIST Special Publication 800-209, Security Guidelines for Storage Infrastructure: https://csrc.nist.gov/pubs/sp/800/209/final
- Python 3 hashlib documentation: https://docs.python.org/3/library/hashlib.html
- Python 3 tarfile documentation: https://docs.python.org/3/library/tarfile.html
- Python 3 shutil documentation: https://docs.python.org/3/library/shutil.html

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

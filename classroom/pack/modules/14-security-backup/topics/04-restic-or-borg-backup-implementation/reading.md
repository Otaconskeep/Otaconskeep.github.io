# Reading: Restic or Borg Backup Implementation

**Module:** Segmentation, Backup & Power
**Activity type:** Reading (Learn)
**Objective:** Initialize and use a password-protected local Restic repository.

## Vocabulary

| Term | Meaning |
|---|---|
| Repository | The Restic-managed destination containing encrypted metadata, snapshots, indexes, and deduplicated data packs. |
| Snapshot | An immutable backup record that references a filesystem state, source paths, timestamp, host, and optional tags. |
| Tag | User-supplied snapshot metadata used to describe or select snapshots, such as class73-v1 or class73-v2. |
| Restore target | The directory beneath which Restic reconstructs paths stored in a snapshot. |
| Absolute snapshot path | A source path stored without its leading slash in the restore tree. For example, /opt/lab-classroom/class73/data is restored beneath a target as opt/lab-classroom/class73/data. |
| Deduplication | Reusing already stored content chunks instead of storing identical content again. |
| Retention policy | Rules that determine which snapshots should be kept or selected for removal. |
| Dry run | A preview that reports intended changes without applying them. |
| Staged restore | A restore into a temporary controlled location that is verified before it replaces or repairs the active source. |
| Recovery point objective | The maximum acceptable amount of data loss measured in time between recoverable backup points. |

## Instruction

A backup is useful only when its contents can be discovered, authenticated, restored, and compared with an expected state. Restic creates encrypted snapshots in a repository and uses content-defined chunking so unchanged data can be reused across snapshots. Deduplication reduces unnecessary duplicate storage, but it is not itself proof that a restore will work. The repository password is part of the recovery dependency: losing it makes the encrypted repository unusable, while exposing it allows anyone with repository access to decrypt the backups.

This lab deliberately backs up the absolute path /opt/lab-classroom/class73/data. Restic records that path in the snapshot. When the snapshot is restored with /opt/lab-classroom/class73/restore as the target, the source appears at /opt/lab-classroom/class73/restore/opt/lab-classroom/class73/data. It does not appear at /opt/lab-classroom/class73/restore/data. The lab therefore creates a source checksum manifest from inside the source directory, producing relative names such as alpha.txt. It then enters the actual restored data directory in a subshell and generates or checks the same relative names. The subshell prevents a directory change from leaking into later commands.

Verification has several layers. Snapshot JSON proves that both expected tags exist. Exact-content assertions provide an independent expectation for alpha.txt, beta.txt, and gamma.txt. A recursive file-list assertion detects missing or unexpected files. The normalized SHA-256 manifest detects byte-level differences between the source and restore. Finally, restic check --read-data reads repository data packs in addition to performing structural checks. A plain restic check is useful for repository structure and pack metadata or hash consistency, but it does not read every backed-up data blob. It must not be described as full verification of all backup data. Using --read-data is more thorough, although a real restore test remains essential because operational recovery includes path selection, credentials, permissions, and restore procedures.

Retention is separate from backup creation. The command restic forget --keep-last 1 --dry-run --json previews which snapshot would be removed while leaving the repository unchanged. The decisive evidence is a nonempty remove array in Restic's JSON output, followed by confirmation that the snapshot count remains unchanged. The Python program prints a sentence beginning with PASS only after inspecting that JSON. That PASS sentence is synthesized by the lesson's Python code; Restic itself does not print it. No prune or non-dry-run forget operation is performed in this lab.

The recovery workflow is intentionally fail-closed. A reset is first restored into reset-stage, and the staged absolute-path location is verified before the active source is moved. If restore or verification fails, the active source remains untouched. Clean reruns use a bounded quarantine under the class directory: the current repository and source are moved to repository.previous and data.previous, replacing only the corresponding older quarantine slots. All repository, cache, temporary, password, restore, evidence, and quarantine paths remain beneath /opt/lab-classroom/class73/.

## Architecture

### scope_boundary
/opt/lab-classroom/class73/

### components
### name
Source dataset

### path
/opt/lab-classroom/class73/data/

### role
Contains the live alpha.txt, beta.txt, and gamma.txt files captured by the second snapshot.
### name
Restic repository

### path
/opt/lab-classroom/class73/repository/

### role
Stores encrypted snapshot metadata, indexes, and deduplicated pack data.
### name
Credential file

### path
/opt/lab-classroom/class73/restic-password

### role
Supplies the local lab repository password through RESTIC_PASSWORD_FILE and is restricted to the current account.
### name
Restic cache and temporary workspace

### path
/opt/lab-classroom/class73/cache/ and /opt/lab-classroom/class73/tmp/

### role
Keeps Restic cache and temporary writes inside the permitted lab boundary.
### name
Restore target

### path
/opt/lab-classroom/class73/restore/

### role
Receives the latest class73-v2 snapshot.
### name
Actual restored dataset

### path
/opt/lab-classroom/class73/restore/opt/lab-classroom/class73/data/

### role
Represents the absolute source path reconstructed beneath the restore target.
### name
Reset staging target

### path
/opt/lab-classroom/class73/reset-stage/opt/lab-classroom/class73/data/

### role
Holds a recovery candidate that must pass checksum and content verification before replacing the source.
### name
Bounded quarantine

### path
/opt/lab-classroom/class73/quarantine/

### role
Retains at most one previous repository and one previous source dataset for reruns or immediate recovery.
### name
Evidence files

### path
/opt/lab-classroom/class73/source-v2.sha256, restored-v2.sha256, snapshots-before.json, snapshots-after.json, and retention-dry-run.json

### role
Records normalized checksums, snapshot metadata, and retention-preview evidence.

### data_flow
The source dataset is backed up to the encrypted local repository. The tagged class73-v2 snapshot is restored beneath the restore target, producing the absolute-path-derived subtree restore/opt/lab-classroom/class73/data. Verification normalizes both source and restored checksums to filenames relative to their respective data directories.

## Required reading

- Restic documentation: Preparing a new repository — https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html
- Restic documentation: Backing up — https://restic.readthedocs.io/en/stable/040_backup.html
- Restic documentation: Restoring from backup — https://restic.readthedocs.io/en/stable/050_restore.html
- Restic documentation: Checking integrity and consistency — https://restic.readthedocs.io/en/stable/045_working_with_repos.html#checking-integrity-and-consistency
- Restic documentation: Removing backup snapshots — https://restic.readthedocs.io/en/stable/060_forget.html

## References

- Restic documentation home — https://restic.readthedocs.io/en/stable/
- Restic: Preparing a new repository — https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html
- Restic: Backing up — https://restic.readthedocs.io/en/stable/040_backup.html
- Restic: Working with repositories — https://restic.readthedocs.io/en/stable/045_working_with_repos.html
- Restic: Restoring from backup — https://restic.readthedocs.io/en/stable/050_restore.html
- Restic: Removing backup snapshots — https://restic.readthedocs.io/en/stable/060_forget.html
- Restic command reference — https://restic.readthedocs.io/en/stable/075_scripting.html

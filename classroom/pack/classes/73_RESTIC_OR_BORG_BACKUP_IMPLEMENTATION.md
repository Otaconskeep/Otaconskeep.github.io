# Class 73: Restic or Borg Backup Implementation

**Learning objective:** Initialize and use a password-protected local Restic repository.; Explain how snapshots, content-addressed storage, encryption, deduplication, and retention differ.; Create tagged snapshots representing two versions of a source directory.; Recognize that Restic records an explicitly supplied absolute source path and recreates that path beneath a restore target.; Normalize source and restored paths so checksum comparisons evaluate the same relative filenames.; Verify snapshot tags, exact restored contents, file count, checksums, and repository data.; Interpret retention dry-run JSON and distinguish Restic output from locally synthesized PASS messages.; Reset the source from a verified staged restore without replacing the source before verification succeeds.
**Bloom level:** Understand / Apply
**Track:** Storage, Backup, and Disaster Recovery · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** medium
**Build output:** Implement a local Restic repository, create two encrypted snapshots, inspect snapshot metadata, restore the latest tagged snapshot, verify exact file contents and checksums at Restic's absolute-path restore location, test repository data integrity, and preview retention without deleting snapshots.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### platform
Linux with Bash and GNU coreutils

### restic
Designed for Restic releases that support JSON output for snapshots and forget, snapshot tags, restore tag selection, and check --read-data. Restic 0.14 or newer is recommended.

### python
Python 3.8 or newer

### filesystem
The account running the lab must be able to create, rename, and remove entries beneath /opt/lab-classroom/class73/.

### notes
The verification commands use GNU stat -c and GNU sha256sum. Systems using BSD utilities require equivalent syntax. Repository JSON formats should be checked against the installed Restic release before adapting the parsing logic for production automation.

## Learning objective

- Initialize and use a password-protected local Restic repository.
- Explain how snapshots, content-addressed storage, encryption, deduplication, and retention differ.
- Create tagged snapshots representing two versions of a source directory.
- Recognize that Restic records an explicitly supplied absolute source path and recreates that path beneath a restore target.
- Normalize source and restored paths so checksum comparisons evaluate the same relative filenames.
- Verify snapshot tags, exact restored contents, file count, checksums, and repository data.
- Interpret retention dry-run JSON and distinguish Restic output from locally synthesized PASS messages.
- Reset the source from a verified staged restore without replacing the source before verification succeeds.

## Why this matters

Implement a local Restic repository, create two encrypted snapshots, inspect snapshot metadata, restore the latest tagged snapshot, verify exact file contents and checksums at Restic's absolute-path restore location, test repository data integrity, and preview retention without deleting snapshots.

## Prerequisites

- A Linux host or Linux virtual machine with Bash.
- Restic, Python 3, GNU sha256sum, find, cmp, and chmod installed.
- Permission to create and modify files beneath /opt/lab-classroom/class73/.
- Basic familiarity with shell variables, files, directories, checksums, and backup terminology.
- Enough free local storage for two small snapshots, a restored copy, a Restic cache, and one bounded quarantine copy from a prior run.

## Required reading

- Restic documentation: Preparing a new repository — https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html
- Restic documentation: Backing up — https://restic.readthedocs.io/en/stable/040_backup.html
- Restic documentation: Restoring from backup — https://restic.readthedocs.io/en/stable/050_restore.html
- Restic documentation: Checking integrity and consistency — https://restic.readthedocs.io/en/stable/045_working_with_repos.html#checking-integrity-and-consistency
- Restic documentation: Removing backup snapshots — https://restic.readthedocs.io/en/stable/060_forget.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

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

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Within /opt/lab-classroom/class73/ only, create a fourth file named delta.txt, take a third snapshot tagged class73-v3, restore that tag to a new target named homework-restore, and verify the absolute-path-derived restore location. Create a normalized four-file manifest, assert exact contents, and preview --keep-last 2 with JSON.

### deliverables
A saved snapshots JSON file proving that class73-v3 exists.
A normalized source checksum manifest and matching restored checksum manifest.
An exact-content assertion for all four files.
Retention dry-run JSON with a nonempty remove array.
A short explanation of why the dry run does not alter the repository.

### constraint
Do not execute a non-dry-run forget or prune command as part of the homework.

## Feynman teach-back

### prompt
Explain the workflow to someone who believes that a successful backup command alone proves recoverability.

### target_explanation
Restic encrypts and stores snapshots, but success during upload does not prove that an operator can locate and restore the intended version. Because the lab backed up an absolute path, Restic rebuilds that path under the restore target. We therefore verify the real restored directory, compare normalized checksums, assert exact expected contents, and read repository data with restic check --read-data. Retention is tested separately with a dry run, and its remove array is evidence of what would be deleted. The source is replaced only after a staged restore passes verification.

### self_check_questions
Why is the restored dataset nested beneath restore/opt/lab-classroom/class73/data?
Why are checksum commands run from inside each data directory?
What does --read-data add to restic check?
Why does a dry-run remove array not mean a snapshot was actually deleted?
Why is the active source not moved until the staged restore passes all checks?

## Retrieval check

1. 1. Where will Restic place a backed-up absolute path of /opt/lab-classroom/class73/data when the restore target is /opt/lab-classroom/class73/restore?
2. 2. Why are source and restored checksum manifests generated from inside their respective data directories?
3. 3. What verification does restic check --read-data add beyond a plain restic check?
4. 4. What evidence demonstrates that the keep-last-one policy selected a snapshot for removal?
5. 5. Why do two snapshots still exist after the retention exercise?
6. 6. Why must the reset procedure verify reset-stage/opt/lab-classroom/class73/data before moving the active source?
7. 7. What are the exact expected contents of alpha.txt, beta.txt, and gamma.txt in class73-v2?

## Guided lab

### scope_rule
Every path created, changed, moved, or removed by these steps is beneath /opt/lab-classroom/class73/. RESTIC_CACHE_DIR and TMPDIR are explicitly redirected into that boundary.

### steps
1. Start a Bash shell and define the lab environment: BASE=/opt/lab-classroom/class73; test "$BASE" = /opt/lab-classroom/class73; mkdir -p "$BASE"; export RESTIC_REPOSITORY="$BASE/repository" RESTIC_PASSWORD_FILE="$BASE/restic-password" RESTIC_CACHE_DIR="$BASE/cache" TMPDIR="$BASE/tmp"; umask 077
2. Perform the bounded rerun preparation. This rotates an existing repository and source into one-slot quarantine locations and clears only generated working paths and evidence files: python3 - <<'PY'
from pathlib import Path
import shutil
base = Path('/opt/lab-classroom/class73')
assert base.resolve() == Path('/opt/lab-classroom/class73')
q = base / 'quarantine'
q.mkdir(parents=True, exist_ok=True)
def clear_path(path):
    assert path == base / path.name or path.parent == q
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)
for name in ('repository', 'data'):
    src = base / name
    dst = q / (name + '.previous')
    clear_path(dst)
    if src.exists() or src.is_symlink():
        src.rename(dst)
for name in ('restore', 'reset-stage', 'cache', 'tmp'):
    clear_path(base / name)
for name in ('source-v2.sha256', 'restored-v2.sha256', 'snapshots-before.json', 'snapshots-after.json', 'retention-dry-run.json'):
    p = base / name
    if p.is_symlink() or p.is_file():
        p.unlink()
(base / 'data').mkdir()
(base / 'cache').mkdir()
(base / 'tmp').mkdir()
PY
3. Create the local lab credential file and initialize the repository: printf '%s\n' 'class73-local-lab-password' > "$RESTIC_PASSWORD_FILE"; chmod 600 "$RESTIC_PASSWORD_FILE"; restic init
4. Create version 1 of the source dataset: printf 'alpha version 1\n' > "$BASE/data/alpha.txt"; printf 'beta stable\n' > "$BASE/data/beta.txt"
5. Back up the explicit absolute source path with the first tag: restic backup "$BASE/data" --tag class73-v1
6. Create version 2 by revising alpha, retaining beta, and adding gamma: printf 'alpha version 2\n' > "$BASE/data/alpha.txt"; printf 'gamma added in version 2\n' > "$BASE/data/gamma.txt"
7. Create a normalized checksum manifest whose entries are relative to the source data directory: (cd "$BASE/data" && sha256sum alpha.txt beta.txt gamma.txt) > "$BASE/source-v2.sha256"
8. Back up version 2 with a distinct tag: restic backup "$BASE/data" --tag class73-v2
9. Capture snapshot JSON and assert that exactly two snapshots exist and both required tags are present: restic snapshots --json > "$BASE/snapshots-before.json"; python3 - <<'PY'
import json
from pathlib import Path
p = Path('/opt/lab-classroom/class73/snapshots-before.json')
snapshots = json.loads(p.read_text())
assert isinstance(snapshots, list), 'Expected a JSON snapshot list'
assert len(snapshots) == 2, f'Expected 2 snapshots, found {len(snapshots)}'
tags = {tag for snap in snapshots for tag in (snap.get('tags') or [])}
assert {'class73-v1', 'class73-v2'} <= tags, f'Missing required tags; found {sorted(tags)}'
print('PASS: two snapshots and both required tags are present')
PY
10. Restore the latest snapshot carrying the class73-v2 tag: restic restore latest --tag class73-v2 --target "$BASE/restore"
11. Set and validate the actual restored data path produced from the absolute source path: RESTORED_DATA="$BASE/restore/opt/lab-classroom/class73/data"; test -d "$RESTORED_DATA"; test ! -e "$BASE/restore/data"
12. Assert the exact restored file list and contents: python3 - <<'PY'
from pathlib import Path
root = Path('/opt/lab-classroom/class73/restore/opt/lab-classroom/class73/data')
expected = {
    'alpha.txt': 'alpha version 2\n',
    'beta.txt': 'beta stable\n',
    'gamma.txt': 'gamma added in version 2\n'
}
actual_names = sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file())
assert actual_names == sorted(expected), f'Unexpected file list: {actual_names}'
for name, content in expected.items():
    actual = (root / name).read_text()
    assert actual == content, f'Content mismatch for {name}: {actual!r}'
print('PASS: restored file names and contents match version 2')
PY
13. Generate the restored checksum manifest using the same relative filenames as the source manifest, compare the manifests, and independently check each restored file: (cd "$RESTORED_DATA" && sha256sum alpha.txt beta.txt gamma.txt) > "$BASE/restored-v2.sha256"; cmp "$BASE/source-v2.sha256" "$BASE/restored-v2.sha256"; (cd "$RESTORED_DATA" && sha256sum -c "$BASE/source-v2.sha256")
14. Read and validate all repository data packs in addition to repository structure: restic check --read-data
15. Preview a keep-last-one retention policy without changing the repository: restic forget --keep-last 1 --dry-run --json > "$BASE/retention-dry-run.json"
16. Prove from Restic's JSON that the dry run selected at least one snapshot for removal. The PASS line is printed by Python, not by Restic: python3 - <<'PY'
import json
from pathlib import Path
doc = json.loads(Path('/opt/lab-classroom/class73/retention-dry-run.json').read_text())
groups = doc if isinstance(doc, list) else [doc]
removed = []
for group in groups:
    if isinstance(group, dict) and isinstance(group.get('remove'), list):
        removed.extend(group['remove'])
assert removed, 'Retention JSON did not contain a nonempty remove array'
print(f'PASS: Python found {len(removed)} snapshot selection(s) in Restic JSON remove arrays')
PY
17. Confirm that dry-run retention changed nothing: restic snapshots --json > "$BASE/snapshots-after.json"; python3 - <<'PY'
import json
from pathlib import Path
base = Path('/opt/lab-classroom/class73')
before = json.loads((base / 'snapshots-before.json').read_text())
after = json.loads((base / 'snapshots-after.json').read_text())
assert len(before) == 2 and len(after) == 2, f'Unexpected counts: before={len(before)}, after={len(after)}'
assert {s['id'] for s in before} == {s['id'] for s in after}, 'Snapshot IDs changed during dry run'
print('PASS: retention dry run left both snapshot IDs unchanged')
PY

## Expected results

- The repository is initialized at /opt/lab-classroom/class73/repository/ and can be opened using /opt/lab-classroom/class73/restic-password.
- Exactly two snapshots exist after the backup steps, with class73-v1 and class73-v2 represented in their tags.
- The second snapshot contains alpha.txt with alpha version 2, beta.txt with beta stable, and gamma.txt with gamma added in version 2.
- Restoring class73-v2 to /opt/lab-classroom/class73/restore reconstructs the source at /opt/lab-classroom/class73/restore/opt/lab-classroom/class73/data/.
- The incorrect flattened path /opt/lab-classroom/class73/restore/data does not exist.
- The source and restored checksum manifests contain the same three relative filenames and identical SHA-256 values.
- The independent sha256sum check reports alpha.txt: OK, beta.txt: OK, and gamma.txt: OK from inside the actual restored data directory.
- restic check --read-data completes successfully after reading repository data.
- The retention dry-run JSON contains a nonempty remove array because keep-last 1 is evaluated against two snapshots in the same default policy group.
- The repository still contains the same two snapshot IDs after the retention dry run.

## Verification checkpoints

- [ ] Confirm the credential mode is restricted: test "$(stat -c '%a' /opt/lab-classroom/class73/restic-password)" = 600
- [ ] Confirm the required tags from saved Restic JSON: python3 -c "import json; p='/opt/lab-classroom/class73/snapshots-before.json'; s=json.load(open(p)); t={x for y in s for x in (y.get('tags') or [])}; assert len(s)==2 and {'class73-v1','class73-v2'}<=t"
- [ ] Confirm the absolute-path restore location: test -d /opt/lab-classroom/class73/restore/opt/lab-classroom/class73/data && test ! -e /opt/lab-classroom/class73/restore/data
- [ ] Confirm exactly the three expected relative files: python3 -c "from pathlib import Path; r=Path('/opt/lab-classroom/class73/restore/opt/lab-classroom/class73/data'); assert sorted(str(p.relative_to(r)) for p in r.rglob('*') if p.is_file())==['alpha.txt','beta.txt','gamma.txt']"
- [ ] Confirm exact version 2 contents: python3 -c "from pathlib import Path; r=Path('/opt/lab-classroom/class73/restore/opt/lab-classroom/class73/data'); e={'alpha.txt':'alpha version 2\n','beta.txt':'beta stable\n','gamma.txt':'gamma added in version 2\n'}; assert all((r/k).read_text()==v for k,v in e.items())"
- [ ] Compare normalized source and restore manifests: cmp /opt/lab-classroom/class73/source-v2.sha256 /opt/lab-classroom/class73/restored-v2.sha256
- [ ] Check the restored bytes against the source manifest in a subshell: (cd /opt/lab-classroom/class73/restore/opt/lab-classroom/class73/data && sha256sum -c /opt/lab-classroom/class73/source-v2.sha256)
- [ ] Perform repository-wide data reading rather than only a structural check: BASE=/opt/lab-classroom/class73 RESTIC_REPOSITORY=/opt/lab-classroom/class73/repository RESTIC_PASSWORD_FILE=/opt/lab-classroom/class73/restic-password RESTIC_CACHE_DIR=/opt/lab-classroom/class73/cache TMPDIR=/opt/lab-classroom/class73/tmp restic check --read-data
- [ ] Confirm real retention evidence exists in Restic's JSON: python3 -c "import json; d=json.load(open('/opt/lab-classroom/class73/retention-dry-run.json')); g=d if isinstance(d,list) else [d]; assert any(isinstance(x,dict) and x.get('remove') for x in g)"
- [ ] Confirm dry-run retention did not change snapshot identities: python3 -c "import json; b=json.load(open('/opt/lab-classroom/class73/snapshots-before.json')); a=json.load(open('/opt/lab-classroom/class73/snapshots-after.json')); assert len(b)==len(a)==2 and {x['id'] for x in b}=={x['id'] for x in a}"

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Restic reports that no repository exists. | RESTIC_REPOSITORY is unset, points to the wrong path, or the initialization step did not complete. | Export RESTIC_REPOSITORY=/opt/lab-classroom/class73/repository and rerun restic init only if the intended repository is absent. |
| Restic reports an incorrect password or cannot decrypt repository data. | RESTIC_PASSWORD_FILE points to a different file, the password file was changed after initialization, or a quarantined repository is being paired with a new password. | Verify RESTIC_PASSWORD_FILE=/opt/lab-classroom/class73/restic-password. If recovering repository.previous, pair it with the password that initialized that repository. |
| The restored files are not present in restore/data. | The absolute source path was reconstructed beneath the restore target. | Use /opt/lab-classroom/class73/restore/opt/lab-classroom/class73/data as the restored dataset path. |
| cmp reports that the source and restored checksum manifests differ even though the files appear correct. | One manifest was generated with prefixed paths while the other used bare filenames, or the file order differed. | Generate both manifests from inside their respective data directories and list alpha.txt, beta.txt, and gamma.txt in the same explicit order. |
| sha256sum reports that files cannot be found. | The check was executed outside the restored data directory while the manifest contains relative filenames. | Run the check in a subshell: (cd "$RESTORED_DATA" && sha256sum -c "$BASE/source-v2.sha256"). |
| The tag assertion finds more than two snapshots. | An older repository was reused instead of being rotated into the bounded quarantine. | Repeat the bounded rerun preparation, confirm repository.previous exists when appropriate, initialize a fresh repository, and rerun the two backups. |
| The retention JSON has no remove entries. | Only one snapshot exists, snapshots were separated into different policy groups, or a different forget command was used. | Confirm that two snapshots of the same absolute source path and host exist, then run restic forget --keep-last 1 --dry-run --json exactly as shown. |
| restic check succeeds quickly but no repository data appears to have been read. | The command was run without --read-data. | Run restic check --read-data. A plain check is not equivalent to reading every data pack. |
| The reset procedure cannot find reset-stage/data. | The reset procedure is looking at a flattened restore location. | Use /opt/lab-classroom/class73/reset-stage/opt/lab-classroom/class73/data. |

## Security considerations

### controls
The repository is encrypted by Restic, but repository availability and password availability remain separate recovery dependencies.
The password file is created with restrictive process umask and explicitly set to mode 600.
RESTIC_CACHE_DIR and TMPDIR keep application-generated writes inside the authorized lab tree.
The lab uses a local repository so no network credentials, remote trust configuration, or external endpoints are required.
Restore data is treated as untrusted until exact filenames, exact contents, and checksums have been verified.
The source reset stages and verifies data before moving the active source, preventing an unverified restore from immediately replacing it.
Retention is previewed with --dry-run. This lesson intentionally does not run a destructive forget or prune operation.
The quarantine is bounded to one previous repository and one previous source, preventing unlimited accumulation across reruns.

### production_considerations
Do not reuse the classroom password in production.
Store repository credentials in a secret manager or protected root-readable file and test credential recovery.
Keep at least one backup copy outside the failure domain of the source host.
Apply immutable or append-only protections where supported and test their interaction with retention.
Schedule automated backups, alert on failures, and conduct periodic restore exercises.
Define retention from business recovery requirements rather than copying the lab's keep-last-one example.
Treat successful backup commands as incomplete evidence until restore tests and repository checks also succeed.

## Rollback

### reset_source_to_verified_latest_snapshot
Use the following fail-closed procedure. It clears only the prior reset stage, restores class73-v2, verifies the staged absolute-path dataset, then moves the current source into a one-slot quarantine before installing the verified stage:
BASE=/opt/lab-classroom/class73
export RESTIC_REPOSITORY="$BASE/repository" RESTIC_PASSWORD_FILE="$BASE/restic-password" RESTIC_CACHE_DIR="$BASE/cache" TMPDIR="$BASE/tmp"
python3 - <<'PY'
from pathlib import Path
import shutil
p = Path('/opt/lab-classroom/class73/reset-stage')
assert p.parent == Path('/opt/lab-classroom/class73')
if p.is_symlink() or p.is_file():
    p.unlink()
elif p.exists():
    shutil.rmtree(p)
PY
restic restore latest --tag class73-v2 --target "$BASE/reset-stage"
STAGED_DATA="$BASE/reset-stage/opt/lab-classroom/class73/data"
test -d "$STAGED_DATA"
(cd "$STAGED_DATA" && sha256sum -c "$BASE/source-v2.sha256")
python3 - <<'PY'
from pathlib import Path
import shutil
base = Path('/opt/lab-classroom/class73')
staged = base / 'reset-stage/opt/lab-classroom/class73/data'
source = base / 'data'
quarantine = base / 'quarantine/source.previous'
expected = {
    'alpha.txt': 'alpha version 2\n',
    'beta.txt': 'beta stable\n',
    'gamma.txt': 'gamma added in version 2\n'
}
assert staged.is_dir()
files = sorted(str(p.relative_to(staged)) for p in staged.rglob('*') if p.is_file())
assert files == sorted(expected)
for name, content in expected.items():
    assert (staged / name).read_text() == content
quarantine.parent.mkdir(parents=True, exist_ok=True)
if quarantine.is_symlink() or quarantine.is_file():
    quarantine.unlink()
elif quarantine.exists():
    shutil.rmtree(quarantine)
if source.exists() or source.is_symlink():
    source.rename(quarantine)
staged.rename(source)
print('PASS: verified staged data installed; former source is quarantined')
PY

### clean_rerun_with_bounded_repository_quarantine
Run the lab's bounded rerun preparation. It replaces only quarantine/repository.previous and quarantine/data.previous, moves the current repository and source into those slots, and then permits creation of a fresh repository and dataset. No operator cleanup is required, but the prior contents of those two older quarantine slots are intentionally discarded.

### failure_behavior
If repository access, restore, checksum validation, file-list validation, or exact-content validation fails before the final Python replacement block, the active source remains unchanged. If replacement fails after the active source has been renamed, recover it by renaming /opt/lab-classroom/class73/quarantine/source.previous back to /opt/lab-classroom/class73/data after confirming the destination is absent.

## Video narration notes

Begin by identifying the single allowed mutation boundary: /opt/lab-classroom/class73. Restic's repository, password file, cache, temporary workspace, restore targets, evidence, and quarantine all remain below it. The rerun preparation rotates an existing repository and source into bounded one-slot quarantine paths, allowing a predictable clean repository without requiring manual cleanup.

Create version 1 with alpha and beta, then back up the explicit absolute path using the class73-v1 tag. Revise alpha, retain beta, add gamma, and capture class73-v2. Snapshot JSON proves that exactly two snapshots exist and that both tags are present.

The key path lesson appears during restore. The target is the restore directory, but the data is not restored directly as restore/data. Since the snapshot records /opt/lab-classroom/class73/data, the restored files appear under restore/opt/lab-classroom/class73/data. Verification must use that complete location.

The source manifest is generated from inside the source data directory, while the restored manifest is generated from inside the actual restored data directory. Both therefore contain alpha.txt, beta.txt, and gamma.txt as the same relative names. Their manifests can be compared directly, and sha256sum can check the restored files from a subshell without changing the caller's working directory. Separate assertions verify the exact filenames and revised version 2 contents.

Next, restic check --read-data reads repository data packs. A plain check is not described as full reading of all backup data. Finally, forget with --dry-run and JSON previews keep-last-one. The nonempty remove array is Restic's actual retention evidence. The readable PASS statement comes from Python after parsing that evidence; it is not Restic output. A final comparison confirms that both snapshot IDs remain because the policy was only previewed.

## References

- Restic documentation home — https://restic.readthedocs.io/en/stable/
- Restic: Preparing a new repository — https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html
- Restic: Backing up — https://restic.readthedocs.io/en/stable/040_backup.html
- Restic: Working with repositories — https://restic.readthedocs.io/en/stable/045_working_with_repos.html
- Restic: Restoring from backup — https://restic.readthedocs.io/en/stable/050_restore.html
- Restic: Removing backup snapshots — https://restic.readthedocs.io/en/stable/060_forget.html
- Restic command reference — https://restic.readthedocs.io/en/stable/075_scripting.html

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

# Lab: Restic or Borg Backup Implementation

**Module:** Segmentation, Backup & Power
**Activity type:** Lab (Practice)
**Lab risk:** medium
**Objective:** Initialize and use a password-protected local Restic repository.

## Before you start

- A Linux host or Linux virtual machine with Bash.
- Restic, Python 3, GNU sha256sum, find, cmp, and chmod installed.
- Permission to create and modify files beneath /opt/lab-classroom/class73/.
- Basic familiarity with shell variables, files, directories, checksums, and backup terminology.
- Enough free local storage for two small snapshots, a restored copy, a Restic cache, and one bounded quarantine copy from a prior run.

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

## Verification

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

## Security

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

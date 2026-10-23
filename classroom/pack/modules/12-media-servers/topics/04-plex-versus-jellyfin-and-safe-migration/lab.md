# Lab: Plex versus Jellyfin and Safe Migration

**Module:** Requests & Media Servers
**Activity type:** Lab (Practice)
**Lab risk:** medium
**Objective:** Compare Plex and Jellyfin across licensing, account dependencies, remote access, plug-ins, client coverage, administration, and migration implications.

## Before you start

- Comfort using a Linux shell and reading command exit statuses.
- A Linux host or virtual machine with Bash, GNU coreutils, GNU findutils, tar, gzip, awk, Python 3, and runuser.
- A root shell is required for the controlled runuser permission test and for creating the isolated workspace under /opt.
- At least 20 MiB of free space under /opt.
- No existing data at /opt/lab-classroom/class59; preserve or relocate any pre-existing directory before beginning.

## Guided lab

### scope_rule
Every command that writes data is constrained to /opt/lab-classroom/class59/. Do not substitute production Plex, Jellyfin, or media paths.

### shell_requirement
Run each command block in the same root Bash session. Stop immediately if a command returns an unexpected nonzero status.

### steps
### step
1

### title
Preflight the isolated workspace

### explanation
Confirm root access, required tools, and the absence of an existing class directory. The test against ROOT prevents accidental reuse or overwrite.

### commands
set -euo pipefail
ROOT=/opt/lab-classroom/class59
test "$(id -u)" -eq 0
for tool in install find sort xargs sha256sum tar awk python3 runuser stat cmp grep; do command -v "$tool" >/dev/null; done
test ! -e "$ROOT"
printf 'Preflight passed for %s\n' "$ROOT"
### step
2

### title
Create separated media, state, backup, report, and cutover areas

### explanation
install -d creates directories. The -m option applies an explicit octal mode: 0755 permits traversal of the lab and media path, while 0750 restricts mutable state and reports to the owner and group.

### commands
umask 027
install -d -m 0755 "$ROOT" "$ROOT/media" "$ROOT/media/library"
install -d -m 0750 "$ROOT/state" "$ROOT/state/plex" "$ROOT/state/plex/config" "$ROOT/state/plex/metadata" "$ROOT/backups" "$ROOT/manifests" "$ROOT/reports" "$ROOT/cutover"
### step
3

### title
Create source fixtures and a read-only media fixture

### explanation
The fixture represents only migration mechanics. The media file contains text rather than copyrighted media. The final mode 0444 denies file writes, and directory mode 0555 denies creation, deletion, or renaming by an unprivileged service identity.

### commands
cat > "$ROOT/state/plex/config/Preferences.xml" <<'EOF'
<Preferences serverName="Class59-Plex" libraryPath="/opt/lab-classroom/class59/media/library" remoteAccess="disabled" />
EOF
printf 'user\titem\tposition_seconds\tplayed\nlocal-alex\tdemo-item\t120\t0\n' > "$ROOT/state/plex/metadata/watch-state.tsv"
printf 'CLASS59 MEDIA FIXTURE\n' > "$ROOT/media/library/demo-media.txt"
chmod 0444 "$ROOT/media/library/demo-media.txt"
chmod 0555 "$ROOT/media/library"
printf 'plex\n' > "$ROOT/cutover/active-service"
cp "$ROOT/cutover/active-service" "$ROOT/cutover/active-service.before"
chmod 0444 "$ROOT/cutover/active-service.before"
### step
4

### title
Prove least-privilege media behavior

### explanation
runuser executes the read and write attempts as the existing unprivileged nobody identity. A successful read and denied append prove behavior rather than merely recording a policy string. The append test is expected to fail.

### commands
runuser -u nobody -- cat "$ROOT/media/library/demo-media.txt" > /dev/null
if runuser -u nobody -- sh -c 'printf "unauthorized-change\n" >> "$1"' sh "$ROOT/media/library/demo-media.txt" 2> "$ROOT/reports/media-write-denied.txt"; then
  printf 'ERROR: unprivileged media write unexpectedly succeeded\n' >&2
  exit 1
else
  printf 'PASS: nobody can read media but cannot append to it\n' | tee "$ROOT/reports/media-permission-result.txt"
fi
test "$(stat -c '%a' "$ROOT/media/library/demo-media.txt")" = 444
test "$(stat -c '%a' "$ROOT/media/library")" = 555
### step
5

### title
Create the source checksum manifest and backup archive

### explanation
find -type f selects regular files. -print0, sort -z, and xargs -0 preserve filenames safely by using NUL delimiters. sha256sum records each file hash. tar -C archives the plex directory using a controlled relative path; -c creates, -z compresses with gzip, and -f selects the output file.

### commands
(cd "$ROOT/state" && find plex -type f -print0 | sort -z | xargs -0 sha256sum) > "$ROOT/manifests/plex.before.sha256"
(cd "$ROOT/state" && sha256sum -c "$ROOT/manifests/plex.before.sha256") | tee "$ROOT/reports/plex-source-check.txt"
tar -C "$ROOT/state" -czf "$ROOT/backups/plex-pre-migration.tgz" plex
tar -tzf "$ROOT/backups/plex-pre-migration.tgz" | tee "$ROOT/reports/backup-members.txt"
grep -Fx 'plex/config/Preferences.xml' "$ROOT/reports/backup-members.txt"
grep -Fx 'plex/metadata/watch-state.tsv' "$ROOT/reports/backup-members.txt"
### step
6

### title
Extract and verify the recovery archive before cutover

### explanation
The archive is extracted into an empty isolated directory, not over the source. tar -x extracts, -z handles gzip, -f identifies the archive, and -C chooses the destination. sha256sum -c then proves the extracted files match the pre-migration manifest.

### commands
install -d -m 0750 "$ROOT/restore-check"
tar -xzf "$ROOT/backups/plex-pre-migration.tgz" -C "$ROOT/restore-check"
(cd "$ROOT/restore-check" && sha256sum -c "$ROOT/manifests/plex.before.sha256") | tee "$ROOT/reports/restore-check.txt"
python3 - "$ROOT/restore-check/plex/config/Preferences.xml" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
assert root.tag == "Preferences"
assert root.attrib["serverName"] == "Class59-Plex"
assert root.attrib["libraryPath"] == "/opt/lab-classroom/class59/media/library"
PY
### step
7

### title
Prepare and validate the Jellyfin candidate

### explanation
The candidate receives a separate configuration and an explicit user mapping. The sample watch-state row is transformed into a candidate TSV. This demonstrates a mapping workflow; it does not imply that production Plex databases can be copied directly into Jellyfin.

### commands
install -d -m 0750 "$ROOT/state/jellyfin" "$ROOT/state/jellyfin/config" "$ROOT/state/jellyfin/data"
cat > "$ROOT/state/jellyfin/config/system.xml" <<'EOF'
<SystemConfiguration>
  <ServerName>Class59-Jellyfin</ServerName>
  <MediaPath>/opt/lab-classroom/class59/media/library</MediaPath>
  <RemoteAccess>false</RemoteAccess>
</SystemConfiguration>
EOF
printf 'source_user\ttarget_user\nlocal-alex\nalex\n' > "$ROOT/state/jellyfin/data/user-map.tsv"
awk -F '\t' 'BEGIN { OFS="\t" } NR==1 { print "target_user",$2,$3,$4; next } $1=="local-alex" { print "alex",$2,$3,$4 }' "$ROOT/state/plex/metadata/watch-state.tsv" > "$ROOT/state/jellyfin/data/watch-state.tsv"
python3 - "$ROOT/state/jellyfin/config/system.xml" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
assert root.tag == "SystemConfiguration"
assert root.findtext("ServerName") == "Class59-Jellyfin"
assert root.findtext("MediaPath") == "/opt/lab-classroom/class59/media/library"
assert root.findtext("RemoteAccess") == "false"
PY
grep -Fx $'alex\tdemo-item\t120\t0' "$ROOT/state/jellyfin/data/watch-state.tsv"
(cd "$ROOT/state" && find jellyfin -type f -print0 | sort -z | xargs -0 sha256sum) > "$ROOT/manifests/jellyfin.candidate.sha256"
(cd "$ROOT/state" && sha256sum -c "$ROOT/manifests/jellyfin.candidate.sha256") | tee "$ROOT/reports/jellyfin-candidate-check.txt"
### step
8

### title
Perform the simulated cutover

### explanation
The marker changes only after source backup, extraction, source validation, candidate validation, and media-permission testing have passed.

### commands
test "$(cat "$ROOT/cutover/active-service.before")" = plex
printf 'jellyfin\n' > "$ROOT/cutover/active-service"
test "$(cat "$ROOT/cutover/active-service")" = jellyfin
printf 'Simulated cutover selected Jellyfin\n' | tee "$ROOT/reports/cutover-result.txt"
### step
9

### title
Introduce source-state damage and execute rollback

### explanation
Appending a line makes the current Plex checksum fail, providing a real recovery condition. Rollback preserves the failed directory with a fixed lab-only name, promotes the already verified extraction, and restores the active marker to Plex.

### commands
printf 'intentional-lab-damage\n' >> "$ROOT/state/plex/config/Preferences.xml"
if (cd "$ROOT/state" && sha256sum -c "$ROOT/manifests/plex.before.sha256") > "$ROOT/reports/expected-damage-check.txt" 2>&1; then
  printf 'ERROR: intentional damage was not detected\n' >&2
  exit 1
fi
test ! -e "$ROOT/state/plex.failed-after-cutover"
mv "$ROOT/state/plex" "$ROOT/state/plex.failed-after-cutover"
mv "$ROOT/restore-check/plex" "$ROOT/state/plex"
printf 'plex\n' > "$ROOT/cutover/active-service"
### step
10

### title
Verify rollback and independently extract the backup again

### explanation
These checks prove that the historical before marker still names Plex, the active marker again names Plex, both manifests still validate, and the archive remains independently extractable after rollback.

### commands
test "$(cat "$ROOT/cutover/active-service.before")" = plex
test "$(cat "$ROOT/cutover/active-service")" = plex
(cd "$ROOT/state" && sha256sum -c "$ROOT/manifests/plex.before.sha256") | tee "$ROOT/reports/plex-after-rollback-check.txt"
(cd "$ROOT/state" && sha256sum -c "$ROOT/manifests/jellyfin.candidate.sha256") | tee "$ROOT/reports/jellyfin-after-rollback-check.txt"
install -d -m 0750 "$ROOT/verification-extract"
tar -xzf "$ROOT/backups/plex-pre-migration.tgz" -C "$ROOT/verification-extract"
(cd "$ROOT/verification-extract" && sha256sum -c "$ROOT/manifests/plex.before.sha256") | tee "$ROOT/reports/backup-post-rollback-extract-check.txt"
cmp "$ROOT/state/plex/config/Preferences.xml" "$ROOT/verification-extract/plex/config/Preferences.xml"
test -d "$ROOT/state/plex.failed-after-cutover"
grep -F 'intentional-lab-damage' "$ROOT/state/plex.failed-after-cutover/config/Preferences.xml"
printf 'CLASS59 COMPLETE: rollback and independent recovery verification passed\n' | tee "$ROOT/reports/final-status.txt"

## Expected results

- The only created or modified paths are beneath /opt/lab-classroom/class59/.
- The nobody service identity can read demo-media.txt but cannot append to it.
- The media fixture has mode 0444 and its containing library directory has mode 0555.
- The Plex source manifest validates before migration.
- The Plex backup archive contains the expected configuration and watch-state fixtures.
- The backup is extracted into restore-check and its files validate against plex.before.sha256 before cutover.
- The Jellyfin candidate contains a distinct XML configuration, explicit user mapping, and translated sample watch-state row.
- The simulated cutover changes active-service from plex to jellyfin.
- Intentional post-cutover damage causes Plex manifest verification to fail as expected.
- Rollback preserves the damaged Plex directory, promotes the verified restore, and returns active-service to plex.
- Both Plex and Jellyfin manifests validate after rollback.
- A fresh post-rollback extraction of the backup validates successfully.

## Verification

- [ ] Run: test "$(cat /opt/lab-classroom/class59/cutover/active-service.before)" = plex
- [ ] Run: test "$(cat /opt/lab-classroom/class59/cutover/active-service)" = plex
- [ ] Run: cd /opt/lab-classroom/class59/state && sha256sum -c /opt/lab-classroom/class59/manifests/plex.before.sha256
- [ ] Run: cd /opt/lab-classroom/class59/state && sha256sum -c /opt/lab-classroom/class59/manifests/jellyfin.candidate.sha256
- [ ] Run: cd /opt/lab-classroom/class59/verification-extract && sha256sum -c /opt/lab-classroom/class59/manifests/plex.before.sha256
- [ ] Run: cmp /opt/lab-classroom/class59/state/plex/config/Preferences.xml /opt/lab-classroom/class59/verification-extract/plex/config/Preferences.xml
- [ ] Run: test "$(stat -c '%a' /opt/lab-classroom/class59/media/library/demo-media.txt)" = 444
- [ ] Run: test "$(stat -c '%a' /opt/lab-classroom/class59/media/library)" = 555
- [ ] Run: test -s /opt/lab-classroom/class59/reports/media-write-denied.txt
- [ ] Run: test -d /opt/lab-classroom/class59/state/plex.failed-after-cutover
- [ ] Run: grep -F 'intentional-lab-damage' /opt/lab-classroom/class59/state/plex.failed-after-cutover/config/Preferences.xml
- [ ] Run: grep -Fx 'CLASS59 COMPLETE: rollback and independent recovery verification passed' /opt/lab-classroom/class59/reports/final-status.txt

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Preflight fails because /opt/lab-classroom/class59 already exists. | A prior attempt or unrelated data occupies the required isolated path. | Do not overwrite it. Inspect and preserve it outside this lesson, then begin only when /opt/lab-classroom/class59 does not exist. |
| runuser reports that only root may specify a user. | The lab is not running in a root shell. | Restart the lab in a root Bash session. Do not replace the permission test with a text declaration because that would not prove least privilege. |
| The nobody read test returns permission denied. | A parent directory lacks execute permission for other users, or local mandatory access controls deny traversal. | Confirm that the class59, media, and media/library directories have the lesson modes and inspect local access-control logs. Keep all changes confined to the class59 workspace. |
| The nobody append unexpectedly succeeds. | The file or directory permissions differ from 0444 and 0555, or the test did not run as nobody. | Check id output inside runuser, inspect modes with stat, reapply the lesson modes, and repeat both the read and denied-write tests. |
| sha256sum -c reports a missing Plex file during restore validation. | The archive was incomplete, extracted into the wrong directory, or the manifest was generated from a different state. | Stop before cutover. List the archive with tar -tzf, confirm it contains paths beginning with plex/, and recreate the archive only from the validated source state. |
| A checksum fails immediately after manifest creation. | A file changed between manifest generation and verification, or the command was run from the wrong working directory. | Quiesce writers, run the check from /opt/lab-classroom/class59/state, and regenerate the manifest only after confirming the source is stable. |
| The expected damage check succeeds instead of failing. | The modified file was not included in the manifest or the append command targeted another path. | Confirm that plex/config/Preferences.xml appears in plex.before.sha256 and that the command uses the exact ROOT value. |
| The second archive extraction fails because verification-extract is not empty. | The step was already run in the same workspace. | Do not merge repeated extraction output. Preserve the current workspace for review and repeat the complete lab in a newly prepared class59 workspace. |
| The awk output lacks the alex watch-state row. | The source fixture delimiter or username was altered. | Inspect the source TSV with a tool that exposes tab characters and confirm the source identity is local-alex before rerunning the transformation. |
| Commands such as sort -z, stat -c, or find -print0 are unsupported. | The host uses non-GNU or reduced userland utilities. | Use the stated GNU-compatible Linux environment. Do not improvise filename-unsafe pipelines for production migrations. |

## Security

### principles
Keep media content separate from server databases and configuration so application recovery does not rewrite the media library.
Grant media-server identities read-only access when the server does not need to rename, delete, or create media.
Treat metadata agents, plug-ins, and migration tools as code with access to sensitive filenames, viewing history, account data, and credentials.
Do not assume Plex users, Jellyfin users, passwords, tokens, shares, or authorization rules are equivalent.
Disable or tightly control remote exposure until authentication, TLS, client behavior, logs, and recovery procedures have been validated.
Quiesce production database writes before file-level backup unless the product documentation explicitly supports live snapshots.
Protect backups because they may contain tokens, account records, library paths, viewing history, and identifying metadata.
Retain the failed state during rollback for investigation rather than immediately destroying evidence.
Validate archive contents before extraction, and extract untrusted archives only into an isolated destination with appropriate tooling.
Use supported export, API, or migration tools for real watch-state transfer; never insert guessed records directly into a production database.

### lab_boundary
The lesson does not expose network services, install plug-ins, alter host accounts, or access real media-server directories. Its unprivileged identity test reads one fixture and performs one intentionally denied append attempt.

## Rollback

### trigger_conditions
The candidate cannot read required media.
A required client, codec, subtitle workflow, or accessibility feature fails acceptance testing.
Users or permissions are mapped incorrectly.
Backup extraction or checksum validation fails.
Unexpected writes occur in the media library.
The replacement service exposes an unapproved remote-access path.

### procedure
Stop client cutover and prevent additional writes to the candidate.
Preserve the failed source or candidate state under a distinct name inside the controlled recovery area.
Promote only the Plex state that was extracted and checksum-verified before cutover.
Restore service selection to Plex.
Verify that active-service.before still records plex and active-service currently records plex.
Verify the Plex manifest from the restored state.
Verify the retained Jellyfin candidate manifest so rollback does not conceal unrelated candidate changes.
Extract the backup again into a new empty directory and verify it independently.
Document the failure and do not retry until its cause and acceptance criteria are understood.

### lab_result
The damaged Plex fixture remains at /opt/lab-classroom/class59/state/plex.failed-after-cutover, while the verified Plex copy is restored to /opt/lab-classroom/class59/state/plex.

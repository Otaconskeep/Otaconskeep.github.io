# Class 59: Plex versus Jellyfin and Safe Migration

**Learning objective:** Compare Plex and Jellyfin across licensing, account dependencies, remote access, plug-ins, client coverage, administration, and migration implications.; Separate immutable media content from mutable application configuration, metadata, accounts, and watch-state data.; Create a checksum manifest and compressed pre-migration archive of Plex application state.; Extract and verify the archive before declaring it usable for recovery.; Apply and test read-only media permissions using an unprivileged service identity.; Translate a small fixture data set into a Jellyfin candidate without claiming that real Plex databases are directly interchangeable.; Perform a simulated cutover and a rollback while preserving failed state for investigation.; Verify the active-service markers and both Plex and Jellyfin manifests after rollback.
**Bloom level:** Understand / Apply
**Track:** Media Services and Data Migration · **Difficulty:** intermediate · **Duration:** ~105 minutes · **Lab risk:** medium
**Build output:** Compare Plex and Jellyfin using operational criteria, then practice a reversible migration that separates media from application state, verifies a backup by extraction, enforces read-only media access for a service identity, performs a simulated cutover, and restores Plex state during rollback.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### tested_design
GNU-compatible Linux userland with Bash, GNU coreutils, GNU findutils, GNU tar, gzip, awk, Python 3, util-linux runuser, and an existing nobody account.

### shell
Bash is required because the lesson enables set -euo pipefail and uses multiline shell blocks.

### unsupported_without_adaptation
macOS and BSD utilities, whose stat, find, xargs, and runuser interfaces differ.
Minimal BusyBox environments that lack sort -z, xargs -0, stat -c, or compatible runuser behavior.
Containers without a nobody identity or without permission to switch identities.
Non-root sessions that cannot perform the service-identity permission test.

### product_scope
The comparison applies to general Plex and Jellyfin operating models, but feature availability, subscription terms, plug-ins, clients, and migration tools can change. Check current upstream documentation before a production decision.

### lab_scope
No Plex or Jellyfin package is installed or started. The lab validates filesystem migration mechanics and rollback discipline using fixtures.

## Learning objective

- Compare Plex and Jellyfin across licensing, account dependencies, remote access, plug-ins, client coverage, administration, and migration implications.
- Separate immutable media content from mutable application configuration, metadata, accounts, and watch-state data.
- Create a checksum manifest and compressed pre-migration archive of Plex application state.
- Extract and verify the archive before declaring it usable for recovery.
- Apply and test read-only media permissions using an unprivileged service identity.
- Translate a small fixture data set into a Jellyfin candidate without claiming that real Plex databases are directly interchangeable.
- Perform a simulated cutover and a rollback while preserving failed state for investigation.
- Verify the active-service markers and both Plex and Jellyfin manifests after rollback.

## Why this matters

Compare Plex and Jellyfin using operational criteria, then practice a reversible migration that separates media from application state, verifies a backup by extraction, enforces read-only media access for a service identity, performs a simulated cutover, and restores Plex state during rollback.

## Prerequisites

- Comfort using a Linux shell and reading command exit statuses.
- A Linux host or virtual machine with Bash, GNU coreutils, GNU findutils, tar, gzip, awk, Python 3, and runuser.
- A root shell is required for the controlled runuser permission test and for creating the isolated workspace under /opt.
- At least 20 MiB of free space under /opt.
- No existing data at /opt/lab-classroom/class59; preserve or relocate any pre-existing directory before beginning.

## Required reading

- Plex Support: Back Up Plex Media Server Data.
- Plex Support: Move an Install to Another System.
- Jellyfin Documentation: Backup and Restore.
- Jellyfin Documentation: Migrating.
- GNU Coreutils manual sections for install, sha256sum, stat, and mv.
- GNU tar manual sections covering archive listing, extraction, and directory selection.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Media library | The video, audio, image, subtitle, and related content files consumed by a media server. These files should normally be separated from application configuration and databases. |
| Application state | Mutable server data such as configuration, database files, metadata, users, watch history, artwork caches, and plug-in state. |
| Control plane | The configuration and state that determine how a service behaves, as distinct from the media files being served. |
| Cutover | The controlled point at which clients or routing begin using the replacement service. |
| Rollback | A planned restoration of the previous service and its validated state after a failed or rejected cutover. |
| Checksum manifest | A file containing cryptographic hashes and paths used to detect missing or changed files. |
| Restore test | Extraction of a backup into an isolated location followed by structural and checksum verification. |
| Least privilege | Granting a process only the access required for its task, such as permitting media reads while denying media modification. |
| Service identity | The operating-system account under which a service runs and whose permissions constrain that service. |
| Candidate state | Prepared replacement-service state that has passed validation but has not necessarily become authoritative. |

## Instruction

1. Begin with requirements, not brand loyalty. Plex and Jellyfin both index media, retrieve metadata, track playback, and serve clients, but their operating models differ.

2. Licensing: Plex is proprietary software with a mixture of free functions and optional Plex Pass features. Jellyfin is free and open-source software. A license difference does not automatically determine reliability or suitability; it affects auditability, feature access, support expectations, and long-term governance.

3. Accounts: Plex commonly integrates server ownership, user access, and discovery through Plex-hosted accounts. Some local-network behavior can continue under configured exceptions, but administrators must understand which workflows depend on Plex infrastructure. Jellyfin normally uses server-local users and authentication. That reduces reliance on a vendor account service but makes the homelab operator responsible for identity lifecycle, password policy, and safe exposure.

4. Remote access: Plex provides an integrated remote-access workflow and may use vendor-assisted discovery or relay behavior when direct connectivity is unavailable. Jellyfin operators generally design their own secure publication path, name resolution, TLS termination, and access policy. Direct exposure is not required for this lesson, and migration must not silently copy old trust assumptions into a new service.

5. Plug-ins and extensions: Plex retains a more restricted modern plug-in model than its historical ecosystem. Jellyfin supports server plug-ins, but each extension expands update, compatibility, and supply-chain risk. Inventory functionality instead of assuming that a plug-in with the same name or purpose will migrate.

6. Client coverage: Plex has broad official client availability across televisions, mobile devices, browsers, streaming appliances, and consoles. Jellyfin has clients for many common platforms, but availability and feature parity vary by device and application. Test every client type actually used in the household, including subtitle handling, codec negotiation, profiles, and accessibility needs.

7. Migration reality: media files are generally reusable, but Plex and Jellyfin configuration databases are not drop-in replacements for one another. Users, passwords, sharing rules, metadata choices, playlists, watch history, and plug-in behavior may require recreation, supported tooling, or documented mappings. Never point two applications at each other's mutable database directories.

8. Safe sequence: inventory the source, stop or quiesce writes in a real deployment, record versions, checksum state, create a backup, extract it into an isolated directory, verify checksums, prepare the candidate, validate clients, cut over, observe, and retain a rollback window. A backup is only a recovery hypothesis until extraction and verification succeed.

9. Lab command details: install -d creates directories rather than copying a file; its -m option sets the requested mode at creation time. find with -type f selects regular files, while -print0 emits NUL-delimited paths so spaces and unusual characters are handled safely. sort -z preserves those NUL delimiters. xargs -0 passes the paths safely to sha256sum. sha256sum -c reads a manifest, recalculates each listed hash, and returns a nonzero status if a file is absent or changed. tar -C changes archive context without changing the shell's working directory; -c creates, -x extracts, -t lists, -z enables gzip, and -f names the archive.

10. The lab uses a simulated service marker instead of starting real Plex or Jellyfin daemons. The files, archive, extraction, permissions, checksums, state translation, cutover, corruption, and recovery are real, but all writes remain beneath /opt/lab-classroom/class59/.

## Architecture

### source_service
A fixture Plex control plane stored at /opt/lab-classroom/class59/state/plex.

### candidate_service
A fixture Jellyfin control plane stored at /opt/lab-classroom/class59/state/jellyfin.

### shared_media
A separate media fixture at /opt/lab-classroom/class59/media/library. It is readable by the unprivileged nobody identity and not writable by that identity.

### backup_path
/opt/lab-classroom/class59/backups/plex-pre-migration.tgz

### restore_test_path
/opt/lab-classroom/class59/restore-check

### post_rollback_extract_path
/opt/lab-classroom/class59/verification-extract

### manifests
SHA-256 manifests are stored under /opt/lab-classroom/class59/manifests.

### cutover_model
The file cutover/active-service represents the selected service. cutover/active-service.before is an immutable migration record of the original Plex selection.

### data_flow
Clients conceptually select the service named by cutover/active-service.
Plex and Jellyfin have separate mutable control-plane directories.
Both services reference the same media path rather than copying media into application state.
The Plex archive is extracted and verified before cutover.
Rollback replaces damaged Plex fixture state with the previously verified extraction while retaining the damaged directory.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Create a migration decision matrix for the client devices actually used in your homelab. Include operating system, official or community client, direct-play needs, subtitle needs, offline use, and accessibility requirements.
Inventory current Plex integrations and classify each as required, replaceable, or removable. Record whether Jellyfin has an equivalent and how it will be tested.
Write production acceptance criteria covering accounts, libraries, posters, collections, playlists, watch state, hardware acceleration, remote access, logs, and restore time objectives without inventing performance claims.
Draft a maintenance-window runbook that includes source quiescence, version recording, backup extraction, checksum evidence, stakeholder approval, cutover, observation, and rollback authority.
Explain where production secrets and backups will be stored, who can read them, and when old copies will expire.

### submission
Submit the decision matrix, integration inventory, acceptance criteria, and rollback runbook. Do not submit credentials, tokens, private URLs, real viewing history, or copyrighted media.

## Feynman teach-back

### prompt
Explain the migration to a household member who understands files but not media-server databases.

### model_explanation
The movie files are like books, while Plex and Jellyfin each keep their own catalog cards, user records, and bookmarks. We leave the books in one read-only room and build Jellyfin a new catalog instead of handing it Plex's private catalog files. Before switching the sign on the door, we copy Plex's catalog, unpack that copy somewhere separate, and compare every file with a checksum list. We then test Jellyfin's catalog and change the sign. If the new catalog is unsuitable, we preserve the failed state, put the verified Plex catalog back, return the sign to Plex, and check the backup again.

### self_check_questions
Why is a successful archive-creation command insufficient evidence that recovery will work?
Why should the media directory and application-state directory have different permission policies?
Why can a watch-history mapping be reasonable while direct database copying is unsafe?
What evidence proves that rollback restored state rather than only changing a service label?

## Retrieval check

1. 1. What are two major operational differences between Plex and Jellyfin concerning licensing and accounts?
2. 2. Why is copying a Plex application database directly into a Jellyfin data directory unsafe?
3. 3. What does sha256sum -c prove, and what does it not prove?
4. 4. Why does this lab extract the backup before cutover and then extract it again after rollback?
5. 5. Which permission behavior demonstrates least privilege for the media fixture?
6. 6. Why are active-service and active-service.before both checked after rollback?
7. 7. Why is the damaged Plex directory retained rather than immediately deleted?
8. 8. What client-related work must be completed before selecting Plex or Jellyfin for a household?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

### estimated_minutes
14

### script
Open with the decision principle: Plex versus Jellyfin is not a universal winner question. Compare them against household requirements. Plex is proprietary, offers optional Plex Pass capabilities, commonly integrates Plex-hosted accounts, and provides a guided remote-access model with broad official client availability. Jellyfin is open source, generally keeps users local to the server, and gives operators more control, but also more responsibility for secure publication and client validation. Plug-in availability is not enough; each extension must be reviewed for maintenance and supply-chain risk.

Next, draw a boundary between media and application state. Media files can be shared as read-only content. Plex configuration and databases belong only to Plex, while Jellyfin receives a separate configuration and database. Users, passwords, playlists, shares, and watch state are migration projects rather than interchangeable files.

Show the class59 directory tree. Emphasize that every write stays below the assigned path. Explain install -d and its mode option while creating the tree. Create the media fixture, Plex preferences, sample watch state, active-service marker, and protected before marker.

Run the least-privilege test. The nobody identity reads the media fixture successfully, then attempts an append that must fail. Point out that this is stronger evidence than writing read-only in a policy document.

Generate the Plex checksum manifest. Explain that find emits NUL-delimited names, sort and xargs preserve that delimiter, and sha256sum hashes the files. Build the compressed archive, list its members, and verify expected paths.

Extract the archive into restore-check. Run the source manifest from inside that extracted tree and parse the XML. State clearly that backup creation without restoration testing is incomplete.

Prepare the Jellyfin candidate. Create separate XML configuration, write an explicit user map, and transform the small watch-state fixture. Clarify that this demonstrates controlled mapping, not direct compatibility with production Plex databases. Validate the XML and candidate manifest.

Change the active marker to Jellyfin only after all gates pass. Then introduce intentional damage to the Plex fixture. Confirm the checksum detects it. Preserve the damaged directory, promote the verified extraction, and return the active marker to Plex.

Finish by checking active-service.before, active-service, the restored Plex manifest, and the untouched Jellyfin candidate manifest. Extract the archive a second time into a new directory and verify it again. The lesson ends with evidence for least privilege, backup usability, candidate integrity, cutover, damage detection, and rollback.

## References

- Plex Support, Back Up Plex Media Server Data: https://support.plex.tv/articles/201539237-backing-up-plex-media-server-data/
- Plex Support, Move an Install to Another System: https://support.plex.tv/articles/201370363-move-an-install-to-another-system/
- Plex Support, Remote Access: https://support.plex.tv/articles/200289506-remote-access/
- Plex Legal, Terms of Service: https://www.plex.tv/about/privacy-legal/plex-terms-of-service/
- Jellyfin Documentation, Backup and Restore: https://jellyfin.org/docs/general/administration/backup-and-restore/
- Jellyfin Documentation, Migrating: https://jellyfin.org/docs/general/administration/migrate/
- Jellyfin Documentation, Networking: https://jellyfin.org/docs/general/networking/
- Jellyfin Documentation, Clients: https://jellyfin.org/downloads/clients/
- Jellyfin Project, Software Freedom: https://jellyfin.org/
- GNU Coreutils Manual, sha2 utilities: https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html
- GNU Coreutils Manual, install invocation: https://www.gnu.org/software/coreutils/manual/html_node/install-invocation.html
- GNU Findutils Manual: https://www.gnu.org/software/findutils/manual/html_mono/find.html
- GNU tar Manual: https://www.gnu.org/software/tar/manual/

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

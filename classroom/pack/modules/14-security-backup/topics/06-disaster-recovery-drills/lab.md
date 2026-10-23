# Lab: Disaster-Recovery Drills

**Module:** Segmentation, Backup & Power
**Activity type:** Lab (Practice)
**Lab risk:** medium
**Objective:** Distinguish disaster recovery from backup creation, high availability, and routine incident response.

## Before you start

- Comfort using a POSIX-compatible shell and standard file-management commands.
- Basic understanding of backups, archives, checksums, service dependencies, and incident response.
- Permission to create and modify /opt/lab-classroom/class75/.
- The parent directory /opt/lab-classroom/ must already exist and be writable by the learner.
- Python 3, tar, gzip, sha256sum, sort, diff, date, mkdir, mv, test, cat, and printf must be available.
- No production service may use /opt/lab-classroom/class75/.

## Guided lab

### scenario
A simulated application directory becomes unavailable. The operator must detect the failure, select and validate a known recovery point, restore it, prove data integrity, and document the drill.

### exercise_targets
### rto
Complete the classroom recovery within 20 minutes. This is an exercise target, not a production benchmark.

### rpo
Recover exactly the state represented by app-state-v1.tgz and baseline.sha256.

### success_condition
The restored manifest matches the baseline, required files exist, configuration values are readable, and the drill report contains measured timestamps.

### safety_rules
Confirm the current directory and LAB_ROOT value before every mutating command.
Do not substitute another path for /opt/lab-classroom/class75/.
Stop if /opt/lab-classroom/class75 already exists; inspect it rather than overwriting prior work.
Do not run this exercise against a production application, mounted backup repository, or shared service path.
Treat archive extraction as an overwrite-capable operation and inspect the archive member list first.

### steps
### step
1

### name
Establish the scoped workspace

### commands
export LAB_ROOT=/opt/lab-classroom/class75
test "$LAB_ROOT" = "/opt/lab-classroom/class75"
test ! -e "$LAB_ROOT"
mkdir "$LAB_ROOT"
mkdir "$LAB_ROOT/service" "$LAB_ROOT/backups" "$LAB_ROOT/manifests" "$LAB_ROOT/incidents" "$LAB_ROOT/drill"
mkdir "$LAB_ROOT/service/current" "$LAB_ROOT/service/current/config" "$LAB_ROOT/service/current/data"

### notes
If the nonexistence check fails, stop. Preserve the existing directory as evidence and use an instructor-approved reset procedure.
### step
2

### name
Create deterministic application state

### commands
printf '%s\n' 'application=inventory' 'mode=training' 'schema_version=1' > "$LAB_ROOT/service/current/config/app.conf"
printf '%s\n' 'asset-001,router,active' 'asset-002,switch,active' 'asset-003,server,maintenance' > "$LAB_ROOT/service/current/data/records.txt"
printf '%s\n' 'config/app.conf' 'data/records.txt' > "$LAB_ROOT/service/current/required-files.txt"
(cd "$LAB_ROOT/service/current" && sha256sum config/app.conf data/records.txt required-files.txt | sort) > "$LAB_ROOT/manifests/baseline.sha256"
cat "$LAB_ROOT/manifests/baseline.sha256"

### notes
The baseline manifest represents the trusted recovery point for this exercise.
### step
3

### name
Create and validate the recovery artifact

### commands
tar -C "$LAB_ROOT/service" -czf "$LAB_ROOT/backups/app-state-v1.tgz" current
sha256sum "$LAB_ROOT/backups/app-state-v1.tgz" > "$LAB_ROOT/manifests/archive.sha256"
gzip -t "$LAB_ROOT/backups/app-state-v1.tgz"
tar -tzf "$LAB_ROOT/backups/app-state-v1.tgz" | tee "$LAB_ROOT/drill/archive-members.txt"
grep -Fx 'current/config/app.conf' "$LAB_ROOT/drill/archive-members.txt"
grep -Fx 'current/data/records.txt' "$LAB_ROOT/drill/archive-members.txt"
grep -Fx 'current/required-files.txt' "$LAB_ROOT/drill/archive-members.txt"

### notes
Review the complete member list. Every member should be under current/ and no member should begin with an absolute path or contain a parent-directory traversal component.
### step
4

### name
Record the start and inject the outage

### commands
date -u +%s > "$LAB_ROOT/drill/start_epoch.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$LAB_ROOT/drill/start_utc.txt"
printf '%s\n' 'Scenario: active application directory unavailable' 'Recovery artifact: backups/app-state-v1.tgz' > "$LAB_ROOT/drill/declaration.txt"
mv "$LAB_ROOT/service/current" "$LAB_ROOT/incidents/current.unavailable"

### notes
The move is the controlled fault injection. It affects only the simulated service under the laboratory root.
### step
5

### name
Confirm detection

### commands
if test -f "$LAB_ROOT/service/current/config/app.conf"; then printf '%s\n' 'UNEXPECTED: health check passed'; else printf '%s\n' 'EXPECTED: health check failed because active state is unavailable'; fi | tee "$LAB_ROOT/drill/detection.txt"
test ! -e "$LAB_ROOT/service/current"

### notes
The second command should succeed silently because the active directory is absent.
### step
6

### name
Revalidate and restore

### commands
sha256sum -c "$LAB_ROOT/manifests/archive.sha256"
gzip -t "$LAB_ROOT/backups/app-state-v1.tgz"
tar -xzf "$LAB_ROOT/backups/app-state-v1.tgz" -C "$LAB_ROOT/service"

### notes
Do not extract until the archive digest, compression test, and previously captured member list are acceptable.
### step
7

### name
Verify integrity and function

### commands
(cd "$LAB_ROOT/service/current" && sha256sum config/app.conf data/records.txt required-files.txt | sort) > "$LAB_ROOT/manifests/restored.sha256"
diff -u "$LAB_ROOT/manifests/baseline.sha256" "$LAB_ROOT/manifests/restored.sha256" | tee "$LAB_ROOT/drill/manifest-diff.txt"
test -f "$LAB_ROOT/service/current/config/app.conf"
test -f "$LAB_ROOT/service/current/data/records.txt"
test -f "$LAB_ROOT/service/current/required-files.txt"
grep -Fx 'application=inventory' "$LAB_ROOT/service/current/config/app.conf"
grep -Fx 'schema_version=1' "$LAB_ROOT/service/current/config/app.conf"
test "$(wc -l < "$LAB_ROOT/service/current/data/records.txt")" -eq 3
printf '%s\n' 'PASS: integrity and functional checks completed' | tee "$LAB_ROOT/drill/verification-summary.txt"

### notes
A successful diff produces no difference output. Do not write the PASS summary if an earlier required command fails.
### step
8

### name
Measure and report

### commands
date -u +%s > "$LAB_ROOT/drill/end_epoch.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$LAB_ROOT/drill/end_utc.txt"
start=$(cat "$LAB_ROOT/drill/start_epoch.txt"); end=$(cat "$LAB_ROOT/drill/end_epoch.txt"); printf 'recovery_time_actual_seconds=%s\n' "$((end-start))" > "$LAB_ROOT/drill/metrics.txt"
printf '%s\n' 'recovery_point_actual=selected archive state' 'data_integrity=matched baseline manifest' 'scope=/opt/lab-classroom/class75/' >> "$LAB_ROOT/drill/metrics.txt"
cat "$LAB_ROOT/drill/start_utc.txt" "$LAB_ROOT/drill/end_utc.txt" "$LAB_ROOT/drill/metrics.txt" "$LAB_ROOT/drill/verification-summary.txt" > "$LAB_ROOT/drill/final-report.txt"
cat "$LAB_ROOT/drill/final-report.txt"

### notes
The measured result applies only to this exercise and environment. Add operator observations and corrective actions to the report after the technical work.

### stop_conditions
LAB_ROOT does not exactly equal /opt/lab-classroom/class75.
The target directory existed before the exercise.
An archive member uses an absolute path or parent-directory traversal.
The archive digest or compression validation fails.
A command would modify a path outside the classroom directory.
The baseline manifest is unavailable or cannot be trusted.
The learner cannot distinguish the simulated service from a real workload.

## Expected results

- The active simulated application becomes unavailable after the controlled move into the incidents directory.
- The health check reports the expected failure before restoration.
- The archive digest check and compression validation succeed before extraction.
- The restored application contains config/app.conf, data/records.txt, and required-files.txt.
- The restored checksum manifest is identical to the baseline manifest.
- The restored configuration identifies the inventory application and schema version 1.
- The restored data file contains exactly the three deterministic training records created during setup.
- The drill directory contains start and end timestamps, measured recovery time, archive members, detection output, verification output, and a final report.
- The original fault-injected directory remains under incidents/current.unavailable for comparison and evidence.

## Verification

- [ ] Run test "$(cat /opt/lab-classroom/class75/drill/manifest-diff.txt | wc -c)" -eq 0; success confirms that diff produced no integrity differences.
- [ ] Run sha256sum -c /opt/lab-classroom/class75/manifests/archive.sha256; the result must report the recovery archive as OK.
- [ ] Run diff -u /opt/lab-classroom/class75/manifests/baseline.sha256 /opt/lab-classroom/class75/manifests/restored.sha256; successful verification produces no differences.
- [ ] Run test -f /opt/lab-classroom/class75/service/current/config/app.conf and test -f /opt/lab-classroom/class75/service/current/data/records.txt; both commands must succeed.
- [ ] Run grep -Fx 'application=inventory' /opt/lab-classroom/class75/service/current/config/app.conf; the exact configuration line must be returned.
- [ ] Run test "$(wc -l < /opt/lab-classroom/class75/service/current/data/records.txt)" -eq 3; the command must succeed.
- [ ] Inspect /opt/lab-classroom/class75/drill/final-report.txt and confirm that it contains UTC start and end timestamps, recovery_time_actual_seconds, the selected recovery point, integrity status, and scope.
- [ ] Confirm that every artifact created by the lab is beneath /opt/lab-classroom/class75/.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Creating the laboratory root fails because the path already exists. | A previous exercise or retained evidence is present. | Stop and inspect the existing directory. Do not overwrite it. Ask the instructor to archive or reset the prior exercise while preserving anything needed for review. |
| Creating the laboratory root fails because the parent directory is missing or not writable. | The classroom host was not prepared or the learner lacks delegated access. | Have the administrator create and authorize the parent classroom directory. Do not redirect the exercise to an unapproved location. |
| The archive digest check reports FAILED. | The archive changed after its digest was recorded, the wrong manifest is being used, or storage corruption occurred. | Stop the restore, preserve the archive and output as evidence, verify the selected artifact, and create a new backup only after determining why the trusted digest no longer matches. |
| The compression validation reports an unexpected end of file. | The archive is incomplete or damaged. | Do not extract it. Select another validated recovery point or recreate the training archive from intact source data before repeating the fault injection. |
| Archive member paths are not confined to current/. | The wrong archive was selected or its contents are unsafe for the planned extraction directory. | Stop before extraction. Quarantine the artifact for analysis and use a recovery artifact whose complete member list is understood and confined to the intended path. |
| Extraction reports that files already exist. | The outage injection did not move the active directory, or a previous restore attempt created partial state. | Do not force an overwrite. Inspect service/current, move partial state to a uniquely named evidence directory under /opt/lab-classroom/class75/incidents/, revalidate the archive, and retry. |
| The restored manifest differs from the baseline. | The wrong recovery point was selected, extraction was incomplete, files changed after restoration, or the baseline is not the manifest for this archive. | Keep the service in a failed state, save the diff, compare archive identity with the selected manifest, and repeat restoration only after identifying the mismatch. |
| The integrity comparison passes but a functional check fails. | The baseline itself lacks required state, the functional expectation is incorrect, or the backup captured files consistently but incompletely. | Treat recovery as unsuccessful. Update backup scope and the runbook, create a corrected recovery artifact, and rerun the drill. |
| The measured recovery time is negative or implausible. | The host clock changed during the exercise or timestamp files came from different runs. | Preserve the recorded timestamps, note the clock issue in the report, correct time synchronization through the normal administrative process, and repeat the measurement. |

## Security

### controls
Use least-privilege access and grant write permission only to the classroom scope required for the exercise.
Verify LAB_ROOT exactly before each mutating operation; an unset or altered variable must be treated as a stop condition.
Keep backup access credentials separate from normal workload credentials in real deployments.
Store at least one production recovery copy outside the failure domain of the protected service.
Cryptographically verify selected artifacts and preserve hashes with the drill evidence.
Inspect archive paths before extraction to reduce path traversal and unintended overwrite risk.
Do not include production secrets, personal data, private keys, tokens, or authentic customer records in this exercise.
Restrict drill reports because real reports may reveal architecture, recovery paths, administrative identities, and security gaps.
Require explicit authorization before conducting fault injection against any shared or production environment.
Treat integrity success as necessary but not sufficient; malware-free status, application consistency, and authorization must also be established before production cutover.

### limitations
The backup and active state are on the same host and filesystem, so the lab does not test host loss, storage loss, media isolation, or off-site recovery.
The simulated service has no network, identity, certificate, database, or external dependency, so those recovery concerns must be addressed separately.
Cryptographic hashes detect differences but do not prove that the original recovery point was safe or semantically correct.

## Rollback

### goal
Return the simulated service to the trusted recovery point while preserving failed or partial state as drill evidence.

### procedure
Stop if any proposed destination is outside /opt/lab-classroom/class75/.
If service/current is absent, revalidate backups/app-state-v1.tgz and extract it into the service directory.
If service/current exists but fails verification, move it to a uniquely named directory beneath incidents/ rather than overwriting evidence.
Revalidate the archive digest and compression stream.
Extract the archive into the service directory.
Recreate restored.sha256 and compare it with baseline.sha256.
Record the rollback action, reason, operator, timestamps, and verification result in the drill report.
Leave all exercise artifacts in place for review unless an instructor authorizes a separate scoped cleanup.

### success_criteria
The active simulated state matches baseline.sha256, required files pass their checks, and the unsuccessful state remains preserved beneath the incidents directory.

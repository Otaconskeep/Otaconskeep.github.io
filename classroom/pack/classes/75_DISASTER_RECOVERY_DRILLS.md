# Class 75: Disaster-Recovery Drills

**Learning objective:** Distinguish disaster recovery from backup creation, high availability, and routine incident response.; Define recovery time objective, recovery point objective, recovery time actual, and recovery point actual.; Create a deterministic backup and a checksum manifest for a simulated application.; Inject a controlled failure without modifying anything outside the assigned laboratory directory.; Restore application state from a validated archive and prove that the restored files match the recovery point.; Collect timestamps, command output, and integrity evidence for a drill report.; Identify runbook gaps and convert drill observations into corrective actions.; Explain why an untested backup should not be treated as a proven recovery capability.
**Bloom level:** Understand / Apply
**Track:** Homelab Operations and Resilience · **Difficulty:** advanced · **Duration:** ~120 minutes · **Lab risk:** medium
**Build output:** Practice a controlled disaster-recovery exercise that validates backup integrity, measures recovery time, confirms restored data, records evidence, and improves a recovery runbook without affecting workloads outside the classroom directory.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux distributions providing a POSIX-compatible shell and GNU-compatible core utilities
Debian 12 or later
Ubuntu Server 22.04 LTS or later
Rocky Linux 9 or later
AlmaLinux 9 or later

### required_tools
POSIX-compatible shell
Python 3
GNU tar or a compatible tar implementation
gzip
sha256sum
diff
grep
sort
tee
date
wc

### notes
Archive listing and command output can differ slightly between tool implementations.
The exercise assumes epoch timestamps are available through date -u +%s.
The learner must not replace the fixed laboratory root with a home directory or another system path.
No container runtime, hypervisor, init system, network service, or external cloud account is required.

## Learning objective

- Distinguish disaster recovery from backup creation, high availability, and routine incident response.
- Define recovery time objective, recovery point objective, recovery time actual, and recovery point actual.
- Create a deterministic backup and a checksum manifest for a simulated application.
- Inject a controlled failure without modifying anything outside the assigned laboratory directory.
- Restore application state from a validated archive and prove that the restored files match the recovery point.
- Collect timestamps, command output, and integrity evidence for a drill report.
- Identify runbook gaps and convert drill observations into corrective actions.
- Explain why an untested backup should not be treated as a proven recovery capability.

## Why this matters

Practice a controlled disaster-recovery exercise that validates backup integrity, measures recovery time, confirms restored data, records evidence, and improves a recovery runbook without affecting workloads outside the classroom directory.

## Prerequisites

- Comfort using a POSIX-compatible shell and standard file-management commands.
- Basic understanding of backups, archives, checksums, service dependencies, and incident response.
- Permission to create and modify /opt/lab-classroom/class75/.
- The parent directory /opt/lab-classroom/ must already exist and be writable by the learner.
- Python 3, tar, gzip, sha256sum, sort, diff, date, mkdir, mv, test, cat, and printf must be available.
- No production service may use /opt/lab-classroom/class75/.

## Required reading

- NIST Special Publication 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: review the sections covering recovery strategies, testing, training, and exercises.
- CISA, Data Backup Options: review the guidance on backup isolation, restoration testing, and recovery planning.
- The local Homelab Academy lesson covering backup types, retention, and integrity verification.
- The documentation for the archive and checksum utilities installed on the laboratory host.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Disaster recovery | The coordinated process of restoring technology services and data after a disruptive event. |
| Recovery time objective | The maximum targeted duration for restoring an acceptable level of service after disruption. |
| Recovery point objective | The maximum targeted amount of data loss, expressed as time between the selected recovery point and the disruption. |
| Recovery time actual | The duration observed during a recovery event or drill. |
| Recovery point actual | The data-loss interval actually observed after recovery. |
| Recovery point | A specific backup, snapshot, replica position, or transaction boundary selected for restoration. |
| Runbook | A tested sequence of recovery actions, decisions, prerequisites, owners, and verification steps. |
| Integrity manifest | A recorded set of cryptographic hashes used to detect unexpected changes in protected files. |
| Fault injection | A deliberate and bounded action that creates a known failure so detection and recovery procedures can be tested. |
| Tabletop exercise | A discussion-based review of roles, decisions, dependencies, and communications without executing a technical recovery. |
| Functional drill | A controlled exercise in which participants execute some or all technical recovery procedures. |
| Evidence | Logs, timestamps, hashes, screenshots, command output, and approvals that demonstrate what occurred during a drill. |

## Instruction

A backup is only an input to disaster recovery. Recovery also requires people who know when to invoke the plan, credentials that remain available during an outage, documented dependencies, compatible replacement capacity, validated data, and a method for deciding when service is safe to return. A successful backup job therefore does not prove that a service can be restored. A drill closes this assurance gap by selecting a scenario, declaring boundaries, injecting a controlled failure, executing the runbook, verifying the result, and recording improvements.

Two common planning measures are recovery time objective and recovery point objective. RTO is a target for how long service restoration may take. RPO is a target for how much recent data may be lost. The observed values from an exercise are recovery time actual and recovery point actual. Targets and actuals must not be confused. A five-minute restore in a tiny classroom directory does not predict the recovery time of a large production system. Production timing includes data transfer, replacement infrastructure, dependency recovery, authentication, network changes, validation, approvals, and user communication.

A rigorous drill starts with scope and safety controls. Identify the protected service, recovery point, incident controller, operator, observer, start condition, stop conditions, communications path, and escalation method. Confirm that the backup is isolated from the simulated failure. Record the exact artifact selected for recovery and validate that it can be read before creating the outage. For an archive, validation should include checking the compression stream, listing members, reviewing paths, and retaining a cryptographic digest. Restoration should occur into an isolated location when possible so that integrity and application checks can happen before cutover.

Verification must test more than file existence. Structural verification asks whether required files and directories are present. Integrity verification compares trusted hashes or application-level records. Functional verification checks whether the service can perform its intended work. Dependency verification checks identity, storage, name resolution, networking, certificates, secrets, and downstream systems. Business validation asks whether the recovered state is acceptable to the service owner. In this laboratory, a deterministic file manifest represents integrity verification, while a configuration-and-data health check represents a minimal functional gate.

Drills should produce evidence and corrective actions rather than a pass-or-fail slogan. Record when the incident was declared, when recovery began, which backup was selected, every deviation from the runbook, when technical verification completed, and who authorized return to service. Separate operator mistakes from runbook defects and environmental defects. Assign each corrective action an owner and due date, then retest material changes. Repeated exercises should vary scenarios: corrupted data, unavailable backup credentials, loss of a host, failed dependencies, compromised administrative accounts, or an unusable recent recovery point. The goal is not theatrical failure. The goal is repeatable proof that recovery assumptions remain true.

## Architecture

### scope_boundary
/opt/lab-classroom/class75/

### components
service/current represents the active application configuration and data.
backups/app-state-v1.tgz is the selected recovery artifact.
manifests/baseline.sha256 records the expected hashes at the recovery point.
incidents/current.unavailable contains the displaced state during fault injection.
drill contains timestamps, observations, command output, and the final report.

### recovery_flow
Create deterministic simulated application state.
Record a trusted integrity manifest.
Create and validate the recovery artifact.
Record the drill start and inject the scoped outage.
Confirm that the health check detects the outage.
Restore the selected archive.
Recalculate hashes and compare them with the trusted manifest.
Run structural and functional checks.
Record the completion time, findings, and corrective actions.

### trust_boundaries
The simulated active state and backup reside in separate subdirectories but on the same laboratory filesystem.
Because this exercise does not provide media isolation, it tests restoration procedure but does not prove resilience against host or filesystem loss.
All write operations are restricted to /opt/lab-classroom/class75/.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Design a second drill for the same simulated application without executing unapproved changes.

### deliverables
Write a scenario in which the newest recovery artifact is unusable and the operator must select an older known-good recovery point.
Define the exercise RTO and RPO, clearly labeling them as targets rather than measured performance.
Create a dependency map covering storage, identity, name resolution, certificates, secrets, monitoring, and operator access.
Write at least five validation checks divided among structural, integrity, functional, dependency, and business validation.
Create a drill report template with roles, timestamps, decisions, deviations, evidence links, corrective-action owners, and retest dates.
Explain how the design would change if backups were encrypted and the primary identity system were unavailable.

### grading_criteria
The scenario has an explicit scope, start condition, stop conditions, and success criteria.
The recovery point selection process is unambiguous.
The plan protects evidence and avoids uncontrolled overwrite.
The proposed validation goes beyond checking that files exist.
Corrective actions include ownership and retesting.

## Feynman teach-back

### prompt
Explain disaster recovery to a new homelab operator using a notebook backup as the analogy. Your explanation must distinguish owning a copy from proving that the copy can restore useful work.

### model_explanation
A backup is like a photocopy of a notebook. Disaster recovery is the full plan for finding the right photocopy, obtaining a replacement notebook, copying the information back, checking that no pages are missing, and deciding that people may use it again. RPO says how much writing we are willing to lose because it happened after the photocopy. RTO says how long we are willing to wait before the notebook is usable. A drill measures what actually happens and reveals missing supplies or unclear instructions before a real emergency.

### self_check_questions
Can I explain why a successful backup job does not prove recoverability?
Can I state the difference between an objective and an observed result?
Can I describe at least one case where matching file hashes would still be insufficient?
Can I identify the failure domains this laboratory does not test?

## Retrieval check

1. 1. What is the difference between an RTO and a recovery time actual?
2. 2. What is the difference between an RPO and a recovery point?
3. 3. Why does a successful backup job not prove disaster-recovery readiness?
4. 4. Why should archive members be inspected before extraction?
5. 5. What does a checksum manifest prove, and what does it not prove?
6. 6. Why must the exercise preserve timestamps and command output?
7. 7. In this laboratory, why is keeping the backup in a separate subdirectory insufficient to prove resilience against storage loss?
8. 8. What should an operator do when restored hashes do not match the trusted baseline?
9. 9. Name three categories of recovery verification beyond basic file existence.
10. 10. Why should drill corrective actions have owners and retest dates?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

### opening
In Class 75, we move beyond creating backups and practice proving recovery. The exercise uses a completely simulated application beneath one classroom directory. We will create a trusted recovery point, inject a controlled outage, restore the application, validate the result, and capture evidence.

### segments
First, define the scope and stop conditions. A recovery drill should never begin with an ambiguous target. In this class, every write must remain beneath /opt/lab-classroom/class75/.
Next, create deterministic configuration and data. We hash the files to establish the exact recovery point. This manifest is not merely a list of files; it records the bytes we expect after restoration.
We then create the archive and validate it before the incident. The compression stream must be readable, the archive digest must be retained, and every member path must remain under the expected current directory.
The outage is injected by moving the active state into an incidents directory. This is deliberately bounded and reversible. The failed health check proves that our detection step notices the simulated outage.
Before restoration, validate the selected artifact again. Recovery pressure is exactly when operators are most likely to select the wrong file or skip a safety check.
After extraction, calculate a new manifest and compare it with the baseline. Then perform functional checks against configuration values and record count. Matching hashes alone would not test every real application behavior, but it supplies strong integrity evidence for this deterministic exercise.
Finally, capture end time and calculate the observed recovery duration. Never present this classroom value as a production benchmark. Real recovery includes larger data sets, infrastructure replacement, dependencies, approvals, security checks, and user communication.
The drill is complete only after documenting deviations, assigning corrective actions, and scheduling a retest. The purpose is not to demonstrate perfection; it is to discover assumptions safely.

### closing
A backup is a recovery ingredient, not a recovery guarantee. Confidence comes from bounded exercises, trusted evidence, layered verification, honest reporting, and repeated improvement.

## References

- NIST Special Publication 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/pubs/sp/800/34/r1/final
- NIST Cybersecurity Framework 2.0, Recover function: https://www.nist.gov/cyberframework
- CISA, Data Backup Options: https://www.cisa.gov/news-events/news/data-backup-options
- CISA StopRansomware Guide: https://www.cisa.gov/stopransomware/ransomware-guide
- GNU tar manual: https://www.gnu.org/software/tar/manual/
- GNU Coreutils manual, sha256sum invocation: https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html
- ISO 22301:2019, Security and resilience — Business continuity management systems — Requirements: https://www.iso.org/standard/75106.html

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

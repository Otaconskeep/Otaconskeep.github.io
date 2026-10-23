# Reading: Disaster-Recovery Drills

**Module:** Segmentation, Backup & Power
**Activity type:** Reading (Learn)
**Objective:** Distinguish disaster recovery from backup creation, high availability, and routine incident response.

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

## Required reading

- NIST Special Publication 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: review the sections covering recovery strategies, testing, training, and exercises.
- CISA, Data Backup Options: review the guidance on backup isolation, restoration testing, and recovery planning.
- The local Homelab Academy lesson covering backup types, retention, and integrity verification.
- The documentation for the archive and checksum utilities installed on the laboratory host.

## References

- NIST Special Publication 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/pubs/sp/800/34/r1/final
- NIST Cybersecurity Framework 2.0, Recover function: https://www.nist.gov/cyberframework
- CISA, Data Backup Options: https://www.cisa.gov/news-events/news/data-backup-options
- CISA StopRansomware Guide: https://www.cisa.gov/stopransomware/ransomware-guide
- GNU tar manual: https://www.gnu.org/software/tar/manual/
- GNU Coreutils manual, sha256sum invocation: https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html
- ISO 22301:2019, Security and resilience — Business continuity management systems — Requirements: https://www.iso.org/standard/75106.html

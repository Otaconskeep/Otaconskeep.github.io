# Homework: SMART, Disk Health, and Failure Warning

**Module:** Segmentation, Backup & Power
**Activity type:** Homework / independent application
**Objective:** Explain what SMART can and cannot predict.

## Requirements

### assignment
Design a disk-health alert policy with separate severities for pending sectors, uncorrectable sectors, increasing CRC errors, excessive temperature, NVMe Critical Warning bits, low available spare, endurance consumption, media errors, and telemetry collection failure.
For every alert, document the evidence to preserve, immediate checks, escalation condition, and replacement decision.
Explain how the policy changes for a standalone disk, a mirrored pool, and a distributed storage cluster.
Identify how your actual controller, HBA, hypervisor, or USB enclosure exposes or hides drive telemetry.
Describe how you would prove that a backup is restorable before replacing a suspect disk.

### submission
Submit a concise runbook containing alert conditions, rationale, operator actions, and rollback or stop conditions. Do not run tests against production or irreplaceable disks as part of the homework.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

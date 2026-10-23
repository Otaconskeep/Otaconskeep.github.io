# Homework: Disaster-Recovery Drills

**Module:** Segmentation, Backup & Power
**Activity type:** Homework / independent application
**Objective:** Distinguish disaster recovery from backup creation, high availability, and routine incident response.

## Requirements

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

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

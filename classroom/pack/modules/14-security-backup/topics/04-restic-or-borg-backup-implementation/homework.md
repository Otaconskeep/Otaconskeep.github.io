# Homework: Restic or Borg Backup Implementation

**Module:** Segmentation, Backup & Power
**Activity type:** Homework / independent application
**Objective:** Initialize and use a password-protected local Restic repository.

## Requirements

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

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

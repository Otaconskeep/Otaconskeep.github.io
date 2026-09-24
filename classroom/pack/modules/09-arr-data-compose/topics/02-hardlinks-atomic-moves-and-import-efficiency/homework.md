# Homework — Hardlinks, Atomic Moves, and Import Efficiency

**Module:** ARR Data Model & Compose
**Activity type:** Homework / independent application
**Objective:** Explain the relationship between a pathname, directory entry, inode, and file data.

## Requirements

### assignment
Design a production import policy for a downloader and media library.

### requirements
Document how the service verifies that incoming and library paths share a filesystem.
Choose whether the source is retained as a hardlink, removed after publication, or copied across a filesystem boundary.
Define behavior for an existing destination with the same name.
Define whether imported content is immutable and identify every application allowed to modify it.
Describe how temporary names are made unique when two workers import concurrently.
List the inode, device, link-count, hash, and application-level checks recorded in logs.
Explain how interrupted copies are distinguished from fully published files when a cross-filesystem copy is unavoidable.
Keep any practical exercise and generated data strictly under /opt/lab-classroom/class35/.

### deliverable
Submit a one-page workflow description and a shell pseudocode sequence that separates validation, temporary creation, publication, verification, and cleanup.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

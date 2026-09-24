# Homework: Logs and journalctl

**Module:** Linux Foundations
**Activity type:** Homework / independent application
**Objective:** Explain the relationship between applications, systemd units, systemd-journald, and journalctl.

## Requirements

Choose one service visible on the lab host and export its current-boot records to /opt/lab-classroom/class20/homework-unit.log using journalctl -b -u with an ISO-like output format.
Create /opt/lab-classroom/class20/homework-notes.txt describing the selected service, the exact query, the visible time range, and any access or retention limitations.
Export records from the last 15 minutes to /opt/lab-classroom/class20/homework-last-15-minutes.log using --since and a human-readable relative time expression.
Compare short-iso, verbose, and JSON output for one recent record, then document which format is best for interactive review and which is best for scripting.
Explain in homework-notes.txt why an empty query result cannot by itself prove that an event never occurred.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

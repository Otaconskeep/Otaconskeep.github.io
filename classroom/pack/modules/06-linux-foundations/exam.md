# Module exam: Linux Foundations (practical)

**Timebox:** 60–90 minutes  
**Environment:** disposable lab VM/shell; console available if SSH tasks are live.

## Stations

### Station A: Navigate & evidence (Classes 16–17)
Create `/opt/lab-classroom/module06-exam/`, write a sample log, and produce `errors.count` via pipeline.  
**Pass:** absolute paths correct; count accurate; no writes outside lab path.

### Station B: Permissions (Class 18)
Create a shared directory proving group-read without world-write.  
**Pass:** `namei -l` evidence; write denied for non-group or others as designed; no 777.

### Station C: Process/service (Classes 19–20)
Install a user oneshot that logs a heartbeat; capture `systemctl --user status` and a journal excerpt.  
**Pass:** unit succeeded; evidence files present; redaction applied.

### Station D: SSH safety (Class 21)
Either (live) prove key login on lab VM with hardening notes, or (simulation) write a one-page hardening order + lockout recovery plan.  
**Pass:** order correct; break-glass documented; no unexplained sshd breakage.

## Rubric (100 points)

| Station | Points | Partial credit |
|---|---:|---|
| A | 25 | 15 if pipeline works but path hygiene weak |
| B | 25 | 10 if permissions work but 777 used (auto-fail security note) |
| C | 25 | 15 if unit runs but journal evidence missing |
| D | 25 | 15 if simulation complete but missing recovery |

**Passing criteria:** ≥80 total **and** zero critical safety failures (777 on shared tree, sshd change without console, writes outside `/opt/lab-classroom`).

## Remediation

If fail: identify weakest station → complete that class lab again → redo Feynman → re-sit only failed stations within one week.

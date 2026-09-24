# Homework: Processes, Signals, and systemd

**Module:** Linux Foundations
**Activity type:** Homework / independent application
**Objective:** Distinguish programs, processes, threads, jobs, services, and systemd units

## Requirements

Under /opt/lab-classroom/class19/, create a text file that maps the common ps state letters R, S, D, T, and Z to their meanings.
Extend a copy of worker.sh under the same directory so SIGUSR1 records a one-line diagnostic message without terminating.
Run the extended worker, verify its identity, send SIGUSR1, and document the observed result under /opt/lab-classroom/class19/.
Choose one existing service and record the read-only values of Id, ActiveState, SubState, MainPID, ControlGroup, and FragmentPath in a file under the lab directory.
Write a short incident procedure under the lab directory describing identity verification, graceful termination, bounded waiting, escalation criteria, and post-action verification.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

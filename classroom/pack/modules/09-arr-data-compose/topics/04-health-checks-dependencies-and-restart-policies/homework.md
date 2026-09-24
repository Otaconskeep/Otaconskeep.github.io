# Homework — Health Checks, Dependencies, and Restart Policies

**Module:** ARR Data Model & Compose
**Activity type:** Homework / independent application
**Objective:** Explain why a running process is not necessarily a healthy or ready service

## Requirements

Modify only the lab copy of supervisor.py to use exponential backoff capped at 16 seconds. Record the delay sequence in a log and explain why a cap is necessary.
Add a maximum of three application restarts within a 60-second window. After the limit is reached, leave the service stopped and emit an explicit operator-action message.
Temporarily change READY_AFTER in dependency.py to 35 seconds and predict the supervisor result before running it. Compare the observed behavior with the 30-second readiness deadline.
Design health checks for a reverse proxy, DNS resolver, database, and backup job. For each, state what startup, liveness, and readiness mean and identify cases where one check is not applicable.
Write a short policy describing when your homelab uses no restart, on-failure restart, or always restart behavior. Include logging, retry limits, and alert thresholds.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

# Homework — Docker Engine Installation and Daemon Fundamentals

**Module:** Docker, Storage & Permissions
**Activity type:** Homework / independent application
**Objective:** Explain the responsibilities of the Docker CLI, Docker daemon, containerd, and OCI runtime

## Requirements

### assignment
Write a one-page Docker Engine deployment plan for a non-production Linux virtual machine. Identify the operating-system release and architecture, the selected installation source, package provenance controls, target version policy, daemon API exposure, logging policy, data-root capacity assumptions, service verification procedure, maintenance window, and rollback criteria.

### practical_extension
Create a second inactive configuration at /opt/lab-classroom/class27/daemon-homework.json that uses only paths under the class workspace. Add a labels object identifying the environment as training and the owner as homelab. Validate the file with an available JSON parser and, if supported, dockerd validation mode. Do not launch the daemon.

### submission
The written deployment plan
The staged daemon-homework.json file
The exact validation output
A short explanation of why daemon socket access is privileged
A rollback checklist containing objective success criteria

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

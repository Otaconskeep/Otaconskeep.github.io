# Class 27: Docker Engine Installation and Daemon Fundamentals

**Learning objective:** Explain the responsibilities of the Docker CLI, Docker daemon, containerd, and OCI runtime; Compare repository-based, distribution-provided, convenience, static-binary, and rootless installation approaches; Identify the daemon API endpoint and explain why access to it is security-sensitive; Describe how a service manager starts, stops, and monitors the Docker daemon; Create a syntactically valid daemon configuration with bounded local logging; Validate a staged daemon configuration without starting a second daemon; Recognize common installation, socket, configuration, storage, and service-start failures; Plan a controlled rollback before changing Docker packages or daemon settings
**Bloom level:** Understand / Apply
**Track:** Containers and Application Platforms · **Difficulty:** beginner · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Teach learners how Docker Engine is packaged, installed, started, configured, and verified while distinguishing the Docker client, daemon, API socket, container runtime, image store, and service manager. The lab safely stages and validates daemon configuration without changing the host package database, system service configuration, or any path outside the class workspace.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-28
**Compatibility:** ### platforms
Linux hosts supported by the selected Docker Engine release
Physical machines and virtual machines with a compatible kernel
x86_64, arm64, and other architectures only when supported by the chosen package source

### notes
Package names, repository setup, service units, and supported versions vary by distribution and release.
The staged configuration is not activated and therefore does not replace the host's normal daemon configuration.
dockerd configuration validation depends on the capabilities of the installed Docker release.
Some service definitions pass daemon options directly; duplicate options in daemon.json may be rejected.
Rootless installations use different service, socket, storage, and environment conventions.
Docker Desktop is architecturally and operationally different from a native Linux Docker Engine installation and is outside this lab's mutation scope.

## Learning objective

- Explain the responsibilities of the Docker CLI, Docker daemon, containerd, and OCI runtime
- Compare repository-based, distribution-provided, convenience, static-binary, and rootless installation approaches
- Identify the daemon API endpoint and explain why access to it is security-sensitive
- Describe how a service manager starts, stops, and monitors the Docker daemon
- Create a syntactically valid daemon configuration with bounded local logging
- Validate a staged daemon configuration without starting a second daemon
- Recognize common installation, socket, configuration, storage, and service-start failures
- Plan a controlled rollback before changing Docker packages or daemon settings

## Why this matters

Teach learners how Docker Engine is packaged, installed, started, configured, and verified while distinguishing the Docker client, daemon, API socket, container runtime, image store, and service manager. The lab safely stages and validates daemon configuration without changing the host package database, system service configuration, or any path outside the class workspace.

## Prerequisites

- Basic Linux command-line navigation
- Familiarity with JSON syntax
- Ability to identify the Linux distribution and CPU architecture
- A Linux host or virtual machine with permission to create files under /opt/lab-classroom/class27/
- Docker Engine is optional; configuration validation steps are skipped when dockerd is unavailable

## Required reading

- Docker Engine installation overview: https://docs.docker.com/engine/install/
- Docker daemon configuration overview: https://docs.docker.com/engine/daemon/
- Docker post-installation guidance for Linux: https://docs.docker.com/engine/install/linux-postinstall/
- Docker Engine security overview: https://docs.docker.com/engine/security/
- OCI runtime specification overview: https://github.com/opencontainers/runtime-spec

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Docker Engine | The container platform consisting primarily of the Docker daemon, its API, and the Docker command-line client. |
| Docker CLI | The docker command-line client that converts user requests into API calls to a Docker daemon. |
| dockerd | The long-running Docker daemon that manages API requests, images, containers, networks, volumes, and integration with lower-level runtimes. |
| containerd | A container lifecycle manager used by Docker Engine for image transfer, container execution coordination, and runtime supervision. |
| OCI runtime | A low-level component, commonly runc, that creates a container process according to the Open Container Initiative runtime specification. |
| Unix socket | A local interprocess communication endpoint represented by a filesystem path; Docker commonly exposes its local API through one. |
| daemon.json | The conventional JSON configuration file used to provide persistent settings to the Docker daemon. |
| storage driver | The Docker subsystem that stores and combines image layers and container writable layers. |
| registry | A service that stores and distributes container images. |
| rootless mode | A Docker operating mode designed to run the daemon and containers without a system-level root daemon, subject to platform requirements and limitations. |
| live restore | A daemon setting intended to allow supported running containers to remain active during certain daemon interruptions or upgrades. |

## Instruction

Docker installation is more than placing a client binary on a host. A functional deployment normally includes the Docker CLI, the dockerd daemon, containerd, an OCI runtime, service definitions, and supporting networking and storage components. When a user runs a docker command, the CLI sends an API request to a daemon. On Linux, that request commonly travels through a local Unix socket. The daemon resolves images, prepares storage and networking, asks containerd to manage the container lifecycle, and ultimately relies on an OCI runtime to create the isolated process. This separation explains why a client can be installed while the daemon is missing, stopped, inaccessible, or located on another system.

Choose an installation source deliberately. Vendor-maintained repositories usually provide current Docker Engine packages and documented upgrade paths. Distribution repositories may integrate well with the operating system but can carry different versions or packaging decisions. Static binaries require the operator to manage service integration and updates. Convenience installers reduce setup effort but are less appropriate when reproducibility, review, and package provenance matter. Rootless mode can reduce dependence on a privileged system daemon, but it has prerequisites and operational differences that must be evaluated rather than assumed away. Record the chosen source, package names, repository signing mechanism, supported operating-system release, architecture, expected version, and rollback procedure before installation.

The host service manager commonly launches dockerd, tracks its process, captures logs, and applies startup dependencies. A daemon can fail even when package installation succeeds. Frequent causes include invalid JSON, options duplicated between startup arguments and daemon configuration, unsupported directives, storage-driver problems, stale process metadata, insufficient disk space, or an occupied API endpoint. Diagnose from the service status and daemon journal before repeatedly restarting it. Repeated retries can obscure the first and most useful error.

Daemon settings should be treated as controlled infrastructure configuration. Validate JSON first, then use dockerd's configuration validation feature when supported by the installed release. Logging must be bounded because unbounded container logs can consume the host filesystem. The local log driver and a rotation policy are reasonable subjects for evaluation, but production values must reflect application volume, retention requirements, and centralized logging design. The data root contains critical Docker state and must not be moved casually. Changing it without a migration plan can make existing images, volumes, and containers appear to disappear.

Access to the Docker API is highly privileged. A user who can control a rootful daemon can generally start containers with host mounts and other capabilities that lead to host-level control. Membership in a local access group should therefore be governed like administrative access. Do not expose an unauthenticated daemon API over a network. Remote administration should use an authenticated and encrypted mechanism supported by the deployment design.

This class does not install or restart Docker because those actions would modify the package database, service state, and system paths outside the permitted lab workspace. Instead, the learner inventories the host, creates an installation decision record, stages a daemon configuration whose paths remain inside the workspace, and performs read-only validation when the relevant tools already exist. A real installation should occur later in an approved maintenance window using the official instructions for the exact operating system and a tested rollback plan.

## Architecture

### request_flow
A user or automation process invokes the Docker CLI.
The CLI selects a Docker context and API endpoint.
The CLI sends an API request to dockerd, commonly through a local Unix socket.
dockerd applies authorization assumptions, configuration, image, network, volume, and container logic.
dockerd delegates container lifecycle work to containerd.
containerd invokes an OCI runtime to create or manage the isolated container process.
Container output is handled by the selected logging driver, while writable layers are handled by the selected storage driver.

### control_plane
The Docker daemon and its API form the local container control plane. The service manager supervises the daemon, but it does not replace Docker's own API or state management.

### data_plane
Container processes, virtual network interfaces, mounted volumes, image layers, and writable layers constitute the workload-facing data plane.

### trust_boundaries
Between an operator and the Docker API endpoint
Between the daemon and images obtained from registries
Between container processes and the host kernel
Between persistent volumes and application containers
Between package repositories and the host package manager

### lab_workspace
/opt/lab-classroom/class27/

### staged_socket
/opt/lab-classroom/class27/runtime/docker.sock

### staged_data_root
/opt/lab-classroom/class27/docker-data

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

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

## Feynman teach-back

### prompt
Explain Docker Engine to someone who thinks the docker command directly creates containers.

### model_explanation
The docker command is usually a client, like a remote control. It sends a request to the Docker daemon through an API endpoint. The daemon decides how to obtain the image, configure storage and networking, and manage the container. It delegates lower-level lifecycle work to containerd, which uses an OCI runtime to create the actual isolated process. Installing only the remote control does not guarantee that the daemon exists, is running, or permits the user to access it.

### self_check
Can you explain why the CLI may be installed while docker commands still fail?
Can you identify which component owns the API and which component creates the low-level process?
Can you explain why access to the daemon socket is equivalent to powerful host access?
Can you explain why changing data-root can make existing Docker objects appear missing?
Can you describe how you would validate a configuration before restarting a production daemon?

## Retrieval check

1. 1. What is the primary role of the Docker CLI?
2. 2. Why can the Docker CLI be present even when containers cannot be started?
3. 3. Which component commonly receives Docker API requests and coordinates images, networks, volumes, and containers?
4. 4. What lower-level components are commonly involved after dockerd accepts a container creation request?
5. 5. Why should access to a rootful Docker daemon socket be treated as administrative access?
6. 6. What is the purpose of validating daemon.json before restarting the daemon?
7. 7. Why is changing data-root without a migration plan dangerous?
8. 8. What problem does a bounded logging configuration help prevent?
9. 9. Why does this class stage an installation plan instead of installing Docker directly?
10. 10. Name two sources of configuration conflict that can prevent dockerd from starting.

## Guided lab

### name
Inventory and Safely Stage a Docker Daemon Configuration

### scope_guardrail
Every command that writes data targets /opt/lab-classroom/class27/. Do not install packages, start or stop services, launch dockerd, edit system daemon configuration, or change Docker's active data directory during this lab.

### steps
### step
1

### title
Create the isolated workspace

### commands
install -d /opt/lab-classroom/class27/runtime /opt/lab-classroom/class27/docker-data /opt/lab-classroom/class27/docker-exec

### explanation
These directories hold all generated class files and staged runtime paths.
### step
2

### title
Capture a read-only host inventory

### commands
{ printf '%s\n' 'Class 27 host inventory'; printf 'Kernel: '; uname -srmo; printf 'Architecture: '; uname -m; printf 'docker CLI: '; command -v docker || printf '%s\n' 'not installed'; printf 'dockerd: '; command -v dockerd || printf '%s\n' 'not installed'; printf 'containerd: '; command -v containerd || printf '%s\n' 'not installed'; } > /opt/lab-classroom/class27/host-inventory.txt
cat /opt/lab-classroom/class27/host-inventory.txt

### explanation
The discovery commands read host information, while their output is written only inside the permitted workspace.
### step
3

### title
Create an installation decision record

### commands
printf '%s\n' 'Installation source: official instructions for the detected operating system' 'Repository provenance must be verified before use: yes' 'Target architecture must match host inventory: yes' 'Maintenance window required: yes' 'Package and service changes executed in this lab: no' 'Rollback must be documented before installation: yes' > /opt/lab-classroom/class27/installation-plan.txt
cat /opt/lab-classroom/class27/installation-plan.txt

### explanation
The record separates installation planning from execution and prevents an unreviewed system change.
### step
4

### title
Stage a daemon configuration

### commands
printf '%s\n' '{' '  "data-root": "/opt/lab-classroom/class27/docker-data",' '  "exec-root": "/opt/lab-classroom/class27/docker-exec",' '  "pidfile": "/opt/lab-classroom/class27/runtime/docker.pid",' '  "hosts": ["unix:///opt/lab-classroom/class27/runtime/docker.sock"],' '  "log-driver": "local",' '  "log-opts": {' '    "max-size": "10m",' '    "max-file": "3"' '  },' '  "live-restore": true' '}' > /opt/lab-classroom/class27/daemon.json
cat /opt/lab-classroom/class27/daemon.json

### explanation
This inactive configuration demonstrates persistent daemon options. Every filesystem path remains under the class workspace.
### step
5

### title
Validate JSON syntax

### commands
if command -v jq >/dev/null 2>&1; then jq empty /opt/lab-classroom/class27/daemon.json && printf '%s\n' 'JSON syntax: valid'; elif command -v python3 >/dev/null 2>&1; then python3 -m json.tool /opt/lab-classroom/class27/daemon.json >/dev/null && printf '%s\n' 'JSON syntax: valid'; else printf '%s\n' 'SKIP: neither jq nor python3 is available'; fi

### explanation
JSON parsing detects commas, quotation, braces, and structural errors before daemon-specific validation.
### step
6

### title
Perform daemon-specific validation when supported

### commands
if command -v dockerd >/dev/null 2>&1; then dockerd --validate --config-file /opt/lab-classroom/class27/daemon.json; else printf '%s\n' 'SKIP: dockerd is not installed'; fi

### explanation
The validation mode reads the staged file but does not start a daemon. If the installed release does not support a directive or validation mode, record the exact error instead of launching dockerd.
### step
7

### title
Confirm the lab boundary

### commands
find /opt/lab-classroom/class27/ -maxdepth 2 -printf '%y %p\n' | sort

### explanation
The listing provides an auditable view of the workspace created by the lab.

## Expected results

- The directory /opt/lab-classroom/class27/ exists with runtime, docker-data, and docker-exec subdirectories.
- host-inventory.txt identifies the kernel, architecture, and whether docker, dockerd, and containerd are present.
- installation-plan.txt records that package and service changes were not performed during the lab.
- daemon.json parses as valid JSON when jq or Python 3 is available.
- Daemon-specific validation succeeds when the installed dockerd version supports all staged directives, or the step reports a clear skip or compatibility error.
- No Docker daemon is started and no active system daemon configuration is changed.

## Verification checkpoints

- [ ] Run: test -d /opt/lab-classroom/class27/runtime && test -d /opt/lab-classroom/class27/docker-data && test -d /opt/lab-classroom/class27/docker-exec && echo PASS
- [ ] Run: test -s /opt/lab-classroom/class27/host-inventory.txt && echo PASS
- [ ] Run: test -s /opt/lab-classroom/class27/installation-plan.txt && echo PASS
- [ ] Run: grep -F 'Package and service changes executed in this lab: no' /opt/lab-classroom/class27/installation-plan.txt
- [ ] Run: grep -F '"data-root": "/opt/lab-classroom/class27/docker-data"' /opt/lab-classroom/class27/daemon.json
- [ ] Run: grep -F '"log-driver": "local"' /opt/lab-classroom/class27/daemon.json
- [ ] Run: if command -v jq >/dev/null 2>&1; then jq -e '.hosts[0] == "unix:///opt/lab-classroom/class27/runtime/docker.sock" and .["log-opts"]["max-file"] == "3"' /opt/lab-classroom/class27/daemon.json; else python3 -m json.tool /opt/lab-classroom/class27/daemon.json >/dev/null; fi
- [ ] Confirm that no lab instruction installed packages, modified a system service, or started dockerd.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Creating /opt/lab-classroom/class27/ fails with permission denied. | The current user does not have permission to create directories under /opt/lab-classroom. | Have an administrator pre-create /opt/lab-classroom/class27/ and assign appropriate ownership for the learner. Do not redirect the lab to unrelated system paths. |
| The JSON parser reports an error. | A quote, comma, brace, or value was changed while creating daemon.json. | Compare the file with the staged configuration in the lab, correct only /opt/lab-classroom/class27/daemon.json, and rerun syntax validation. |
| dockerd reports that --validate is unknown. | The installed Docker daemon is older or packaged without the expected validation behavior. | Record the installed version, retain the successful generic JSON validation, and consult the documentation matching that exact release. Do not start a second daemon as a substitute. |
| dockerd validation reports a duplicated hosts option. | The active service definition may already pass a hosts argument, and the daemon rejects settings supplied through both startup arguments and configuration. | For a future approved deployment, choose one authoritative location for the hosts setting and test the change in a maintenance window. Do not alter the active service during this lab. |
| The Docker CLI exists but reports that it cannot connect to the daemon. | The daemon may be absent, stopped, using a different context or socket, or inaccessible to the user. | Inspect the selected Docker context, expected endpoint, daemon service status, and user authorization. Do not assume that reinstalling the client will repair a daemon connectivity problem. |
| Docker commands return permission denied for the API socket. | The current user is not authorized to access the rootful daemon socket. | Use the organization's approved administrative workflow. Treat daemon access as privileged and do not broaden socket permissions as a shortcut. |
| A real daemon fails after a configuration change. | The file may contain unsupported settings, conflicting startup arguments, inaccessible paths, or storage configuration incompatible with the host. | Review the earliest daemon log error, restore the last known-good configuration using the prepared rollback procedure, validate it, and then restart only within the approved change window. |
| Images or containers appear missing after changing data-root. | The daemon is reading a different storage location rather than the original Docker state. | Stop further changes, identify the previous data root, and follow a tested migration or rollback plan. Do not copy active Docker state while the daemon is writing to it. |

## Security considerations

### principles
Treat control of a rootful Docker daemon as administrative control of the host.
Grant local daemon access only to identities that are authorized for host-level administration.
Do not expose an unauthenticated or unencrypted daemon API to a network.
Verify repository provenance, signing configuration, operating-system support, and package architecture before installation.
Pin or otherwise control versions when reproducible deployments are required.
Use bounded logging and monitor both the Docker data filesystem and the host log filesystem.
Prefer minimal container privileges, read-only filesystems where practical, explicit mounts, and narrowly scoped capabilities.
Review third-party images, use trusted registries, and track image digests or approved tags according to policy.
Keep secrets out of daemon configuration, image layers, command history, and ordinary environment files.
Back up application data according to the storage system's consistency requirements; image caches are not substitutes for backups.

### socket_warning
Possession of the Docker API socket can allow an operator or process to create highly privileged containers, mount host filesystems, and control workloads. Filesystem permissions around the socket are a security boundary, not a convenience setting.

### rootless_note
Rootless mode can reduce exposure to a privileged system daemon, but it does not eliminate container security risks and may have networking, storage, resource-management, or port-binding differences.

## Rollback

### lab_rollback
Remove only the class workspace through the classroom's approved cleanup process. The lab does not provide a destructive cleanup command because preserving the files may be useful for review and no system configuration was changed.

### real_installation_rollback_plan
Record current package versions, service state, active daemon configuration, Docker data root, and storage driver before making changes.
Back up configuration files and application data using methods appropriate to the workload.
Keep the previously approved package version available when organizational policy and repository retention permit.
If a new daemon configuration prevents startup, restore the last known-good configuration, validate it, and restart the service in the maintenance window.
Do not delete the Docker data root as an uninstall shortcut; it may contain persistent application volumes and other required state.
Verify daemon health, expected containers, networks, volumes, logs, and application functionality after rollback.

### success_criteria
Rollback is complete only when the intended daemon version and configuration are restored, the daemon is healthy, expected workloads and persistent data are available, and monitoring shows no continuing storage or connectivity errors.

## Video narration notes

Welcome to Class 27, Docker Engine Installation and Daemon Fundamentals. Begin with the most important distinction: the docker command and the Docker daemon are not the same program. The command-line client prepares an API request. A daemon, which may be local or remote, receives that request and coordinates the work. On a typical Linux host, the client communicates with dockerd through a Unix socket. dockerd manages the higher-level Docker model, including images, containers, networks, and volumes. It delegates lifecycle operations to containerd, which uses an OCI runtime to create the isolated process.

This architecture explains several common failures. If the client exists but the daemon is not installed or running, commands cannot create containers. If the client points to the wrong context, it may contact an unexpected endpoint. If the user cannot access the socket, the daemon can be healthy while commands still fail. Reinstalling the client does not correct these daemon, endpoint, or authorization problems.

Installation method matters. A vendor-maintained package repository usually supplies a documented upgrade path, while a distribution repository may provide different versions and integration choices. Static binaries transfer more lifecycle responsibility to the operator. Rootless mode changes the privilege model but also introduces platform requirements and operational differences. Whichever method you choose, verify operating-system support, CPU architecture, package provenance, target version, and rollback steps before touching the host.

The daemon is commonly supervised by the operating system's service manager. The service manager launches it and records output, but a successful package installation does not guarantee a successful daemon start. Invalid JSON, duplicate options, inaccessible paths, storage problems, or an occupied socket can all block startup. Read the first meaningful daemon error rather than repeatedly retrying.

In the lab, we respect a strict mutation boundary. We do not install packages, start services, or alter active Docker settings. We create a workspace under /opt/lab-classroom/class27, inventory available components, document an installation decision, and stage a daemon configuration. The configuration places its data root, execution root, process file, and socket under the workspace. It also demonstrates bounded local logging and live restore. First validate the file as JSON. If dockerd is already installed and supports validation mode, ask it to validate the staged configuration without starting a daemon.

Finally, remember that Docker API access is powerful. A user able to control a rootful daemon can often mount host paths or create privileged workloads. Treat socket authorization like administrator access, avoid unauthenticated network exposure, and use authenticated, encrypted remote-management designs. Before any production installation or upgrade, document current state, back up required application data, test the configuration, define rollback criteria, and schedule an appropriate maintenance window.

## References

- Docker Engine installation documentation: https://docs.docker.com/engine/install/
- Docker daemon configuration documentation: https://docs.docker.com/engine/daemon/
- Docker daemon command reference: https://docs.docker.com/reference/cli/dockerd/
- Docker Linux post-installation documentation: https://docs.docker.com/engine/install/linux-postinstall/
- Docker rootless mode documentation: https://docs.docker.com/engine/security/rootless/
- Docker logging configuration documentation: https://docs.docker.com/engine/logging/configure/
- Docker storage driver documentation: https://docs.docker.com/engine/storage/drivers/
- Docker security documentation: https://docs.docker.com/engine/security/
- containerd project documentation: https://containerd.io/
- Open Container Initiative runtime specification: https://github.com/opencontainers/runtime-spec

## Mastery gate

- [ ] Objectives demonstrated with evidence
- [ ] Feynman complete
- [ ] Quiz self-scored ≥80%
- [ ] Lab verification boxes checked
- [ ] Rollback understood

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Return to this class whenever a later service fails for identity, process, log, remote access, update, or routing reasons covered here.

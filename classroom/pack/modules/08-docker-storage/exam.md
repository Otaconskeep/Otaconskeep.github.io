# Module 8 exam

The module exam below is the authored Module 8 completion document.

# Module 8 Completion: Docker, Storage & Permissions

## Module Purpose

Move learners from installing Docker Engine to operating containers with controlled images, bounded resources, durable data, understood Linux storage, reliable mounts, and intentional file permissions.

## Module Objectives

By the end of Classes 27–33, learners can:

1. Trace a request from the Docker CLI through the daemon and runtime.
2. distinguish image tags from immutable digests and record provenance evidence.
3. Control container lifecycle, signals, restart behavior, CPU, memory, and PID limits.
4. Select named volumes or bind mounts based on ownership, portability, backup, and security needs.
5. Explain the disk → partition → filesystem → mount hierarchy without experimenting on a physical disk.
6. Stage and validate an `fstab` entry using UUIDs without altering boot configuration.
7. Diagnose container file-access failures using UID, GID, mode bits, ACLs, and mount properties.
8. Back up, verify, restore, and roll back the state created in the module labs.

## Required Reading

- Docker images: https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/
- Docker image digests: https://docs.docker.com/dhi/core-concepts/digests/
- Docker resource constraints: https://docs.docker.com/engine/containers/resource_constraints/
- Docker storage overview: https://docs.docker.com/engine/storage/
- Docker volumes: https://docs.docker.com/engine/storage/volumes/
- Docker bind mounts: https://docs.docker.com/engine/storage/bind-mounts/
- Linux `lsblk`: https://man7.org/linux/man-pages/man8/lsblk.8.html
- Linux `findmnt`: https://man7.org/linux/man-pages/man8/findmnt.8.html
- Linux `fstab`: https://man7.org/linux/man-pages/man5/fstab.5.html
- Linux ACLs: https://man7.org/linux/man-pages/man5/acl.5.html

## Homework / Lab

Create an operator evidence folder containing:

- An image inventory with tag, image ID, labels, and digest when available.
- A container inspection showing explicit memory and PID limits.
- A named-volume backup archive and a verified restore.
- A read-only block-device and mount inventory.
- A staged `fstab` entry that passes available syntax verification.
- A numeric UID/GID permission test with expected success and expected denial.
- A one-page rollback plan covering every state-changing exercise.

Do not include secrets, registry tokens, private image names, public IP addresses, or host-specific personal paths.

## Module Quiz

Target: 10/12 correct. Missed objectives route to remediation before a second attempt.

1. Why is a Docker tag insufficient as immutable provenance evidence?
2. What does an image digest identify?
3. Why should containers receive explicit resource limits in a shared homelab?
4. What is the operational difference between `docker stop` and `docker kill` with its default signal?
5. When is a named volume normally preferable to a bind mount?
6. What additional host exposure does a bind mount create?
7. Put these in order: mount, disk, filesystem, partition.
8. Why is filesystem free space not the same as physical-disk health?
9. Why are UUID-based `fstab` entries often safer than `/dev/sdX` names?
10. What should be done before running `mount -a` against production `fstab` changes?
11. Why can a container process receive `Permission denied` even when the path exists?
12. What problem can a default ACL solve?

## Answer Key

1. Tags are mutable references and can be reassigned to different manifests.
2. A digest identifies content through a cryptographic hash of the referenced manifest.
3. Limits prevent one workload from exhausting memory, CPU scheduling, or process capacity needed by others.
4. `stop` requests graceful termination and later forces termination; default `kill` sends immediate `SIGKILL`.
5. When Docker-managed, portable persistent storage is desired without coupling to a specific host path.
6. The container can access the selected host path, subject to mount mode and kernel enforcement; a bad path or broad mount increases host-data risk.
7. Disk → partition → filesystem → mount.
8. Free space describes filesystem allocation; disk health concerns the underlying device and its error/failure signals.
9. UUIDs identify the intended filesystem more consistently when kernel device names change.
10. Back up the current file, stage the edit, validate syntax and targets, and plan recovery for a boot or mount failure.
11. The process UID/GID, mode bits, ACL, mount flags, or security policy may not permit the requested operation.
12. It automatically grants defined permissions to new children created inside a directory.

## Module Project

### Durable Container Storage Blueprint

Design a small self-hosted service with one stateless container and one persistent data location. Deliver:

1. An image provenance record containing registry, repository, tag, digest policy, and update policy.
2. A Compose-style service design with explicit memory and PID limits.
3. A decision record choosing a named volume or bind mount.
4. A backup and restore procedure with a verification hash.
5. A host storage map from device to filesystem to mountpoint.
6. A staged UUID-based mount entry if host-managed storage is used.
7. A numeric UID/GID and ACL plan.
8. Security boundaries, monitoring signals, failure modes, and rollback steps.

The project may use a disposable VM or remain a reviewed design. Do not expose a new service publicly as part of the assessment.

## Module Exam

### Part A: Concepts (30 points)

- Explain tag versus digest and the provenance consequence. (10)
- Explain writable layer versus persistent mount. (10)
- Explain UID/GID evaluation for a bind-mounted path. (10)

### Part B: Diagnosis (30 points)

Given a container that restarts, exceeds memory, and cannot write to `/config`, identify evidence commands, likely causes, and a safe repair sequence.

### Part C: Practical evidence (40 points)

- Image inspection and recorded identity: 8
- Bounded container configuration: 8
- Volume backup and verified restore: 8
- Staged mount validation: 8
- Permission and rollback evidence: 8

## Passing Criteria and Rubric

- Pass: at least 80/100 overall.
- Safety gate: no credit for a practical step that targets an unverified physical disk, edits live `fstab` without staging, exposes the Docker socket, or uses a broad destructive deletion.
- Mastery: at least 80%, completed project evidence, successful Feynman explanation, and all rollback questions answered.

## Remediation

| Missed skill | Return to | Required retry evidence |
|---|---|---|
| Image identity/provenance | Class 28 | Explain tag vs digest using one inspected image |
| Lifecycle/resources | Class 29 | Interpret one bounded container inspection |
| Persistent storage | Class 30 | Restore and hash-check one named-volume backup |
| Disk/filesystem model | Class 31 | Label a disk/partition/filesystem/mount diagram |
| Mount persistence | Class 32 | Validate a staged UUID entry without editing `/etc/fstab` |
| Permissions | Class 33 | Predict and verify one allowed and one denied write |

After remediation, retake only the affected quiz objectives, then repeat the integrated explanation below.

## Final Feynman Explanation

Explain to a new homelab operator how an approved image becomes a bounded container whose data survives replacement on a known filesystem and remains writable only to the intended numeric identity. Use plain language and include one failure and rollback example.

## Course Reflection

1. Which hidden dependency, image identity, resources, storage, mounts, or permissions, was easiest to overlook?
2. Which verification step would have prevented a failure you have previously experienced?
3. What will you standardize in future Compose files?

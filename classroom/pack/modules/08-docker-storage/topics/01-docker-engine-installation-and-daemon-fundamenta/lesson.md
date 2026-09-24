# Lesson 08.01: Docker Engine Installation and Daemon Fundamentals

**Module:** Docker, Storage & Permissions
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the responsibilities of the Docker CLI, Docker daemon, containerd, and OCI runtime
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-28

## Learning objective

Explain the responsibilities of the Docker CLI, Docker daemon, containerd, and OCI runtime

## Why this matters

Teach learners how Docker Engine is packaged, installed, started, configured, and verified while distinguishing the Docker client, daemon, API socket, container runtime, image store, and service manager. The lab safely stages and validates daemon configuration without changing the host package database, system service configuration, or any path outside the class workspace.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

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

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain |
| 3 | [Lab](./lab.md) | Practice |
| 4 | [Homework](./homework.md) | Apply |
| 5 | [Quiz](./quiz.md) | Test |

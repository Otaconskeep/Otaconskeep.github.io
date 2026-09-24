# Reading: Health Checks, Dependencies, and Restart Policies

**Module:** ARR Data Model & Compose
**Activity type:** Reading (Learn)
**Objective:** Explain why a running process is not necessarily a healthy or ready service

## Vocabulary

| Term | Meaning |
|---|---|
| health check | A repeatable test that evaluates a defined aspect of a service and returns a result suitable for automation. |
| startup check | A check used to determine whether an application has completed initialization. It protects slow-starting services from premature liveness failures. |
| liveness check | A check that answers whether a service process is functioning sufficiently to remain running. Repeated liveness failure may justify a restart. |
| readiness check | A check that answers whether a service can currently accept useful traffic. Readiness failure should normally remove traffic without automatically restarting the process. |
| dependency | A service, file, network endpoint, credential, or other resource required for another service to start or provide useful work. |
| dependency ordering | A rule controlling which component is started first. Ordering alone does not prove that the earlier component is ready. |
| restart policy | A rule specifying whether and under what conditions a supervisor should start a process again after it exits. |
| restart loop | A repeated cycle in which a service starts, fails, and is immediately restarted without resolving the underlying fault. |
| backoff | An increasing or fixed delay between retries that reduces resource pressure and gives dependencies time to recover. |
| grace period | A period during startup or shutdown in which normal health expectations are temporarily relaxed. |
| fail open | A design choice that permits traffic or operation when a check cannot confirm health. |
| fail closed | A design choice that refuses traffic or operation when a check cannot confirm health. |

## Instruction

A process being present only proves that the operating system has not observed it exit. The process may be deadlocked, unable to reach its database, serving stale data, or still performing initialization. Reliable operations therefore separate startup, liveness, and readiness. A startup check allows a slow application time to initialize. A liveness check should test an internal condition that indicates whether restarting could help. A readiness check should test whether the instance can perform useful work now, including critical dependency access when appropriate. Readiness can change repeatedly during the lifetime of a process and should usually control traffic rather than process replacement.

Dependencies introduce another distinction: start order is not readiness. Starting a database before an application does not guarantee that the database has opened its sockets, completed recovery, applied migrations, or accepted credentials. A dependent application should use bounded connection attempts, explicit timeouts, and backoff. Orchestrator dependency conditions can improve initial sequencing, but applications still need runtime resilience because dependencies may fail after startup.

Restart policies are recovery tools, not substitutes for diagnosis. An on-failure policy is useful when a nonzero process exit may be transient. An always-style policy can be appropriate for appliance-like services, but it can also restart intentionally stopped workloads unless the supervisor distinguishes operator action. A no-restart policy is often best for one-shot jobs, migrations, and failures requiring human review. Every restart policy should be paired with logs, rate limits, and an alert for repeated failures. Immediate retries can overload storage, DNS, authentication services, or remote APIs. Backoff and retry ceilings reduce that risk.

Health checks should be narrowly scoped, inexpensive, deterministic, and protected by short timeouts. A check that performs a costly full transaction every few seconds can become its own denial-of-service source. Conversely, a check that only confirms an HTTP listener may report success even when the application cannot do useful work. Operators should document what each check proves, what it does not prove, how often it runs, and what automation consumes its result. The safest design connects each failure signal to a proportionate action: stop routing traffic for readiness failure, restart only for credible liveness failure, and escalate persistent or repeated failures to a human.

## Architecture

### scope
All persistent lab files are created beneath /opt/lab-classroom/class37/. The services listen only on the loopback interface.

### components
A dependency service on 127.0.0.1:18370 with separate liveness and readiness endpoints
An application service on 127.0.0.1:18371 whose readiness depends on the dependency service
A small Python supervisor that waits for dependency readiness and restarts the application after a nonzero exit
Log and PID files stored under /opt/lab-classroom/class37/

### request_flow
A client requests the application. The application liveness endpoint reports whether its own HTTP process can respond. Its readiness endpoint performs a short, bounded request to the dependency readiness endpoint. If the dependency is unavailable or unready, the application returns HTTP 503 while remaining live.

### failure_flow
The controlled /crash endpoint makes the application exit with status 17. The supervisor records the exit, waits two seconds, and starts a replacement application process. This models an on-failure restart with fixed backoff.

### boundaries
The exercise does not install packages, modify system service definitions, alter firewall policy, or write outside the designated class directory.

## Required reading

- Docker documentation: Start containers automatically at https://docs.docker.com/engine/containers/start-containers-automatically/
- Docker Compose documentation: Control startup and shutdown order in Compose at https://docs.docker.com/compose/how-tos/startup-order/
- Kubernetes documentation: Configure liveness, readiness and startup probes at https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
- systemd.service manual sections covering Restart= and RestartSec= at https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html

## References

- Docker Engine documentation, Start containers automatically: https://docs.docker.com/engine/containers/start-containers-automatically/
- Docker Compose documentation, Control startup and shutdown order: https://docs.docker.com/compose/how-tos/startup-order/
- Docker Compose file reference, depends_on: https://docs.docker.com/reference/compose-file/services/#depends_on
- Docker Compose file reference, healthcheck: https://docs.docker.com/reference/compose-file/services/#healthcheck
- Kubernetes documentation, Configure liveness, readiness and startup probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
- systemd.service manual: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
- RFC 9110, HTTP Semantics: https://www.rfc-editor.org/rfc/rfc9110

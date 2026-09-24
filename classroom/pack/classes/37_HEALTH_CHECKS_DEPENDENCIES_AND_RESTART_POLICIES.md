# Class 37: Health Checks, Dependencies, and Restart Policies

**Learning objective:** Explain why a running process is not necessarily a healthy or ready service; Differentiate startup, liveness, and readiness checks; Describe what dependency ordering can and cannot guarantee; Select an appropriate restart policy for expected failure modes; Identify restart loops, dependency failures, and overly aggressive health checks from logs; Verify recovery behavior by introducing a controlled application failure; Apply bounded retries, timeouts, and backoff concepts to reduce cascading failures
**Bloom level:** Understand / Apply
**Track:** Homelab Operations and Reliability · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach operators to distinguish process state from service health, model startup and runtime dependencies, and apply bounded restart behavior without creating restart loops or hiding real failures.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-20
**Compatibility:** ### operating_systems
Linux distributions with Python 3.8 or newer
A Linux virtual machine or homelab host where the designated directory is writable

### required_software
POSIX-compatible shell
Python 3 standard library
Standard utilities including mkdir, cat, sleep, tail, find, test, and kill

### network
Requires free loopback TCP ports 18370 and 18371. No Internet access is required for the lab.

### container_runtime
Not required. The concepts map to Docker Compose, Kubernetes, systemd, and other supervisors, but the lab avoids runtime-specific host changes.

### known_limitations
The teaching supervisor is intentionally minimal and is not a replacement for a production init system or orchestrator.
The supervisor uses fixed two-second restart delays rather than exponential backoff.
The supervisor does not implement production-grade restart-rate limiting or durable state.
The health checks use local HTTP and do not demonstrate TLS, authentication, or distributed network failure modes.

## Learning objective

- Explain why a running process is not necessarily a healthy or ready service
- Differentiate startup, liveness, and readiness checks
- Describe what dependency ordering can and cannot guarantee
- Select an appropriate restart policy for expected failure modes
- Identify restart loops, dependency failures, and overly aggressive health checks from logs
- Verify recovery behavior by introducing a controlled application failure
- Apply bounded retries, timeouts, and backoff concepts to reduce cascading failures

## Why this matters

Teach operators to distinguish process state from service health, model startup and runtime dependencies, and apply bounded restart behavior without creating restart loops or hiding real failures.

## Prerequisites

- Comfort using a Linux shell and reading process logs
- Basic understanding of TCP ports, HTTP status codes, and local services
- Ability to run Python 3 from a terminal
- Write access to /opt/lab-classroom/class37/
- Completion of earlier service-management or container fundamentals lessons is recommended

## Required reading

- Docker documentation: Start containers automatically at https://docs.docker.com/engine/containers/start-containers-automatically/
- Docker Compose documentation: Control startup and shutdown order in Compose at https://docs.docker.com/compose/how-tos/startup-order/
- Kubernetes documentation: Configure liveness, readiness and startup probes at https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
- systemd.service manual sections covering Restart= and RestartSec= at https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

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

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Modify only the lab copy of supervisor.py to use exponential backoff capped at 16 seconds. Record the delay sequence in a log and explain why a cap is necessary.
Add a maximum of three application restarts within a 60-second window. After the limit is reached, leave the service stopped and emit an explicit operator-action message.
Temporarily change READY_AFTER in dependency.py to 35 seconds and predict the supervisor result before running it. Compare the observed behavior with the 30-second readiness deadline.
Design health checks for a reverse proxy, DNS resolver, database, and backup job. For each, state what startup, liveness, and readiness mean and identify cases where one check is not applicable.
Write a short policy describing when your homelab uses no restart, on-failure restart, or always restart behavior. Include logging, retry limits, and alert thresholds.

## Feynman teach-back

### prompt
Explain the lesson to a new operator using a restaurant analogy.

### model_explanation
A process is like a restaurant building with the lights on. Liveness asks whether staff are present and able to respond. Readiness asks whether the kitchen can actually serve customers now. A food delivery service is a dependency: opening the restaurant after the delivery truck arrives does not guarantee ingredients were unloaded and checked. A restart policy is like sending the manager home and bringing in a replacement when the manager fails. That may help after a temporary problem, but repeatedly replacing managers will not fix an empty pantry. Traffic should be paused when the restaurant is unready, while restarts should be reserved for failures that a fresh process can plausibly correct.

### self_check
If your explanation treats process existence, readiness, and liveness as the same condition, revise it until each signal has a distinct meaning and response.

## Retrieval check

1. What is the operational difference between liveness and readiness?
2. Why is dependency start order insufficient to guarantee that an application can use the dependency?
3. When is an on-failure restart policy generally more appropriate than an always restart policy?
4. What action should normally follow a readiness failure when the process remains live?
5. Why should health checks use explicit, short timeouts?
6. What is a restart loop, and why can it harm other services?
7. In the lab, what evidence proves that the application was restarted rather than merely recovering inside the same process?
8. Why is the lab's /crash endpoint unacceptable as an unauthenticated production endpoint?

## Guided lab

### name
Observe readiness gating and a controlled on-failure restart

### environment_notes
Run the commands from a shell with Python 3 available.
Ports 18370 and 18371 must be unused on the local machine.
Do not change ROOT in the scripts; the fixed path enforces the lab boundary.
The lab creates local processes rather than system services or containers.

### steps
### step
1

### title
Create the isolated lab directory

### commands
mkdir -p /opt/lab-classroom/class37
cd /opt/lab-classroom/class37
pwd

### explanation
The printed working directory must be /opt/lab-classroom/class37. All subsequent generated files and logs remain under this directory.
### step
2

### title
Create a dependency with distinct liveness and readiness behavior

### commands
cat > /opt/lab-classroom/class37/dependency.py <<'PY'
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STARTED = time.monotonic()
READY_AFTER = 8.0

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        age = time.monotonic() - STARTED
        if self.path == '/live':
            self.reply(200, {'live': True, 'age_seconds': round(age, 2)})
        elif self.path == '/ready':
            ready = age >= READY_AFTER
            self.reply(200 if ready else 503, {'ready': ready, 'age_seconds': round(age, 2)})
        else:
            self.reply(404, {'error': 'not found'})

    def log_message(self, format, *args):
        print('dependency:', format % args, flush=True)

ThreadingHTTPServer(('127.0.0.1', 18370), Handler).serve_forever()
PY

### explanation
The dependency becomes live as soon as it can answer HTTP, but deliberately remains unready for its first eight seconds.
### step
3

### title
Create an application whose readiness includes a bounded dependency check

### commands
cat > /opt/lab-classroom/class37/application.py <<'PY'
import json
import os
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STARTED = time.monotonic()

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def dependency_ready(self):
        try:
            with urllib.request.urlopen('http://127.0.0.1:18370/ready', timeout=0.5) as response:
                return response.status == 200
        except (urllib.error.URLError, TimeoutError):
            return False

    def do_GET(self):
        if self.path == '/live':
            self.reply(200, {'live': True, 'pid': os.getpid()})
        elif self.path == '/ready':
            ready = self.dependency_ready()
            self.reply(200 if ready else 503, {'ready': ready, 'pid': os.getpid()})
        elif self.path == '/crash':
            self.reply(200, {'message': 'controlled failure requested', 'pid': os.getpid()})
            self.wfile.flush()
            os._exit(17)
        else:
            self.reply(404, {'error': 'not found'})

    def log_message(self, format, *args):
        print('application:', format % args, flush=True)

ThreadingHTTPServer(('127.0.0.1', 18371), Handler).serve_forever()
PY

### explanation
The readiness request has a 0.5-second timeout. A missing, slow, or unready dependency produces HTTP 503 without declaring the application process dead.
### step
4

### title
Create a supervisor with readiness gating and a restart delay

### commands
cat > /opt/lab-classroom/class37/supervisor.py <<'PY'
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = '/opt/lab-classroom/class37'
RUNNING = True
children = {}

def record(message):
    print(time.strftime('%Y-%m-%dT%H:%M:%S'), message, flush=True)

def start(name, script, log_name):
    log_path = os.path.join(ROOT, log_name)
    log = open(log_path, 'ab', buffering=0)
    process = subprocess.Popen(
        [sys.executable, '-B', os.path.join(ROOT, script)],
        cwd=ROOT,
        stdout=log,
        stderr=subprocess.STDOUT
    )
    children[name] = (process, log)
    record(f'started {name} pid={process.pid}')
    return process

def wait_for_dependency(timeout=30):
    deadline = time.monotonic() + timeout
    while RUNNING and time.monotonic() < deadline:
        try:
            with urllib.request.urlopen('http://127.0.0.1:18370/ready', timeout=0.5) as response:
                if response.status == 200:
                    record('dependency is ready')
                    return True
        except (urllib.error.URLError, TimeoutError):
            pass
        record('dependency not ready; retrying in 1 second')
        time.sleep(1)
    return False

def stop_all(signum=None, frame=None):
    global RUNNING
    RUNNING = False
    record('shutdown requested')

signal.signal(signal.SIGTERM, stop_all)
signal.signal(signal.SIGINT, stop_all)

dependency = start('dependency', 'dependency.py', 'dependency.log')
application = None

if wait_for_dependency():
    application = start('application', 'application.py', 'application.log')
else:
    record('dependency readiness deadline exceeded; application not started')

try:
    while RUNNING:
        if dependency.poll() is not None:
            record(f'dependency exited status={dependency.returncode}; restarting in 2 seconds')
            time.sleep(2)
            dependency = start('dependency', 'dependency.py', 'dependency.log')
        if application is not None and application.poll() is not None:
            status = application.returncode
            record(f'application exited status={status}')
            if status != 0:
                record('on-failure policy selected; restarting application in 2 seconds')
                time.sleep(2)
                application = start('application', 'application.py', 'application.log')
            else:
                record('clean application exit; no restart')
                application = None
        time.sleep(0.5)
finally:
    for name, item in list(children.items()):
        process, log = item
        if process.poll() is None:
            process.terminate()
    deadline = time.monotonic() + 5
    for name, item in list(children.items()):
        process, log = item
        remaining = max(0.0, deadline - time.monotonic())
        try:
            process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        log.close()
    record('supervisor stopped')
PY

### explanation
The supervisor starts the dependency first, polls readiness with a deadline, and only then starts the application. A failed application receives a two-second delay before restart.
### step
5

### title
Start the lab and observe dependency readiness gating

### commands
cd /opt/lab-classroom/class37 && nohup python3 -B supervisor.py > supervisor.log 2>&1 & echo $! > /opt/lab-classroom/class37/supervisor.pid
sleep 2
cat /opt/lab-classroom/class37/supervisor.log
sleep 8
cat /opt/lab-classroom/class37/supervisor.log

### explanation
The first log view should show readiness retries. The later view should show that the dependency became ready and that the application was then started.
### step
6

### title
Verify liveness and readiness

### commands
python3 -B -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:18370/live', timeout=1).read().decode())"
python3 -B -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:18370/ready', timeout=1).read().decode())"
python3 -B -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:18371/live', timeout=1).read().decode())"
python3 -B -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:18371/ready', timeout=1).read().decode())"

### explanation
All four requests should return JSON. The application readiness response proves both that the application can answer and that its dependency is ready.
### step
7

### title
Trigger a controlled failure and observe the restart policy

### commands
python3 -B -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:18371/live', timeout=1).read().decode())"
python3 -B -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:18371/crash', timeout=1).read().decode())"
sleep 3
tail -n 12 /opt/lab-classroom/class37/supervisor.log
python3 -B -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:18371/live', timeout=1).read().decode())"

### explanation
Compare the application PID before and after the failure. The replacement should have a different PID, and the supervisor log should contain exit status 17 followed by an on-failure restart message.
### step
8

### title
Stop the isolated lab

### commands
kill "$(cat /opt/lab-classroom/class37/supervisor.pid)"
sleep 2
tail -n 8 /opt/lab-classroom/class37/supervisor.log

### explanation
The supervisor handles the termination signal, stops its child processes, closes its logs, and records a final stopped message.

## Expected results

- The supervisor log initially reports that the dependency is not ready and retries at one-second intervals.
- The application is not started until the dependency returns a successful readiness response.
- The dependency and application liveness endpoints return HTTP 200 while their processes can serve requests.
- The application readiness endpoint returns HTTP 200 when the dependency readiness endpoint is successful.
- Requesting the controlled crash endpoint causes the application to exit with status 17.
- The supervisor waits approximately two seconds and starts a replacement application process with a different PID.
- Stopping the supervisor also stops the child services and leaves the generated files only under /opt/lab-classroom/class37/.

## Verification checkpoints

- [ ] Run `cat /opt/lab-classroom/class37/supervisor.log` and confirm that dependency readiness retries occur before the first application start message.
- [ ] Run `python3 -B -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:18371/ready', timeout=1).status)"` while the lab is running and confirm that it prints 200.
- [ ] Record the PID returned by the application /live endpoint, invoke /crash, wait three seconds, and confirm that the new /live response contains a different PID.
- [ ] Confirm that supervisor.log includes `application exited status=17` and `on-failure policy selected`.
- [ ] After shutdown, run `python3 -B -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:18371/live', timeout=1)"` and confirm that it fails to connect.
- [ ] Run `find /opt/lab-classroom/class37 -maxdepth 1 -type f -print` and confirm that the scripts, PID file, and logs are contained in the designated lab directory.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Python reports PermissionError while creating the lab directory or files. | The current account does not have write access to /opt/lab-classroom/. | Have the lab administrator pre-create /opt/lab-classroom/class37/ and grant the student account appropriate ownership. Do not redirect the exercise to an unapproved path. |
| The supervisor log shows Address already in use. | Another process is listening on port 18370 or 18371, or an earlier lab process is still running. | Check the recorded supervisor PID and stop that specific lab supervisor if it is still active. Do not terminate unrelated processes. If the PID is stale, ask the lab administrator to identify the listener before continuing. |
| The application never starts. | The dependency failed to bind, Python exited with a syntax error, or the readiness deadline expired. | Read supervisor.log and dependency.log. Correct only the files under /opt/lab-classroom/class37/, stop the current supervisor if present, and start the lab again. |
| The application readiness request returns HTTP 503. | The dependency is still initializing, unavailable, or returning an unsuccessful readiness result. | Query the dependency /live and /ready endpoints separately. Treat a live-but-unready dependency as an availability issue rather than immediately restarting the application. |
| The controlled crash request reports a disconnected or incomplete response. | The process exited before the client consumed the complete response body. | Inspect supervisor.log for exit status 17 and wait at least three seconds before querying /live again. The intended result is the process failure and supervised restart, not a guaranteed crash-response body. |
| The PID does not change after requesting /crash. | The request did not reach the application, the old PID was not recorded, or the restart had not completed. | Check application.log and supervisor.log, wait for the restart message, and then query /live again. |
| Repeated application restarts appear in the log. | The application has a persistent startup fault or cannot bind its port, so restarting cannot resolve the failure. | Stop the supervisor to break the loop, inspect application.log, correct the persistent cause, and restart only after verification. In production, add retry ceilings and alerting. |
| The shutdown command says there is no such process. | The supervisor already exited or supervisor.pid is stale. | Read supervisor.log for the final state. Verify the exact PID before taking any further action and do not issue broad process-kill commands. |

## Security considerations

### principles
Health endpoints can reveal version, dependency, topology, and failure information. Expose only the minimum response required by the health consumer.
Bind administrative health endpoints to a management network or loopback interface unless remote access is explicitly required.
Do not place credentials, tokens, connection strings, stack traces, or customer data in health responses.
Use short timeouts so a health check cannot accumulate blocked workers or connections.
Rate-limit externally reachable checks and ensure monitoring cannot become a denial-of-service source.
Treat a health check as an input to automation. Authenticate and authorize any endpoint that changes state, such as the lab's controlled crash endpoint.
The /crash endpoint in this exercise is intentionally unauthenticated only because it is bound to loopback in an isolated lab. It must not be copied into a production service.
Restart policies should run services with least privilege and should not repeatedly execute unsafe initialization or migration operations.

### lab_controls
Both HTTP servers bind only to 127.0.0.1. The scripts use fixed paths, fixed local ports, explicit network timeouts, and no external dependencies. The only state-changing HTTP endpoint affects the disposable application process.

## Rollback

### goal
Stop all lab processes while preserving files and logs for review.

### commands
test -f /opt/lab-classroom/class37/supervisor.pid && kill "$(cat /opt/lab-classroom/class37/supervisor.pid)"
sleep 2
tail -n 20 /opt/lab-classroom/class37/supervisor.log

### verification
Confirm that supervisor.log ends with `supervisor stopped` and that requests to ports 18370 and 18371 no longer connect.

### data_retention
The rollback intentionally retains scripts and logs under /opt/lab-classroom/class37/. No files outside that directory are created or removed by the lesson.

### recovery_note
If the supervisor is already absent, do not use broad process matching. Ask the lab administrator to identify any remaining listener by exact PID and command line.

## Video narration notes

In this class, we separate four ideas that are often incorrectly collapsed into one: process state, startup completion, liveness, and readiness. A process listed by the operating system may still be unable to serve useful traffic. Liveness asks whether keeping that process is sensible. Readiness asks whether traffic should be sent to it right now. Startup checks give slow applications time to initialize before normal liveness expectations apply.

Our lab models a service dependency with an eight-second initialization period. The dependency can answer its liveness endpoint immediately, but its readiness endpoint returns an unsuccessful status until initialization completes. The supervisor starts the dependency, polls readiness with a timeout, and starts the application only after readiness succeeds. This demonstrates why start order is not enough: a process can exist without being ready.

The application has its own liveness endpoint and a readiness endpoint that performs a bounded check against the dependency. If the dependency becomes unavailable, the application can remain alive while reporting that it is not ready for traffic. That distinction is important. Restarting an otherwise healthy application does not repair a failed database, DNS server, or identity provider.

Next, we request a controlled application failure. The application exits with status 17, and the supervisor applies an on-failure policy. It records the failure, waits two seconds, and launches a replacement. We compare process identifiers to confirm that replacement occurred. The delay is intentionally simple, but production systems should commonly use bounded exponential backoff, restart-rate limits, and alerting.

Finally, remember that health checks are part of the control plane. They must be cheap, predictable, minimally informative, and protected from abuse. A check that is too shallow can hide outages, while a check that is too expensive can create one. Match each signal to a proportionate response: gate startup with startup checks, remove traffic with readiness, restart only for credible liveness failures, and involve an operator when repeated retries show that automation is not fixing the cause.

## References

- Docker Engine documentation, Start containers automatically: https://docs.docker.com/engine/containers/start-containers-automatically/
- Docker Compose documentation, Control startup and shutdown order: https://docs.docker.com/compose/how-tos/startup-order/
- Docker Compose file reference, depends_on: https://docs.docker.com/reference/compose-file/services/#depends_on
- Docker Compose file reference, healthcheck: https://docs.docker.com/reference/compose-file/services/#healthcheck
- Kubernetes documentation, Configure liveness, readiness and startup probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
- systemd.service manual: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
- RFC 9110, HTTP Semantics: https://www.rfc-editor.org/rfc/rfc9110

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

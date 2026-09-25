# Class 46: Radarr Monitoring and Availability

**Learning objective:** Explain why a running Radarr process does not prove that movie automation is working; Differentiate process, port, HTTP, application, dependency, and workflow monitoring; Create a local availability probe with explicit latency and success criteria; Interpret HTTP failures, timeouts, slow responses, and partial dependency failures; Design alerts that are actionable and resistant to transient failures; Verify recovery after a simulated outage without modifying a production service
**Bloom level:** Understand / Apply
**Track:** Media Automation Operations · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach operators how to distinguish Radarr process availability, HTTP reachability, application health, dependency health, and end-to-end functionality. The lab builds a local Radarr-like service and an availability probe without changing a production Radarr installation.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** The lab is compatible with Linux systems that provide Python 3, a POSIX-compatible shell, loopback networking, and write access to /opt/lab-classroom/class46/. It does not depend on a particular Radarr release because it uses a local mock service. Production endpoint names and authentication behavior must be checked against the documentation for the deployed Radarr release.

## Learning objective

- Explain why a running Radarr process does not prove that movie automation is working
- Differentiate process, port, HTTP, application, dependency, and workflow monitoring
- Create a local availability probe with explicit latency and success criteria
- Interpret HTTP failures, timeouts, slow responses, and partial dependency failures
- Design alerts that are actionable and resistant to transient failures
- Verify recovery after a simulated outage without modifying a production service

## Why this matters

Teach operators how to distinguish Radarr process availability, HTTP reachability, application health, dependency health, and end-to-end functionality. The lab builds a local Radarr-like service and an availability probe without changing a production Radarr installation.

## Prerequisites

- Completion of introductory Radarr deployment and configuration lessons
- Basic familiarity with Linux processes, HTTP status codes, JSON, and shell commands
- Python 3 installed on the lab host
- Write access to /opt/lab-classroom/class46/
- TCP port 8787 available on the loopback interface

## Required reading

- Radarr Wiki: System and health-check documentation at https://wiki.servarr.com/radarr
- Prometheus documentation: Instrumentation practices at https://prometheus.io/docs/practices/instrumentation/
- IETF RFC 9110: HTTP Semantics at https://www.rfc-editor.org/rfc/rfc9110
- Python documentation: urllib.request at https://docs.python.org/3/library/urllib.request.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Availability | The proportion of intended observations during which a service satisfies a defined success condition. |
| Liveness | Evidence that a process or service is running and can respond at a basic level. |
| Readiness | Evidence that a service is prepared to perform useful work, including access to required dependencies. |
| Synthetic probe | An automated request that tests a service from the perspective of a client. |
| Dependency health | The operational state of systems Radarr relies on, such as indexers, download clients, storage, DNS, and databases. |
| Timeout | A client-defined limit after which an incomplete operation is treated as a failure. |
| Latency | The elapsed time between initiating a request and receiving its result. |
| False positive | An alert that reports an outage or defect when the monitored service is functioning acceptably. |
| End-to-end check | A test that validates a complete user or automation workflow rather than one isolated component. |

## Instruction

Monitoring Radarr requires more than checking whether its process exists. A process check only establishes that the operating system still has a Radarr process. A port check adds evidence that something is accepting connections, while an HTTP check confirms that an application-level response can be received. Even a successful HTTP response does not prove that Radarr can query an indexer, submit a download, import a completed file, write to the movie library, or reach its database and download client. Good monitoring therefore uses layers. The first layer checks host and process liveness. The second checks local HTTP reachability. The third evaluates Radarr health information and application logs. The fourth checks critical dependencies. The final layer verifies a safe end-to-end workflow or a close approximation of one.

Every availability measurement must define success. For this lesson, a probe succeeds when the local service returns HTTP 200 within the probe timeout. The lab also applies a 500 millisecond latency policy to demonstrate how a reachable service may still violate an operator-defined objective. This value is a classroom policy, not a universal Radarr performance benchmark. Production thresholds should be based on normal observed behavior, user impact, storage characteristics, network placement, and the frequency of the check.

A monitor should record enough context to explain a failure: observation time, target, HTTP status, elapsed time, exception category, and the number of successful attempts. Repeated attempts can reduce alerts caused by a single transient event, but retries also delay detection. Alert rules should generally require more than one failed observation and should include a recovery notification. Avoid hiding persistent defects behind unlimited retries.

Radarr may remain reachable while reporting degraded dependency health. An unavailable indexer can prevent searches, a failed download client can prevent queue submission, and an unwritable library path can prevent imports. These conditions should not all be labeled identically. Separate alerts allow an operator to route and prioritize incidents correctly. A local HTTP failure may justify an application availability alert, while one failed indexer may justify a dependency warning. An end-to-end import failure is more consequential because it proves the automation path is broken.

Monitor placement also matters. A probe running on the same host validates the application and loopback network path but cannot detect every reverse-proxy, DNS, routing, or client-network failure. A second probe from another trusted system tests more of the real access path. Production monitoring should avoid exposing administrative interfaces solely to make probing easier. Monitoring requests should use the least privilege available, protect authentication material outside scripts and reports, and prevent sensitive headers or query data from appearing in logs. The laboratory avoids those concerns by using an unauthenticated mock service bound only to 127.0.0.1.

## Architecture

The laboratory architecture consists of a Python mock service bound to 127.0.0.1:8787, a state file under /opt/lab-classroom/class46/, and a Python synthetic monitor. The mock service reads state.txt for each request. In the available state it returns HTTP 200 with a small JSON document. In the unavailable state it returns HTTP 503. In the slow state it delays the response before returning HTTP 200. The monitor performs three observations, records status and latency, calculates observed availability, writes report.json, and exits unsuccessfully if any observation fails or if the maximum observed latency exceeds the classroom policy. In production, the equivalent design would combine a host or container check, an HTTP probe, Radarr health observations, dependency checks for indexers and download clients, storage checks, and monitoring from a trusted remote location.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Add a fourth mock state named degraded that returns HTTP 200 with healthy set to false, then update the monitor to distinguish reachability from application health.
Extend the report with consecutive failure count logic stored in a file under /opt/lab-classroom/class46/.
Design an alert message containing the target, failure category, first observation time, latest status, and a concise operator action.
Draw a production monitoring plan that covers Radarr, its database, indexers, download clients, library storage, DNS, and reverse proxy.
Write a short policy explaining when a warning should escalate to a critical alert and when a recovery notification should be sent.

## Feynman teach-back

Explain the monitoring model to another learner using a restaurant analogy. A lit sign is like a running process: it suggests the business exists but proves little. An unlocked door is like an open TCP port. A host greeting you is like a successful HTTP response. A working kitchen, available ingredients, and functioning payment system represent Radarr dependencies. Receiving the meal you ordered represents an end-to-end automation check. Then explain why each layer can succeed while the next layer fails, and identify which alert would help the operator act on each failure.

## Retrieval check

1. Why is checking only the Radarr process insufficient to establish service availability?
2. What is the operational difference between liveness and readiness?
3. Why can an HTTP 200 response coexist with broken movie automation?
4. What does the lab monitor treat as a successful individual observation?
5. Why should production latency thresholds be based on local observations rather than copied from the classroom policy?
6. What additional failure paths can a trusted remote probe detect compared with a loopback-only probe?
7. Why should monitoring distinguish an indexer failure from complete Radarr HTTP unavailability?

## Guided lab

Create the isolated workspace and initial state. Run: mkdir -p /opt/lab-classroom/class46 && printf '%s\n' 'available' > /opt/lab-classroom/class46/state.txt
Create the mock service. Run: cat > /opt/lab-classroom/class46/mock_radarr.py <<'PY'
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path('/opt/lab-classroom/class46')
STATE_FILE = ROOT / 'state.txt'

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/ping':
            self.send_response(404)
            self.end_headers()
            return
        state = STATE_FILE.read_text(encoding='utf-8').strip()
        if state == 'slow':
            time.sleep(0.8)
        status = 503 if state == 'unavailable' else 200
        body = json.dumps({'service': 'radarr-lab', 'state': state, 'healthy': status == 200}).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

server = ThreadingHTTPServer(('127.0.0.1', 8787), Handler)
server.serve_forever()
PY
Create the synthetic monitor. Run: cat > /opt/lab-classroom/class46/monitor.py <<'PY'
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TARGET = 'http://127.0.0.1:8787/ping'
REPORT = Path('/opt/lab-classroom/class46/report.json')
TIMEOUT_SECONDS = 2
LATENCY_POLICY_MS = 500
checks = []

for attempt in range(1, 4):
    started = time.monotonic()
    status = None
    error = None
    try:
        with urllib.request.urlopen(TARGET, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        error = 'http_error'
    except Exception as exc:
        error = type(exc).__name__
    elapsed_ms = round((time.monotonic() - started) * 1000, 2)
    checks.append({'attempt': attempt, 'status': status, 'latency_ms': elapsed_ms, 'success': status == 200, 'error': error})
    time.sleep(0.1)

successes = sum(1 for item in checks if item['success'])
availability_percent = round((successes / len(checks)) * 100, 2)
maximum_latency_ms = max(item['latency_ms'] for item in checks)
report = {
    'observed_at': datetime.now(timezone.utc).isoformat(),
    'target': TARGET,
    'checks': checks,
    'availability_percent': availability_percent,
    'maximum_latency_ms': maximum_latency_ms,
    'latency_policy_ms': LATENCY_POLICY_MS,
    'healthy': successes == len(checks) and maximum_latency_ms <= LATENCY_POLICY_MS
}
REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['healthy'] else 1)
PY
Start the loopback-only mock service and record its process identifier inside the workspace. Run: cd /opt/lab-classroom/class46; python3 mock_radarr.py > server.log 2>&1 & service_pid=$!; printf '%s\n' "$service_pid" > /opt/lab-classroom/class46/server.pid
Confirm that the service process exists before probing it. Run: test -s /opt/lab-classroom/class46/server.pid && kill -0 "$(cat /opt/lab-classroom/class46/server.pid)"
Run the healthy baseline probe. Run: python3 /opt/lab-classroom/class46/monitor.py
Inspect the report using the Python JSON parser. Run: python3 -c "import json; p='/opt/lab-classroom/class46/report.json'; r=json.load(open(p, encoding='utf-8')); print('healthy=', r['healthy'], 'availability=', r['availability_percent'], 'max_latency_ms=', r['maximum_latency_ms'])"
Simulate an unavailable application and verify that the monitor detects it. Run: printf '%s\n' 'unavailable' > /opt/lab-classroom/class46/state.txt; python3 /opt/lab-classroom/class46/monitor.py; result=$?; printf 'monitor_exit=%s\n' "$result"; test "$result" -ne 0
Inspect the failed observations. Run: python3 -c "import json; r=json.load(open('/opt/lab-classroom/class46/report.json', encoding='utf-8')); print([(c['status'], c['success'], c['error']) for c in r['checks']])"
Simulate a service that is reachable but slower than the classroom policy. Run: printf '%s\n' 'slow' > /opt/lab-classroom/class46/state.txt; python3 /opt/lab-classroom/class46/monitor.py; result=$?; printf 'monitor_exit=%s\n' "$result"; test "$result" -ne 0
Restore the available state and confirm recovery. Run: printf '%s\n' 'available' > /opt/lab-classroom/class46/state.txt; python3 /opt/lab-classroom/class46/monitor.py
Confirm the final report is healthy and contains three successful observations. Run: python3 -c "import json; r=json.load(open('/opt/lab-classroom/class46/report.json', encoding='utf-8')); assert r['healthy'] is True; assert len(r['checks']) == 3; assert all(c['success'] for c in r['checks']); print('final verification passed')"

## Expected results

- The mock service listens only on 127.0.0.1:8787 and responds to the /ping path.
- The available state produces three HTTP 200 observations and a healthy report.
- The unavailable state produces HTTP 503 observations, zero successful checks, and a nonzero monitor exit status.
- The slow state remains HTTP-reachable but violates the 500 millisecond classroom latency policy and produces a nonzero monitor exit status.
- After recovery, report.json records three successful observations and healthy is true.
- All files created or modified by the lab remain under /opt/lab-classroom/class46/.

## Verification checkpoints

- [ ] Run test -s /opt/lab-classroom/class46/server.pid && kill -0 "$(cat /opt/lab-classroom/class46/server.pid)" to confirm that the recorded process is running.
- [ ] Run python3 -c "import json; r=json.load(open('/opt/lab-classroom/class46/report.json', encoding='utf-8')); assert r['target'] == 'http://127.0.0.1:8787/ping'" to confirm the intended target.
- [ ] Run python3 -c "import json; r=json.load(open('/opt/lab-classroom/class46/report.json', encoding='utf-8')); assert len(r['checks']) == 3" to confirm the sample count.
- [ ] Run python3 -c "import json; r=json.load(open('/opt/lab-classroom/class46/report.json', encoding='utf-8')); assert r['healthy']; assert all(x['status'] == 200 for x in r['checks'])" after recovery.
- [ ] Run find /opt/lab-classroom/class46 -maxdepth 1 -type f -printf '%f\n' to review the lab artifacts without changing them.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The service exits immediately and the monitor reports connection refusal. | TCP port 8787 is already in use or Python could not bind the loopback socket. | Read /opt/lab-classroom/class46/server.log. Stop the conflicting lab process if it is known to be disposable, or edit both lab scripts to use the same unused loopback port. |
| The monitor reports connection refusal even though server.pid exists. | The process recorded in server.pid has exited, leaving a stale identifier file. | Use kill -0 with the recorded identifier to test the process, inspect server.log, and restart mock_radarr.py from the class workspace. |
| The baseline receives HTTP 503. | state.txt still contains unavailable from the outage simulation. | Write available followed by a newline to /opt/lab-classroom/class46/state.txt and rerun the monitor. |
| The service returns HTTP 200, but the monitor still exits unsuccessfully. | The measured maximum latency exceeded the classroom policy or one of the three observations failed. | Inspect maximum_latency_ms and every checks entry in report.json. Confirm that state.txt contains available and that the host is not heavily constrained. |
| Python reports PermissionError while creating files or writing report.json. | The current user lacks write access to the class workspace. | Use the authorized classroom account or have the lab administrator correct ownership of /opt/lab-classroom/class46/ without broadening permissions beyond the required users. |
| A JSON parsing command fails. | report.json is incomplete because the monitor was interrupted during its write or the file was manually edited. | Run monitor.py again and then parse the newly generated report. |

## Security considerations

The mock service binds only to 127.0.0.1 and is not intended to accept remote connections.
Do not expose a Radarr administrative interface to an untrusted network merely to support monitoring.
Keep production authentication material out of command history, scripts, monitoring labels, reports, and alert messages.
Use the least privilege needed by a production monitoring integration and restrict who can read its configuration.
Redact request headers and sensitive query data before forwarding monitoring logs to centralized systems.
Use separate alerts for application reachability, dependency failures, and workflow failures so responders receive accurate context.
Monitor storage capacity and write access without performing destructive test writes in a production movie library.

## Rollback

Restore the mock service state by running: printf '%s\n' 'available' > /opt/lab-classroom/class46/state.txt
Stop only the recorded lab process by running: test -s /opt/lab-classroom/class46/server.pid && kill "$(cat /opt/lab-classroom/class46/server.pid)"
Confirm the recorded process has stopped by running: if kill -0 "$(cat /opt/lab-classroom/class46/server.pid)" 2>/dev/null; then echo 'lab process still running'; else echo 'lab process stopped'; fi
Leave the scripts, logs, state, identifier, and report in /opt/lab-classroom/class46/ for instructor review. No production Radarr files or services require restoration because the lab did not modify them.

## Video narration notes

In this class, we are going to monitor Radarr as a service rather than merely checking whether its process exists. Start by thinking in layers. The operating system can report a running process while the application is unable to answer HTTP requests. Radarr can answer HTTP requests while an indexer or download client is unavailable. It can communicate with those dependencies while still failing to import a movie because the destination storage is full, unavailable, or unwritable. Each layer tells us something different.

The lab uses a local Python service that behaves like a small health endpoint. It is deliberately bound to the loopback interface so it is not exposed to the network. Its behavior is controlled by a state file in the class workspace. The available state returns HTTP 200. The unavailable state returns HTTP 503. The slow state waits before returning HTTP 200. This lets us observe the important distinction between a failed request and a successful but unacceptably slow request.

Next, examine the monitor. It performs three observations and records the HTTP status, latency, success flag, and error category for each one. It then calculates observed availability and records the maximum latency. The monitor exits successfully only when every observation receives HTTP 200 and the maximum latency remains within the classroom policy. That latency policy exists to demonstrate alert logic; it is not a performance claim about Radarr.

Run the healthy baseline and inspect report.json. Then change the state to unavailable. The service now returns HTTP 503, and the monitor exits unsuccessfully. Notice that this is better evidence than a process check because the mock process remains alive throughout the failure. Next, change the state to slow. The HTTP requests still succeed, but the monitor identifies a policy violation. Finally, restore the available state and verify recovery.

For a production design, retain this layered approach. Check the host or container, probe HTTP, observe Radarr health information, test important dependencies, watch storage, and validate a safe workflow. Use a trusted remote probe when you need to include DNS, routing, and reverse-proxy behavior. Protect monitoring configuration, avoid recording sensitive request data, and make alerts specific enough that an operator knows whether to investigate Radarr itself, an indexer, a download client, storage, or the network.

## References

- Radarr project documentation: https://wiki.servarr.com/radarr
- Radarr source repository: https://github.com/Radarr/Radarr
- Prometheus instrumentation practices: https://prometheus.io/docs/practices/instrumentation/
- Prometheus alerting practices: https://prometheus.io/docs/practices/alerting/
- IETF RFC 9110, HTTP Semantics: https://www.rfc-editor.org/rfc/rfc9110
- Python urllib.request documentation: https://docs.python.org/3/library/urllib.request.html
- Python http.server documentation: https://docs.python.org/3/library/http.server.html

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

# Class 26: Network Troubleshooting Tools and Methodology

**Learning objective:** Apply a layered troubleshooting workflow from local state through application response; Distinguish name-resolution failures from routing, transport, and application failures; Use ip, ping, getent, ss, curl, and optional tracepath observations appropriately; Interpret connection refused, timeout, name-resolution failure, and HTTP error symptoms; Verify which address and port a process is listening on; Collect before-and-after evidence while limiting changes to the lab scope; Document a concise incident hypothesis, test, result, and conclusion
**Bloom level:** Understand / Apply
**Track:** Homelab Operations and Networking · **Difficulty:** intermediate · **Duration:** ~105 minutes · **Lab risk:** low
**Build output:** Develop a repeatable, evidence-driven method for diagnosing connectivity problems without making premature configuration changes. The lesson uses a local HTTP service to demonstrate how addressing, routing, name resolution, transport ports, listening sockets, and application behavior can be tested independently.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### primary_platform
Linux systems with procfs and iproute2

### tested_command_families
iproute2 ip
iproute2 ss
GNU or compatible getent
curl
Python 3 http.server
POSIX-compatible shell utilities

### notes
The ss process column may omit details when the current user lacks permission.
tracepath is optional and may not be installed by default.
The socket-filter expression requires a reasonably current iproute2 release; if unsupported, run `ss -lntp` and visually filter for ports 18080 and 18081.
macOS and Windows use different native commands for route and socket inspection, so the exact lab commands target Linux.
The service is deliberately IPv4-only because it binds to 127.0.0.1.

## Learning objective

- Apply a layered troubleshooting workflow from local state through application response
- Distinguish name-resolution failures from routing, transport, and application failures
- Use ip, ping, getent, ss, curl, and optional tracepath observations appropriately
- Interpret connection refused, timeout, name-resolution failure, and HTTP error symptoms
- Verify which address and port a process is listening on
- Collect before-and-after evidence while limiting changes to the lab scope
- Document a concise incident hypothesis, test, result, and conclusion

## Why this matters

Develop a repeatable, evidence-driven method for diagnosing connectivity problems without making premature configuration changes. The lesson uses a local HTTP service to demonstrate how addressing, routing, name resolution, transport ports, listening sockets, and application behavior can be tested independently.

## Prerequisites

- Comfort using a Linux shell and reading command output
- Basic understanding of IPv4 addresses, TCP, UDP, ports, and DNS
- A Linux host or virtual machine with sudo access
- Python 3, iproute2 utilities, curl, and getent
- Permission to create files under /opt/lab-classroom/class26/

## Required reading

- Linux ip-address manual: https://man7.org/linux/man-pages/man8/ip-address.8.html
- Linux ip-route manual: https://man7.org/linux/man-pages/man8/ip-route.8.html
- Linux ss manual: https://man7.org/linux/man-pages/man8/ss.8.html
- curl command-line documentation: https://curl.se/docs/manpage.html
- RFC 1122, Requirements for Internet Hosts: Communication Layers: https://www.rfc-editor.org/rfc/rfc1122

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| symptom | An observed failure or unexpected behavior, such as a timeout, refused connection, or incorrect response. |
| hypothesis | A specific, testable explanation for a symptom. |
| loopback | A host-local network interface and address range used to communicate with services on the same system. |
| socket | An operating-system endpoint identified by protocol, local address, and local port, with optional remote endpoint information. |
| listener | A process waiting for incoming transport connections on a particular address and port. |
| route | A rule used by the operating system to choose an outgoing interface, next hop, and source address for a destination. |
| resolver | The software path that converts names into addresses using sources such as local host records or DNS. |
| connection refused | A transport-level response commonly indicating that the destination host was reached but no service accepted the connection on that address and port. |
| timeout | A failure in which the expected response did not arrive before a configured deadline; it does not by itself identify where packets were lost. |
| bind address | The local address on which a service accepts traffic, such as 127.0.0.1 for host-local access or a non-loopback address for access through an external interface. |
| application-layer response | A protocol-specific result, such as an HTTP status line and response body, proving more than basic port reachability. |

## Instruction

Effective network troubleshooting is a process of reducing uncertainty, not a process of trying random fixes. Begin by recording the exact symptom, the source host, the intended destination, the protocol, the port, the time, and what success should look like. A statement such as “the network is down” is too broad. A statement such as “an HTTP request from this host to 127.0.0.1 port 18081 is refused immediately” is testable.

Work through the path in layers. First confirm local interface state and addressing with `ip address`. Next ask the kernel how it would reach the destination with `ip route get DESTINATION`; this is usually more useful than merely reading the entire route table because it reveals the selected interface and source address. If a hostname is involved, test resolution separately with `getent ahosts NAME`. This follows the host's configured name-service path and helps distinguish name lookup from packet delivery. A name resolving successfully does not prove that an application is available, and a successful ping does not prove that a TCP port is open.

At the transport layer, identify whether a service is actually listening with `ss -lntp`. Address scope matters: a process bound only to 127.0.0.1 can be reached locally but not through a different host interface. A process may also be healthy on one port while the client is configured for another. An immediate “connection refused” is evidence that the destination stack was reached and rejected the connection or had no matching listener. A timeout is less specific; possible causes include packet loss, an incorrect route, an unavailable destination, or silent policy filtering. Preserve that distinction instead of treating every failure as the same condition.

Finally, test the application protocol. `curl -v` exposes address selection, connection attempts, request headers, response headers, and application status. A completed TCP connection followed by an HTTP 404 is not a basic connectivity failure: the network path and web service worked, but the requested resource was absent. Likewise, an HTTP 500 indicates that the request reached the application even though the application failed internally. Use bounded tests such as `--connect-timeout` and `--max-time` so a diagnostic command cannot wait indefinitely.

A disciplined cycle is: observe, scope, hypothesize, test one variable, compare the result with the prediction, and record the conclusion. Prefer read-only inspection before changing anything. Do not restart unrelated services or alter host networking merely because a client failed. Changes can erase evidence and create a second problem. In this lab, the deliberately wrong port produces a transport failure, while the correct port produces an HTTP success. The contrast demonstrates how listener inspection and client output can locate a fault without changing system-wide network configuration.

## Architecture

### diagnostic_path
Client command constructs an HTTP request
A literal loopback address avoids external name-service dependencies during the primary test
The kernel performs a route lookup and selects the loopback interface
TCP attempts to connect to the selected destination port
A Python process listens only on 127.0.0.1:18080
The HTTP server reads health.txt from /opt/lab-classroom/class26/site/
Server output is redirected to /opt/lab-classroom/class26/server.log

### fault_model
Port 18081 is intentionally unused, while port 18080 is the known-good listener. Comparing the two requests isolates a destination-port mismatch.

### scope_boundary
All persistent files and directory metadata created or modified by the lab are confined to /opt/lab-classroom/class26/. No host network configuration is changed.

### evidence_flow
ip address establishes local interface state; ip route get establishes path selection; getent establishes name-resolution behavior; ss establishes listener state; curl establishes transport and HTTP behavior; the server log confirms that the application received the successful request.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Create a troubleshooting worksheet for a hypothetical service at app.example.test:8443. Include the exact symptom, at least three ordered hypotheses, one minimally invasive test per hypothesis, the expected result for each test, and a stopping condition before any configuration change.

### extension
Repeat the reasoning on an authorized homelab service without changing it. Compare a literal-address request with a hostname request and document whether the two tests exercise the same resolver and address-family path.

### deliverable
Submit a one-page incident note containing scope, timestamps, commands, relevant output excerpts, hypothesis updates, final conclusion, and any remaining uncertainty.

### grading_criteria
The scope and expected behavior are explicit.
Tests isolate name resolution, routing, transport, and application behavior.
Claims are supported by observed evidence.
No unnecessary configuration change is proposed.
The note distinguishes confirmed facts from assumptions.

## Feynman teach-back

### prompt
Explain the diagnosis to a teammate who knows what a website is but does not know network layers.

### model_explanation
An address is like the building, and a port is like a numbered service desk inside that building. The computer knew how to reach the local building, but the client first asked for desk 18081. No one was working at that desk, so the connection was refused. We then listed the active desks and found the web service at desk 18080. Requesting the same file from 18080 returned class26-ok. That proves the route and web service worked; the original problem was the wrong desk number.

### self_check
Can you explain why successful name resolution does not prove that a service is running?
Can you explain why an HTTP 404 proves more connectivity than a timeout?
Can you identify which command tested routing, which tested listeners, and which tested the application?
Can you state what this loopback-only exercise does not prove about access from another host?

## Retrieval check

1. 1. Why should `ip route get 127.0.0.1` be used in addition to viewing interface addresses?
2. 2. What does an immediate TCP connection refusal usually tell you that a timeout does not?
3. 3. If `getent ahosts server.example` succeeds, what has been proven and what has not been proven?
4. 4. Why can an HTTP 404 response be evidence that basic network connectivity is working?
5. 5. Which command in this lesson identifies whether ports 18080 and 18081 have TCP listeners?
6. 6. What is the diagnostic significance of a service being bound to 127.0.0.1 rather than a non-loopback address?
7. 7. Why must the process command line be checked before using the PID stored in server.pid?
8. 8. In the lab, what evidence supports the conclusion that the client used the wrong destination port?

## Guided lab

### name
Diagnose a Wrong-Port Failure Against a Local HTTP Service

### constraints
Do not edit operating-system network configuration.
Do not install packages during the exercise.
Create or modify persistent files only under /opt/lab-classroom/class26/.
Use port 18080 for the controlled service and port 18081 for the deliberate failure.
Run each observation before making any corrective change.

### steps
### step
1

### title
Create the isolated workspace

### commands
LAB=/opt/lab-classroom/class26
sudo install -d -m 0755 "$LAB/site"
sudo chown -R "$(id -u):$(id -g)" "$LAB"
printf 'class26-ok\n' > "$LAB/site/health.txt"

### observe
Confirm that the health file exists only inside the assigned lab directory.
### step
2

### title
Start a loopback-only HTTP service

### commands
LAB=/opt/lab-classroom/class26
python3 -m http.server 18080 --bind 127.0.0.1 --directory "$LAB/site" > "$LAB/server.log" 2>&1 &
echo "$!" > "$LAB/server.pid"
sleep 1

### observe
The background process identifier is stored in server.pid, and service output is stored in server.log.
### step
3

### title
Establish local addressing and route evidence

### commands
ip address show dev lo
ip route get 127.0.0.1
getent ahosts localhost

### observe
The loopback interface should be active, the route lookup should select lo, and localhost should resolve to one or more loopback addresses.
### step
4

### title
Reproduce the deliberate failure

### commands
curl --connect-timeout 2 --max-time 4 -v http://127.0.0.1:18081/health.txt

### observe
The request should fail because the lab did not create a listener on port 18081. Record the exact curl message and exit status rather than paraphrasing it as a generic network failure.
### step
5

### title
Inspect transport listeners

### commands
ss -lntp '( sport = :18080 or sport = :18081 )'

### observe
A listener should appear on 127.0.0.1:18080, while no listener should appear on port 18081. Process details may be partially hidden on some systems, but the local address and port should remain visible.
### step
6

### title
Test the correct endpoint

### commands
curl --connect-timeout 2 --max-time 4 -v http://127.0.0.1:18080/health.txt
printf 'curl_exit=%s\n' "$?"

### observe
The client should connect, receive an HTTP success response, print class26-ok, and report curl_exit=0.
### step
7

### title
Correlate client and server evidence

### commands
LAB=/opt/lab-classroom/class26
cat "$LAB/server.log"
cat "$LAB/server.pid"

### observe
The log should contain the successful request for /health.txt. The failed request to port 18081 should not appear because it never reached this HTTP process.
### step
8

### title
Optionally inspect the local path

### commands
command -v tracepath >/dev/null 2>&1 && tracepath -n 127.0.0.1 || printf 'tracepath is not installed; optional step skipped\n'

### observe
If available, tracepath should show a host-local path rather than an external router.
### step
9

### title
Write the incident conclusion

### commands
LAB=/opt/lab-classroom/class26
printf '%s\n' 'Symptom: HTTP request to 127.0.0.1:18081 failed.' 'Evidence: route selected lo; ss showed a listener only on 127.0.0.1:18080; HTTP on 18080 returned class26-ok.' 'Conclusion: the client used the wrong destination port, not a broken route or failed HTTP service.' > "$LAB/conclusion.txt"
cat "$LAB/conclusion.txt"

### observe
The conclusion should connect each claim to collected evidence and should not claim that external networking was tested.

## Expected results

- The loopback interface is present and the route lookup for 127.0.0.1 selects the local loopback path.
- localhost resolves to at least one loopback address through the host name-service configuration.
- The request to 127.0.0.1:18081 fails because no lab listener exists on that port.
- ss reports a TCP listener on 127.0.0.1:18080 and no listener on port 18081.
- The request to http://127.0.0.1:18080/health.txt returns the body class26-ok.
- The successful request appears in /opt/lab-classroom/class26/server.log.
- The written conclusion identifies a destination-port mismatch and does not misdiagnose the route or name resolver.

## Verification checkpoints

- [ ] Run `test -f /opt/lab-classroom/class26/site/health.txt && printf 'health file present\n'` and confirm the success message.
- [ ] Run `ss -lnt '( sport = :18080 )'` and confirm that 127.0.0.1:18080 is in the LISTEN state.
- [ ] Run `curl --fail --silent --show-error --max-time 4 http://127.0.0.1:18080/health.txt` and confirm that the output is exactly class26-ok.
- [ ] Run `curl --silent --max-time 2 http://127.0.0.1:18081/health.txt >/dev/null; test "$?" -ne 0` and confirm that the shell test succeeds.
- [ ] Run `grep -F 'GET /health.txt' /opt/lab-classroom/class26/server.log` and confirm that at least one successful request is logged.
- [ ] Run `grep -F 'wrong destination port' /opt/lab-classroom/class26/conclusion.txt` and confirm that the evidence-based conclusion was recorded.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| python3 reports that port 18080 is already in use. | Another process is already listening on the selected port, or a previous lab server is still running. | Inspect `ss -lntp '( sport = :18080 )'`. If the listener is the prior lab process recorded in server.pid, verify its command line and stop it using the controlled procedure. Do not terminate an unidentified service. |
| The request to port 18080 is refused. | The Python server failed to start, exited immediately, or is not bound to the expected address and port. | Read /opt/lab-classroom/class26/server.log, check the PID file, and inspect `ss -lntp '( sport = :18080 )'`. Correct the startup command only after identifying the failure. |
| The request to port 18080 connects but returns an HTTP 404 response. | The server is reachable, but health.txt is absent from the configured document directory or the requested path is incorrect. | Confirm that /opt/lab-classroom/class26/site/health.txt exists and that the request path is /health.txt. Treat this as an application resource problem, not a routing problem. |
| curl is not found. | The required client package is absent from the lab host. | Stop the exercise and install curl through the platform's approved package-management process outside this lesson, then repeat the lab. Do not substitute unreviewed download-and-execute commands. |
| getent returns IPv6 and IPv4 results in an unexpected order. | The system's host database and address-selection policy prefer one address family over the other. | Record the result as resolver evidence. Continue using the literal IPv4 loopback address for the controlled service test because the server is intentionally bound to 127.0.0.1. |
| ss shows the listener but omits the process name or PID. | The current user lacks permission to view complete process metadata. | Use the visible address, port, and LISTEN state as evidence. Correlate the service with the PID file and server log instead of broadening privileges unnecessarily. |
| The request hangs until the maximum time is reached instead of being refused immediately. | The environment is handling the destination differently than expected, or a local packet-filter policy is silently discarding traffic. | Confirm that the destination is exactly 127.0.0.1, inspect route and listener evidence again, record the timeout as distinct from refusal, and consult the host owner before changing any security policy. |
| server.log remains empty after a successful response. | Output buffering, inspection of the wrong file, or a different process serving the request. | Confirm the server command line associated with the recorded PID, repeat the request, wait briefly, and inspect the exact path /opt/lab-classroom/class26/server.log. |

## Security considerations

### principles
Use read-only observations before corrective actions.
Bind the training service to 127.0.0.1 so it is not intentionally exposed through non-loopback interfaces.
Use explicit connection and total time limits for client probes.
Probe only systems and ports for which authorization has been granted.
Do not include credentials, session tokens, or sensitive response bodies in shared troubleshooting records.
Verify process identity before sending a termination signal because PID files can become stale.
Avoid changing routing, resolver settings, interface state, or security policy during evidence collection.

### data_handling
The lab serves only the text class26-ok. Logs and notes remain under /opt/lab-classroom/class26/ and should not contain secrets.

### exposure
The service listens only on the IPv4 loopback address. This design limits direct access to processes on the same host, although local users may still be able to connect.

### authorization
Commands demonstrated against loopback must not be redirected toward third-party systems without explicit permission.

## Rollback

### goal
Stop only the lab-owned Python process and remove only the class 26 workspace.

### steps
Set `LAB=/opt/lab-classroom/class26`.
If `$LAB/server.pid` exists, read the PID and inspect `ps -p "$PID" -o pid=,args=`.
Proceed only if the displayed process is the expected Python HTTP server using port 18080 and the class 26 site directory.
Run `kill "$PID"` and verify that `ss -lnt '( sport = :18080 )'` no longer shows the lab listener.
Run `sudo rm -r -- /opt/lab-classroom/class26/` only after confirming the exact path.
Verify rollback with `test ! -e /opt/lab-classroom/class26 && printf 'class26 workspace removed\n'`.

### persistent_effects
After successful rollback, no lab-created files remain. The lesson does not intentionally change persistent host networking.

## Video narration notes

Begin with the failed request to port 18081 and resist the temptation to label it simply as a network outage. Freeze the symptom: source host, destination address, destination port, protocol, exact error, and time. Show the loopback interface with `ip address`, then ask the kernel for the selected path using `ip route get 127.0.0.1`. Explain that these observations establish local addressing and path selection, but they do not prove that a server is listening. Use `getent ahosts localhost` to demonstrate that name resolution is a separate subsystem, even though the controlled HTTP test uses a literal address. Next, inspect listening TCP sockets with `ss`. Highlight the listener on 127.0.0.1 port 18080 and the absence of a listener on port 18081. Repeat the HTTP request against port 18080. Point out the completed connection, HTTP response, and class26-ok body. Open server.log and correlate the successful request with the application process. Emphasize that the failed request never reached that process. Finish by writing a concise conclusion: the route was valid, the service was healthy on 18080, and the original client used the wrong destination port. Demonstrate rollback only after verifying that the recorded PID belongs to the lab server.

## References

- Linux ip-address manual: https://man7.org/linux/man-pages/man8/ip-address.8.html
- Linux ip-route manual: https://man7.org/linux/man-pages/man8/ip-route.8.html
- Linux ss manual: https://man7.org/linux/man-pages/man8/ss.8.html
- curl manual: https://curl.se/docs/manpage.html
- GNU C Library host-name lookup documentation: https://www.gnu.org/software/libc/manual/html_node/Host-Names.html
- Python http.server documentation: https://docs.python.org/3/library/http.server.html
- RFC 1122, Requirements for Internet Hosts: Communication Layers: https://www.rfc-editor.org/rfc/rfc1122
- RFC 9293, Transmission Control Protocol: https://www.rfc-editor.org/rfc/rfc9293
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

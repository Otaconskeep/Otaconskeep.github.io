# Lab: Reverse Proxy Fundamentals

**Module:** Edge Access & VPN
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Distinguish a reverse proxy from a forward proxy and from the upstream application it serves.

## Before you start

- Comfort using a Linux shell and reading HTTP request and response headers.
- Python 3.9 or newer with the standard library available.
- The curl and ss commands.
- Permission to create files and launch user-owned processes under /opt/lab-classroom/class64/.
- Local TCP ports 18080 and 18081 must be available.

## Guided lab

### workspace
/opt/lab-classroom/class64/

### steps
1. Confirm that the planned listeners are free: `ss -ltn | grep -E ':(18080|18081)[[:space:]]' || true`. Do not continue if an unrelated listener is using either port.
2. Create and enter the isolated workspace: `mkdir -p /opt/lab-classroom/class64 && cd /opt/lab-classroom/class64`.
3. Create the backend with a shell heredoc:
`cat > /opt/lab-classroom/class64/backend.py <<'PY'
#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 18081

class BackendHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print("backend:", fmt % args, flush=True)

    def send_json(self, status, payload):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "X-Backend-Hop")
        self.send_header("X-Backend-Hop", "must-not-reach-client")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/hello":
            self.send_json(200, {
                "path": self.path,
                "host": self.headers.get("Host"),
                "x_forwarded_for": self.headers.get("X-Forwarded-For"),
                "x_forwarded_host": self.headers.get("X-Forwarded-Host"),
                "x_forwarded_proto": self.headers.get("X-Forwarded-Proto"),
                "via": self.headers.get("Via"),
                "x_lab_hop": self.headers.get("X-Lab-Hop")
            })
        elif self.path == "/fail":
            self.send_json(500, {"error": "intentional failure"})
        else:
            self.send_json(404, {"error": "not found"})

if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), BackendHandler).serve_forever()
PY`
4. Create the reverse proxy with a shell heredoc:
`cat > /opt/lab-classroom/class64/proxy.py <<'PY'
#!/usr/bin/env python3
import http.client
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 18080
UPSTREAM_HOST = "127.0.0.1"
UPSTREAM_PORT = 18081

FIXED_HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate",
    "proxy-authorization", "te", "trailer",
    "transfer-encoding", "upgrade"
}


def connection_tokens(headers):
    tokens = set()
    for value in headers.get_all("Connection", []):
        for token in value.split(","):
            token = token.strip().lower()
            if token:
                tokens.add(token)
    return tokens


def appended(existing, value):
    return f"{existing}, {value}" if existing else value


class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print("proxy:", fmt % args, flush=True)

    def send_local_json(self, status, payload):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def proxy_request(self):
        request_hop = FIXED_HOP_BY_HOP | connection_tokens(self.headers)
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_local_json(400, {"error": "invalid content-length"})
            return
        body = self.rfile.read(content_length) if content_length else None
        outbound = {}
        managed = {
            "host", "content-length", "x-forwarded-for",
            "x-forwarded-host", "x-forwarded-proto", "via"
        }
        for name, value in self.headers.items():
            lower = name.lower()
            if lower not in request_hop and lower not in managed:
                outbound[name] = value
        outbound["Host"] = f"{UPSTREAM_HOST}:{UPSTREAM_PORT}"
        if body is not None:
            outbound["Content-Length"] = str(len(body))
        outbound["X-Forwarded-For"] = appended(
            self.headers.get("X-Forwarded-For"), self.client_address[0]
        )
        outbound["X-Forwarded-Host"] = self.headers.get("Host", "")
        outbound["X-Forwarded-Proto"] = "http"
        outbound["Via"] = appended(self.headers.get("Via"), "1.1 class64-proxy")

        connection = http.client.HTTPConnection(UPSTREAM_HOST, UPSTREAM_PORT, timeout=3)
        try:
            connection.request(self.command, self.path, body=body, headers=outbound)
            response = connection.getresponse()
            response_body = response.read()
            response_hop = FIXED_HOP_BY_HOP | connection_tokens(response.headers)
            self.send_response(response.status, response.reason)
            for name, value in response.getheaders():
                lower = name.lower()
                if lower not in response_hop and lower != "content-length":
                    self.send_header(name, value)
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)
        except (OSError, http.client.HTTPException):
            self.send_local_json(502, {
                "error": "bad_gateway",
                "detail": "upstream unavailable"
            })
        finally:
            connection.close()

    def do_GET(self):
        self.proxy_request()

    def do_POST(self):
        self.proxy_request()

    def do_PUT(self):
        self.proxy_request()

    def do_DELETE(self):
        self.proxy_request()

if __name__ == "__main__":
    ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), ProxyHandler).serve_forever()
PY`
5. Start the backend and proxy from the workspace: `cd /opt/lab-classroom/class64 && nohup python3 backend.py > backend.log 2>&1 & echo $! > backend.pid && nohup python3 proxy.py > proxy.log 2>&1 & echo $! > proxy.pid && sleep 1`. Confirm both listeners with `ss -ltn | grep -E ':(18080|18081)[[:space:]]'`.
6. Request the backend through the proxy: `curl -sS http://127.0.0.1:18080/hello`. The exact body is `{"path":"/hello","host":"127.0.0.1:18081","x_forwarded_for":"127.0.0.1","x_forwarded_host":"127.0.0.1:18080","x_forwarded_proto":"http","via":"1.1 class64-proxy","x_lab_hop":null}`.
7. Observe the full proxied response: `curl -sS -i http://127.0.0.1:18080/hello`. Expect HTTP 200, a Content-Type of application/json, and a Content-Length matching the buffered response. Neither `Connection: X-Backend-Hop` nor `X-Backend-Hop: must-not-reach-client` may appear.
8. Verify Via appending and removal of a Connection-nominated request header: `curl -sS -H 'Via: 1.0 lab-client' -H 'Connection: X-Lab-Hop' -H 'X-Lab-Hop: remove-me' http://127.0.0.1:18080/hello`. The exact body is `{"path":"/hello","host":"127.0.0.1:18081","x_forwarded_for":"127.0.0.1","x_forwarded_host":"127.0.0.1:18080","x_forwarded_proto":"http","via":"1.0 lab-client, 1.1 class64-proxy","x_lab_hop":null}`.
9. Request the intentional backend failure: `curl -sS -i http://127.0.0.1:18080/fail`. Expect status HTTP 500 and the exact body `{"error":"intentional failure"}`. This demonstrates that the proxy relays an upstream application error rather than changing it to 502.
10. Stop only the backend and test bad-gateway behavior: `cd /opt/lab-classroom/class64 && kill "$(cat backend.pid)" && sleep 1 && curl -sS -i http://127.0.0.1:18080/hello`. Expect status HTTP 502 and the exact body `{"error":"bad_gateway","detail":"upstream unavailable"}`.
11. Restart the backend immediately after the 502 test so all later checks can succeed: `cd /opt/lab-classroom/class64 && nohup python3 backend.py > backend.log 2>&1 & echo $! > backend.pid && sleep 1 && curl -sS http://127.0.0.1:18080/hello`. The final curl must again return the exact successful /hello JSON shown in step 6.
12. Review process logs without changing system state: `cat /opt/lab-classroom/class64/proxy.log` and `cat /opt/lab-classroom/class64/backend.log`.

### implementation_limits
The proxy uses a single fixed upstream and has no load balancing or service discovery.
Only plain HTTP on loopback is used; TLS termination is not implemented.
Request bodies using Content-Length are buffered. Chunked request decoding and streaming are not implemented.
Responses are buffered so the proxy can synthesize an accurate Content-Length.
Protocol upgrades, WebSockets, CONNECT, retries, caching, authentication, rate limits, and production observability are not implemented.
X-Forwarded-Proto is fixed to http because the client-facing listener is plain HTTP.
The proxy demonstrates header mechanics but is not intended for Internet-facing deployment.

## Expected results

- A request to http://127.0.0.1:18080/hello returns HTTP 200 with the exact body {"path":"/hello","host":"127.0.0.1:18081","x_forwarded_for":"127.0.0.1","x_forwarded_host":"127.0.0.1:18080","x_forwarded_proto":"http","via":"1.1 class64-proxy","x_lab_hop":null}.
- The backend sees Host as 127.0.0.1:18081 while X-Forwarded-Host preserves 127.0.0.1:18080.
- An incoming Via value of 1.0 lab-client becomes 1.0 lab-client, 1.1 class64-proxy rather than being replaced.
- X-Lab-Hop is absent at the backend when its name is listed in the incoming Connection field, producing x_lab_hop:null.
- The backend's Connection-nominated X-Backend-Hop response field does not reach the client.
- A request to /fail returns HTTP 500 with the exact body {"error":"intentional failure"}.
- A request made while the backend is stopped returns HTTP 502 with the exact body {"error":"bad_gateway","detail":"upstream unavailable"}.
- After the backend restart step, both ports are listening and /hello succeeds again.

## Verification

- [ ] Prerequisite for verification items 1-5: both processes must be restarted first. From /opt/lab-classroom/class64, stop any class processes referenced by existing PID files, then launch fresh instances: `cd /opt/lab-classroom/class64; if test -f proxy.pid && kill -0 "$(cat proxy.pid)" 2>/dev/null; then kill "$(cat proxy.pid)"; fi; if test -f backend.pid && kill -0 "$(cat backend.pid)" 2>/dev/null; then kill "$(cat backend.pid)"; fi; sleep 1; nohup python3 backend.py > backend.log 2>&1 & echo $! > backend.pid; nohup python3 proxy.py > proxy.log 2>&1 & echo $! > proxy.pid; sleep 1; ss -ltn | grep -E ':(18080|18081)[[:space:]]'`. The output must show listeners for both 127.0.0.1:18080 and 127.0.0.1:18081.
- [ ] With both processes running, execute `test "$(curl -sS http://127.0.0.1:18080/hello)" = '{"path":"/hello","host":"127.0.0.1:18081","x_forwarded_for":"127.0.0.1","x_forwarded_host":"127.0.0.1:18080","x_forwarded_proto":"http","via":"1.1 class64-proxy","x_lab_hop":null}' && echo PASS`. The exact expected output is `PASS`.
- [ ] With both processes running, execute `code=$(curl -sS -o /opt/lab-classroom/class64/verify-fail.json -w '%{http_code}' http://127.0.0.1:18080/fail); test "$code" = '500' && test "$(cat /opt/lab-classroom/class64/verify-fail.json)" = '{"error":"intentional failure"}' && echo PASS`. The exact expected output is `PASS`.
- [ ] With both processes running, execute `body=$(curl -sS -D /opt/lab-classroom/class64/verify-headers.txt -H 'Via: 1.0 verifier' -H 'Connection: X-Lab-Hop' -H 'X-Lab-Hop: remove-me' http://127.0.0.1:18080/hello); test "$body" = '{"path":"/hello","host":"127.0.0.1:18081","x_forwarded_for":"127.0.0.1","x_forwarded_host":"127.0.0.1:18080","x_forwarded_proto":"http","via":"1.0 verifier, 1.1 class64-proxy","x_lab_hop":null}' && ! grep -qi '^X-Backend-Hop:' /opt/lab-classroom/class64/verify-headers.txt && ! grep -qi '^Connection:.*X-Backend-Hop' /opt/lab-classroom/class64/verify-headers.txt && echo PASS`. The exact expected output is `PASS`.
- [ ] With both processes initially running, verify and recover from an outage: `cd /opt/lab-classroom/class64; kill "$(cat backend.pid)"; sleep 1; code=$(curl -sS -o verify-502.json -w '%{http_code}' http://127.0.0.1:18080/hello); test "$code" = '502' && test "$(cat verify-502.json)" = '{"error":"bad_gateway","detail":"upstream unavailable"}' && echo PASS-502; nohup python3 backend.py > backend.log 2>&1 & echo $! > backend.pid; sleep 1; test "$(curl -sS http://127.0.0.1:18080/hello)" = '{"path":"/hello","host":"127.0.0.1:18081","x_forwarded_for":"127.0.0.1","x_forwarded_host":"127.0.0.1:18080","x_forwarded_proto":"http","via":"1.1 class64-proxy","x_lab_hop":null}' && echo PASS-RECOVERY`. The exact output lines are `PASS-502` followed by `PASS-RECOVERY`; both processes are running again afterward.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The Python process reports Address already in use. | Port 18080 or 18081 is already occupied, or an earlier class process is still running. | Run `ss -ltnp | grep -E ':(18080|18081)[[:space:]]'` and inspect the owner. Stop only a confirmed class process using the corresponding PID file. Do not terminate an unrelated service. |
| The proxy returns 502 even though the lab was just started. | The backend failed to launch, exited because its port was occupied, or was not restarted after the outage test. | Read `/opt/lab-classroom/class64/backend.log`, verify port 18081 with `ss -ltn | grep ':18081[[:space:]]'`, and restart backend.py from the class directory. |
| A direct request to port 18081 works, but a request to port 18080 fails. | The proxy is not running or port 18080 is occupied. | Read `/opt/lab-classroom/class64/proxy.log`, check the PID in proxy.pid, and verify the port with `ss -ltn | grep ':18080[[:space:]]'`. |
| The expected JSON comparison fails even though the response looks similar. | The request used a different Host value, added forwarding headers, targeted the backend directly, or was sent from somewhere other than the local host. | Use the exact curl command and URL from the verification item. Confirm that the request targets 127.0.0.1:18080 rather than 18081. |
| X-Lab-Hop appears in the backend JSON instead of null. | The Connection field did not name X-Lab-Hop, or proxy.py was copied incorrectly. | Use both `Connection: X-Lab-Hop` and `X-Lab-Hop: remove-me`, then compare connection_tokens and request_hop in proxy.py with the supplied implementation. |
| The proxy process exits after an upstream request. | There is a syntax error, an incomplete heredoc, or a local edit introduced an unhandled problem. | Run `python3 -m py_compile /opt/lab-classroom/class64/backend.py /opt/lab-classroom/class64/proxy.py` and inspect proxy.log. Recreate the affected file using the complete heredoc. |
| A chunked request fails or blocks. | The educational proxy does not decode chunked request bodies. | Use the provided GET requests or send a request with Content-Length. Use a production reverse proxy for streaming and chunked-request support. |

## Security

Both services bind to 127.0.0.1 so the exercise is not intentionally exposed beyond the host.
Forwarding headers are not inherently trustworthy. An Internet-facing edge should discard untrusted client-supplied forwarding values before establishing authoritative values.
An internal application should trust proxy-generated forwarding metadata only when requests can arrive exclusively through known proxies.
Preserving an arbitrary Host value without validation can enable host-header attacks, poisoned links, or incorrect tenant routing. Production proxies should enforce an allowlist of accepted hostnames.
Hop-by-hop fields must be removed on both request and response paths, including names dynamically nominated by Connection.
The lab sends no credentials or sensitive data. Plain HTTP provides neither transport confidentiality nor peer authentication.
A production proxy requires request-size limits, timeouts, resource controls, structured logging, safe error handling, TLS policy, and ongoing updates.
Detailed upstream exceptions are not returned to clients; the lab emits a stable 502 body to avoid leaking local implementation details.
PID files are trusted only within the isolated classroom workspace. Before stopping a process, confirm that its PID belongs to the expected class command.

## Rollback

### procedure
The verification items 1-5 require both processes to have been restarted first. Rollback is performed only after all desired verification is complete.
Stop the proxy if its recorded process is alive: `cd /opt/lab-classroom/class64; if test -f proxy.pid && kill -0 "$(cat proxy.pid)" 2>/dev/null; then kill "$(cat proxy.pid)"; fi`.
Stop the backend if its recorded process is alive: `cd /opt/lab-classroom/class64; if test -f backend.pid && kill -0 "$(cat backend.pid)" 2>/dev/null; then kill "$(cat backend.pid)"; fi`.
Wait for shutdown: `sleep 1`.
Confirm proxy port closure explicitly: `curl --max-time 1 -sS http://127.0.0.1:18080/hello`; the expected result is a connection failure and a nonzero exit status.
Confirm backend port closure explicitly: `curl --max-time 1 -sS http://127.0.0.1:18081/hello`; the expected result is a connection failure and a nonzero exit status.
Confirm port 18080 has no listener: `ss -ltn | grep ':18080[[:space:]]'`; the expected result is no output and grep exit status 1.
Confirm port 18081 has no listener: `ss -ltn | grep ':18081[[:space:]]'`; the expected result is no output and grep exit status 1.
Remove only class-created regular files: `cd /opt/lab-classroom/class64 && rm -f backend.py proxy.py backend.log proxy.log backend.pid proxy.pid verify-fail.json verify-headers.txt verify-502.json`.
Remove the class directory only if it is empty: `rmdir /opt/lab-classroom/class64`.

### success_condition
Neither port 18080 nor port 18081 has a listener, both curl checks fail to connect, and the class directory is absent or empty.

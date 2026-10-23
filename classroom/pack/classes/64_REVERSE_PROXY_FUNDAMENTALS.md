# Class 64: Reverse Proxy Fundamentals

**Learning objective:** Distinguish a reverse proxy from a forward proxy and from the upstream application it serves.; Trace a request from a client through a reverse proxy to an upstream backend.; Explain the purposes of Host, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto, and Via.; Explain why fixed hop-by-hop headers and headers named by Connection must not be forwarded.; Verify successful responses, upstream application failures, and proxy-generated 502 responses.; Describe trust-boundary risks associated with client-supplied forwarding headers.; Safely start, stop, verify, and remove the isolated class processes and files.
**Bloom level:** Understand / Apply
**Track:** Networking and Web Services · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Build and inspect a small HTTP reverse proxy so learners can explain request forwarding, upstream selection, forwarding headers, hop-by-hop header removal, response relaying, and bad-gateway behavior without relying on a production proxy package.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-20
**Compatibility:** ### operating_system
Linux with a proc-style process environment and loopback networking

### python
Python 3.9 or newer

### shell
POSIX-like shell with heredoc support

### tools
curl
ss
grep
nohup
kill
cat
mkdir
rmdir

### network_scope
IPv4 loopback only

### http_scope
Educational HTTP/1.1 handling with Content-Length request bodies; no TLS, chunked request decoding, streaming, or protocol upgrades

## Learning objective

- Distinguish a reverse proxy from a forward proxy and from the upstream application it serves.
- Trace a request from a client through a reverse proxy to an upstream backend.
- Explain the purposes of Host, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto, and Via.
- Explain why fixed hop-by-hop headers and headers named by Connection must not be forwarded.
- Verify successful responses, upstream application failures, and proxy-generated 502 responses.
- Describe trust-boundary risks associated with client-supplied forwarding headers.
- Safely start, stop, verify, and remove the isolated class processes and files.

## Why this matters

Build and inspect a small HTTP reverse proxy so learners can explain request forwarding, upstream selection, forwarding headers, hop-by-hop header removal, response relaying, and bad-gateway behavior without relying on a production proxy package.

## Prerequisites

- Comfort using a Linux shell and reading HTTP request and response headers.
- Python 3.9 or newer with the standard library available.
- The curl and ss commands.
- Permission to create files and launch user-owned processes under /opt/lab-classroom/class64/.
- Local TCP ports 18080 and 18081 must be available.

## Required reading

- RFC 9110, Section 3.7, Intermediaries.
- RFC 9110, Section 7.2, Host and :authority.
- RFC 9110, Section 7.6.1, Connection.
- RFC 9110, Section 7.6.3, Via.
- RFC 9110, Section 15.6.3, 502 Bad Gateway.
- RFC 9112, Section 6.3, Message Body Length.
- RFC 7239, Sections 4 through 7, Forwarded HTTP Extension.
- Python 3 documentation for http.server, http.client, and socketserver.ThreadingMixIn.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Reverse proxy | A server-facing intermediary that accepts client requests, selects an upstream service, forwards the requests, and returns the upstream responses. |
| Forward proxy | A client-facing intermediary that sends requests to destinations on behalf of clients, often for policy, privacy, or caching. |
| Upstream | The backend service to which a reverse proxy sends a request. |
| Host | The HTTP field that identifies the target host and optional port. In this lab the proxy replaces it with the backend authority when contacting the upstream. |
| X-Forwarded-For | A conventional field carrying the originating client address and, when appended correctly, the chain of forwarding intermediaries. |
| X-Forwarded-Host | A conventional field preserving the Host value received by the proxy before the proxy replaces Host for the upstream request. |
| X-Forwarded-Proto | A conventional field describing the client-facing scheme, such as http or https. |
| Via | A standardized field used by intermediaries to record protocol versions and pseudonyms. A proxy appends its entry rather than replacing existing entries. |
| Hop-by-hop header | A field that applies only to one transport connection and must not be blindly forwarded to the next connection. |
| Connection-nominated header | A header whose name appears as a token in the Connection field. That named header is hop-by-hop for the current connection and must be removed before forwarding. |
| 502 Bad Gateway | A response indicating that a gateway or proxy could not obtain a valid response from the selected upstream. |
| Trust boundary | A point where data moves between parties with different levels of trust and therefore requires validation, replacement, or controlled interpretation. |

## Instruction

A reverse proxy is an HTTP intermediary placed in front of one or more application servers. The client connects to the proxy, while the proxy opens a separate connection to an upstream. Those are two independent HTTP hops: client-to-proxy and proxy-to-backend. This distinction explains why blindly copying every header is incorrect. Connection, Keep-Alive, Proxy-Authenticate, Proxy-Authorization, TE, Trailer, Transfer-Encoding, and Upgrade are hop-by-hop fields or closely associated with connection handling. In addition, every field named by a Connection token becomes hop-by-hop for that connection. The lab proxy calculates that dynamic set for both requests and responses.

The original Host value can be useful to the application even when the proxy must send a different Host value to its upstream. This lab therefore places the client-facing value in X-Forwarded-Host and uses 127.0.0.1:18081 as the upstream Host. X-Forwarded-For records the observed client address, X-Forwarded-Proto records the client-facing scheme, and Via records the intermediary. Existing Via and X-Forwarded-For values are appended rather than silently discarded. In production, however, forwarding fields are security-sensitive. An edge proxy should remove or normalize untrusted client values before creating a trusted chain, while an internal proxy should accept such values only from explicitly trusted peers.

The proxy buffers each response body. Because the body length is then known, it removes any upstream Content-Length or Transfer-Encoding value and emits a new Content-Length matching the bytes actually sent. This prevents stale framing metadata. The proxy also relays an intentional upstream 500 response unchanged, demonstrating that an application error is not automatically a proxy failure. When no upstream connection can be established, the proxy itself generates a deterministic 502 response. This educational implementation supports ordinary HTTP/1.1 requests with Content-Length but does not implement client request streaming, chunked request decoding, protocol upgrades, WebSockets, TLS termination, load balancing, retries, health-based routing, or production hardening.

## Architecture

### flow
curl client -> class64 proxy on 127.0.0.1:18080 -> class64 backend on 127.0.0.1:18081

### client_role
Sends HTTP requests and observes status codes, headers, and JSON bodies.

### proxy_role
Selects the fixed backend, rewrites forwarding metadata, removes hop-by-hop fields, buffers responses, synthesizes Content-Length, and returns 502 when the backend is unavailable.

### backend_role
Returns diagnostic JSON for /hello and an intentional HTTP 500 JSON response for /fail.

### isolation
All created files, PID files, logs, and verification artifacts remain under /opt/lab-classroom/class64/. Both listeners bind only to 127.0.0.1.

### ports
### 18080
Client-facing reverse proxy

### 18081
Upstream backend

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Draw a sequence diagram for a successful /hello request showing the client, proxy, backend, two TCP connections, request headers, and returned status.
Modify a copy of the lab under the same class directory so the backend exposes a /whoami endpoint that returns only the forwarding fields. Predict the exact JSON before testing.
Add a second local backend on an unused port under the same workspace and describe, without claiming performance results, how path-based routing could select between the two upstreams.
Research the standardized Forwarded field from RFC 7239 and compare its syntax and trust considerations with the X-Forwarded-* convention.
Write a short production-readiness review listing at least eight capabilities this educational proxy lacks.

## Feynman teach-back

### prompt
Explain the lab to someone who knows what a web server is but has never used a reverse proxy.

### model_explanation
The client does not contact the application directly. It contacts the reverse proxy on port 18080. The proxy creates a second request to the application on port 18081 and then carries the response back. Because these are separate connections, connection-specific headers cannot simply cross from one connection to the other. The proxy also records useful information about the original request: the client address in X-Forwarded-For, the original Host in X-Forwarded-Host, the original scheme in X-Forwarded-Proto, and its own intermediary identity in Via. If the application deliberately returns 500, the proxy relays that application error. If the proxy cannot contact the application at all, the proxy creates a 502 response.

### self_check
Your explanation should identify the two TCP connections, distinguish an upstream 500 from a proxy-generated 502, and explain why forwarding fields and hop-by-hop fields receive different treatment.

## Retrieval check

1. 1. What makes a reverse proxy different from a forward proxy?
2. 2. Why does the lab proxy send Host: 127.0.0.1:18081 while also sending X-Forwarded-Host: 127.0.0.1:18080?
3. 3. If an incoming request contains `Connection: X-Lab-Hop`, what must the proxy do with the X-Lab-Hop field before forwarding?
4. 4. Why does the proxy append its Via entry instead of replacing the existing Via value?
5. 5. What is the difference between the /fail HTTP 500 result and the HTTP 502 result produced while the backend is stopped?
6. 6. Why does the proxy generate a new Content-Length after reading the complete upstream response body?
7. 7. Why should an application not automatically trust X-Forwarded-For received directly from an arbitrary client?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

Begin with the architecture diagram: the client connects to loopback port 18080, and the reverse proxy connects separately to the backend on port 18081. Emphasize that these are two HTTP hops rather than one transparent socket. Create backend.py and proxy.py with the displayed heredocs, then start both processes and verify both listeners. Request /hello through the proxy and read every JSON field. Point out that Host contains the backend authority while X-Forwarded-Host preserves the client-facing authority. Explain how X-Forwarded-For, X-Forwarded-Proto, and Via describe the route and original request context. Next, send a preexisting Via field and show that the proxy appends its entry. Send X-Lab-Hop while naming it in Connection, then show that the backend receives null because dynamically nominated hop-by-hop fields must be removed. Inspect the response headers and confirm that the backend's X-Backend-Hop field was also removed. Request /fail and explain that the backend is reachable and intentionally returned 500, so the proxy relays it. Stop the backend and repeat /hello; the proxy now creates a deterministic 502 because no upstream response was available. Restart the backend immediately and demonstrate successful recovery. Close by discussing trust boundaries, the dangers of accepting forged forwarding metadata, the implementation's educational limits, and the explicit rollback checks for both ports.

## References

- RFC 9110: HTTP Semantics, https://www.rfc-editor.org/rfc/rfc9110
- RFC 9112: HTTP/1.1, https://www.rfc-editor.org/rfc/rfc9112
- RFC 7239: Forwarded HTTP Extension, https://www.rfc-editor.org/rfc/rfc7239
- Python http.server documentation, https://docs.python.org/3/library/http.server.html
- Python http.client documentation, https://docs.python.org/3/library/http.client.html
- Python socketserver documentation, https://docs.python.org/3/library/socketserver.html

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

# Reading: Reverse Proxy Fundamentals

**Module:** Edge Access & VPN
**Activity type:** Reading (Learn)
**Objective:** Distinguish a reverse proxy from a forward proxy and from the upstream application it serves.

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

## Required reading

- RFC 9110, Section 3.7, Intermediaries.
- RFC 9110, Section 7.2, Host and :authority.
- RFC 9110, Section 7.6.1, Connection.
- RFC 9110, Section 7.6.3, Via.
- RFC 9110, Section 15.6.3, 502 Bad Gateway.
- RFC 9112, Section 6.3, Message Body Length.
- RFC 7239, Sections 4 through 7, Forwarded HTTP Extension.
- Python 3 documentation for http.server, http.client, and socketserver.ThreadingMixIn.

## References

- RFC 9110: HTTP Semantics, https://www.rfc-editor.org/rfc/rfc9110
- RFC 9112: HTTP/1.1, https://www.rfc-editor.org/rfc/rfc9112
- RFC 7239: Forwarded HTTP Extension, https://www.rfc-editor.org/rfc/rfc7239
- Python http.server documentation, https://docs.python.org/3/library/http.server.html
- Python http.client documentation, https://docs.python.org/3/library/http.client.html
- Python socketserver documentation, https://docs.python.org/3/library/socketserver.html

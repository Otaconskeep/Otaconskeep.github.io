# Homework: Reverse Proxy Fundamentals

**Module:** Edge Access & VPN
**Activity type:** Homework / independent application
**Objective:** Distinguish a reverse proxy from a forward proxy and from the upstream application it serves.

## Requirements

Draw a sequence diagram for a successful /hello request showing the client, proxy, backend, two TCP connections, request headers, and returned status.
Modify a copy of the lab under the same class directory so the backend exposes a /whoami endpoint that returns only the forwarding fields. Predict the exact JSON before testing.
Add a second local backend on an unused port under the same workspace and describe, without claiming performance results, how path-based routing could select between the two upstreams.
Research the standardized Forwarded field from RFC 7239 and compare its syntax and trust considerations with the X-Forwarded-* convention.
Write a short production-readiness review listing at least eight capabilities this educational proxy lacks.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

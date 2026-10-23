# Quiz: Reverse Proxy Fundamentals

**Module:** Edge Access & VPN
**Activity type:** Quiz / retrieval practice
**Target:** ≥80%
**Objective:** Distinguish a reverse proxy from a forward proxy and from the upstream application it serves.

## Questions

1. 1. What makes a reverse proxy different from a forward proxy?
2. 2. Why does the lab proxy send Host: 127.0.0.1:18081 while also sending X-Forwarded-Host: 127.0.0.1:18080?
3. 3. If an incoming request contains `Connection: X-Lab-Hop`, what must the proxy do with the X-Lab-Hop field before forwarding?
4. 4. Why does the proxy append its Via entry instead of replacing the existing Via value?
5. 5. What is the difference between the /fail HTTP 500 result and the HTTP 502 result produced while the backend is stopped?
6. 6. Why does the proxy generate a new Content-Length after reading the complete upstream response body?
7. 7. Why should an application not automatically trust X-Forwarded-For received directly from an arbitrary client?

## After scoring

- Missed items → return to Reading → redo Feynman Retry → reattempt.

<!-- answer key is maintained in instructor materials / automation batch report; not printed for students -->

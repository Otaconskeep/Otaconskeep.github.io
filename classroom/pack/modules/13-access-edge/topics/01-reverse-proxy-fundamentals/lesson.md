# Lesson 13.01: Reverse Proxy Fundamentals

**Module:** Edge Access & VPN
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Distinguish a reverse proxy from a forward proxy and from the upstream application it serves.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-20

## Learning objective

Distinguish a reverse proxy from a forward proxy and from the upstream application it serves.

## Why this matters

Build and inspect a small HTTP reverse proxy so learners can explain request forwarding, upstream selection, forwarding headers, hop-by-hop header removal, response relaying, and bad-gateway behavior without relying on a production proxy package.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the lab to someone who knows what a web server is but has never used a reverse proxy.

### model_explanation
The client does not contact the application directly. It contacts the reverse proxy on port 18080. The proxy creates a second request to the application on port 18081 and then carries the response back. Because these are separate connections, connection-specific headers cannot simply cross from one connection to the other. The proxy also records useful information about the original request: the client address in X-Forwarded-For, the original Host in X-Forwarded-Host, the original scheme in X-Forwarded-Proto, and its own intermediary identity in Via. If the application deliberately returns 500, the proxy relays that application error. If the proxy cannot contact the application at all, the proxy creates a 502 response.

### self_check
Your explanation should identify the two TCP connections, distinguish an upstream 500 from a proxy-generated 502, and explain why forwarding fields and hop-by-hop fields receive different treatment.

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

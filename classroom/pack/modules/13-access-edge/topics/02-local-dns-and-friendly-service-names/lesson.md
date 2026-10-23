# Lesson 13.02: Local DNS and Friendly Service Names

**Module:** Edge Access & VPN
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the roles of stub resolvers, recursive resolvers, authoritative data, and DNS caches.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain the roles of stub resolvers, recursive resolvers, authoritative data, and DNS caches.

## Why this matters

Teach learners how local DNS converts memorable service names into IP addresses, why home.arpa is the appropriate namespace for residential networks, and how to test a private DNS namespace safely without changing the host resolver or exposing a DNS service to the LAN.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain local DNS to someone who knows that computers have IP addresses but has never administered a network.

### model_explanation
A local DNS server is like a private address book. Instead of remembering that a dashboard lives at 10.20.30.40, a user asks for dashboard.home.arpa. The computer sends that question to a DNS resolver, and the resolver replies with the address stored for that name. The name can stay the same even if the service later moves to another address. Cached copies make repeated lookups faster, but they can temporarily preserve an old answer after a change. DNS only tells the client where to try connecting; it does not prove that the service is running or trusted.

### self_check
Can you distinguish a DNS answer from proof that an application is healthy?
Can you explain why two clients might temporarily receive different answers?
Can you explain why home.arpa is preferable to an invented suffix?
Can you describe why this lab uses 127.0.0.1:1053 instead of replacing the host resolver?

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

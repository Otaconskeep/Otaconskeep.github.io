# Lesson 15.01: Docker Networking

**Module:** Compose Operations & IaC
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the difference between a container port and a host-published port
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain the difference between a container port and a host-published port

## Why this matters

Teach how Docker Compose creates isolated bridge networks, provides service-name DNS, connects multi-homed services, and controls host exposure through explicit port publishing.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the lab to someone who knows basic networking but has never used Docker.

### model_explanation
Each container is like a small machine with one or more virtual network cards. The frontend network connects the client to the gateway, and the backend network connects the gateway to the database. Docker supplies a private directory service so containers on a shared network can use names such as gateway and database instead of changing IP addresses. The client cannot directly find or contact database because they do not share a network. The gateway has a virtual connection to both networks, so it can talk to each side. Port 8080 is open inside the gateway container, but it is not mapped to a port on the physical host. Therefore, other containers on frontend can use it, while host users do not receive a Docker-published endpoint.

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

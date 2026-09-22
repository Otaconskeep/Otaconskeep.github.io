# Lesson 07.04 — Ports, Protocols, and Host Firewalls

**Module:** Network Operations
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Distinguish an IP address, a transport protocol, and a port number
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-24

## Learning objective

Distinguish an IP address, a transport protocol, and a port number

## Why this matters

Teach learners how transport protocols, port numbers, listening sockets, network interfaces, connection state, and host firewall policy work together. The lab uses loopback traffic and a policy simulator so learners can observe these concepts without changing the computer's real firewall configuration.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the lesson to someone who knows that websites use networks but has never administered a server.

### model_explanation
An IP address identifies where a machine or interface can be reached, while a port helps deliver traffic to the correct program on that machine. TCP and UDP are different delivery systems, so the same port number can exist independently in both. A listening program is like someone waiting at a particular internal desk. A host firewall is a security checkpoint that decides which traffic may approach that desk. Opening the checkpoint does not place someone at the desk, and placing someone at the desk does not guarantee the checkpoint will admit visitors. Binding a service only to loopback is like making the desk reachable only from inside the building. A careful policy permits only the visitors, delivery method, and desk required for the service, then rejects unneeded traffic.

### self_check
Can you explain why TCP port 18080 and UDP port 18080 are not the same endpoint?
Can you explain why an allowed port can still appear unavailable?
Can you explain why a loopback-only bind reduces exposure?
Can you predict what happens when no firewall rule matches?

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

# Lesson 13.05: Tailscale for Homelab Remote Access

**Module:** Edge Access & VPN
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain how Tailscale separates identity and policy decisions from encrypted peer-to-peer packet transport.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain how Tailscale separates identity and policy decisions from encrypted peer-to-peer packet transport.

## Why this matters

Design and validate a least-privilege Tailscale remote-access architecture for a homelab without modifying a live tailnet. The lesson focuses on identity-based access, groups, device tags, device and route approval, narrowly scoped subnet routes, negative access tests, rollout gates, and rollback planning.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the design to a new homelab operator without using the words VPN, ACL, or zero trust.

### required_points
People receive permissions through role groups.
The router receives a device role through a tag.
Device approval decides whether the router may join, while route approval decides whether its host route may be used.
Only one legacy host is routed, so a /32 is used instead of the whole subnet.
Administrators receive two services, operators receive one, and contractors receive none.
An exit node is unnecessary because ordinary internet traffic is not part of the requirement.
Negative tests and rollback triggers prove the boundary and provide a safe stopping plan.

### self_check
If the explanation implies that an approved device automatically has permission to every destination, or that a subnet router must also be an exit node, revise it.

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

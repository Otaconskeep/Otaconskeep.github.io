# Lesson 07.02 — IP Addresses, Subnets, Gateways, and Routing

**Module:** Network Operations
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Distinguish an IPv4 address from a subnet prefix, network address, broadcast address, and usable host range
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Distinguish an IPv4 address from a subnet prefix, network address, broadcast address, and usable host range

## Why this matters

Build a practical mental model of IPv4 addressing, CIDR subnetting, default gateways, routing tables, and route selection. Learners will inspect their host configuration and use an offline Python model to calculate networks and predict routing decisions without changing any interface, route, DNS, or system networking configuration.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

Explain the lesson using a postal analogy. An IP address is a destination, while the prefix describes the local neighborhood. A host first asks whether the destination is in its own neighborhood. If it is, delivery is direct. If not, the host consults a list of directions called the routing table and chooses the most-specific applicable direction. The default gateway is the general-purpose exit used only when no more-specific direction exists. Then test the explanation with 192.168.50.77/26: .100 is in the same .64-to-.127 block, but .140 is in the next block and therefore needs a router. If the explanation cannot show why a /16 route beats a /8 route for the same destination, revisit longest-prefix matching.

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

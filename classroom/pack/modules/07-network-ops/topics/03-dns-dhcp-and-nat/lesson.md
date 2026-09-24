# Lesson 07.03: DNS, DHCP, and NAT

**Module:** Network Operations
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Describe the separate responsibilities of DNS, DHCP, and NAT
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Describe the separate responsibilities of DNS, DHCP, and NAT

## Why this matters

Explain how DNS, DHCP, and NAT cooperate in a typical homelab, then reinforce the concepts with a deterministic simulator that creates DNS records, allocates DHCP leases, and builds NAT translation entries without modifying the host network.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### exercise
Explain the system to a learner who knows what an IP address is but has never administered a network.

### model_explanation
DHCP is like a reception desk that temporarily gives each visitor a room number, directions to the exit, and the number for an information desk. DNS is the information desk that turns a memorable name into the numeric location needed to reach a service. NAT is like a mailroom shared by many rooms: outgoing packages use one building address, but the mailroom records a separate reference number so replies return to the correct room. The three systems often cooperate, but none performs the complete job of the others.

### self_check_prompts
Can you explain why a client may have a valid DHCP lease but still fail to resolve names?
Can you explain why a correct DNS answer does not prove that the destination service is reachable?
Can you explain how two internal clients can share one external IPv4 address at the same time?
Can you explain why a returning DHCP client may receive the same address?
Can you explain why changing a DNS record may not affect every client immediately?

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

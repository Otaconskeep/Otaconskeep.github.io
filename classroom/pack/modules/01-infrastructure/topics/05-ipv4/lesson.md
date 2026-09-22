# Lesson 01.05 — IPv4 addresses & gateways

**Module:** Module 1 — Infrastructure & Addressing  
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)  
**Learning objective:** Given a host, the learner can read IPv4 address, mask, and gateway; explain network vs host bits; contrast classful charts with classless `/24` math; and decide same-LAN vs via-gateway delivery.  
**Bloom level:** Understand / Apply  
**Build output:** find your host’s IPv4, mask, and gateway; explain network vs host bits with the “255 / 0” reading hack; map an address to its historic class (A–E) and default mask; calculate usable addresses on a simple `/24`; prove same-LAN vs via-gateway reachability; prove loopback with `ping 127.0.0.1`  
**Mastery unlock for this topic:** reading done + Feynman complete + quiz ≥80% (when scored) + lab gate + homework submitted

## Learning objective

Given a host, the learner can read IPv4 address, mask, and gateway; explain network vs host bits; contrast classful charts with classless `/24` math; and decide same-LAN vs via-gateway delivery.

## Why this matters

Every ‘why can’t these containers/hosts talk?’ ticket eventually becomes addressing. If you cannot read IP/mask/gateway, Docker and ARR networking stay superstition.

## Prior-knowledge check

Answer briefly before reading Instruction. Wrong answers are useful — they show what to review.

1. What does an IP address identify?
2. What is a default gateway for?
3. What is 127.0.0.1 used for?

## Learn

Complete the module reading first:

- [Reading — IPv4 addresses & gateways](./reading.md)

Then review the worked example inside that reading (I do).

## Guided practice (We do)

**We do** — hints allowed. Check your reasoning against Instruction.

Given two example IPs + `/24` mask, decide same-LAN vs needs-gateway together.

## Feynman teach-back (required)

Required. Do not skip.

### Explain
Describe **IPv4 addresses, masks, gateways, and why classful charts are history — not how modern LANs work** in your own words. No copying the lesson verbatim.

### Simplify
Explain the same idea to a 12-year-old. If you use a technical word, define it.

### Example
Analogy: street address + ZIP (network) vs apartment number (host), and the post office (gateway) for other ZIPs.

### Weak spot
What part was hard to explain? That is where your understanding is thin.

### Retry
Return to that part of **Instruction**, restudy it, then rewrite a clearer explanation below.

> Mastery note: a completed Feynman teach-back is required before the next class unlocks — “I get it” without explanation does not count.

## Reflection

Which addressing misconception did you personally hold, and what calculation corrected it?

Also answer:

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Use this whenever Class 3 Docker networks, Class 5 ARR URLs, Class 10 remote access, or Class 12 Wyoming hosts misbehave. Addressing is a permanent spiral skill.

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain / understand |
| 3 | [Lab](./lab.md) | Practice under guidance + break/fix |
| 4 | [Homework](./homework.md) | Independent apply |
| 5 | [Quiz](./quiz.md) | Test / retrieval |

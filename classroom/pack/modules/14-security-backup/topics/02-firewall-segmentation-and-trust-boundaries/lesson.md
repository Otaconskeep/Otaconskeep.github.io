# Lesson 14.02: Firewall Segmentation and Trust Boundaries

**Module:** Segmentation, Backup & Power
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Define zones as groups of systems with similar trust and policy requirements.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Define zones as groups of systems with similar trust and policy requirements.

## Why this matters

Teach learners to translate trust boundaries into ordered firewall policy, recognize first-match shadowing, distinguish RFC 1918 private networks from RFC 5737 documentation networks, and verify changes with repeatable positive and negative tests. The lab uses a file-backed policy simulator and does not modify the host firewall or network configuration.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the lab to someone who knows IP addresses but has never designed segmentation.

### model_explanation
A zone is a group of systems that should be treated similarly. Moving from one zone to another crosses a trust boundary, so the policy asks who is connecting, where the connection is going, and which protocol and port it uses. Rules are read from top to bottom, and the first matching rule decides the result. That is why an allow below a rule that denies everything never works. We gave monitoring its own private subnet and allowed only two metrics ports toward servers. We then tested not only that those flows became allowed, but also that they matched the two intended rule names and that unrelated SSH attempts stayed denied. The external example used an RFC 5737 documentation prefix, while internal zones used RFC 1918 private prefixes. Finally, we restored the original files and checked that no selected host firewall configuration changed.

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

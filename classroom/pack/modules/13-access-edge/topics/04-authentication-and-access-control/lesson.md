# Lesson 13.04: Authentication and Access Control

**Module:** Edge Access & VPN
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the difference between identification, authentication, authorization, and accounting.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain the difference between identification, authentication, authorization, and accounting.

## Why this matters

Teach homelab administrators how to distinguish authentication from authorization, design role-based permissions, apply default-deny decisions, protect stored credentials, and produce useful security audit events. The lab implements a self-contained authentication and authorization model without modifying host accounts, remote-access services, or system policy.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the system to a new homelab operator without using the words authentication or authorization at first.

### model_explanation
First, the service asks, 'Can you prove you are the identity you claimed?' After accepting that proof, it separately asks, 'Is this identity allowed to perform this exact action on this exact resource?' A valid identity may still receive a denial because proof of identity is not a universal permission grant. The system records both decisions without recording the submitted secret. In formal terms, the first decision is authentication and the second is authorization.

### self_test
Can you explain why a logged-in viewer must still be denied a service restart?
Can you explain why a salt may be stored beside a password verifier?
Can you explain why hiding an administrative control in a web page does not enforce access control?
Can you explain why the recovery process belongs inside the authentication threat model?

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

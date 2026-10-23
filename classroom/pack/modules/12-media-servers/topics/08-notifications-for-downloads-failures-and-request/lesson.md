# Lesson 12.08: Notifications for Downloads, Failures, and Requests

**Module:** Requests & Media Servers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the difference between an application event and a delivered notification.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain the difference between an application event and a delivered notification.

## Why this matters

Design and test a reliable notification pipeline for download completions, download failures, and user request events. The lesson emphasizes event normalization, severity-based routing, duplicate suppression, secret redaction, durable local queuing, dead-letter handling, and verification without contacting a real notification provider.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the pipeline to a household member who understands messaging applications but does not administer servers.

### model_explanation
An application first writes a small note saying what happened. The notification processor checks that the note has an identity and a recognized type. It removes secret values, decides who should care, and puts a safe message into an outgoing tray. It also records the note's identity so receiving the same note twice does not create two messages. If the note is malformed, the processor records only enough information to diagnose the problem. A separate delivery worker would carry messages from the outgoing tray to the messaging service. Keeping those jobs separate means a temporary messaging outage does not erase the original alert.

### self_check_questions
Why is a completed download usually routed differently from a failed download?
Why does the event need a stable identifier?
Why must redaction happen before the outbox is written?
Why is a durable outbox safer than sending directly during event processing?
Why should malformed input be represented by a digest instead of being copied without review?

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

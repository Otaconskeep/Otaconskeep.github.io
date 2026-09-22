# Lesson 06.05 — Logs and journalctl

**Module:** Linux Foundations
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the relationship between applications, systemd units, systemd-journald, and journalctl.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-20

## Learning objective

Explain the relationship between applications, systemd units, systemd-journald, and journalctl.

## Why this matters

Teach learners how systemd-journald collects Linux events and how journalctl can retrieve, filter, format, export, and interpret those events without modifying system services or journal configuration.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the journal to a new administrator as if it were a searchable event notebook. Describe who writes events, who stores them, how metadata makes them searchable, and how journalctl selects a useful subset.

### model_explanation
Programs and the kernel produce events. systemd-journald collects those events and stores each one with useful labels such as time, boot, process, unit, and severity. journalctl does not create the historical event; it asks the journal to show records matching a query. A good query first selects the relevant boot or time window, then narrows by source or severity. Because retention and permissions affect what can be seen, no output does not always mean no event occurred.

### self_check
If the explanation cannot distinguish collection by systemd-journald from querying by journalctl, review the architecture before continuing.

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

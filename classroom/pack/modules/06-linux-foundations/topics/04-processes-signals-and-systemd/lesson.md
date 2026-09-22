# Lesson 06.04 — Processes, Signals, and systemd

**Module:** Linux Foundations
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Distinguish programs, processes, threads, jobs, services, and systemd units
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Distinguish programs, processes, threads, jobs, services, and systemd units

## Why this matters

Develop a practical mental model of Linux processes, process states, signals, service supervision, and the relationship between systemd units, cgroups, and operating-system processes. The lab safely creates and controls only a purpose-built process whose persistent files remain under /opt/lab-classroom/class19/.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the lesson to someone who knows only that applications run on Linux.

### model_explanation
A program is a recipe stored on disk, and a process is a cook currently following that recipe. The kernel gives each cook a temporary number called a PID. A signal is a short instruction delivered through the kernel. SIGTERM politely asks the cook to finish safely, SIGSTOP freezes the cook, SIGCONT allows work to continue, and SIGKILL removes the cook immediately without allowing cleanup. Because PID numbers can be reused, you must check who currently owns a number before sending an instruction. systemd acts like a supervisor: it tracks services as managed units and groups their related processes together, rather than relying only on one number written in a file.

### self_check
Can you explain why a stale PID file could cause harm?
Can you explain why SIGKILL is not a stronger version of graceful shutdown?
Can you distinguish a shell job number from a kernel PID?
Can you describe how a systemd service can contain more than one process?

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

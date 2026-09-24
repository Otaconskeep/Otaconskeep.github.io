# Lesson 07.05: Network Troubleshooting Tools and Methodology

**Module:** Network Operations
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Apply a layered troubleshooting workflow from local state through application response
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Apply a layered troubleshooting workflow from local state through application response

## Why this matters

Develop a repeatable, evidence-driven method for diagnosing connectivity problems without making premature configuration changes. The lesson uses a local HTTP service to demonstrate how addressing, routing, name resolution, transport ports, listening sockets, and application behavior can be tested independently.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the diagnosis to a teammate who knows what a website is but does not know network layers.

### model_explanation
An address is like the building, and a port is like a numbered service desk inside that building. The computer knew how to reach the local building, but the client first asked for desk 18081. No one was working at that desk, so the connection was refused. We then listed the active desks and found the web service at desk 18080. Requesting the same file from 18080 returned class26-ok. That proves the route and web service worked; the original problem was the wrong desk number.

### self_check
Can you explain why successful name resolution does not prove that a service is running?
Can you explain why an HTTP 404 proves more connectivity than a timeout?
Can you identify which command tested routing, which tested listeners, and which tested the application?
Can you state what this loopback-only exercise does not prove about access from another host?

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

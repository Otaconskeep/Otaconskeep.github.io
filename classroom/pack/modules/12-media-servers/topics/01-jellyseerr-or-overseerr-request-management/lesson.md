# Lesson 12.01: Jellyseerr or Overseerr Request Management

**Module:** Requests & Media Servers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the role of Jellyseerr or Overseerr between users, a media server, and download automation
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain the role of Jellyseerr or Overseerr between users, a media server, and download automation

## Why this matters

Teach learners how to design, validate, and safely operate a media request-management service using Jellyseerr or Overseerr. The class emphasizes first-run dependencies, least-privilege request policy, media-server user synchronization, request approval, availability synchronization, Docker Compose validation, secret handling, and the distinction between detecting available media and initiating a library scan.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the system to a household member who can request a movie but does not administer the server.

### model_explanation
The request manager is a front desk. It searches a catalog, checks whether the media server already knows about the title, and applies rules to the request. A normal user can ask for an item, but an operator approves it. After approval, automation may obtain and import it. The media server must then notice the imported file through its own library process. Only after that can the request manager synchronize and show the title as available. Giving the front desk an updated availability list is not the same as asking the media server to inspect all of its shelves.

### self_check
Can the learner explain why metadata search needs a separate provider integration?
Can the learner explain why synchronized users still need role review?
Can the learner distinguish an availability refresh from a library scan?
Can the learner explain why a loopback bind reduces exposure?
Can the learner describe why the intentionally unsafe policy must fail before remediation is accepted?

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

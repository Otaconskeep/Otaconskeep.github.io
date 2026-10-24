# Lesson 15.03: Image Version Pinning and Controlled Updates

**Module:** Compose Operations & IaC
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain why a mutable tag is unsuitable as the final deployment identity.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain why a mutable tag is unsuitable as the final deployment identity.

## Why this matters

Teach operators to distinguish mutable image tags, OCI image indexes, and platform-specific manifests; deploy an immutable repository@sha256 reference; require an out-of-band approved channel, platform, and digest; prove that dry runs and rejected updates do not mutate state; record auditable digest transitions; and perform a validated rollback without destroying the backup or failed deployment evidence.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the update to a teammate without using the phrase secure because it is hashed.

### model_explanation
The stable channel points to an image index, and that index lists separate manifests for amd64 and arm64. We request linux/amd64, so only the amd64 descriptor is eligible. We verify that its bytes match its descriptor, but that alone is not approval because an attacker might replace both. We also require the digest that a reviewer supplied independently and require the same channel, platform, and digest tuple in local policy. Only after all checks agree do we write repository@sha256 for the selected amd64 manifest. The audit log records the old and new digests. A dry run or rejected update performs no write. Rollback keeps the backup, saves the failed state, verifies the approved old digest, restores it, and records the reverse digest transition.

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

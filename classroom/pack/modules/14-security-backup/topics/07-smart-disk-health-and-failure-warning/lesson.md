# Lesson 14.07: SMART, Disk Health, and Failure Warning

**Module:** Segmentation, Backup & Power
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain what SMART can and cannot predict.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-15

## Learning objective

Explain what SMART can and cannot predict.

## Why this matters

Teach operators how to interpret SATA, SAS, and NVMe health information without treating a single health flag as proof that a disk is safe. Students will learn which indicators require immediate action, which may indicate a cable or controller problem, and how to turn raw health data into useful monitoring and replacement decisions.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain disk-health monitoring to a new homelab operator without using the phrase SMART is magic.

### model_explanation
A disk keeps a maintenance notebook containing temperatures, errors, damaged locations, lifetime usage, and test history. The notebook can show warning signs, but it cannot promise that the disk will work tomorrow. The large PASSED stamp on the cover means only that the firmware's own failure rule has not been crossed. You still need to read the individual entries. Sectors that cannot be read suggest a media problem. CRC errors often suggest a problem in the cable or controller path. NVMe media errors remain important even when its Critical Warning field is zero. Keep backups, save reports over time, watch for growth, and replace suspect drives using the storage system's documented process.

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

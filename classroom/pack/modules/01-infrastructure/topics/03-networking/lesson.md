# Lesson 01.03 — Docker networking

**Module:** Module 1 — Infrastructure & Addressing  
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)  
**Learning objective:** Given two Compose services, the learner can place them on an isolated user-defined network, call one service by DNS name from the other, and explain host-port publish versus container-to-container traffic.  
**Bloom level:** Analyze  
**Build output:** isolated application network with DNS-based calls  
**Mastery unlock for this topic:** reading done + Feynman complete + quiz ≥80% (when scored) + lab gate + homework submitted

## Learning objective

Given two Compose services, the learner can place them on an isolated user-defined network, call one service by DNS name from the other, and explain host-port publish versus container-to-container traffic.

## Why this matters

Wrong networking is the #1 silent failure in ARR and Home Assistant stacks: ‘it works in the browser on the host’ but containers cannot see each other — or everything is published to the LAN by accident.

## Prior-knowledge check

Answer briefly before reading Instruction. Wrong answers are useful — they show what to review.

1. What does a port number identify?
2. What is DNS used for?
3. If two containers share a Docker network, do they need published host ports to talk to each other?

## Learn

Complete the module reading first:

- [Reading — Docker networking](./reading.md)

Then review the worked example inside that reading (I do).

## Guided practice (We do)

**We do** — hints allowed. Check your reasoning against Instruction.

With the lesson open, trace one packet path: browser → host port → container A → DNS name → container B. Label each hop.

## Feynman teach-back (required)

Required. Do not skip.

### Explain
Describe **Docker networks, DNS service discovery, and why localhost inside a container is not your PC** in your own words. No copying the lesson verbatim.

### Simplify
Explain the same idea to a 12-year-old. If you use a technical word, define it.

### Example
Analogy: apartment intercoms (container DNS) vs listing your home phone number on a billboard (publishing ports).

### Weak spot
What part was hard to explain? That is where your understanding is thin.

### Retry
Return to that part of **Instruction**, restudy it, then rewrite a clearer explanation below.

> Mastery note: a completed Feynman teach-back is required before the next class unlocks — “I get it” without explanation does not count.

## Reflection

Where did you confuse host localhost with container localhost, and how will you check DNS next time?

Also answer:

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Prowlarr→Sonarr (Class 5), HA add-ons (8–10), Wyoming voice (11–12), and n8n (14) all depend on this model. Class 15 (IPv4) explains same-LAN vs gateway when Docker networking meets your home router.

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain / understand |
| 3 | [Lab](./lab.md) | Practice under guidance + break/fix |
| 4 | [Homework](./homework.md) | Independent apply |
| 5 | [Quiz](./quiz.md) | Test / retrieval |

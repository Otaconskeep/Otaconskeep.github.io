# Lesson 05.01 — n8n homelab automation

**Module:** Module 5 — Workflow Automation (n8n)  
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)  
**Learning objective:** Given a lab-only Docker network, the learner can run n8n, build an RSS digest workflow explaining item cardinality, and require human approval before any mutating Keep Agent / SSH action.  
**Bloom level:** Apply / Evaluate  
**Build output:** n8n in Docker; RSS digest workflow; guarded Keep Agent; optional n8n→SSH→AI-CLI bridge with a resumable session  
**Mastery unlock for this topic:** reading done + Feynman complete + quiz ≥80% (when scored) + lab gate + homework submitted

## Learning objective

Given a lab-only Docker network, the learner can run n8n, build an RSS digest workflow explaining item cardinality, and require human approval before any mutating Keep Agent / SSH action.

## Why this matters

Automation without approval gates turns small mistakes into fast, wide damage — especially when agents can run commands.

## Prior-knowledge check

Answer briefly before reading Instruction. Wrong answers are useful — they show what to review.

1. What is a workflow node?
2. Why might one RSS item become five messages?
3. What must never be committed to git?

## Learn

Complete the module reading first:

- [Reading — n8n homelab automation](./reading.md)

Then review the worked example inside that reading (I do).

## Guided practice (We do)

**We do** — hints allowed. Check your reasoning against Instruction.

Trace item count through a sample RSS → split → notify path with assistance.

## Feynman teach-back (required)

Required. Do not skip.

### Explain
Describe **why n8n automations need cardinality awareness and approval gates** in your own words. No copying the lesson verbatim.

### Simplify
Explain the same idea to a 12-year-old. If you use a technical word, define it.

### Example
Analogy: a mail merge that accidentally sends 500 letters — vs a draft folder that waits for your stamp.

### Weak spot
What part was hard to explain? That is where your understanding is thin.

### Retry
Return to that part of **Instruction**, restudy it, then rewrite a clearer explanation below.

> Mastery note: a completed Feynman teach-back is required before the next class unlocks — “I get it” without explanation does not count.

## Reflection

Where could your workflow mutate something accidentally, and what gate stops it?

Also answer:

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Capstone expects guarded automation evidence. Infrastructure classes (2–4) and security (10) are prerequisites for doing this safely.

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain / understand |
| 3 | [Lab](./lab.md) | Practice under guidance + break/fix |
| 4 | [Homework](./homework.md) | Independent apply |
| 5 | [Quiz](./quiz.md) | Test / retrieval |

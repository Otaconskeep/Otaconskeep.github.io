# Lesson 04.03 — Private smart speaker

**Module:** Module 4 — Local Voice Assistant  
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)  
**Learning objective:** Given working STT/TTS providers, the learner can integrate wake → action → spoken response and prove an internet-disconnected end-to-end pass with staged gates.  
**Bloom level:** Create / Evaluate  
**Build output:** wake-to-action-to-spoken-response system that passes with internet disconnected  
**Mastery unlock for this topic:** reading done + Feynman complete + quiz ≥80% (when scored) + lab gate + homework submitted

## Learning objective

Given working STT/TTS providers, the learner can integrate wake → action → spoken response and prove an internet-disconnected end-to-end pass with staged gates.

## Why this matters

Integrate a voice satellite, wake-word engine, VAD/audio transport, Whisper, Home Assistant Assist, local intent or conversation processing, Piper, and speaker playback. The final privacy requirement is demonstrated behavior under WAN disconnection—not a marketing label.

## Prior-knowledge check

Answer briefly before reading Instruction. Wrong answers are useful — they show what to review.

1. Which Class 11 stage tests already pass?
2. What HA action will you trigger by voice?
3. How will you prove the WAN is down during the test?

## Learn

Complete the module reading first:

- [Reading — Private smart speaker](./reading.md)

Then review the worked example inside that reading (I do).

## Guided practice (We do)

**We do** — hints allowed. Check your reasoning against Instruction.

Execute the progressive integration gates in order with the checklist open.

## Feynman teach-back (required)

Required. Do not skip.

### Explain
Describe **what ‘completely local smart speaker’ actually requires** in your own words. No copying the lesson verbatim.

### Simplify
Explain the same idea to a 12-year-old. If you use a technical word, define it.

### Example
Analogy: a flashlight that still works when the power grid is down — vs one that needs a cloud app to turn on.

### Weak spot
What part was hard to explain? That is where your understanding is thin.

### Retry
Return to that part of **Instruction**, restudy it, then rewrite a clearer explanation below.

> Mastery note: a completed Feynman teach-back is required before the next class unlocks — “I get it” without explanation does not count.

## Reflection

Did the disconnected test change your architecture confidence? What remains fragile?

Also answer:

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Capstone will ask for this evidence again. n8n (14) must not sneak cloud dependencies into the voice path without labeling them.

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain / understand |
| 3 | [Lab](./lab.md) | Practice under guidance + break/fix |
| 4 | [Homework](./homework.md) | Independent apply |
| 5 | [Quiz](./quiz.md) | Test / retrieval |

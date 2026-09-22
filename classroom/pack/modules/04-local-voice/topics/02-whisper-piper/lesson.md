# Lesson 04.02 — Whisper, Piper & Wyoming

**Module:** Module 4 — Local Voice Assistant  
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)  
**Learning objective:** Given CPU/RAM constraints, the learner can deploy local Whisper (STT) and Piper (TTS) via Wyoming, benchmark them separately, and record latency/quality tradeoffs before integration.  
**Bloom level:** Apply / Evaluate  
**Build output:** local STT and TTS providers integrated and benchmarked separately  
**Mastery unlock for this topic:** reading done + Feynman complete + quiz ≥80% (when scored) + lab gate + homework submitted

## Learning objective

Given CPU/RAM constraints, the learner can deploy local Whisper (STT) and Piper (TTS) via Wyoming, benchmark them separately, and record latency/quality tradeoffs before integration.

## Why this matters

Voice feels ‘AI magic’ until a tiny host thrashes. Separate STT/TTS proof prevents false blame on Home Assistant or the satellite.

## Prior-knowledge check

Answer briefly before reading Instruction. Wrong answers are useful — they show what to review.

1. What network contract do Wyoming services need?
2. Why might a larger Whisper model be a bad choice on a small NUC?
3. What evidence proves STT alone works?

## Learn

Complete the module reading first:

- [Reading — Whisper, Piper & Wyoming](./reading.md)

Then review the worked example inside that reading (I do).

## Guided practice (We do)

**We do** — hints allowed. Check your reasoning against Instruction.

Run the STT known-sentence check with notes open; record text output.

## Feynman teach-back (required)

Required. Do not skip.

### Explain
Describe **what Whisper, Piper, and Wyoming each contribute** in your own words. No copying the lesson verbatim.

### Simplify
Explain the same idea to a 12-year-old. If you use a technical word, define it.

### Example
Analogy: ears (STT), mouth (TTS), and the headset cable standard (Wyoming).

### Weak spot
What part was hard to explain? That is where your understanding is thin.

### Retry
Return to that part of **Instruction**, restudy it, then rewrite a clearer explanation below.

> Mastery note: a completed Feynman teach-back is required before the next class unlocks — “I get it” without explanation does not count.

## Reflection

What latency/quality tradeoff did you accept, and what resource limit forced it?

Also answer:

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Class 13 demands these providers still work with the internet disconnected. Keep the separate tests — you will reuse them under failure.

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain / understand |
| 3 | [Lab](./lab.md) | Practice under guidance + break/fix |
| 4 | [Homework](./homework.md) | Independent apply |
| 5 | [Quiz](./quiz.md) | Test / retrieval |

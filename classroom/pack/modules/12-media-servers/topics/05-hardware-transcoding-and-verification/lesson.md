# Lesson 12.05: Hardware Transcoding and Verification

**Module:** Requests & Media Servers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Distinguish hardware decoding, hardware filtering, hardware encoding, and software fallback.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-20

## Learning objective

Distinguish hardware decoding, hardware filtering, hardware encoding, and software fallback.

## Why this matters

Configure and validate a hardware-accelerated video transcode without confusing codec compatibility with proof of hardware execution. The lab establishes a software baseline, exercises either VA-API or NVIDIA NVENC, captures evidence, validates the resulting media, and documents the limits of performance and quality comparisons.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain hardware transcoding to another homelab operator without using the phrase 'the GPU makes it faster.'

### model_explanation
A compressed video first has to be decoded into frames. Those frames may then be resized or otherwise filtered before a new encoder compresses them. Hardware acceleration can apply to decoding, filtering, encoding, or only one of those steps. The output file saying H.264 does not reveal whether the CPU or a hardware encoder created it. To prove the path, I check that FFmpeg supports the backend, confirm that the process can open the device, request a backend-specific decoder or encoder, save the stream mapping, and validate the finished file. I also distinguish proof of execution from proof of performance: one successful synthetic transcode demonstrates functionality on that host, but it does not establish universal speed or quality.

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

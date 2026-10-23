# Quiz: Hardware Transcoding and Verification

**Module:** Requests & Media Servers
**Activity type:** Quiz / retrieval practice
**Target:** ≥80%
**Objective:** Distinguish hardware decoding, hardware filtering, hardware encoding, and software fallback.

## Questions

1. Why does an H.264 output codec reported by FFprobe not prove that a hardware encoder was used?
2. What are the four major processing stages that may independently use hardware in a transcode pipeline?
3. Which two evidence sources in this lesson most directly identify the selected hardware encoding implementation?
4. Why can a software-only filter break an otherwise hardware-backed pipeline?
5. What does a successful full decode to FFmpeg's null muxer establish?
6. Why is low sampled GPU utilization not definitive proof that hardware acceleration failed?
7. What is the security advantage of assigning only a DRM render node to a media workload?
8. Why should equal nominal bitrates from a software encoder and hardware encoder not be assumed to have equal visual quality?
9. What must be verified separately when moving a successful host FFmpeg command into a container?
10. What conclusion is justified if the hardware command succeeds, the log names h264_vaapi or h264_nvenc, and the output passes a full decode?

## After scoring

- Missed items → return to Reading → redo Feynman Retry → reattempt.

<!-- answer key is maintained in instructor materials / automation batch report; not printed for students -->

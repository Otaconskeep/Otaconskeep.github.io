# Reading: Hardware Transcoding and Verification

**Module:** Requests & Media Servers
**Activity type:** Reading (Learn)
**Objective:** Distinguish hardware decoding, hardware filtering, hardware encoding, and software fallback.

## Vocabulary

| Term | Meaning |
|---|---|
| Transcoding | Decoding media and encoding it again, usually to change codec, resolution, bitrate, profile, or container compatibility. |
| Hardware decoder | A fixed-function or GPU-assisted component that converts a compressed video stream into frames. |
| Hardware encoder | A fixed-function or GPU-assisted component that converts frames into a compressed video stream. |
| VA-API | A Linux userspace API used by applications such as FFmpeg to access supported hardware video acceleration. |
| NVENC | NVIDIA's dedicated hardware video encoder interface, exposed in FFmpeg through encoders such as h264_nvenc. |
| Render node | A Linux DRM device, commonly under /dev/dri/, that permits non-display GPU work without granting control of the display subsystem. |
| Pixel format | The representation and layout of decoded image samples, such as yuv420p, nv12, vaapi, or cuda-backed frames. |
| Hardware frames | Video frames stored in a hardware-managed memory context rather than ordinary system memory. |
| Zero-copy path | A processing path designed to keep frames in hardware memory between decoding, filtering, and encoding, avoiding unnecessary transfers. |
| Software fallback | Processing performed by the CPU because a requested hardware stage was unavailable, unsupported, or omitted. |
| Stream mapping | FFmpeg's report of which input streams, decoders, filters, and encoders feed each output stream. |
| Backend verification | The use of logs, encoder names, hardware frame configuration, device telemetry, and successful output validation to establish which processing path actually ran. |

## Instruction

Hardware transcoding is not a single switch. A media pipeline can decode on the CPU, transfer frames to the GPU, filter on the GPU, encode in fixed-function hardware, and then copy packets into a container. It can also use hardware for only one of those stages. Therefore, seeing H.264 in the finished file does not establish that hardware acceleration occurred; H.264 identifies a codec, not the implementation that produced it. Verification begins with capability discovery. FFmpeg must list the relevant acceleration method and encoder, the operating system must expose the device, the active user must be able to open it, and the driver must support the requested codec, profile, dimensions, and pixel format.

A reliable test separates correctness from performance. First create a small deterministic source and produce a software baseline. Then run one explicitly selected hardware path and save the complete FFmpeg log. The log should show the requested backend-specific encoder, such as h264_vaapi or h264_nvenc, as well as the stream mapping and hardware frame behavior. FFprobe is then used to validate the output's codec, dimensions, pixel format, and duration. Finally, decoding the entire output to a null muxer checks that the produced stream is readable. None of these checks alone is perfect. Encoder naming confirms the selected implementation, but utilization telemetry can provide additional evidence that the expected engine was active. Conversely, a low utilization sample does not prove failure because a short or low-resolution job may finish between samples.

Hardware and software results must not be treated as quality-equivalent merely because they use the same nominal bitrate. Encoder presets, rate-control algorithms, reference-frame behavior, look-ahead, codec profiles, driver versions, and content complexity all affect quality and speed. The lab records observed behavior but does not claim universal performance. A valid conclusion is narrowly scoped: the tested host, driver, FFmpeg build, command, and source either completed through the requested backend or produced evidence explaining why it did not.

Pixel formats and memory domains cause many failures. VA-API commonly works with NV12 hardware frames, while NVIDIA CUDA paths use CUDA-backed frames. A software-only filter cannot necessarily consume those frames directly. Moving frames between system and hardware memory may require explicit upload or download filters, and every transfer can reduce the benefit of acceleration. For production media servers, verify the exact operation the application performs rather than relying on a standalone encoder test. Tone mapping, subtitle burn-in, image-based subtitles, scaling, and unsupported source formats can introduce CPU stages even when the final encoder is hardware-backed.

## Architecture

### pipeline
A generated H.264/AAC MP4 source is stored under /opt/lab-classroom/class60/.
The software baseline decodes the source, scales with a CPU filter, and encodes with libx264.
The VA-API path opens a DRM render node, requests VA-API decoding, scales hardware frames, and encodes with h264_vaapi.
The NVIDIA path requests CUDA-backed decoding, scales with scale_cuda, and encodes with h264_nvenc.
FFmpeg diagnostic output is retained in the lab directory for backend verification.
FFprobe and a full decode test validate the resulting media independently of the initial encode process.

### trust_boundaries
The FFmpeg process crosses from an ordinary user process into a kernel-managed GPU device interface.
The media application depends on the host driver and FFmpeg build rather than controlling those components itself.
A containerized media service would require an explicit device assignment and should not receive unrelated host devices.

### evidence_layers
Build evidence: FFmpeg lists the intended acceleration API and encoder.
Access evidence: the process can open the selected GPU device.
Execution evidence: the saved log identifies the backend-specific encoder and expected hardware frame path.
Telemetry evidence: optional vendor tooling observes activity during the operation.
Output evidence: FFprobe and a complete decode confirm that the generated file is structurally usable.

## Required reading

- FFmpeg documentation: Hardware Acceleration at https://ffmpeg.org/ffmpeg.html#Hardware-Acceleration
- FFmpeg Filters documentation, including hardware upload, download, and scaling filters, at https://ffmpeg.org/ffmpeg-filters.html
- FFprobe documentation at https://ffmpeg.org/ffprobe.html
- FFmpeg Codecs documentation at https://ffmpeg.org/ffmpeg-codecs.html
- Linux DRM userspace API overview at https://www.kernel.org/doc/html/latest/gpu/drm-uapi.html

## References

- FFmpeg main documentation: https://ffmpeg.org/ffmpeg.html
- FFmpeg codec documentation: https://ffmpeg.org/ffmpeg-codecs.html
- FFmpeg filter documentation: https://ffmpeg.org/ffmpeg-filters.html
- FFprobe documentation: https://ffmpeg.org/ffprobe.html
- FFmpeg wiki hardware acceleration introduction: https://trac.ffmpeg.org/wiki/HWAccelIntro
- Linux kernel DRM userspace API documentation: https://www.kernel.org/doc/html/latest/gpu/drm-uapi.html
- VA-API project repository and documentation: https://github.com/intel/libva
- NVIDIA Video Codec SDK documentation: https://developer.nvidia.com/nvidia-video-codec-sdk

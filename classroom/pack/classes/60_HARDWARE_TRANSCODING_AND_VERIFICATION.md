# Class 60: Hardware Transcoding and Verification

**Learning objective:** Distinguish hardware decoding, hardware filtering, hardware encoding, and software fallback.; Discover which hardware acceleration methods and encoders are available in the active FFmpeg build.; Create a deterministic local source clip and a software-encoded baseline.; Run a VA-API or NVIDIA hardware transcode while retaining diagnostic logs.; Validate output codec, dimensions, duration, decodability, and hardware-backend evidence.; Explain why an output codec name alone does not prove that a GPU performed the work.; Identify device-access, driver, pixel-format, filter-graph, and build-capability failures.; Apply least-privilege principles to GPU access in both host and container deployments.
**Bloom level:** Understand / Apply
**Track:** Media Services and GPU Acceleration · **Difficulty:** advanced · **Duration:** ~90 minutes · **Lab risk:** medium
**Build output:** Configure and validate a hardware-accelerated video transcode without confusing codec compatibility with proof of hardware execution. The lab establishes a software baseline, exercises either VA-API or NVIDIA NVENC, captures evidence, validates the resulting media, and documents the limits of performance and quality comparisons.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-20
**Compatibility:** ### primary_platform
Linux

### ffmpeg
Commands assume an FFmpeg build that includes libx264 plus either VA-API with h264_vaapi or NVIDIA support with h264_nvenc and scale_cuda.

### vaapi
The example assumes /dev/dri/renderD128. Systems with another render node must substitute the existing node. Codec and scaling support vary by GPU and driver.

### nvidia
The NVIDIA branch requires a compatible GPU, working host driver, NVENC-capable FFmpeg build, and support for CUDA hardware frames and scale_cuda.

### amd
Supported AMD GPUs may use the VA-API branch when the installed driver exposes the required H.264 encode and scaling capabilities.

### intel
Supported Intel GPUs may use the VA-API branch. Intel Quick Sync encoders may also be available, but QSV-specific commands are not exercised in this lab.

### virtual_machines
A virtual machine requires supported GPU passthrough, mediated-device support, or another explicitly configured acceleration mechanism. A visible virtual display adapter is not sufficient.

### containers
Container use requires explicit device exposure, appropriate group access, compatible userspace libraries, and a container FFmpeg build with the selected backend.

### unsupported_assumptions
The lesson does not assume AV1, HEVC, HDR tone mapping, subtitle composition, interlaced processing, multi-GPU selection, or session-limit behavior.

## Learning objective

- Distinguish hardware decoding, hardware filtering, hardware encoding, and software fallback.
- Discover which hardware acceleration methods and encoders are available in the active FFmpeg build.
- Create a deterministic local source clip and a software-encoded baseline.
- Run a VA-API or NVIDIA hardware transcode while retaining diagnostic logs.
- Validate output codec, dimensions, duration, decodability, and hardware-backend evidence.
- Explain why an output codec name alone does not prove that a GPU performed the work.
- Identify device-access, driver, pixel-format, filter-graph, and build-capability failures.
- Apply least-privilege principles to GPU access in both host and container deployments.

## Why this matters

Configure and validate a hardware-accelerated video transcode without confusing codec compatibility with proof of hardware execution. The lab establishes a software baseline, exercises either VA-API or NVIDIA NVENC, captures evidence, validates the resulting media, and documents the limits of performance and quality comparisons.

## Prerequisites

- A Linux homelab host with a writable, pre-provisioned /opt/lab-classroom/class60/ directory.
- FFmpeg and FFprobe installed with the intended hardware backend enabled.
- For VA-API, a supported Intel or AMD GPU with an accessible DRM render node such as /dev/dri/renderD128.
- For NVIDIA, a supported GPU, a functioning host driver, and FFmpeg built with the NVENC encoder.
- Permission to access the selected GPU device without changing host permissions during the lab.
- Familiarity with codecs, containers, pixel formats, shell pipelines, and reading FFmpeg stream mappings.

## Required reading

- FFmpeg documentation: Hardware Acceleration at https://ffmpeg.org/ffmpeg.html#Hardware-Acceleration
- FFmpeg Filters documentation, including hardware upload, download, and scaling filters, at https://ffmpeg.org/ffmpeg-filters.html
- FFprobe documentation at https://ffmpeg.org/ffprobe.html
- FFmpeg Codecs documentation at https://ffmpeg.org/ffmpeg-codecs.html
- Linux DRM userspace API overview at https://www.kernel.org/doc/html/latest/gpu/drm-uapi.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

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

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Using only files under /opt/lab-classroom/class60/, generate a second synthetic source at a different supported resolution and repeat the same selected hardware path. Compare the two FFmpeg logs and explain how frame size, transfer overhead, filter selection, rate control, and clip duration could affect observed results.

### deliverable
Create /opt/lab-classroom/class60/homework-report.txt containing the exact commands, selected backend, capability evidence, output probe results, decode-validation result, and a paragraph separating verified facts from hypotheses.

### constraints
Do not install packages or alter drivers as part of the assignment.
Do not change device ownership or permissions.
Do not use private media.
Do not present a single run as a general benchmark.
Keep every generated artifact under /opt/lab-classroom/class60/.

## Feynman teach-back

### prompt
Explain hardware transcoding to another homelab operator without using the phrase 'the GPU makes it faster.'

### model_explanation
A compressed video first has to be decoded into frames. Those frames may then be resized or otherwise filtered before a new encoder compresses them. Hardware acceleration can apply to decoding, filtering, encoding, or only one of those steps. The output file saying H.264 does not reveal whether the CPU or a hardware encoder created it. To prove the path, I check that FFmpeg supports the backend, confirm that the process can open the device, request a backend-specific decoder or encoder, save the stream mapping, and validate the finished file. I also distinguish proof of execution from proof of performance: one successful synthetic transcode demonstrates functionality on that host, but it does not establish universal speed or quality.

## Retrieval check

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

## Guided lab

### scope_rule
Every file or directory created, changed, or removed by this lab must remain under /opt/lab-classroom/class60/. Package installation, driver changes, service configuration, and permission changes are outside the lab scope.

### steps
### step
1

### title
Initialize the lab workspace

### instructions
Confirm that /opt/lab-classroom/class60/ was pre-provisioned for your account.
Run: mkdir -p /opt/lab-classroom/class60
Run: printf '%s\n' "Class 60 hardware transcoding evidence" > /opt/lab-classroom/class60/README.txt
Run: ffmpeg -version > /opt/lab-classroom/class60/ffmpeg-version.txt 2>&1
### step
2

### title
Discover available hardware interfaces

### instructions
Run: ffmpeg -hide_banner -hwaccels 2>&1 | tee /opt/lab-classroom/class60/hwaccels.txt
Run: ffmpeg -hide_banner -encoders 2>&1 | grep -E 'h264_(vaapi|nvenc|qsv)|hevc_(vaapi|nvenc|qsv)' | tee /opt/lab-classroom/class60/hardware-encoders.txt
For a VA-API host, run: ls -l /dev/dri 2>&1 | tee /opt/lab-classroom/class60/dri-devices.txt
For an NVIDIA host, run: nvidia-smi 2>&1 | tee /opt/lab-classroom/class60/nvidia-status.txt
Select exactly one hardware branch that is listed by FFmpeg and supported by the host.
### step
3

### title
Generate a deterministic source clip

### instructions
Run: ffmpeg -hide_banner -y -f lavfi -i testsrc2=size=1280x720:rate=30 -f lavfi -i sine=frequency=1000:sample_rate=48000 -t 10 -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 128k /opt/lab-classroom/class60/source.mp4 > /opt/lab-classroom/class60/source-generation.log 2>&1
Run: ffprobe -v error -show_entries stream=index,codec_type,codec_name,width,height,pix_fmt -show_entries format=duration -of default=noprint_wrappers=1 /opt/lab-classroom/class60/source.mp4 | tee /opt/lab-classroom/class60/source-probe.txt
### step
4

### title
Create a software baseline

### instructions
Run: ffmpeg -hide_banner -y -benchmark -i /opt/lab-classroom/class60/source.mp4 -vf scale=854:480 -c:v libx264 -preset medium -b:v 2M -c:a copy /opt/lab-classroom/class60/software-output.mp4 > /opt/lab-classroom/class60/software-transcode.log 2>&1
Treat the recorded timing as an observation for this host and run only, not as a general benchmark.
### step
5

### title
Run the VA-API branch if selected

### instructions
Confirm that vaapi appears in hwaccels.txt, h264_vaapi appears in hardware-encoders.txt, and the selected render node exists.
Run: ffmpeg -hide_banner -y -benchmark -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi -i /opt/lab-classroom/class60/source.mp4 -vf 'scale_vaapi=w=854:h=480:format=nv12' -c:v h264_vaapi -b:v 2M -c:a copy /opt/lab-classroom/class60/hardware-output.mp4 > /opt/lab-classroom/class60/hardware-transcode.log 2>&1
If the render node differs, substitute the correct existing node without changing device permissions.
### step
6

### title
Run the NVIDIA branch if selected

### instructions
Confirm that cuda appears in hwaccels.txt, h264_nvenc appears in hardware-encoders.txt, and nvidia-smi reports a working device.
Run: ffmpeg -hide_banner -y -benchmark -hwaccel cuda -hwaccel_output_format cuda -i /opt/lab-classroom/class60/source.mp4 -vf 'scale_cuda=854:480' -c:v h264_nvenc -b:v 2M -c:a copy /opt/lab-classroom/class60/hardware-output.mp4 > /opt/lab-classroom/class60/hardware-transcode.log 2>&1
### step
7

### title
Validate the hardware output

### instructions
Run only after the selected hardware command exits successfully.
Run: ffprobe -v error -show_entries stream=index,codec_type,codec_name,width,height,pix_fmt -show_entries format=duration -of default=noprint_wrappers=1 /opt/lab-classroom/class60/hardware-output.mp4 | tee /opt/lab-classroom/class60/hardware-probe.txt
Run: ffmpeg -hide_banner -v error -i /opt/lab-classroom/class60/hardware-output.mp4 -map 0:v:0 -f null - > /opt/lab-classroom/class60/hardware-decode-check.log 2>&1
Run: grep -E 'h264_vaapi|h264_nvenc|Stream mapping|frame=|bench:' /opt/lab-classroom/class60/hardware-transcode.log > /opt/lab-classroom/class60/hardware-evidence.txt
Run: sha256sum /opt/lab-classroom/class60/source.mp4 /opt/lab-classroom/class60/software-output.mp4 /opt/lab-classroom/class60/hardware-output.mp4 > /opt/lab-classroom/class60/checksums.sha256
### step
8

### title
Record the conclusion

### instructions
Create /opt/lab-classroom/class60/conclusion.txt and state the selected backend, device, FFmpeg version, output properties, whether the complete decode check was clean, and which log lines demonstrate the hardware encoder.
Do not claim that the entire pipeline was hardware accelerated unless the command and log demonstrate hardware decoding, hardware-compatible filtering, and hardware encoding.
Do not claim a universal speed or quality advantage from this single synthetic clip.

## Expected results

- The workspace contains the generated source, software baseline, capability reports, logs, and verification artifacts.
- FFmpeg capability discovery lists at least one backend-specific encoder selected for the hardware branch.
- The source probe reports one H.264 video stream at 1280x720 and an audio stream generated by the lab.
- The software baseline is created at 854x480 using libx264.
- On a correctly configured compatible host, the selected hardware branch exits successfully and creates hardware-output.mp4.
- The hardware output probe reports an H.264 video stream at 854x480 and a duration close to the ten-second source duration.
- The saved transcode log names h264_vaapi or h264_nvenc according to the selected branch.
- The complete decode check produces no error messages for a valid output.
- Observed timing may differ between systems and is not expected to match any fixed value.

## Verification checkpoints

- [ ] Confirm that all lab-created artifacts are located under /opt/lab-classroom/class60/.
- [ ] Run: test -s /opt/lab-classroom/class60/source.mp4 && test -s /opt/lab-classroom/class60/software-output.mp4 && test -s /opt/lab-classroom/class60/hardware-output.mp4
- [ ] Run: grep -E 'h264_vaapi|h264_nvenc' /opt/lab-classroom/class60/hardware-transcode.log
- [ ] Run: ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height -of csv=p=0 /opt/lab-classroom/class60/hardware-output.mp4
- [ ] Verify that the preceding probe reports h264,854,480, allowing for FFprobe's field ordering as displayed by the local build.
- [ ] Run: ffmpeg -hide_banner -v error -i /opt/lab-classroom/class60/hardware-output.mp4 -map 0:v:0 -f null -
- [ ] Confirm that the full decode command exits successfully and prints no decoding errors.
- [ ] Review hardware-evidence.txt and confirm that the selected hardware encoder appears in the stream mapping.
- [ ] Compare source-probe.txt and hardware-probe.txt to confirm that the intended resolution change occurred.
- [ ] Document whether hardware decoding, hardware filtering, and hardware encoding were each explicitly requested; do not infer all three from the output codec.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| FFmpeg reports that the requested encoder is unknown. | The installed FFmpeg build was compiled without that encoder, or the encoder name was typed incorrectly. | Review hardware-encoders.txt and select only an encoder listed by the active FFmpeg binary. Rebuilding or replacing FFmpeg is outside this lab and must follow the host's normal change process. |
| The VA-API command reports that it cannot open /dev/dri/renderD128. | The render node is absent, a different node is in use, the driver did not initialize, or the current account lacks device access. | Inspect dri-devices.txt, identify the correct render node, and verify account membership in the host's GPU-access group. Do not broaden device permissions as a shortcut. |
| The VA-API command fails with an unsupported profile, entry point, or surface format. | The driver or GPU does not support the requested codec operation, profile, dimensions, or pixel format. | Confirm device capabilities with host-supported VA-API diagnostic tooling, retain NV12 where required, and test a codec and profile actually supported by the hardware. |
| The filter graph reports that software and hardware pixel formats cannot be connected. | Frames are crossing between system memory and hardware memory without a compatible upload, download, or hardware-native filter. | Use the backend-native scaling filter shown in the lab, or explicitly design the required transfer with the appropriate hardware frame filters. Recheck the log after every filter-graph change. |
| The NVIDIA command reports that no capable devices were found. | The driver is unavailable, the device is not exposed to the environment, the GPU lacks the requested NVENC generation, or the FFmpeg build and driver are incompatible. | Confirm that nvidia-smi succeeds, that the GPU model supports the requested codec, and that the application environment can see the device. |
| The command succeeds, but GPU telemetry shows little or no sampled utilization. | The clip is too short, sampling missed the operation, the selected metric monitors a different engine, or only one pipeline stage used hardware. | Use the saved FFmpeg log as primary evidence, select a telemetry view for the video engine, and if policy permits, repeat the same lab command with a longer source generated inside the lab directory. |
| The output file exists but the decode validation reports errors. | The transcode was interrupted, the muxer did not finalize, the driver produced an invalid stream, or storage was exhausted. | Inspect the end of hardware-transcode.log, verify available storage through read-only inspection, remove only the failed lab output through the documented rollback process, and rerun the selected branch. |
| The hardware run is not faster than the software baseline. | Startup overhead, transfers between memory domains, a short synthetic source, different encoder behavior, filtering, or host contention dominates the test. | Do not classify the run as failed based on speed alone. Verify backend use and output correctness, then evaluate representative production media under a separately approved test plan. |
| Subtitles or tone mapping in a media server cause CPU use even though this lab succeeds. | The production filter chain includes operations unsupported by the selected hardware backend or requires frame transfers. | Reproduce the application's exact codec, subtitle, scaling, and tone-mapping path and inspect its complete FFmpeg command and logs. |

## Security considerations

### principles
Grant access only to the render or video device required by the media workload.
Prefer render nodes over interfaces that unnecessarily expose display-control capabilities.
Use normal GPU-access group membership or an orchestrator's explicit device assignment rather than globally writable device nodes.
Treat media files as untrusted input because malformed codecs and containers exercise complex parsers and drivers.
Keep the kernel, GPU driver, FFmpeg, and media application within supported security maintenance windows.
Avoid privileged containers for transcoding; map only the required GPU device and retain the smallest practical capability set.
Do not expose vendor management interfaces to unrelated workloads merely to enable video encoding.
Preserve logs without including private filenames, user paths, media titles, or tokens when sharing troubleshooting evidence.

### container_note
A successful host-side test proves that the host stack can work, but it does not prove that a container has the correct device mapping, supplemental groups, driver libraries, or FFmpeg build. Verify those layers independently.

### data_handling
This lab uses generated synthetic media so that evidence files can be shared without disclosing personal content.

## Rollback

### impact
Rollback removes only artifacts created under the dedicated class directory. It does not change drivers, packages, users, groups, services, or device configuration.

### precheck
Run: find /opt/lab-classroom/class60 -mindepth 1 -maxdepth 1 -printf '%f\n'

### command
find /opt/lab-classroom/class60 -mindepth 1 -maxdepth 1 -delete

### postcheck
Run: find /opt/lab-classroom/class60 -mindepth 1 -maxdepth 1 -print

### success_condition
The postcheck prints nothing and the class60 directory itself still exists.

## Video narration notes

Welcome to Class 60, Hardware Transcoding and Verification. In this lesson, we will avoid the most common verification mistake: assuming that an H.264 output automatically proves GPU use. A codec is a format, while an encoder is an implementation. The CPU-based libx264 encoder, VA-API hardware encoders, and NVIDIA NVENC can all produce H.264.

We begin by recording the active FFmpeg version and discovering its hardware acceleration methods and backend-specific encoders. This matters because installed hardware is not enough. FFmpeg must have been built with the corresponding interface, the driver must expose the required capability, and the current process must be able to access the device.

Next, we generate a short synthetic source. This keeps the lab repeatable and avoids exposing private media. We produce a software baseline, then select either the VA-API branch or the NVIDIA branch. The VA-API command keeps decoded frames in a VA-API hardware context and uses the hardware-native scaling filter before h264_vaapi encoding. The NVIDIA command requests CUDA-backed frames, uses CUDA scaling, and sends the result to h264_nvenc.

The saved FFmpeg log is essential evidence. We inspect its stream mapping for the backend-specific encoder, but we do not stop there. FFprobe confirms the output codec, dimensions, pixel format, and duration. A complete decode to the null muxer checks that the entire output video can be decoded without errors. Optional device telemetry can strengthen the evidence, although short jobs can be missed by slow sampling.

Finally, we document a narrow conclusion. A successful result proves that this host, driver, FFmpeg build, command, and source worked with the selected encoder. It does not prove that all media-server operations will remain on the GPU. Subtitle burn-in, tone mapping, unsupported codecs, and software filters can introduce CPU stages or frame transfers. It also does not establish a universal performance or quality advantage. Good homelab engineering records what was actually tested, preserves the evidence, and avoids claims broader than the evidence supports.

## References

- FFmpeg main documentation: https://ffmpeg.org/ffmpeg.html
- FFmpeg codec documentation: https://ffmpeg.org/ffmpeg-codecs.html
- FFmpeg filter documentation: https://ffmpeg.org/ffmpeg-filters.html
- FFprobe documentation: https://ffmpeg.org/ffprobe.html
- FFmpeg wiki hardware acceleration introduction: https://trac.ffmpeg.org/wiki/HWAccelIntro
- Linux kernel DRM userspace API documentation: https://www.kernel.org/doc/html/latest/gpu/drm-uapi.html
- VA-API project repository and documentation: https://github.com/intel/libva
- NVIDIA Video Codec SDK documentation: https://developer.nvidia.com/nvidia-video-codec-sdk

## Mastery gate

- [ ] Objectives demonstrated with evidence
- [ ] Feynman complete
- [ ] Quiz self-scored ≥80%
- [ ] Lab verification boxes checked
- [ ] Rollback understood

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Return to this class whenever a later service fails for identity, process, log, remote access, update, or routing reasons covered here.

# Lab: Hardware Transcoding and Verification

**Module:** Requests & Media Servers
**Activity type:** Lab (Practice)
**Lab risk:** medium
**Objective:** Distinguish hardware decoding, hardware filtering, hardware encoding, and software fallback.

## Before you start

- A Linux homelab host with a writable, pre-provisioned /opt/lab-classroom/class60/ directory.
- FFmpeg and FFprobe installed with the intended hardware backend enabled.
- For VA-API, a supported Intel or AMD GPU with an accessible DRM render node such as /dev/dri/renderD128.
- For NVIDIA, a supported GPU, a functioning host driver, and FFmpeg built with the NVENC encoder.
- Permission to access the selected GPU device without changing host permissions during the lab.
- Familiarity with codecs, containers, pixel formats, shell pipelines, and reading FFmpeg stream mappings.

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

## Verification

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

## Security

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

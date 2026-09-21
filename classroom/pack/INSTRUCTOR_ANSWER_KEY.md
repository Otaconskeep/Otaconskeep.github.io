# Instructor Answer Key and Acceptance Guidance

These are model answers. Equivalent technically correct explanations are acceptable. Practical evidence outweighs memorized wording.

## Class 1

1. Host is the physical system/hypervisor environment; guest is the managed virtual system.  
2. VM.  
3. A virtual Ethernet switch/bridge.  
4. It separates working IP routing from failed name resolution.  
5. It provides a clear, supported isolation boundary and avoids teaching nested LXC/Docker complexities first.

Reject a practical pass if the student cannot identify the target installation disk, uses a guessed IP, or treats one successful browser load as proof of DNS and SSH.

## Class 2

1. Containers are replaceable; writable-layer data can disappear during recreation.  
2. `8080`.  
3. The Compose model parses/renders; it does not prove runtime health.  
4. No.  
5. Image is the reusable artifact; container is an instance.  
6. Host ownership/mode, numeric UID/GID, read-only mount, or security labeling can deny writes.

Require an actual destroy/recreate or `down`/`up` persistence demonstration.

## Class 3

1. The Sonarr container itself.  
2. It supplies scoped networking and embedded service-name DNS.  
3. No, not when containers share a network.  
4. Multi-host orchestrated container networking.  
5. It changes isolation/exposure and can create conflicts; it masks design errors.

Require a name-resolution test and proof that an unexposed service is unavailable from the LAN.

## Class 4

1. Process state does not prove application, dependencies, or user transaction.  
2. Data whose loss cannot be recreated from another trusted source.  
3. It moves and does not identify the last-known-good bytes.  
4. Version, config/data backup, health baseline, and acceptance result.  
5. It can delete persistent data volumes.

Require update and rollback, not only a written procedure.

## Class 5

1. Prowlarr manages indexers/sync; Sonarr/Radarr own monitored content, selection policy, handoff, and import.  
2. API reachability can succeed while configuration is not synchronized.  
3. Separates queues and connects completed jobs to the intended importer.  
4. It reduces translation and hardlink/remote-path mistakes.  
5. Device and inode.  
6. RSS covers new feed items, not all historical possibilities.

Do not require a copyrighted download. Authorized test data or connection/search evidence is acceptable.

## Class 6

1. Quality is a built-in source/encode classification; CF matches additional traits.  
2. Rules overlap and scores accumulate.  
3. When quality-driven upgrades stop.  
4. Endless or unnecessary upgrade attempts.  
5. HDR/audio/resolution choices must match the playback chain and resources.  
6. No.

Require observed candidate rankings and written local policy.

## Class 7

1. Difference between declared and observed configuration.  
2. It exposes unwanted duplication or non-convergent behavior.  
3. A completed write does not prove resulting selection behavior.  
4. Oscillation or one overwrites the other.  
5. Rejections, cutoff/upgrade targets, size definitions, deletions, and major tool updates.  
6. After preview, impact review, staged application, and behavioral verification.

Require backup and restoration evidence.

## Class 8

1. Device is a represented product; entity is one state/control surface.  
2. OS is a managed appliance with Supervisor/add-ons; Container is Core managed by the operator's Docker environment.  
3. Unavailable means state cannot be determined, not that the device is off.  
4. Known scope, off-instance copy, protected recovery information, and tested restore process.  
5. Areas improve target resolution, naming, dashboards, and voice commands.

## Class 9

1. Trigger starts evaluation; condition permits or blocks action.  
2. It proves the guard prevents unwanted behavior.  
3. When the newest trigger should replace a still-running older execution.  
4. Which path and data the automation evaluated.  
5. To prevent thrashing, erase less evidence, and escalate persistent faults.

Require positive, negative, and restart/reload evidence.

## Class 10

1. No. Authorization policy is separate.  
2. They hold powerful API/admin controls and are not designed as public consumer endpoints.  
3. The internal destination served through the connector/proxy.  
4. Loss/misconfiguration of the access path denies external access rather than bypassing controls.  
5. It supports least privilege, revocation, and attribution.  
6. External access fails while local service can remain available.

Any direct unauthenticated public ARR/admin port is an automatic failure.

## Class 11

1. The action could succeed despite a poor transcript in another trial; inspect the STT artifact directly.  
2. Speech start/end detection and captured utterance boundary.  
3. Transcript paired with source audio.  
4. To separate synthesis from device routing/volume/playback.  
5. Microphone, wake, VAD, STT, text-only intent/action, TTS, and playback.

## Class 12

1. Wyoming transports/coordinates compatible voice-service interactions; Whisper performs STT inference.  
2. Model load/cache effects change latency.  
3. It does not prove protocol, model, inference, or output quality.  
4. Metadata defines compatible voice/model configuration.  
5. Resource contention for memory, compute, and thermals.  
6. One variable.

## Class 13

1. Successful defined operation while WAN is disconnected, with traffic/dependency evidence.  
2. The test targets cloud dependence, not intentional destruction of local routing.  
3. Deterministic safety/home-control commands where supported.  
4. It identifies where to observe and repair each boundary.  
5. Wake, end-of-speech, transcript, intent, state change, synthesis, playback.  
6. Least privilege and reduced accidental control.

The capstone cannot pass if only text input works or if the offline test is skipped.

## Grading rubric

| Dimension | Weight |
|---|---:|
| Architecture explanation | 15% |
| Correct build and configuration | 25% |
| Verification evidence | 25% |
| Fault isolation and repair | 20% |
| Security, backup, and rollback | 15% |

Minimum pass: 80% overall and no critical safety/security failure.


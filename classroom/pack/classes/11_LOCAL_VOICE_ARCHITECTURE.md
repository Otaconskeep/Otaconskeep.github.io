# Class 11 — Local Voice Architecture and Fault Isolation

**Lecture (optional):** [Everything Smart Home — Local Smart Home Voice](https://www.youtube.com/watch?v=w9BbjUowmnE)
**Time:** 120 minutes
**Learning objective:** Given a voice request, the learner can draw the local Assist pipeline stages, instrument one test per stage, and isolate faults to mic, wake, STT, intent/action, TTS, or playback.
**Bloom level:** Analyze
**Build output:** voice-pipeline test record with one test per stage
**Mastery unlock:** ≥80% retrieval target when scored + completed Feynman teach-back + independent practice + all practical gate boxes + workbook evidence.

## Learning objective

Given a voice request, the learner can draw the local Assist pipeline stages, instrument one test per stage, and isolate faults to mic, wake, STT, intent/action, TTS, or playback.

## Why this matters

Never test the entire voice pipeline first. Each stage transforms an input into an output. Capture the boundary result and prove it before moving forward.

```mermaid
flowchart TD
    H["Human speech"] --> M["Microphone"]
    M --> W["Wake word"]
    W --> V["VAD + audio capture"]
    V --> S["STT"]
    S --> C["Conversation / intent"]
    C --> A["Home Assistant action"]
    A --> T["TTS"]
    T --> P["Speaker"]
```

## Prior-knowledge check

Answer briefly before reading Instruction. Wrong answers are useful — they show what to review.

1. What does STT mean? TTS?
2. Why test stages independently before the full pipeline?
3. Which HA entities will voice actions target (from Class 8–9)?

## Vocabulary

| Acronym | Meaning | Boundary output |
|---|---|---|
| VAD | Voice Activity Detection | Start/end of utterance |
| STT/ASR | Speech to Text / Automatic Speech Recognition | Transcript |
| NLU | Natural-language understanding | Intent and slots/entities |
| HA | Home Assistant | State/action result |
| TTS | Text to Speech | Audio waveform/stream |
| Wake word | Local keyword detector | Detection event |

## Instruction

### Signal chain

Microphone quality, gain, distance, echo, noise, sample format, and clipping affect everything downstream. An LLM cannot recover words that were never captured. Begin with a recorded audio sample and listen to it.

### Wake word

Wake-word detection should occur before expensive STT in a typical always-listening satellite. Tune for the environment: too sensitive causes false activations; not sensitive enough causes misses. Measure both false rejects and false accepts.

### VAD and endpointing

VAD determines when speech begins and ends. If endpointing cuts early, the transcript may miss the final noun. If it waits too long, latency increases. Diagnose timing from captured audio length and pipeline timestamps.

### STT

STT turns captured audio into text. Its test result is the transcript, not whether a light eventually changes. Use a known sentence and acceptance rule.

### Conversation and intent

The conversation layer interprets text. Deterministic home-control sentences should produce a clear intent and target. Open-ended LLM responses and smart-home commands may use different agents or routing policies.

### Action

Home Assistant must be able to perform the action from text/manual developer tools before voice is involved.

### TTS and playback

TTS produces audio; the output device must play it. Test synthesis and playback separately so a muted speaker is not blamed on Piper.

### Acceptance criteria example

```text
Wake detect ≥ 8/10 at 1m
False wakes ≤ 1/10
STT exact match ≥ 4/5 fixed phrases
Assist maps to correct intent 5/5 when given perfect text
TTS intelligible 5/5
E2E success ≥ 7/10 from seating position
```

### Symptom-to-layer diagnosis

| Symptom | Check layer first |
|---|---|
| Never wakes | Mic / wake model |
| Wakes but silence | VAD / transport |
| Wrong words | STT / noise / model |
| Right words, wrong action | Assist / expose entities |
| Action ok, no voice back | TTS / speaker |

## Worked example

**I do** — study the reasoning, not just the final answer.

**Bad debug:** “Voice is broken” → reinstall everything.

**Better:** Stage table — mic level OK? wake fired? STT text correct? intent matched? action ran? TTS audio generated? speaker played? Fix the first failing stage only.

## Guided practice

**We do** — hints allowed. Check your reasoning against Instruction.

Fill the stage table for a sample phrase with assistance.

## Independent practice

**You do** — close the hints. Solve before opening the lab.

Create your pipeline test record template with one pass/fail line per stage. Run it once on a known sentence.

## Feynman teach-back

Required. Do not skip.

### Explain
Describe **the local voice signal chain and fault isolation** in your own words. No copying the lesson verbatim.

### Simplify
Explain the same idea to a 12-year-old. If you use a technical word, define it.

### Example
Analogy: a relay race — you must know which runner dropped the baton.

### Weak spot
What part was hard to explain? That is where your understanding is thin.

### Retry
Return to that part of **Instruction**, restudy it, then rewrite a clearer explanation below.

> Mastery note: a completed Feynman teach-back is required before the next class unlocks — “I get it” without explanation does not count.


## Retrieval check

Active recall — write answers without rereading first. Target ≥80% before the gate.

1. Why does a correct HA action not prove STT quality?
2. What does VAD control?
3. Which artifact proves STT behavior?
4. Why test TTS synthesis separately from playback?
5. What should be tested before adding an LLM conversation agent?

## Guided lab

Test the voice chain **one layer at a time**. Do not run full wake→action until layers 1–10 pass.

1. **Record raw mic audio** (arecord/Audacity/Phone). Confirm intelligible, not clipped.

:::linux
```bash
# Example if ALSA device exists on the satellite/host:
arecord -l
arecord -d 5 -f cd /tmp/voice-raw.wav
aplay /tmp/voice-raw.wav
ls -l /tmp/voice-raw.wav
```
:::

:::windows
```powershell
# Record with Voice Recorder / Audacity; save to Desktop\voice-raw.wav
Get-Item $HOME\Desktop\voice-raw.wav | Format-List Name, Length, LastWriteTime
```
:::

2. **Wake word:** 10 attempts at fixed distance → record detections / misses.

3. **False activations:** 10 unrelated phrases → record false wakes.

4. **VAD/endpointing:** confirm start/end do not chop words (inspect recording or pipeline debug).

5. **STT alone:** submit the same audio/phrase to configured STT; save transcript text in workbook.

6. **Assist text path:** paste that exact transcript into HA Assist; record intent + target entity.

7. **Action alone:** call the HA service manually; confirm entity changes.

8. **TTS alone:** synthesize a fixed phrase; confirm audio file/stream exists.

9. **Playback alone:** play a known WAV/MP3 on the target speaker.

:::linux
```bash
aplay /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null || ffplay -autoexit -nodisp /tmp/test.wav
```
:::

10. **Full pipeline** only after 1–9 pass. Time wake→action latency; log failures by layer.

## Break / fix

### Break/fix

Mute mic; confirm wake fails. Unmute. Play TTS with speaker unplugged; confirm synthesis may succeed while playback fails—record both.

## Feedback / common mistakes

- Skipping evidence and calling it done.
- Changing multiple variables before retesting.
- Moving on without completing Feynman teach-back.

## Practical mastery gate

All boxes must be true before the next class unlocks. If you fail: feedback → targeted review → new practice → reassess.

- [ ] Raw microphone sample is acceptable.
- [ ] Wake-word hit/miss evidence is recorded.
- [ ] STT transcript meets criterion.
- [ ] Text-only HA command works.
- [ ] TTS and speaker pass separately.
- [ ] Stage timestamps identify latency.
- [ ] End-to-end command passes.
- [ ] Prior-knowledge check answered
- [ ] Feynman teach-back completed (Explain, Simplify, Example, Weak spot, Retry)
- [ ] Independent practice completed
- [ ] Retrieval check attempted (target ≥80% when scored)
- [ ] Evidence recorded in workbook / verification matrix

## Reflection

Which stage is hardest to observe, and what log or UI proves it?

Also answer:

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Classes 12–13 implement STT/TTS and the full speaker. Every failure report should cite a Class 11 stage name.

## 2026 correction

Home Assistant voice pipelines and supported hardware continue to evolve. Use current HA voice documentation for UI and integration steps; preserve boundary testing regardless of the selected satellite or agent.

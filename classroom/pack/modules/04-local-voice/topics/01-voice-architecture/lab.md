# Lab — Local voice architecture

**Module:** Module 4 — Local Voice Assistant  
**Activity type:** Lab (Practice)  
**Objective:** Given a voice request, the learner can draw the local Assist pipeline stages, instrument one test per stage, and isolate faults to mic, wake, STT, intent/action, TTS, or playback.

## Before you start

- Reading complete
- Lesson Feynman teach-back drafted (you may refine after the lab)

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

## Lab gate

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

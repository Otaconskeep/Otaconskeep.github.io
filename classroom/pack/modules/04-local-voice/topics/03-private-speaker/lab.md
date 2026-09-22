# Lab — Private smart speaker

**Module:** Module 4 — Local Voice Assistant  
**Activity type:** Lab (Practice)  
**Objective:** Given working STT/TTS providers, the learner can integrate wake → action → spoken response and prove an internet-disconnected end-to-end pass with staged gates.

## Before you start

- Reading complete
- Lesson Feynman teach-back drafted (you may refine after the lab)

## Guided lab

Complete gates **in order**. Do not skip to end-to-end.

1. **Inventory** satellite hardware, mic, speaker, network, power, OS/firmware versions (workbook table).

2. **Stable identity.** Set hostname + reserved IP. Restrict firewall to required LAN flows only.

:::linux
```bash
hostnamectl
ip -br addr
ping -c 2 HA-IP
ping -c 2 STT-HOST
```
:::

:::windows
```powershell
hostname
ipconfig
ping -n 2 HA-IP
```
:::

3. **Pin audio devices explicitly** (card/device names), not “default” indices that shuffle after reboot.

:::linux
```bash
arecord -l
aplay -l
# Save chosen device strings in workbook
```
:::

4. **Gate A — audio:** record + playback sample; save file hash/path.

5. **Gate B — wake:** one wake model; 10/10 log sheet.

6. **Gate C — STT path:** Wyoming/satellite transport → transcript proof (Class 12 commands).

7. **Gate D — HA understanding:** Assist intent from perfect text; expose only needed entities.

8. **Gate E — action:** service call changes entity.

9. **Gate F — TTS + playback:** hear response on satellite speaker.

10. **Gate G — E2E:** 10 attempts from seating position; log latency + failure layer.

:::linux
```bash
# Example timing wrapper around a manual attempt log:
date -Is | tee -a ~/voice-e2e.log
# after each attempt append: PASS/FAIL layer=... ms=...
```
:::

11. **Gate H — offline privacy:** disable WAN for the test segment **without** killing LAN routing to HA/STT/TTS.

:::linux
```bash
# Example idea only — use your router/firewall controls preferentially:
# On a test client VLAN, block 0.0.0.0/0 except RFC1918.
ping -c 1 1.1.1.1 || echo WAN_BLOCKED_OK
ping -c 1 HA-IP && echo LAN_HA_OK
```
:::

   Repeat one local voice command successfully. Restore WAN. Confirm normal operation.

12. **Responsibility map:** write which box does wake/STT/intent/TTS/playback and where logs live.

## Break / fix

### Break/fix exam

1. Unplug speaker — note which gate fails.  
2. Stop STT container — note failure layer.  
3. Block HA from satellite — Assist must fail closed.  
4. Restore each fault before the next.

## Feedback / common mistakes

- Skipping evidence and calling it done.
- Changing multiple variables before retesting.
- Moving on without completing Feynman teach-back.

## Lab gate

All boxes must be true before the next class unlocks. If you fail: feedback → targeted review → new practice → reassess.

- [ ] Gates A–F pass independently.
- [ ] Ten end-to-end trials are recorded.
- [ ] Wake, STT, action, and response latency are measurable.
- [ ] A hidden fault is isolated without reinstalling the stack.
- [ ] WAN-disconnected command and spoken response pass.
- [ ] Recovery from one service restart is proven.
- [ ] Voice permissions expose only necessary entities.
- [ ] Prior-knowledge check answered
- [ ] Feynman teach-back completed (Explain, Simplify, Example, Weak spot, Retry)
- [ ] Independent practice completed
- [ ] Retrieval check attempted (target ≥80% when scored)
- [ ] Evidence recorded in workbook / verification matrix

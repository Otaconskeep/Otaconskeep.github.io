#!/usr/bin/env python3
"""Complete Module 06 Linux Foundations assessments aligned to Classes 16–21."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import atomic_write_text, today_iso


def write_complete_module06(pack_root: Path, bundles: list[dict[str, Any]]) -> Path:
    """Write substantive MODULE.md, project, quiz, exam, remediation for module 06."""
    mod = pack_root / "modules" / "06-linux-foundations"
    mod.mkdir(parents=True, exist_ok=True)
    titles = [b["title"] for b in bundles]
    ids = [int(b["class_id"]) for b in bundles]

    module_md = f"""# Module 06 — Linux Foundations

**Design chain:** Backward Design → Bloom’s Taxonomy → Learn / Practice / Test / Reflect → Mastery → Spiral Review  
**Feynman teach-back is required in every lesson.**  
**Last reviewed:** {today_iso()}

## Backward design — module outcome

Student can navigate a Linux lab tree safely, compose shell pipelines for investigation, apply least-privilege users/groups/permissions, manage processes with signals and user systemd units, extract evidence with journalctl, and harden SSH with keys using console break-glass — all verified under disposable `/opt/lab-classroom/` paths.

## Bloom arc

Remember/Understand (paths, streams) → Apply (permissions, pipelines, journalctl) → Analyze/Evaluate (sshd hardening order, process signals)

## Module learning cycle

Orient → Recall → Learn (reading) → Demonstrate → Guided practice → Independent practice → **Feynman** → Lab → Quiz → Feedback → Module project → Module quiz → Exam → Reflect

## Topics (Classes {ids[0]}–{ids[-1]})

| Class | Topic |
|---|---|
""" + "\n".join(f"| {i} | {t} |" for i, t in zip(ids, titles)) + """

## Mastery gate (module unlock)

Do **not** unlock Module 07 until:
- All six topic labs verified with evidence
- All six Feynman teach-backs completed
- Module project accepted
- Module quiz ≥80%
- Practical exam pass per rubric
"""
    atomic_write_text(mod / "MODULE.md", module_md)

    # Required reading index
    atomic_write_text(
        mod / "REQUIRED_READING.md",
        "\n".join(
            [
                "# Module 06 — Required reading",
                "",
                "Complete each topic reading before its lab:",
                "",
                *[f"- Class {i}: {t} — `topics/` activity reading.md" for i, t in zip(ids, titles)],
                "",
                "Primary references: hier(7), bash(1), chmod/chown/id, systemd.service(5), journalctl(1), sshd_config(5).",
                "",
            ]
        ),
    )

    project = f"""# Module project — Linux Foundations

**Module:** Module 06 — Linux Foundations  
**Activity type:** Project (integrated Apply/Create)  
**Classes covered:** {", ".join(str(i) for i in ids)}  
**Lab risk:** medium (disposable paths + optional user systemd + ssh lab VM only)

## Objective

Deliver a single evidence pack proving you can navigate, pipe, permission, supervise, log, and SSH-harden a disposable lab without touching production `/data`.

## Deliverables

1. **Lab tree** under `/opt/lab-classroom/module06-project/` with `configs/`, `logs/`, `bin/`.
2. **Pipeline** that filters ERROR lines from a sample log into `logs/errors.txt` using grep|tee and reports a count.
3. **Identity** — a lab group and two lab users; shared directory mode proving group-read without world-write (no 777).
4. **Service** — a user-level oneshot systemd unit that appends a heartbeat line to `logs/heartbeat.log`.
5. **Journal evidence** — redacted `journalctl --user` excerpt for that unit.
6. **SSH notes** — screenshot or command transcript of key auth on a lab VM *or* a clearly labeled simulation documenting hardening order and break-glass console plan if no second VM is available.

## Verification checklist

- [ ] `realpath` shows all artifacts under `/opt/lab-classroom/module06-project`
- [ ] Pipeline evidence file exists and count matches ERROR lines
- [ ] `namei -l` shows non-777 shared directory ownership
- [ ] `systemctl --user status` shows oneshot success
- [ ] Journal excerpt redacted
- [ ] SSH section either proven or labeled simulation with recovery plan

## Rollback

```bash
systemctl --user disable --now module06-heartbeat.service 2>/dev/null || true
rm -f ~/.config/systemd/user/module06-heartbeat.service
systemctl --user daemon-reload
rm -rf /opt/lab-classroom/module06-project
# remove any lab-only users/groups you created for this project
```

## Security

No production paths. No `chmod 777`. No private keys committed. No sshd changes without console.
"""
    atomic_write_text(mod / "project.md", project)

    quiz = """# Module quiz — Linux Foundations

**Target:** ≥80% (at least 8/10)  
**Closed book preferred.**

1. What is the difference between an absolute and a relative path in the Linux filesystem?
2. Why does this curriculum forbid experimenting in `/data` during Module 06 labs?
3. What does `>` do differently from `>>` when used in a shell pipe/redirection workflow?
4. Which stream usually carries error messages?
5. What numeric identities does the kernel use for file access decisions?
6. Why is `chmod 777` usually wrong for shared lab or media directories?
7. Contrast SIGTERM and SIGKILL.
8. Give one `journalctl` flag that limits logs to the current boot.
9. What is the safe order for SSH hardening regarding password authentication?
10. Which command validates `sshd` configuration syntax before reload?

## After scoring

Missed items → return to the matching class reading → redo Feynman Retry → reattempt.
"""
    atomic_write_text(mod / "module-quiz.md", quiz)

    answer_key = """# Module quiz answer key — Linux Foundations

1. Absolute starts at `/` and does not depend on cwd; relative is interpreted from cwd.
2. `/data` may hold production media; labs must stay disposable under `/opt/lab-classroom`.
3. `>` overwrites; `>>` appends.
4. stderr (fd 2).
5. UID and GID.
6. It grants world write, destroying confidentiality and inviting accidents.
7. SIGTERM requests graceful exit; SIGKILL forces termination and cannot be caught.
8. `-b`.
9. Install/test key auth on a second session first; only then consider disabling passwords; keep console break-glass.
10. `sshd -t`.
"""
    atomic_write_text(mod / "ANSWER_KEY.md", answer_key)

    exam = """# Module exam — Linux Foundations (practical)

**Timebox:** 60–90 minutes  
**Environment:** disposable lab VM/shell; console available if SSH tasks are live.

## Stations

### Station A — Navigate & evidence (Classes 16–17)
Create `/opt/lab-classroom/module06-exam/`, write a sample log, and produce `errors.count` via pipeline.  
**Pass:** absolute paths correct; count accurate; no writes outside lab path.

### Station B — Permissions (Class 18)
Create a shared directory proving group-read without world-write.  
**Pass:** `namei -l` evidence; write denied for non-group or others as designed; no 777.

### Station C — Process/service (Classes 19–20)
Install a user oneshot that logs a heartbeat; capture `systemctl --user status` and a journal excerpt.  
**Pass:** unit succeeded; evidence files present; redaction applied.

### Station D — SSH safety (Class 21)
Either (live) prove key login on lab VM with hardening notes, or (simulation) write a one-page hardening order + lockout recovery plan.  
**Pass:** order correct; break-glass documented; no unexplained sshd breakage.

## Rubric (100 points)

| Station | Points | Partial credit |
|---|---:|---|
| A | 25 | 15 if pipeline works but path hygiene weak |
| B | 25 | 10 if permissions work but 777 used (auto-fail security note) |
| C | 25 | 15 if unit runs but journal evidence missing |
| D | 25 | 15 if simulation complete but missing recovery |

**Passing criteria:** ≥80 total **and** zero critical safety failures (777 on shared tree, sshd change without console, writes outside `/opt/lab-classroom`).

## Remediation

If fail: identify weakest station → complete that class lab again → redo Feynman → re-sit only failed stations within one week.
"""
    atomic_write_text(mod / "exam.md", exam)

    remediation = """# Remediation — Module 06

## Feedback → targeted review → reassess

| Weak signal | Return to | Re-do |
|---|---|---|
| Lost in directories | Class 16 reading + lab | Rebuild lab tree from memory |
| Pipeline mistakes / overwrites | Class 17 | Redo tee/grep lab; explain > vs >> |
| Permission denied / 777 temptation | Class 18 | Rebuild least-privilege share |
| Unit won't start | Class 19 | `daemon-reload`, absolute ExecStart |
| Can't find logs | Class 20 | `journalctl -u/-b` drills |
| SSH lockout fear | Class 21 | Practice hardening order on disposable VM only |

## Completion checklist

- [ ] All topic quizzes ≥80%
- [ ] Module project accepted
- [ ] Module quiz ≥80%
- [ ] Exam ≥80 with no critical safety fails
- [ ] Remediation notes filed if any station failed first attempt
"""
    atomic_write_text(mod / "remediation.md", remediation)

    checklist = """# Module 06 completion checklist

- [ ] Required reading complete for Classes 16–21
- [ ] Six Feynman teach-backs complete
- [ ] Six labs verified
- [ ] Homework evidence filed
- [ ] Module project accepted
- [ ] Module quiz ≥80%
- [ ] Practical exam passed per rubric
- [ ] Remediation closed (if any)
"""
    atomic_write_text(mod / "COMPLETION_CHECKLIST.md", checklist)
    return mod

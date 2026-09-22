# Homelab Academy — Learning Methodology

This course is a **learning system**, not a pile of readings, labs, and exams.

## Design chain

**Backward Design → Bloom’s Taxonomy → Learn / Practice / Test / Reflect → Mastery → Spiral Review**

The Feynman Technique is a **required** section in every class — not an optional study tip.

## Whole-course architecture

| Part | Purpose |
|---|---|
| Course Overview | What the class teaches and why it matters |
| Syllabus | Expectations, schedule, grading, policies, required tools |
| Course Outcomes | What the student should be able to do by the end |
| Prerequisite Assessment | Determine what the student already knows |
| Modules (Units) | Major subject areas in logical progression |
| Lessons (Classes) | Small focused learning units within each module |
| Reading / Reference | Background knowledge and deeper explanations |
| Worked Examples | Show how concepts are actually applied |
| Practice Exercises | Low-risk repetition before grading |
| Homework / Projects | Apply concepts independently |
| Quizzes | Frequent knowledge / retrieval checks |
| Module Gates | Verify mastery of the module |
| Midterm / Milestone | Integrate several modules |
| Final Capstone | Demonstrate complete course mastery |
| Review / Remediation | Re-teach weak areas |
| Final Reflection | Explain what was learned and how concepts connect |

Every part maps back to course learning outcomes.

## Backward design

We do **not** start with “What lessons should we make?”

We start with: **What should the student be capable of doing when this course is finished?**

**Final outcome:** Student can design, build, operate, troubleshoot, and verify a private homelab that includes Dockerized services, ARR media automation (authorized content only), Home Assistant automations, a local voice pipeline, and guarded workflow automation — with evidence in a verification matrix.

Working backward produces the modules:

| Module | Classes | Capability unlocked |
|---|---|---|
| 1 — Infrastructure | 1–4, 15 | Virtualize, compose, network, operate, and address hosts |
| 2 — ARR media | 5–7 | Request → search → download → import with quality policy |
| 3 — Home Assistant | 8–10 | Entities, automations, and secure remote access |
| 4 — Local voice | 11–13 | Stage-by-stage local STT/TTS to private speaker |
| 5 — Workflow automation | 14 | n8n digests and approval-gated agent actions |
| Capstone | Final | End-to-end verification matrix |

## Module learning cycle

Every module (and every class) follows:

**Orient → Recall → Learn → Demonstrate → Guided Practice → Independent Practice → Feynman → Apply → Assess → Feedback → Reflect**

## Lesson template (required sections)

Every class markdown and HTML page uses this order:

1. **Learning objective** — measurable Bloom verb (not “understand”)
2. **Why this matters** — reason to care before theory
3. **Prior-knowledge check** — 2–5 activation questions
4. **Vocabulary** — terms linked to the objective
5. **Instruction** — one major concept (or tightly related group)
6. **Worked example** — I do (bad → better with reasoning)
7. **Guided practice** — We do (hints allowed)
8. **Independent practice** — You do (hints removed)
9. **Feynman teach-back** — mandatory Explain / Simplify / Example / Weak spot / Retry
10. **Retrieval check** — 3–7 active-recall questions
11. **Guided lab** — realistic build with OS-specific commands
12. **Break / fix** — failure modes and recovery
13. **Common mistakes / feedback** — targeted correction
14. **Practical mastery gate** — checklist; unlock next class only when complete
15. **Reflection** — learn / struggle / connect
16. **Spiral hook** — where this concept returns later
17. **Current correction** — docs/tooling that change over time

Pattern inside practice: **I do → We do → You do**.

## Feynman checkpoint (mandatory)

Every class includes **Teach it back**:

| Step | Prompt |
|---|---|
| Explain | Describe today’s concept in your own words |
| Simplify | Explain it to a 12-year-old (define any jargon) |
| Example | Give your own real-world analogy |
| Weak spot | What part could you not explain clearly? |
| Retry | Restudy that section and rewrite the explanation |

Self-report “I understood” is not accepted as evidence of understanding.

## Assessment ladder

| Assessment | Purpose |
|---|---|
| Prior-knowledge check | Activate / diagnose |
| Feynman teach-back | Understanding |
| Guided + independent practice | Application |
| Retrieval check | Retention |
| Guided lab + break/fix | Skill under stress |
| Practical gate | Mastery unlock |
| Module / stage gate | Integrated skill |
| Capstone | Real-world application |
| Final reflection | Metacognition + connections |

## Mastery gates

Do not advance because you clicked Next.

**Default unlock rule per class:**

- Retrieval check attempted (target ≥ 80% when scored)
- Feynman teach-back completed (all five prompts)
- Independent practice completed
- Practical gate checkboxes all true
- Evidence logged in the verification matrix / workbook

If not met: **Feedback → targeted review → new practice → reassessment**.

## Spiral review

Earlier modules stay alive in later ones.

Examples:

- Class 2 Compose returns in every later service deploy
- Class 3 networking returns in ARR, HA, voice, and n8n
- Class 6 quality policy returns when Class 7 automates profiles
- Class 8 entities return in Class 9 automations and Class 11–13 voice actions
- Class 15 addressing returns whenever you debug “same LAN vs via gateway”

## Combined loop

**Learn → See → Practice → Explain → Apply → Test → Correct → Revisit → Master**

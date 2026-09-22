# Otaconskeep Classroom — Homelab Academy

**Site:** https://otaconskeep.github.io/classroom/

# Homelab Academy: module learning system

This is a **module-based learning system**, not a pile of readings, videos, quizzes, and exams.

**Design chain:** Backward Design → Bloom’s Taxonomy → Learn / Practice / Test / Reflect → Mastery → Spiral Review  

**Feynman teach-back is required in every lesson.**

## Start here

1. [`pack/METHODOLOGY.md`](pack/METHODOLOGY.md) — how the system works  
2. [`pack/LEARNING_OUTCOMES.md`](pack/LEARNING_OUTCOMES.md) — what you can do at the end  
3. [`pack/PREREQUISITE_ASSESSMENT.md`](pack/PREREQUISITE_ASSESSMENT.md)  
4. [`pack/modules/README.md`](pack/modules/README.md) — **authoritative module index**  
5. Open Module 1 → Topic 1 → Reading → Lesson (Feynman) → Lab → Homework → Quiz  

## Module shape

```
Module
├── MODULE.md            outcome, Bloom arc, mastery gate, spiral
├── topics/Txx-name/
│   ├── reading.md       Learn
│   ├── lesson.md        Orient + Feynman (required) + reflect
│   ├── lab.md           Practice
│   ├── homework.md      Apply
│   └── quiz.md          Test
├── project.md           integrated skill
├── module-quiz.md       retention
├── exam.md              mastery
└── remediation.md       re-teach weak areas
```

## Package contents

- `pack/modules/` — **primary curriculum**
- `pack/classes/` — combined reference exports of each topic (legacy-compatible)
- Course docs: overview, syllabus, outcomes, methodology, prereq, map
- Workbook, instructor key, capstone, templates, references

## Boundaries

- Authorized indexers/content only  
- Do not expose ARR/download admin to the public internet  
- Never paste real secrets into public repos or screenshots  

## License

MIT — Antonio G. Garcia (Otaconskeep)

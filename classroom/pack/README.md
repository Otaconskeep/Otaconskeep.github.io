# Otaconskeep Classroom — Homelab Academy

**Site:** https://otaconskeep.github.io/classroom/

# Homelab Academy: ARR + Home Assistant + Local Voice + n8n

This is a complete, build-first course package. It is not a transcript collection. Each class converts useful ideas into original instruction, adds current operational guidance, and connects the lesson to one final working homelab.

## How to use the pack

1. Read the class lesson.
2. Complete the guided lab exactly once without improvising.
3. Run the break/fix exercise so you learn how the subsystem fails.
4. Complete the quiz without the answer key.
5. Pass the practical gate before moving to the next class.
6. Record evidence in `templates/verification_matrix.csv`.

The course progression is:

**Understand → Build → Break → Fix → Verify**

## Package contents

- `COURSE_MAP.md` — sequence, prerequisites, deliverables, and capstone architecture.
- `classes/01...15` — complete class lessons with labs, troubleshooting, quizzes, and gates (Class 14 = n8n; Class 15 = IPv4 addressing).
- `STUDENT_WORKBOOK.md` — reusable note and evidence pages for every class.
- `INSTRUCTOR_ANSWER_KEY.md` — quiz answers and practical acceptance criteria.
- `FINAL_CAPSTONE.md` — end-to-end ARR, media, Home Assistant, and local-voice exam.
- `templates/` — inventory, port plan, IP plan, service contract, incident log, and verification matrix.
- `references/VIDEO_LINKS.md` — optional lecture links in one place.
- `references/OFFICIAL_DOCUMENTATION.md` — current documentation used for corrections.

## Important boundaries

- Use media automation only with content, indexers, and download sources you are legally authorized to use.
- Do not expose ARR applications or download clients directly to the public internet.
- Back up configuration and databases before migrations or mass profile changes.
- Commands are examples. Replace sample paths, users, IPs, and secrets with values from your own design records.
- Never paste real passwords, API keys, or tunnel tokens into screenshots, assignments, or public repositories.

## Recommended lab target

- One Proxmox server or one Linux host capable of running Docker.
- A separate workstation with a browser and SSH client.
- 16 GB RAM minimum for the combined learning lab; 32 GB is more comfortable.
- Wired Ethernet for servers.
- A test media library and a test Home Assistant entity.
- Optional microphone and speaker for Classes 11–13.



## License

MIT — Antonio G. Garcia (Otaconskeep)

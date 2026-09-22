#!/usr/bin/env python3
"""Inject module publisher into classroom _gen_from_pack.py and regenerate."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

GEN = Path("/root/Otaconskeep.github.io/classroom/_gen_from_pack.py")
PACK_SRC = Path("/root/Classroom/pack")
SITE_PACK = Path("/root/Otaconskeep.github.io/classroom/pack")

MODULE_FUNCS = r'''
MODULE_DIRS = [
    ("01-infrastructure", "01", "Infrastructure & Addressing", "5 topics / Gate 1"),
    ("02-arr-media", "02", "ARR Media Automation", "3 topics / Gate 2"),
    ("03-home-assistant", "03", "Home Assistant & Secure Access", "3 topics / Gate 3"),
    ("04-local-voice", "04", "Local Voice Assistant", "3 topics / Gate 4"),
    ("05-workflow-automation", "05", "Workflow Automation (n8n)", "1 topic / Gate 5"),
]

ACTIVITY_KIND = {
    "reading": "learn",
    "lesson": "feynman",
    "lab": "lab",
    "homework": "practice",
    "quiz": "quiz",
    "project": "practice",
    "module-quiz": "quiz",
    "exam": "gate",
    "remediation": "trouble",
    "MODULE": "objective",
}


def _rewrite_md_links(md: str, topic_url_base: str, mod_url_base: str) -> str:
    md = re.sub(r"\]\(\./(reading|lesson|lab|homework|quiz)\.md\)", rf"]({topic_url_base}\1.html)", md)
    md = re.sub(r"\]\((project|module-quiz|exam|remediation)\.md\)", rf"]({mod_url_base}\1.html)", md)
    md = re.sub(r"\]\(\./(project|module-quiz|exam|remediation)\.md\)", rf"]({mod_url_base}\1.html)", md)
    return md


def gen_activity_page(md_path: Path, out_path: Path, title: str, bar: str, canon: str, kind: str, prev, next_, lede: str, topic_base: str, mod_base: str):
    raw = _rewrite_md_links(md_path.read_text(), topic_base, mod_base)
    _t, lead, sections = split_sections(raw)
    parts = []
    if lead.strip():
        parts.append(f'<div class="cr-box"><h3>Overview</h3>{md_fragment(lead)}</div>')
    for h2, body in sections:
        if "feynman" in h2.lower() or "teach-back" in h2.lower():
            parts.append(render_feynman(body, out_path.stem))
        else:
            parts.append(render_section(h2, body, out_path.stem))
    badge = kind_badge(ACTIVITY_KIND.get(kind, "box"))
    osbar = OSBAR if kind in {"lab", "lesson", "homework"} else ""
    body = f"""
<div class="wrap">
 <section class="hero flush">
 <div class="stamp">{H.escape(bar)}<small>{H.escape(kind)}</small></div>
 <p class="eyebrow" style="margin-top:18px;">Homelab Academy / Modules</p>
 <h1 class="display" style="font-size:clamp(1.6rem,4.5vw,2.5rem);">{badge} {H.escape(title)}</h1>
 <p class="lede">{H.escape(lede)}</p>
 {osbar}
 </section>
</div>
<div class="wrap">
 {''.join(parts)}
 {pager(prev, next_)}
</div>
"""
    write(out_path, wrap(f"{title} · Classroom", title, canon, bar, body))


def gen_modules():
    root = SITE / "modules"
    pack_mod = PACK / "modules"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    cards = []
    for slug, num, title, meta in MODULE_DIRS:
        cards.append(
            f'<a class="cr-course-card" href="{slug}/">'
            f'<div class="num">{num}</div><div>'
            f"<h3>{H.escape(title)}</h3>"
            f"<p>Reading / Lesson / Lab / Homework / Quiz / Project / Exam</p>"
            f'<div class="meta">{H.escape(meta)}</div>'
            f"</div></a>"
        )
    body = f"""
<div class="wrap">
 <section class="hero flush">
 <p class="tag">Modules</p>
 <h1 class="display" style="font-size:clamp(2rem,5vw,3rem);">Course modules</h1>
 <p class="lede">Backward Design outcomes. Each topic ships separate Reading, Lesson (Feynman required), Lab, Homework, and Quiz. Unlock the next module only after project + module quiz + exam.</p>
 </section>
</div>
<div class="wrap">
 <div class="cr-course-grid">{''.join(cards)}</div>
 {pager(("/classroom/", "Academy"), ("01-infrastructure/", "Module 1"))}
</div>
"""
    write(root / "index.html", wrap("Modules · Classroom", "Module curriculum", "/classroom/modules/", "MODULES", body))

    for slug, num, title, meta in MODULE_DIRS:
        mdir = pack_mod / slug
        out = root / slug
        out.mkdir(parents=True)
        mod_base = f"/classroom/modules/{slug}/"

        # Build rich module hub with topic activity grid
        topic_blocks = []
        topics = sorted((mdir / "topics").iterdir()) if (mdir / "topics").is_dir() else []
        for tdir in topics:
            if not tdir.is_dir():
                continue
            tb = f"/classroom/modules/{slug}/topics/{tdir.name}/"
            topic_blocks.append(
                f'<div class="cr-box"><h3>{H.escape(tdir.name)}</h3>'
                f'<ol class="cr-class-list">'
                f'<li><a href="{tb}reading.html"><strong>Reading</strong></a> — Learn</li>'
                f'<li><a href="{tb}lesson.html"><strong>Lesson</strong></a> — Feynman required</li>'
                f'<li><a href="{tb}lab.html"><strong>Lab</strong></a> — Practice</li>'
                f'<li><a href="{tb}homework.html"><strong>Homework</strong></a> — Apply</li>'
                f'<li><a href="{tb}quiz.html"><strong>Quiz</strong></a> — Test</li>'
                f"</ol></div>"
            )

        mod_md = (mdir / "MODULE.md").read_text()
        _t, lead, sections = split_sections(mod_md)
        sec_html = []
        if lead.strip():
            sec_html.append(f'<div class="cr-box"><h3>Overview</h3>{md_fragment(lead)}</div>')
        for h2, body_md in sections:
            if h2.lower().startswith("topics"):
                continue  # replaced by interactive grid
            sec_html.append(render_section(h2, body_md, f"mod-{num}"))

        hub = f"""
<div class="wrap">
 <section class="hero flush">
 <div class="stamp">MODULE {int(num):02d}<small>{H.escape(meta)}</small></div>
 <p class="eyebrow" style="margin-top:18px;">Homelab Academy</p>
 <h1 class="display" style="font-size:clamp(1.8rem,5vw,2.8rem);">{H.escape(title)}</h1>
 <p class="lede">Learn / Practice / Test / Reflect inside every topic. Module project, quiz, exam, and remediation close the gate.</p>
 </section>
</div>
<div class="wrap">
 {''.join(sec_html)}
 <div class="cr-box"><h3>Topics — activity paths</h3>{''.join(topic_blocks)}</div>
 <div class="cr-box"><h3>Module assessments</h3>
 <ol class="cr-class-list">
  <li><a href="project.html"><strong>Project</strong></a> — integrated Apply/Create</li>
  <li><a href="module-quiz.html"><strong>Module quiz</strong></a> — retention</li>
  <li><a href="exam.html"><strong>Exam</strong></a> — mastery</li>
  <li><a href="remediation.html"><strong>Remediation</strong></a> — re-teach weak areas</li>
 </ol></div>
 {pager(("/classroom/modules/", "All modules"), ("project.html", "Project"))}
</div>
"""
        write(out / "index.html", wrap(f"Module {int(num)} — {title} · Classroom", title, f"/classroom/modules/{slug}/", f"MODULE {int(num)}", hub))

        for act, label, lede in [
            ("project", "Project", "Integrated Apply/Create across this module's topics."),
            ("module-quiz", "Module quiz", "Cross-topic retrieval. Target >=80%."),
            ("exam", "Module exam", "Practical mastery verification for the module outcome."),
            ("remediation", "Remediation", "Feedback -> targeted review -> reassess."),
        ]:
            gen_activity_page(
                mdir / f"{act}.md",
                out / f"{act}.html",
                f"{title} — {label}",
                f"M{int(num)} {label.upper()}",
                f"/classroom/modules/{slug}/{act}.html",
                act,
                (f"/classroom/modules/{slug}/", "Module hub"),
                ("/classroom/modules/", "All modules"),
                lede,
                topic_base="",
                mod_base=mod_base,
            )

        for tdir in topics:
            if not tdir.is_dir():
                continue
            tout = out / "topics" / tdir.name
            tout.mkdir(parents=True)
            topic_base = f"/classroom/modules/{slug}/topics/{tdir.name}/"
            acts = [
                ("reading", "Reading", "Learn — instruction, vocabulary, worked example."),
                ("lesson", "Lesson", "Orient, prior check, guided practice, required Feynman, reflect."),
                ("lab", "Lab", "Guided practice + break/fix + lab gate."),
                ("homework", "Homework", "Independent application with evidence."),
                ("quiz", "Quiz", "Retrieval practice. Target >=80%."),
            ]
            for i, (act, label, lede) in enumerate(acts):
                prev = (f"/classroom/modules/{slug}/", "Module hub") if i == 0 else (f"{acts[i-1][0]}.html", acts[i-1][1])
                nxt = (f"{acts[i+1][0]}.html", acts[i+1][1]) if i < len(acts) - 1 else (f"/classroom/modules/{slug}/project.html", "Module project")
                gen_activity_page(
                    tdir / f"{act}.md",
                    tout / f"{act}.html",
                    f"{tdir.name} — {label}",
                    f"M{int(num)} {label.upper()}",
                    f"{topic_base}{act}.html",
                    act,
                    prev,
                    nxt,
                    lede,
                    topic_base=topic_base,
                    mod_base=mod_base,
                )
            links = "".join(
                f'<li><a href="{a}.html"><strong>{lab}</strong></a> — {lede}</li>'
                for a, lab, lede in acts
            )
            tbody = f"""
<div class="wrap">
 <section class="hero flush">
 <p class="tag">Module {int(num)} / Topic</p>
 <h1 class="display" style="font-size:clamp(1.6rem,4vw,2.4rem);">{H.escape(tdir.name)}</h1>
 <p class="lede">Complete in order: Reading then Lesson (Feynman) then Lab then Homework then Quiz.</p>
 </section>
</div>
<div class="wrap">
 <div class="cr-box"><ol class="cr-class-list">{links}</ol></div>
 {pager((f"/classroom/modules/{slug}/", "Module hub"), ("reading.html", "Reading"))}
</div>
"""
            write(tout / "index.html", wrap(f"{tdir.name} · Classroom", tdir.name, topic_base, "TOPIC", tbody))

    print("modules published")


def class_to_module_redirects():
    mapping = {
        "01": "01-infrastructure/topics/01-virtualization/lesson.html",
        "02": "01-infrastructure/topics/02-compose/lesson.html",
        "03": "01-infrastructure/topics/03-networking/lesson.html",
        "04": "01-infrastructure/topics/04-operations/lesson.html",
        "05": "02-arr-media/topics/01-prowlarr-flow/lesson.html",
        "06": "02-arr-media/topics/02-trash-profiles/lesson.html",
        "07": "02-arr-media/topics/03-config-automation/lesson.html",
        "08": "03-home-assistant/topics/01-ha-foundations/lesson.html",
        "09": "03-home-assistant/topics/02-ha-automations/lesson.html",
        "10": "03-home-assistant/topics/03-secure-remote/lesson.html",
        "11": "04-local-voice/topics/01-voice-architecture/lesson.html",
        "12": "04-local-voice/topics/02-whisper-piper/lesson.html",
        "13": "04-local-voice/topics/03-private-speaker/lesson.html",
        "14": "05-workflow-automation/topics/01-n8n-automation/lesson.html",
        "15": "01-infrastructure/topics/05-ipv4/lesson.html",
    }
    CLASSES_DIR.mkdir(parents=True, exist_ok=True)
    for num, dest in mapping.items():
        dst = f"/classroom/modules/{dest}"
        write(
            CLASSES_DIR / f"{num}.html",
            f'<!doctype html><meta http-equiv="refresh" content="0;url={dst}">'
            f'<link rel="canonical" href="https://otaconskeep.github.io{dst}">'
            f'<script>location.replace("{dst}")</script>'
            f'<p>Moved into the module curriculum. <a href="{dst}">Continue</a>.</p>',
        )
    write(
        CLASSES_DIR / "index.html",
        '<!doctype html><meta http-equiv="refresh" content="0;url=/classroom/modules/">'
        '<script>location.replace("/classroom/modules/")</script>',
    )
'''


def main():
    # Sync pack first
    if SITE_PACK.exists():
        shutil.rmtree(SITE_PACK)
    shutil.copytree(PACK_SRC, SITE_PACK)

    text = GEN.read_text()
    text = text.replace('CSS_V = "20260922a"', 'CSS_V = "20260922b"')
    text = text.replace('CSS_V = "20260922b"', 'CSS_V = "20260922b"')

    # SUB nav
    text = re.sub(
        r"(<a href=\"/classroom/\">Academy</a>\n <a href=\"/classroom/)classes(/\">)Classes(</a>)",
        r'\1modules\2Modules\3',
        text,
        count=1,
    )
    # if still has Classes link only, force replace line
    if 'href="/classroom/modules/"' not in text.split("SUB =", 1)[-1][:500]:
        text = text.replace(
            '<a href="/classroom/classes/">Classes</a>',
            '<a href="/classroom/modules/">Modules</a>',
        )

    if "def gen_modules():" not in text:
        text = text.replace("\ndef gen_hub():", "\n" + MODULE_FUNCS + "\ndef gen_hub():")

    text = text.replace(
        '<a class="btn btn-primary" href="classes/01.html">Start Class 1</a>',
        '<a class="btn btn-primary" href="modules/01-infrastructure/">Start Module 1</a>',
    )
    text = text.replace(
        '<a class="btn btn-primary" href="modules/01-infrastructure/">Start Module 1</a>',
        '<a class="btn btn-primary" href="modules/01-infrastructure/">Start Module 1</a>',
    )

    # Hub section: prefer modules CTA
    if "Open modules" not in text:
        text = text.replace(
            """ <p class="tag">02 // Classes</p>
 <h2>All fifteen lessons</h2>
 <div class="cr-course-grid">
{''.join(cards)}
 </div>""",
            """ <p class="tag">02 // Modules</p>
 <h2>Five modules with readings, labs, homework, quizzes</h2>
 <p class="intro">Each topic is split into Reading (Learn), Lesson with <strong>required Feynman</strong>, Lab (Practice), Homework (Apply), and Quiz (Test). Modules close with project, module quiz, exam, and remediation.</p>
 <div class="btn-row" style="margin-top:18px;">
  <a class="btn btn-primary" href="modules/">Open modules</a>
  <a class="btn btn-ghost" href="modules/01-infrastructure/topics/01-virtualization/">Topic 1.1 path</a>
 </div>
 <div class="cr-course-grid" style="margin-top:22px;">
{''.join(cards)}
 </div>""",
        )

    if "gen_modules()" not in text.split("def main", 1)[-1]:
        text = text.replace(
            "    gen_hub()\n    gen_classes()",
            "    gen_hub()\n    gen_modules()\n    class_to_module_redirects()\n    gen_classes()",
        )
        # If gen_classes still desired for pack viewing - actually redirects overwrite class html.
        # Keep gen_classes BEFORE redirects so redirects win — reorder:
        text = text.replace(
            "    gen_hub()\n    gen_modules()\n    class_to_module_redirects()\n    gen_classes()",
            "    gen_hub()\n    gen_modules()\n    gen_classes()\n    class_to_module_redirects()",
        )

    text = text.replace(
        '"Sequence, gates, and final architecture for the 15-class pack.",',
        '"Module curriculum: readings, lessons, labs, homework, quizzes, projects, exams.",',
    )

    GEN.write_text(text)
    compile(text, str(GEN), "exec")
    print("patched", GEN)


if __name__ == "__main__":
    main()

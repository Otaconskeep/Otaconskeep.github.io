#!/usr/bin/env python3
"""Patch classroom _gen_from_pack.py for learning-system sections."""
from __future__ import annotations

import re
from pathlib import Path

NEW_SECTION_KIND = '''SECTION_KIND = {
    "vocabulary": "vocab",
    "learning objective": "objective",
    "why this matters": "why",
    "prior-knowledge check": "prior",
    "instruction": "learn",
    "worked example": "example",
    "guided practice": "practice",
    "independent practice": "practice",
    "feynman teach-back": "feynman",
    "retrieval check": "quiz",
    "knowledge check": "quiz",
    "end-to-end architecture": "diagram",
    "architecture": "diagram",
    "architecture overview": "diagram",
    "guided lab": "lab",
    "lab": "lab",
    "break/fix": "break",
    "break / fix": "break",
    "break/fix exercises": "break",
    "break / fix exercises": "break",
    "break it, then fix it": "break",
    "feedback / common mistakes": "trouble",
    "common mistakes": "trouble",
    "troubleshooting matrix": "trouble",
    "troubleshooting": "trouble",
    "practical mastery gate": "gate",
    "practical gate": "gate",
    "reflection": "reflect",
    "spiral hook": "spiral",
    "2026 correction": "tip",
    "scope and legal boundary": "tip",
    "important boundaries": "tip",
    "safety boundary": "tip",
}
'''

RENDER_FEYNMAN = r'''
def render_feynman(body_md: str, class_id: str) -> str:
    """Interactive Feynman teach-back with persistent textareas."""
    mean, more = plain_for_section("feynman teach-back", "feynman")
    fields = [
        ("explain", "Explain", "Describe today's concept in your own words."),
        ("simplify", "Simplify", "Explain it to a 12-year-old. Define any jargon."),
        ("example", "Example", "Give your own real-world analogy or example."),
        ("weak", "Weak spot", "What part could you not explain clearly?"),
        ("retry", "Retry", "Restudy that section and rewrite a clearer explanation."),
    ]
    cards = []
    for key, label, hint in fields:
        cards.append(
            f'<div class="cr-feynman-field">'
            f'<label for="fy-{H.escape(class_id)}-{key}"><strong>{label}</strong> — {H.escape(hint)}</label>'
            f'<textarea id="fy-{H.escape(class_id)}-{key}" data-feynman-id="{H.escape(class_id)}" '
            f'data-feynman-field="{key}" rows="4" placeholder="Write here…"></textarea>'
            f"</div>"
        )
    prose = md_fragment(body_md) if body_md.strip() else ""
    return (
        f'<div class="cr-box cr-box-feynman" id="feynman">'
        f'<div class="cr-box-head">{kind_badge("feynman")}<h3>Feynman teach-back — required</h3></div>'
        f"{help_widget(mean, more)}"
        f'<div class="cr-prose-block">{prose}</div>'
        f'<div class="cr-feynman-form" data-feynman-form="{H.escape(class_id)}">'
        f'{"".join(cards)}'
        f'<p class="cr-feynman-note">Answers save in this browser (localStorage). '
        f"Completing all five fields is part of the mastery unlock.</p>"
        f"</div></div>"
    )


'''

NEW_FUZZY = '''    if kind == "box":
        if "feynman" in low or "teach-back" in low or "teach it back" in low:
            kind = "feynman"
        elif "lab" in low:
            kind = "lab"
        elif "break" in low or ("fix" in low and "exercise" in low):
            kind = "break"
        elif "vocab" in low or "outcome" in low:
            kind = "vocab"
        elif "architect" in low or "diagram" in low or "flow" in low:
            kind = "diagram"
        elif "trouble" in low or "matrix" in low or "mistakes" in low or "feedback" in low:
            kind = "trouble"
        elif "retrieval" in low or "knowledge" in low or "quiz" in low:
            kind = "quiz"
        elif "gate" in low or "mastery" in low:
            kind = "gate"
        elif "prior" in low:
            kind = "prior"
        elif "reflect" in low:
            kind = "reflect"
        elif "spiral" in low:
            kind = "spiral"
        elif "worked example" in low:
            kind = "example"
        elif "practice" in low:
            kind = "practice"
        elif "why this" in low:
            kind = "why"
        elif "objective" in low:
            kind = "objective"
        elif "instruction" in low:
            kind = "learn"
        elif "correction" in low or "scope" in low or "legal" in low or "safety" in low:
            kind = "tip"

    if kind == "feynman":
        return render_feynman(body, class_id)

    if kind == "gate":
        return render_gate(body, f"gate-{class_id}")
'''

INSERT_PAGES = '''    gen_md_page(
        "METHODOLOGY.md", "methodology.html", "Learning methodology", "METHOD",
        "/classroom/methodology.html", "Methodology",
        ("/classroom/", "Academy"), ("syllabus.html", "Syllabus"),
        "Backward Design, Bloom, Feynman, mastery gates, and spiral review.",
    )
    gen_md_page(
        "COURSE_OVERVIEW.md", "overview.html", "Course overview", "OVERVIEW",
        "/classroom/overview.html", "Overview",
        ("/classroom/", "Academy"), ("syllabus.html", "Syllabus"),
        "What the Academy teaches and why it is built as a learning system.",
    )
    gen_md_page(
        "SYLLABUS.md", "syllabus.html", "Syllabus", "SYLLABUS",
        "/classroom/syllabus.html", "Syllabus",
        ("overview.html", "Overview"), ("outcomes.html", "Outcomes"),
        "Expectations, mastery rules, policies, tools, and suggested schedule.",
    )
    gen_md_page(
        "LEARNING_OUTCOMES.md", "outcomes.html", "Learning outcomes", "OUTCOMES",
        "/classroom/outcomes.html", "Outcomes",
        ("syllabus.html", "Syllabus"), ("prereq.html", "Prereq"),
        "What you should be able to do when the course is finished.",
    )
    gen_md_page(
        "PREREQUISITE_ASSESSMENT.md", "prereq.html", "Prerequisite assessment", "PREREQ",
        "/classroom/prereq.html", "Prereq",
        ("outcomes.html", "Outcomes"), ("classes/01.html", "Class 1"),
        "Diagnose what you already know before Class 1.",
    )
    gen_references()'''


def patch(path: Path) -> None:
    text = path.read_text()
    if "Otaconskeep.github.io" in str(path):
        text = text.replace(
            'SITE = Path("/root/otaconskeep-site/classroom")',
            'SITE = Path("/root/Otaconskeep.github.io/classroom")',
        )
    text = text.replace('CSS_V = "20260921o"', 'CSS_V = "20260922a"')
    text = text.replace('CSS_V = "20260922a"', 'CSS_V = "20260922a"')  # idempotent

    text2, n = re.subn(
        r"SECTION_KIND = \{.*?\n\}",
        NEW_SECTION_KIND.strip(),
        text,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit(f"SECTION_KIND replace failed for {path}: {n}")
    text = text2

    if "def render_feynman" not in text:
        text = text.replace(
            "def render_section(h2: str, body: str, class_id: str) -> str:",
            RENDER_FEYNMAN + "def render_section(h2: str, body: str, class_id: str) -> str:",
        )

    # Replace from `if kind == "box":` through first `if kind == "gate":` return block
    pat = re.compile(
        r'    if kind == "box":\n(?:.*?\n)*?    if kind == "gate":\n        return render_gate\(body, f"gate-\{class_id\}"\)\n',
        re.M,
    )
    text2, n = pat.subn(NEW_FUZZY + "\n", text, count=1)
    if n != 1:
        if 'if kind == "feynman":' in text:
            print("fuzzy already patched", path)
        else:
            raise SystemExit(f"fuzzy replace failed for {path}: {n}")
    else:
        text = text2

    text = text.replace(
        '<div class="cr-gate">All boxes true → continue to the next class</div>',
        '<div class="cr-gate">Mastery unlock: all boxes true + Feynman complete → continue to the next class</div>',
    )
    text = text.replace(
        '<h1 class="display" style="font-size:clamp(2.2rem,6vw,3.6rem);">Build. Break. Fix. Verify.</h1>\n <p class="lede">Build-first curriculum for ARR, Home Assistant, and local voice. Same Otaconskeep chrome as the rest of the Keep — structured lessons, checkpoints, and a final verification matrix.</p>',
        '<h1 class="display" style="font-size:clamp(2.2rem,6vw,3.6rem);">Learn. Practice. Explain. Master.</h1>\n <p class="lede">A learning system for ARR, Home Assistant, and local voice — Backward Design, Bloom progression, mandatory Feynman teach-backs, mastery gates, and spiral review. Not a pile of videos and quizzes.</p>',
    )
    text = text.replace(
        '<p class="meta" style="margin-top:22px;">UNDERSTAND → BUILD → BREAK → FIX → VERIFY</p>',
        '<p class="meta" style="margin-top:22px;">LEARN → SEE → PRACTICE → EXPLAIN → APPLY → TEST → CORRECT → REVISIT → MASTER</p>',
    )
    old_how = ''' <p class="tag">00 // How to use</p>
 <h2>One concept. One lab. One gate.</h2>
 <p class="intro">Read the class, run the guided lab once, break it on purpose, fix it, then pass the practical gate. Log evidence in the verification matrix — “it seems to work” is not a grade.</p>
 <div class="cr-callout tip"><strong>Legal / safety:</strong> use only authorized indexers and content. Do not expose ARR admin or download clients to the public internet. Never paste real API keys into screenshots.</div>'''
    new_how = ''' <p class="tag">00 // How to use</p>
 <h2>Every class is a learning cycle</h2>
 <p class="intro">Objective → why it matters → prior check → instruction → worked example → guided practice → independent practice → <strong>Feynman teach-back</strong> → retrieval check → lab → break/fix → mastery gate → reflection → spiral hook. Unlock the next class only when the gate is truly met.</p>
 <div class="cr-callout tip"><strong>Legal / safety:</strong> use only authorized indexers and content. Do not expose ARR admin or download clients to the public internet. Never paste real API keys into screenshots.</div>
 <div class="btn-row" style="margin-top:18px;">
  <a class="btn btn-ghost" href="methodology.html">Methodology</a>
  <a class="btn btn-ghost" href="syllabus.html">Syllabus</a>
  <a class="btn btn-ghost" href="outcomes.html">Outcomes</a>
  <a class="btn btn-ghost" href="prereq.html">Prerequisite assessment</a>
 </div>'''
    if old_how in text:
        text = text.replace(old_how, new_how)
    text = text.replace(
        '<p class="lede">Guided lab, break/fix, quiz, and practical gate. Prefer current official docs linked in References.</p>',
        '<p class="lede">Full learning cycle with mandatory Feynman teach-back, retrieval practice, lab, and mastery gate. Prefer current official docs in References.</p>',
    )
    text = text.replace("All 13 classes", "All 15 classes")
    text = text.replace("All 13 Homelab Academy classes.", "All 15 Homelab Academy classes.")

    old_sub = '''SUB = \'\'\'<nav class="cr-subnav" aria-label="Classroom">
 <div class="wrap">
 <a href="/classroom/">Academy</a>
 <a href="/classroom/classes/">Classes</a>
 <a href="/classroom/workbook.html">Workbook</a>
 <a href="/classroom/final-exam.html">Capstone</a>
 <a href="/classroom/references/">References</a>
 <a href="/classroom/glossary.html">Glossary</a>
 </div>
</nav>\'\'\''''
    new_sub = '''SUB = \'\'\'<nav class="cr-subnav" aria-label="Classroom">
 <div class="wrap">
 <a href="/classroom/">Academy</a>
 <a href="/classroom/classes/">Classes</a>
 <a href="/classroom/methodology.html">Method</a>
 <a href="/classroom/syllabus.html">Syllabus</a>
 <a href="/classroom/workbook.html">Workbook</a>
 <a href="/classroom/final-exam.html">Capstone</a>
 <a href="/classroom/references/">References</a>
 <a href="/classroom/glossary.html">Glossary</a>
 </div>
</nav>\'\'\''''
    if old_sub in text:
        text = text.replace(old_sub, new_sub)
    else:
        print("SUB not matched", path)

    if "methodology.html" not in text:
        if "    gen_references()" not in text:
            raise SystemExit("gen_references missing")
        text = text.replace("    gen_references()", INSERT_PAGES, 1)

    path.write_text(text)
    print("patched", path)


def main():
    for p in [
        Path("/root/Otaconskeep.github.io/classroom/_gen_from_pack.py"),
        Path("/root/otaconskeep-site/classroom/_gen_from_pack.py"),
    ]:
        patch(p)


if __name__ == "__main__":
    main()

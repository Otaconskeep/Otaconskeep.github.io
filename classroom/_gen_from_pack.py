#!/usr/bin/env python3
"""Build Homelab Academy Classroom — pack content in Otaconskeep site chrome."""
from __future__ import annotations

import html as H
import re
import shutil
from pathlib import Path

import markdown

from _plain_help import (
    extract_h3_blocks,
    extract_numbered_steps,
    help_widget,
    kind_badge,
    kind_class,
    plain_for_paragraph,
    plain_for_section,
    plain_for_step,
)

SITE = Path("/root/otaconskeep-site/classroom")
PACK = SITE / "pack"
CLASSES_DIR = SITE / "classes"
GH = Path("/root/Classroom")
CSS_V = "20260921h"

NAV = f'''<nav class="topnav">
 <div class="wrap">
 <a class="brand" href="/">Otaconskeep</a>
 <button class="navtoggle" aria-label="Toggle navigation" aria-expanded="false">MENU</button>
 <div class="navlinks">
 <a href="/">Home</a>
 <a href="/otacon/">Otacon</a>
 <a href="/keepdesk/">Keep Desk</a>
 <a href="/keeproute/">KeepRoute</a>
 <a href="/expansion/">Expansion</a>
 <a href="/ai9/">AI9</a>
 <a href="/classroom/" aria-current="page">Classroom</a>
 <a href="/engineering/">Engineering</a>
 <a href="/faq/">FAQ</a>
 <a href="/about/">About</a>
 <a href="https://github.com/Otaconskeep" target="_blank" rel="noopener">GitHub</a>
 <a class="discord" href="https://discord.gg/cZDeqECzX" target="_blank" rel="noopener">Discord</a>
 </div>
 </div>
</nav>'''

SUB = '''<nav class="cr-subnav" aria-label="Classroom">
 <div class="wrap">
 <a href="/classroom/">Academy</a>
 <a href="/classroom/classes/">Classes</a>
 <a href="/classroom/workbook.html">Workbook</a>
 <a href="/classroom/final-exam.html">Capstone</a>
 <a href="/classroom/references/">References</a>
 <a href="/classroom/glossary.html">Glossary</a>
 </div>
</nav>'''

FOOT = f'''<footer class="sitefoot">
 <div class="wrap">
 <span>Otaconskeep Classroom · Homelab Academy</span>
 <span><a href="https://github.com/Otaconskeep/Classroom">GitHub</a> · <a href="/classroom/pack/">Source pack</a></span>
 </div>
</footer>
<script src="/classroom/classroom.js?v={CSS_V}"></script>'''

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://otaconskeep.github.io{canon}">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<link rel="stylesheet" href="/classroom/classroom.css?v={cssv}">
</head>
<body>

<div class="filebar">
 <div class="wrap">
 <span>CLASSROOM // HOMELAB ACADEMY</span>
 <span>{bar}<span class="blink"></span></span>
 </div>
</div>

{nav}
{sub}
'''

CLASS_META = [
    ("01", "01_PROXMOX_VIRTUALIZATION.md", "VMs, hypervisors, and Proxmox", "1", "Infrastructure"),
    ("02", "02_DOCKER_COMPOSE.md", "Docker Compose", "1", "Infrastructure"),
    ("03", "03_DOCKER_NETWORKING.md", "Docker networking", "1", "Infrastructure"),
    ("04", "04_CONTAINER_OPERATIONS.md", "Container operations", "1", "Infrastructure"),
    ("05", "05_PROWLARR_AND_ARR_FLOW.md", "Prowlarr and ARR flow", "2", "ARR"),
    ("06", "06_TRASH_QUALITY_PROFILES.md", "TRaSH quality profiles", "2", "ARR"),
    ("07", "07_CONFIGURATION_AUTOMATION.md", "Configuration automation", "2", "ARR"),
    ("08", "08_HOME_ASSISTANT_FOUNDATIONS.md", "Home Assistant foundations", "3", "Home Assistant"),
    ("09", "09_HOME_ASSISTANT_AUTOMATIONS.md", "Home Assistant automations", "3", "Home Assistant"),
    ("10", "10_SECURE_REMOTE_ACCESS.md", "Secure remote access", "3", "Home Assistant"),
    ("11", "11_LOCAL_VOICE_ARCHITECTURE.md", "Local voice architecture", "4", "Voice"),
    ("12", "12_WHISPER_PIPER_WYOMING.md", "Whisper, Piper, Wyoming", "4", "Voice"),
    ("13", "13_PRIVATE_SMART_SPEAKER.md", "Private smart speaker", "4", "Voice"),
]

MD = markdown.Markdown(extensions=["tables", "fenced_code", "nl2br", "sane_lists"])

SECTION_KIND = {
    "vocabulary": "vocab",
    "end-to-end architecture": "diagram",
    "architecture": "diagram",
    "architecture overview": "diagram",
    "guided lab": "lab",
    "lab": "lab",
    "break/fix exercises": "break",
    "break / fix exercises": "break",
    "troubleshooting matrix": "trouble",
    "troubleshooting": "trouble",
    "knowledge check": "quiz",
    "practical gate": "gate",
    "2026 correction": "tip",
    "scope and legal boundary": "tip",
    "important boundaries": "tip",
}


def scrub_lectures(text: str) -> str:
    """Remove lecture video lines and YouTube URLs from pack markdown."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"\*\*Lecture:\*\*", s, re.I):
            continue
        if re.match(r"\*\*Time:\*\*", s, re.I):
            continue
        if re.match(r"\*\*Build output:\*\*", s, re.I):
            continue
        # Drop bare YouTube links / markdown links to YouTube
        if re.search(r"youtube\.com|youtu\.be", s, re.I):
            continue
        out.append(line)
    text = "\n".join(out)
    # Strip any remaining youtube URLs inline
    text = re.sub(r"https?://(?:www\.)?(?:youtube\.com/\S+|youtu\.be/\S+)", "", text)
    text = re.sub(r"\[([^\]]+)\]\(\s*\)", r"\1", text)
    return text


def md_fragment(text: str) -> str:
    MD.reset()
    text = scrub_lectures(text)
    text = re.sub(
        r"```mermaid\n(.*?)```",
        lambda m: "```text\n" + m.group(1).strip() + "\n```",
        text,
        flags=re.S,
    )
    html = MD.convert(text)
    html = re.sub(
        r'<a href="(https?://[^"]+)"',
        r'<a href="\1" target="_blank" rel="noopener"',
        html,
    )
    # Never leave youtube anchors even if scrub missed
    html = re.sub(
        r'<a href="https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^"]*"[^>]*>.*?</a>',
        "",
        html,
        flags=re.I | re.S,
    )
    return html


def wrap(title: str, desc: str, canon: str, bar: str, body: str) -> str:
    return (
        HEAD.format(
            title=H.escape(title),
            desc=H.escape(desc[:160]),
            canon=canon,
            bar=H.escape(bar),
            nav=NAV,
            sub=SUB,
            cssv=CSS_V,
        )
        + body
        + f"\n{FOOT}\n</body></html>\n"
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print("wrote", path.relative_to(SITE))


def pager(prev, next_):
    left = f'<a href="{prev[0]}">← {H.escape(prev[1])}</a>' if prev else "<span></span>"
    right = f'<a href="{next_[0]}">{H.escape(next_[1])} →</a>' if next_ else "<span></span>"
    return f'<div class="cr-pager">{left}{right}</div>'


def split_sections(md: str):
    """Return (title, lead_md, [(h2, body_md), ...])."""
    lines = md.splitlines()
    title = ""
    i = 0
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        i = 1
        while i < len(lines) and not lines[i].strip():
            i += 1
    lead = []
    while i < len(lines) and not lines[i].startswith("## "):
        lead.append(lines[i])
        i += 1
    sections = []
    while i < len(lines):
        h2 = lines[i][3:].strip()
        i += 1
        body = []
        while i < len(lines) and not lines[i].startswith("## "):
            body.append(lines[i])
            i += 1
        sections.append((h2, "\n".join(body).strip()))
    return title, "\n".join(lead).strip(), sections


def parse_meta(lead_md: str):
    """Extract Lecture / Time / Build output from bold lead lines."""
    lecture = time = build = ""
    rest = []
    for line in lead_md.splitlines():
        s = line.strip()
        m = re.match(r"\*\*Lecture:\*\*\s*(.+)", s, re.I)
        if m:
            lecture = m.group(1).strip()
            continue
        m = re.match(r"\*\*Time:\*\*\s*(.+)", s, re.I)
        if m:
            time = m.group(1).strip()
            continue
        m = re.match(r"\*\*Build output:\*\*\s*(.+)", s, re.I)
        if m:
            build = m.group(1).strip()
            continue
        if s:
            rest.append(line)
    return lecture, time, build, "\n".join(rest).strip()


def render_gate(body_md: str, cid: str) -> str:
    items = []
    for line in body_md.splitlines():
        m = re.match(r"- \[[ xX]?\]\s*(.+)", line.strip())
        if m:
            items.append(m.group(1).strip())
    mean, more = plain_for_section("practical gate", "gate")
    if not items:
        return (
            f'<div class="cr-box cr-box-gate"><div class="cr-box-head">{kind_badge("gate")}<h3>Practical gate</h3></div>'
            f"{md_fragment(body_md)}{help_widget(mean, more)}</div>"
        )
    boxes = "".join(
        f'<div class="cr-check-item">'
        f'<label><input type="checkbox" data-k="{i}"> '
        f"<span>{H.escape(t)}</span></label>"
        f"{help_widget(plain_for_step(t))}"
        f"</div>"
        for i, t in enumerate(items)
    )
    return f'''<div class="cr-check" data-check-id="{H.escape(cid)}">
 <div class="cr-box-head">{kind_badge("gate")}<h3>Practical gate — pass before you continue</h3></div>
 {help_widget(mean, more)}
 {boxes}
 <div class="cr-gate">All boxes true → continue to the next class</div>
</div>'''


def render_lab_steps(steps: list[str], title: str, *, wrap_box: bool = True) -> str:
    mean, more = plain_for_section(title, "lab")
    cards = []
    for i, step in enumerate(steps, 1):
        cards.append(
            f'''<div class="cr-step" data-step="{i}">
 <div class="cr-step-num">{i}</div>
 <div class="cr-step-body">
  <div class="cr-step-text">{md_fragment(step)}</div>
  {help_widget(plain_for_step(step))}
 </div>
</div>'''
        )
    inner = (
        f"{help_widget(mean, more)}"
        f'<div class="cr-step-list">{"".join(cards)}</div>'
    )
    if not wrap_box:
        head = f"<h4>{H.escape(title)}</h4>" if title else ""
        return f'<div class="cr-lab-path">{head}{inner}</div>'
    return (
        f'<div class="{kind_class("lab")}" id="lab">'
        f'<div class="cr-box-head">{kind_badge("lab")}<h3>{H.escape(title)}</h3></div>'
        f"{inner}</div>"
    )


def render_lab_section(h2: str, body: str) -> str:
    """Lab with optional ### path subsections and numbered step cards."""
    mean, more = plain_for_section(h2, "lab")
    blocks = extract_h3_blocks(body)
    if blocks:
        parts = [
            f'<div class="{kind_class("lab")}" id="lab">',
            f'<div class="cr-box-head">{kind_badge("lab")}<h3>{H.escape(h2)}</h3></div>',
            help_widget(mean, more),
        ]
        for sub, text in blocks:
            steps = extract_numbered_steps(text) or []
            # Also accept short lists (<3) inside a named path
            if not steps:
                steps = []
                for line in text.splitlines():
                    m = re.match(r"^(\d+)\.\s+(.+)$", line.strip())
                    if m:
                        steps.append(m.group(2).strip())
            if sub and steps:
                # preamble inside subsection before numbers
                pre = []
                for line in text.splitlines():
                    if re.match(r"^\d+\.\s+", line.strip()):
                        break
                    pre.append(line)
                preamble = "\n".join(pre).strip()
                parts.append(f'<div class="cr-lab-path"><h4>{H.escape(sub)}</h4>')
                if preamble:
                    parts.append(f'<div class="cr-prose-block">{md_fragment(preamble)}</div>')
                parts.append(help_widget(plain_for_step(sub) if not preamble else plain_for_paragraph(preamble)))
                parts.append('<div class="cr-step-list">')
                for i, step in enumerate(steps, 1):
                    parts.append(
                        f'''<div class="cr-step" data-step="{i}">
 <div class="cr-step-num">{i}</div>
 <div class="cr-step-body">
  <div class="cr-step-text">{md_fragment(step)}</div>
  {help_widget(plain_for_step(step))}
 </div>
</div>'''
                    )
                parts.append("</div></div>")
            elif sub:
                parts.append(
                    f'<div class="cr-lab-path"><h4>{H.escape(sub)}</h4>'
                    f"{md_fragment(text)}"
                    f"{help_widget(plain_for_paragraph(text) or plain_for_step(sub))}</div>"
                )
            elif text:
                parts.append(f'<div class="cr-prose-block">{md_fragment(text)}</div>')
        parts.append("</div>")
        return "".join(parts)

    steps = extract_numbered_steps(body)
    if steps:
        pre = []
        for line in body.splitlines():
            if re.match(r"^\d+\.\s+", line.strip()):
                break
            pre.append(line)
        preamble = "\n".join(pre).strip()
        if preamble:
            cards = "".join(
                f'''<div class="cr-step" data-step="{i}">
 <div class="cr-step-num">{i}</div>
 <div class="cr-step-body">
  <div class="cr-step-text">{md_fragment(step)}</div>
  {help_widget(plain_for_step(step))}
 </div>
</div>'''
                for i, step in enumerate(steps, 1)
            )
            return (
                f'<div class="{kind_class("lab")}" id="lab">'
                f'<div class="cr-box-head">{kind_badge("lab")}<h3>{H.escape(h2)}</h3></div>'
                f"{help_widget(mean, more)}"
                f'<div class="cr-prose-block">{md_fragment(preamble)}</div>'
                f'<div class="cr-step-list">{cards}</div></div>'
            )
        return render_lab_steps(steps, h2)
    return render_prose_with_help(body, "lab", h2)


def render_break_blocks(blocks: list[tuple[str, str]], title: str) -> str:
    mean, more = plain_for_section(title, "break")
    parts = [help_widget(mean, more)]
    for sub, body in blocks:
        if not sub and not body:
            continue
        head = f"<h4>{H.escape(sub)}</h4>" if sub else ""
        parts.append(
            f'<div class="cr-break-card">'
            f"{head}{md_fragment(body)}"
            f"{help_widget(plain_for_paragraph(body) if body else plain_for_step(sub))}"
            f"</div>"
        )
    return (
        f'<div class="{kind_class("break")}">'
        f'<div class="cr-box-head">{kind_badge("break")}<h3>{H.escape(title)}</h3></div>'
        f'{"".join(parts)}</div>'
    )


def render_prose_with_help(body: str, kind: str, title: str) -> str:
    """Split ### blocks or paragraphs and attach plain-language help."""
    mean, more = plain_for_section(title, kind)
    chunks = []
    h3s = extract_h3_blocks(body)
    if h3s:
        for sub, text in h3s:
            if not text and not sub:
                continue
            head = f"<h4>{H.escape(sub)}</h4>" if sub else ""
            chunks.append(
                f'<div class="cr-prose-block">{head}{md_fragment(text)}'
                f"{help_widget(plain_for_paragraph(text) or plain_for_step(sub or title))}</div>"
            )
    else:
        # Split on blank lines into paragraph groups; keep code fences intact
        pieces = re.split(r"\n(?=```)", body)
        buf = []
        for piece in pieces:
            if piece.startswith("```"):
                if buf:
                    text = "\n\n".join(buf).strip()
                    if text:
                        chunks.append(
                            f'<div class="cr-prose-block">{md_fragment(text)}'
                            f"{help_widget(plain_for_paragraph(text))}</div>"
                        )
                    buf = []
                chunks.append(f'<div class="cr-prose-block cr-prose-code">{md_fragment(piece)}</div>')
            else:
                paras = [p.strip() for p in re.split(r"\n\s*\n", piece) if p.strip()]
                for p in paras:
                    # tables stay as one block
                    if p.lstrip().startswith("|"):
                        chunks.append(
                            f'<div class="cr-prose-block">{md_fragment(p)}'
                            f"{help_widget(plain_for_section(title, kind)[0])}</div>"
                        )
                    else:
                        chunks.append(
                            f'<div class="cr-prose-block">{md_fragment(p)}'
                            f"{help_widget(plain_for_paragraph(p))}</div>"
                        )
    return (
        f'<div class="{kind_class(kind)}">'
        f'<div class="cr-box-head">{kind_badge(kind)}<h3>{H.escape(title)}</h3></div>'
        f"{help_widget(mean, more)}"
        f'{"".join(chunks)}</div>'
    )


def render_section(h2: str, body: str, class_id: str) -> str:
    kind = SECTION_KIND.get(h2.lower().strip(), "box")
    # Fuzzy kind from title words
    low = h2.lower()
    if kind == "box":
        if "lab" in low:
            kind = "lab"
        elif "break" in low or "fix" in low and "exercise" in low:
            kind = "break"
        elif "vocab" in low or "outcome" in low:
            kind = "vocab"
        elif "architect" in low or "diagram" in low or "flow" in low:
            kind = "diagram"
        elif "trouble" in low or "matrix" in low:
            kind = "trouble"
        elif "knowledge" in low or "quiz" in low or "check" in low:
            kind = "quiz"
        elif "gate" in low:
            kind = "gate"
        elif "correction" in low or "scope" in low or "legal" in low:
            kind = "tip"

    if kind == "gate":
        return render_gate(body, f"gate-{class_id}")

    if kind == "lab":
        return render_lab_section(h2, body)

    if kind == "break":
        blocks = extract_h3_blocks(body)
        if blocks:
            return render_break_blocks(blocks, h2)
        return render_prose_with_help(body, "break", h2)

    if kind == "tip":
        mean, more = plain_for_section(h2, "tip")
        return (
            f'<div class="cr-callout tip">'
            f'<div class="cr-box-head">{kind_badge("tip")}<strong>{H.escape(h2)}</strong></div>'
            f"{md_fragment(body)}{help_widget(mean, more)}</div>"
        )

    if kind == "diagram":
        mean, more = plain_for_section(h2, "diagram")
        inner = md_fragment(body)
        inner = re.sub(
            r"<pre><code[^>]*>(.*?)</code></pre>",
            lambda m: f'<pre class="cr-diagram">{m.group(1)}</pre>',
            inner,
            flags=re.S,
            count=1,
        )
        return (
            f'<div class="{kind_class("diagram")}">'
            f'<div class="cr-box-head">{kind_badge("diagram")}<h3>{H.escape(h2)}</h3></div>'
            f"{help_widget(mean, more)}{inner}</div>"
        )

    return render_prose_with_help(body, kind, h2)

def render_doc_page(md_text: str, page_title: str, lede: str | None = None) -> str:
    """Generic pack markdown → sectioned cr-boxes (for workbook/map/etc)."""
    _t, lead, sections = split_sections(md_text)
    parts = []
    if lead:
        parts.append(f'<div class="cr-box"><h3>Overview</h3>{md_fragment(lead)}</div>')
    for h2, body in sections:
        parts.append(render_section(h2, body, "doc"))
    hero_lede = lede or ""
    return "\n".join(parts), hero_lede


def gen_hub():
    cards = []
    for num, _fn, title, unit, unit_name in CLASS_META:
        cards.append(
            f'<a class="cr-course-card" href="classes/{num}.html">'
            f'<div class="num">{num}</div><div>'
            f"<h3>{H.escape(title)}</h3>"
            f'<p>Unit {unit} — {H.escape(unit_name)}</p>'
            f'<div class="meta">Class {int(num)}</div>'
            f"</div></a>"
        )
    body = f'''
<div class="wrap">
 <section class="hero flush">
 <div class="stamp">HOMELAB ACADEMY<small>free · 13-class pack</small></div>
 <p class="eyebrow" style="margin-top:18px;">Otaconskeep Classroom</p>
 <h1 class="display" style="font-size:clamp(2.2rem,6vw,3.6rem);">Build. Break. Fix. Verify.</h1>
 <p class="lede">Build-first curriculum for ARR, Home Assistant, and local voice. Same Otaconskeep chrome as the rest of the Keep — structured lessons, checkpoints, and a final verification matrix.</p>
 <div class="btn-row" style="margin-top:26px;">
  <a class="btn btn-primary" href="classes/01.html">Start Class 1</a>
  <a class="btn btn-ghost" href="workbook.html">Student workbook</a>
  <a class="btn btn-ghost" href="final-exam.html">Final capstone</a>
  <a class="btn btn-ghost" href="references/">References</a>
 </div>
 <p class="meta" style="margin-top:22px;">UNDERSTAND → BUILD → BREAK → FIX → VERIFY</p>
 </section>
</div>

<div class="wrap">
 <section>
 <p class="tag">00 // How to use</p>
 <h2>One concept. One lab. One gate.</h2>
 <p class="intro">Read the class, run the guided lab once, break it on purpose, fix it, then pass the practical gate. Log evidence in the verification matrix — “it seems to work” is not a grade.</p>
 <div class="cr-callout tip"><strong>Legal / safety:</strong> use only authorized indexers and content. Do not expose ARR admin or download clients to the public internet. Never paste real API keys into screenshots.</div>
 </section>
</div>

<div class="wrap">
 <section>
 <p class="tag">01 // Stage gates</p>
 <h2>Pass each gate before the next unit</h2>
 <pre class="cr-diagram"><span class="hi">COURSE FLOW</span>
Classes 1–4   Infrastructure (Compose, networks, ops)
Classes 5–7   ARR / Prowlarr / TRaSH / config sync
Classes 8–10  Home Assistant + secure remote access
Classes 11–13 Local voice → private smart speaker
→ FINAL CAPSTONE verification matrix</pre>
 </section>
</div>

<div class="wrap">
 <section>
 <p class="tag">02 // Classes</p>
 <h2>All thirteen lessons</h2>
 <div class="cr-course-grid">
{''.join(cards)}
 </div>
 </section>
</div>

<div class="wrap">
 <section>
 <p class="tag">03 // Pack extras</p>
 <h2>Workbook, answers, templates</h2>
 <p class="intro">The source markdown pack ships with the site so students and instructors share one curriculum.</p>
 <div class="btn-row">
  <a class="btn btn-ghost" href="course-map.html">Course map</a>
  <a class="btn btn-ghost" href="instructor.html">Instructor answer key</a>
  <a class="btn btn-ghost" href="pack/templates/">CSV templates</a>
  <a class="btn btn-ghost" href="pack/">Raw markdown pack</a>
 </div>
 </section>
</div>
'''
    write(SITE / "index.html", wrap("Homelab Academy · Classroom", "13-class ARR + HA + voice curriculum.", "/classroom/", "ACADEMY", body))


def gen_classes():
    CLASSES_DIR.mkdir(parents=True, exist_ok=True)
    index_lis = []
    for i, (num, fn, title, unit, unit_name) in enumerate(CLASS_META):
        raw = (PACK / "classes" / fn).read_text()
        _md_title, lead, sections = split_sections(raw)
        _lecture, _time, _build, lead_rest = parse_meta(scrub_lectures(lead))
        lead_html = f'<div class="cr-box"><h3>Before you start</h3>{md_fragment(lead_rest)}</div>' if lead_rest.strip() else ""

        section_html = "\n".join(render_section(h2, body, num) for h2, body in sections)

        prev = (f"{CLASS_META[i-1][0]}.html", f"Class {int(CLASS_META[i-1][0])}") if i else ("/classroom/", "Academy")
        nxt = (
            (f"{CLASS_META[i+1][0]}.html", f"Class {int(CLASS_META[i+1][0])}")
            if i < len(CLASS_META) - 1
            else ("/classroom/final-exam.html", "Capstone")
        )

        body = f'''
<div class="wrap">
 <section class="hero flush">
 <div class="stamp">CLASS {int(num):02d}<small>unit {unit} · {H.escape(unit_name.lower())}</small></div>
 <p class="eyebrow" style="margin-top:18px;">Homelab Academy</p>
 <h1 class="display" style="font-size:clamp(1.8rem,5vw,2.8rem);">{H.escape(title)}</h1>
 <p class="lede">Guided lab, break/fix, quiz, and practical gate. Prefer current official docs linked in References.</p>
 </section>
</div>

<div class="wrap">
 {lead_html}
 {section_html}
 {pager(prev, nxt)}
</div>
'''
        write(
            CLASSES_DIR / f"{num}.html",
            wrap(f"Class {int(num)} — {title} · Classroom", title, f"/classroom/classes/{num}.html", f"CLASS {int(num)}", body),
        )
        index_lis.append(
            f'<li><a href="{num}.html"><strong>Class {int(num)}</strong> — {H.escape(title)}</a> <span class="meta">Unit {unit}</span></li>'
        )

    body = f'''
<div class="wrap">
 <section class="hero flush">
 <p class="tag">Classes</p>
 <h1 class="display" style="font-size:clamp(2rem,5vw,3rem);">All 13 classes</h1>
 <p class="lede">Complete in order. Pass each practical gate before advancing.</p>
 </section>
</div>
<div class="wrap">
 <div class="cr-box"><ol class="cr-class-list">{"".join(index_lis)}</ol></div>
 {pager(("/classroom/", "Academy"), ("01.html", "Class 1"))}
</div>
'''
    write(CLASSES_DIR / "index.html", wrap("Classes · Classroom", "All 13 Homelab Academy classes.", "/classroom/classes/", "CLASSES", body))


def gen_md_page(md_name: str, out_name: str, title: str, bar: str, canon: str, tag: str, prev, next_, lede: str):
    raw = (PACK / md_name).read_text()
    sections_html, _ = render_doc_page(raw, title)
    body = f'''
<div class="wrap">
 <section class="hero flush">
 <p class="tag">{H.escape(tag)}</p>
 <h1 class="display" style="font-size:clamp(1.9rem,5vw,3rem);">{H.escape(title)}</h1>
 <p class="lede">{H.escape(lede)}</p>
 </section>
</div>
<div class="wrap">
 {sections_html}
 {pager(prev, next_)}
</div>
'''
    write(SITE / out_name, wrap(f"{title} · Classroom", title, canon, bar, body))


def gen_references():
    ref = PACK / "references"
    out = SITE / "references"
    out.mkdir(parents=True, exist_ok=True)
    links = []
    for f in sorted(ref.glob("*.md")):
        # Do not publish video-link catalogs on the public site
        if "VIDEO" in f.stem.upper():
            continue
        slug = f.stem.lower().replace("_", "-")
        html_name = f"{slug}.html"
        sections_html, _ = render_doc_page(f.read_text(), f.stem)
        body = f'''
<div class="wrap">
 <section class="hero flush">
 <p class="tag">References</p>
 <h1 class="display" style="font-size:clamp(1.7rem,4.5vw,2.6rem);">{H.escape(f.stem.replace("_", " ").title())}</h1>
 <p class="lede">Current official documentation for commands and UI. No lecture videos on Academy pages.</p>
 </section>
</div>
<div class="wrap">
 {sections_html}
 {pager(("/classroom/references/", "References"), ("/classroom/", "Academy"))}
</div>
'''
        write(out / html_name, wrap(f"{f.stem} · Classroom", f.stem, f"/classroom/references/{html_name}", "REFS", body))
        links.append(f'<li><a href="{html_name}">{H.escape(f.stem.replace("_", " ").title())}</a></li>')

    # Remove previously generated video-links page if present
    stale = out / "video-links.html"
    if stale.exists():
        stale.unlink()

    trows = "".join(
        f'<li><a href="/classroom/pack/templates/{H.escape(t.name)}">{H.escape(t.name)}</a></li>'
        for t in sorted((PACK / "templates").glob("*"))
    )
    body = f'''
<div class="wrap">
 <section class="hero flush">
 <p class="tag">References</p>
 <h1 class="display" style="font-size:clamp(1.9rem,5vw,3rem);">References &amp; templates</h1>
 <p class="lede">Official docs and CSV evidence templates. Lecture videos are not listed on this site.</p>
 </section>
</div>
<div class="wrap">
 <div class="cr-box"><h3>Documents</h3><ul>{"".join(links)}</ul></div>
 <div class="cr-box"><h3>CSV templates</h3><ul>{trows}</ul></div>
 {pager(("/classroom/", "Academy"), ("official-documentation.html", "Official docs"))}
</div>
'''
    write(out / "index.html", wrap("References · Classroom", "Docs and templates.", "/classroom/references/", "REFS", body))


def gen_glossary_stub():
    body = '''
<div class="wrap">
 <section class="hero flush">
 <p class="tag">Glossary</p>
 <h1 class="display" style="font-size:clamp(1.9rem,5vw,3rem);">Vocabulary lives in each class</h1>
 <p class="lede">Every pack lesson has its own vocabulary table. Jump to the unit you need.</p>
 <div class="btn-row" style="margin-top:22px;">
  <a class="btn btn-primary" href="classes/01.html">Class 1</a>
  <a class="btn btn-ghost" href="classes/05.html">Class 5 — ARR</a>
  <a class="btn btn-ghost" href="classes/08.html">Class 8 — HA</a>
  <a class="btn btn-ghost" href="classes/11.html">Class 11 — Voice</a>
 </div>
 </section>
</div>
'''
    write(SITE / "glossary.html", wrap("Glossary · Classroom", "Per-class vocabulary.", "/classroom/glossary.html", "GLOSSARY", body))


def gen_redirects():
    redirects = {
        "start.html": "/classroom/classes/01.html",
        "path.html": "/classroom/classes/",
        "units/1-infrastructure/": "/classroom/classes/01.html",
        "units/2-arr/": "/classroom/classes/05.html",
        "units/3-home-assistant/": "/classroom/classes/08.html",
        "units/4-voice/": "/classroom/classes/11.html",
        "courses/": "/classroom/",
    }
    for src, dst in redirects.items():
        path = SITE / src / "index.html" if src.endswith("/") else SITE / src
        write(
            path,
            f'<!doctype html><meta http-equiv="refresh" content="0;url={dst}">'
            f'<script>location.replace("{dst}")</script>',
        )


def sync_github():
    readme = (PACK / "README.md").read_text()
    (GH / "README.md").write_text(
        "# Otaconskeep Classroom — Homelab Academy\n\n"
        "**Site:** https://otaconskeep.github.io/classroom/\n\n"
        + readme
        + "\n\n## License\n\nMIT — Antonio G. Garcia (Otaconskeep)\n"
    )
    dest = GH / "pack"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(PACK, dest)
    print("github pack synced")


def main():
    assert PACK.is_dir(), PACK
    gen_hub()
    gen_classes()
    gen_md_page(
        "COURSE_MAP.md", "course-map.html", "Course map", "MAP",
        "/classroom/course-map.html", "Course map",
        ("/classroom/", "Academy"), ("classes/", "Classes"),
        "Sequence, gates, and final architecture for the 13-class pack.",
    )
    gen_md_page(
        "STUDENT_WORKBOOK.md", "workbook.html", "Student workbook", "WORKBOOK",
        "/classroom/workbook.html", "Workbook",
        ("/classroom/", "Academy"), ("final-exam.html", "Capstone"),
        "Reusable notes and evidence pages for every class.",
    )
    gen_md_page(
        "FINAL_CAPSTONE.md", "final-exam.html", "Final capstone", "CAPSTONE",
        "/classroom/final-exam.html", "Capstone",
        ("classes/13.html", "Class 13"), ("/classroom/", "Academy"),
        "End-to-end verification matrix. “It seems to work” is not evidence.",
    )
    gen_md_page(
        "INSTRUCTOR_ANSWER_KEY.md", "instructor.html", "Instructor answer key", "INSTRUCTOR",
        "/classroom/instructor.html", "Instructor",
        ("/classroom/", "Academy"), ("workbook.html", "Workbook"),
        "Quiz answers and practical acceptance criteria.",
    )
    gen_references()
    gen_glossary_stub()
    gen_redirects()
    sync_github()
    print("DONE — pack in site chrome")


if __name__ == "__main__":
    main()

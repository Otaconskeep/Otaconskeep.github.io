#!/usr/bin/env python3
"""Build Homelab Academy Classroom site from Homelab_Academy_13_Class_Pack."""
from __future__ import annotations

import html as H
import re
from pathlib import Path

import markdown

SITE = Path("/root/otaconskeep-site/classroom")
PACK = SITE / "pack"
CLASSES_DIR = SITE / "classes"
GH = Path("/root/Classroom")

NAV = '''<nav class="topnav">
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
 <a href="https://github.com/Otaconskeep/Classroom" target="_blank" rel="noopener">GitHub</a>
 <a class="discord" href="https://discord.gg/cZDeqECzX" target="_blank" rel="noopener">Discord</a>
 </div></div>
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

FOOT = '''<footer class="sitefoot"><div class="wrap">
<span>Otaconskeep Classroom · Homelab Academy</span>
<span><a href="https://github.com/Otaconskeep/Classroom">GitHub</a> · <a href="/classroom/pack/">Source pack</a></span>
</div></footer>
<script src="/classroom/classroom.js?v=20260921d"></script>'''

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
<link rel="stylesheet" href="/classroom/classroom.css?v=20260921d">
</head>
<body>
<div class="filebar"><div class="wrap"><span>CLASSROOM // HOMELAB ACADEMY</span><span>{bar}<span class="blink"></span></span></div></div>
{nav}{sub}
'''

CLASS_META = [
    ("01", "01_PROXMOX_VIRTUALIZATION.md", "Proxmox, VMs, and LXC", "1", "Infrastructure"),
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


def md_to_html(text: str) -> str:
    MD.reset()
    # Keep mermaid readable as diagrams (no embed dependency)
    text = re.sub(
        r"```mermaid\n(.*?)```",
        lambda m: "```text\n" + m.group(1).strip() + "\n```",
        text,
        flags=re.S,
    )
    html = MD.convert(text)
    # External links open safely
    html = re.sub(
        r'<a href="(https?://[^"]+)"',
        r'<a href="\1" target="_blank" rel="noopener"',
        html,
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
        )
        + f'<div class="wrap cr-md">{body}</div>\n{FOOT}\n</body></html>\n'
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print("wrote", path.relative_to(SITE))


def pager(prev, next_):
    left = f'<a href="{prev[0]}">← {H.escape(prev[1])}</a>' if prev else "<span></span>"
    right = f'<a href="{next_[0]}">{H.escape(next_[1])} →</a>' if next_ else "<span></span>"
    return f'<div class="cr-pager">{left}{right}</div>'


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
<section class="hero flush">
 <div class="stamp">HOMELAB ACADEMY<small>13-class pack</small></div>
 <p class="eyebrow" style="margin-top:18px;">Otaconskeep Classroom · Free</p>
 <h1 class="display" style="font-size:clamp(2rem,6vw,3.4rem);">Watch → Understand → Build → Break → Fix → Verify</h1>
 <p class="lede">Complete build-first curriculum for ARR, Home Assistant, and local voice. Lectures stay off-site — this site is the lab, workbook, and verification matrix.</p>
 <div class="btn-row" style="margin-top:22px;">
  <a class="btn btn-primary" href="classes/01.html">Start Class 1</a>
  <a class="btn btn-ghost" href="workbook.html">Student workbook</a>
  <a class="btn btn-ghost" href="final-exam.html">Final capstone</a>
  <a class="btn btn-ghost" href="references/">References</a>
 </div>
</section>
<div class="cr-callout tip"><strong>How to use:</strong> read the class → do the guided lab once → run break/fix → quiz → pass the practical gate → log evidence in the verification matrix.</div>
<pre class="cr-diagram"><span class="hi">GATES</span>
1–4 Infrastructure  →  5–7 ARR / quality  →  8–10 Home Assistant  →  11–13 Local voice
→ FINAL CAPSTONE verification matrix</pre>
<div class="cr-course-grid">
{''.join(cards)}
</div>
<section>
 <p class="tag">Also in the pack</p>
 <div class="btn-row">
  <a class="btn btn-ghost" href="course-map.html">Course map</a>
  <a class="btn btn-ghost" href="instructor.html">Instructor answer key</a>
  <a class="btn btn-ghost" href="pack/templates/">CSV templates</a>
  <a class="btn btn-ghost" href="pack/">Raw markdown pack</a>
 </div>
</section>
'''
    write(SITE / "index.html", wrap("Homelab Academy · Classroom", "13-class ARR + HA + voice curriculum.", "/classroom/", "ACADEMY", body))


def gen_classes():
    CLASSES_DIR.mkdir(parents=True, exist_ok=True)
    index_lis = []
    for i, (num, fn, title, unit, unit_name) in enumerate(CLASS_META):
        src = PACK / "classes" / fn
        raw = src.read_text()
        content = md_to_html(raw)
        prev = (f"{CLASS_META[i-1][0]}.html", f"Class {int(CLASS_META[i-1][0])}") if i else ("/classroom/", "Academy")
        nxt = (f"{CLASS_META[i+1][0]}.html", f"Class {int(CLASS_META[i+1][0])}") if i < len(CLASS_META) - 1 else ("/classroom/final-exam.html", "Capstone")
        body = f'''
<section class="hero flush">
 <p class="tag">Unit {unit} — {H.escape(unit_name)} · Class {int(num)}</p>
 <h1 class="display" style="font-size:clamp(1.6rem,4.5vw,2.5rem);">{H.escape(title)}</h1>
 <p class="lede">From the Homelab Academy 13-class pack. No video embeds — lecture links stay in the lesson text / references.</p>
</section>
<article class="cr-article">
{content}
</article>
{pager(prev, nxt)}
'''
        write(CLASSES_DIR / f"{num}.html", wrap(f"Class {int(num)} — {title} · Classroom", title, f"/classroom/classes/{num}.html", f"CLASS {int(num)}", body))
        index_lis.append(f'<li><a href="{num}.html"><strong>Class {int(num)}</strong> — {H.escape(title)}</a></li>')

    body = f'''
<section class="hero flush">
 <p class="tag">Classes</p>
 <h1 class="display" style="font-size:clamp(1.8rem,5vw,2.8rem);">All 13 classes</h1>
 <p class="lede">Complete in order. Pass each practical gate before advancing.</p>
</section>
<div class="cr-box"><ol class="cr-class-list">{''.join(index_lis)}</ol></div>
{pager(("/classroom/", "Academy"), ("01.html", "Class 1"))}
'''
    write(CLASSES_DIR / "index.html", wrap("Classes · Classroom", "All 13 Homelab Academy classes.", "/classroom/classes/", "CLASSES", body))


def gen_md_page(md_name: str, out_name: str, title: str, bar: str, canon: str, prev, next_):
    raw = (PACK / md_name).read_text()
    body = f'''
<section class="hero flush">
 <p class="tag">Homelab Academy</p>
 <h1 class="display" style="font-size:clamp(1.8rem,5vw,2.8rem);">{H.escape(title)}</h1>
</section>
<article class="cr-article">
{md_to_html(raw)}
</article>
{pager(prev, next_)}
'''
    write(SITE / out_name, wrap(f"{title} · Classroom", title, canon, bar, body))


def gen_references():
    ref = PACK / "references"
    out = SITE / "references"
    out.mkdir(parents=True, exist_ok=True)
    links = []
    for f in sorted(ref.glob("*.md")):
        slug = f.stem.lower().replace("_", "-")
        html_name = f"{slug}.html"
        body = f'''
<section class="hero flush">
 <p class="tag">References</p>
 <h1 class="display" style="font-size:clamp(1.6rem,4.5vw,2.4rem);">{H.escape(f.stem.replace("_", " ").title())}</h1>
 <p class="lede">Lecture links and official docs. Videos are not embedded on Academy pages.</p>
</section>
<article class="cr-article">{md_to_html(f.read_text())}</article>
{pager(("/classroom/references/", "References"), ("/classroom/", "Academy"))}
'''
        write(out / html_name, wrap(f"{f.stem} · Classroom", f.stem, f"/classroom/references/{html_name}", "REFS", body))
        links.append(f'<li><a href="{html_name}">{H.escape(f.stem.replace("_", " ").title())}</a></li>')

    # templates listing
    templates = PACK / "templates"
    trows = "".join(
        f'<li><a href="/classroom/pack/templates/{H.escape(t.name)}">{H.escape(t.name)}</a></li>'
        for t in sorted(templates.glob("*"))
    )
    body = f'''
<section class="hero flush">
 <p class="tag">References</p>
 <h1 class="display" style="font-size:clamp(1.8rem,5vw,2.8rem);">References &amp; templates</h1>
</section>
<div class="cr-box"><h3>Documents</h3><ul>{''.join(links)}</ul></div>
<div class="cr-box"><h3>CSV templates</h3><ul>{trows}</ul></div>
{pager(("/classroom/", "Academy"), ("official-documentation.html", "Official docs"))}
'''
    write(out / "index.html", wrap("References · Classroom", "Docs and templates.", "/classroom/references/", "REFS", body))


def gen_glossary_stub():
    # Keep a simple glossary landing pointing into classes
    body = '''
<section class="hero flush">
 <p class="tag">Glossary</p>
 <h1 class="display" style="font-size:clamp(1.8rem,5vw,2.8rem);">Vocabulary lives in each class</h1>
 <p class="lede">Every class in the 13-class pack has its own vocabulary table. Start with Class 1 or jump to the unit you need.</p>
 <div class="btn-row" style="margin-top:18px;">
  <a class="btn btn-primary" href="classes/01.html">Class 1</a>
  <a class="btn btn-ghost" href="classes/05.html">Class 5 — ARR</a>
  <a class="btn btn-ghost" href="classes/08.html">Class 8 — HA</a>
  <a class="btn btn-ghost" href="classes/11.html">Class 11 — Voice</a>
 </div>
</section>
'''
    write(SITE / "glossary.html", wrap("Glossary · Classroom", "Per-class vocabulary.", "/classroom/glossary.html", "GLOSSARY", body))


def gen_redirects():
    # Old unit URLs → new structure
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
        path = SITE / src
        if src.endswith("/"):
            path = SITE / src / "index.html"
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
    # mirror pack
    import shutil

    dest = GH / "pack"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(PACK, dest)
    print("github pack synced")


def main():
    assert PACK.is_dir(), PACK
    gen_hub()
    gen_classes()
    gen_md_page("COURSE_MAP.md", "course-map.html", "Course map", "MAP", "/classroom/course-map.html", ("/classroom/", "Academy"), ("classes/", "Classes"))
    gen_md_page("STUDENT_WORKBOOK.md", "workbook.html", "Student workbook", "WORKBOOK", "/classroom/workbook.html", ("/classroom/", "Academy"), ("final-exam.html", "Capstone"))
    gen_md_page("FINAL_CAPSTONE.md", "final-exam.html", "Final capstone", "CAPSTONE", "/classroom/final-exam.html", ("classes/13.html", "Class 13"), ("/classroom/", "Academy"))
    gen_md_page("INSTRUCTOR_ANSWER_KEY.md", "instructor.html", "Instructor answer key", "INSTRUCTOR", "/classroom/instructor.html", ("/classroom/", "Academy"), ("workbook.html", "Workbook"))
    gen_references()
    gen_glossary_stub()
    gen_redirects()
    sync_github()
    print("DONE 13 classes from pack")


if __name__ == "__main__":
    main()

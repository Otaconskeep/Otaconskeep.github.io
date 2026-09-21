#!/usr/bin/env python3
"""Generate Homelab Academy Classroom pages."""
from __future__ import annotations
from pathlib import Path
import html as H

SITE = Path(__file__).resolve().parent
COURSES = SITE / "courses"
GH = Path("/root/Classroom")
DOCS = GH / "docs"

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
 <a href="/classroom/start.html">Start here</a>
 <a href="/classroom/path.html">Choose path</a>
 <a href="/classroom/glossary.html">Glossary</a>
 <a href="/classroom/courses/00-fundamentals/">Course 0</a>
 <a href="/classroom/courses/01-arr-stack/">Course 1</a>
 <a href="/classroom/courses/04-ha-fundamentals/">HA 101</a>
 <a href="/classroom/courses/06-local-voice/">Voice</a>
 </div>
</nav>'''

FOOT = '''<footer class="sitefoot"><div class="wrap">
<span>Otaconskeep Classroom · Homelab Academy</span>
<span><a href="https://github.com/Otaconskeep/Classroom">GitHub</a> · <a href="/classroom/glossary.html">Glossary</a></span>
</div></footer>
<script src="/classroom/classroom.js?v=20260921b"></script>'''

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
<link rel="stylesheet" href="/classroom/classroom.css?v=20260921b">
</head>
<body>
<div class="filebar"><div class="wrap"><span>CLASSROOM // HOMELAB ACADEMY</span><span>{bar}<span class="blink"></span></span></div></div>
{nav}
{sub}
'''

OSBAR = '''<div class="cr-osbar" role="group" aria-label="Show instructions for">
 <span>Show steps for:</span>
 <button type="button" class="win" data-os="windows">Windows (WSL2 + Docker)</button>
 <button type="button" class="lin" data-os="linux">Linux (Ubuntu/Debian + Docker)</button>
 <a href="/classroom/path.html" style="margin-left:auto;font-size:.85rem;">Change path</a>
</div>'''

LEVEL = {
  "baby": ('baby', '🟢 Baby step — no previous knowledge expected'),
  "mid": ('mid', '🟡 Intermediate — Docker/networking basics'),
  "adv": ('adv', '🔴 Advanced — VPN, VLANs, proxies, custom voice, GPU'),
}

GLOSSARY = [
  ("ARR", "Radarr / Sonarr ecosystem", "Apps that automate your media library."),
  ("API", "Application Programming Interface", "How programs talk to each other."),
  ("IP", "Internet Protocol address", "A device's network address."),
  ("LAN", "Local Area Network", "Your home network."),
  ("WAN", "Wide Area Network", "The internet side of your router."),
  ("DNS", "Domain Name System", "Turns names into IP addresses."),
  ("DHCP", "Dynamic Host Configuration Protocol", "Automatically gives devices IP addresses."),
  ("VLAN", "Virtual LAN", "Separates devices into isolated networks."),
  ("VPN", "Virtual Private Network", "Encrypted / private network connection."),
  ("UID", "User ID", "Linux number representing a user."),
  ("GID", "Group ID", "Linux number representing a user group."),
  ("SMB", "Server Message Block", "Windows-style network file sharing."),
  ("NFS", "Network File System", "Linux-oriented network file sharing."),
  ("YAML", "YAML Ain't Markup Language", "Human-readable configuration format."),
  ("Docker", "Container platform", "Runs apps in isolated packages."),
  ("Container", "Running Docker application", "A lightweight packaged application."),
  ("Image", "Container template", "Blueprint used to create a container."),
  ("Volume", "Persistent storage", "Data that survives container restarts."),
  ("Bind mount", "Host folder mounted into container", "Lets Docker see one of your folders."),
  ("Port", "Network communication endpoint", "The door an application listens on."),
  ("Reverse proxy", "Gateway to internal websites", "Gives internal services friendly / secure URLs."),
  ("Hardlink", "Second directory entry for one file", "Two names, one copy on disk — great for torrents."),
  ("Atomic move", "Same-filesystem rename/move", "Usenet finish step without a slow full copy."),
  ("Indexer", "Torrent / Usenet search source", "Where ARR apps look for releases."),
  ("Custom Format", "ARR scoring rule", "Grades releases so the best one wins."),
  ("TRaSH", "TRaSH Guides", "Maintained playbook for ARR folder layouts and profiles."),
  ("Recyclarr", "TRaSH sync tool", "Pushes guide profiles into Sonarr/Radarr automatically."),
  ("Prowlarr", "Indexer manager", "One place to manage search sources for ARR apps."),
  ("Sonarr", "TV automation", "Finds, downloads, renames, and files TV shows."),
  ("Radarr", "Movie automation", "Finds, downloads, renames, and files movies."),
  ("Lidarr", "Music automation", "ARR-style automation for music."),
  ("Bazarr", "Subtitle automation", "Grabs subtitles for your library."),
  ("qBittorrent", "Torrent client", "Downloads torrent files."),
  ("SABnzbd", "Usenet client", "Downloads and unpacks Usenet posts."),
  ("Gluetun", "VPN container", "Puts only the torrent client behind a VPN."),
  ("Seerr", "Request UI family", "Friends request movies/shows; ARR does the work."),
  ("Tautulli", "Plex monitor", "Shows who watched what on Plex."),
  ("STT", "Speech to Text", "Voice → words."),
  ("TTS", "Text to Speech", "Words → voice."),
  ("LLM", "Large Language Model", "AI language model."),
  ("Wyoming", "Voice service protocol", "Lets Home Assistant connect speech / wake-word services."),
  ("Piper", "Text-to-speech engine", "Gives Home Assistant a local voice."),
  ("Whisper", "Speech recognition model", "Converts spoken audio to text."),
  ("ESPHome", "Device firmware / platform", "Connects DIY devices directly to Home Assistant."),
  ("HA", "Home Assistant", "Home automation platform."),
  ("MQTT", "Message Queuing Telemetry Transport", "Lightweight messaging between smart devices."),
  ("Zigbee", "Low-power mesh radio", "Sensors and plugs that hop messages through each other."),
  ("Thread", "Low-power IPv6 mesh", "Mesh used by many Matter devices (including some locks)."),
  ("Matter", "Smart-home language", "Shared way devices talk across brands."),
  ("Border router", "Thread ↔ LAN bridge", "Device that lets Thread gadgets join your home network."),
  ("Assist", "HA voice pipeline", "Home Assistant's built-in voice control system."),
]


def wrap(title, desc, canon, bar, body):
    return (
        HEAD.format(title=H.escape(title), desc=H.escape(desc), canon=canon, bar=H.escape(bar), nav=NAV, sub=SUB)
        + f'<div class="wrap">{body}</div>\n{FOOT}\n</body></html>\n'
    )


def badge(level):
    cls, label = LEVEL[level]
    return f'<span class="cr-badge {cls}">{label}</span>'


def mean_more(mean, more):
    return f'''<div class="cr-actions">
 <button type="button" class="cr-btn" data-cr="mean" aria-expanded="false">What's this mean?</button>
 <button type="button" class="cr-btn" data-cr="more" aria-expanded="false">More detail</button>
</div>
<div class="cr-panel mean" hidden><strong>In plain words:</strong> {mean}</div>
<div class="cr-panel more" hidden><strong>More detail:</strong> {more}</div>'''


def step_block(n, title, body, *, mean="", more="", windows=None, linux=None, common_code=None):
    parts = [f'<div class="cr-step"><h3>Step {n} — {H.escape(title)}</h3><p class="cr-body">{body}</p>']
    if windows is not None or linux is not None:
        if windows is not None:
            parts.append(f'<div class="cr-os-block" data-os="windows"><span class="cr-os-label win">Windows</span><pre class="cr-code">{H.escape(windows)}</pre></div>')
        if linux is not None:
            parts.append(f'<div class="cr-os-block" data-os="linux"><span class="cr-os-label lin">Linux</span><pre class="cr-code">{H.escape(linux)}</pre></div>')
    if common_code:
        parts.append(f'<pre class="cr-code">{H.escape(common_code)}</pre>')
    if mean or more:
        parts.append(mean_more(mean, more))
    parts.append('</div>')
    return '\n'.join(parts)


def checkpoint(cid, items, next_href, next_label):
    boxes = []
    for i, text in enumerate(items):
        boxes.append(f'<label><input type="checkbox" data-k="{i}"> {H.escape(text)}</label>')
    return f'''<div class="cr-check" data-check-id="{cid}">
 <h3>Checkpoint — before you continue</h3>
 {''.join(boxes)}
 <div class="cr-gate">Check every box above. When all are true, continue → <a href="{next_href}">{H.escape(next_label)}</a></div>
</div>'''


def lesson_page(meta):
    """meta keys: id, course_slug, course_title, title, level, learning, prereqs, words, diagram, steps_html, checkpoint_html, prev, next"""
    words = ''.join(f'<a href="/classroom/glossary.html#{H.escape(w.lower().replace(" ","-"))}">{H.escape(w)}</a>' for w in meta["words"])
    prereq = ''.join(f'<li>{H.escape(p)}</li>' for p in meta["prereqs"])
    body = f'''
<section class="hero flush cr-lesson-head">
 <div class="row">{badge(meta["level"])}<span class="tag" style="margin:0">{H.escape(meta["course_title"])} · Lesson {H.escape(meta["id"])}</span></div>
 <h1 class="display" style="font-size:clamp(1.7rem,4.5vw,2.6rem);">{H.escape(meta["title"])}</h1>
</section>
{OSBAR}
<div class="cr-box"><h3>What you are learning</h3><p>{meta["learning"]}</p></div>
<div class="cr-box"><h3>You should already have</h3><ul>{prereq}</ul></div>
<div class="cr-box"><h3>New words</h3><div class="cr-words">{words}</div></div>
<div class="cr-box"><h3>Picture</h3><pre class="cr-diagram">{meta["diagram"]}</pre></div>
{meta["steps_html"]}
{meta["checkpoint_html"]}
<div class="cr-pager">
 <a href="{meta["prev"][0]}">← {H.escape(meta["prev"][1])}</a>
 <a href="{meta["next"][0]}">{H.escape(meta["next"][1])} →</a>
</div>'''
    return wrap(
        f"Lesson {meta['id']} — {meta['title']} · Classroom",
        meta["learning"][:150],
        f"/classroom/courses/{meta['course_slug']}/{meta['file']}",
        f"LESSON {meta['id']}",
        body,
    )


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print("wrote", path.relative_to(SITE) if str(path).startswith(str(SITE)) else path)


# ---------- static pages ----------
def gen_hub():
    courses = [
        ("00", "Homelab Fundamentals", "Networking, IPs, DNS, storage, Docker, Windows/Linux basics.", "00-fundamentals", "baby"),
        ("01", "Building the ARR Stack", "TRaSH order, qBit, SAB, Prowlarr, Sonarr, Radarr, Recyclarr.", "01-arr-stack", "baby"),
        ("02", "Perfecting the ARR Stack", "Hardlinks, Custom Formats, anime, Maintainerr, cross-seed.", "02-perfecting-arr", "mid"),
        ("03", "Plex / Jellyfin", "Libraries, Direct Play, transcoding, hardware encode, remote access.", "03-plex-jellyfin", "mid"),
        ("04", "Home Assistant Fundamentals", "Devices, entities, integrations, dashboards, automations.", "04-ha-fundamentals", "baby"),
        ("05", "Home Assistant Advanced", "Zigbee, ESPHome, MQTT, Matter, Thread, network isolation.", "05-ha-advanced", "mid"),
        ("06", "Local Voice", "Assist, Whisper, Piper, Wyoming, Linux Voice Assistant, satellites.", "06-local-voice", "mid"),
        ("07", "Ultimate Homelab", "VLANs, VPNs, reverse proxies, backups, GPUs, local AI, HA.", "07-ultimate", "adv"),
    ]
    cards = []
    for num, title, blurb, slug, level in courses:
        cards.append(f'''<a class="cr-course-card" href="courses/{slug}/">
 <div class="num">{num}</div>
 <div><h3>{H.escape(title)}</h3><p>{H.escape(blurb)}</p><div class="meta">{LEVEL[level][1]}</div></div>
</a>''')
    body = f'''
<section class="hero flush">
 <div class="stamp">HOMELAB ACADEMY<small>self-paced · classroom</small></div>
 <p class="eyebrow" style="margin-top:18px;">Otaconskeep Classroom</p>
 <h1 class="display" style="font-size:clamp(2.1rem,6vw,3.5rem);">Ultimate Homelab<br>ARR · Home Assistant · Voice</h1>
 <p class="lede">Not a wiki dump. Every lesson teaches <strong>one concept</strong>, shows <strong>one picture</strong>, gives <strong>one action</strong>, then a <strong>checkpoint</strong> before you move on. Windows and Linux split only where install paths differ — then rejoin the common course.</p>
 <div class="btn-row" style="margin-top:22px;">
  <a class="btn btn-primary" href="start.html">Start here</a>
  <a class="btn btn-ghost" href="path.html">Choose your path</a>
  <a class="btn btn-ghost" href="glossary.html">Glossary</a>
 </div>
</section>
<pre class="cr-diagram"><span class="hi">START HERE</span>
   │
   ├── What are we building?
   ├── Network diagram
   ├── Acronyms / terminology
   └── Hardware checklist
          │
          ▼
     <span class="hi">CHOOSE YOUR PATH</span>
      Windows (WSL2+Docker)  ·  Linux (Ubuntu+Docker)
          │
          └──────────► <span class="hi">COMMON COURSE</span>
                         Docker → Storage → ARR
                         Home Assistant → Voice → Advanced</pre>
<section>
 <p class="tag">Eight courses</p>
 <h2>Curriculum map</h2>
 <p class="intro">Pick Course 0 if you are new. Skip ahead only if you can pass the previous course lab.</p>
 <div class="cr-course-grid">{''.join(cards)}</div>
</section>
<div class="cr-callout tip"><strong>Classroom rule:</strong> if the checkpoint boxes are not all true, do not continue. Fix the gate first — that is how this stays a course, not a scroll of hope.</div>
'''
    write(SITE / "index.html", wrap("Homelab Academy · Classroom · Otaconskeep", "Self-paced ARR, Home Assistant, and local voice course.", "/classroom/", "ACADEMY", body))


def gen_start():
    body = f'''
<section class="hero flush">
 {badge("baby")}
 <h1 class="display" style="font-size:clamp(2rem,5vw,3rem);margin-top:12px;">Start here</h1>
 <p class="lede">You are building an automated media library and a local smart home that can talk back — without turning day one into VLANs and iptables.</p>
</section>
<div class="cr-box"><h3>What we are building</h3>
<p>A homelab where: you request a movie → ARR finds and files it → Plex/Jellyfin shows it → Home Assistant watches the house → a local voice satellite can answer without a cloud brain.</p>
{mean_more("You want robots that fetch shows, a TV app that plays them, and a house brain that listens at home. We build that in layers so nothing collapses.", "Capstone (Course 7): request → acquire → organize → publish → HA monitors infrastructure → local voice reports status.")}
</div>
<pre class="cr-diagram"><span class="hi">YOU</span>
 │
 ▼
<span class="hi">SEERR</span>  "Give me Dune"
 │
 ▼
<span class="hi">RADARR</span>  already have it?
 │
 ▼
<span class="hi">PROWLARR</span> → indexer → download client
 │
 ▼
<span class="hi">/data/media/movies/Dune</span>
 │
 ▼
<span class="hi">PLEX / JELLYFIN</span></pre>
<div class="cr-box"><h3>Hardware checklist (minimum)</h3>
<ul>
<li>☐ Always-on PC / NUC / NAS that can run Docker</li>
<li>☐ Enough disk for media (SSD for apps, HDD/NAS for library is fine)</li>
<li>☐ Wired Ethernet preferred for the server</li>
<li>☐ Optional later: Zigbee stick, Pi for voice, NVIDIA GPU for Whisper/Plex encode</li>
</ul>
</div>
<div class="cr-box"><h3>Difficulty badges you will see</h3>
<p>{badge("baby")} &nbsp; {badge("mid")} &nbsp; {badge("adv")}</p>
<p style="margin-top:10px;color:var(--cream-dim);">If you see 🔴 on day one, stop and go back. Those lessons assume you already finished earlier labs.</p>
</div>
{checkpoint("start-here", [
  "I know we build media automation first, then Home Assistant, then voice",
  "I opened the glossary once so I know where acronyms live",
  "I have (or will pick) a machine that can run Docker",
], "path.html", "Choose your path")}
<div class="cr-pager"><a href="/classroom/">← Academy</a><a href="path.html">Choose path →</a></div>
'''
    write(SITE / "start.html", wrap("Start here · Classroom", "What we are building, diagram, hardware checklist.", "/classroom/start.html", "START HERE", body))


def gen_path():
    body = f'''
<section class="hero flush">
 {badge("baby")}
 <h1 class="display" style="font-size:clamp(2rem,5vw,3rem);margin-top:12px;">Choose your path</h1>
 <p class="lede">Windows and Linux only split where install, paths, and permissions differ. Sonarr itself is the same idea on both. After Docker is running, you rejoin the common course.</p>
</section>
<div class="cr-path-grid">
 <a class="cr-path-card win" href="courses/00-fundamentals/windows.html" data-set-os="windows">
  <h3>Windows 11</h3>
  <p><strong>Recommended:</strong> WSL2 + Docker Desktop (or Engine in WSL). Native Windows containers are not the ARR path we teach.</p>
 </a>
 <a class="cr-path-card lin" href="courses/00-fundamentals/linux.html" data-set-os="linux">
  <h3>Linux</h3>
  <p><strong>Recommended:</strong> Ubuntu / Debian + Docker Engine. Best long-term server path.</p>
 </a>
 <a class="cr-path-card dim" href="#soon">
  <h3>Proxmox / VM host</h3>
  <p>Version 1 points you to a Linux VM guest, then the Linux path. Full Proxmox track lands in Course 7.</p>
 </a>
 <a class="cr-path-card dim" href="#soon">
  <h3>NAS</h3>
  <p>Use NAS for /data storage; run Docker on a small Linux/WSL box that mounts the share. Deep NAS UI tracks come later.</p>
 </a>
</div>
<table class="tablewrap" style="width:100%;border-collapse:collapse;margin:18px 0;">
<thead><tr><th style="text-align:left;padding:8px;border-bottom:1px solid var(--line);">Concept</th><th style="text-align:left;padding:8px;border-bottom:1px solid var(--line);">Windows</th><th style="text-align:left;padding:8px;border-bottom:1px solid var(--line);">Linux</th></tr></thead>
<tbody>
<tr><td style="padding:8px;border-bottom:1px solid var(--line);">Terminal</td><td style="padding:8px;border-bottom:1px solid var(--line);">PowerShell / WSL</td><td style="padding:8px;border-bottom:1px solid var(--line);">Bash</td></tr>
<tr><td style="padding:8px;border-bottom:1px solid var(--line);">Path example</td><td style="padding:8px;border-bottom:1px solid var(--line);"><span class="mono">/mnt/d/homelab</span> in WSL</td><td style="padding:8px;border-bottom:1px solid var(--line);"><span class="mono">/home/you/homelab</span></td></tr>
<tr><td style="padding:8px;border-bottom:1px solid var(--line);">Docker</td><td style="padding:8px;border-bottom:1px solid var(--line);">Docker Desktop / Engine in WSL</td><td style="padding:8px;border-bottom:1px solid var(--line);">Docker Engine</td></tr>
<tr><td style="padding:8px;border-bottom:1px solid var(--line);">Permissions</td><td style="padding:8px;border-bottom:1px solid var(--line);">NTFS + WSL mappings</td><td style="padding:8px;border-bottom:1px solid var(--line);">UID/GID + chmod/chown</td></tr>
<tr><td style="padding:8px;border-bottom:1px solid var(--line);">Firewall</td><td style="padding:8px;border-bottom:1px solid var(--line);">Windows Firewall</td><td style="padding:8px;border-bottom:1px solid var(--line);">UFW / nftables</td></tr>
</tbody>
</table>
{checkpoint("choose-path", [
  "I picked Windows (WSL2+Docker) or Linux (Ubuntu/Debian+Docker)",
  "I understand most ARR lessons are shared after Docker works",
], "courses/00-fundamentals/", "Open Course 0")}
<div class="cr-pager"><a href="start.html">← Start here</a><a href="courses/00-fundamentals/">Course 0 →</a></div>
'''
    write(SITE / "path.html", wrap("Choose your path · Classroom", "Windows vs Linux fork for Homelab Academy.", "/classroom/path.html", "PATH", body))


def gen_glossary():
    items = []
    for term, meaning, baby in GLOSSARY:
        aid = term.lower().replace(" ", "-")
        items.append(f'''<details id="{H.escape(aid)}"><summary>{H.escape(term)} — {H.escape(meaning)}</summary>
<p class="baby">{H.escape(baby)}</p>
<p class="tech">{H.escape(meaning)}</p>
</details>''')
    body = f'''
<section class="hero flush">
 <h1 class="display" style="font-size:clamp(2rem,5vw,3rem);">What the hell does that mean?</h1>
 <p class="lede">Permanent glossary. Lessons link here. Plain words first — then the technical name.</p>
</section>
<div class="cr-glossary">{''.join(items)}</div>
<div class="cr-pager"><a href="/classroom/">← Academy</a><a href="start.html">Start here →</a></div>
'''
    write(SITE / "glossary.html", wrap("Glossary · Classroom", "ARR, Docker, networking, Home Assistant, and voice acronyms in plain words.", "/classroom/glossary.html", "GLOSSARY", body))


def course_index(num, slug, title, level, blurb, lessons, lab=None, troubleshoot=None):
    lis = ''.join(f'<li><a href="{fn}">{H.escape(label)}</a></li>' for fn, label in lessons)
    extra = ""
    if lab:
        extra += f'<p><a class="btn btn-ghost" href="{lab[0]}">{H.escape(lab[1])}</a></p>'
    if troubleshoot:
        extra += f'<p><a class="btn btn-ghost" href="{troubleshoot[0]}">{H.escape(troubleshoot[1])}</a></p>'
    body = f'''
<section class="hero flush">
 {badge(level)}
 <h1 class="display" style="font-size:clamp(1.9rem,5vw,2.8rem);margin-top:12px;">Course {num} — {H.escape(title)}</h1>
 <p class="lede">{blurb}</p>
</section>
{OSBAR}
<div class="cr-box"><h3>Lessons</h3><ul>{lis}</ul>{extra}</div>
<div class="cr-pager"><a href="/classroom/">← Academy</a><a href="{lessons[0][0]}">First lesson →</a></div>
'''
    write(COURSES / slug / "index.html", wrap(f"Course {num} — {title} · Classroom", blurb, f"/classroom/courses/{slug}/", f"COURSE {num}", body))


# ---------- Course 0 ----------
def gen_c0():
    slug = "00-fundamentals"
    course_index("0", slug, "Homelab Fundamentals", "baby",
        "Networking words, the picture of your LAN, Docker baby steps, and OS-specific install paths.",
        [
            ("what-we-build.html", "0.1 What are we building?"),
            ("network-diagram.html", "0.2 Network diagram"),
            ("windows.html", "0.3 Windows path (WSL2 + Docker)"),
            ("linux.html", "0.4 Linux path (Ubuntu + Docker)"),
            ("docker-verify.html", "0.5 Verify Docker (common)"),
        ],
        lab=("labs/lab-0.html", "Lab 0 — Prove Docker works"),
    )

    # 0.1
    meta = {
        "id": "0.1", "file": "what-we-build.html", "course_slug": slug, "course_title": "Course 0",
        "title": "What are we building?", "level": "baby",
        "learning": "The end state: automated media + local home automation + optional local voice — built in layers.",
        "prereqs": ["You opened Start here", "You glanced at the glossary"],
        "words": ["ARR", "Docker", "HA", "LAN"],
        "diagram": '''MEDIA LAYER          HOME LAYER
Prowlarr/Sonarr/Radarr   Home Assistant
qBit / SAB               Zigbee / ESPHome
Plex / Jellyfin          Assist / Voice
        \\               /
         \\             /
          YOUR HOMELAB SERVER''',
        "steps_html": step_block(1, "Say the goal out loud",
            "Write one sentence for your build. Example: “Docker on a small PC, ARR for TV/movies, Plex for playback, Home Assistant later.”",
            mean="If you cannot say the goal in one sentence, the project is still a fog. Clear the fog before installing apps.",
            more="Skip VLANs, reverse proxies, and custom wake words until Course 5–6."),
        "checkpoint_html": checkpoint("c0-01", [
            "I can describe my goal in one sentence",
            "I will not start with VLANs or reverse proxies today",
        ], "network-diagram.html", "Lesson 0.2"),
        "prev": ("/classroom/path.html", "Choose path"),
        "next": ("network-diagram.html", "0.2 Network diagram"),
    }
    write(COURSES / slug / meta["file"], lesson_page(meta))

    meta = {
        "id": "0.2", "file": "network-diagram.html", "course_slug": slug, "course_title": "Course 0",
        "title": "Network diagram", "level": "baby",
        "learning": "Your server lives on the LAN. Clients talk to it by IP or name. The internet (WAN) is outside the router.",
        "prereqs": ["Lesson 0.1 done"],
        "words": ["LAN", "WAN", "IP", "DNS", "Router"],
        "diagram": '''Internet (WAN)
      │
   ROUTER / FIREWALL
      │
   LAN switch / Wi‑Fi
      ├── Your laptop
      ├── Phone
      └── <span class="hi">HOMELAB SERVER</span>
             ├── Docker ARR stack
             └── (later) Home Assistant''',
        "steps_html": step_block(1, "Find your server IP",
            "On the server, note its LAN IP (example 192.168.50.20). You will open http://THAT-IP:PORT for each app.",
            windows="ipconfig\n# look for IPv4 under Ethernet/Wi‑Fi or inside WSL: hostname -I",
            linux="hostname -I\n# or: ip -4 addr",
            mean="An IP is the house number on your home street. Apps are doors (ports) on that house.",
            more="Prefer a DHCP reservation on the router so the server IP does not jump."),
        "checkpoint_html": checkpoint("c0-02", [
            "I know my server LAN IP",
            "I understand WAN is outside / LAN is inside",
        ], "windows.html", "Windows path (or skip to Linux)"),
        "prev": ("what-we-build.html", "0.1"),
        "next": ("windows.html", "0.3 Windows"),
    }
    # fix diagram - can't have html inside pre easily with span - use plain
    meta["diagram"] = '''Internet (WAN)
      |
   ROUTER / FIREWALL
      |
   LAN switch / Wi-Fi
      |-- Your laptop
      |-- Phone
      +-- HOMELAB SERVER  <--- Docker lives here
             |-- ARR stack
             +-- (later) Home Assistant'''
    write(COURSES / slug / meta["file"], lesson_page(meta))

    # windows
    body = f'''
<section class="hero flush"><div class="row">{badge("baby")}</div>
<h1 class="display" style="font-size:clamp(1.7rem,4vw,2.4rem);margin-top:10px;">0.3 Windows path — WSL2 + Docker</h1>
<p class="lede">We teach ARR on Windows through WSL2 Linux + Docker. That keeps paths and Compose close to the Linux course.</p></section>
{OSBAR}
<div class="cr-box"><h3>Action</h3>
<ol style="color:var(--cream-dim);">
<li>Install WSL2 with Ubuntu from Microsoft’s docs.</li>
<li>Install Docker Desktop with the WSL2 backend enabled (or Docker Engine inside WSL).</li>
<li>Open Ubuntu and confirm <span class="mono">docker version</span> works.</li>
<li>Create a project folder, e.g. <span class="mono">~/homelab</span> inside WSL (can live on <span class="mono">/mnt/d/...</span> if needed).</li>
</ol>
{mean_more("Windows runs a tiny Linux friend (WSL). Docker runs inside that friend so your homelab recipes match Linux servers.", "Avoid Hyper-V-only mental models for ARR. If Docker Desktop is cranky, Engine-in-WSL is a solid alternative.")}
</div>
{checkpoint("c0-win", [
  "WSL2 Ubuntu opens",
  "docker version works inside WSL",
  "I have a ~/homelab (or /mnt/d/homelab) folder",
], "docker-verify.html", "0.5 Verify Docker")}
<div class="cr-pager"><a href="network-diagram.html">← 0.2</a><a href="linux.html">Linux path →</a></div>
'''
    write(COURSES / slug / "windows.html", wrap("0.3 Windows path · Classroom", "WSL2 + Docker for ARR.", f"/classroom/courses/{slug}/windows.html", "0.3 WINDOWS", body))

    body = f'''
<section class="hero flush"><div class="row">{badge("baby")}</div>
<h1 class="display" style="font-size:clamp(1.7rem,4vw,2.4rem);margin-top:10px;">0.4 Linux path — Ubuntu / Debian + Docker</h1>
<p class="lede">Install Docker Engine from Docker’s official docs for your distro. Add your user to the docker group, log out/in, then verify.</p></section>
{OSBAR}
<div class="cr-box"><h3>Action</h3>
<pre class="cr-code">sudo apt update
# follow https://docs.docker.com/engine/install/ for your distro
sudo usermod -aG docker "$USER"
# log out and back in
mkdir -p ~/homelab && cd ~/homelab
docker version
docker compose version</pre>
{mean_more("Linux is the native home for Docker. Your user needs permission to talk to Docker without typing sudo every time.", "After usermod, a full logout/login (or reboot) is required before group membership applies.")}
</div>
{checkpoint("c0-lin", [
  "docker version works without sudo",
  "docker compose version works",
  "~/homelab exists",
], "docker-verify.html", "0.5 Verify Docker")}
<div class="cr-pager"><a href="windows.html">← Windows path</a><a href="docker-verify.html">0.5 →</a></div>
'''
    write(COURSES / slug / "linux.html", wrap("0.4 Linux path · Classroom", "Ubuntu/Debian Docker Engine setup.", f"/classroom/courses/{slug}/linux.html", "0.4 LINUX", body))

    meta = {
        "id": "0.5", "file": "docker-verify.html", "course_slug": slug, "course_title": "Course 0",
        "title": "Verify Docker (common)", "level": "baby",
        "learning": "Prove Docker can pull an image and run a container. This is the merge point for Windows and Linux paths.",
        "prereqs": ["Docker installed via Windows or Linux path", "~/homelab (or equivalent) exists"],
        "words": ["Docker", "Container", "Image"],
        "diagram": '''YOU
 |
 docker pull hello-world
 |
 docker run --rm hello-world
 |
 SUCCESS MESSAGE
 |
 join Course 1 (ARR)''',
        "steps_html": step_block(1, "Run hello-world",
            "From your homelab folder:",
            windows="cd ~/homelab   # inside WSL\ndocker run --rm hello-world",
            linux="cd ~/homelab\ndocker run --rm hello-world",
            mean="If hello-world prints a hello message, Docker can download blueprints and run them. That is the skill ARR needs.",
            more="If this fails: Docker service not running, permissions (Linux group), or Desktop WSL integration disabled."),
        "checkpoint_html": checkpoint("c0-05", [
            "hello-world ran successfully",
            "I know where my homelab folder is",
        ], "/classroom/courses/01-arr-stack/", "Course 1 — ARR Stack"),
        "prev": ("linux.html", "0.4 Linux"),
        "next": ("/classroom/courses/01-arr-stack/", "Course 1"),
    }
    write(COURSES / slug / meta["file"], lesson_page(meta))

    # Lab 0
    body = f'''
<section class="hero flush">{badge("baby")}<h1 class="display" style="font-size:clamp(1.7rem,4vw,2.4rem);margin-top:10px;">Lab 0 — Prove Docker works</h1>
<p class="lede">Evidence beats vibes.</p></section>
<div class="cr-box"><h3>Assignment</h3>
<p>Run hello-world and a Compose version check. Save screenshots or paste outputs into your notes.</p>
<div class="cr-lab-evidence">
<label><input type="checkbox"> Screenshot / paste: docker version</label>
<label><input type="checkbox"> Screenshot / paste: docker compose version</label>
<label><input type="checkbox"> Screenshot / paste: hello-world success</label>
</div>
</div>
<div class="cr-pager"><a href="../">← Course 0</a><a href="/classroom/courses/01-arr-stack/">Course 1 →</a></div>
'''
    write(COURSES / slug / "labs/lab-0.html", wrap("Lab 0 · Classroom", "Prove Docker works.", f"/classroom/courses/{slug}/labs/lab-0.html", "LAB 0", body))


# ---------- Course 1 ARR ----------
def gen_c1():
    slug = "01-arr-stack"
    course_index("1", slug, "Building the ARR Stack", "baby",
        "TRaSH order: storage → downloaders → Prowlarr → Sonarr/Radarr → Recyclarr. One concept per lesson.",
        [
            ("trash-order.html", "1.1 TRaSH order"),
            ("storage.html", "1.2 Create /data layout"),
            ("qbittorrent.html", "1.3 qBittorrent"),
            ("prowlarr.html", "1.4 Prowlarr"),
            ("sonarr.html", "1.5 Install Sonarr"),
            ("radarr.html", "1.6 Install Radarr"),
            ("recyclarr.html", "1.7 Recyclarr sync"),
        ],
        lab=("labs/lab-1.html", "ARR Lab 1 — One TV show end-to-end"),
        troubleshoot=("troubleshoot-sonarr-import.html", "Tree: Sonarr didn't import"),
    )

    lessons = []

    # 1.1
    lessons.append({
        "id": "1.1", "file": "trash-order.html", "title": "TRaSH order — not YouTube order", "level": "baby",
        "learning": "Build filesystem → downloader → ARR apps → media server. TRaSH Guides are the maintained source of truth.",
        "prereqs": ["Course 0 Lab complete", "Docker verified"],
        "words": ["TRaSH", "ARR", "Hardlink"],
        "diagram": '''1 FILESYSTEM (/data)
2 DOWNLOADER (qBit / SAB)
3 ARR APPS (Prowlarr → Sonarr/Radarr)
4 MEDIA SERVER (Plex / Jellyfin)''',
        "steps": [(1, "Open TRaSH Getting Started",
                   "Skim the Getting Started + File & Folder Structure pages. Do not install random stacks from a single video.",
                   "TRaSH is the school book. Videos are the movie trailer — useful, not the syllabus.",
                   "https://trash-guides.info/", None, None, None)],
        "check": ["I will follow filesystem → downloader → ARR → media server", "I bookmarked TRaSH Guides"],
        "next_file": "storage.html", "next_label": "1.2 Storage",
    })

    compose_data = '''services: {}
# We will add services lesson by lesson in this folder.
# Keep one compose project: ~/homelab/arr/docker-compose.yml'''

    lessons.append({
        "id": "1.2", "file": "storage.html", "title": "Create the /data layout", "level": "baby",
        "learning": "One parent tree for torrents, usenet, and media so hardlinks and atomic moves work.",
        "prereqs": ["Lesson 1.1", "Docker works"],
        "words": ["Bind mount", "Hardlink", "Volume"],
        "diagram": '''/data
├── torrents/{movies,tv,anime,music}
├── usenet/{incomplete,complete/...}
└── media/{movies,tv,anime,music}''',
        "steps": [
            (1, "Create folders on the host",
             "Create the tree on the machine that will run Docker. Put it on the disk that holds media.",
             "One closet for all boxes. Downloads and finished shows must share a filesystem parent.",
             "TRaSH warns against separate /downloads + /movies mounts that Docker treats as different filesystems.",
             "mkdir -p /data/{torrents/{movies,tv,anime,music},usenet/{incomplete,complete/{movies,tv,anime,music}},media/{movies,tv,anime,music}}\n# If you cannot use /data on Windows/WSL, use e.g. /mnt/d/data and stay consistent in Compose.",
             "sudo mkdir -p /data/{torrents/{movies,tv,anime,music},usenet/{incomplete,complete/{movies,tv,anime,music}},media/{movies,tv,anime,music}}\nsudo chown -R \"$USER:$USER\" /data",
             None),
            (2, "Start an ARR compose folder",
             "Create ~/homelab/arr for Compose files we fill in next lessons.",
             "This is the recipe binder for your media robots.",
             "One project keeps networks and mounts consistent.",
             "mkdir -p ~/homelab/arr && cd ~/homelab/arr",
             "mkdir -p ~/homelab/arr && cd ~/homelab/arr",
             compose_data),
        ],
        "check": ["/data (or your chosen parent) exists with torrents, usenet, media", "homelab/arr folder exists"],
        "next_file": "qbittorrent.html", "next_label": "1.3 qBittorrent",
    })

    qbit_compose = '''  gluetun:
    image: qmcgaw/gluetun
    # configure VPN_SERVICE_PROVIDER + private env file — see Gluetun wiki
    cap_add: [NET_ADMIN]
    ports:
      - "8080:8080"   # qBit UI published here
  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    network_mode: "service:gluetun"
    environment:
      - PUID=1000
      - PGID=1000
    volumes:
      - ./qbittorrent/config:/config
      - /data/torrents:/data/torrents
    # UI at http://SERVER-IP:8080 via Gluetun'''

    lessons.append({
        "id": "1.3", "file": "qbittorrent.html", "title": "qBittorrent (+ optional Gluetun)", "level": "mid",
        "learning": "Torrent client writes only under /data/torrents with categories. VPN wraps qBit — not the whole ARR stack.",
        "prereqs": ["/data/torrents exists", "Compose folder ready"],
        "words": ["qBittorrent", "Gluetun", "VPN", "Category"],
        "diagram": '''Internet → VPN Provider → Gluetun → qBittorrent
                                      │
                                      ▼
                              /data/torrents/...
ARR apps stay on normal LAN bridge''',
        "steps": [
            (1, "Add qBit to Compose (start without VPN if you need a baby step)",
             "Beginners may run qBit on the bridge network first. Intermediate: put qBit on Gluetun and publish ports on Gluetun.",
             "Only the download truck uses the secret tunnel. Librarians stay on the normal road.",
             "Gluetun can update qBit’s listen port when the VPN forwards one.",
             None, None, qbit_compose),
            (2, "Create categories",
             "In qBit: categories radarr, sonarr, anime, lidarr → save paths under /data/torrents/movies|tv|anime|music.",
             "Labeled mail slots so each librarian finds the right pile.",
             "Disable UPnP if you manually forward. Prefer a real forwarded port.",
             None, None, None),
        ],
        "check": ["qBit UI opens", "Categories point under /data/torrents", "I did not put Sonarr behind the VPN"],
        "next_file": "prowlarr.html", "next_label": "1.4 Prowlarr",
    })

    prowlarr_compose = '''  prowlarr:
    image: lscr.io/linuxserver/prowlarr:latest
    ports: ["9696:9696"]
    environment: [PUID=1000, PGID=1000]
    volumes: ["./prowlarr/config:/config"]'''

    lessons.append({
        "id": "1.4", "file": "prowlarr.html", "title": "Prowlarr — indexer hub", "level": "baby",
        "learning": "Add indexers once in Prowlarr; sync to Sonarr/Radarr later. Do not maintain duplicate indexer lists.",
        "prereqs": ["qBit reachable"],
        "words": ["Prowlarr", "Indexer", "API"],
        "diagram": '''PROWLARR
   │
   ├── Sonarr
   ├── Radarr
   └── Lidarr''',
        "steps": [
            (1, "Create the Prowlarr container", "Add service and start Compose.",
             "One phone book for search sources.", "Open http://SERVER-IP:9696",
             "cd ~/homelab/arr && docker compose up -d", "cd ~/homelab/arr && docker compose up -d", prowlarr_compose),
            (2, "Add one indexer", "Add a single indexer and note the API key for ARR apps.",
             "Start with one source so failures are easy to see.", "You will sync apps in the Sonarr/Radarr lessons.",
             None, None, None),
        ],
        "check": ["Prowlarr UI opens on :9696", "At least one indexer shows"],
        "next_file": "sonarr.html", "next_label": "1.5 Sonarr",
    })

    sonarr_compose = '''  sonarr:
    image: lscr.io/linuxserver/sonarr:latest
    ports: ["8989:8989"]
    environment: [PUID=1000, PGID=1000]
    volumes:
      - ./sonarr/config:/config
      - /data:/data'''

    lessons.append({
        "id": "1.5", "file": "sonarr.html", "title": "Install Sonarr", "level": "baby",
        "learning": "Sonarr monitors, downloads, renames, and organizes TV shows into /data/media/tv.",
        "prereqs": ["Docker installed", "/data created", "qBittorrent working", "Prowlarr installed"],
        "words": ["ARR", "Container", "Volume", "Port", "API"],
        "diagram": '''           SONARR
              |
     +--------+--------+
     |                 |
 PROWLARR         qBITTORRENT
 finds files        downloads
     |                 |
     +--------+--------+
              |
              v
        /data/media/tv
              |
              v
            PLEX''',
        "steps": [
            (1, "Open your terminal", "Go to the ARR project folder.",
             "Terminal is the text window where you type computer instructions.",
             "Keep using the same folder every lesson.",
             "cd ~/homelab/arr", "cd ~/homelab/arr", None),
            (2, "Create the Sonarr container", "Add Sonarr with /data mounted. Start it.",
             "Sonarr needs to see torrents and media under one /data tree.",
             "Mounting only /data/media is not enough for hardlinks from torrents.",
             "docker compose up -d", "docker compose up -d", sonarr_compose),
            (3, "Open Sonarr", "Visit the UI and set the root folder.",
             "Root folder = the shelf where finished shows live.",
             "Settings → Media Management → Root Folders → Add /data/media/tv",
             "http://YOUR-SERVER-IP:8989", "http://YOUR-SERVER-IP:8989", None),
            (4, "Connect download client + Prowlarr", "Add qBit (category sonarr) and Prowlarr sync/app connection. Click Test until green.",
             "Green tests mean the robots can phone each other.",
             "Use Prowlarr’s Apps screen to push indexers into Sonarr.",
             None, None, None),
        ],
        "check": [
            "Sonarr page opens",
            "/data/media/tv appears as a root folder",
            "qBittorrent appears under Download Clients (test green)",
            "Prowlarr appears under Indexers / Apps sync (test green)",
            "Test buttons are green",
        ],
        "next_file": "radarr.html", "next_label": "1.6 Radarr",
    })

    radarr_compose = '''  radarr:
    image: lscr.io/linuxserver/radarr:latest
    ports: ["7878:7878"]
    environment: [PUID=1000, PGID=1000]
    volumes:
      - ./radarr/config:/config
      - /data:/data'''

    lessons.append({
        "id": "1.6", "file": "radarr.html", "title": "Install Radarr", "level": "baby",
        "learning": "Radarr is Sonarr’s movie twin. Same /data mount pattern. Root folder /data/media/movies. Category radarr in qBit.",
        "prereqs": ["Sonarr checkpoint passed"],
        "words": ["Radarr", "Custom Format"],
        "diagram": '''RADARR → Prowlarr + qBit/SAB → /data/media/movies → Plex''',
        "steps": [
            (1, "Add Radarr service", "Mirror Sonarr mounts; open :7878.",
             "Same filing rules, movie shelves instead of TV shelves.",
             "Do not invent Custom Formats yet — Recyclarr comes next.",
             "docker compose up -d", "docker compose up -d", radarr_compose),
            (2, "Root folder + clients", "Add /data/media/movies; connect qBit category radarr; sync Prowlarr.",
             "Test buttons must be green before Lab 1.",
             "Optional: add SABnzbd later with /data/usenet paths.",
             None, None, None),
        ],
        "check": ["Radarr opens on :7878", "Root folder /data/media/movies set", "Download client + Prowlarr tests green"],
        "next_file": "recyclarr.html", "next_label": "1.7 Recyclarr",
    })

    lessons.append({
        "id": "1.7", "file": "recyclarr.html", "title": "Recyclarr syncs TRaSH profiles", "level": "mid",
        "learning": "Stop hand-scoring hundreds of Custom Formats. Git-controlled Recyclarr YAML syncs TRaSH into Sonarr/Radarr.",
        "prereqs": ["Sonarr + Radarr healthy"],
        "words": ["Recyclarr", "TRaSH", "Custom Format", "YAML"],
        "diagram": '''TRaSH Guides
     |
 Recyclarr YAML (git)
     |
 Sonarr + Radarr profiles''',
        "steps": [
            (1, "Create a Recyclarr config", "Follow Recyclarr docs for Sonarr/Radarr instances and pick starter profiles (e.g. WEB-1080p).",
             "Recyclarr is the robot that updates grading rubrics for you.",
             "Anime needs its own TRaSH Sonarr anime profile — do not merge blindly.",
             None, None, None),
            (2, "Run a sync", "Execute recyclarr sync and confirm Custom Formats appeared in ARR.",
             "One sync beats a night of clicking.",
             "Schedule sync later with cron/systemd.",
             None, None, None),
        ],
        "check": ["Recyclarr ran without errors", "At least one TRaSH quality profile visible in Sonarr or Radarr"],
        "next_file": "labs/lab-1.html", "next_label": "ARR Lab 1",
    })

    for i, L in enumerate(lessons):
        steps_html = []
        for s in L["steps"]:
            n, title, body, mean, more, win, lin, code = s
            steps_html.append(step_block(n, title, body, mean=mean, more=more, windows=win, linux=lin, common_code=code))
        prev = (lessons[i-1]["file"], lessons[i-1]["id"]) if i else ("/classroom/courses/00-fundamentals/", "Course 0")
        nxt = (L["next_file"], L["next_label"])
        meta = {
            "id": L["id"], "file": L["file"], "course_slug": slug, "course_title": "Course 1",
            "title": L["title"], "level": L["level"], "learning": L["learning"],
            "prereqs": L["prereqs"], "words": L["words"], "diagram": L["diagram"],
            "steps_html": "\n".join(steps_html),
            "checkpoint_html": checkpoint(f"c1-{L['id']}", L["check"], L["next_file"], L["next_label"]),
            "prev": (prev[0] if prev[0].startswith("/") else prev[0], f"{prev[1]}" if i else prev[1]),
            "next": nxt,
        }
        if i:
            meta["prev"] = (lessons[i-1]["file"], f"{lessons[i-1]['id']} {lessons[i-1]['title']}")
        write(COURSES / slug / L["file"], lesson_page(meta))

    # Lab 1
    body = f'''
<section class="hero flush">{badge("baby")}<h1 class="display" style="font-size:clamp(1.7rem,4vw,2.4rem);margin-top:10px;">ARR Lab 1 — One TV show end-to-end</h1>
<p class="lede">Add one show. Prove the chain. Collect evidence.</p></section>
{OSBAR}
<div class="cr-box"><h3>Assignment</h3>
<p>Add one television show to Sonarr and prove: Sonarr finds it → qBittorrent downloads → Sonarr imports/renames → file lands under <span class="mono">/data/media/tv/...</span> → Plex/Jellyfin can see it (library scan).</p>
</div>
<div class="cr-box"><h3>Evidence checklist</h3>
<div class="cr-lab-evidence">
<label><input type="checkbox"> Sonarr screenshot (show added / activity)</label>
<label><input type="checkbox"> qBit screenshot (torrent in sonarr category)</label>
<label><input type="checkbox"> Filesystem path of the imported episode</label>
<label><input type="checkbox"> Plex/Jellyfin screenshot (episode visible)</label>
</div>
</div>
<div class="cr-callout">If import fails, open the <a href="../troubleshoot-sonarr-import.html">Sonarr didn't import</a> decision tree before changing random settings.</div>
<div class="cr-pager"><a href="../sonarr.html">← Sonarr lesson</a><a href="/classroom/courses/02-perfecting-arr/">Course 2 →</a></div>
'''
    write(COURSES / slug / "labs/lab-1.html", wrap("ARR Lab 1 · Classroom", "End-to-end TV show proof.", f"/classroom/courses/{slug}/labs/lab-1.html", "LAB 1", body))

    # troubleshooting tree
    body = f'''
<section class="hero flush">{badge("mid")}<h1 class="display" style="font-size:clamp(1.7rem,4vw,2.4rem);margin-top:10px;">Troubleshooting — Sonarr didn't import</h1>
<p class="lede">Follow the tree. Change one thing at a time.</p></section>
<div class="cr-tree">
 <div class="node q">SONARR DIDN'T IMPORT — Can Sonarr see the download?</div>
 <div class="branch">
  <div class="node bad"><strong>NO</strong><br>Check Docker mounts: Sonarr needs /data (torrents + media). Restart container after fixes.</div>
  <div class="node ok"><strong>YES</strong><br>Does the completed path match the category save path?</div>
 </div>
 <div class="branch">
  <div class="node bad"><strong>Path mismatch</strong><br>Fix qBit category path and Sonarr remote path maps if used.</div>
  <div class="node ok"><strong>Paths match</strong><br>Check permissions (PUID/PGID) and hardlink test on same filesystem.</div>
 </div>
 <div class="node">Still stuck? Permissions → then quality profile rejected the release → then check Activity / Queue errors word for word.</div>
</div>
{mean_more("The robot either cannot see the file, sees it in the wrong place, or is not allowed to touch it. We test those ideas in order.", "Hardlink failure often means torrents and media are on different filesystems/mounts — return to Lesson 1.2.")}
<div class="cr-pager"><a href="labs/lab-1.html">← Lab 1</a><a href="/classroom/courses/02-perfecting-arr/">Course 2 →</a></div>
'''
    write(COURSES / slug / "troubleshoot-sonarr-import.html", wrap("Sonarr import tree · Classroom", "Decision tree for failed imports.", f"/classroom/courses/{slug}/troubleshoot-sonarr-import.html", "TROUBLESHOOT", body))


def scaffold(num, slug, title, level, blurb, units, diagram, tip):
    course_index(num, slug, title, level, blurb, [("index.html#units", u) for u in units])
    # overwrite with richer scaffold body
    units_html = ''.join(f'<li>{H.escape(u)}</li>' for u in units)
    body = f'''
<section class="hero flush">{badge(level)}
<h1 class="display" style="font-size:clamp(1.9rem,5vw,2.8rem);margin-top:12px;">Course {num} — {H.escape(title)}</h1>
<p class="lede">{blurb}</p></section>
<pre class="cr-diagram">{diagram}</pre>
<div class="cr-box"><h3>Units in this course</h3><ul>{units_html}</ul>
<p style="margin-top:12px;color:var(--cream-dim);">Full classroom lessons (one concept → picture → action → checkpoint) expand here next — structure is locked so Course 0–1 stay the on-ramp.</p>
</div>
<div class="cr-callout tip">{tip}</div>
<div class="cr-pager"><a href="/classroom/">← Academy</a><a href="/classroom/glossary.html">Glossary →</a></div>
'''
    write(COURSES / slug / "index.html", wrap(f"Course {num} — {title} · Classroom", blurb, f"/classroom/courses/{slug}/", f"COURSE {num}", body))


def gen_scaffolds():
    scaffold("2", "02-perfecting-arr", "Perfecting the ARR Stack", "mid",
             "Hardlinks proofs, Custom Formats mastery, anime split, Maintainerr, cross-seed, qbit_manage.",
             ["Hardlink verification lab", "Anime profile isolation", "Maintainerr cleanup rules", "cross-seed + qbit_manage"],
             "CORE ARR HEALTHY\n    |\n    +-- prove hardlinks\n    +-- Recyclarr profiles deeper\n    +-- anime != TV\n    +-- library automation tools",
             "<strong>Rule:</strong> do not open Course 2 until ARR Lab 1 evidence exists.")
    scaffold("3", "03-plex-jellyfin", "Plex / Jellyfin", "mid",
             "Libraries on /data/media only. Direct Play vs Direct Stream vs Transcode.",
             ["Library roots", "Direct Play diagnostics", "Hardware encode", "Remote access without Relay abuse"],
             "CLIENT\n  |-- Direct Play (best)\n  |-- Direct Stream\n  +-- Transcode (find WHY first)",
             "Mount <span class='mono'>/data/media</span> only into the media server.")
    scaffold("4", "04-ha-fundamentals", "Home Assistant Fundamentals", "baby",
             "HA 101 → 201: devices through automations. Backups before fancy.",
             ["HA OS install", "Devices / entities / areas", "Helpers & dashboards", "Automations: trigger → condition → action", "Lab: motion after sunset → lamp 5 minutes"],
             "HA 101: Devices → Entities → Areas → Integrations → Helpers → Dashboards\nHA 201: Triggers → Conditions → Actions → Scripts → Scenes → Blueprints",
             "Turn on automatic backups before deep customization.")
    scaffold("5", "05-ha-advanced", "Home Assistant Advanced", "mid",
             "Zigbee mesh, ESPHome, MQTT, Matter/Thread — including Kwikset Thread border-router tip.",
             ["ESPHome first sensor", "Zigbee coordinator + routers", "MQTT when needed", "Matter/Thread + Kwikset BR tip", "Network isolation (advanced)"],
             "Coordinator\n  +-- mains routers (plugs)\n        +-- battery end devices",
             "<strong>Kwikset / Thread:</strong> many locks need a Thread border router on the LAN. HA seeing Wi-Fi alone is not enough for Thread-only pairing.")
    scaffold("6", "06-local-voice", "Local Voice", "mid",
             "Assist pipeline, Wyoming STT/TTS, Linux Voice Assistant satellites (not archived wyoming-satellite).",
             ["Assist overview", "Whisper + Piper via Wyoming", "Wake word validation layers", "Linux Voice Assistant on Pi", "Voice lab: turn on office light"],
             "Mic → Wake → STT(Whisper) → HA Assist → Intent/LLM → TTS(Piper) → Speaker",
             "wyoming-satellite is archived (2026-01-27). New path: Linux Voice Assistant / ESPHome protocol; Wyoming remains for Whisper/Piper.")
    # voice troubleshoot mini page
    body = f'''
<section class="hero flush">{badge("mid")}<h1 class="display" style="font-size:clamp(1.7rem,4vw,2.4rem);margin-top:10px;">Tree — Voice doesn't work</h1></section>
<div class="cr-tree">
 <div class="node q">VOICE DOESN'T WORK — Wake word detected?</div>
 <div class="branch">
  <div class="node bad"><strong>NO</strong><br>Mic / wake-word service / satellite audio path</div>
  <div class="node ok"><strong>YES</strong><br>STT returns text?</div>
 </div>
 <div class="branch">
  <div class="node bad"><strong>NO</strong><br>Whisper/Wyoming audio quality</div>
  <div class="node ok"><strong>YES</strong><br>HA intent correct? → then TTS/Piper/speaker</div>
 </div>
</div>
<p class="intro">Validate one layer at a time. Never debug custom wake word + mic + Whisper + intent + Piper together on day one.</p>
<div class="cr-pager"><a href="./">← Course 6</a><a href="/classroom/glossary.html">Glossary →</a></div>
'''
    write(COURSES / "06-local-voice" / "troubleshoot-voice.html", wrap("Voice tree · Classroom", "Voice troubleshooting decision tree.", "/classroom/courses/06-local-voice/troubleshoot-voice.html", "VOICE TREE", body))

    scaffold("7", "07-ultimate", "Ultimate Homelab", "adv",
             "VLANs, VPNs, reverse proxies, monitoring, backups, GPUs, local AI, high availability. Capstone project.",
             ["VLAN segmentation", "Remote access (Tailscale)", "Reverse proxy", "Backups & restore drill", "GPU for Whisper/Plex", "Capstone: request→ARR→Plex→HA monitor→local voice status"],
             "CAPSTONE\nRequest movie → ARR acquires → Plex publishes\nHA monitors infra → local voice reports status\n(no cloud AI required)",
             "🔴 Do not start here. Finish Labs 0 and 1 first.")


def mirror_github():
    # copy generated HTML text summaries into docs as markdown outlines
    readme = '''# Otaconskeep Classroom — Homelab Academy

Self-paced technical course (not a wiki dump).

**Canonical site:** https://otaconskeep.github.io/classroom/

## How lessons work

1. What you are learning  
2. Prerequisites  
3. New words (link to glossary)  
4. One picture  
5. Steps (Windows / Linux where needed)  
6. Checkpoint checkboxes — only then continue  
7. Labs + troubleshooting trees  

## Courses

0. Homelab Fundamentals  
1. Building the ARR Stack  
2. Perfecting the ARR Stack  
3. Plex / Jellyfin  
4. Home Assistant Fundamentals  
5. Home Assistant Advanced (Zigbee / ESPHome / Matter / Thread / Kwikset tip)  
6. Local Voice (Wyoming + Linux Voice Assistant)  
7. Ultimate Homelab + Capstone  

## Path fork

Windows → WSL2 + Docker  
Linux → Ubuntu/Debian + Docker  
Then merge into the common Docker → Storage → ARR → HA → Voice track.

## Glossary

Plain-language acronyms live on the site: [/classroom/glossary.html](https://otaconskeep.github.io/classroom/glossary.html)

## License

MIT — Antonio G. Garcia (Otaconskeep)
'''
    (GH / "README.md").write_text(readme)
    (DOCS / "COURSES.md").write_text("See site curriculum. HTML lessons are the source of truth for checkpoints and OS tabs.\n")
    print("github mirrored readme")


def main():
    gen_hub()
    gen_start()
    gen_path()
    gen_glossary()
    gen_c0()
    gen_c1()
    gen_scaffolds()
    mirror_github()
    print("DONE")


if __name__ == "__main__":
    main()

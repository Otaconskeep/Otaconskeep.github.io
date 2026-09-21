#!/usr/bin/env python3
"""Homelab Academy curriculum: Units 1-4, Classes 1-13. No video embeds."""
from __future__ import annotations
from pathlib import Path
import html as H

SITE = Path("/root/otaconskeep-site/classroom")
UNITS = SITE / "units"
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
 <a href="/classroom/start.html">Start</a>
 <a href="/classroom/path.html">Path</a>
 <a href="/classroom/glossary.html">Glossary</a>
 <a href="/classroom/units/1-infrastructure/">Unit 1</a>
 <a href="/classroom/units/2-arr/">Unit 2</a>
 <a href="/classroom/units/3-home-assistant/">Unit 3</a>
 <a href="/classroom/units/4-voice/">Unit 4</a>
 <a href="/classroom/final-exam.html">Final exam</a>
 </div>
</nav>'''

FOOT = '''<footer class="sitefoot"><div class="wrap">
<span>Otaconskeep Classroom · Homelab Academy</span>
<span><a href="https://github.com/Otaconskeep/Classroom">GitHub</a> · <a href="/classroom/glossary.html">Glossary</a></span>
</div></footer>
<script src="/classroom/classroom.js?v=20260921c"></script>'''

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
<link rel="stylesheet" href="/classroom/classroom.css?v=20260921c">
</head>
<body>
<div class="filebar"><div class="wrap"><span>CLASSROOM // HOMELAB ACADEMY</span><span>{bar}<span class="blink"></span></span></div></div>
{nav}{sub}
'''

OSBAR = '''<div class="cr-osbar" role="group" aria-label="Show instructions for">
 <span>Show steps for:</span>
 <button type="button" class="win" data-os="windows">Windows (WSL2 + Docker)</button>
 <button type="button" class="lin" data-os="linux">Linux (Ubuntu/Debian + Docker)</button>
 <a href="/classroom/path.html" style="margin-left:auto;font-size:.85rem;">Change path</a>
</div>'''

LEVEL = {
  "baby": ('baby', '🟢 Baby step'),
  "mid": ('mid', '🟡 Intermediate'),
  "adv": ('adv', '🔴 Advanced'),
}


def wrap(title, desc, canon, bar, body):
    return HEAD.format(title=H.escape(title), desc=H.escape(desc), canon=canon, bar=H.escape(bar), nav=NAV, sub=SUB) + f'<div class="wrap">{body}</div>\n{FOOT}\n</body></html>\n'


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print("wrote", path.relative_to(SITE))


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


def checkpoint(cid, items, next_href, next_label):
    boxes = ''.join(f'<label><input type="checkbox" data-k="{i}"> {H.escape(t)}</label>' for i, t in enumerate(items))
    return f'''<div class="cr-check" data-check-id="{cid}">
 <h3>Checkpoint — pass before you continue</h3>
 {boxes}
 <div class="cr-gate">All boxes true → <a href="{next_href}">{H.escape(next_label)}</a></div>
</div>'''


def page_block(n, title, inner):
    return f'''<div class="cr-box" id="page-{n}"><h3>Workbook page {n} — {H.escape(title)}</h3>{inner}</div>'''


def class_page(c):
    """c: id, unit, unit_slug, title, level, goal, lecture_note, words, diagram, notes, lab_steps, breakfix, check, prev, next, current_docs"""
    words = ''.join(
        f'<a href="/classroom/glossary.html#{H.escape(w.lower().replace(" ","-"))}">{H.escape(w)}</a>'
        for w in c["words"]
    )
    docs = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{H.escape(t)}</a></li>' for t, u in c.get("docs", []))
    body = f'''
<section class="hero flush">
 <div class="row" style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:10px;">
  {badge(c["level"])}
  <span class="tag" style="margin:0">{H.escape(c["unit"])} · Class {H.escape(c["id"])}</span>
 </div>
 <h1 class="display" style="font-size:clamp(1.6rem,4.5vw,2.5rem);">{H.escape(c["title"])}</h1>
 <p class="lede">{c["goal"]}</p>
 <div class="cr-callout tip"><strong>Lecture pairing:</strong> {c["lecture_note"]} <em>We do not embed the video here</em> — concepts are built into this workbook. Prefer current official docs for commands and UI.</div>
</section>
{OSBAR}
{page_block(1, "What you're going to learn", f"<p>{c['goal']}</p>{mean_more(c.get('mean_goal',''), c.get('more_goal',''))}")}
{page_block(2, "Acronyms & vocabulary", f'<div class="cr-words">{words}</div><p style="margin-top:10px;color:var(--cream-dim);">Jump to the <a href="/classroom/glossary.html">full glossary</a> anytime.</p>')}
{page_block(3, "Architecture picture", f'<pre class="cr-diagram">{c["diagram"]}</pre>')}
{page_block(4, "Guided notes (from the lecture ideas)", c["notes"])}
{page_block(5, "Windows / Linux baby-step lab", c["lab"])}
{page_block(6, "Break → fix → verify", c["breakfix"] + checkpoint(f"class-{c['id']}", c["check"], c["next"][0], c["next"][1]))}
<div class="cr-refs" style="margin:18px 0;padding:16px;border:1px dashed var(--line-bright);border-radius:6px;">
 <h3 style="font-family:'JetBrains Mono',monospace;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--cream-faint);">Current docs (prefer these over old UI screens)</h3>
 <ul style="color:var(--cream-dim);">{docs}</ul>
</div>
<div class="cr-pager">
 <a href="{c['prev'][0]}">← {H.escape(c['prev'][1])}</a>
 <a href="{c['next'][0]}">{H.escape(c['next'][1])} →</a>
</div>'''
    return wrap(
        f"Class {c['id']} — {c['title']} · Classroom",
        c["goal"][:160],
        f"/classroom/units/{c['unit_slug']}/classes/{c['file']}",
        f"CLASS {c['id']}",
        body,
    )


def unit_index(num, slug, title, blurb, classes, next_unit):
    lis = ''.join(f'<li><a href="classes/{fn}">{H.escape(label)}</a></li>' for fn, label in classes)
    first = classes[0][0]
    body = f'''
<section class="hero flush">
 <p class="tag">Unit {num}</p>
 <h1 class="display" style="font-size:clamp(1.9rem,5vw,2.8rem);">{H.escape(title)}</h1>
 <p class="lede">{blurb}</p>
</section>
<div class="cr-box"><h3>Classes in this unit</h3><ol>{lis}</ol></div>
<div class="cr-callout tip">Pattern every class: <strong>Understand → Build → Break → Fix → Verify</strong>. Videos are lectures only — this site holds the labs and checkpoints. No videos are embedded.</div>
<div class="cr-pager"><a href="/classroom/">← Academy</a><a href="classes/{first}">First class →</a></div>
'''
    write(UNITS / slug / "index.html", wrap(f"Unit {num} — {title} · Classroom", blurb, f"/classroom/units/{slug}/", f"UNIT {num}", body))


# ===================== CLASSES =====================

CLASSES = []

# --- Class 1 ---
CLASSES.append(dict(
    id="1", file="01-virtualization.html", unit="Unit 1 — Infrastructure & Docker", unit_slug="1-infrastructure",
    title="What virtualization actually is", level="baby",
    goal="Understand physical host vs VM vs container, and why Home Assistant OS often lives in a VM while Sonarr usually lives in Docker.",
    lecture_note="Concept lecture: NetworkChuck Proxmox / Type-1 hypervisor material (older UI — learn the ideas, not every click).",
    mean_goal="A big computer can pretend to be several smaller computers. A container is a lightweight packaged app. A VM is a whole fake PC.",
    more_goal="Type-1 hypervisor sits on bare metal. VMs get full guest OS. LXC/containers share the host kernel. HA OS likes appliance VMs; ARR likes Compose containers.",
    words=["Hypervisor", "VM", "LXC", "ISO", "Host", "Guest", "Bridge", "Docker"],
    diagram='''PHYSICAL SERVER
      |
      v
   PROXMOX (or Hyper-V / just Docker host)
      |
 +----+----------+
 v    v          v
HA OS Ubuntu    Docker / LXC
 VM    VM       containers
                 |
            Sonarr / Radarr ...''',
    notes='''<ul>
<li><strong>Host</strong> = the real machine. <strong>Guest</strong> = a VM running on it.</li>
<li><strong>Bridge</strong> networking lets VMs look like devices on your LAN.</li>
<li>Windows students: learn the concept; practice with Hyper-V or skip to Docker on WSL2.</li>
<li>Linux/homelab students: optional spare-box Proxmox install — not required to finish Unit 1.</li>
<li><strong>Exit question:</strong> Why HA OS as a VM, Sonarr as Docker?</li>
</ul>
''' + mean_more("HA OS wants to feel like an appliance with add-ons. Sonarr is just an app — containers fit better.", "Common pattern: Proxmox host → HA OS VM + Ubuntu VM for Docker ARR stack."),
    lab='''<p>Pick one track:</p>
<div class="cr-os-block" data-os="windows"><span class="cr-os-label win">Windows</span>
<pre class="cr-code"># Baby step: you do NOT need Proxmox on your daily PC.
# Option A: enable WSL2 Ubuntu (Course path) and treat that as your "guest Linux".
# Option B (optional): create a disposable Hyper-V Ubuntu VM, note its IP, SSH in.
wsl -l -v
hostname -I   # inside WSL</pre></div>
<div class="cr-os-block" data-os="linux"><span class="cr-os-label lin">Linux</span>
<pre class="cr-code"># Baby step without Proxmox: verify this machine can be a Docker host.
hostname -I
ping -c 2 1.1.1.1
# Optional advanced: install Proxmox on spare hardware later — not required for Class 2.</pre></div>
''' + mean_more("Today’s lab proves you can reach a Linux environment and know its IP. Proxmox is optional hardware homework.", "If you already run Proxmox: create one disposable Ubuntu VM, boot it, find IP, SSH, confirm green status."),
    breakfix='''<div class="cr-tree">
 <div class="node q">Cannot SSH to the guest?</div>
 <div class="branch">
  <div class="node bad"><strong>No ping</strong><br>Check bridge/LAN, guest powered on, wrong IP</div>
  <div class="node ok"><strong>Ping works</strong><br>SSH service / firewall / username</div>
 </div>
</div>''',
    check=["I can explain host vs guest vs container", "I have a Linux shell (WSL or native) with a known IP", "I answered: HA OS→VM appliance, Sonarr→Docker app"],
    docs=[("Proxmox VE docs", "https://pve.proxmox.com/pve-docs/"), ("Docker overview", "https://docs.docker.com/get-started/")],
    prev=("/classroom/path.html", "Choose path"), next=("02-compose.html", "Class 2"),
))

# --- Class 2 ---
CLASSES.append(dict(
    id="2", file="02-compose.html", unit="Unit 1 — Infrastructure & Docker", unit_slug="1-infrastructure",
    title="Docker Compose from zero", level="baby",
    goal="Stop thinking in one-off docker run commands. Learn Compose so ARR is reproducible.",
    lecture_note="Concept lecture: NetworkChuck Docker Compose (2022-era UI — use current Compose V2 docs for commands).",
    mean_goal="Compose is a recipe card that starts many apps together.",
    more_goal="Images are blueprints; containers are running copies; volumes/bind mounts keep data after delete.",
    words=["Docker", "Container", "Image", "Compose", "YAML", "Volume", "Environment variable"],
    diagram='''compose.yaml
    |
    +-- Sonarr
    +-- Radarr
    +-- Prowlarr
    +-- qBittorrent

docker compose up -d
docker compose ps
docker compose logs
docker compose down''',
    notes='''<ul>
<li>Lesson mantra: <strong>Containers are disposable. Data and configuration are not.</strong></li>
<li>Lab progression: one container → convert to Compose → destroy/recreate → prove data survives.</li>
<li>After this class, Windows and Linux merge into the same Compose workflow.</li>
</ul>''' + mean_more("If you delete a container and your settings vanish, you stored data inside the disposable box. Put settings on a volume/bind mount.", "Use Compose V2: <span class='mono'>docker compose</span> (space), not only legacy docker-compose."),
    lab='''<div class="cr-os-block" data-os="windows"><span class="cr-os-label win">Windows (WSL)</span>
<pre class="cr-code">mkdir -p ~/homelab/unit1 && cd ~/homelab/unit1
# Lab 1: run hello-world
docker run --rm hello-world
# Lab 2: create compose.yaml with a tiny service (e.g. nginx) + a named volume or bind mount
# Lab 3: docker compose up -d && docker compose down && up again — prove mount survived</pre></div>
<div class="cr-os-block" data-os="linux"><span class="cr-os-label lin">Linux</span>
<pre class="cr-code">mkdir -p /opt/homelab/unit1 && cd /opt/homelab/unit1
docker run --rm hello-world
# Same Labs 2–3 with compose.yaml under /opt/homelab</pre></div>
<p>Homework: write three sentences — image vs container vs volume.</p>''',
    breakfix='''<div class="cr-tree">
 <div class="node q">Data gone after compose down/up?</div>
 <div class="branch">
  <div class="node bad">Wrote into container filesystem</div>
  <div class="node ok">Fix bind mount / named volume; recreate; retest</div>
 </div>
</div>''',
    check=["hello-world succeeds", "A Compose file starts a service", "Data survives destroy/recreate", "I can explain image vs container vs volume"],
    docs=[("Compose how-to", "https://docs.docker.com/compose/"), ("Compose file reference", "https://docs.docker.com/reference/compose-file/")],
    prev=("01-virtualization.html", "Class 1"), next=("03-networking.html", "Class 3"),
))

# --- Class 3 ---
CLASSES.append(dict(
    id="3", file="03-networking.html", unit="Unit 1 — Infrastructure & Docker", unit_slug="1-infrastructure",
    title="Docker networking", level="mid",
    goal="Understand how containers find each other — and the difference between localhost, LAN IP, published ports, and container DNS names.",
    lecture_note="Concept lecture: NetworkChuck Docker networking (2022). Pair with current Docker network docs; skip copying obsolete MACVLAN steps unless you need them.",
    mean_goal="Apps on the same private Docker street can call each other by name. Your phone usually uses the house number (LAN IP) plus a door (port).",
    more_goal="bridge vs user-defined bridge vs host vs macvlan/ipvlan — start with a user-defined bridge for ARR.",
    words=["Bridge", "Subnet", "Gateway", "DNS", "Port", "VLAN", "LAN"],
    diagram='''HOME LAN  192.168.x.0/24
      |
 Docker Host  (e.g. 192.168.x.20)
      |
 media_network  172.20.0.0/16
      |
 +----+----------+
 |    |          |
Sonarr Radarr  Prowlarr

Reachability cheat sheet:
  localhost:9696        only on the host
  192.168.x.20:9696     from another LAN device
  prowlarr:9696         container-to-container on media_network''',
    notes='''<ul>
<li>Create <span class="mono">media_network</span>; attach Sonarr + Prowlarr.</li>
<li>Experiment: curl/wget from Sonarr container to <span class="mono">http://prowlarr:9696</span>.</li>
<li>Break/fix: disconnect Prowlarr from the network and diagnose.</li>
</ul>''' + mean_more("Same Docker network = same private hallway. Container names are room signs.", "Publishing <span class='mono'>9696:9696</span> opens a door from the LAN into that hallway."),
    lab='''<pre class="cr-code">docker network create media_network
# In compose: networks: [media_network] on prowlarr + sonarr
# From host: curl -I http://127.0.0.1:9696
# From another container on media_network: wget -qO- http://prowlarr:9696 | head</pre>
''' + mean_more("If container-name DNS fails, they are not on the same user-defined network.", "Do not put the whole stack on host networking 'to make it easy' — that hides useful failures."),
    breakfix='''<div class="cr-tree">
 <div class="node q">Sonarr cannot reach Prowlarr by name?</div>
 <div class="branch">
  <div class="node bad">Different networks / typo service name</div>
  <div class="node ok">Same media_network + service name == DNS name</div>
 </div>
</div>''',
    check=["I created media_network", "Two services share it", "I can explain localhost vs LAN IP vs container name", "I broke and fixed name DNS once"],
    docs=[("Docker networking", "https://docs.docker.com/engine/network/")],
    prev=("02-compose.html", "Class 2"), next=("04-docker-playground.html", "Class 4"),
))

# --- Class 4 ---
CLASSES.append(dict(
    id="4", file="04-docker-playground.html", unit="Unit 1 — Infrastructure & Docker", unit_slug="1-infrastructure",
    title="Docker beyond the basics (playground)", level="mid",
    goal="Treat containers as disposable labs: isolation, ports, volumes, networks, Compose reproduce, inspect privileges.",
    lecture_note="Mindset lecture: NetworkChuck 'weird Docker uses' — pick a few exercises, not all 18.",
    mean_goal="Try apps without installing them forever. Keep the data you care about outside the container.",
    more_goal="Inspect mounts and capabilities before you trust a random image.",
    words=["Container", "Port", "Volume", "Bind mount", "Compose"],
    diagram='''TRY APP IN CONTAINER
        |
   change published port
        |
   attach volume
        |
   attach custom network
        |
   write compose.yaml
        |
   inspect privileges/mounts''',
    notes='''<p>Student exercises (pick ≥4): isolation · change exposed port · persist something · custom network · reproduce via YAML · inspect privileges.</p>'''
    + mean_more("You are practicing control, not collecting containers.", "Unit 1 exit: you are ready for ARR only if Compose + network + volume habits are boring."),
    lab='''<pre class="cr-code"># Example playground: run a throwaway web app, map host 8088→80, mount a folder, join media_network, then express it in compose.yaml
# Finish by: docker inspect ... | less   and list Mounts + CapAdd</pre>''',
    breakfix='''<div class="cr-callout">If an image asks for <span class="mono">/var/run/docker.sock</span> or <span class="mono">privileged: true</span>, stop and ask why before Class 5.</div>''',
    check=["I changed a published port on purpose", "I persisted data with a mount", "I wrote Compose for one playground app", "I inspected mounts/privileges once"],
    docs=[("docker run reference", "https://docs.docker.com/reference/cli/docker/container/run/")],
    prev=("03-networking.html", "Class 3"), next=("/classroom/units/2-arr/", "Unit 2"),
))

# --- Class 5 ---
CLASSES.append(dict(
    id="5", file="05-prowlarr.html", unit="Unit 2 — ARR Media Automation", unit_slug="2-arr",
    title="What Prowlarr actually does", level="baby",
    goal="Use Prowlarr as the indexer hub. Start with ONE indexer, sync to Sonarr, verify.",
    lecture_note="Concept lecture: IBRACORP Prowlarr (2021). UI changed — follow current Servarr/Prowlarr docs for clicks.",
    mean_goal="Prowlarr is the shared phone book of search sites. Sonarr/Radarr borrow it instead of each keeping a messy copy.",
    more_goal="API keys connect apps. Sync pushes indexer config into ARR applications.",
    words=["Prowlarr", "Indexer", "Tracker", "Usenet", "Torrent", "API", "Sync"],
    diagram='''              PROWLARR
                 |
        INDEXER MANAGEMENT
                 |
        +--------+--------+
        v        v        v
     SONARR   RADARR   LIDARR''',
    notes='''<ol>
<li>Add <strong>one</strong> indexer</li>
<li>Test it</li>
<li>Connect Sonarr (Apps)</li>
<li>Sync</li>
<li>Verify indexer appears in Sonarr</li>
</ol>
<p>Checkpoint equation: Prowlarr works + Sonarr works + API connection works = PASS.</p>''',
    lab='''<pre class="cr-code"># In compose: linuxserver/prowlarr on media_network, publish 9696
# Open http://SERVER-IP:9696
# Add 1 indexer → Test → Settings/Apps → Sonarr → Sync
# Confirm indexer list in Sonarr</pre>
''' + mean_more("One indexer keeps failures obvious.", "Do not add fifty indexers on day one."),
    breakfix='''<div class="cr-tree">
 <div class="node q">Sonarr never sees the indexer?</div>
 <div class="branch">
  <div class="node bad">Wrong API key / Sonarr URL (use http://sonarr:8989 on Docker DNS)</div>
  <div class="node ok">Re-sync from Prowlarr Apps; confirm Test green</div>
 </div>
</div>''',
    check=["Prowlarr UI opens", "One indexer tests OK", "Sonarr connected via API", "Indexer visible in Sonarr"],
    docs=[("Prowlarr wiki", "https://wiki.servarr.com/prowlarr"), ("TRaSH Prowlarr", "https://trash-guides.info/Prowlarr/")],
    prev=("/classroom/units/1-infrastructure/classes/04-docker-playground.html", "Class 4"), next=("06-trash-fundamentals.html", "Class 6"),
))

# --- Class 6 ---
CLASSES.append(dict(
    id="6", file="06-trash-fundamentals.html", unit="Unit 2 — ARR Media Automation", unit_slug="2-arr",
    title="TRaSH Guides fundamentals", level="mid",
    goal="Learn Quality + Custom Formats + Scoring + Profiles — by grading fake releases, not by blind clicking.",
    lecture_note="Concept lecture: IBRACORP TRaSH/Custom Formats material. Scoring tables change — always pull current TRaSH definitions.",
    mean_goal="You write a grading rubric. Radarr/Sonarr pick the release that scores best for your house.",
    more_goal="There is no universal best profile — resolution, HDR, devices, disk, and bandwidth matter.",
    words=["TRaSH", "Custom Format", "Quality Profile", "Radarr", "Sonarr"],
    diagram='''QUALITY
   +
CUSTOM FORMATS
   +
SCORING
   +
QUALITY PROFILES
   =
WHAT RADARR/SONARR PREFER''',
    notes='''<p>Grade these fake releases for a “normal TV living-room 1080p” profile vs a “4K HDR enthusiast” profile:</p>
<pre class="cr-code">Movie.2160p.WEB-DL.DV.HDR.DDP5.1.mkv
Movie.1080p.BluRay.x264.DTS.mkv
Movie.2160p.REMUX.DV.TrueHD.Atmos.mkv</pre>
<p>Write which one each profile prefers and why (size, HDR, remux bandwidth).</p>''',
    lab='''<p>Open TRaSH Radarr/Sonarr quality profile pages. Map your answers to real CF names (without syncing yet — Class 7 syncs).</p>'''
    + mean_more("If everything is ‘grab anything,’ you taught the robot no taste.", "Anime needs a separate TRaSH anime profile — never merge blindly into TV."),
    breakfix='''<div class="cr-callout">If your preferred pick is a REMUX but your network is weak, the profile is wrong for your house — not ‘broken ARR’.</div>''',
    check=["I graded the three fake releases for two profiles", "I can define Custom Format in plain words", "I know anime ≠ normal TV profiles"],
    docs=[("TRaSH Guides", "https://trash-guides.info/"), ("Radarr CF collection", "https://trash-guides.info/Radarr/Radarr-collection-of-custom-formats/")],
    prev=("05-prowlarr.html", "Class 5"), next=("07-trash-automation.html", "Class 7"),
))

# --- Class 7 ---
CLASSES.append(dict(
    id="7", file="07-trash-automation.html", unit="Unit 2 — ARR Media Automation", unit_slug="2-arr",
    title="Automating TRaSH configuration", level="mid",
    goal="Choose GUI sync vs config-file sync. Advanced path: Recyclarr YAML → sync → verify CF scores.",
    lecture_note="Concept lecture: IBRACORP TRaSH & Notifiarr sync. TRaSH now also recognizes Recyclarr, Configarr, Clonarr — we teach Recyclarr for reproducible infrastructure.",
    mean_goal="Robots update your grading rubrics so you don’t click 150 checkboxes after every guide change.",
    more_goal="GUI: Notifiarr/Clonarr. Config file: Recyclarr. Homelab Academy prefers Recyclarr + git.",
    words=["Recyclarr", "TRaSH", "YAML", "Custom Format"],
    diagram='''How do you manage TRaSH?
            START
              |
       +------+------+
       |             |
      GUI        CONFIG FILE
       |             |
 Notifiarr /       Recyclarr
   Clonarr           |
                     v
              Radarr / Sonarr''',
    notes='''<ol>
<li>Pick a starter TRaSH profile (e.g. WEB-1080p)</li>
<li>Write Recyclarr config for Sonarr/Radarr instances</li>
<li>Sync</li>
<li>Verify Custom Formats + scores appeared</li>
</ol>''',
    lab='''<pre class="cr-code"># Follow current Recyclarr docs for your Sonarr/Radarr URLs + API keys
# recyclarr sync
# In Radarr: Custom Formats list should populate; Quality Profile scores update</pre>''',
    breakfix='''<div class="cr-tree">
 <div class="node q">Sync ran but scores empty?</div>
 <div class="branch">
  <div class="node bad">Wrong instance URL/API key / profile name typo</div>
  <div class="node ok">Re-read Recyclarr logs; confirm guide IDs match current TRaSH</div>
 </div>
</div>''',
    check=["I chose GUI or Recyclarr path deliberately", "A sync completed", "CF scores visible in ARR", "I did not hand-build dozens of CFs"],
    docs=[("Recyclarr", "https://recyclarr.dev/"), ("TRaSH sync tools notes", "https://trash-guides.info/")],
    prev=("06-trash-fundamentals.html", "Class 6"), next=("/classroom/units/3-home-assistant/", "Unit 3"),
))

# --- Class 8 ---
CLASSES.append(dict(
    id="8", file="08-ha-beginner.html", unit="Unit 3 — Home Assistant", unit_slug="3-home-assistant",
    title="Home Assistant for complete beginners", level="baby",
    goal="No YAML yet. Master Device / Entity / Integration / Area — and put one device on a dashboard.",
    lecture_note="Concept lecture: Smart Home Junkie HA beginner guide (UI aged — use current HA Getting Started).",
    mean_goal="A device is the gadget. Entities are the controllable pieces. Areas are rooms. Integrations are the translators.",
    more_goal="One Hue bulb can expose light + power sensor entities.",
    words=["HA", "Device", "Entity", "Integration", "Area"],
    diagram='''DEVICE
Philips Hue Bulb
   |
   +-- ENTITY light.office_lamp
   +-- ENTITY sensor.office_lamp_power
   |
   v
 AREA: Office
   |
   v
 DASHBOARD card''',
    notes='''<p><strong>Exit ticket (must pass):</strong> explain Device vs Entity vs Integration vs Area without notes.</p>
<ol><li>Add device</li><li>Rename device</li><li>Rename entity</li><li>Assign Area</li><li>Dashboard</li></ol>''',
    lab='''<p>Install HA OS (VM or official supported hardware) using current docs. Onboard one real or virtual device. No automations yet.</p>'''
    + mean_more("If you jump to YAML now, you skip the map of your house.", "Enable automatic backups before Class 9."),
    breakfix='''<div class="cr-callout">Cannot explain Device/Entity/Integration/Area? Do not continue — re-lab with one bulb/switch only.</div>''',
    check=["I can explain Device / Entity / Integration / Area", "One device renamed + area-assigned", "It appears on a dashboard", "Backups enabled"],
    docs=[("HA Getting Started", "https://www.home-assistant.io/getting-started/"), ("HA concepts", "https://www.home-assistant.io/docs/")],
    prev=("/classroom/units/2-arr/classes/07-trash-automation.html", "Class 7"), next=("09-ha-automation.html", "Class 9"),
))

# --- Class 9 ---
CLASSES.append(dict(
    id="9", file="09-ha-automation.html", unit="Unit 3 — Home Assistant", unit_slug="3-home-assistant",
    title="Real Home Assistant automation", level="baby",
    goal="Automate a real household problem — not a toy toggle. Build trigger → condition → action, then break each piece.",
    lecture_note="Concept lecture: NetworkChuck ‘your home automation sucks’ — solve a real problem. Pair with current Automation editor docs.",
    mean_goal="When something happens, if it’s still true that we care, do the helpful thing — then stop.",
    more_goal="PROBLEM → TRIGGER → CONDITION → ACTION → WAIT → ACTION.",
    words=["HA", "Automation", "Trigger", "Condition", "Action"],
    diagram='''PROBLEM
"Hallway is too dark at night"
       |
       v
TRIGGER   Motion detected
       |
       v
CONDITION Sun below horizon
       |
       v
ACTION    Light 30%
       |
       v
WAIT      5 minutes
       |
       v
ACTION    Light off''',
    notes='''<p>Lab: motion → night condition → lamp → timeout off.</p>
<p>Then break Trigger, Condition, Action one at a time and diagnose.</p>''',
    lab='''<p>Use UI Automations (no YAML required). Evidence: screenshot of automation + phone video of motion test.</p>''',
    breakfix='''<div class="cr-tree">
 <div class="node q">Light never turns on?</div>
 <div class="branch">
  <div class="node bad">Trigger silent (motion entity wrong)</div>
  <div class="node ok">Trigger fires → check condition (sun) → then action entity</div>
 </div>
</div>''',
    check=["Automation solves a stated PROBLEM sentence", "I broke trigger/condition/action separately once", "Evidence screenshot saved"],
    docs=[("Automations", "https://www.home-assistant.io/docs/automation/"), ("Automation editor", "https://www.home-assistant.io/docs/automation/editor/")],
    prev=("08-ha-beginner.html", "Class 8"), next=("10-remote-access.html", "Class 10"),
))

# --- Class 10 ---
CLASSES.append(dict(
    id="10", file="10-remote-access.html", unit="Unit 3 — Home Assistant", unit_slug="3-home-assistant",
    title="Secure remote access", level="adv",
    goal="Remote access ≠ randomly opening ports. Choose VPN vs authenticated tunnel/proxy with a decision chart.",
    lecture_note="Concept lecture: NetworkChuck Cloudflare Tunnel (2022). Useful architecture; follow current Cloudflare + HA remote-access docs. Prefer Tailscale/ZeroTier for family-only access.",
    mean_goal="Don’t hang Sonarr and qBit on the public internet just because you learned port forwarding.",
    more_goal="LAN/WAN/NAT/firewall/port-forward/reverse-proxy/VPN/tunnel/TLS/DNS — pick the smallest door that solves the need.",
    words=["LAN", "WAN", "VPN", "Reverse proxy", "DNS", "TLS", "Firewall"],
    diagram='''Need remote access?
       |
       v
Only you/family?
   |
  YES --> VPN (Tailscale / ZeroTier / WireGuard)
   |
  Need public web service?
   |
  YES --> Reverse proxy / authenticated tunnel
          (NOT raw :8787/:8123/:8989 to the world)''',
    notes='''<p><strong>Warning slide:</strong> REMOTE ACCESS ≠ RANDOMLY OPENING PORTS.</p>
<p>Teach vocabulary, then choose a path. Do not expose qBit/Sonarr UIs publicly.</p>''',
    lab='''<p>Baby step: install Tailscale (or chosen VPN) on phone + HA host; reach HA without port forward.</p>
<p>Advanced optional: Cloudflare Tunnel to a single authenticated service — never the whole Docker socket.</p>''',
    breakfix='''<div class="cr-callout tip">If your plan starts with ‘forward 7878/8989/8080,’ stop and redraw the decision chart.</div>''',
    check=["I can explain VPN vs public tunnel", "I did not publish ARR/qBit to WAN", "Family-only access uses VPN (or documented exception)"],
    docs=[("HA remote access", "https://www.home-assistant.io/docs/configuration/remote/"), ("Cloudflare Tunnel docs", "https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/")],
    prev=("09-ha-automation.html", "Class 9"), next=("/classroom/units/4-voice/", "Unit 4"),
))

# --- Class 11 ---
CLASSES.append(dict(
    id="11", file="11-voice-architecture.html", unit="Unit 4 — Local Voice", unit_slug="4-voice",
    title="What Home Assistant Voice actually is", level="baby",
    goal="Architecture-only class. Map mic → wake → STT → conversation → HA → TTS → speaker. Diagnose which stage fails.",
    lecture_note="Concept lecture: Everything Smart Home / HA Voice Preview coverage — behavior reference, not an install guide yet.",
    mean_goal="Voice is an assembly line. Find which station jammed.",
    more_goal="STT/TTS/VAD/LLM/ASR vocabulary before touching satellites.",
    words=["STT", "TTS", "VAD", "LLM", "HA", "ASR", "Wake word"],
    diagram='''YOU
 |
 v
MICROPHONE
 |
 v
WAKE WORD
 |
 v
SPEECH TO TEXT
 |
 v
CONVERSATION AGENT
 |
 v
HOME ASSISTANT
 |
 v
TEXT TO SPEECH
 |
 v
SPEAKER''',
    notes='''<p>Drill: “Wake sound happens, but HA receives gibberish.” → investigate STT / mic / language model — not TTS.</p>
<table style="width:100%;border-collapse:collapse"><tr><th style="text-align:left;padding:6px;border-bottom:1px solid var(--line)">Acronym</th><th style="text-align:left;padding:6px;border-bottom:1px solid var(--line)">Meaning</th></tr>
<tr><td style="padding:6px">STT</td><td style="padding:6px">Speech to Text</td></tr>
<tr><td style="padding:6px">TTS</td><td style="padding:6px">Text to Speech</td></tr>
<tr><td style="padding:6px">VAD</td><td style="padding:6px">Voice Activity Detection</td></tr>
<tr><td style="padding:6px">ASR</td><td style="padding:6px">Automatic Speech Recognition</td></tr>
</table>''',
    lab='''<p>No install. On paper/whiteboard: label where each failure would appear (no wake / wrong text / wrong intent / no speech out).</p>''',
    breakfix='''<div class="cr-tree">
 <div class="node q">Symptom: wake OK, text wrong</div>
 <div class="node bad">Focus STT / mic quality / language — not Piper yet</div>
</div>''',
    check=["I drew the pipeline from memory", "I diagnosed the gibberish-after-wake scenario correctly", "I know STT vs TTS"],
    docs=[("HA Assist", "https://www.home-assistant.io/voice_control/"), ("Voice overview", "https://www.home-assistant.io/voice_control/")],
    prev=("/classroom/units/3-home-assistant/classes/10-remote-access.html", "Class 10"), next=("12-whisper-piper.html", "Class 12"),
))

# --- Class 12 ---
CLASSES.append(dict(
    id="12", file="12-whisper-piper.html", unit="Unit 4 — Local Voice", unit_slug="4-voice",
    title="Whisper + Piper + Wyoming", level="mid",
    goal="Hands-on local voice services. Baby-step the pipeline — never test everything at once.",
    lecture_note="Concept lecture: Whisper+Piper/Wyoming setup walkthroughs. Use current HA Wyoming + Whisper/Piper add-on/docs; compute needs vary.",
    mean_goal="Whisper listens. Piper talks. Wyoming is the cable to Home Assistant.",
    more_goal="Focused local speech vs full Whisper/Piper path — Whisper wants more CPU/GPU.",
    words=["Whisper", "Piper", "Wyoming", "Assist", "STT", "TTS"],
    diagram='''           HOME ASSISTANT
                 |
           Assist Pipeline
                 |
        +--------+--------+
        v                 v
     WHISPER            PIPER
       STT                TTS
        |                 |
        +---- WYOMING ----+''',
    notes='''<ol>
<li>Microphone test</li><li>STT test</li><li>HA text command</li><li>TTS test</li>
<li>Full pipeline</li><li>Wake word last</li>
</ol>
<p>Lab phrase: “Turn on the office light.” Capture audio → text → intent → action → spoken reply.</p>''',
    lab='''<pre class="cr-code"># Install Whisper + Piper via current HA-supported method (add-ons or Wyoming on another LAN host)
# Verify each gate before enabling wake word
# Prefer starting with a known wake word (e.g. ok nabu) per HA docs</pre>''',
    breakfix='''<div class="cr-tree">
 <div class="node q">VOICE PIPELINE FAIL</div>
 <div class="branch">
  <div class="node bad">No wake → mic/wake</div>
  <div class="node ok">Wake OK → STT text? → intent? → TTS?</div>
 </div>
</div>''',
    check=["Mic records cleanly", "STT returns correct text for a known sentence", "TTS speaks a known sentence", "Full command works BEFORE custom wake words"],
    docs=[("Wyoming integration", "https://www.home-assistant.io/integrations/wyoming/"), ("Fully local Assist", "https://www.home-assistant.io/voice_control/")],
    prev=("11-voice-architecture.html", "Class 11"), next=("13-voice-capstone.html", "Class 13"),
))

# --- Class 13 ---
CLASSES.append(dict(
    id="13", file="13-voice-capstone.html", unit="Unit 4 — Local Voice", unit_slug="4-voice",
    title="Build a completely local smart speaker", level="adv",
    goal="Voice capstone with progressive gates A–G including internet disconnected. Prefer Linux Voice Assistant / ESPHome-path satellites; Wyoming remains for Whisper/Piper.",
    lecture_note="Concept lecture: 2026 DIY local voice builds (HA OS, Whisper, Piper, openWakeWord, Wyoming, optional Ollama, ESP32/Pi satellite). wyoming-satellite is archived — use modern Linux Voice Assistant direction.",
    mean_goal="A speaker in the room should still work when the internet dies.",
    more_goal="Satellite catches audio; HA decides; Whisper/Piper may run on a stronger box.",
    words=["Wyoming", "ESPHome", "Wake word", "LLM", "Piper", "Whisper"],
    diagram='''SATELLITE (ESP32 / Pi)
     | audio
     v
HOME ASSISTANT
     |
     +-- Whisper
     +-- Assist
     +-- optional Ollama
     +-- Piper
           |
           v
        SPEAKER''',
    notes='''<p>Gates: A mic → B wake → C Whisper text → D HA understands → E HA acts → F Piper answers → G internet unplugged still works → PASS.</p>
<p>Do not debug custom wake word + mic + Whisper + intent + Piper simultaneously.</p>''',
    lab='''<p>Build/configure one satellite path using current docs (Linux Voice Assistant or HA-supported hardware). Complete gates A–G with evidence checklist.</p>''',
    breakfix='''<div class="cr-check" data-check-id="voice-gates">
 <h3>Voice gates</h3>
 <label><input type="checkbox" data-k="a"> A Microphone records good audio</label>
 <label><input type="checkbox" data-k="b"> B Wake word works</label>
 <label><input type="checkbox" data-k="c"> C Whisper produces correct text</label>
 <label><input type="checkbox" data-k="d"> D HA understands the command</label>
 <label><input type="checkbox" data-k="e"> E HA performs the action</label>
 <label><input type="checkbox" data-k="f"> F Piper answers</label>
 <label><input type="checkbox" data-k="g"> G Internet disconnected — core still works</label>
 <div class="cr-gate">All gates → <a href="/classroom/final-exam.html">Final exam</a></div>
</div>''',
    check=["Gates A–F passed on LAN", "Gate G passed offline", "I did not use archived wyoming-satellite as the primary path"],
    docs=[("Linux Voice Assistant", "https://github.com/OHF-Voice/linux-voice-assistant"), ("HA wake word", "https://www.home-assistant.io/voice_control/")],
    prev=("12-whisper-piper.html", "Class 12"), next=("/classroom/final-exam.html", "Final exam"),
))


def gen_all_classes():
    for i, c in enumerate(CLASSES):
        write(UNITS / c["unit_slug"] / "classes" / c["file"], class_page(c))


def gen_unit_indexes():
    unit_index(1, "1-infrastructure", "Infrastructure & Docker",
               "Virtualization concepts → Compose → networking → playground mindset. Videos are lectures; labs live here.",
               [("01-virtualization.html", "Class 1 — Virtualization"),
                ("02-compose.html", "Class 2 — Docker Compose"),
                ("03-networking.html", "Class 3 — Docker networking"),
                ("04-docker-playground.html", "Class 4 — Docker playground")], None)
    unit_index(2, "2-arr", "ARR Media Automation",
               "Prowlarr → TRaSH thinking → automated sync. Start with one indexer. Prefer current TRaSH + Recyclarr docs.",
               [("05-prowlarr.html", "Class 5 — Prowlarr"),
                ("06-trash-fundamentals.html", "Class 6 — TRaSH fundamentals"),
                ("07-trash-automation.html", "Class 7 — Automating TRaSH")], None)
    unit_index(3, "3-home-assistant", "Home Assistant",
               "Beginner concepts without YAML → real automations → secure remote access decision-making.",
               [("08-ha-beginner.html", "Class 8 — HA beginners"),
                ("09-ha-automation.html", "Class 9 — Real automation"),
                ("10-remote-access.html", "Class 10 — Secure remote access")], None)
    unit_index(4, "4-voice", "Local Voice",
               "Architecture → Whisper/Piper/Wyoming → local satellite capstone with offline gate.",
               [("11-voice-architecture.html", "Class 11 — Voice architecture"),
                ("12-whisper-piper.html", "Class 12 — Whisper + Piper"),
                ("13-voice-capstone.html", "Class 13 — Local smart speaker")], None)


def gen_hub():
    body = f'''
<section class="hero flush">
 <div class="stamp">HOMELAB ACADEMY<small>guided curriculum</small></div>
 <p class="eyebrow" style="margin-top:18px;">Otaconskeep Classroom</p>
 <h1 class="display" style="font-size:clamp(2rem,6vw,3.4rem);">Watch is the lecture.<br>This site is the lab.</h1>
 <p class="lede">Thirteen classes across four units. Each class is a six-page workbook: learn → vocabulary → picture → guided notes → Windows/Linux lab → break/fix/checkpoint. <strong>No videos are embedded</strong> — pair optional off-site lectures with current official docs.</p>
 <div class="btn-row" style="margin-top:22px;">
  <a class="btn btn-primary" href="start.html">Start here</a>
  <a class="btn btn-ghost" href="path.html">Choose path</a>
  <a class="btn btn-ghost" href="glossary.html">Glossary</a>
  <a class="btn btn-ghost" href="final-exam.html">Final exam</a>
 </div>
</section>
<pre class="cr-diagram"><span class="hi">RECOMMENDED ORDER</span>
1 Virtualization → 2 Compose → 3 Networking → 4 Playground
→ 5 Prowlarr → 6 TRaSH → 7 Recyclarr/sync
→ 8 HA beginner → 9 Automation → 10 Remote access
→ 11 Voice architecture → 12 Whisper/Piper → 13 Local speaker
→ FINAL EXAM verification matrix</pre>
<div class="cr-course-grid">
 <a class="cr-course-card" href="units/1-infrastructure/"><div class="num">1</div><div><h3>Infrastructure &amp; Docker</h3><p>Classes 1–4</p><div class="meta">🟢→🟡</div></div></a>
 <a class="cr-course-card" href="units/2-arr/"><div class="num">2</div><div><h3>ARR Media Automation</h3><p>Classes 5–7</p><div class="meta">🟢→🟡</div></div></a>
 <a class="cr-course-card" href="units/3-home-assistant/"><div class="num">3</div><div><h3>Home Assistant</h3><p>Classes 8–10</p><div class="meta">🟢→🔴</div></div></a>
 <a class="cr-course-card" href="units/4-voice/"><div class="num">4</div><div><h3>Local Voice</h3><p>Classes 11–13</p><div class="meta">🟢→🔴</div></div></a>
</div>
<div class="cr-callout tip"><strong>Important rule:</strong> older NetworkChuck/IBRACORP lectures teach concepts. Do not blindly copy every command or UI screen — always prefer current Docker, TRaSH, Servarr, and Home Assistant documentation linked in each class.</div>
<section>
 <p class="tag">Coming expansions</p>
 <h2>More lectures later</h2>
 <p class="intro">Next backlog: dedicated beginner+advanced pairs for Sonarr, Radarr, SAB, qBit, hardlinks, Recyclarr deep-dives, Plex/Jellyfin, Zigbee, ESPHome, MQTT, VLANs, UniFi, Linux Voice Assistant, and troubleshooting studios — so every module has ≥1 beginner lecture + ≥1 advanced lecture + official guide.</p>
</section>
'''
    write(SITE / "index.html", wrap("Homelab Academy · Classroom", "Guided Homelab/ARR/HA/Voice curriculum with labs and checkpoints.", "/classroom/", "ACADEMY", body))


def gen_start_path():
    start = f'''
<section class="hero flush">{badge("baby")}
<h1 class="display" style="font-size:clamp(2rem,5vw,3rem);margin-top:12px;">Start here</h1>
<p class="lede">This is a self-paced technical course. The video (if you use one) is only the lecture. You pause, lab, checkpoint, then continue.</p></section>
<div class="cr-box"><h3>Rules of the Academy</h3>
<ul>
<li>One concept → one picture → one action → verify → next</li>
<li>Windows/Linux split only for install paths; concepts merge</li>
<li>No embedded videos on these pages</li>
<li>Prefer current official docs over old screenshots in lectures</li>
<li>🔴 classes assume earlier checkpoints passed</li>
</ul></div>
{checkpoint("academy-start", [
  "I understand videos are optional lectures, not copy-paste scripts",
  "I will use the glossary when a word is new",
  "I picked or will pick a Windows WSL2 or Linux Docker path",
], "path.html", "Choose path")}
<div class="cr-pager"><a href="/classroom/">← Academy</a><a href="path.html">Path →</a></div>
'''
    write(SITE / "start.html", wrap("Start here · Classroom", "Academy rules.", "/classroom/start.html", "START", start))

    path = f'''
<section class="hero flush">{badge("baby")}
<h1 class="display" style="font-size:clamp(2rem,5vw,3rem);margin-top:12px;">Choose your path</h1>
<p class="lede">After Docker works, you rejoin the common class order.</p></section>
<div class="cr-path-grid">
 <a class="cr-path-card win" href="units/1-infrastructure/classes/01-virtualization.html" data-set-os="windows"><h3>Windows 11</h3><p>WSL2 + Docker Desktop/Engine. Proxmox optional as concept-only.</p></a>
 <a class="cr-path-card lin" href="units/1-infrastructure/classes/01-virtualization.html" data-set-os="linux"><h3>Linux</h3><p>Ubuntu/Debian + Docker Engine. Optional Proxmox on spare hardware.</p></a>
</div>
{checkpoint("academy-path", ["I selected Windows or Linux for OS tabs", "I know Class 1 is next"], "units/1-infrastructure/classes/01-virtualization.html", "Class 1")}
'''
    write(SITE / "path.html", wrap("Choose path · Classroom", "OS fork.", "/classroom/path.html", "PATH", path))


def gen_final():
    rows = [
        ("Docker persistent", "Destroy/recreate container; config survives"),
        ("ARR connectivity", "API tests green"),
        ("Hardlinks", "Same inode / no duplicate storage (when using torrents)"),
        ("Prowlarr", "Indexer propagates to ARRs"),
        ("TRaSH", "Expected CFs and scores present"),
        ("Download", "Request reaches downloader"),
        ("Import", "Correct path/name under /data/media"),
        ("Plex/Jellyfin", "Media detected"),
        ("HA", "Automation works"),
        ("STT", "Known sentence transcribed"),
        ("TTS", "Known response spoken"),
        ("Voice", "End-to-end command passes"),
        ("Local operation", "Internet disconnected; core functions survive"),
    ]
    checks = ''.join(f'<label><input type="checkbox" data-k="{i}"><strong>{H.escape(r)}</strong> — {H.escape(v)}</label>' for i,(r,v) in enumerate(rows))
    body = f'''
<section class="hero flush">{badge("adv")}
<h1 class="display" style="font-size:clamp(1.8rem,5vw,2.8rem);margin-top:12px;">Final exam — working homelab</h1>
<p class="lede">Not a written test. A verification matrix. “It seems to work” is not a grade.</p></section>
<pre class="cr-diagram">REQUEST MOVIE → SEERR → RADARR → PROWLARR → qBIT/SAB → /data/media → PLEX

HOME ASSISTANT
  |-- monitors infrastructure
  |-- runs automations
  +-- local voice → "Is Plex online?" → spoken answer</pre>
<div class="cr-check" data-check-id="final-exam">
 <h3>Verification matrix</h3>
 {checks}
 <div class="cr-gate">All requirements evidenced → you finished Homelab Academy v1</div>
</div>
<div class="cr-pager"><a href="units/4-voice/classes/13-voice-capstone.html">← Class 13</a><a href="/classroom/">Academy home →</a></div>
'''
    write(SITE / "final-exam.html", wrap("Final exam · Classroom", "Homelab verification matrix.", "/classroom/final-exam.html", "FINAL EXAM", body))


def gen_github():
    (GH / "README.md").write_text('''# Otaconskeep Classroom — Homelab Academy

Guided curriculum for ARR + Home Assistant + local voice.

**Site (canonical):** https://otaconskeep.github.io/classroom/

## Format

Each class is a six-page workbook:

1. What you’re going to learn  
2. Acronyms / vocabulary  
3. Architecture picture  
4. Guided notes (lecture concepts — **no embedded videos**)  
5. Windows/Linux baby-step lab  
6. Troubleshooting + checkpoint  

Pattern: **Understand → Build → Break → Fix → Verify**

Older NetworkChuck / IBRACORP material is treated as concept lectures. Always prefer current official documentation linked in each class.

## Units

1. Infrastructure & Docker (Classes 1–4)  
2. ARR Media Automation (Classes 5–7)  
3. Home Assistant (Classes 8–10)  
4. Local Voice (Classes 11–13)  
5. Final exam verification matrix  

## License

MIT — Antonio G. Garcia (Otaconskeep)
''')
    print("github readme updated")


def main():
    gen_hub()
    gen_start_path()
    gen_unit_indexes()
    gen_all_classes()
    gen_final()
    gen_github()
    # redirect old courses path
    write(SITE / "courses" / "index.html", '''<!doctype html><meta http-equiv="refresh" content="0;url=/classroom/"><script>location.replace('/classroom/')</script>''')
    print("DONE", len(CLASSES), "classes")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Write /news/, the two-desk News hub, with a real latest-story preview
per desk pulled from each desk's own archive.json.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://otaconskeep.github.io'

DESKS = (
    {
        'slug': 'ai-homelab',
        'kicker': 'Live',
        'title': 'AI &amp; Homelab',
        'desc': 'Self-hosting, local models, videos, Reddit, and social. Updated from the Keep.',
    },
    {
        'slug': 'systems-engineering',
        'kicker': 'Live',
        'title': 'Systems Engineering',
        'desc': 'Requirements, architecture, MBSE, verification and validation. Updated from the Keep.',
    },
)


def newest_item(slug: str) -> dict | None:
    path = ROOT / 'news' / slug / 'archive.json'
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None
    items = [row for row in (data.get('items') or []) if isinstance(row, dict) and row.get('url')]
    if not items:
        return None

    def ts(row: dict) -> str:
        return str(row.get('added_at') or row.get('published') or '')

    items.sort(key=ts, reverse=True)
    return items[0]


def desk_card(desk: dict) -> str:
    top = newest_item(desk['slug'])
    slug = desk['slug']
    title = desk['title']
    kicker = desk['kicker']
    desc = desk['desc']
    preview = ''
    if top:
        story_title = html.escape(str(top.get('title') or '')[:140])
        story_url = html.escape(str(top.get('url') or ''))
        story_source = html.escape(str(top.get('source') or ''))
        preview = (
            '<div class="news-hub-preview">'
            f'<span class="news-hub-preview-tag">Latest &middot; {story_source}</span>'
            f'<a class="news-hub-preview-title" href="{story_url}" target="_blank" rel="noopener">{story_title}</a>'
            '</div>'
        )
    else:
        kicker = 'Next desk'
        preview = '<div class="news-hub-preview"><span class="news-hub-preview-tag">Page ships when the first edition is ready.</span></div>'
    return (
        '<article class="resource">'
        f'<span>{html.escape(kicker)}</span>'
        f'<a class="title" href="/news/{slug}/">{title}</a>'
        f'<p>{html.escape(desc)}</p>'
        f'{preview}'
        '<div class="btn-row" style="margin-top:12px;">'
        f'<a class="btn btn-ghost" href="/news/{slug}/">See more stories</a>'
        '</div>'
        '</article>'
    )


def page() -> str:
    cards = '\n  '.join(desk_card(desk) for desk in DESKS)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="canonical" href="{SITE}/news/">
<link rel="alternate" type="application/rss+xml" title="AI & Homelab News" href="{SITE}/news/ai-homelab/feed.xml">
<link rel="alternate" type="application/rss+xml" title="Systems Engineering News" href="{SITE}/news/systems-engineering/feed.xml">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>News &middot; Otaconskeep</title>
<meta name="description" content="News from the Keep: AI and homelab for people running it at home, plus systems engineering.">
<meta name="robots" content="index,follow">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=20260929e">
<style>
.news-hub {{
  display:grid; grid-template-columns: repeat(2, minmax(0, 1fr));
  gap:16px; margin: 8px 0 48px;
}}
@media (max-width: 860px) {{
  .news-hub {{ grid-template-columns: 1fr; }}
}}
.news-hub .resource {{
  border:1px solid var(--line); background:var(--surface); padding:18px 16px 16px;
}}
.news-hub .resource a.title {{
  color:var(--cream); font-weight:700; font-size:1.15rem; text-decoration:none;
}}
.news-hub .resource a.title:hover {{ color:var(--accent-bright); }}
.news-hub .resource span {{
  display:block; margin:6px 0 10px; color:var(--accent-bright);
  font-family:'JetBrains Mono', ui-monospace, monospace;
  font-size:.72rem; letter-spacing:.08em; text-transform:uppercase;
}}
.news-hub .resource p {{ margin:0 0 14px; color:var(--cream-dim); }}
.news-hub-preview {{
  border-top:1px solid var(--line); padding-top:12px; margin-top:2px;
}}
.news-hub-preview-tag {{
  display:block; margin:0 0 6px; color:var(--cream-faint);
  font-family:'JetBrains Mono', ui-monospace, monospace;
  font-size:.68rem; letter-spacing:.06em; text-transform:uppercase;
}}
.news-hub-preview-title {{
  color:var(--cream); font-weight:600; font-size:.94rem; text-decoration:none; line-height:1.4;
}}
.news-hub-preview-title:hover {{ color:var(--accent-bright); }}
</style>
</head>
<body>

<div class="filebar">
 <div class="wrap">
 <span>FILE // NEWS</span>
 <span>OTACONSKEEP // EDITIONS</span>
 </div>
</div>

<nav class="topnav">
 <div class="wrap">
 <a class="brand" href="/"><img class="brand-avatar" src="/assets/img/otacon-brand-fullbody.png" alt=""><span class="brand-text">Otaconskeep<span class="brand-byline">Antonio G. Garcia</span></span></a>
 <button class="navtoggle" aria-label="Toggle navigation" aria-expanded="false">MENU</button>
 <div class="navlinks">
 <a href="/">Home</a>
 <a href="/#ecosystem">Platform</a>
 <div class="navdrop">
 <a href="/#ecosystem">Products</a>
 <div class="navdrop-menu">
 <a href="/otacon/">Otacon Lite</a>
 <a href="/keeproute/">KeepRoute</a>
 <a href="/keepdesk/">Keep Desk</a>
 <a href="/expansion/">Expansion</a>
 <a href="/ai9/">AI9</a>
 </div>
 </div>
 <a href="/classroom/">Learn</a>
 <a href="/engineering/">Engineering</a>
 <a href="/about/">About</a>
 <a href="/news/" aria-current="page">News</a>
 <a href="/donate/">Donate</a>
 <a href="/install/" class="discord">Get Otacon</a>
 </div></div>
</nav>
<nav class="cr-subnav" aria-label="News">
 <div class="wrap">
 <a href="/news/" aria-current="page">News</a>
 <a href="/news/ai-homelab/">AI &amp; Homelab</a>
 <a href="/news/systems-engineering/">Systems Engineering</a>
 </div>
</nav>

<div class="wrap">
 <section class="hero flush">
 <p class="eyebrow">From the Keep</p>
 <h1 class="display" style="font-size: clamp(2.4rem, 6vw, 4.4rem);">News</h1>
 <p class="lede">Editions for people running AI, a lab, and systems engineering work. Pick a desk.</p>
 </section>

 <div class="news-hub">
  {cards}
 </div>
</div>
<script src="/assets/site.js"></script>
</body>
</html>
'''


def main() -> None:
    out = ROOT / 'news' / 'index.html'
    out.write_text(page(), encoding='utf-8')
    print('wrote news hub')


if __name__ == '__main__':
    main()

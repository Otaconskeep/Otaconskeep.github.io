#!/usr/bin/env python3
"""Write the public News in AI page and RSS from the Keep's Home Current edition."""
from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANKS = Path(
    os.environ.get('OTACON_BANKS')
    or '/mnt/data/docker/volumes/otacon-executor_otacon-data/_data/learning/category_banks.json'
)
SITE = 'https://otaconskeep.github.io'
PAGE = f'{SITE}/news/'
FEED = f'{SITE}/news/feed.xml'


def clean(raw: str) -> str:
    text = raw or ''
    for _ in range(3):
        nxt = html.unescape(text)
        if nxt == text:
            break
        text = nxt
    text = re.sub(r'<[^>]*>', ' ', text)
    text = text.split('<', 1)[0]
    text = re.split(r'\shttps?://', text, maxsplit=1)[0]
    text = re.sub(r'\s+', ' ', text).strip(' |-')
    return text


def lane(item: dict) -> str:
    kind = str(item.get('kind') or '')
    source = str(item.get('source') or '').lower()
    if kind == 'youtube':
        return 'Video'
    if kind == 'social':
        if source.startswith('r/'):
            return 'Reddit'
        if 'lemmy' in source:
            return 'Lemmy'
        if 'bluesky' in source:
            return 'Bluesky'
        if 'hacker' in source:
            return 'Hacker News'
        return 'Social'
    return 'Article'


def present(item: dict) -> dict:
    source = str(item.get('source') or 'Home Current')
    title = clean(str(item.get('title') or ''))
    prefix = f'{source}: '
    if title.lower().startswith(prefix.lower()):
        title = title[len(prefix):].strip()
    if ' |' in title:
        head = title.split(' |', 1)[0].strip()
        if len(head) > 24:
            title = head
    summary = clean(str(item.get('summary') or ''))
    summary = re.split(r'\s#\s', summary, maxsplit=1)[0].strip()
    if summary.lower().startswith(title.lower()):
        summary = summary[len(title):].strip(' |-')
    if summary.lower() == title.lower():
        summary = ''
    return {
        'title': title[:180] or source,
        'url': str(item.get('url') or ''),
        'source': source,
        'lane': lane(item),
        'summary': summary[:280],
    }


def load_items() -> tuple[list[dict], str]:
    data = json.loads(BANKS.read_text(encoding='utf-8'))
    slot = ((data.get('banks') or {}).get('home_current') or {})
    rows = [present(row) for row in (slot.get('items') or []) if isinstance(row, dict) and row.get('url')]
    when = str(slot.get('updated_at') or '')
    return rows, when


def stamp(when: str) -> str:
    try:
        moment = datetime.fromisoformat(when.replace('Z', '+00:00'))
    except ValueError:
        moment = datetime.now(timezone.utc)
    return moment.strftime('%B %-d, %Y')


def cards(rows: list[dict]) -> str:
    blocks = []
    for row in rows:
        summary = f'<p>{html.escape(row["summary"])}</p>' if row['summary'] else ''
        blocks.append(
            '<article class="news-card">'
            f'<p class="news-kicker">{html.escape(row["lane"])} · {html.escape(row["source"])}</p>'
            f'<h2><a href="{html.escape(row["url"])}" target="_blank" rel="noopener">{html.escape(row["title"])}</a></h2>'
            f'{summary}'
            '</article>'
        )
    return '\n'.join(blocks)


def page(rows: list[dict], when: str) -> str:
    dated = stamp(when)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="canonical" href="{PAGE}">
<link rel="alternate" type="application/rss+xml" title="News in AI" href="{FEED}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>News in AI · Otaconskeep</title>
<meta name="description" content="News in AI for people running it at home. Self-hosting, local models, videos, Reddit, and social. Updated from the Keep.">
<meta name="robots" content="index,follow">
<link rel="icon" type="image/svg+xml" href="../assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/style.css?v=20260920i">
<style>
.news-list {{ display:grid; gap:14px; margin: 8px 0 36px; }}
.news-card {{
  border:1px solid var(--line); background:var(--surface);
  padding:18px 18px 8px;
}}
.news-kicker {{
  margin:0 0 6px; color:var(--accent-bright);
  font-family:'JetBrains Mono', ui-monospace, monospace;
  font-size:.72rem; letter-spacing:.12em; text-transform:uppercase;
}}
.news-card h2 {{ font-size:1.25rem; line-height:1.3; }}
.news-card h2 a {{ color:var(--cream); text-decoration:none; }}
.news-card h2 a:hover {{ color:var(--accent-bright); }}
.news-card p {{ color:var(--cream-dim); }}
</style>
</head>
<body>

<div class="filebar">
 <div class="wrap">
 <span>FILE // NEWS-IN-AI</span>
 <span>HOME CURRENT · {html.escape(dated.upper())}</span>
 </div>
</div>

<nav class="topnav">
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
 <a href="/classroom/">Classroom</a>
 <a href="/engineering/">Engineering</a>
 <a href="/news/" aria-current="page">News</a>
 <a href="/faq/">FAQ</a>
 <a href="/about/">About</a>
 <a href="https://github.com/Otaconskeep" target="_blank" rel="noopener">GitHub</a>
 <a class="discord" href="https://discord.gg/cZDeqECzX" target="_blank" rel="noopener">Discord</a>
 </div></div>
</nav>

<div class="wrap">
 <section class="hero flush">
 <p class="eyebrow">Home Current · {html.escape(dated)}</p>
 <h1 class="display" style="font-size: clamp(2.4rem, 6vw, 4.4rem);">News in AI</h1>
 <p class="lede">For people running it at home. Self-hosting, local models, videos, Reddit, and social. The Keep refreshes this edition, and doom headlines stay out.</p>
 <div class="btn-row" style="margin-top: 22px;">
 <a class="btn btn-primary" href="{FEED}">Subscribe with RSS</a>
 <a class="btn btn-ghost" href="https://discord.gg/cZDeqECzX" target="_blank" rel="noopener">Join Discord</a>
 <a class="btn btn-ghost" href="https://github.com/Otaconskeep" target="_blank" rel="noopener">GitHub</a>
 </div>
 </section>
 <div class="news-list">
{cards(rows)}
 </div>
</div>
<script src="../assets/site.js"></script>
</body>
</html>
'''


def feed(rows: list[dict], when: str) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0"><channel>',
        '<title>News in AI</title>',
        f'<link>{PAGE}</link>',
        '<description>News in AI for people running it at home. Self-hosting, local models, videos, Reddit, and social.</description>',
        f'<lastBuildDate>{html.escape(when or stamp(""))}</lastBuildDate>',
    ]
    for row in rows:
        summary = f'{row["lane"]} · {row["source"]}. {row["summary"]}'.strip()
        lines.extend([
            '<item>',
            f'<title>{html.escape(row["title"])}</title>',
            f'<link>{html.escape(row["url"])}</link>',
            f'<guid isPermaLink="true">{html.escape(row["url"])}</guid>',
            f'<description>{html.escape(summary[:500])}</description>',
            '</item>',
        ])
    lines.append('</channel></rss>')
    return '\n'.join(lines) + '\n'


def main() -> None:
    rows, when = load_items()
    if len(rows) < 1:
        raise SystemExit('Home Current edition is empty')
    out = ROOT / 'news'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'index.html').write_text(page(rows, when), encoding='utf-8')
    (out / 'feed.xml').write_text(feed(rows, when), encoding='utf-8')
    print(f'wrote {len(rows)} stories')


if __name__ == '__main__':
    main()

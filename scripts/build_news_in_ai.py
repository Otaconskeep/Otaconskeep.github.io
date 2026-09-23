#!/usr/bin/env python3
"""Write the public News in AI page and RSS from the Keep's Home Current edition."""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import urllib.request
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


_IMG = re.compile(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', re.I)
_OG = re.compile(
    r'<meta\b[^>]*(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]*>',
    re.I,
)
_CONTENT = re.compile(r'\bcontent=["\']([^"\']+)', re.I)
_YT = re.compile(r'(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{6,})')


def youtube_id(url: str) -> str:
    match = _YT.search(url or '')
    return match.group(1) if match else ''


def https_url(raw: str) -> str:
    src = html.unescape(raw or '').strip()
    if src.startswith('//'):
        src = 'https:' + src
    if src.startswith('https://') and ' ' not in src:
        return src
    return ''


def summary_image(raw: str) -> str:
    for src in _IMG.findall(html.unescape(raw or '')):
        url = https_url(src)
        lowered = url.lower()
        if not url or any(skip in lowered for skip in ('avatar', 'logo', 'emoji', 'badge')):
            continue
        return url
    return ''


def og_image(url: str) -> str:
    request = urllib.request.Request(url, headers={'User-Agent': 'OtaconskeepNews/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            page = response.read(180000).decode('utf-8', 'replace')
    except Exception:
        return ''
    for tag in _OG.findall(page):
        match = _CONTENT.search(tag)
        if not match:
            continue
        image = https_url(match.group(1))
        if image:
            return image
    return ''


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
    if summary.lower() == title.lower() or len(summary) < 12:
        summary = ''
    if re.fullmatch(r'v\d[\w.+-]*', title):
        title = f'{source} {title}'
    url = str(item.get('url') or '')
    video = youtube_id(url)
    image = ''
    if video:
        image = f'https://i.ytimg.com/vi/{video}/maxresdefault.jpg'
    else:
        image = summary_image(str(item.get('summary') or '')) or og_image(url)
    if not summary:
        summary = f'{lane(item)} from {source}.'
    return {
        'title': title[:180] or source,
        'url': url,
        'source': source,
        'lane': lane(item),
        'summary': summary[:280],
        'image': image,
        'video': video,
        'short': '/shorts/' in url,
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


def _kind(data: bytes) -> str:
    if data[:3] == b'\xff\xd8\xff':
        return '.jpg'
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return '.webp'
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return '.gif'
    return ''


def download_image(url: str, dest: Path) -> str:
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read(8_000_000)
    except Exception:
        return ''
    ext = _kind(data)
    if not ext or len(data) < 4000:
        return ''
    path = dest.with_suffix(ext)
    path.write_bytes(data)
    return path.name


def screenshot(url: str, dest: Path) -> str:
    path = dest.with_suffix('.png')
    try:
        subprocess.run(
            [
                'chromium', '--headless', '--disable-gpu', '--no-sandbox',
                '--window-size=1280,720', f'--screenshot={path}', url,
            ],
            check=False, timeout=40, capture_output=True,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ''
    if path.is_file() and path.stat().st_size > 4000:
        return path.name
    return ''


def save_visuals(rows: list[dict], folder: Path) -> None:
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    for index, row in enumerate(rows, start=1):
        stem = folder / f'{index:02d}'
        name = ''
        if row['image']:
            name = download_image(row['image'], stem)
            if not name and row['video']:
                name = download_image(f'https://i.ytimg.com/vi/{row["video"]}/hqdefault.jpg', stem)
        if not name:
            name = screenshot(row['url'], stem)
        row['file'] = f'media/{name}' if name else ''


def visual(row: dict) -> str:
    title = html.escape(row['title'])
    picture = ''
    if row.get('file'):
        picture = (
            f'<img src="{html.escape(row["file"])}" alt="{title}" width="1280" height="720">'
        )
    if row['video']:
        src = f'https://www.youtube-nocookie.com/embed/{row["video"]}'
        return (
            '<div class="story-visual">'
            f'<iframe src="{src}" title="{title}" width="1280" height="720" '
            'style="display:block;width:100%;aspect-ratio:16/9;height:auto;border:0;background:#000" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            'allowfullscreen></iframe>'
            '</div>'
        )
    if picture:
        return (
            f'<a class="story-visual" href="{html.escape(row["url"])}" target="_blank" rel="noopener">'
            f'{picture}</a>'
        )
    return ''


def cards(rows: list[dict]) -> str:
    blocks = []
    for row in rows:
        blocks.append(
            '<article class="story">'
            f'{visual(row)}'
            '<div class="story-copy">'
            f'<p class="news-kicker">{html.escape(row["lane"])} · {html.escape(row["source"])}</p>'
            f'<h2><a href="{html.escape(row["url"])}" target="_blank" rel="noopener">{html.escape(row["title"])}</a></h2>'
            f'<p>{html.escape(row["summary"])}</p>'
            '</div></article>'
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
.news-list {{
  display:grid; grid-template-columns: repeat(3, minmax(0, 1fr));
  gap:16px; margin: 8px 0 48px; align-items: start;
}}
@media (max-width: 860px) {{
  .news-list {{ grid-template-columns: 1fr; }}
}}
.story {{
  border:1px solid var(--line); background:var(--surface); overflow:hidden;
}}
.story-visual {{ display:block; background:#000; }}
.story-visual img, .story-visual iframe {{
  display:block; width:100%; aspect-ratio:16/9; height:auto; object-fit:cover;
  object-position:center top; background:#000; border:0;
}}
.story-copy {{ padding: 14px 14px 16px; }}
.news-kicker {{
  margin:0 0 6px; color:var(--accent-bright);
  font-family:'JetBrains Mono', ui-monospace, monospace;
  font-size:.72rem; letter-spacing:.12em; text-transform:uppercase;
}}
.story h2 {{ font-size: 1.05rem; line-height:1.3; margin: 0 0 8px; }}
.story h2 a {{ color:var(--cream); text-decoration:none; }}
.story h2 a:hover {{ color:var(--accent-bright); }}
.story-copy p {{ margin:0; color:var(--cream-dim); }}
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
 <a href="/news/" aria-current="page">News</a>
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
 <a class="discord" href="/install/">Get Otacon</a>
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
        picture = f'{PAGE}{row["file"]}' if row.get('file') else ''
        summary = f'{row["lane"]} · {row["source"]}. {row["summary"]}'.strip()
        body = summary[:500]
        if picture:
            body = f'<img src="{html.escape(picture)}" alt=""><p>{html.escape(body)}</p>'
        else:
            body = html.escape(body)
        lines.extend([
            '<item>',
            f'<title>{html.escape(row["title"])}</title>',
            f'<link>{html.escape(row["url"])}</link>',
            f'<guid isPermaLink="true">{html.escape(row["url"])}</guid>',
            f'<description><![CDATA[{body.replace("]]>", "]]&gt;")}]]></description>',
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
    rows.sort(key=lambda row: (0 if row['video'] else 1 if row['image'] else 2))
    save_visuals(rows, out / 'media')
    missing = [row['title'] for row in rows if not row.get('file')]
    if missing:
        raise SystemExit('missing picture for: ' + '; '.join(missing))
    (out / 'index.html').write_text(page(rows, when), encoding='utf-8')
    (out / 'feed.xml').write_text(feed(rows, when), encoding='utf-8')
    print(f'wrote {len(rows)} stories')


if __name__ == '__main__':
    main()

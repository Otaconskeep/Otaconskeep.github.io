#!/usr/bin/env python3
"""Write the public Systems Engineering News page and RSS from the Keep's
systems_engineering bank.

New stories are added. Older stories stay. The page shows the newest first.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANKS = Path(
    os.environ.get('OTACON_BANKS')
    or '/mnt/data/docker/volumes/otacon-executor_otacon-data/_data/learning/category_banks.json'
)
SITE = 'https://otaconskeep.github.io'
PAGE = f'{SITE}/news/systems-engineering/'
FEED = f'{SITE}/news/systems-engineering/feed.xml'
ARCHIVE = ROOT / 'news' / 'systems-engineering' / 'archive.json'
MIN_STORIES = 12
NEW_VISUALS = int(os.environ.get('NEWS_NEW_VISUALS', '48'))
NEW_SCREENSHOTS = int(os.environ.get('NEWS_NEW_SCREENSHOTS', '12'))


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
    text = text.replace(' — ', ' - ').replace('—', '-')
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


_SOCIAL_LANES = {'Reddit', 'Lemmy', 'Bluesky', 'Hacker News', 'Social'}


def is_social(row: dict) -> bool:
    return str(row.get('kind') or '') == 'social' or str(row.get('lane') or '') in _SOCIAL_LANES


def social_blurb(summary: str) -> str:
    text = summary or ''
    text = re.sub(r'\s*submitted by\s+/\w+\S*.*$', '', text, flags=re.I).strip()
    text = re.sub(r'\s*submitted by\s+\S+\s+to\s+.*$', '', text, flags=re.I).strip()
    text = re.sub(r'\s*\[link\]\s*\[comments\]\s*$', '', text, flags=re.I).strip()
    if text.lower().startswith('social from ') or text.lower().startswith('submitted by '):
        return ''
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
    source = str(item.get('source') or 'Systems Engineering News')
    title = clean(str(item.get('title') or ''))
    prefix = f'{source}: '
    if title.lower().startswith(prefix.lower()):
        title = title[len(prefix):].strip()
    if ' |' in title:
        head = title.split(' |', 1)[0].strip()
        if len(head) > 24:
            title = head
    if re.fullmatch(r'(?:v|b)?\d[\w.+-]*', title, re.I):
        title = f'{source} {title}'.strip()
    summary = clean(str(item.get('summary') or ''))
    summary = re.split(r'\s#\s', summary, maxsplit=1)[0].strip()
    if summary.lower().startswith(title.lower()):
        summary = summary[len(title):].strip(' |-')
    if summary.lower() == title.lower() or len(summary) < 12:
        summary = ''
    url = str(item.get('url') or '')
    video = youtube_id(url)
    image = ''
    if video:
        image = f'https://i.ytimg.com/vi/{video}/hqdefault.jpg'
    else:
        image = summary_image(str(item.get('summary') or ''))
    if not summary:
        summary = f'{lane(item)} from {source}.'
    return {
        'title': title[:180] or source,
        'url': url,
        'source': source,
        'kind': str(item.get('kind') or ''),
        'lane': lane(item),
        'summary': summary[:280],
        'image': image,
        'video': video,
        'published': str(item.get('published') or ''),
        'short': '/shorts/' in url,
    }


def load_items() -> tuple[list[dict], str]:
    data = json.loads(BANKS.read_text(encoding='utf-8'))
    banks = data.get('banks') or {}
    slot = banks.get('systems_engineering') or {}
    rows = [present(row) for row in (slot.get('items') or []) if isinstance(row, dict) and row.get('url')]
    when = str(slot.get('updated_at') or '')
    return rows, when


def to_ts(raw: str) -> float:
    text = (raw or '').strip()
    if not text:
        return 0.0
    try:
        return datetime.fromisoformat(text.replace('Z', '+00:00')).timestamp()
    except ValueError:
        pass
    try:
        return parsedate_to_datetime(text).timestamp()
    except (TypeError, ValueError, IndexError):
        return 0.0


def norm_key(url: str) -> str:
    video = youtube_id(url)
    if video:
        return 'yt:' + video
    text = (url or '').split('#', 1)[0].strip()
    text = re.sub(r'\?.*$', '', text)
    return text.rstrip('/').lower()


# Same gates as learning/systems_engineering.py, so the archive stays about
# real systems engineering, not general software engineering or aerospace chatter.
_DIRECT = {
    'r/systemsengineering', 'r/systems_engineering', 'r/controltheory',
    'tech xplore · systems engineering', 'serc',
}
_BROAD = {'r/aerospaceengineering', 'r/askengineers'}
_SE_TITLE = (
    'systems engineering', 'requirements', 'sysml', 'mbse', 'model-based',
    'verification', 'validation', 'v&v', 'trade study', 'trade-off',
    'interface control', 'architecture', 'incose', 'reliability',
    'configuration management', 'system of systems', 'digital engineering',
    'stakeholder needs', 'concept of operations', 'conops',
)
_META = (
    'megathread', 'weekly discussion', 'daily discussion', '[mod]', 'mod post',
    'subreddit rules', 'mods:', 'mod team', 'this subreddit', 'rule change',
    'career advice', 'which degree', 'is it worth it', 'salary',
)
_FEEDS = (
    {'name': 'r/SystemsEngineering', 'kind': 'social', 'url': 'https://www.reddit.com/r/SystemsEngineering/.rss'},
    {'name': 'r/systems_engineering', 'kind': 'social', 'url': 'https://www.reddit.com/r/systems_engineering/.rss'},
    {'name': 'r/ControlTheory', 'kind': 'social', 'url': 'https://www.reddit.com/r/ControlTheory/.rss'},
    {'name': 'r/AerospaceEngineering', 'kind': 'social', 'url': 'https://www.reddit.com/r/AerospaceEngineering/.rss'},
    {'name': 'r/AskEngineers', 'kind': 'social', 'url': 'https://www.reddit.com/r/AskEngineers/.rss'},
    {'name': 'Hacker News · systems engineering', 'kind': 'social', 'url': 'https://hnrss.org/newest?q=systems+engineering&points=3'},
    {'name': 'Hacker News · MBSE', 'kind': 'social', 'url': 'https://hnrss.org/newest?q=MBSE&points=1'},
    {'name': 'Hacker News · SysML', 'kind': 'social', 'url': 'https://hnrss.org/newest?q=SysML&points=1'},
    {'name': 'Hacker News · requirements engineering', 'kind': 'social', 'url': 'https://hnrss.org/newest?q=requirements+engineering&points=1'},
    {'name': 'IEEE Spectrum · Aerospace', 'kind': 'article', 'url': 'https://spectrum.ieee.org/feeds/topic/aerospace.rss'},
    {'name': 'NASA Technology', 'kind': 'article', 'url': 'https://www.nasa.gov/technology/feed/'},
    {'name': 'Tech Xplore · Systems Engineering', 'kind': 'article', 'url': 'https://techxplore.com/rss-feed/tags/systems+engineering/', 'curated': True},
    {'name': 'SERC', 'kind': 'article', 'url': 'https://sercuarc.org/feed/', 'curated': True},
)
_INTERESTS = (
    ('requirements', 'Requirements'),
    ('mbse', 'MBSE / SysML'),
    ('reliability', 'Reliability & V&V'),
    ('aerospace', 'Aerospace / NASA'),
    ('communities', 'Communities'),
    ('research', 'Research'),
)
_REQ_WORDS = (
    'requirements', 'stakeholder needs', 'concept of operations', 'conops',
    'trade study', 'trade-off', 'interface control',
)
_MBSE_WORDS = ('sysml', 'mbse', 'model-based', 'digital engineering')
_RELIABILITY_WORDS = (
    'verification', 'validation', 'v&v', 'reliability', 'configuration management',
)
_AEROSPACE_WORDS = ('nasa', 'aerospace', 'spacecraft', 'satellite', 'mars', 'orbit')
_RESEARCH_WORDS = ('serc', 'incose', 'research', 'workshop', 'study')
_VERSION = re.compile(r'\b(?:v?\d+\.\d+(?:\.\d+)?|b\d{4,})\b', re.I)


def _title_has(title: str, tokens: tuple[str, ...]) -> bool:
    text = title.lower()
    for token in tokens:
        if len(token) <= 3:
            if re.search(rf'\b{re.escape(token)}\b', text):
                return True
        elif token in text:
            return True
    return False


def keep_story(item: dict) -> bool:
    """Drop meta/career-advice posts and anything not really systems engineering."""
    source = str(item.get('source') or '').lower()
    title = str(item.get('title') or '')
    summary = str(item.get('summary') or '')
    text = f'{title} {summary}'.lower()
    kind = str(item.get('kind') or '')
    if any(phrase in title.lower() for phrase in _META):
        return False
    if source in _BROAD and not _title_has(title, _SE_TITLE):
        return False
    if source in _DIRECT:
        return True
    if kind == 'article':
        return _title_has(title, _SE_TITLE) or _title_has(text, _SE_TITLE)
    return _title_has(title, _SE_TITLE)


def categories_for(item: dict) -> list[str]:
    text = f"{item.get('title') or ''} {item.get('summary') or ''} {item.get('source') or ''}".lower()
    kind = str(item.get('kind') or '')
    lane_name = str(item.get('lane') or '')
    cats: list[str] = []
    if any(word in text for word in _REQ_WORDS):
        cats.append('requirements')
    if any(word in text for word in _MBSE_WORDS):
        cats.append('mbse')
    if any(word in text for word in _RELIABILITY_WORDS):
        cats.append('reliability')
    if any(word in text for word in _AEROSPACE_WORDS):
        cats.append('aerospace')
    if any(word in text for word in _RESEARCH_WORDS):
        cats.append('research')
    if kind == 'social' or lane_name in ('Reddit', 'Lemmy', 'Bluesky', 'Hacker News', 'Social'):
        cats.append('communities')
    if not cats:
        cats.append('research')
    return list(dict.fromkeys(cats))


def load_archive() -> dict:
    if ARCHIVE.is_file():
        try:
            data = json.loads(ARCHIVE.read_text(encoding='utf-8'))
            if isinstance(data, dict) and isinstance(data.get('items'), list):
                return data
        except json.JSONDecodeError:
            pass
    return {'items': []}


def save_archive(archive: dict) -> None:
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_text(json.dumps(archive, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def merge_rows(archive: dict, rows: list[dict]) -> int:
    """Add stories. A URL already on file is refreshed and never removed."""
    items = archive.setdefault('items', [])
    index = {norm_key(str(row.get('url') or '')): row for row in items if row.get('url')}
    added = 0
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    for row in rows:
        url = str(row.get('url') or '')
        key = norm_key(url)
        if not key:
            continue
        if key in index:
            old = index[key]
            for field in ('title', 'summary', 'source', 'kind', 'lane', 'published', 'image', 'video'):
                if row.get(field):
                    old[field] = row[field]
            if row.get('file') and not old.get('file'):
                old['file'] = row['file']
            old['categories'] = categories_for(old)
            continue
        stored = {
            'url': url,
            'title': row.get('title') or '',
            'summary': row.get('summary') or '',
            'source': row.get('source') or '',
            'kind': row.get('kind') or '',
            'lane': row.get('lane') or lane(row),
            'published': row.get('published') or '',
            'added_at': row.get('added_at') or now,
            'image': row.get('image') or '',
            'file': row.get('file') or '',
            'video': row.get('video') or '',
        }
        stored['categories'] = categories_for(stored)
        items.append(stored)
        index[key] = stored
        added += 1
    return added


def _field(block: str, name: str) -> str:
    match = re.search(rf'<{name}[^>]*>(.*?)</{name}>', block, flags=re.I | re.S)
    if not match:
        return ''
    text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', match.group(1), flags=re.S)
    text = re.sub(r'<[^>]+>', ' ', text)
    return clean(text)


def parse_feed(xml: str, *, source: str, kind: str, limit: int = 40) -> list[dict]:
    items = []
    for match in re.finditer(r'<(item|entry)\b[^>]*>(.*?)</\1>', xml or '', flags=re.I | re.S):
        block = match.group(2)
        title = _field(block, 'title')
        url = ''
        link = re.search(r'<link[^>]+href=["\']([^"\']+)["\']', block, flags=re.I)
        if link:
            url = html.unescape(link.group(1)).strip()
        if not url:
            link = re.search(r'<link[^>]*>\s*([^<]+)\s*</link>', block, flags=re.I)
            if link and link.group(1).strip().startswith('http'):
                url = html.unescape(link.group(1)).strip()
        if not url:
            ident = re.search(r'<id>\s*(https?://[^<\s]+)\s*</id>', block, flags=re.I)
            if ident:
                url = ident.group(1).strip()
        summary = _field(block, 'description') or _field(block, 'summary') or _field(block, 'content')
        if not title or not url.startswith('http'):
            continue
        items.append({
            'title': title[:180],
            'url': url,
            'summary': summary[:500],
            'source': source,
            'kind': kind,
            'published': _field(block, 'pubDate') or _field(block, 'published') or _field(block, 'updated'),
        })
        if len(items) >= limit:
            break
    return items


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (compatible; OtaconskeepNews/1.0)'},
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read(4_000_000).decode('utf-8', 'replace')


def backfill_feeds(archive: dict) -> int:
    def one(feed: dict) -> list[dict]:
        try:
            xml = fetch_text(feed['url'])
        except Exception as exc:
            print(f'skip {feed["name"]}: {exc}')
            return []
        raw = parse_feed(xml, source=feed['name'], kind=feed['kind'], limit=40)
        for row in raw:
            if feed.get('curated'):
                row['curated'] = True
        kept = [present(row) for row in raw if keep_story(row)]
        print(f'{feed["name"]}: {len(kept)} kept of {len(raw)}')
        return kept

    added = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        for rows in pool.map(one, _FEEDS):
            added += merge_rows(archive, rows)
    return added


def harvest_page(html_text: str, published: str = '') -> list[dict]:
    rows = []
    for block in re.findall(r'<article class="story">(.*?)</article>', html_text, flags=re.S):
        link = re.search(r'<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>', block, flags=re.S)
        if not link:
            continue
        kicker = re.search(r'class="news-kicker">(.*?)</p>', block, flags=re.S)
        summary = re.search(r'<p>(?!class)(.*?)</p>\s*</div>', block, flags=re.S)
        image = re.search(r'<img src="([^"]+)"', block)
        parts = clean(kicker.group(1) if kicker else '').split('·')
        lane_name = parts[0].strip() if parts else 'Article'
        source = parts[1].strip() if len(parts) > 1 else ''
        url = html.unescape(link.group(1))
        rows.append({
            'title': clean(link.group(2))[:180],
            'url': url,
            'summary': clean(summary.group(1) if summary else '')[:280],
            'source': source,
            'kind': 'youtube' if 'youtube.com' in url or 'youtu.be' in url else '',
            'lane': lane_name,
            'published': published,
            'image': '',
            'video': youtube_id(url),
            'file': html.unescape(image.group(1)) if image else '',
        })
    return rows


def harvest_history(archive: dict) -> int:
    added = 0
    current = ROOT / 'news' / 'systems-engineering' / 'index.html'
    if current.is_file():
        added += merge_rows(archive, harvest_page(current.read_text(encoding='utf-8', errors='replace')))
    log = subprocess.run(
        ['git', 'log', '--follow', '--format=%H%x09%cI', '--', 'news/systems-engineering/index.html'],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    for line in log.stdout.splitlines():
        if '\t' not in line:
            continue
        sha, published = line.split('\t', 1)
        show = subprocess.run(
            ['git', 'show', f'{sha}:news/systems-engineering/index.html'],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if show.returncode != 0:
            continue
        added += merge_rows(archive, harvest_page(show.stdout, published))
    return added


def newest_first(items: list[dict]) -> list[dict]:
    def key(row: dict) -> tuple[float, float]:
        return (to_ts(str(row.get('published') or '')), to_ts(str(row.get('added_at') or '')))
    return sorted(items, key=key, reverse=True)


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


def media_stem(url: str) -> str:
    return hashlib.sha256(norm_key(url).encode()).hexdigest()[:16]


def cached_file(row: dict, folder: Path) -> str:
    """Return media/name when this story's picture is already on disk."""
    existing = str(row.get('file') or '')
    if existing.startswith('media/'):
        path = folder / Path(existing).name
        if path.is_file() and path.stat().st_size > 4000:
            return f'media/{path.name}'
    stem = folder / media_stem(str(row.get('url') or ''))
    for ext in ('.jpg', '.png', '.webp', '.gif'):
        path = stem.with_suffix(ext)
        if path.is_file() and path.stat().st_size > 4000:
            return f'media/{path.name}'
    return ''


def save_visuals(rows: list[dict], folder: Path) -> None:
    """Keep pictures already on disk. Fill missing previews for the newest stories."""
    folder.mkdir(parents=True, exist_ok=True)
    pending: list[dict] = []
    for row in rows:
        if is_social(row):
            row['file'] = ''
            continue
        found = cached_file(row, folder)
        if found:
            row['file'] = found
            continue
        row['file'] = ''
        if len(pending) < NEW_VISUALS:
            pending.append(row)

    def pull_remote(row: dict) -> None:
        stem = folder / media_stem(str(row.get('url') or ''))
        image = str(row.get('image') or '')
        if not image:
            image = og_image(str(row.get('url') or ''))
            if image:
                row['image'] = image
        name = download_image(image, stem) if image else ''
        if not name and row.get('video'):
            name = download_image(
                f'https://i.ytimg.com/vi/{row["video"]}/hqdefault.jpg',
                stem,
            )
        if name:
            row['file'] = f'media/{name}'

    if pending:
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(pull_remote, pending))

    shots = [row for row in pending if not row.get('file')][:NEW_SCREENSHOTS]

    def shoot(row: dict) -> None:
        stem = folder / media_stem(str(row.get('url') or ''))
        name = screenshot(str(row.get('url') or ''), stem)
        if name:
            row['file'] = f'media/{name}'

    if shots:
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(shoot, shots))


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
    label = html.escape(row.get('source') or row.get('lane') or 'News')
    return (
        f'<a class="story-visual story-fallback" href="{html.escape(row["url"])}" target="_blank" rel="noopener">'
        f'<span>{label}</span></a>'
    )


def cards(rows: list[dict]) -> str:
    blocks = []
    for row in rows:
        cats = '|'.join(row.get('categories') or [])
        title = html.escape(row['title'])
        url = html.escape(row['url'])
        if is_social(row):
            blurb = social_blurb(str(row.get('summary') or ''))
            body = f'<p>{html.escape(blurb)}</p>' if blurb else ''
            blocks.append(
                f'<article class="story story-social" data-cats="{html.escape(cats)}">'
                '<div class="story-copy">'
                f'<p class="social-mark">{html.escape(row["lane"])} · {html.escape(row["source"])}</p>'
                f'<h2><a href="{url}" target="_blank" rel="noopener">{title}</a></h2>'
                f'{body}'
                '</div></article>'
            )
            continue
        blocks.append(
            f'<article class="story" data-cats="{html.escape(cats)}">'
            f'{visual(row)}'
            '<div class="story-copy">'
            f'<p class="news-kicker">{html.escape(row["lane"])} · {html.escape(row["source"])}</p>'
            f'<h2><a href="{url}" target="_blank" rel="noopener">{title}</a></h2>'
            f'<p>{html.escape(row["summary"])}</p>'
            '</div></article>'
        )
    return '\n'.join(blocks)


def filter_bar(rows: list[dict]) -> str:
    counts = {slug: sum(1 for row in rows if slug in (row.get('categories') or [])) for slug, _label in _INTERESTS}
    buttons = [
        f'<button type="button" class="news-filter is-on" data-filter="all" aria-pressed="true">All <span>{len(rows)}</span></button>'
    ]
    for slug, label in _INTERESTS:
        if counts[slug] < 1:
            continue
        buttons.append(
            '<button type="button" class="news-filter" '
            f'data-filter="{slug}" aria-pressed="false">{html.escape(label)} <span>{counts[slug]}</span></button>'
        )
    return '<div class="news-filters" role="toolbar" aria-label="Show news by interest">' + ''.join(buttons) + '</div>'


# Subscribe links. The edition only keeps items that are actually about
# systems engineering, not general software or aerospace chatter.
_RESOURCES = (
    ('Publishers', (
        ('IEEE Spectrum · Aerospace', 'https://spectrum.ieee.org/tag/aerospace', 'Site', 'Aerospace and space-systems engineering.'),
        ('Tech Xplore · Systems Engineering', 'https://techxplore.com/tags/systems+engineering/', 'Site', 'Tag-filtered systems engineering coverage.'),
        ('SERC', 'https://sercuarc.org/news/', 'Site', 'Systems Engineering Research Center, DoD/academic research.'),
        ('NASA Technology', 'https://www.nasa.gov/technology/', 'Site', 'NASA engineering and technology updates.'),
    )),
    ('Communities', (
        ('r/SystemsEngineering', 'https://www.reddit.com/r/SystemsEngineering/', 'Reddit', 'Requirements, architecture, INCOSE, career threads.'),
        ('r/ControlTheory', 'https://www.reddit.com/r/ControlTheory/', 'Reddit', 'Control systems and feedback design.'),
        ('r/AerospaceEngineering', 'https://www.reddit.com/r/AerospaceEngineering/', 'Reddit', 'Kept only when it names a systems-engineering topic.'),
        ('Hacker News', 'https://news.ycombinator.com/', 'Front page', 'MBSE, SysML, and requirements-engineering threads.'),
    )),
)


def resources() -> str:
    blocks = []
    for heading, rows in _RESOURCES:
        cards = []
        for name, url, meta, note in rows:
            cards.append(
                '<li class="resource">'
                f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(name)}</a>'
                f'<span>{html.escape(meta)}</span>'
                f'<p>{html.escape(note)}</p>'
                '</li>'
            )
        blocks.append(
            f'<h3>{html.escape(heading)}</h3><ul class="resource-list">{"".join(cards)}</ul>'
        )
    return '\n'.join(blocks)


def page(rows: list[dict], when: str) -> str:
    dated = stamp(when)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="canonical" href="{PAGE}">
<link rel="alternate" type="application/rss+xml" title="Systems Engineering News" href="{FEED}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Systems Engineering News · Otaconskeep</title>
<meta name="description" content="Requirements, architecture, MBSE, verification and validation, and real systems engineering work. Updated from the Keep.">
<meta name="robots" content="index,follow">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=20260929e">
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
.news-filters {{
  display:flex; flex-wrap:wrap; gap:8px; margin: 0 0 14px;
}}
.news-filter {{
  border:1px solid var(--line); background:var(--surface); color:var(--cream);
  font-family:'Figtree', sans-serif; font-size:.92rem; font-weight:650;
  padding:8px 12px; cursor:pointer;
}}
.news-filter span {{
  margin-left:6px; color:var(--accent-bright);
  font-family:'JetBrains Mono', ui-monospace, monospace; font-size:.75rem;
}}
.news-filter.is-on {{ background:var(--accent, #8a5a12); color:#1a140c; }}
.news-filter.is-on span {{ color:#1a140c; }}
.news-count {{
  margin:0 0 14px; color:var(--cream-dim);
  font-family:'JetBrains Mono', ui-monospace, monospace; font-size:.78rem;
}}
.story-fallback {{
  display:flex; align-items:flex-end; aspect-ratio:16/9; padding:14px;
  background:linear-gradient(160deg, #1c1915, #3a2a18); text-decoration:none;
}}
.story-fallback span {{
  color:var(--cream); font-weight:700; font-size:1rem; line-height:1.3;
}}
.story-social {{
  border-left: 3px solid var(--accent);
  background:
    linear-gradient(180deg, rgba(22, 168, 147, .16), transparent 88px),
    var(--surface);
}}
.story-social .story-copy {{ padding: 18px 16px 18px; }}
.social-mark {{
  margin: 0 0 10px; color: var(--accent-bright);
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: .72rem; letter-spacing: .14em; text-transform: uppercase;
}}
.story-social h2 {{ font-size: 1.2rem; line-height: 1.35; }}
.story[hidden] {{ display:none; }}
.resource-list {{
  list-style:none; padding:0; margin:0 0 28px;
  display:grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap:12px;
}}
@media (max-width: 860px) {{
  .resource-list {{ grid-template-columns: 1fr; }}
}}
.resource {{
  border:1px solid var(--line); background:var(--surface); padding:14px 14px 12px;
}}
.resource a {{ color:var(--cream); font-weight:650; text-decoration:none; }}
.resource a:hover {{ color:var(--accent-bright); }}
.resource span {{
  display:block; margin:4px 0 6px; color:var(--accent-bright);
  font-family:'JetBrains Mono', ui-monospace, monospace;
  font-size:.72rem; letter-spacing:.06em; text-transform:uppercase;
}}
.resource p {{ margin:0; color:var(--cream-dim); }}
</style>
</head>
<body>

<div class="filebar">
 <div class="wrap">
 <span>FILE // SYSTEMS-ENGINEERING-NEWS</span>
 <span>SE DESK · {html.escape(dated.upper())}</span>
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
 <a href="/news/">News</a>
 <a href="/news/ai-homelab/">AI &amp; Homelab</a>
 <a href="/news/systems-engineering/" aria-current="page">Systems Engineering</a>
 </div>
</nav>

<div class="wrap">
 <section class="hero flush">
 <p class="eyebrow">Systems Engineering Desk · {html.escape(dated)}</p>
 <h1 class="display" style="font-size: clamp(2.4rem, 6vw, 4.4rem);">Systems Engineering News</h1>
 <p class="lede">Requirements, architecture, MBSE and SysML, verification and validation, and real aerospace/defense systems engineering work. New stories are added. Older ones stay, with the newest first.</p>
 <div class="btn-row" style="margin-top: 22px;">
 <a class="btn btn-primary" href="{FEED}">Subscribe with RSS</a>
 <a class="btn btn-ghost" href="/classroom/systems-engineering/">SE Academy</a>
 <a class="btn btn-ghost" href="https://github.com/Otaconskeep" target="_blank" rel="noopener">GitHub</a>
 </div>
 </section>
 {filter_bar(rows)}
 <p class="news-count" id="news-count">{len(rows)} stories · newest first · 3 columns</p>
 <div class="news-list">
{cards(rows)}
 </div>
 <section id="resources">
 <p class="tag">Sources</p>
 <h2>Resources</h2>
 <p class="intro">Publishers and communities the edition reads. A broad community only contributes a story when that story actually names a systems-engineering topic.</p>
{resources()}
 </section>
</div>
<script>
(function () {{
  var buttons = document.querySelectorAll('.news-filter');
  var cards = document.querySelectorAll('.story');
  var count = document.getElementById('news-count');
  function show(key) {{
    var n = 0;
    cards.forEach(function (card) {{
      var cats = (card.getAttribute('data-cats') || '').split('|');
      var on = key === 'all' || cats.indexOf(key) !== -1;
      card.hidden = !on;
      if (on) n += 1;
    }});
    buttons.forEach(function (button) {{
      var active = button.getAttribute('data-filter') === key;
      button.classList.toggle('is-on', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    }});
    if (count) {{
      var label = 'All';
      buttons.forEach(function (button) {{
        if (button.getAttribute('data-filter') === key) label = button.childNodes[0].textContent.trim();
      }});
      count.textContent = n + ' stories · ' + label + ' · newest first · 3 columns';
    }}
  }}
  buttons.forEach(function (button) {{
    button.addEventListener('click', function () {{
      show(button.getAttribute('data-filter') || 'all');
    }});
  }});
}})();
</script>
<script src="/assets/site.js"></script>
</body>
</html>
'''


def feed(rows: list[dict], when: str) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0"><channel>',
        '<title>Systems Engineering News</title>',
        f'<link>{PAGE}</link>',
        '<description>Requirements, architecture, MBSE, verification and validation, and real systems engineering work.</description>',
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
        published = html.escape(str(row.get('published') or ''))
        lines.extend([
            '<item>',
            f'<title>{html.escape(row["title"])}</title>',
            f'<link>{html.escape(row["url"])}</link>',
            f'<guid isPermaLink="true">{html.escape(row["url"])}</guid>',
            f'<pubDate>{published}</pubDate>' if published else '',
            f'<description><![CDATA[{body.replace("]]>", "]]&gt;")}]]></description>',
            '</item>',
        ])
    lines.append('</channel></rss>')
    return '\n'.join(lines) + '\n'


def main() -> None:
    edition, when = load_items()
    if len(edition) < 1:
        raise SystemExit('Systems Engineering edition is empty')
    out = ROOT / 'news' / 'systems-engineering'
    out.mkdir(parents=True, exist_ok=True)
    archive = load_archive()
    kept_history = harvest_history(archive)
    kept_edition = merge_rows(archive, edition)
    added = backfill_feeds(archive)
    print(
        f'archive {len(archive["items"])} '
        f'history +{kept_history} edition +{kept_edition} feeds +{added}'
    )
    if len(archive['items']) < MIN_STORIES:
        raise SystemExit(f'archive has {len(archive["items"])} stories, need at least {MIN_STORIES}')
    rows = newest_first(archive['items'])
    for row in rows:
        row['categories'] = categories_for(row)
        row['video'] = row.get('video') or youtube_id(str(row.get('url') or ''))
    save_visuals(rows, out / 'media')
    save_archive(archive)
    (out / 'index.html').write_text(page(rows, when), encoding='utf-8')
    (out / 'feed.xml').write_text(feed(rows, when), encoding='utf-8')
    print(f'wrote {len(rows)} stories')


if __name__ == '__main__':
    main()

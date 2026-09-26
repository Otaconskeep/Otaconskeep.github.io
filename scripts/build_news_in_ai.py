#!/usr/bin/env python3
"""Write the public News in AI page and RSS from the Keep's Home Current archive.

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
PAGE = f'{SITE}/news/'
FEED = f'{SITE}/news/feed.xml'
ARCHIVE = ROOT / 'news' / 'archive.json'
MIN_STORIES = 200


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
    slot = banks.get('home_current') or {}
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


# Same gates as Home Current, so the archive stays about running AI at home.
_DIRECT = {
    'ollama', 'llama.cpp', 'open webui', 'comfyui', 'text-generation-webui',
    'home assistant', 'immich', 'jellyfin', 'localai', 'litellm', 'vllm',
    'n8n', 'paperless-ngx', 'koboldcpp', 'anythingllm', 'dify', 'noted.lol',
    'self-hosted',
    'r/localllama', 'r/comfyui', 'r/stablediffusion', 'r/ollama', 'r/localllm',
    'lemmy localllama', 'fosstodon #localllama', 'sigmoid #localllama',
}
_BROAD = {'r/selfhosted', 'lemmy selfhosted', 'fosstodon #selfhosting'}
_AI_TITLE = (
    'ai', 'llm', 'model', 'ollama', 'gpu', 'npu', 'gguf', 'comfy', 'qwen',
    'llama', 'gemma', 'local', 'webui', 'agent', 'diffusion',
)
_HOME = (
    'ollama', 'llama.cpp', 'llamacpp', 'gguf', 'open webui', 'open-webui',
    'self-host', 'self hosted', 'selfhost', 'homelab', 'home lab', 'local llm',
    'local model', 'local ai', 'quantiz', 'comfyui', 'comfy',
    'lm studio', 'kobold', 'text-generation-webui', 'consumer gpu',
    'rtx', 'npu', 'proxmox', 'truenas', 'unraid',
    'home assistant', 'immich', 'jellyfin', 'paperless', 'n8n',
    'localai', 'litellm',
)
_VIDEO_TITLE = (
    'llm', 'model', 'ollama', 'gpu', 'npu', 'local', 'gguf',
    'comfy', 'whisper', 'qwen', 'llama', 'gemma', 'mistral', 'webui', 'agent',
    'homelab', 'self-host', 'selfhost',
)
_META = (
    'megathread', 'weekly discussion', 'daily discussion', '[mod]', 'mod post',
    'subreddit rules', 'mods:', 'mod team', 'this subreddit', 'rule change',
)
_ROUNDUP = (
    'ai news', 'news roundup', 'this week in ai', 'weekly ai news',
    'what you missed', 'need to stop', 'stop doing this', 'ai companies',
)
_FEAR = (
    'extinction', 'apocalypse', 'doomsday', 'end of humanity', 'existential risk',
    'terrifying', 'nightmare', 'panic', 'godlike', 'destroy humanity',
    'ai will kill', 'will kill us', 'out of control', 'job apocalypse',
    'mass unemployment', 'threat to humanity', 'ban all ai', 'scary ai',
    'end of the world', 'superintelligence', 'doom',
    'take your job', 'take our jobs', 'taking jobs', 'steal your job', 'steal jobs',
    'replace workers', 'replacing workers', 'end of work', 'ai takeover',
    'killing jobs', 'lose your job', 'job loss', 'they think', 'experts warn',
    'experts fear', 'going to replace', 'will replace humans',
)
_FEEDS = (
    {'name': 'Ollama', 'kind': 'article', 'url': 'https://github.com/ollama/ollama/releases.atom'},
    {'name': 'llama.cpp', 'kind': 'article', 'url': 'https://github.com/ggml-org/llama.cpp/releases.atom'},
    {'name': 'Open WebUI', 'kind': 'article', 'url': 'https://github.com/open-webui/open-webui/releases.atom'},
    {'name': 'ComfyUI', 'kind': 'article', 'url': 'https://github.com/Comfy-Org/ComfyUI/releases.atom'},
    {'name': 'Hugging Face', 'kind': 'article', 'url': 'https://huggingface.co/blog/feed.xml', 'curated': True},
    {'name': 'selfh.st', 'kind': 'article', 'url': 'https://selfh.st/rss/'},
    {'name': 'r/LocalLLaMA', 'kind': 'social', 'url': 'https://www.reddit.com/r/LocalLLaMA/.rss'},
    {'name': 'r/selfhosted', 'kind': 'social', 'url': 'https://www.reddit.com/r/selfhosted/.rss'},
    {'name': 'r/comfyui', 'kind': 'social', 'url': 'https://www.reddit.com/r/comfyui/.rss'},
    {'name': 'r/StableDiffusion', 'kind': 'social', 'url': 'https://www.reddit.com/r/StableDiffusion/.rss'},
    {'name': 'r/ollama', 'kind': 'social', 'url': 'https://www.reddit.com/r/ollama/.rss'},
    {'name': 'Lemmy LocalLLaMA', 'kind': 'social', 'url': 'https://lemmy.world/feeds/c/localllama.xml'},
    {'name': 'Lemmy selfhosted', 'kind': 'social', 'url': 'https://lemmy.world/feeds/c/selfhosted.xml'},
    {'name': 'Fosstodon #localllama', 'kind': 'social', 'url': 'https://fosstodon.org/tags/localllama.rss'},
    {'name': 'Sigmoid #localllama', 'kind': 'social', 'url': 'https://sigmoid.social/tags/localllama.rss'},
    {'name': 'Fosstodon #selfhosting', 'kind': 'social', 'url': 'https://fosstodon.org/tags/selfhosting.rss'},
    {'name': 'Hacker News', 'kind': 'social', 'url': 'https://hnrss.org/newest?q=ollama&points=5'},
    {'name': 'Hacker News · llama.cpp', 'kind': 'social', 'url': 'https://hnrss.org/newest?q=llama.cpp&points=5'},
    {'name': 'Hacker News · self-hosted', 'kind': 'social', 'url': 'https://hnrss.org/newest?q=self-hosted&points=15'},
    {'name': 'Hacker News · homelab', 'kind': 'social', 'url': 'https://hnrss.org/newest?q=homelab&points=5'},
    {'name': 'Bluesky Simon Willison', 'kind': 'social', 'url': 'https://bsky.app/profile/simonwillison.net/rss'},
    {'name': 'text-generation-webui', 'kind': 'article', 'url': 'https://github.com/oobabooga/text-generation-webui/releases.atom'},
    {'name': 'r/LocalLLM', 'kind': 'social', 'url': 'https://www.reddit.com/r/LocalLLM/.rss'},
    {'name': 'Yannic Kilcher', 'kind': 'youtube', 'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UCZHmQk67mSJgfCCTn7xBfew'},
    {'name': 'Jeff Geerling', 'kind': 'youtube', 'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UCR-DXc1voovS8nhAvccRZhg'},
    {'name': 'NetworkChuck', 'kind': 'youtube', 'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UC9x0AN7BWHpCDHSm9NiJFJQ'},
    {'name': 'Techno Tim', 'kind': 'youtube', 'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UCOk-gHyjcWZNj3Br4oxwh0A'},
    {'name': "Wolfgang's Channel", 'kind': 'youtube', 'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UCsnGwSIHyoYN0kiINAGUKxg'},
    {'name': 'Home Assistant', 'kind': 'article', 'url': 'https://www.home-assistant.io/atom.xml'},
    {'name': 'Immich', 'kind': 'article', 'url': 'https://github.com/immich-app/immich/releases.atom'},
    {'name': 'Jellyfin', 'kind': 'article', 'url': 'https://github.com/jellyfin/jellyfin/releases.atom'},
    {'name': 'LocalAI', 'kind': 'article', 'url': 'https://github.com/mudler/LocalAI/releases.atom'},
    {'name': 'LiteLLM', 'kind': 'article', 'url': 'https://github.com/BerriAI/litellm/releases.atom'},
    {'name': 'vLLM', 'kind': 'article', 'url': 'https://github.com/vllm-project/vllm/releases.atom'},
    {'name': 'n8n', 'kind': 'article', 'url': 'https://github.com/n8n-io/n8n/releases.atom'},
    {'name': 'Paperless-ngx', 'kind': 'article', 'url': 'https://github.com/paperless-ngx/paperless-ngx/releases.atom'},
    {'name': 'KoboldCpp', 'kind': 'article', 'url': 'https://github.com/LostRuins/koboldcpp/releases.atom'},
    {'name': 'AnythingLLM', 'kind': 'article', 'url': 'https://github.com/Mintplex-Labs/anything-llm/releases.atom'},
    {'name': 'Dify', 'kind': 'article', 'url': 'https://github.com/langgenius/dify/releases.atom'},
    {'name': 'noted.lol', 'kind': 'article', 'url': 'https://noted.lol/rss/'},
    {'name': 'Self-Hosted', 'kind': 'article', 'url': 'https://feeds.fireside.fm/selfhosted/rss'},
    {'name': 'ServeTheHome', 'kind': 'article', 'url': 'https://www.servethehome.com/feed/', 'curated': True},
    {'name': 'Simon Willison', 'kind': 'article', 'url': 'https://simonwillison.net/atom/everything/', 'curated': True},
    {'name': 'r/homelab', 'kind': 'social', 'url': 'https://www.reddit.com/r/homelab/.rss'},
    {'name': 'Lemmy homelab', 'kind': 'social', 'url': 'https://lemmy.world/feeds/c/homelab.xml'},
    {'name': 'The Rundown AI', 'kind': 'article', 'url': 'https://www.therundown.ai/feed', 'curated': True},
    {'name': 'TLDR AI', 'kind': 'article', 'url': 'https://tldr.tech/api/rss/ai', 'curated': True},
    {'name': "Ben's Bites", 'kind': 'article', 'url': 'https://www.bensbites.com/feed', 'curated': True},
    {'name': 'Import AI', 'kind': 'article', 'url': 'https://importai.substack.com/feed', 'curated': True},
    {'name': 'MarkTechPost', 'kind': 'article', 'url': 'https://www.marktechpost.com/feed/', 'curated': True},
    {'name': 'Last Week in AI', 'kind': 'article', 'url': 'https://lastweekin.ai/feed', 'curated': True},
)
_INTERESTS = (
    ('local-models', 'Local models'),
    ('homelab', 'Homelab'),
    ('home-automation', 'Home automation'),
    ('video', 'Video'),
    ('communities', 'Communities'),
    ('releases', 'Releases'),
)
_LOCAL_WORDS = (
    'ollama', 'llama', 'gguf', 'open webui', 'open-webui', 'comfy', 'kobold',
    'localai', 'litellm', 'vllm', 'anythingllm', 'dify', 'lm studio', 'qwen',
    'gemma', 'mistral', 'webui', 'npu', 'local llm', 'local model', 'ggml',
)
_HOMELAB_WORDS = (
    'homelab', 'home lab', 'self-host', 'self hosted', 'selfhost', 'proxmox',
    'immich', 'jellyfin', 'paperless', 'unraid', 'truenas', 'noted.lol',
)
_AUTO_WORDS = ('home assistant', 'esphome', 'n8n')
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
    """Drop takeover headlines and posts that are not about running something at home."""
    source = str(item.get('source') or '').lower()
    title = str(item.get('title') or '')
    summary = str(item.get('summary') or '')
    text = f'{title} {summary}'.lower()
    if 'wolfe' in source or any(phrase in title.lower() for phrase in _ROUNDUP):
        return False
    if any(phrase in text for phrase in _FEAR):
        return False
    kind = str(item.get('kind') or '')
    if kind == 'social' and any(phrase in title.lower() for phrase in _META):
        return False
    if kind == 'social' and source in _BROAD and not _title_has(title, _AI_TITLE):
        return False
    if kind == 'youtube' and not _title_has(title, _VIDEO_TITLE):
        return False
    if item.get('curated') and not any(hint in text for hint in _HOME):
        return False
    if source in _DIRECT:
        return True
    if any(hint in text for hint in _HOME):
        return True
    return False


def categories_for(item: dict) -> list[str]:
    text = f"{item.get('title') or ''} {item.get('summary') or ''} {item.get('source') or ''}".lower()
    kind = str(item.get('kind') or '')
    lane_name = str(item.get('lane') or '')
    url = str(item.get('url') or '')
    cats: list[str] = []
    if any(word in text for word in _LOCAL_WORDS):
        cats.append('local-models')
    if any(word in text for word in _HOMELAB_WORDS):
        cats.append('homelab')
    if any(word in text for word in _AUTO_WORDS):
        cats.append('home-automation')
    if kind == 'youtube' or lane_name == 'Video':
        cats.append('video')
    if kind == 'social' or lane_name in ('Reddit', 'Lemmy', 'Bluesky', 'Hacker News', 'Social'):
        cats.append('communities')
    if '/releases/' in url or (kind == 'article' and _VERSION.search(str(item.get('title') or ''))):
        cats.append('releases')
    if not cats:
        cats.append('homelab' if ('self' in text or 'home' in text) else 'local-models')
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
    current = ROOT / 'news' / 'index.html'
    if current.is_file():
        added += merge_rows(archive, harvest_page(current.read_text(encoding='utf-8', errors='replace')))
    log = subprocess.run(
        ['git', 'log', '--format=%H%x09%cI', '--', 'news/index.html'],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    for line in log.stdout.splitlines():
        if '\t' not in line:
            continue
        sha, published = line.split('\t', 1)
        show = subprocess.run(
            ['git', 'show', f'{sha}:news/index.html'],
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


def save_visuals(rows: list[dict], folder: Path) -> None:
    """Keep pictures already on disk. Download only a missing thumbnail."""
    folder.mkdir(parents=True, exist_ok=True)

    def one(row: dict) -> None:
        existing = str(row.get('file') or '')
        if existing:
            path = folder.parent / existing if not existing.startswith('media/') else folder / Path(existing).name
            if existing.startswith('media/'):
                path = folder / Path(existing).name
            if path.is_file() and path.stat().st_size > 4000:
                row['file'] = f'media/{path.name}'
                return
        stem = folder / media_stem(str(row.get('url') or ''))
        for ext in ('.jpg', '.png', '.webp', '.gif'):
            path = stem.with_suffix(ext)
            if path.is_file() and path.stat().st_size > 4000:
                row['file'] = f'media/{path.name}'
                return
        name = ''
        image = str(row.get('image') or '')
        if image:
            name = download_image(image, stem)
        if not name and row.get('video'):
            name = download_image(
                f'https://i.ytimg.com/vi/{row["video"]}/hqdefault.jpg',
                stem,
            )
        row['file'] = f'media/{name}' if name else ''

    with ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(one, rows))


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
        blocks.append(
            f'<article class="story" data-cats="{html.escape(cats)}">'
            f'{visual(row)}'
            '<div class="story-copy">'
            f'<p class="news-kicker">{html.escape(row["lane"])} · {html.escape(row["source"])}</p>'
            f'<h2><a href="{html.escape(row["url"])}" target="_blank" rel="noopener">{html.escape(row["title"])}</a></h2>'
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


# Subscribe links. Broad letters are listed here, and the edition only keeps
# the items that are about a homelab or self-hosting.
_RESOURCES = (
    ('Letters', (
        ('Techpresso', 'https://techpresso.beehiiv.com/', 'Email · daily · free', 'Five-minute morning digest.'),
        ('The Rundown AI', 'https://www.therundown.ai/', 'Email · daily · free', 'Practical “how to use this.”'),
        ('TLDR AI', 'https://tldr.tech/ai', 'Email · weekdays · free', 'Short bullets for engineers.'),
        ("Ben's Bites", 'https://www.bensbites.com/', 'Newsletter · daily · free and paid', 'Builders and indie founders.'),
        ('Import AI', 'https://importai.substack.com/', 'Substack · weekly · free', 'Policy and research. Home-lab pieces only.'),
        ('The Batch', 'https://www.deeplearning.ai/the-batch/', 'Email · Wednesday · free', 'Research notes for practitioners.'),
        ('Last Week in AI', 'https://lastweekin.ai/', 'Newsletter and podcast · weekly · free', 'Long-form audio.'),
        ('MarkTechPost', 'https://www.marktechpost.com/', 'Site and newsletter · several a day · free', 'Open-source releases and tutorials.'),
    )),
    ('Homelab and self-hosted', (
        ('Hacker News', 'https://news.ycombinator.com/', 'Front page', 'Ollama, llama.cpp, self-hosted, and homelab threads.'),
        ('r/LocalLLaMA', 'https://www.reddit.com/r/LocalLLaMA/', 'Reddit', 'Local models, GGUF, and home GPUs.'),
        ('r/selfhosted', 'https://www.reddit.com/r/selfhosted/', 'Reddit', 'Services you run yourself.'),
        ('r/homelab', 'https://www.reddit.com/r/homelab/', 'Reddit', 'Racks, Proxmox, and home servers.'),
        ('selfh.st', 'https://selfh.st/', 'Site', 'Self-hosted app discoveries.'),
        ('noted.lol', 'https://noted.lol/', 'Site', 'Homelab writeups and walkthroughs.'),
        ('Self-Hosted', 'https://selfhosted.show/', 'Podcast', 'Weekly homelab show.'),
        ('Home Assistant', 'https://www.home-assistant.io/blog/', 'Blog', 'Home automation releases.'),
        ('Ollama', 'https://github.com/ollama/ollama/releases', 'Releases', 'Local model runtime.'),
        ('llama.cpp', 'https://github.com/ggml-org/llama.cpp/releases', 'Releases', 'Local inference builds.'),
        ('Open WebUI', 'https://github.com/open-webui/open-webui/releases', 'Releases', 'Browser UI for local models.'),
        ('ComfyUI', 'https://github.com/Comfy-Org/ComfyUI/releases', 'Releases', 'Local image workflows.'),
        ('Immich', 'https://github.com/immich-app/immich/releases', 'Releases', 'Self-hosted photos.'),
        ('Jellyfin', 'https://github.com/jellyfin/jellyfin/releases', 'Releases', 'Self-hosted media.'),
        ('Paperless-ngx', 'https://github.com/paperless-ngx/paperless-ngx/releases', 'Releases', 'Self-hosted documents.'),
        ('LocalAI', 'https://github.com/mudler/LocalAI/releases', 'Releases', 'OpenAI-compatible local API.'),
        ('n8n', 'https://github.com/n8n-io/n8n/releases', 'Releases', 'Self-hosted automation.'),
        ('Simon Willison', 'https://simonwillison.net/', 'Blog', 'Tools and local-model notes.'),
        ('ServeTheHome', 'https://www.servethehome.com/', 'Site', 'Lab hardware, when the piece is about a homelab.'),
        ('Techno Tim', 'https://www.youtube.com/@TechnoTim', 'YouTube', 'Homelab and self-hosting videos.'),
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
 <p class="lede">For people running it at home. Self-hosting, local models, videos, Reddit, and social. New stories are added. Older ones stay, with the newest first. Takeover headlines and “they think it will” predictions stay out.</p>
 <div class="btn-row" style="margin-top: 22px;">
 <a class="btn btn-primary" href="{FEED}">Subscribe with RSS</a>
 <a class="btn btn-ghost" href="https://discord.gg/cZDeqECzX" target="_blank" rel="noopener">Join Discord</a>
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
 <p class="intro">Letters, communities, and homelab projects the edition reads. A broad newsletter only contributes a story when that story is about running something at home.</p>
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
        raise SystemExit('Home Current edition is empty')
    out = ROOT / 'news'
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

# Otaconskeep

[![Site](https://img.shields.io/badge/Site-otaconskeep.github.io-39e6c8.svg)](https://otaconskeep.github.io/)
[![GitHub org](https://img.shields.io/badge/GitHub-Otaconskeep-17202f.svg)](https://github.com/Otaconskeep)
[![Discord](https://img.shields.io/badge/Discord-join-5865F2.svg)](https://discord.gg/cZDeqECzX)

[![Otaconskeep trailer](https://img.youtube.com/vi/vYXsi4ZRStw/maxresdefault.jpg)](https://youtu.be/vYXsi4ZRStw)

**Canonical public site: [https://otaconskeep.github.io/](https://otaconskeep.github.io/)** 
(Cloudflare Workers at `otaconskeep-site.otaconskeep.workers.dev` is a deploy mirror, same tree.)

**[Watch the trailer](https://youtu.be/vYXsi4ZRStw)** · **[Watch the Deck](https://otaconskeep.github.io/keepdesk/#demo)** · **[AI9 video](https://youtu.be/aUiwMACSPBk)** · **[Engineering](https://otaconskeep.github.io/engineering/)**

Public site for Otaconskeep: [Otacon](https://github.com/Otaconskeep/otacons-ai-ecosystem), [KeepRoute](https://github.com/Otaconskeep/KeepRoute), [AI9](https://github.com/Otaconskeep/AI9), Keep Desk, Expansion. Designed & engineered by Antonio G. Garcia.

Plain static HTML/CSS/JS. No build step, no framework, no server-side code.

Install pages offer **dual methods**: one-click Setup and beginner baby steps (prerequisites, copy-paste one-liners, clickable error → fix).

```
index.html Homepage (product cards + What is it? explainers)
engineering/ System Engineering portal
about/ About the Creator
data/products/ Product explainer JSON
data/engineering/ Engineering evidence JSON
otacon/ Otacon Core
keepdesk/ Keep Desk (Watch the Deck)
keeproute/ KeepRoute 1.0
expansion/ Expansion (honest fresh-PC status)
ai9/ AI9 Manga Colorizer
cloud/ Redirect → Keep Desk vs-cloud
premium/ Member HQ
assets/ Shared CSS/JS/media
```

## Canonical URL

Use **https://otaconskeep.github.io/** everywhere (profile blog, READMEs, Discord, SEO).

Deploy paths:
- **GitHub Pages** ← `Otaconskeep/Otaconskeep.github.io` (canonical)
- **Cloudflare Workers** ← this repo (`otaconskeep-site`) as a mirror

## Local preview

```bash
python -m http.server 8000
```

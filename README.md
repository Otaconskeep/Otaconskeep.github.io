# Otaconskeep

[![Otaconskeep trailer](https://img.youtube.com/vi/vYXsi4ZRStw/maxresdefault.jpg)](https://youtu.be/vYXsi4ZRStw)

**[Watch the trailer on YouTube](https://youtu.be/vYXsi4ZRStw)**

Public site for the Otaconskeep project: [Otacon AI Ecosystem](https://github.com/Otaconskeep/otacons-ai-ecosystem)
and [AI9 Manga Colorizer](https://github.com/Otaconskeep/AI9). Designed & Engineered
by Antonio G. Garcia.

**[Watch the AI9 video on YouTube](https://youtu.be/aUiwMACSPBk)** (embedded on [`/ai9/`](https://otaconskeep.com/ai9/))

Plain static HTML/CSS/JS. No build step, no framework, no server-side code.

```
index.html          Homepage
otacon/index.html   Otacon AI Ecosystem detail page
ai9/index.html       AI9 Manga Colorizer detail page
assets/              Shared stylesheet, script, favicon, images
```

## Deploy to Cloudflare Pages

1. Cloudflare dashboard → **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**.
2. Select the `Otaconskeep/otaconskeep-site` repository.
3. Branch: `main`.
4. Framework preset: **None**.
5. Build command: *(leave blank, none needed)*.
6. Build output directory: `/` (repo root).
7. Save and deploy.

That's the entire setup: this is a pure static site, so Cloudflare serves the
files directly with no build step.

## Local preview

```bash
python -m http.server 8000
```

Then open `http://127.0.0.1:8000/`.

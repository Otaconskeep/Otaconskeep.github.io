"""Scrape the public Ollama library into a catalog snapshot plus an evidence file.

This is an independent scraper for the Keep. It reads the same public HTML
pages as the library site (index + each family's /tags page). It does not use
an API key. A failed parse never silently replaces a good snapshot: the writer
uses a temp file and only renames it after both JSON documents are valid.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

SOURCE = "https://ollama.com/library"
USER_AGENT = "OtaconskeepCatalog/1.0 (public library snapshot; +https://otaconskeep.github.io/ollama-catalog/)"
PARSER_ID = "keep-library-html-1"
# Listed download size is not VRAM. A tag "fits" a budget only when that
# listed size is at most this fraction of the budget, and the tag is not cloud.
VRAM_HEADROOM = Decimal("0.75")
VRAM_BUDGETS_GB = (8, 12, 16, 24, 32)

ROOT = Path(__file__).resolve().parent
DEFAULT_MODELS = ROOT / "data" / "models.json"
DEFAULT_EVIDENCE = ROOT / "data" / "evidence.json"


def parse_count(value: str) -> int:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([KMB])?", value.replace(",", "").strip(), re.I)
    if not match:
        raise ValueError(f"Invalid count: {value!r}")
    multiplier = {"K": 1000, "M": 1_000_000, "B": 1_000_000_000}.get((match.group(2) or "").upper(), 1)
    return int(Decimal(match.group(1)) * multiplier)


def magnitude(label: str | None, unit: str) -> float | None:
    """Parse a printed size or context label into a decimal number of `unit`.

    GB labels become gigabytes (1000-based, matching the printed number).
    Context labels like 128K become token counts.
    """
    if not label:
        return None
    text = label.strip()
    if unit == "GB":
        match = re.fullmatch(r"([\d.]+)\s*([KMGT])?B", text, re.I)
        if not match:
            return None
        scale = {"": 1 / 1000, "K": 1 / 1_000_000, "M": 1 / 1000, "G": 1, "T": 1000}
        return float(Decimal(match.group(1)) * Decimal(str(scale[match.group(2).upper() if match.group(2) else ""])))
    if unit == "tokens":
        match = re.fullmatch(r"([\d.]+)\s*([KMB])?", text, re.I)
        if not match:
            return None
        scale = {"": 1, "K": 1000, "M": 1_000_000, "B": 1_000_000_000}
        return float(Decimal(match.group(1)) * scale[(match.group(2) or "").upper()])
    raise ValueError(unit)


def quant_hint(tag: str) -> str:
    """Classify a tag name. Default Ollama tags often omit the quant."""
    text = tag.lower()
    if "cloud" in text:
        return "cloud"
    if re.search(r"mxfp4|nvfp4", text):
        return "mxfp4"
    if re.search(r"bf16|fp16|(?<![a-z])f16(?![a-z])", text):
        return "fp16"
    if re.search(r"q8|iq8|int8", text):
        return "q8"
    if re.search(r"q4|iq4", text):
        return "q4"
    if re.search(r"q[2356]|iq[2356]", text):
        return "other-quant"
    return "unspecified"


def fits_vram(size_gb: float | None, cloud: bool, budget_gb: int) -> bool:
    if cloud or size_gb is None:
        return False
    return Decimal(str(size_gb)) <= Decimal(budget_gb) * VRAM_HEADROOM


def _pagination_present(soup: BeautifulSoup) -> bool:
    if soup.select('a[rel="next"]'):
        return True
    for anchor in soup.select("a[href]"):
        if re.search(r"[?&]page=", anchor["href"]):
            return True
    return False


def parse_library(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    if _pagination_present(soup):
        raise ValueError("Library index paginates; the scraper must follow pages before it can claim a full snapshot.")
    models = []
    for card in soup.select('#repo li a[href^="/library/"]'):
        heading = card.find("h2")
        name = heading.get_text(" ", strip=True) if heading else ""
        paragraphs = card.find_all("p")
        if not name or len(paragraphs) < 2:
            raise ValueError(f"Incomplete model card: {name or 'unknown'}")
        badges = [span.get_text(strip=True) for span in card.select("span.rounded-md")]
        sizes = [badge for badge in badges if re.search(r"\d", badge)]
        stats = paragraphs[-1].find_all("span", recursive=False)

        def stat(label: str) -> str:
            for span in stats:
                if re.search(rf"\b{label}s?\b", span.get_text(" ", strip=True), re.I):
                    value = span.find("span")
                    if value and value.get_text(strip=True):
                        return value.get_text(strip=True)
            raise ValueError(f"Missing {label} for {name}")

        date_text = next((span.get("title") for span in stats if span.get("title")), None)
        if not date_text:
            raise ValueError(f"Missing update date for {name}")
        updated = datetime.strptime(date_text, "%b %d, %Y %I:%M %p UTC").replace(tzinfo=timezone.utc)
        pulls_label = stat("Pull")
        models.append({
            "name": name,
            "url": "https://ollama.com" + card["href"],
            "tagsUrl": "https://ollama.com" + card["href"] + "/tags",
            "description": paragraphs[0].get_text(" ", strip=True),
            "capabilities": [badge for badge in badges if badge not in sizes],
            "sizes": sizes,
            "pulls": parse_count(pulls_label),
            "pullsLabel": pulls_label,
            "tagCountListed": parse_count(stat("Tag")),
            "updatedAt": updated.isoformat().replace("+00:00", "Z"),
        })
    if not models:
        raise ValueError("No model cards found; the library markup may have changed.")
    if len({model["name"] for model in models}) != len(models):
        raise ValueError("Duplicate model names found.")
    return sorted(models, key=lambda model: model["name"])


def parse_tags(html: str, model: dict) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    if _pagination_present(soup):
        raise ValueError(f"Tag page paginates for {model['name']}")
    variants: dict[str, dict] = {}
    prefix = f"/library/{model['name']}:"
    for link in soup.select("a[href]"):
        href = link["href"]
        if not href.startswith(prefix) or not link.select_one(".font-mono"):
            continue
        digest = link.select_one(".font-mono").get_text(strip=True)
        text = link.get_text(" ", strip=True)
        details = [part.strip() for part in text.split(digest, 1)[-1].split("•") if part.strip()]
        name = href.removeprefix("/library/")
        size = next((part for part in details if re.fullmatch(r"[\d.]+\s*[KMGT]?B", part, re.I)), None)
        context = next((part.removesuffix(" context window").strip() for part in details if "context window" in part), None)
        inputs = next((part.removesuffix(" input").strip() for part in details if part.endswith(" input")), None)
        tag = name.split(":", 1)[1]
        # Cloud is a tag, not a family-wide flag. Mixed families list a cloud badge
        # and still publish local weights (gemma4, gpt-oss).
        cloud = "cloud" in tag.lower()
        variants[name] = {
            "name": name,
            "tag": tag,
            "url": "https://ollama.com" + href,
            "pullCommand": f"ollama pull {name}",
            "digest": digest,
            "sizeLabel": size,
            "sizeGB": magnitude(size, "GB"),
            "contextLabel": context,
            "contextTokens": magnitude(context, "tokens"),
            "inputLabel": inputs,
            "cloud": cloud,
            "quantHint": quant_hint(tag),
        }
    if not variants:
        raise ValueError(f"No variants found for {model['name']}")
    count_label = soup.find(string=re.compile(r"^\s*[\d,]+\s+models?\s*$"))
    if count_label:
        expected = int(re.search(r"[\d,]+", count_label).group().replace(",", ""))
        if len(variants) != expected:
            raise ValueError(f"Expected {expected} variants for {model['name']}, found {len(variants)}")
    return list(variants.values())


def fetch(url: str) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=40) as response:
                status = getattr(response, "status", 200)
                body = response.read().decode("utf-8")
                return status, body
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            time.sleep(2 ** attempt)
    raise RuntimeError(f"GET {url} failed: {last_error}")


def _atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def build_evidence(models: list[dict], library_status: int, library_html: str, failures: list[dict], started: str) -> dict:
    variants = [variant for model in models for variant in model.get("variants") or []]
    capability_counts: dict[str, int] = {}
    for model in models:
        for capability in model["capabilities"]:
            capability_counts[capability] = capability_counts.get(capability, 0) + 1
    fits = {}
    for budget in VRAM_BUDGETS_GB:
        matched = [variant["name"] for variant in variants if fits_vram(variant.get("sizeGB"), variant.get("cloud"), budget)]
        fits[str(budget)] = {
            "budgetGb": budget,
            "maxListedSizeGb": float(Decimal(budget) * VRAM_HEADROOM),
            "matchingTags": len(matched),
            "sample": matched[:8],
        }
    return {
        "schemaVersion": 1,
        "catalog": "otaconskeep-ollama-catalog",
        "parser": PARSER_ID,
        "source": SOURCE,
        "userAgent": USER_AGENT,
        "startedAt": started,
        "fetchedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "libraryHttp": library_status,
        "libraryBytes": len(library_html.encode("utf-8")),
        "librarySha256": hashlib.sha256(library_html.encode("utf-8")).hexdigest(),
        "familyCount": len(models),
        "variantCount": len(variants),
        "tagPagesOk": sum(1 for model in models if model.get("variants")),
        "tagPageFailures": failures,
        "capabilityFamilyCounts": capability_counts,
        "rules": {
            "vramFit": (
                "A tag fits a VRAM budget when it is not a cloud tag and its listed "
                f"download size is at most {VRAM_HEADROOM} of that budget. "
                "Download size is the number printed on the tag page. It is not a measured VRAM figure. "
                "KV cache and runtime overhead are extra, so this is a shortlist, not a guarantee."
            ),
            "headroom": float(VRAM_HEADROOM),
            "sizeParse": "Printed labels use decimal K/M/G/T (1000). 9.3GB is stored as 9.3, not as measured bytes.",
            "quantHint": "Parsed from the tag name only. Most default tags omit quantization and are marked unspecified.",
            "pulls": "Pull counts are the abbreviated figures on the library card (1.2M means 1200000), not an exact counter.",
            "pagination": "The index and tag pages had no next-page link. If Ollama adds paging, the parser refuses the snapshot.",
        },
        "vramFit": fits,
        "examples": {
            "firstFamily": models[0]["name"] if models else None,
            "toolsFamilies": capability_counts.get("tools", 0),
            "visionFamilies": capability_counts.get("vision", 0),
            "thinkingFamilies": capability_counts.get("thinking", 0),
            "embeddingFamilies": capability_counts.get("embedding", 0),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", type=Path, default=DEFAULT_MODELS)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--limit", type=int, default=0, help="Scrape only the first N families (debug).")
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    library_status, library_html = fetch(SOURCE)
    models = parse_library(library_html)
    if args.limit:
        models = models[: args.limit]
    failures: list[dict] = []
    for index, model in enumerate(models, 1):
        print(f"[{index}/{len(models)}] {model['tagsUrl']}", flush=True)
        time.sleep(args.sleep)
        try:
            status, html = fetch(model["tagsUrl"])
            model["variants"] = parse_tags(html, model)
            model["tagPageHttp"] = status
        except (OSError, ValueError, RuntimeError) as error:
            failures.append({"name": model["name"], "url": model["tagsUrl"], "error": str(error)})
            model["variants"] = []
            model["tagPageHttp"] = 0
            print(f"  FAIL {error}", flush=True)
    evidence = build_evidence(models, library_status, library_html, failures, started)
    snapshot = {
        "schemaVersion": 1,
        "source": SOURCE,
        "fetchedAt": evidence["fetchedAt"],
        "parser": PARSER_ID,
        "count": len(models),
        "variantCount": evidence["variantCount"],
        "models": models,
    }
    _atomic_json(args.models, snapshot)
    _atomic_json(args.evidence, evidence)
    print(f"Saved {len(models)} families / {evidence['variantCount']} tags")
    print(f"Evidence {args.evidence}")
    if failures:
        raise SystemExit(f"{len(failures)} tag pages failed")


if __name__ == "__main__":
    main()

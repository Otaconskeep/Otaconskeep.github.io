#!/usr/bin/env python3
"""Refresh Lesson 00 background notes.

Pulls the public Linus Tech Tips YouTube feed and writes a small JSON file
the wizard reads. Prices stay as source links. This script does not invent
a dollar amount.
"""
from __future__ import annotations

import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

FEED = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
ATOM = "{http://www.w3.org/2005/Atom}"
OUT = Path(__file__).resolve().parents[1] / "modules" / "00-pick-your-lab" / "lab-notes.json"

PRICES = {
    "note": "Open the source for the number. This file records where to look, not a sale price.",
    "sources": [
        {"name": "Jawa", "href": "https://www.jawa.gg/", "detail": "Used graphics cards and used whole PCs."},
        {"name": "PCPartPicker", "href": "https://pcpartpicker.com/", "detail": "New parts, a running total, and their compatibility notes."},
    ],
    "parts": [
        {
            "name": "Graphics card",
            "look": "8 GB is the start for a small chat model. 12 GB is the calmer start for pictures.",
            "jawa": "https://www.jawa.gg/",
            "pcpp": "https://pcpartpicker.com/products/video-card/",
        },
        {
            "name": "Memory",
            "look": "Match DDR4 or DDR5 to the motherboard. 32 GB is the calmer chat desk.",
            "pcpp": "https://pcpartpicker.com/products/memory/",
        },
        {
            "name": "Boot SSD",
            "look": "NVMe for the system. Check the slot. M.2 is only the shape.",
            "pcpp": "https://pcpartpicker.com/products/internal-hard-drive/",
        },
    ],
    "builds": [
        {
            "name": "First desk",
            "for": "School, the web, and older games.",
            "parts": "16 GB of memory, a 1 TB SSD, and either no extra card or a used 8 GB card.",
            "check": "Match the socket and the memory type in the checker, then price the list on PCPartPicker.",
        },
        {
            "name": "Chat at home",
            "for": "A 7B or 8B model.",
            "parts": "32 GB of memory and a 12 GB card. One heavy job at a time.",
            "check": "Price the card on Jawa if used, or PCPartPicker if new.",
        },
        {
            "name": "Movie shelf",
            "for": "Plex or Jellyfin.",
            "parts": "A small SSD for the system and CMR hard drives for the files.",
            "check": "Read the disk datasheet for CMR. Do not buy a Purple drive for this.",
        },
    ],
}


def videos(limit: int = 3) -> list[dict]:
    request = urllib.request.Request(FEED, headers={"User-Agent": "otaconskeep-lab-notes"})
    with urllib.request.urlopen(request, timeout=20) as response:
        root = ET.fromstring(response.read())
    found = []
    for entry in root.findall(f"{ATOM}entry"):
        link = ""
        for node in entry.findall(f"{ATOM}link"):
            if node.attrib.get("rel") == "alternate":
                link = node.attrib.get("href", "")
        if "/shorts/" in link:
            continue
        title = (entry.findtext(f"{ATOM}title") or "").strip()
        published = (entry.findtext(f"{ATOM}published") or "")[:10]
        if title and link:
            found.append({"title": title, "href": link, "date": published})
        if len(found) >= limit:
            break
    return found


def main() -> None:
    payload = {
        "checked": datetime.now(timezone.utc).date().isoformat(),
        "ltt_source": FEED,
        "ltt": videos(),
        "prices": PRICES,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(payload['ltt'])} videos)")


if __name__ == "__main__":
    main()

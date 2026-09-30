"""Parser checks against the markup shape of ollama.com/library."""

import json
import tempfile
import unittest
from pathlib import Path

from scrape import fits_vram, magnitude, parse_count, parse_library, parse_tags, quant_hint


CARD = """<div id="repo"><ul><li><a href="/library/example">
<h2><span>example</span></h2>
<p>A model &amp; description.</p>
<span class="rounded-md">tools</span>
<span class="rounded-md">7b</span>
<p>
<span><span>1.2M</span><span>Pulls</span></span>
<span><span>1</span><span>Tag</span></span>
<span title="Mar 18, 2026 6:05 PM UTC"><span>Updated</span></span>
</p></a></li></ul></div>"""


class ScrapeTests(unittest.TestCase):
    def test_library_card(self):
        model = parse_library(CARD)[0]
        self.assertEqual(model["name"], "example")
        self.assertEqual(model["capabilities"], ["tools"])
        self.assertEqual(model["sizes"], ["7b"])
        self.assertEqual(model["pulls"], 1_200_000)
        self.assertEqual(model["tagCountListed"], 1)
        self.assertEqual(model["description"], "A model & description.")
        self.assertEqual(model["updatedAt"], "2026-03-18T18:05:00Z")

    def test_rejects_pagination_and_empty(self):
        with self.assertRaises(ValueError):
            parse_library("Blocked")
        with self.assertRaises(ValueError):
            parse_library(CARD + '<a rel="next" href="/library?page=2">Next</a>')

    def test_tags(self):
        html = """<p>1 model</p>
        <a href="/library/example:7b">example:7b <span class="font-mono">abc123</span>
        • 4.9GB • 128K context window • Text input • yesterday</a>
        <a href="/library/example:7b">example:7b</a>"""
        variants = parse_tags(html, {"name": "example", "capabilities": ["tools"]})
        self.assertEqual(len(variants), 1)
        self.assertEqual(variants[0]["pullCommand"], "ollama pull example:7b")
        self.assertEqual(variants[0]["sizeGB"], 4.9)
        self.assertEqual(variants[0]["contextTokens"], 128000)
        self.assertFalse(variants[0]["cloud"])
        with self.assertRaises(ValueError):
            parse_tags(html.replace("1 model", "2 models"), {"name": "example", "capabilities": []})

    def test_counts_and_fit_rule(self):
        self.assertEqual(parse_count("119.8M"), 119_800_000)
        self.assertEqual(magnitude("523MB", "GB"), 0.523)
        self.assertEqual(quant_hint("14b-q4_K_M"), "q4")
        self.assertEqual(quant_hint("14b"), "unspecified")
        self.assertTrue(fits_vram(12, False, 16))
        self.assertFalse(fits_vram(12.1, False, 16))
        self.assertFalse(fits_vram(4, True, 16))

    def test_search_form_is_not_pagination(self):
        html = CARD + '<form hx-get="/library" hx-trigger="submit"></form>'
        self.assertEqual(parse_library(html)[0]["name"], "example")

    def test_atomic_roundtrip_via_main_helpers(self):
        from scrape import build_evidence

        models = parse_library(CARD)
        models[0]["variants"] = parse_tags(
            """<p>1 model</p><a href="/library/example:7b">example:7b
            <span class="font-mono">abc</span> • 4.9GB • 8K context window • Text input</a>""",
            models[0],
        )
        evidence = build_evidence(models, 200, CARD, [], "2026-09-30T00:00:00Z")
        self.assertEqual(evidence["familyCount"], 1)
        self.assertEqual(evidence["vramFit"]["16"]["matchingTags"], 1)
        self.assertEqual(evidence["libraryHttp"], 200)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(evidence), encoding="utf-8")
            self.assertEqual(json.loads(path.read_text())["parser"], "keep-library-html-1")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Tests for product cards + What is it? explainers."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / "index.html"
DATA = ROOT / "data" / "products" / "explainers.json"
JS = ROOT / "assets" / "product-explainers.js"
CSS = ROOT / "assets" / "product-explainers.css"


class ProductExplainerTests(unittest.TestCase):
    def setUp(self):
        self.home = HOME.read_text(encoding="utf-8")
        self.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_assets_exist(self):
        self.assertTrue(DATA.is_file())
        self.assertTrue(JS.is_file())
        self.assertTrue(CSS.is_file())
        self.assertIn("product-explainers.css", self.home)
        self.assertIn("product-explainers.js", self.home)

    def test_every_product_has_what_is_it(self):
        for pid in ("lite", "ai9", "expansion", "keepdesk", "keeproute"):
            self.assertIn(f'data-explainer="{pid}"', self.home)
            self.assertIn(f'data-product-id="{pid}"', self.home)

    def test_card_copy_not_terse_jargon_only(self):
        self.assertNotIn("Grok Bot genre", self.home)
        self.assertNotIn("BMC · 91.6%", self.home)
        self.assertNotIn("Command Deck cinema", self.home)
        self.assertIn("What is it?", self.home)
        self.assertIn("Run your own persistent AI agents", self.home)

    def test_install_links_preserved(self):
        self.assertIn('href="#install-otacon"', self.home)
        self.assertIn('href="#install-ai9"', self.home)
        self.assertIn('href="/keeproute/"', self.home)
        self.assertIn("youtu.be/OitYjPlbTng", self.home)
        self.assertIn("youtu.be/aUiwMACSPBk", self.home)

    def test_data_model_complete(self):
        ids = {p["id"] for p in self.data["products"]}
        self.assertEqual(ids, {"lite", "ai9", "expansion", "keepdesk", "keeproute"})
        for p in self.data["products"]:
            self.assertIn("quick", p)
            self.assertIn("technical", p)
            self.assertIn("headline", p["quick"])
            self.assertIn("systemRole", p["technical"])
            self.assertTrue(p["quick"].get("points"))
            self.assertIn("engineeringLinks", p["technical"])

    def test_keeproute_distinguishes_omniroute(self):
        kr = next(p for p in self.data["products"] if p["id"] == "keeproute")
        self.assertIn("omniVsKeep", kr["technical"])
        blob = json.dumps(kr).lower()
        self.assertIn("omniroute routes", blob)
        self.assertIn("keeproute owns", blob.replace("’", "'"))

    def test_ai9_independent_of_core(self):
        ai9 = next(p for p in self.data["products"] if p["id"] == "ai9")
        self.assertIn("does not require", ai9["quick"]["relationship"].lower())

    def test_expansion_roster_public_names(self):
        ex = next(p for p in self.data["products"] if p["id"] == "expansion")
        comps = " ".join(ex["technical"]["components"])
        for name in ("Aria", "Vector", "Ledger", "Muse", "Sentry"):
            self.assertIn(name, comps)
        self.assertIn("capabilityStatus", ex["technical"])

    def test_deep_link_hashes(self):
        hashes = {p["hash"] for p in self.data["products"]}
        self.assertEqual(
            hashes,
            {
                "lite-explainer",
                "ai9-explainer",
                "expansion-explainer",
                "keepdesk-explainer",
                "keeproute-explainer",
            },
        )
        js = JS.read_text(encoding="utf-8")
        self.assertIn("hashchange", js)
        self.assertIn("aria-modal", js)
        self.assertIn("Escape", js)

    def test_no_ataconskeep(self):
        self.assertNotIn("AtaconsKeep", self.home)
        self.assertNotIn("AtaconsKeep", DATA.read_text(encoding="utf-8"))

    def test_comparison_present_in_data(self):
        self.assertGreaterEqual(len(self.data["comparison"]), 5)

    def test_no_private_ips_in_product_data(self):
        blob = DATA.read_text(encoding="utf-8")
        self.assertNotRegex(blob, r"\b192\.168\.\d+\.\d+\b")


if __name__ == "__main__":
    unittest.main()

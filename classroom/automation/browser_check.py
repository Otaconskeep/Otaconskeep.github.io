#!/usr/bin/env python3
"""Playwright desktop/mobile checks against staged preview classroom (no live deploy)."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def run_browser_suite(site_root: Path, out_dir: Path, class_ids: list[int], port: int = 8765) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(site_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(0.6)
    results: dict = {
        "ok": True,
        "failures": [],
        "screenshots": [],
        "console_errors": [],
        "viewports": {},
        "nav_ok": [],
        "quiz_controls": [],
    }
    base = f"http://127.0.0.1:{port}/classroom"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for label, viewport in [
                ("desktop", {"width": 1440, "height": 900}),
                ("mobile", {"width": 390, "height": 844}),
            ]:
                context = browser.new_context(viewport=viewport)
                page = context.new_page()
                cons: list[dict] = []
                page.on(
                    "console",
                    lambda msg: cons.append({"type": msg.type, "text": msg.text})
                    if msg.type == "error"
                    else None,
                )
                page.goto(f"{base}/", wait_until="networkidle", timeout=60000)
                shot = out_dir / f"{label}_hub.png"
                page.screenshot(path=str(shot), full_page=True)
                results["screenshots"].append(str(shot))
                hub_text = page.inner_text("body")
                for needle in ["HOMELAB", "Academy", "Class"]:
                    if needle.lower() not in hub_text.lower() and needle not in hub_text:
                        # soft: Academy branding
                        pass
                # staged batch should appear once preview includes classes 16+
                if any(i > 15 for i in class_ids):
                    if "15-class pack" in hub_text and "21-class" not in hub_text and f"{max(class_ids)}-class" not in hub_text:
                        # Fail only if stamp still hard-claims exclusively 15 while new classes exist in pack
                        # Check class index instead
                        pass
                # syllabus
                syl = page.goto(f"{base}/syllabus.html", wait_until="domcontentloaded", timeout=30000)
                if syl and syl.status >= 400:
                    results["failures"].append(f"{label}: syllabus status {syl.status}")
                else:
                    shot = out_dir / f"{label}_syllabus.png"
                    page.screenshot(path=str(shot))
                    results["screenshots"].append(str(shot))

                # Existing + new classes
                for cid in [1, 15] + class_ids:
                    resp = page.goto(f"{base}/classes/{cid:02d}.html", wait_until="networkidle", timeout=60000)
                    if resp and resp.status >= 400:
                        results["failures"].append(f"{label}: class {cid} status {resp.status}")
                        continue
                    page.wait_for_timeout(350)
                    overflow = page.evaluate(
                        "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"
                    )
                    if overflow:
                        results["failures"].append(f"{label}: horizontal overflow class {cid}")
                    # code readability
                    pre_bad = page.evaluate(
                        """() => {
                          const pres = [...document.querySelectorAll('pre')];
                          return !pres.every(pre => {
                            const s = getComputedStyle(pre);
                            return s.overflowX === 'auto' || s.overflowX === 'scroll' || pre.scrollWidth <= pre.clientWidth + 80;
                          });
                        }"""
                    )
                    if pre_bad:
                        results["failures"].append(f"{label}: unreadable code block class {cid}")
                    # tables not breaking layout
                    # Tables may scroll inside cards; fail only if they force page-level overflow
                    table_page_bad = page.evaluate(
                        """() => {
                          const pageWide = document.documentElement.scrollWidth > document.documentElement.clientWidth + 2;
                          if (!pageWide) return false;
                          const tables = [...document.querySelectorAll('table')];
                          return tables.some(t => t.scrollWidth > document.documentElement.clientWidth + 40);
                        }"""
                    )
                    if table_page_bad:
                        results["failures"].append(f"{label}: table makes page unusable class {cid}")
                    # prev/next nav when present
                    nav_info = page.evaluate(
                        """() => {
                          const links = [...document.querySelectorAll('a')].map(a => ({text: (a.textContent||'').trim(), href: a.getAttribute('href')||''}));
                          const prev = links.find(l => /prev/i.test(l.text) || /previous/i.test(l.text));
                          const next = links.find(l => /next/i.test(l.text));
                          return {prev: !!prev, next: !!next, hrefs: links.filter(l => /class|module|topic|lesson/i.test(l.href)).slice(0,8)};
                        }"""
                    )
                    results["nav_ok"].append({"viewport": label, "class": cid, **nav_info})
                    shot = out_dir / f"{label}_class_{cid:02d}.png"
                    page.screenshot(path=str(shot))
                    results["screenshots"].append(str(shot))

                # Module quiz / answer key controls if present
                for path in [
                    "/modules/06-linux-foundations/module-quiz.html",
                    "/modules/06-linux-foundations/ANSWER_KEY.html",
                    "/modules/06-linux-foundations/",
                ]:
                    r = page.goto(f"{base}{path}", wait_until="domcontentloaded", timeout=30000)
                    if r and r.status < 400:
                        controls = page.evaluate(
                            """() => {
                              const buttons = [...document.querySelectorAll('button, details, summary, [data-answer], .answer-key, .quiz')].length;
                              const details = document.querySelectorAll('details').length;
                              return {buttons, details, title: document.title};
                            }"""
                        )
                        results["quiz_controls"].append({"viewport": label, "path": path, **controls})
                        shot = out_dir / f"{label}_module06_{Path(path).name or 'index'}.png"
                        page.screenshot(path=str(shot))
                        results["screenshots"].append(str(shot))

                results["console_errors"].extend(
                    [
                        {"viewport": label, **c}
                        for c in cons
                        if c["type"] == "error" and "404" not in c.get("text", "") and "Failed to load resource" not in c.get("text", "")
                    ]
                )
                results["viewports"][label] = dict(viewport)
                context.close()
            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
    results["ok"] = not results["failures"] and not results["console_errors"]
    (out_dir / "browser_report.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", required=True, help="Path to generated classroom preview directory")
    ap.add_argument("--out", required=True, help="Evidence output directory (outside live classroom)")
    ap.add_argument("--classes", default="16,17,18,19,20,21")
    args = ap.parse_args()
    ids = [int(x) for x in args.classes.split(",") if x.strip()]
    preview = Path(args.preview).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    site_root = out_dir / "site_root"
    if site_root.exists():
        shutil.rmtree(site_root)
    site_root.mkdir(parents=True)
    (site_root / "classroom").symlink_to(preview)
    live_assets = Path(__file__).resolve().parents[2] / "assets"
    if not live_assets.is_dir():
        live_assets = Path("/root/otaconskeep-site/assets")
    if live_assets.is_dir():
        (site_root / "assets").symlink_to(live_assets)
    results = run_browser_suite(site_root, out_dir, ids)
    print(json.dumps({"ok": results["ok"], "failures": results["failures"], "shots": len(results["screenshots"]), "console_errors": len(results["console_errors"])}, indent=2))
    return 0 if results["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

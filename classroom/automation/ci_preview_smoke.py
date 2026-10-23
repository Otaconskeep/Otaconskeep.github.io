#!/usr/bin/env python3
"""CI preview smoke: serve repo root, screenshot homepage + classroom welcome (desktop/mobile)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--base-dir", default=".")
    ap.add_argument("--port", type=int, default=8768)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    root = Path(args.base_dir).resolve()

    from playwright.sync_api import sync_playwright

    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(args.port), "--bind", "127.0.0.1"],
        cwd=str(root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(0.6)
    base = f"http://127.0.0.1:{args.port}"
    report: dict = {"ok": True, "failures": [], "screenshots": []}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for label, vp in [("desktop", {"width": 1440, "height": 900}), ("mobile", {"width": 390, "height": 844})]:
                ctx = browser.new_context(viewport=vp)
                page = ctx.new_page()
                for path, name in [("/", "home"), ("/classroom/welcome.html", "welcome")]:
                    resp = page.goto(f"{base}{path}", wait_until="networkidle", timeout=60000)
                    if resp and resp.status >= 400:
                        report["failures"].append(f"{label}:{name} status {resp.status}")
                        continue
                    body = page.inner_text("body")
                    if name == "welcome":
                        if "discord.gg" in body.lower():
                            report["failures"].append(f"{label}: welcome embeds discord invite text")
                        if "log in" in body.lower() or "sign in" in body.lower():
                            report["failures"].append(f"{label}: welcome requires login")
                    if "Otaconskeep" not in body and "OtaconsKeep" not in body:
                        report["failures"].append(f"{label}:{name} missing brand")
                    shot = out / f"{label}_{name}.png"
                    page.screenshot(path=str(shot), full_page=True)
                    report["screenshots"].append(str(shot))
                ctx.close()
            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
    report["ok"] = not report["failures"]
    (out / "smoke_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

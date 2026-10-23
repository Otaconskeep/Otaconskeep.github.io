#!/usr/bin/env python3
"""Breakthrough news evaluator — fail closed; News Lab only; never touches core numbering."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import JsonLogger, load_config, new_run_id, publication_lock, utc_now, atomic_write_json
from lib.content_security import scan_text

# Conservative allowlist of primary sources (fetched only if network allowed)
PRIMARY_FEEDS = [
    "https://www.freedesktop.org/blog/",
    "https://www.docker.com/blog/",
    "https://ollama.com/blog",
]

# Topics that may qualify (AI / self-hosted / homelab). Marketing fluff does not.
_TOPIC_RE = re.compile(
    r"\b(self-?host|homelab|ollama|local\s*llm|open-?source\s*ai|kubernetes|docker|podman|"
    r"proxmox|truenas|wireguard|tailscale|systemd|journald)\b",
    re.I,
)


def load_rejects(cfg) -> set[str]:
    path = cfg.news_reject_path
    seen: set[str] = set()
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                seen.add(json.loads(line).get("fingerprint", ""))
            except Exception:
                continue
    return seen


def append_reject(cfg, fingerprint: str, reason: str, title: str) -> None:
    cfg.news_reject_path.parent.mkdir(parents=True, exist_ok=True)
    with cfg.news_reject_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": utc_now(), "fingerprint": fingerprint, "reason": reason, "title": title}) + "\n")


def news_lab_dir(cfg) -> Path:
    """Separate dated News Lab / Breaking Lab area — not numbered core classes."""
    return cfg.classroom_dir / "news-lab"


def write_noop_record(cfg, report: dict) -> Path:
    # Prefer state_dir for machine records so git tree stays clean; HTML area is separate.
    d = cfg.state_dir / "news_lab_runs"
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"noop_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    atomic_write_json(path, report)
    return path


def qualify_candidate(item: dict) -> tuple[bool, str]:
    """Require primary source URL, publication date, and practical relevance."""
    title = str(item.get("title") or "")
    url = str(item.get("url") or "")
    published = str(item.get("published") or "")
    summary = str(item.get("summary") or "")
    if not url.startswith("https://"):
        return False, "missing_primary_https_url"
    if not published:
        return False, "missing_publication_date"
    blob = f"{title}\n{summary}"
    if not _TOPIC_RE.search(blob):
        return False, "not_ai_selfhost_or_homelab"
    if not item.get("practical_relevance"):
        return False, "missing_practical_relevance"
    # Never invent significance — caller must set significant=True from verified evidence
    if not item.get("significant"):
        return False, "not_marked_significant"
    sec = scan_text(blob, path="news_candidate")
    if sec:
        return False, "security_gate:" + ",".join(sec)
    return True, "ok"


def evaluate_candidates(cfg, logger: JsonLogger, *, injected: list[dict] | None = None) -> dict:
    """Without inventing news: if no verified primary candidate, return clean no-op."""
    rejects = load_rejects(cfg)
    candidates = []
    if injected is not None:
        for item in injected:
            fp = str(item.get("fingerprint") or f"inject:{item.get('url')}")
            if fp in rejects:
                candidates.append({"url": item.get("url"), "status": "rejected", "reason": "duplicate"})
                continue
            ok, reason = qualify_candidate(item)
            if ok:
                # Still do not auto-publish into core; stage News Lab draft only when activated.
                return {
                    "ok": True,
                    "bonus_lesson": {
                        "area": "news-lab",
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "published": item.get("published"),
                        "practical_relevance": item.get("practical_relevance"),
                    },
                    "message": "Qualifying news candidate (News Lab only; core numbering untouched).",
                    "candidates": candidates + [{"url": item.get("url"), "status": "qualified"}],
                    "core_class_ids_touched": [],
                }
            append_reject(cfg, fp, reason, str(item.get("title") or ""))
            candidates.append({"url": item.get("url"), "status": "rejected", "reason": reason})
    else:
        import urllib.request

        for url in PRIMARY_FEEDS:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "otaconskeep-classroom-news/1.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    body = resp.read(8000).decode("utf-8", errors="replace")
                fp = f"feed:{url}:{hash(body) & 0xffffffff}"
                if fp in rejects:
                    continue
                # Do not auto-claim breakthroughs from HTML scraping alone.
                append_reject(cfg, fp, "insufficient_primary_verification_for_auto_bonus", url)
                candidates.append(
                    {"url": url, "status": "rejected", "reason": "insufficient_primary_verification_for_auto_bonus"}
                )
            except Exception as e:
                candidates.append({"url": url, "status": "rejected", "reason": f"fetch_failed:{type(e).__name__}"})
    logger.event("news_eval", candidates=len(candidates), bonus=0)
    report = {
        "ok": True,
        "bonus_lesson": None,
        "message": "No qualifying breakthrough.",
        "candidates": candidates,
        "core_class_ids_touched": [],
        "area": "news-lab",
    }
    write_noop_record(cfg, report)
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write report JSON")
    ap.add_argument("--inject-json", help="test-only: path to candidate list JSON")
    args = ap.parse_args()
    cfg = load_config()
    run_id = new_run_id("news")
    try:
        cfg.log_dir.mkdir(parents=True, exist_ok=True)
        cfg.state_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        base = Path("/tmp/otaconskeep-classroom-dryrun")
        cfg.log_dir = base / "logs"
        cfg.state_dir = base / "state"
        cfg.lock_file = base / "classroom.publish.lock"
        cfg.classroom_dir = Path(os.environ.get("CLASSROOM_SITE_REPO", "/root/otaconskeep-site")) / "classroom"
        cfg.log_dir.mkdir(parents=True, exist_ok=True)
        cfg.state_dir.mkdir(parents=True, exist_ok=True)

    logger = JsonLogger(cfg.log_dir / f"{run_id}.jsonl", run_id, "news")
    try:
        with publication_lock(cfg, logger):
            if not cfg.news_enabled:
                report = {"message": "News disabled", "bonus_lesson": None, "core_class_ids_touched": []}
            else:
                injected = None
                if args.inject_json:
                    injected = json.loads(Path(args.inject_json).read_text(encoding="utf-8"))
                report = evaluate_candidates(cfg, logger, injected=injected)
            if args.out:
                Path(args.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report, indent=2))
            return 0
    except RuntimeError as e:
        if "lock busy" in str(e):
            print(json.dumps({"message": "lock busy", "bonus_lesson": None, "core_class_ids_touched": []}))
            return 75
        raise
    finally:
        logger.close()


if __name__ == "__main__":
    raise SystemExit(main())

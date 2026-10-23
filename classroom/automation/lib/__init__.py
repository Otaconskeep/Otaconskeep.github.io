#!/usr/bin/env python3
"""Shared paths, locking, logging, config for classroom automation."""
from __future__ import annotations

import json
import os
import re
import socket
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from filelock import FileLock, Timeout

AUTOMATION_ROOT = Path(__file__).resolve().parents[1]
SITE_DEFAULT = AUTOMATION_ROOT.parents[1]  # .../otaconskeep-site
SCHEMA_VERSION = "1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_dotenv_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


@dataclass
class Config:
    site_repo: Path
    pack_rel: str
    upstream_repo: Path | None
    state_dir: Path
    log_dir: Path
    staging_dir: Path
    artifact_dir: Path
    lock_file: Path
    omni_base: str
    omni_key: str
    writer_model: str
    critic_model: str
    weak_prefixes: list[str]
    allow_weak: bool
    generator_backend: str
    publish_mode: str
    allow_direct_main: bool
    git_remote: str
    git_base: str
    dry_run: bool
    news_enabled: bool
    notify_backend: str
    discord_webhook: str
    notify_script: Path | None
    job_timeout: int
    llm_timeout: int
    max_repair: int
    critic_min: int
    artifact_retention_days: int
    staging_retention_days: int

    @property
    def pack_dir(self) -> Path:
        return self.site_repo / self.pack_rel

    @property
    def classroom_dir(self) -> Path:
        return self.site_repo / "classroom"

    @property
    def automation_dir(self) -> Path:
        return AUTOMATION_ROOT

    @property
    def roadmap_path(self) -> Path:
        return AUTOMATION_ROOT / "roadmap.yaml"

    @property
    def schema_path(self) -> Path:
        return AUTOMATION_ROOT / "lesson-schema.json"

    @property
    def manifest_path(self) -> Path:
        return self.state_dir / "curriculum_manifest.json"

    @property
    def news_reject_path(self) -> Path:
        return self.state_dir / "news_rejects.jsonl"


def load_config(env_file: str | Path | None = None) -> Config:
    env: dict[str, str] = {}
    candidate = Path(env_file) if env_file else Path("/etc/otaconskeep-classroom.env")
    env.update(load_dotenv_file(candidate))
    # process env overrides file
    for k, v in os.environ.items():
        if k.startswith("CLASSROOM_") or k.startswith("OMNIROUTE_") or k in {
            "WRITER_MODEL",
            "CRITIC_MODEL",
            "GENERATOR_BACKEND",
            "PUBLISH_MODE",
            "ALLOW_DIRECT_MAIN",
            "ALLOW_WEAK_MODELS",
            "DRY_RUN",
            "DISCORD_WEBHOOK_URL",
            "NOTIFY_BACKEND",
            "NEWS_ENABLED",
        }:
            env[k] = v

    def g(key: str, default: str = "") -> str:
        return env.get(key, default)

    site = Path(g("CLASSROOM_SITE_REPO", str(SITE_DEFAULT))).resolve()
    upstream = g("CLASSROOM_UPSTREAM_REPO", "/root/Classroom")
    notify = g("OTACONSKEEP_NOTIFY_SCRIPT", "/opt/otaconskeep_notifications/media_announcement.py")
    return Config(
        site_repo=site,
        pack_rel=g("CLASSROOM_PACK_REL", "classroom/pack"),
        upstream_repo=Path(upstream) if upstream else None,
        state_dir=Path(g("CLASSROOM_STATE_DIR", "/var/lib/otaconskeep-classroom/state")),
        log_dir=Path(g("CLASSROOM_LOG_DIR", "/var/log/otaconskeep-classroom")),
        staging_dir=Path(g("CLASSROOM_STAGING_DIR", "/var/lib/otaconskeep-classroom/staging")),
        artifact_dir=Path(g("CLASSROOM_ARTIFACT_DIR", "/var/lib/otaconskeep-classroom/artifacts")),
        lock_file=Path(g("CLASSROOM_LOCK_FILE", "/var/lib/otaconskeep-classroom/classroom.publish.lock")),
        omni_base=g("OMNIROUTE_BASE_URL", "http://127.0.0.1:20128/v1").rstrip("/"),
        omni_key=g("OMNIROUTE_API_KEY", os.environ.get("OMNIROUTE_API_KEY", "")),
        writer_model=g("WRITER_MODEL", "auto/pro-reasoning"),
        critic_model=g("CRITIC_MODEL", "auto/best-reasoning"),
        weak_prefixes=[p.strip() for p in g("WEAK_MODEL_PREFIXES", "ollama-local/,ollama/,llama3.2,granite3").split(",") if p.strip()],
        allow_weak=g("ALLOW_WEAK_MODELS", "0") in {"1", "true", "TRUE", "yes"},
        generator_backend=g("GENERATOR_BACKEND", "llm"),
        publish_mode=g("PUBLISH_MODE", "pr"),
        allow_direct_main=g("ALLOW_DIRECT_MAIN", "0") in {"1", "true", "TRUE"},
        git_remote=g("GIT_REMOTE", "origin"),
        git_base=g("GIT_BASE_BRANCH", "main"),
        dry_run=g("DRY_RUN", "1") in {"1", "true", "TRUE", "yes"},
        news_enabled=g("NEWS_ENABLED", "1") in {"1", "true", "TRUE", "yes"},
        notify_backend=g("NOTIFY_BACKEND", "otaconskeep"),
        discord_webhook=g("DISCORD_WEBHOOK_URL", ""),
        notify_script=Path(notify) if notify else None,
        job_timeout=int(g("JOB_TIMEOUT_SEC", "7200")),
        llm_timeout=int(g("LLM_TIMEOUT_SEC", "300")),
        max_repair=int(g("LLM_MAX_REPAIR_ATTEMPTS", "2")),
        critic_min=int(g("CRITIC_MIN_SCORE", "85")),
        artifact_retention_days=int(g("ARTIFACT_RETENTION_DAYS", "45")),
        staging_retention_days=int(g("STAGING_RETENTION_DAYS", "14")),
    )


class JsonLogger:
    def __init__(self, path: Path, run_id: str, batch_type: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.run_id = run_id
        self.batch_type = batch_type
        self._fp = path.open("a", encoding="utf-8")

    def event(self, stage: str, **fields: Any) -> None:
        rec = {
            "ts": utc_now(),
            "run_id": self.run_id,
            "batch_type": self.batch_type,
            "host": socket.gethostname(),
            "stage": stage,
            **fields,
        }
        # never log secrets
        blob = json.dumps(rec, ensure_ascii=False, default=str)
        blob = redact_secrets(blob)
        self._fp.write(blob + "\n")
        self._fp.flush()
        print(f"[{stage}] {fields.get('message', fields.get('disposition', ''))}".strip())

    def close(self) -> None:
        self._fp.close()


_SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|token|password|secret|webhook|bearer)\s*[:=]\s*['\"]?([^\s'\"]+)"
)


def redact_secrets(text: str) -> str:
    text = _SECRET_RE.sub(r"\1=***REDACTED***", text)
    text = re.sub(r"gho_[A-Za-z0-9]+", "gho_***", text)
    text = re.sub(r"ghp_[A-Za-z0-9]+", "ghp_***", text)
    text = re.sub(r"https://discord.com/api/webhooks/\S+", "https://discord.com/api/webhooks/***REDACTED***", text)
    return text


def new_run_id(prefix: str = "run") -> str:
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"


@contextmanager
def publication_lock(cfg: Config, logger: JsonLogger | None = None) -> Iterator[None]:
    """Global lock shared by AM, late, and news jobs (one publisher at a time)."""
    from lib.publish_control import clear_lock_owner, recover_stale_lock, write_lock_owner

    cfg.lock_file.parent.mkdir(parents=True, exist_ok=True)
    recover_stale_lock(cfg, logger)
    # Non-blocking: concurrent AM/late/news starts must exit cleanly, not queue.
    lock = FileLock(str(cfg.lock_file), timeout=0)
    try:
        lock.acquire()
    except Timeout as e:
        if logger:
            logger.event("lock_busy", message="Another classroom publication job holds the lock", disposition="exit_clean")
        raise RuntimeError("publication lock busy") from e
    try:
        write_lock_owner(cfg)
        if logger:
            logger.event("lock_acquired", lock=str(cfg.lock_file))
        yield
    finally:
        clear_lock_owner(cfg)
        lock.release()
        if logger:
            logger.event("lock_released")


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def slugify(title: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", title.strip()).strip("_").upper()
    return s[:80] or "LESSON"

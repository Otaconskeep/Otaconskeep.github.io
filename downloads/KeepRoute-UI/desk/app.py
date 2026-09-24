#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KeepRoute: public OtaconsKeep field UI over OmniRoute.

Cool cinematic GUI in front. OmniRoute picks the best backend (or a
local LLM / named specialist). Optional real CLIs stay available as
power-user paths. No lab LAN IPs hardcoded.
"""
from __future__ import annotations

import json
import os
import queue
import re
import shutil
import subprocess
import threading
import time
import uuid
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Generator

from flask import Flask, Response, jsonify, request, send_from_directory, stream_with_context

ROOT = Path(__file__).resolve().parent
OMNI_ROOT = ROOT.parent
ENV_FILE = OMNI_ROOT / ".env"
STATE_DIR = ROOT / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
VAULT_FILE = STATE_DIR / "credentials.json"

DESK_PORT = int(os.environ.get("OMNIROUTE_DESK_PORT", os.environ.get("ARIA_PORT", "20129")))
DESK_BIND = os.environ.get("OMNIROUTE_DESK_BIND", os.environ.get("ARIA_BIND", "0.0.0.0"))
MISSION_CONTROLLER = os.environ.get("MISSION_CONTROLLER_URL", "http://127.0.0.1:20130").rstrip("/")
ARIA_OWNS_AUTO_POLICY = False  # P1: Mission Controller owns Auto
DEFAULT_OMNI = os.environ.get("OMNIROUTE_HOST", "http://127.0.0.1:20128").rstrip("/")
LOCAL_LLM_MODEL = os.environ.get("ARIA_LOCAL_MODEL", "ollama-local/gpt-oss:20b")
# OmniRoute auto/* currently prefers Grok on this host: KeepRoute Auto therefore
# picks Local LLM for simple jobs and only escalates for hard/coding work.
AUTO_MODEL = os.environ.get("ARIA_AUTO_MODEL", LOCAL_LLM_MODEL)
AUTO_CODING_MODEL = os.environ.get("ARIA_AUTO_CODING_MODEL", "auto/best-coding")
AUTO_HEAVY_MODEL = os.environ.get("ARIA_AUTO_HEAVY_MODEL", "auto/best-reasoning")

# mode: omni = chat via OmniRoute (default). cli = spawn local CLI.
AGENTS = {
    "auto": {
        "label": "Auto",
        "codename": "ORACLE",
        "mode": "omni",
        "model": AUTO_MODEL,
        "cli": None,
        "key_fields": ["omniroute_api_key"],
        "hint": "KeepRoute routes: greetings/simple → Local LLM; coding/hard → cloud via OmniRoute",
        "blurb": "Recommended · simple jobs → Local LLM (saves tokens); hard jobs → cloud",
        "default": True,
    },
    "llm": {
        "label": "Local LLM",
        "codename": "KEEP",
        "mode": "omni",
        "model": LOCAL_LLM_MODEL,
        "cli": None,
        "key_fields": ["omniroute_api_key"],
        "hint": "Runs on your machine through OmniRoute → Ollama",
        "blurb": "Private · on your hardware",
        "default": False,
    },
    "claude": {
        "label": "Claude",
        "codename": "GHOST",
        "mode": "omni",
        "model": "claude/claude-opus-5",
        "cli": "claude",
        "key_fields": ["anthropic_api_key", "omniroute_api_key"],
        "hint": "Claude via OmniRoute (or Claude Code CLI)",
        "blurb": "Deep reasoning specialist",
        "default": False,
    },
    "codex": {
        "label": "Codex",
        "codename": "SOL",
        "mode": "omni",
        "model": "codex/gpt-5.6-sol-medium",
        "cli": "codex",
        "key_fields": ["openai_api_key", "omniroute_api_key"],
        "hint": "OpenAI Codex via OmniRoute (or codex CLI)",
        "blurb": "Code field agent",
        "default": False,
    },
    "cursor-agent": {
        "label": "Cursor",
        "codename": "NEEDLE",
        "mode": "omni",
        "model": "cursor/auto-balance",
        "cli": "cursor-agent",
        "key_fields": ["cursor_api_key", "omniroute_api_key"],
        "hint": "Cursor via OmniRoute (or cursor-agent CLI)",
        "blurb": "Repo-aware edits",
        "default": False,
    },
    "grok": {
        "label": "Grok",
        "codename": "STORM",
        "mode": "omni",
        "model": "grok-cli/grok-4.6",
        "cli": "grok",
        "key_fields": ["xai_api_key", "omniroute_api_key"],
        "hint": "Grok via OmniRoute (or grok CLI)",
        "blurb": "Wild card · realtime edge",
        "default": False,
    },
}

AUTH_FIELDS = [
    {
        "id": "omniroute_url",
        "label": "OmniRoute URL",
        "placeholder": "http://127.0.0.1:20128",
        "secret": False,
        "help": "Where OmniRoute lives on this computer. Leave the default if unsure.",
    },
    {
        "id": "omniroute_api_key",
        "label": "OmniRoute API key",
        "placeholder": "ork_…",
        "secret": True,
        "help": "The main key. With this, KeepRoute can talk to every connected provider.",
    },
    {
        "id": "omniroute_password",
        "label": "OmniRoute dashboard password",
        "placeholder": "dashboard password",
        "secret": True,
        "help": "Only if you need KeepRoute to open the OmniRoute settings page for you.",
    },
    {
        "id": "anthropic_api_key",
        "label": "Claude / Anthropic key (optional)",
        "placeholder": "sk-ant-…",
        "secret": True,
        "help": "Only needed if you use Claude without OmniRoute login.",
    },
    {
        "id": "openai_api_key",
        "label": "OpenAI / Codex key (optional)",
        "placeholder": "sk-…",
        "secret": True,
        "help": "Only needed if you use Codex without OmniRoute login.",
    },
    {
        "id": "cursor_api_key",
        "label": "Cursor key (optional)",
        "placeholder": "key_…",
        "secret": True,
        "help": "Only needed for Cursor outside OmniRoute.",
    },
    {
        "id": "xai_api_key",
        "label": "Grok / xAI key (optional)",
        "placeholder": "xai-…",
        "secret": True,
        "help": "Only needed for Grok outside OmniRoute.",
    },
]

# Ultra-simple guides for the UI modals
HOW_IT_WORKS = {
    "title": "How to use KeepRoute",
    "intro": (
        "KeepRoute is a simple screen that talks for you. "
        "Underneath it, a helper named OmniRoute automatically chooses "
        "the best service for your job: like Claude, Codex, Cursor, Grok, "
        "or your computer's own Local LLM. You do not have to pick the smartest one. "
        "Auto does that for you."
    ),
    "emphasis": (
        "Most important idea: leave Auto turned on. "
        "Then type what you want in plain words and press the green button. "
        "OmniRoute looks at your request and routes it to the best provider for that job."
    ),
    "steps": [
        {
            "n": 1,
            "title": "You are already in the right place",
            "body": "This page is KeepRoute. The dark window in the middle is where answers appear.",
        },
        {
            "n": 2,
            "title": "Leave Auto selected on the left",
            "body": (
                "Auto means: \"Please choose the best helper for this job.\" "
                "That is the whole point of KeepRoute + OmniRoute. "
                "Only tap another name if you already know you want that one."
            ),
        },
        {
            "n": 3,
            "title": "Type a plain sentence",
            "body": (
                "In the box under the dark window, write what you want: "
                "the same way you would tell a helpful person. "
                "Example: \"Make a short shopping list for tacos.\""
            ),
        },
        {
            "n": 4,
            "title": "Press the green EXECUTE button",
            "body": (
                "KeepRoute sends your words to OmniRoute. "
                "OmniRoute picks the best connected provider for that job and gets the answer. "
                "Words will show up in the dark window. Wait until it says the job is finished."
            ),
        },
        {
            "n": 5,
            "title": "Watch the two lights next to each name",
            "body": (
                "Status light: green means that service is connected and ready; red means it is not. "
                "Routed light: green means OmniRoute just used that service for your last request."
            ),
        },
        {
            "n": 6,
            "title": "Need to connect a new service?",
            "body": (
                "Press ADD PROVIDERS at the top. "
                "That is also where you paste your keys. "
                "Follow the simple steps for the service you want."
            ),
        },
    ],
}

FAQ = [
    {
        "q": "What is KeepRoute?",
        "a": (
            "KeepRoute is a friendly screen. It helps you ask for help "
            "without learning computer commands. It looks cool on purpose so the hard parts feel less scary."
        ),
    },
    {
        "q": "What is OmniRoute?",
        "a": (
            "OmniRoute is the traffic director behind KeepRoute. "
            "You give KeepRoute a job. OmniRoute decides which connected service should handle it: "
            "Claude, Codex, Cursor, Grok, Local LLM, or another one you added."
        ),
    },
    {
        "q": "What does Auto do?",
        "a": (
            "Auto means KeepRoute chooses the route for you. "
            "Simple things like \"hi\" go to Local LLM on your computer (no cloud tokens). "
            "Coding or hard thinking jobs can go to cloud providers through OmniRoute. "
            "That saves money and still uses the strong helpers when you need them."
        ),
    },
    {
        "q": "Why did my message go to Grok before?",
        "a": (
            "OmniRoute\'s built-in auto shortcuts on this machine were sending almost everything to Grok, "
            "even short hellos. KeepRoute Auto now overrides that: greetings and everyday chat use Local LLM first. "
            "Hard or coding jobs can still use cloud providers."
        ),
    },
    {
        "q": "Do I have to pick Claude or Codex myself?",
        "a": (
            "No. If Auto is selected, you do not. "
            "Only pick a specific name when you already know you want that one every time."
        ),
    },
    {
        "q": "Why do some names not show up on the left?",
        "a": (
            "KeepRoute only shows providers you have actually connected. "
            "If Claude is not connected yet, Claude will not appear. "
            "Connect it under ADD PROVIDERS, then it will show up with a Status light."
        ),
    },
    {
        "q": "What do the two lights mean?",
        "a": (
            "Status: green = connected and ready; red = not connected. "
            "Routed: green = OmniRoute used this provider for your latest request; red = it did not."
        ),
    },
    {
        "q": "Where do I put my keys? Where did Clearance go?",
        "a": (
            "Keys now live inside ADD PROVIDERS so everything is in one place. "
            "Open ADD PROVIDERS → follow the steps → scroll to Keys → paste → Save keys."
        ),
    },
    {
        "q": "What key do I need first?",
        "a": (
            "Start with your OmniRoute API key. "
            "That one key lets KeepRoute talk to OmniRoute, and OmniRoute talks to the providers you connected."
        ),
    },
    {
        "q": "What is Local LLM?",
        "a": (
            "Local LLM means a helper running on your own computer. "
            "It stays more private. Connect it in OmniRoute, then it can appear in KeepRoute's list."
        ),
    },
    {
        "q": "I pressed EXECUTE and nothing happened. What now?",
        "a": (
            "1) Check the top badge: OmniRoute should say ONLINE. "
            "2) Open ADD PROVIDERS and confirm your OmniRoute API key is saved. "
            "3) Make sure at least one provider Status light is green. "
            "4) Try a shorter sentence. If it still fails, press ABORT and try again."
        ),
    },
]

PROVIDER_GUIDES = [
    {
        "id": "omniroute",
        "title": "OmniRoute (do this first)",
        "summary": "This is the main switch. Without it, KeepRoute cannot auto-pick helpers.",
        "steps": [
            "Make sure OmniRoute is running on this computer.",
            "Open OmniRoute in a browser (same computer, usually port 20128).",
            "Find and copy the API key.",
            "Come back here → scroll to Keys → paste it into OmniRoute API key → Save keys.",
            "When the top of KeepRoute says OMNIROUTE ONLINE, you are ready for Auto.",
        ],
    },
    {
        "id": "claude",
        "title": "Claude",
        "summary": "A careful helper for writing and thinking.",
        "steps": [
            "In OmniRoute, open Providers.",
            "Connect Claude (sign in if it asks).",
            "Wait until it shows healthy / active.",
            "Return to KeepRoute and refresh: Claude should appear on the left with a green Status light.",
            "Optional: if a key is needed, paste it under Keys below.",
        ],
    },
    {
        "id": "codex",
        "title": "Codex (OpenAI)",
        "summary": "A helper that is strong with code and computer tasks.",
        "steps": [
            "In OmniRoute → Providers, connect Codex / ChatGPT.",
            "Sign in when asked.",
            "When it is active, refresh KeepRoute: Codex appears on the left.",
            "Optional key paste is under Keys if needed.",
        ],
    },
    {
        "id": "cursor",
        "title": "Cursor",
        "summary": "A helper for editing projects and code files.",
        "steps": [
            "In OmniRoute → Providers, connect Cursor.",
            "Finish any login it shows.",
            "Refresh KeepRoute: Cursor appears when connected.",
        ],
    },
    {
        "id": "grok",
        "title": "Grok",
        "summary": "A bold, fast helper from xAI.",
        "steps": [
            "In OmniRoute → Providers, connect Grok.",
            "Finish login or paste an xAI key if asked.",
            "Refresh KeepRoute: Grok appears when connected.",
        ],
    },
    {
        "id": "llm",
        "title": "Local LLM",
        "summary": "A helper that runs on your own computer.",
        "steps": [
            "Install your local model app (often Ollama) on this computer.",
            "Download a chat model.",
            "In OmniRoute → Providers, turn on the local / ollama provider.",
            "Refresh KeepRoute: Local LLM appears when it is connected.",
        ],
    },
    {
        "id": "other",
        "title": "Something else",
        "summary": "If OmniRoute can connect it, KeepRoute can use it through Auto.",
        "steps": [
            "Open OmniRoute → Providers.",
            "Add the new service and finish its login or key form.",
            "Make sure it shows active / healthy.",
            "In KeepRoute, leave Auto selected: OmniRoute can route jobs to it when it is the best fit.",
        ],
    },
]

# Map KeepRoute agent id → OmniRoute provider id(s)
PROVIDER_MAP = {
    "llm": ["ollama-local"],
    "claude": ["claude"],
    "codex": ["codex"],
    "cursor-agent": ["cursor"],
    "grok": ["grok-cli"],
}

# Map model prefix → KeepRoute agent for "routed" light
MODEL_ROUTE_MAP = [
    ("ollama-local/", "llm"),
    ("auto/offline", "llm"),
    ("claude/", "claude"),
    ("cc/", "claude"),
    ("codex/", "codex"),
    ("cx/", "codex"),
    ("cxa/", "codex"),
    ("cursor/", "cursor-agent"),
    ("cu/", "cursor-agent"),
    ("grok-cli/", "grok"),
    ("gc/", "grok"),
]

_missions: dict[str, dict[str, Any]] = {}
_missions_lock = threading.Lock()
_last_routed: dict[str, Any] = {"agent": None, "model": None, "at": None}

app = Flask(
    __name__,
    static_folder=str(ROOT / "static"),
    template_folder=str(ROOT / "templates"),
)


def _mask(value: str) -> str:
    v = (value or "").strip()
    if not v:
        return ""
    if len(v) <= 8:
        return "•" * len(v)
    return f"{v[:4]}…{v[-4:]}"


def _load_vault() -> dict[str, str]:
    base = {
        "omniroute_url": DEFAULT_OMNI,
        "omniroute_api_key": "",
        "omniroute_password": "",
        "anthropic_api_key": "",
        "openai_api_key": "",
        "cursor_api_key": "",
        "xai_api_key": "",
    }
    if ENV_FILE.is_file():
        for line in ENV_FILE.read_text().splitlines():
            if "=" not in line or line.strip().startswith("#"):
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k == "OMNIROUTE_API_KEY" and v:
                base["omniroute_api_key"] = v
            elif k == "OMNIROUTE_INITIAL_PASSWORD" and v:
                base["omniroute_password"] = v
    if VAULT_FILE.is_file():
        try:
            data = json.loads(VAULT_FILE.read_text())
            if isinstance(data, dict):
                for k in base:
                    if k in data and data[k] is not None:
                        base[k] = str(data[k])
        except Exception:
            pass
    env_map = {
        "omniroute_url": "OMNIROUTE_HOST",
        "omniroute_api_key": "OMNIROUTE_API_KEY",
        "omniroute_password": "OMNIROUTE_INITIAL_PASSWORD",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "openai_api_key": "OPENAI_API_KEY",
        "cursor_api_key": "CURSOR_API_KEY",
        "xai_api_key": "XAI_API_KEY",
    }
    for field, env_key in env_map.items():
        if os.environ.get(env_key):
            base[field] = os.environ[env_key]
    return base


def _save_vault(updates: dict[str, Any]) -> dict[str, str]:
    vault = _load_vault()
    for field in vault:
        if field in updates and updates[field] is not None:
            val = str(updates[field]).strip()
            if val or updates.get("_clear"):
                vault[field] = val
    VAULT_FILE.write_text(json.dumps(vault, indent=2))
    try:
        os.chmod(VAULT_FILE, 0o600)
    except OSError:
        pass
    return vault


def _omni_host(vault: dict[str, str] | None = None) -> str:
    v = vault or _load_vault()
    host = (v.get("omniroute_url") or DEFAULT_OMNI).rstrip("/")
    if re.search(r"192\.168\.50\.(219|221)\b", host):
        host = "http://127.0.0.1:20128"
    return host


def _which_cli(name: str | None) -> str | None:
    if not name:
        return None
    path = shutil.which(name)
    if path:
        return path
    candidates = [
        Path.home() / ".local" / "bin" / name,
        Path("/usr/local/bin") / name,
        Path.home() / ".local" / "bin" / name,
    ]
    if name == "cursor-agent":
        candidates += [
            Path.home() / ".local" / "bin" / "agent",
            Path.home() / ".local" / "bin" / "agent",
        ]
        path = shutil.which("agent")
        if path:
            return path
    for c in candidates:
        if c.is_file() and os.access(c, os.X_OK):
            return str(c)
    return None


def _health(omni: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(f"{omni}/api/health", timeout=3) as r:
            return {"ok": r.status == 200, "status": r.status}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _omni_login_session(vault: dict[str, str]):
    """Cookie session for OmniRoute dashboard APIs (optional)."""
    import http.cookiejar
    pw = vault.get("omniroute_password") or ""
    omni = _omni_host(vault)
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    if pw:
        body = json.dumps({"password": pw}).encode()
        req = urllib.request.Request(
            f"{omni}/api/auth/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            opener.open(req, timeout=15).read()
        except Exception:
            pass
    return opener, omni


def _provider_connections(vault: dict[str, str] | None = None) -> list[dict[str, Any]]:
    vault = vault or _load_vault()
    try:
        opener, omni = _omni_login_session(vault)
        req = urllib.request.Request(f"{omni}/api/omniroute/status")
        with opener.open(req, timeout=20) as r:
            data = json.loads(r.read().decode())
        return list(((data.get("providers") or {}).get("connections")) or [])
    except Exception:
        return []


def _connection_index(conns: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out = {}
    for c in conns:
        p = c.get("provider")
        if p:
            out[p] = c
    return out


def _agent_from_model(model: str | None) -> str | None:
    if not model:
        return None
    m = str(model).lower()
    for prefix, agent in MODEL_ROUTE_MAP:
        p = prefix.lower()
        if m.startswith(p) or p.rstrip("/") in m.split("/")[0] or p in m:
            return agent
    # bare model ids from OmniRoute (no provider prefix)
    # Local / open-weight models first (gpt-oss is Ollama, NOT OpenAI)
    if (
        "gpt-oss" in m
        or "llama" in m
        or "ollama" in m
        or "qwen" in m
        or "hermes" in m
        or "granite" in m
        or "deepseek-r1" in m
        or m.endswith(":1b")
        or m.endswith(":8b")
        or m.endswith(":20b")
    ):
        return "llm"
    if m.startswith("grok") or "grok" in m:
        return "grok"
    if m.startswith("claude") or "sonnet" in m or "opus" in m or "haiku" in m:
        return "claude"
    if "codex" in m or m.startswith("gpt-5") or m.startswith("gpt-4") or m.startswith("o1") or m.startswith("o3"):
        return "codex"
    if "cursor" in m or "composer" in m:
        return "cursor-agent"
    if m.startswith("auto/"):
        return "auto"
    return None


def _visible_agents(vault: dict[str, str], omni_ok: bool) -> dict[str, dict[str, Any]]:
    """Only Auto + providers the user has actually connected."""
    conns = _connection_index(_provider_connections(vault))
    visible = {}
    # Auto always visible when OmniRoute key exists
    if vault.get("omniroute_api_key") and omni_ok:
        visible["auto"] = {
            **AGENTS["auto"],
            "connected": True,
            "status": "connected",
            "added": True,
        }
    elif vault.get("omniroute_api_key"):
        visible["auto"] = {
            **AGENTS["auto"],
            "connected": False,
            "status": "disconnected",
            "added": True,
        }

    for agent_id, providers in PROVIDER_MAP.items():
        added = False
        connected = False
        health = "missing"
        for p in providers:
            c = conns.get(p)
            if not c:
                continue
            added = True
            health = c.get("health") or "unknown"
            if bool(c.get("active")) and health not in ("disabled", "unhealthy", "error", "down"):
                connected = True
        key_fields = AGENTS[agent_id].get("key_fields") or []
        if any(vault.get(k) for k in key_fields if k != "omniroute_api_key"):
            added = True
        if not added:
            continue
        is_up = bool(connected and omni_ok)
        visible[agent_id] = {
            **AGENTS[agent_id],
            "connected": is_up,
            "status": "connected" if is_up else "disconnected",
            "health": health,
            "added": True,
        }
    return visible



def _public_base() -> str:
    proto = request.headers.get("X-Forwarded-Proto") or request.scheme or "http"
    host = request.headers.get("X-Forwarded-Host") or request.host or f"127.0.0.1:{DESK_PORT}"
    return f"{proto}://{host}".rstrip("/")


def _agent_ready(key: str, vault: dict[str, str], omni_ok: bool) -> bool:
    meta = AGENTS[key]
    if meta["mode"] == "omni":
        return omni_ok and bool(vault.get("omniroute_api_key"))
    return bool(_which_cli(meta.get("cli")))


def _cli_env(vault: dict[str, str], agent: str) -> dict[str, str]:
    env = os.environ.copy()
    if vault.get("anthropic_api_key"):
        env["ANTHROPIC_API_KEY"] = vault["anthropic_api_key"]
    if vault.get("openai_api_key"):
        env["OPENAI_API_KEY"] = vault["openai_api_key"]
    if vault.get("cursor_api_key"):
        env["CURSOR_API_KEY"] = vault["cursor_api_key"]
    if vault.get("xai_api_key"):
        env["XAI_API_KEY"] = vault["xai_api_key"]
        env["GROK_API_KEY"] = vault["xai_api_key"]
    if vault.get("omniroute_api_key"):
        env["OMNIROUTE_API_KEY"] = vault["omniroute_api_key"]
        omni = _omni_host(vault)
        env.setdefault("OPENAI_BASE_URL", f"{omni}/v1")
        if agent == "claude":
            env.setdefault("ANTHROPIC_BASE_URL", omni)
            env.setdefault("ANTHROPIC_API_KEY", vault["omniroute_api_key"])
    return env


def _build_cli_cmd(agent: str, prompt: str) -> list[str]:
    cli = AGENTS[agent].get("cli")
    binary = _which_cli(cli)
    if not binary:
        raise RuntimeError(f"{AGENTS[agent]['label']} CLI not found.")
    if agent == "claude":
        return [binary, "-p", prompt, "--output-format", "text"]
    if agent == "codex":
        return [binary, "exec", "--skip-git-repo-check", prompt]
    if agent == "cursor-agent":
        return [binary, "-p", prompt, "--output-format", "text"]
    if agent == "grok":
        return [binary, prompt]
    raise RuntimeError(f"No CLI path for {agent}")



def _run_omni_mission(mission_id: str, agent: str, prompt: str) -> None:
    mission = _missions[mission_id]
    vault = _load_vault()
    q: queue.Queue = mission["queue"]
    meta = AGENTS[agent]
    model = meta["model"]
    route_hint = agent
    reason = ""
    omni = _omni_host(vault)
    key = vault.get("omniroute_api_key") or ""

    def emit(kind: str, text: str) -> None:
        q.put({"t": time.time(), "kind": kind, "text": text})

    try:
        # P1: Auto is owned by Mission Controller sidecar: KeepRoute does not classify/route.
        if agent == "auto":
            if ARIA_OWNS_AUTO_POLICY:
                raise RuntimeError("KeepRoute Auto policy is disabled; Mission Controller must own routing")
            emit("sys", f"MISSION {mission_id[:8].upper()} · Auto → Mission Controller")
            emit("sys", "Policy owner: mission-controller (not KeepRoute)")
            mission["status"] = "running"
            import urllib.request
            payload = json.dumps({"objective": prompt, "archive_evidence": False}).encode()
            req = urllib.request.Request(
                f"{MISSION_CONTROLLER}/v1/missions/execute",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
            if not data.get("ok"):
                raise RuntimeError(data.get("error") or "Mission Controller failed")
            dec = data.get("decision") or {}
            emit("sys", f"MC classification: {dec.get('classification')}")
            emit("sys", f"MC policy: {dec.get('policy_rule')}")
            emit("sys", f"MC selected: {dec.get('selected_route')}")
            emit("sys", f"Actual provider: {data.get('actual_provider_reached')} ({data.get('paid_or_local')})")
            if data.get("reply"):
                emit("out", data["reply"])
            routed_agent = data.get("actual_provider_reached") or "llm"
            if routed_agent == "local":
                routed_agent = "llm"
            global _last_routed
            _last_routed = {
                "agent": routed_agent,
                "model": data.get("actual_model"),
                "at": time.time(),
                "requested": "auto",
                "owner": "mission-controller",
            }
            emit("route", json.dumps({"agent": routed_agent, "model": data.get("actual_model"), "owner": "mission-controller"}))
            mission["status"] = "ok"
            mission["exit_code"] = 0
            emit("sys", "MISSION COMPLETE · exit 0")
            return

        if not key:
            raise RuntimeError("OmniRoute API key missing: open ADD PROVIDERS and paste it under Keys.")
        emit("sys", f"MISSION {mission_id[:8].upper()} · {meta['label']} via OmniRoute")
        emit("sys", f"MODEL {model}")
        mission["status"] = "running"

        def _mark_route(routed_model: str | None) -> str | None:
            global _last_routed
            ra = _agent_from_model(routed_model)
            if agent != "auto":
                ra = agent
            else:
                # Classifier said local → keep Routed light on Local LLM
                if route_hint == "llm":
                    ra = "llm"
                elif route_hint and route_hint != "auto":
                    ra = ra if (ra and ra != "auto") else route_hint
                else:
                    ra = ra or "auto"
            _last_routed = {
                "agent": ra,
                "model": routed_model or model,
                "at": time.time(),
                "requested": agent,
            }
            return ra

        # Non-stream first (reliable). OmniRoute still auto-picks for auto/* models.
        payload = json.dumps(
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            }
        ).encode()
        req = urllib.request.Request(
            f"{omni}/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        if data.get("error"):
            raise RuntimeError(str(data.get("error")))
        routed_model = data.get("model") or model
        if routed_model in ("keepalive", "null"):
            routed_model = model
        mission["_routed_model"] = routed_model
        choice = ((data.get("choices") or [{}])[0]).get("message") or {}
        text_out = choice.get("content") or ""
        if text_out:
            emit("out", text_out)
        routed_agent = _mark_route(routed_model)
        emit("sys", f"OmniRoute routed to: {routed_model}")
        if routed_agent and routed_agent in AGENTS:
            emit("sys", f"Provider used: {AGENTS[routed_agent]['label']}")
        emit("route", json.dumps({"agent": routed_agent, "model": routed_model}))
        mission["status"] = "ok"
        mission["exit_code"] = 0
        emit("sys", "MISSION COMPLETE · exit 0")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:800]
        mission["status"] = "fail"
        mission["exit_code"] = e.code
        emit("err", f"OmniRoute HTTP {e.code}: {body}")
        emit("sys", "MISSION ABORTED")
    except Exception as e:
        mission["status"] = "fail"
        mission["exit_code"] = 1
        emit("err", str(e))
        emit("sys", "MISSION ABORTED")
    finally:
        q.put(None)


def _run_cli_mission(mission_id: str, agent: str, prompt: str) -> None:
    mission = _missions[mission_id]
    vault = _load_vault()
    q: queue.Queue = mission["queue"]

    def emit(kind: str, text: str) -> None:
        q.put({"t": time.time(), "kind": kind, "text": text})

    try:
        cmd = _build_cli_cmd(agent, prompt)
        env = _cli_env(vault, agent)
        emit("sys", f"MISSION {mission_id[:8].upper()} · CLI {AGENTS[agent]['codename']}")
        emit("sys", f"$ {' '.join(cmd[:2])} …")
        mission["status"] = "running"
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
            cwd=str(Path.home()),
        )
        mission["pid"] = proc.pid
        assert proc.stdout is not None
        for line in proc.stdout:
            emit("out", line.rstrip("\n"))
        code = proc.wait()
        mission["exit_code"] = code
        mission["status"] = "ok" if code == 0 else "fail"
        emit("sys", f"MISSION COMPLETE · exit {code}")
    except Exception as e:
        mission["status"] = "fail"
        mission["exit_code"] = 1
        emit("err", str(e))
        emit("sys", "MISSION ABORTED")
    finally:
        q.put(None)


def _run_mission(mission_id: str, agent: str, prompt: str, force_cli: bool = False) -> None:
    meta = AGENTS[agent]
    if force_cli and meta.get("cli"):
        _run_cli_mission(mission_id, agent, prompt)
    elif meta["mode"] == "omni":
        _run_omni_mission(mission_id, agent, prompt)
    else:
        _run_cli_mission(mission_id, agent, prompt)


@app.get("/")
def index() -> Response:
    return send_from_directory(app.template_folder, "index.html")


@app.get("/api/meta")
def meta():
    vault = _load_vault()
    omni = _omni_host(vault)
    omni_ok = bool(_health(omni).get("ok"))
    visible = _visible_agents(vault, omni_ok)
    agents_out = {}
    for k, v in visible.items():
        agents_out[k] = {
            "label": v["label"],
            "blurb": v.get("blurb"),
            "hint": v.get("hint"),
            "mode": v.get("mode"),
            "model": v.get("model"),
            "default": bool(v.get("default")),
            "connected": bool(v.get("connected")),
            "status": v.get("status"),
            "routed": (_last_routed.get("agent") == k),
            "added": True,
        }
    return jsonify(
        {
            "product": "KeepRoute",
            "org": "OtaconsKeep",
            "public": True,
            "base": _public_base(),
            "omniroute": omni,
            "omniroute_ok": omni_ok,
            "default_agent": "auto",
            "last_routed": _last_routed,
            "agents": agents_out,
            "auth_fields": [
                {**f, "configured": bool(vault.get(f["id"]))} for f in AUTH_FIELDS
            ],
        }
    )



@app.get("/api/guides")
def guides():
    return jsonify({
        "how_it_works": HOW_IT_WORKS,
        "faq": FAQ,
        "providers": PROVIDER_GUIDES,
    })


@app.get("/api/auth")
def auth_get():
    vault = _load_vault()
    omni_ok = bool(_health(_omni_host(vault)).get("ok"))
    return jsonify(
        {
            "ok": True,
            "fields": [
                {
                    **f,
                    "configured": bool(vault.get(f["id"])),
                    "masked": _mask(vault.get(f["id"], "")) if f["secret"] else vault.get(f["id"], ""),
                    "value": "" if f["secret"] else vault.get(f["id"], ""),
                }
                for f in AUTH_FIELDS
            ],
            "agents": {
                k: {
                    "ready": _agent_ready(k, vault, omni_ok),
                    "mode": v["mode"],
                    "keys": {f: bool(vault.get(f)) for f in v["key_fields"]},
                }
                for k, v in AGENTS.items()
            },
        }
    )


@app.post("/api/auth")
def auth_save():
    body = request.get_json(force=True, silent=True) or {}
    allowed = {f["id"] for f in AUTH_FIELDS}
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        return jsonify({"ok": False, "error": "No fields to save"}), 400
    _save_vault(updates)
    return jsonify({"ok": True, "saved": list(updates.keys())})


@app.get("/api/status")
def status():
    vault = _load_vault()
    omni = _omni_host(vault)
    health = _health(omni)
    omni_ok = bool(health.get("ok"))
    visible = _visible_agents(vault, omni_ok)
    return jsonify(
        {
            "health": health,
            "omniroute": omni,
            "vault_present": VAULT_FILE.is_file(),
            "default_agent": "auto",
            "last_routed": _last_routed,
            "agents": {
                k: {
                    "label": v["label"],
                    "connected": bool(v.get("connected")),
                    "status": v.get("status"),
                    "routed": (_last_routed.get("agent") == k),
                }
                for k, v in visible.items()
            },
        }
    )



@app.post("/api/mission")
def mission_start():
    body = request.get_json(force=True, silent=True) or {}
    agent = (body.get("agent") or "auto").strip().lower()
    aliases = {
        "claude code": "claude",
        "claude-code": "claude",
        "cc": "claude",
        "openai": "codex",
        "gpt": "codex",
        "cursor": "cursor-agent",
        "agent": "cursor-agent",
        "xai": "grok",
        "grok-cli": "grok",
        "local": "llm",
        "ollama": "llm",
        "oracle": "auto",
        "best": "auto",
    }
    agent = aliases.get(agent, agent)
    prompt = (body.get("prompt") or "").strip()
    force_cli = bool(body.get("force_cli"))
    if agent not in AGENTS:
        return jsonify({"ok": False, "error": "Pick an agent", "agents": list(AGENTS)}), 400
    if not prompt:
        return jsonify({"ok": False, "error": "Mission brief required"}), 400

    mission_id = uuid.uuid4().hex
    q: queue.Queue = queue.Queue()
    with _missions_lock:
        _missions[mission_id] = {
            "id": mission_id,
            "agent": agent,
            "prompt": prompt,
            "status": "queued",
            "queue": q,
            "started": time.time(),
            "pid": None,
            "exit_code": None,
        }
    t = threading.Thread(
        target=_run_mission, args=(mission_id, agent, prompt, force_cli), daemon=True
    )
    t.start()
    return jsonify(
        {
            "ok": True,
            "mission_id": mission_id,
            "agent": agent,
            "codename": AGENTS[agent]["codename"],
            "mode": "cli" if force_cli else AGENTS[agent]["mode"],
            "model": AGENTS[agent].get("model"),
            "stream": f"/api/mission/{mission_id}/stream",
        }
    )


@app.get("/api/mission/<mission_id>/stream")
def mission_stream(mission_id: str):
    mission = _missions.get(mission_id)
    if not mission:
        return jsonify({"ok": False, "error": "Unknown mission"}), 404

    def gen() -> Generator[str, None, None]:
        q: queue.Queue = mission["queue"]
        while True:
            item = q.get()
            if item is None:
                yield f"data: {json.dumps({'kind': 'done', 'status': mission['status'], 'exit_code': mission.get('exit_code')})}\n\n"
                break
            yield f"data: {json.dumps(item)}\n\n"

    return Response(
        stream_with_context(gen()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/mission/<mission_id>")
def mission_get(mission_id: str):
    mission = _missions.get(mission_id)
    if not mission:
        return jsonify({"ok": False, "error": "Unknown mission"}), 404
    return jsonify(
        {
            "ok": True,
            "id": mission_id,
            "agent": mission["agent"],
            "status": mission["status"],
            "exit_code": mission.get("exit_code"),
            "pid": mission.get("pid"),
        }
    )


@app.post("/api/mission/<mission_id>/abort")
def mission_abort(mission_id: str):
    mission = _missions.get(mission_id)
    if not mission:
        return jsonify({"ok": False, "error": "Unknown mission"}), 404
    pid = mission.get("pid")
    if pid:
        try:
            os.kill(pid, 15)
        except OSError:
            pass
    mission["status"] = "aborted"
    return jsonify({"ok": True})


@app.get("/shortcuts/<path:name>")
def shortcuts(name: str):
    return send_from_directory(ROOT / "shortcuts", name)


if __name__ == "__main__":
    app.run(host=DESK_BIND, port=DESK_PORT, debug=False, threaded=True)

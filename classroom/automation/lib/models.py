#!/usr/bin/env python3
"""OmniRoute / Ollama client with fail-closed weak-model detection."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from . import Config, redact_secrets


class ModelError(RuntimeError):
    pass


class WeakModelError(ModelError):
    pass


def _post_json(url: str, payload: dict[str, Any], key: str, timeout: int) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "otaconskeep-classroom-automation/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        raise ModelError(redact_secrets(f"HTTP {e.code}: {body}")) from e
    except Exception as e:
        raise ModelError(redact_secrets(str(e))) from e


def chat(
    cfg: Config,
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 8000,
) -> tuple[str, str]:
    """Return (content, resolved_model). Fail closed on weak resolved models unless allowed."""
    if not cfg.omni_key:
        raise ModelError("OMNIROUTE_API_KEY missing")
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    url = f"{cfg.omni_base}/chat/completions"
    result = _post_json(url, payload, cfg.omni_key, cfg.llm_timeout)
    resolved = str(result.get("model") or model)
    content = ""
    try:
        content = result["choices"][0]["message"]["content"] or ""
    except Exception as e:
        raise ModelError(f"unexpected response shape: {e}") from e
    if not cfg.allow_weak:
        low = resolved.lower()
        for prefix in cfg.weak_prefixes:
            if prefix and prefix.lower() in low:
                raise WeakModelError(
                    f"Resolved model '{resolved}' matches weak prefix '{prefix}'. "
                    "Refusing silent downgrade (set ALLOW_WEAK_MODELS=1 only with operator approval)."
                )
    return content, resolved


def extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < 0:
        raise ModelError("no JSON object in model output")
    return json.loads(text[start : end + 1])

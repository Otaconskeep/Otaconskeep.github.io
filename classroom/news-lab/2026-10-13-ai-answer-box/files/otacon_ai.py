# SPDX-License-Identifier: AGPL-3.0-or-later
"""Otaconskeep AI answer: a short cited answer from a local Ollama model.

Public teaching copy. Set OK_AI_OLLAMA to an address this container can reach.
Do not put LAN addresses, VPN status URLs, or secrets in the copy you publish.
"""
from __future__ import annotations
import json, os, re, time
import urllib.request
from searx.plugins import Plugin, PluginInfo

OLLAMA = os.environ.get("OK_AI_OLLAMA", "http://127.0.0.1:11434")
MODEL = os.environ.get("OK_AI_MODEL", "gpt-oss:20b")
THINK = os.environ.get("OK_AI_THINK", "low")
SYSTEM = (
    "You are the answer box of a private search engine. Using ONLY the numbered search results, "
    "write a direct answer in 2 to 4 short sentences (under 90 words). After every sentence put the "
    "number of the result it came from in square brackets, like [1] or [2][4]. Use only numbers that exist. "
    "No preamble, no headings, no source list, no URLs. If the results do not answer it, say so briefly."
)

def _clean(s, n):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s[:n]

class SXNGPlugin(Plugin):
    id = "otaconai"
    def __init__(self, plg_cfg):
        super().__init__(plg_cfg)
        self.info = PluginInfo(
            id=self.id,
            name="Otacon AI answer",
            description="Local AI summary of the top results.",
            preference_section=None,
        )

    def init(self, app) -> bool:
        from flask import Response, abort, request, stream_with_context

        @app.route("/ok/ai", methods=["POST"])
        def ok_ai():
            if request.headers.get("Sec-Fetch-Site") not in {"same-origin", None}:
                abort(403)
            data = request.get_json(silent=True) or {}
            q = _clean(data.get("q"), 300)
            res = data.get("results") or []
            if not q or not isinstance(res, list) or not res:
                abort(400)
            ctx = []
            for i, r in enumerate(res[:5], 1):
                if not isinstance(r, dict):
                    abort(400)
                ctx.append(
                    f"[{i}] {_clean(r.get('title'), 160)}\n"
                    f"{_clean(r.get('url'), 300)}\n"
                    f"{_clean(r.get('snippet'), 600)}"
                )
            body = {
                "model": MODEL,
                "stream": True,
                "keep_alive": "30m",
                "options": {"temperature": 0.2, "num_predict": 900},
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": "Search results:\n\n" + "\n\n".join(ctx) + f"\n\nQuestion: {q}"},
                ],
            }
            if THINK:
                body["think"] = THINK

            def gen():
                t0 = time.time()
                first = None
                try:
                    rq = urllib.request.Request(
                        OLLAMA + "/api/chat",
                        json.dumps(body).encode(),
                        {"Content-Type": "application/json"},
                    )
                    with urllib.request.urlopen(rq, timeout=120) as resp:
                        for line in resp:
                            if not line.strip():
                                continue
                            j = json.loads(line)
                            tok = (j.get("message") or {}).get("content", "")
                            if tok:
                                if first is None:
                                    first = time.time() - t0
                                yield json.dumps({"t": tok}) + "\n"
                            if j.get("done"):
                                break
                    yield json.dumps({
                        "done": True,
                        "model": MODEL,
                        "first": round(first or 0, 2),
                        "total": round(time.time() - t0, 2),
                    }) + "\n"
                except Exception:
                    yield json.dumps({"error": "The local model is not reachable right now."}) + "\n"

            return Response(
                stream_with_context(gen()),
                mimetype="application/x-ndjson",
                headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
            )
        return True

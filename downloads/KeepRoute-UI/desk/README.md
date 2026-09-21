# KeepRoute, OtaconsKeep field UI

GUI in front. OmniRoute underneath. Providers you connect (Claude, Codex, Cursor, Grok, Local LLM).

## Run

```bash
pip install flask
python3 desk/app.py
# → http://127.0.0.1:20129/
```

Or install the example systemd user unit from this package.

## Rules

- Do not hardcode private LAN addresses.
- Default gateway URL is `http://127.0.0.1:20128` (OmniRoute).
- Mission Controller (optional for Auto mission policy): `http://127.0.0.1:20130`
- Credentials live in `desk/state/credentials.json` (create empty `{}` if missing; mode 600).

## Flow

1. Start OmniRoute, then KeepRoute UI
2. Open **ADD PROVIDERS**, paste keys, **SAVE KEYS**
3. Leave **Auto** selected (or pick a provider)
4. Type a request, **GO**

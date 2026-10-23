# Classroom automation (Homelab Academy)

Fail-closed lesson generation and publication for OtaconsKeep Homelab Academy.

## What this is

After **activation approval**, systemd timers generate six core lessons twice nightly (America/Phoenix 01:00 and 03:30), validate them, and publish through git only when every hard gate passes. A news evaluator runs after the late batch and creates at most one bonus lesson when a breakthrough clears the quality gate.

Until activation: `DRY_RUN=1` — scheduled jobs no-op publish.

## Repository facts (discovered)

- Publish repo: `/root/otaconskeep-site` → Cloudflare Workers (`wrangler` on `main`)
- Curriculum pack: `classroom/pack/` (module-first; Classes 01–15 published)
- Build: `classroom/_gen_from_pack.py`
- Upstream mirror: `/root/Classroom`
- Next missing core numbers: **16–21** (Classes 14–15 numbers already used by n8n / IPv4)

## Layout

See scripts in this directory plus `systemd/`, `tests/`, `fixtures/`, `lib/`.

## Secrets

Copy `config.example.env` → `/etc/otaconskeep-classroom.env` (mode `0640`). Never commit it.

## Operator commands

```bash
# status / pending / timers / pause / resume / logs
python3 status.py status
python3 status.py pending
python3 status.py timers
python3 status.py pause
python3 status.py resume
python3 status.py logs -n 100

# tests
python3 tests/run_tests.py

# non-destructive dry run (no git push, live pack unchanged)
GENERATOR_BACKEND=curated DRY_RUN=1 python3 run_dry_batch.py

# rollback demo (fixture) / real revert instructions
python3 rollback_batch.py --demonstrate-fixture
```

## Activation (do not run until evidence approved)

1. Review dry-run report under `/tmp/otaconskeep-classroom-dryrun/staging/*/DRY_RUN_REPORT.json`
2. Write `/var/lib/otaconskeep-classroom/state/ACTIVATION_APPROVED`
3. Set `DRY_RUN=0` in `/etc/otaconskeep-classroom.env` after reviewing writer model
4. `sudo ./install.sh --activate`

## Publication policy

Preferred: PR branch → checks → merge → Cloudflare deploy.  
`main` is currently **unprotected** on GitHub — direct-to-main remains blocked unless `ALLOW_DIRECT_MAIN=1` with explicit approval.

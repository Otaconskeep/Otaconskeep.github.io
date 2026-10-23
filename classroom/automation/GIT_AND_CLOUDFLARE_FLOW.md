# Safe Git + Cloudflare publication flow

## Canonical repository

**Source of truth:** `/root/otaconskeep-site` (`https://github.com/Otaconskeep/otaconskeep-site.git`)

**Mirror only:** `/root/Classroom` (`https://github.com/Otaconskeep/Classroom.git`) — one-way after approved publish. Dual dirty packs → fail closed (`lib/source_of_truth.py`).

## ALLOW_DIRECT_MAIN=0

Automation must not push commits straight to `main`.

## Workflows (separated)

| Workflow | File | Trigger | Job / check name | Purpose |
|---|---|---|---|---|
| classroom-validate | `.github/workflows/classroom-validate.yml` | `pull_request` → `main` | **`classroom-validate`** | Unit tests, schema/roadmap, secret scan, wrangler `--dry-run` |
| classroom-preview | `.github/workflows/classroom-preview.yml` | `pull_request` → `main` | **`classroom-preview`** | Generator sanity, welcome-page gates, Playwright smoke |
| Deploy Cloudflare | `.github/workflows/deploy-cloudflare.yml` | `push` → `main` only | `cloudflare-deploy` | **Production deploy after merge** — never a required PR check |

## Required ruleset on `main`

- Require pull request before merge
- Required approving review count: **0** (unattended publishing OK)
- Required status checks: **`classroom-validate`**, **`classroom-preview`**
- Block force pushes
- Block branch deletion
- **No bypass** for the automation account on failed checks
- Repository setting: allow auto-merge; use `gh pr merge --auto --squash` only when both required checks are green

## Automation identity permissions

- `contents: write` (push branches)
- `pull-requests: write`
- `checks: read` / `actions: read`
- Cloudflare secrets stay in GitHub Actions secrets — never in git

## Evidence retention

- Durable root: `/var/lib/otaconskeep-classroom/evidence/<run-id>/`
- Script: `classroom/automation/preserve_evidence.sh`
- Marker: `/var/lib/otaconskeep-classroom/evidence/KNOWN_GOOD_RUN_ID`
- Retention cleanup never deletes the known-good run

## Cloudflare production detection / rollback

- After merge to `main`: poll `gh pr view --json state,statusCheckRollup` then `gh run list --workflow deploy-cloudflare.yml` → conclusion `success`
- Workers deploy job name: `cloudflare-deploy` (not a required PR check)
- Rollback: redeploy prior known-good Worker via Actions/wrangler — **no force-push**
- Record `known_good=$(git rev-parse HEAD)` before merge for rollback targeting

## Auto-merge path policy

Unattended `gh pr merge --auto` is allowed **only** for lesson-content paths
(see `lib/automergable_paths.py`). Workflow, automation runtime, deploy, secrets,
and unrelated site files require **manual** merge. Draft PRs never auto-merge.

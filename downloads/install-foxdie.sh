#!/usr/bin/env bash
# install-foxdie.sh — Enable + verify FOXDIE on an existing otacon-executor deployment.
#
# FOXDIE is a module INSIDE otacon-executor, not a standalone program. This
# script does not install otacon-executor itself; it assumes a running
# otacon-executor container with the foxdie/ package already present in the
# image, and configures/verifies the three pieces that have to work together
# for it to actually do anything: the extraction dependency (unar), the
# daily job chain (scan -> triage -> self-fix), and the 24h deletion-hold
# sweep.
#
# Written 2026-09-28 after finding, live, that every one of those pieces can
# be individually "installed" (file present, route present, package listed
# in the Dockerfile) while the feature as a whole does nothing — see
# GAP-FOXDIE-TRIAGE-NEVER-RUNS in GAP_REGISTRY.md. This script's job is to
# make that failure mode structurally hard to reproduce: every step it takes
# is followed by a real check that the step actually took effect, not just
# that the command exited 0.
#
# Usage:
#   ./install-foxdie.sh              configure + verify (safe to re-run any time)
#   ./install-foxdie.sh --verify-only   check current state, change nothing
#   ./install-foxdie.sh --uninstall     remove the cron entries this script owns
#
# Exit code: 0 if the end state is healthy, 1 otherwise. Every check prints
# PASS/FAIL/SKIP on its own line so failures are greppable.
set -uo pipefail

CONTAINER="${OTACON_FOXDIE_CONTAINER:-otacon-executor}"
EXECUTOR_URL="${OTACON_EXECUTOR_URL:-http://localhost:5757}"
CRON_MARK="# --- managed by install-foxdie.sh ---"

VERIFY_ONLY=0
UNINSTALL=0
for arg in "$@"; do
  case "$arg" in
    --verify-only) VERIFY_ONLY=1 ;;
    --uninstall)   UNINSTALL=1 ;;
    -h|--help)
      sed -n '1,25p' "$0"; exit 0 ;;
  esac
done

PASS=0
FAIL=0
_pass() { echo "PASS  $1"; PASS=$((PASS+1)); }
_fail() { echo "FAIL  $1"; FAIL=$((FAIL+1)); }
_skip() { echo "SKIP  $1"; }
_info() { echo "..    $1"; }

# ── 0. Container reachable at all ─────────────────────────────────────────────
_info "Checking otacon-executor container..."
if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  _fail "container '$CONTAINER' is not running"
  echo
  echo "Nothing else can be checked without the container. Start it first:"
  echo "  docker start $CONTAINER   # or: docker compose up -d"
  exit 1
fi
_pass "container '$CONTAINER' is running"

if ! curl -s -m 10 -o /dev/null -w '' "$EXECUTOR_URL/health"; then
  _fail "otacon-executor did not respond at $EXECUTOR_URL/health"
  exit 1
fi
_pass "otacon-executor responds at $EXECUTOR_URL/health"

# ── 1. FOXDIE module actually loaded ──────────────────────────────────────────
_info "Checking FOXDIE module..."
STATUS_JSON="$(curl -s -m 15 "$EXECUTOR_URL/foxdie/status")"
if [[ -z "$STATUS_JSON" ]]; then
  _fail "GET /foxdie/status returned nothing. Is this an old image without the status route? Rebuild/redeploy otacon-executor first."
  exit 1
fi
INSTALLED="$(echo "$STATUS_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("installed", False))' 2>/dev/null)"
if [[ "$INSTALLED" != "True" ]]; then
  REASON="$(echo "$STATUS_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("reason",""))' 2>/dev/null)"
  _fail "FOXDIE module failed to load: ${REASON:-unknown reason}"
  exit 1
fi
_pass "FOXDIE module loaded"

if [[ "$UNINSTALL" -eq 1 ]]; then
  _info "Removing install-foxdie.sh-managed crontab entries..."
  TMP_CRON="$(mktemp)"
  crontab -l 2>/dev/null | awk -v mark="$CRON_MARK" '
    $0 == mark { skip=1; next }
    skip > 0 { skip--; next }
    { print }
  ' > "$TMP_CRON"
  crontab "$TMP_CRON"
  rm -f "$TMP_CRON"
  _pass "cron entries removed (unar and the FOXDIE module itself are left alone, this only disables the schedule)"
  echo
  echo "FOXDIE is now dormant: routes still work if you POST to them by hand, nothing runs on its own."
  exit 0
fi

# ── 2. unar present in the running container (not just the Dockerfile) ───────
_info "Checking unar (archive self-fix dependency)..."
UNAR_INSTALLED="$(echo "$STATUS_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("checks",{}).get("unar_installed", False))' 2>/dev/null)"
if [[ "$UNAR_INSTALLED" == "True" ]]; then
  _pass "unar is installed in the running container"
else
  if [[ "$VERIFY_ONLY" -eq 1 ]]; then
    _fail "unar is NOT installed in the running container (verify-only: not installing)"
  else
    _info "unar missing. The Dockerfile may list it, but if the running image predates that change (image/dependency drift, see GAP-FOXDIE-TRIAGE-NEVER-RUNS) it won't actually be there. Installing live now..."
    if docker exec -u root "$CONTAINER" bash -c "apt-get update -qq && apt-get install -y unar" >/tmp/install-foxdie-unar.log 2>&1; then
      if docker exec "$CONTAINER" which unar >/dev/null 2>&1; then
        _pass "unar installed live (durable until the container is next rebuilt, add it to the Dockerfile too if it isn't there, so a rebuild doesn't lose it again)"
      else
        _fail "apt-get reported success but 'which unar' still fails. See /tmp/install-foxdie-unar.log"
      fi
    else
      _fail "apt-get install unar failed. See /tmp/install-foxdie-unar.log"
    fi
  fi
fi

# ── 3. Scheduling: scan -> triage -> self-fix, in that order, plus sweep ──────
# Deliberately NOT wired through the internal schedules.json job scheduler:
# that scheduler is a single-threaded 30s-poll loop (otacon-job-scheduler
# systemd service) shared by every other scheduled job on the host (alarms,
# reminders, backups...). Triage/self-fix take minutes, not seconds; routing
# them through that loop would stall every unrelated scheduled job on the
# host for the duration. A dedicated host-crontab line with its own
# background curl call has no such blast radius. The scan itself
# (foxdie_media_integrity_job) is already scheduled that way from before —
# left alone here.
_info "Checking cron schedule (scan / triage / self-fix / sweep)..."

declare -A CRON_JOBS=(
  [triage]="10 3 * * * curl -s -m 900 -X POST ${EXECUTOR_URL}/foxdie/otacon/triage >> /var/log/foxdie-otacon-triage.log 2>&1"
  [self_fix]="25 3 * * * curl -s -m 900 -X POST ${EXECUTOR_URL}/foxdie/otacon/self-fix >> /var/log/foxdie-otacon-selffix.log 2>&1"
  [sweep]="*/30 * * * * curl -s -m 120 -X POST ${EXECUTOR_URL}/foxdie/otacon/sweep >> /var/log/foxdie-otacon-sweep.log 2>&1"
)

CURRENT_CRON="$(crontab -l 2>/dev/null || true)"
for job in "${!CRON_JOBS[@]}"; do
  line="${CRON_JOBS[$job]}"
  route="${line##*POST }"; route="${route%% *}"
  if echo "$CURRENT_CRON" | grep -qF "$route"; then
    _pass "cron entry for $job already present ($route)"
  else
    if [[ "$VERIFY_ONLY" -eq 1 ]]; then
      _fail "cron entry for $job is missing ($route) (verify-only: not adding)"
    else
      { crontab -l 2>/dev/null; echo "$CRON_MARK"; echo "$line"; } | crontab -
      CURRENT_CRON="$(crontab -l 2>/dev/null || true)"
      if echo "$CURRENT_CRON" | grep -qF "$route"; then
        _pass "cron entry for $job added ($route)"
      else
        _fail "tried to add cron entry for $job but it's not there after. Did the crontab write fail?"
      fi
    fi
  fi
done

if ! echo "$CURRENT_CRON" | grep -q 'foxdie_media_integrity_job\|/foxdie/run'; then
  _info "Note: the daily scan (foxdie_media_integrity_job) is scheduled through the internal scheduler (schedules.json), not host cron, so it won't show up in 'crontab -l'. Check via the Keep admin UI or GET ${EXECUTOR_URL}/foxdie/status after it's run once — this script can't add that entry for you, since it needs schedules.json, which lives inside the container's data volume, edited via the admin UI."
fi

# ── 4. Prove it, don't just configure it: trigger each step once and re-check status ──
if [[ "$VERIFY_ONLY" -eq 0 ]]; then
  _info "Triggering triage and self-fix once now, so 'installed' is proven by a real run, not just config presence (this can take several minutes, triage alone took about 6 minutes on the reference deployment)..."
  curl -s -m 900 -X POST "$EXECUTOR_URL/foxdie/otacon/triage" >/dev/null
  curl -s -m 900 -X POST "$EXECUTOR_URL/foxdie/otacon/self-fix" >/dev/null
  curl -s -m 120 -X POST "$EXECUTOR_URL/foxdie/otacon/sweep" >/dev/null
fi

echo
_info "Final verification via /foxdie/status..."
STATUS_JSON="$(curl -s -m 15 "$EXECUTOR_URL/foxdie/status")"
HEALTHY="$(echo "$STATUS_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("healthy", False))' 2>/dev/null)"
echo "$STATUS_JSON" | python3 -c '
import json, sys
d = json.load(sys.stdin)
for k, v in d.get("checks", {}).items():
    print(("PASS  " if v else "FAIL  ") + k)
'
if [[ "$HEALTHY" == "True" ]]; then
  _pass "overall: FOXDIE is installed and every component has run successfully and recently"
else
  _fail "overall: at least one component is missing, stale, or failing. See checks above"
fi

echo
echo "==================================================================="
echo "install-foxdie.sh: ${PASS} pass, ${FAIL} fail"
echo "Full status any time: curl -s ${EXECUTOR_URL}/foxdie/status | python3 -m json.tool"
echo "Disable/uninstall:    $0 --uninstall"
echo "==================================================================="

[[ "$FAIL" -eq 0 ]]

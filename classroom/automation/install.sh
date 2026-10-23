#!/usr/bin/env bash
# Idempotent installer for Homelab Academy classroom automation.
# Creates a dedicated venv (PEP 668 safe), installs systemd units DISABLED,
# and points ExecStart at the venv Python. Does NOT enable timers by default.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SITE_REPO="${CLASSROOM_SITE_REPO:-/root/otaconskeep-site}"
ENV_DST="/etc/otaconskeep-classroom.env"
STATE="/var/lib/otaconskeep-classroom"
LOG="/var/log/otaconskeep-classroom"
VENV="${CLASSROOM_VENV:-$STATE/venv}"
PYTHON_BIN="$VENV/bin/python"
ACTIVATE=0

for arg in "$@"; do
  case "$arg" in
    --activate) ACTIVATE=1 ;;
    --help|-h)
      echo "Usage: $0 [--activate]"
      echo "  Default: create venv, install units DISABLED, run unit tests."
      echo "  --activate: enable timers only when \$STATE/state/ACTIVATION_APPROVED exists."
      exit 0
      ;;
  esac
done

echo "== prerequisites =="
command -v python3 >/dev/null
command -v systemctl >/dev/null
python3 -c 'import venv' >/dev/null
[[ -d "$SITE_REPO/classroom/pack" ]] || { echo "missing site classroom pack: $SITE_REPO"; exit 1; }
[[ -d "$ROOT" ]] || exit 1

echo "== runtime dirs =="
install -d -m 0755 "$STATE/state" "$STATE/staging" "$STATE/artifacts" "$LOG"
touch "$STATE/classroom.publish.lock"
chmod 0644 "$STATE/classroom.publish.lock"

echo "== env file =="
if [[ ! -f "$ENV_DST" ]]; then
  cp "$ROOT/config.example.env" "$ENV_DST"
  if [[ -n "${OMNIROUTE_API_KEY:-}" ]]; then
    sed -i "s|^OMNIROUTE_API_KEY=.*|OMNIROUTE_API_KEY=${OMNIROUTE_API_KEY}|" "$ENV_DST"
  fi
  chmod 0640 "$ENV_DST"
  echo "Wrote $ENV_DST (mode 0640). Review WRITER_MODEL before activation."
else
  echo "Keeping existing $ENV_DST"
fi
# Ensure CLASSROOM_VENV is recorded for operators
if ! grep -q '^CLASSROOM_VENV=' "$ENV_DST" 2>/dev/null; then
  echo "CLASSROOM_VENV=$VENV" >>"$ENV_DST"
fi

echo "== python venv ($VENV) =="
if [[ ! -x "$PYTHON_BIN" ]]; then
  python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --upgrade pip setuptools wheel >/dev/null
python -m pip install -r "$ROOT/requirements.txt"
# Prove interpreter path for systemd
test -x "$PYTHON_BIN"
"$PYTHON_BIN" -c "import filelock, yaml, jsonschema, markdown; print('venv_ok', __import__('sys').executable)"

echo "== render systemd units from templates (venv python) =="
UNIT_DIR=/etc/systemd/system
install -d -m 0755 "$UNIT_DIR"
for tmpl in "$ROOT"/systemd/*.service.tmpl "$ROOT"/systemd/*.timer; do
  [[ -e "$tmpl" ]] || continue
  base="$(basename "$tmpl")"
  if [[ "$base" == *.service.tmpl ]]; then
    out_name="${base%.tmpl}"
    sed "s|@PYTHON@|$PYTHON_BIN|g; s|@AUTOMATION_ROOT@|$ROOT|g; s|@SITE_REPO@|$SITE_REPO|g" \
      "$tmpl" >"$UNIT_DIR/$out_name"
    chmod 0644 "$UNIT_DIR/$out_name"
    echo "installed $out_name -> ExecStart=$PYTHON_BIN ..."
  else
    install -m 0644 "$tmpl" "$UNIT_DIR/$base"
    echo "installed $base"
  fi
done
# Remove any stale hand-copied .service that might bypass venv if templates exist
systemctl daemon-reload

echo "== unit tests (venv) =="
cd "$ROOT"
"$PYTHON_BIN" tests/run_tests.py
"$PYTHON_BIN" tests/test_expanded.py
"$PYTHON_BIN" tests/test_fault_injection.py

echo "== dry-run helper (does not publish) =="
echo "Run: GENERATOR_BACKEND=curated DRY_RUN=1 $PYTHON_BIN $ROOT/run_dry_batch.py"

# Always leave timers disabled unless activate + approval
for u in otaconskeep-classroom-core-am.timer otaconskeep-classroom-core-late.timer otaconskeep-classroom-news.timer; do
  systemctl disable "$u" 2>/dev/null || true
  systemctl stop "$u" 2>/dev/null || true
done

if [[ "$ACTIVATE" -eq 1 ]]; then
  echo "Refusing --activate without \$STATE/state/ACTIVATION_APPROVED"
  if [[ -f "$STATE/state/ACTIVATION_APPROVED" ]]; then
    systemctl enable --now otaconskeep-classroom-core-am.timer
    systemctl enable --now otaconskeep-classroom-core-late.timer
    systemctl enable --now otaconskeep-classroom-news.timer
    systemctl list-timers 'otaconskeep-classroom*'
  else
    exit 2
  fi
else
  echo "Timers installed but DISABLED."
  systemctl list-timers --all 'otaconskeep-classroom*' || true
  for u in otaconskeep-classroom-core-am.timer otaconskeep-classroom-core-late.timer otaconskeep-classroom-news.timer; do
    echo "$u enabled=$(systemctl is-enabled "$u" 2>&1 || true) active=$(systemctl is-active "$u" 2>&1 || true)"
  done
fi

echo "OK — install complete (venv=$VENV; fail-closed; no publish)."

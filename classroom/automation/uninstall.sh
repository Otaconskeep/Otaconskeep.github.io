#!/usr/bin/env bash
# Remove only classroom automation units. Preserve lessons, repo, artifacts (unless --purge-artifacts).
set -euo pipefail

PURGE_ART=0
PURGE_ENV=0
for arg in "$@"; do
  case "$arg" in
    --purge-artifacts) PURGE_ART=1 ;;
    --purge-env) PURGE_ENV=1 ;;
  esac
done

UNITS=(
  otaconskeep-classroom-core-am.timer
  otaconskeep-classroom-core-late.timer
  otaconskeep-classroom-news.timer
  otaconskeep-classroom-core-am.service
  otaconskeep-classroom-core-late.service
  otaconskeep-classroom-news.service
  otaconskeep-classroom-batch.service
)

for u in "${UNITS[@]}"; do
  systemctl disable --now "$u" 2>/dev/null || true
  rm -f "/etc/systemd/system/$u"
done
systemctl daemon-reload

echo "Removed automation units."
echo "Preserved: git repos, published lessons under classroom/pack."
if [[ "$PURGE_ART" -eq 1 ]]; then
  rm -rf /var/lib/otaconskeep-classroom/artifacts
  echo "Purged artifacts."
else
  echo "Artifacts retained at /var/lib/otaconskeep-classroom/artifacts"
fi
if [[ "$PURGE_ENV" -eq 1 ]]; then
  rm -f /etc/otaconskeep-classroom.env
  echo "Removed env file."
else
  echo "Env retained at /etc/otaconskeep-classroom.env (use --purge-env to delete)."
fi

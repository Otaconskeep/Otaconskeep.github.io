#!/usr/bin/env bash
set -euo pipefail
ENV_FILE="${OMNIROUTE_ENV:-${OMNIROUTE_ENV:-./.env}}"
export OMNIROUTE_API_KEY="${OMNIROUTE_API_KEY:-$(grep OMNIROUTE_API_KEY "$ENV_FILE" | cut -d= -f2-)}"
export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-http://127.0.0.1:20128}"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-$OMNIROUTE_API_KEY}"
exec claude "$@"

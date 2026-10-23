#!/usr/bin/env bash
# Preserve dry-run evidence outside /tmp. Never deletes the most recent known-good.
set -euo pipefail
SRC_ROOT="${1:-/tmp/otaconskeep-classroom-dryrun}"
DEST_ROOT="${CLASSROOM_EVIDENCE_ROOT:-/var/lib/otaconskeep-classroom/evidence}"
RETENTION_DAYS="${EVIDENCE_RETENTION_DAYS:-45}"
KNOWN_GOOD_MARKER="${DEST_ROOT}/KNOWN_GOOD_RUN_ID"

mkdir -p "$DEST_ROOT"

copy_run() {
  local run_id="$1"
  local src="$2"
  local dest="$DEST_ROOT/$run_id"
  mkdir -p "$dest"
  if [[ -d "$src" ]]; then
    cp -a "$src/." "$dest/"
  fi
  # also pull matching zip from artifacts if present
  local art="/tmp/otaconskeep-classroom-dryrun/artifacts"
  if [[ -d "$art" ]]; then
    shopt -s nullglob
    for z in "$art"/*"${run_id}"*; do
      cp -a "$z" "$dest/"
    done
    shopt -u nullglob
  fi
  if [[ -f "$dest/CHECKSUMS.json" ]]; then
    :
  else
    python3 - <<PY
import hashlib, json
from pathlib import Path
root = Path("$dest")
rows = []
for p in sorted(root.rglob("*")):
    if p.is_file():
        rows.append({"path": str(p.relative_to(root)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size})
(root / "CHECKSUMS.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
print("wrote", root / "CHECKSUMS.json", "entries", len(rows))
PY
  fi
  echo "$run_id" > "$KNOWN_GOOD_MARKER"
  echo "preserved $run_id -> $dest (marked known-good)"
}

# Prefer explicit live dry run id if present
if [[ -d "$SRC_ROOT/evidence/live_dry_20260922T161500Z_remap" ]]; then
  copy_run "live_dry_20260922T161500Z_remap" "$SRC_ROOT/evidence/live_dry_20260922T161500Z_remap"
fi

# Copy other evidence run dirs
if [[ -d "$SRC_ROOT/evidence" ]]; then
  for d in "$SRC_ROOT/evidence"/live_dry_* "$SRC_ROOT/evidence"/dry_*; do
    [[ -d "$d" ]] || continue
    rid=$(basename "$d")
    [[ -d "$DEST_ROOT/$rid" ]] && continue
    copy_run "$rid" "$d"
  done
fi

# Top-level evidence files (auth proof, matrix, wrangler, activation)
mkdir -p "$DEST_ROOT/_shared"
for f in WRITER_AUTH_PROOF.json VERIFICATION_MATRIX.json wrangler_dryrun.log ACTIVATION_COMMAND.txt unittest_final.log; do
  if [[ -f "$SRC_ROOT/evidence/$f" ]]; then
    cp -a "$SRC_ROOT/evidence/$f" "$DEST_ROOT/_shared/"
  fi
done
if [[ -d "$SRC_ROOT/evidence/wrangler-dry" ]]; then
  cp -a "$SRC_ROOT/evidence/wrangler-dry" "$DEST_ROOT/_shared/"
fi

# Retention: delete old run dirs except known-good and anything newer than retention
KNOWN_GOOD=$(cat "$KNOWN_GOOD_MARKER" 2>/dev/null || true)
python3 - <<PY
import os, time, shutil
from pathlib import Path
root = Path("$DEST_ROOT")
known = "$KNOWN_GOOD"
days = int("$RETENTION_DAYS")
cutoff = time.time() - days * 86400
for p in root.iterdir():
    if not p.is_dir() or p.name.startswith("_"):
        continue
    if p.name == known:
        continue
    if p.stat().st_mtime >= cutoff:
        continue
    print("retention delete", p)
    shutil.rmtree(p)
print("retention complete; known-good=", known or "(none)")
PY

# Prefer successful remapped dry-run as known-good when present
if [[ -f "$DEST_ROOT/live_dry_20260922T161500Z_remap/DRY_RUN_REPORT.json" ]]; then
  echo "live_dry_20260922T161500Z_remap" > "$KNOWN_GOOD_MARKER"
elif [[ -f "$DEST_ROOT/KNOWN_GOOD_RUN_ID" ]]; then
  :
fi

echo "DEST_ROOT=$DEST_ROOT"
ls -la "$DEST_ROOT"

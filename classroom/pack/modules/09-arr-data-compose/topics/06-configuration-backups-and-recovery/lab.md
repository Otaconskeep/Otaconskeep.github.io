# Lab: Configuration Backups and Recovery

**Module:** ARR Data Model & Compose
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain why a configuration archive alone is not a complete recovery strategy.

## Before you start

- Comfort using a Linux shell and absolute paths.
- Basic understanding of files, directories, archives, and checksums.
- Ability to read simple JSON and INI configuration formats.
- GNU tar, GNU coreutils, find, xargs, and Python 3 installed.
- Permission to create files and directories under /opt/lab-classroom/class39/.

## Guided lab

### objective
Create and test a configuration backup lifecycle without writing outside /opt/lab-classroom/class39/.

### safety_boundary
Every filesystem mutation in this lab is explicitly located beneath /opt/lab-classroom/class39/. The attempt1 directory is created without a forceful cleanup operation; if it already exists, stop and choose a new attempt directory under the same classroom root after reviewing the previous work.

### steps
Create a fresh workspace, sample configuration, and semantic validator:
BASE=/opt/lab-classroom/class39/attempt1
mkdir -p /opt/lab-classroom/class39
mkdir "$BASE"
mkdir "$BASE/config" "$BASE/backups" "$BASE/staging" "$BASE/restore" "$BASE/rollback"
cat > "$BASE/config/app.json" <<'EOF'
{
  "service_name": "inventory",
  "listen_port": 8080,
  "feature_enabled": true
}
EOF
cat > "$BASE/config/service.ini" <<'EOF'
[service]
workers = 4
log_level = INFO
EOF
cat > "$BASE/validate.py" <<'PY'
import configparser
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
with (root / "app.json").open(encoding="utf-8") as handle:
    app = json.load(handle)
required = {"service_name", "listen_port", "feature_enabled"}
missing = required.difference(app)
if missing:
    raise SystemExit(f"missing JSON keys: {sorted(missing)}")
if app["service_name"] != "inventory":
    raise SystemExit("unexpected service_name")
if not isinstance(app["listen_port"], int) or isinstance(app["listen_port"], bool):
    raise SystemExit("listen_port must be an integer")
if not 1024 <= app["listen_port"] <= 65535:
    raise SystemExit("listen_port is outside the approved range")
if not isinstance(app["feature_enabled"], bool):
    raise SystemExit("feature_enabled must be Boolean")
parser = configparser.ConfigParser()
loaded = parser.read(root / "service.ini", encoding="utf-8")
if len(loaded) != 1 or not parser.has_section("service"):
    raise SystemExit("service.ini is missing the service section")
workers = parser.getint("service", "workers")
if not 1 <= workers <= 32:
    raise SystemExit("workers is outside the approved range")
if parser.get("service", "log_level") not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
    raise SystemExit("unsupported log_level")
print(f"validated configuration at {root}")
PY
python3 "$BASE/validate.py" "$BASE/config"
Assemble the package, generate a manifest, record metadata, create the archive, and generate a checksum for the archive:
BASE=/opt/lab-classroom/class39/attempt1
mkdir "$BASE/staging/package"
cp -a "$BASE/config" "$BASE/staging/package/config"
printf '%s\n' 'class_id=39' 'backup_version=1' 'source=config' 'format=tar-gzip' > "$BASE/staging/package/BACKUP_INFO.txt"
(
  cd "$BASE/staging/package"
  find config -type f -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256
)
tar -C "$BASE/staging/package" -czf "$BASE/backups/config-backup-v1.tar.gz" .
sha256sum "$BASE/backups/config-backup-v1.tar.gz" > "$BASE/backups/config-backup-v1.tar.gz.sha256"
Verify the backup before simulating any failure:
BASE=/opt/lab-classroom/class39/attempt1
sha256sum -c "$BASE/backups/config-backup-v1.tar.gz.sha256"
tar -tzf "$BASE/backups/config-backup-v1.tar.gz"
(
  cd "$BASE/staging/package"
  sha256sum -c MANIFEST.sha256
)
python3 "$BASE/validate.py" "$BASE/staging/package/config"
Introduce configuration drift that remains syntactically and semantically valid, then demonstrate that only comparison with the trusted backup manifest detects it:
BASE=/opt/lab-classroom/class39/attempt1
cat > "$BASE/config/app.json" <<'EOF'
{
  "service_name": "inventory",
  "listen_port": 9090,
  "feature_enabled": false
}
EOF
python3 "$BASE/validate.py" "$BASE/config"
mkdir "$BASE/restore/candidate"
tar -C "$BASE/restore/candidate" -xzf "$BASE/backups/config-backup-v1.tar.gz"
if (
  cd "$BASE"
  sha256sum -c restore/candidate/MANIFEST.sha256
); then
  echo 'ERROR: drift was not detected'
  exit 1
else
  echo 'Expected result: active configuration differs from the backup manifest'
fi
Validate the isolated recovery candidate before promotion:
BASE=/opt/lab-classroom/class39/attempt1
sha256sum -c "$BASE/backups/config-backup-v1.tar.gz.sha256"
(
  cd "$BASE/restore/candidate"
  sha256sum -c MANIFEST.sha256
)
python3 "$BASE/validate.py" "$BASE/restore/candidate/config"
cat "$BASE/restore/candidate/BACKUP_INFO.txt"
Preserve the pre-recovery state and promote the validated candidate using directory renames within the same filesystem:
BASE=/opt/lab-classroom/class39/attempt1
cp -a "$BASE/config" "$BASE/rollback/pre-recovery-config"
mv "$BASE/config" "$BASE/config.drifted"
mv "$BASE/restore/candidate/config" "$BASE/config"
python3 "$BASE/validate.py" "$BASE/config"
(
  cd "$BASE/restore/candidate"
  sha256sum -c MANIFEST.sha256
)
Compare the promoted configuration with the retained drifted state and inspect the final recovery artifacts:
BASE=/opt/lab-classroom/class39/attempt1
printf '%s\n' 'Promoted port:'
python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["listen_port"])' "$BASE/config/app.json"
printf '%s\n' 'Retained pre-recovery port:'
python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["listen_port"])' "$BASE/config.drifted/app.json"
find "$BASE" -maxdepth 3 -type f -print | sort

## Expected results

- The original configuration passes semantic validation with listen_port set to 8080, workers set to 4, and an approved log level.
- The backup package contains config/app.json, config/service.ini, BACKUP_INFO.txt, and MANIFEST.sha256.
- The archive checksum reports an OK result before extraction.
- The staged package files pass the manifest check.
- The drifted configuration still passes semantic validation because port 9090 and the changed Boolean are allowed values.
- Comparison of the drifted active configuration with the backup manifest reports a checksum mismatch for config/app.json.
- The isolated recovery candidate passes both manifest verification and semantic validation.
- After promotion, the active app.json again contains listen_port 8080.
- The pre-recovery state remains available in config.drifted and rollback/pre-recovery-config, where app.json contains listen_port 9090.
- No lab-created file is located outside /opt/lab-classroom/class39/.

## Verification

- [ ] Run `sha256sum -c /opt/lab-classroom/class39/attempt1/backups/config-backup-v1.tar.gz.sha256`; the archive must report OK.
- [ ] Run `tar -tzf /opt/lab-classroom/class39/attempt1/backups/config-backup-v1.tar.gz`; confirm that the two configuration files, metadata file, and manifest are listed.
- [ ] Run `cd /opt/lab-classroom/class39/attempt1 && sha256sum -c restore/candidate/MANIFEST.sha256`; both active configuration files must report OK after promotion.
- [ ] Run `python3 /opt/lab-classroom/class39/attempt1/validate.py /opt/lab-classroom/class39/attempt1/config`; it must print a successful validation message.
- [ ] Run `python3 -c 'import json; print(json.load(open("/opt/lab-classroom/class39/attempt1/config/app.json", encoding="utf-8"))["listen_port"])'`; the result must be 8080.
- [ ] Run `python3 -c 'import json; print(json.load(open("/opt/lab-classroom/class39/attempt1/config.drifted/app.json", encoding="utf-8"))["listen_port"])'`; the result must be 9090.
- [ ] Run `find /opt/lab-classroom/class39/attempt1 -maxdepth 3 -type f -print | sort` and account for the active configuration, archive, checksum, staging package, candidate metadata, validator, and rollback copies.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Creating attempt1 reports that the file or directory already exists. | A previous lab attempt is still present. | Do not overwrite it blindly. Inspect the previous artifacts, then use a new directory such as /opt/lab-classroom/class39/attempt2 and consistently substitute that path throughout the lab. |
| The shell reports permission denied while creating the classroom directory. | The current account lacks write permission under /opt/lab-classroom/. | Ask the homelab administrator to provision the classroom root with appropriate ownership. Do not redirect the exercise into an unrelated system directory. |
| The archive checksum reports FAILED or cannot find the archive. | The archive changed, the sidecar references a different absolute path, or the archive creation step did not complete. | Confirm both files exist under the attempt's backups directory. Treat a real mismatch as an integrity failure and rebuild the backup from a known-good staged package rather than proceeding with recovery. |
| Manifest verification cannot find config/app.json. | The command was run from the wrong working directory because manifest paths are relative to the package root. | Run the check from staging/package when testing the source package, from restore/candidate when testing the candidate, or from the attempt root when intentionally comparing the active config with the candidate manifest. |
| The drift comparison exits unsuccessfully and prints a checksum warning. | The lab intentionally changed app.json after the backup. | This is the expected drift-detection result. Continue only if the mismatch is limited to the intentionally changed file. |
| Python reports a JSON parsing error. | app.json has malformed punctuation, quoting, or value syntax. | Compare the file with the lesson's intended content. Recover the archived copy into the candidate directory and validate that copy before promotion. |
| The validator rejects workers, log_level, or listen_port even though parsing succeeds. | The file is syntactically valid but violates the lab's semantic policy. | Review the validator's allowed ranges and values. Use a backup known to match the intended application policy rather than bypassing the check. |
| Promotion reports that config.drifted already exists. | The promotion step was already run or a previous partial attempt used the same workspace. | Stop and inspect config, config.drifted, and rollback/pre-recovery-config. Determine which tree is active and validated before selecting a fresh attempt directory for another run. |

## Security

### principles
Treat configuration backups as sensitive because they may contain credentials, tokens, private endpoints, account names, and topology information.
Grant backup creation, retrieval, and restoration rights separately when operational roles permit.
Protect archive checksums or manifests independently; integrity data stored beside a writable archive does not prevent coordinated replacement.
Use signed manifests, independently controlled storage, or immutable retention for higher-assurance recovery.
Do not place real secrets in this classroom exercise.
Record who created, approved, retrieved, validated, and promoted production backups.
Test recovered configuration against a compatible application version before activation.

### confidentiality_note
Compression is not encryption. A compressed configuration archive requires an additional approved encryption and key-management design when it contains confidential material.

### integrity_note
A checksum detects changes relative to the checksum value supplied to the verifier. It does not identify the author or prove that the checksum itself is trustworthy.

### availability_note
Maintain multiple recovery generations and at least one independently controlled copy so that corruption, operator mistakes, or compromise of the primary host does not eliminate every recovery point.

## Rollback

### when_to_use
Use rollback if post-promotion validation fails, if an application rejects the recovered configuration, or if the recovered version does not match the deployed application.

### preconditions
Confirm that /opt/lab-classroom/class39/attempt1/config.drifted exists.
Confirm that the currently active config directory is the recovered version.
Record the reason for rollback and any observed validation failure.

### commands
BASE=/opt/lab-classroom/class39/attempt1
mv "$BASE/config" "$BASE/config.recovered-v1"
mv "$BASE/config.drifted" "$BASE/config"
python3 "$BASE/validate.py" "$BASE/config"

### expected_state
The drifted pre-recovery configuration is active again under config/, while the recovered version remains available under config.recovered-v1 for investigation.

### caution
This classroom rollback restores files only. A real service may require a separately approved reload, restart, health check, and dependency validation procedure.

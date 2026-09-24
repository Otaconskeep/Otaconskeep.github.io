# Class 39 — Configuration Backups and Recovery

**Learning objective:** Explain why a configuration archive alone is not a complete recovery strategy.; Create a versioned configuration backup with a manifest and archive checksum.; Distinguish archive integrity, file integrity, syntax validation, and semantic validation.; Detect valid-looking configuration drift by comparing files with a trusted manifest.; Restore into a candidate directory instead of immediately overwriting the active configuration.; Promote a validated recovery candidate using same-filesystem directory renames.; Retain a pre-recovery copy and perform a controlled rollback.; Describe how retention, access control, secret handling, and restore testing affect backup reliability.
**Bloom level:** Understand / Apply
**Track:** Homelab Operations and Reliability · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach a repeatable, verifiable process for backing up configuration files, detecting configuration drift, validating recovery candidates, promoting a recovered configuration, and rolling back an unsuccessful recovery without touching files outside the classroom directory.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-20
**Compatibility:** ### operating_systems
Linux distributions providing GNU coreutils and GNU tar

### required_tools
POSIX-compatible shell
GNU tar
GNU sha256sum
GNU find
GNU sort
GNU xargs
Python 3.8 or newer

### notes
The use of null-delimited find, sort, and xargs input assumes GNU-compatible implementations.
The archive checksum sidecar records the absolute classroom archive path and should be checked on the same lab host unless regenerated through a trusted process.
Directory rename behavior is expected to remain on one filesystem because all paths are under a single attempt directory.
The sample validator uses only Python standard-library modules.

## Learning objective

- Explain why a configuration archive alone is not a complete recovery strategy.
- Create a versioned configuration backup with a manifest and archive checksum.
- Distinguish archive integrity, file integrity, syntax validation, and semantic validation.
- Detect valid-looking configuration drift by comparing files with a trusted manifest.
- Restore into a candidate directory instead of immediately overwriting the active configuration.
- Promote a validated recovery candidate using same-filesystem directory renames.
- Retain a pre-recovery copy and perform a controlled rollback.
- Describe how retention, access control, secret handling, and restore testing affect backup reliability.

## Why this matters

Teach a repeatable, verifiable process for backing up configuration files, detecting configuration drift, validating recovery candidates, promoting a recovered configuration, and rolling back an unsuccessful recovery without touching files outside the classroom directory.

## Prerequisites

- Comfort using a Linux shell and absolute paths.
- Basic understanding of files, directories, archives, and checksums.
- Ability to read simple JSON and INI configuration formats.
- GNU tar, GNU coreutils, find, xargs, and Python 3 installed.
- Permission to create files and directories under /opt/lab-classroom/class39/.

## Required reading

- GNU tar manual, tutorial and archive operations: https://www.gnu.org/software/tar/manual/
- GNU Coreutils manual, sha2 utilities: https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html
- Python documentation, json module: https://docs.python.org/3/library/json.html
- Python documentation, configparser module: https://docs.python.org/3/library/configparser.html
- NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/pubs/sp/800/34/r1/final

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| configuration backup | A captured copy of configuration state, normally accompanied by version, source, integrity, and retention information. |
| recovery point objective | The maximum acceptable amount of configuration history that could be lost, usually expressed as a period of time. |
| recovery time objective | The target amount of time allowed to restore a usable configuration after a failure. |
| manifest | A list of expected files and associated metadata such as cryptographic checksums. |
| integrity check | A test that determines whether bytes have changed since a trusted checksum was created. |
| syntax validation | A check that confirms a file can be parsed according to its data format. |
| semantic validation | A check that confirms parsed values meet application-specific rules, ranges, and required relationships. |
| configuration drift | A difference between the intended configuration and the configuration currently present on a system. |
| recovery candidate | Restored content held in an isolated location while integrity and application-specific checks are performed. |
| promotion | The controlled action that makes a validated recovery candidate the active configuration. |
| rollback | The process of returning to the state that existed immediately before a change or recovery attempt. |

## Instruction

A useful configuration backup is more than a compressed copy of a directory. A recovery operator must know what was captured, which system or service it belongs to, when it was captured, whether the archive remained intact, and whether the restored files are usable. These requirements create several separate validation layers. An archive listing proves that the container can be read, but it does not prove that the files express valid settings. A cryptographic checksum detects byte changes, but a perfectly intact file can still contain an invalid port, a missing required key, or a value incompatible with the installed application version. Syntax validation confirms that a parser accepts the document. Semantic validation then checks rules meaningful to the service, such as an integer being within an allowed range.

Recovery should be staged. Extracting directly over an active configuration mixes backup extraction, validation, and activation into one difficult-to-reverse operation. Instead, restore into a candidate directory, verify the archive checksum, verify the manifest, inspect metadata, parse the files, and apply semantic checks. Only after those gates pass should the candidate be promoted. Keeping the old configuration under a distinct name provides a rapid rollback path. Renaming directories on the same filesystem also reduces the interval in which an incomplete tree could be visible, although application behavior and open file handles still determine whether a restart or reload is required.

Checksums establish integrity relative to a trusted checksum, not authenticity by themselves. If an attacker can replace both an archive and its checksum, the pair can still verify. Higher-assurance environments should protect manifests with signing, immutable storage, restricted backup credentials, or an independently controlled backup system. Configuration backups may also contain passwords, API tokens, private keys, internal addresses, or identity-provider details. They therefore require access restrictions, retention limits, secure transfer, and tested destruction procedures.

The final measure of backup quality is a successful restore test. A job reporting that it created an archive only proves that a command completed. Regular drills should recover a representative version, validate it against the target software version, and document the time and decisions required. This lab models that workflow entirely under one classroom path: establish a known configuration, create a manifest and archive, introduce legitimate-looking drift, recover to an isolated candidate, validate it, promote it, and preserve a rollback route.

## Architecture

### scope_root
/opt/lab-classroom/class39/attempt1/

### components
config/: active configuration used as the source of the backup and later as the promoted recovery target.
staging/package/: immutable-in-practice package layout assembled before archive creation.
backups/: compressed archive and its independently stored archive checksum.
restore/candidate/: isolated extraction location used for recovery validation.
rollback/: retained copy of the configuration immediately before promotion.
validate.py: read-only semantic validator for the JSON and INI examples.

### data_flow
Known configuration is written under config/.
Configuration is copied into staging/package/config/.
A deterministic file manifest is generated relative to the package root.
Package contents are archived under backups/ and the archive receives a separate checksum.
The active configuration is changed to model drift.
The archive is extracted into restore/candidate/ and validated before activation.
The drifted configuration is retained, and the candidate configuration is renamed into the active location.

### trust_boundaries
The archive checksum is useful only while its sidecar file is obtained from a trusted location.
The manifest verifies packaged configuration bytes but does not establish who created them.
The validator represents application-specific policy and must evolve when configuration schemas change.
Promotion does not automatically reload a real service; service lifecycle actions require a separate, service-specific runbook.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Create a second attempt under /opt/lab-classroom/class39/attempt2/. Add a third configuration file in a format Python can parse, include it in the package manifest, and extend the validator with at least two semantic rules. Create two backup generations with clearly different metadata, introduce drift, recover the older generation into a candidate directory, and document why selecting that generation is justified.

### deliverables
A short recovery runbook stored beneath the attempt2 directory.
Two versioned backup archives with separate archive checksums.
A manifest for each generation.
A validator that checks all three configuration files.
A text record of the integrity, syntax, semantic, promotion, and rollback checks performed.
A retention proposal specifying how many generations to keep and why.

### constraints
All filesystem changes must remain under /opt/lab-classroom/class39/.
Do not use real credentials or production configuration.
Do not activate a candidate until every documented validation gate passes.
Preserve the pre-recovery state until the exercise is fully verified.

## Feynman teach-back

### prompt
Explain the recovery process to a new homelab operator without using the words archive, checksum, manifest, or atomic.

### model_explanation
First, make a packaged copy of the settings and keep a trusted list of what every copied file should look like. When recovery is needed, unpack the copy into a separate waiting area rather than placing it directly over the live settings. Confirm that nothing changed, make sure each file can be read, and check that the values make sense for the application. Keep the current settings under another name, then move the tested copy into place. If the recovered settings cause trouble, move the previous settings back.

### self_check
Did the explanation distinguish detecting changed bytes from checking whether values make sense?
Did it explain why recovery uses a separate candidate location?
Did it retain a way to return to the pre-recovery state?
Did it avoid claiming that successful file recovery automatically proves service health?

## Retrieval check

1. 1. Why is successful creation of a compressed configuration file insufficient proof that recovery will work?
2. 2. What is the difference between an archive checksum and semantic configuration validation?
3. 3. Why should a backup normally be restored into a candidate directory before it replaces active configuration?
4. 4. In the lab, why does the drifted app.json pass the Python validator but fail comparison with the backup manifest?
5. 5. What security limitation remains when an archive and its checksum are writable by the same compromised account?
6. 6. What is the purpose of retaining config.drifted and rollback/pre-recovery-config during promotion?
7. 7. Why should relative paths in a checksum manifest be verified from the intended package root?
8. 8. What does a successful configuration promotion fail to prove about a real application?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

In this class we build a complete configuration recovery workflow rather than stopping after archive creation. The workspace is confined to the Class 39 classroom directory. We begin with a small JSON application file and an INI service file. A Python validator parses both formats and enforces policy: required JSON keys must exist, the port must be an integer in the approved range, the feature flag must be Boolean, the worker count must be reasonable, and the log level must be approved.

Next, we copy the known-good configuration into a staging package. We create a cryptographic manifest for the configuration files and add simple package metadata. The package becomes a compressed backup, and the completed archive receives a separate checksum. These controls answer different questions. The outer checksum asks whether the archive bytes changed. The inner manifest asks whether the recovered configuration files match the captured versions. The Python validator asks whether those files make sense to the application.

We then model configuration drift by changing the port from 8080 to 9090 and disabling a feature. Those values are still valid, so semantic validation succeeds. That is intentional: a valid file is not necessarily the intended file. Comparing the active configuration with the trusted backup manifest detects the difference.

For recovery, we extract into a candidate directory. We verify the archive again, verify every file listed in the manifest, run semantic validation, and inspect the metadata. Only then do we promote the candidate. Before promotion, we retain the current configuration. Directory renames place the tested candidate into the active path while preserving the previous state for rollback.

The lesson ends by verifying both versions: the promoted configuration contains port 8080, while the retained pre-recovery copy contains port 9090. In a production runbook, this file-level process would be followed by application-specific reload, health, dependency, and functional checks. Remember that checksums are not signatures, compression is not encryption, and a backup is trustworthy only when its restore process is repeatedly tested.

## References

- GNU tar manual: https://www.gnu.org/software/tar/manual/
- GNU Coreutils sha2 utilities: https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html
- GNU Coreutils sha2 invocation: https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html
- Python json module documentation: https://docs.python.org/3/library/json.html
- Python configparser documentation: https://docs.python.org/3/library/configparser.html
- Python pathlib documentation: https://docs.python.org/3/library/pathlib.html
- NIST SP 800-34 Rev. 1: https://csrc.nist.gov/pubs/sp/800/34/r1/final
- CISA Stop Ransomware Guide, backup and recovery guidance: https://www.cisa.gov/stopransomware/ransomware-guide

## Mastery gate

- [ ] Objectives demonstrated with evidence
- [ ] Feynman complete
- [ ] Quiz self-scored ≥80%
- [ ] Lab verification boxes checked
- [ ] Rollback understood

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Return to this class whenever a later service fails for identity, process, log, remote access, update, or routing reasons covered here.

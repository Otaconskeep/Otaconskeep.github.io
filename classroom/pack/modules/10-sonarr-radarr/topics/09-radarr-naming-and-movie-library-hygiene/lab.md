# Lab: Radarr Naming and Movie Library Hygiene

**Module:** Sonarr & Radarr
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain the difference between a movie folder format and a movie file format in Radarr.

## Before you start

- Basic familiarity with Radarr movies, root folders, and the Media Management settings page
- Ability to run shell and Python 3 commands on a Linux host
- Understanding of files, directories, extensions, hard links, and symbolic links
- Completion of introductory storage and media-library organization lessons
- Write access to /opt/lab-classroom/class48/

## Guided lab

### scope
All files created or modified by this lab remain under /opt/lab-classroom/class48/. The lab does not connect to Radarr or rename a production media file.

### scenario
A synthetic movie library contains inconsistent folder names, weak file names, sidecar files, duplicate-title movies from different years, and one edition. You will build an inventory and calculate deterministic destination paths from an authoritative fixture manifest.

### steps
### step
1

### title
Create the isolated fixture library

### instructions
Run the following command. It creates small text fixtures with media-like extensions; it does not create or copy real video content.

### command
python3 - <<'PY'
from pathlib import Path
import json
root = Path('/opt/lab-classroom/class48')
assert str(root) == '/opt/lab-classroom/class48'
library = root / 'library'
reports = root / 'reports'
backups = root / 'backups'
for path in (library, reports, backups):
    path.mkdir(parents=True, exist_ok=True)
fixtures = [
    {
        'source': 'Arrival (2016)/Arrival.2016.mkv',
        'title': 'Arrival', 'year': 2016, 'tmdb_id': 329865,
        'quality': 'Bluray-1080p', 'edition': ''
    },
    {
        'source': 'Dune 2021/Dune.2021.1080p.mkv',
        'title': 'Dune', 'year': 2021, 'tmdb_id': 438631,
        'quality': 'WEBDL-1080p', 'edition': ''
    },
    {
        'source': 'The Thing/thing_final.mkv',
        'title': 'The Thing', 'year': 1982, 'tmdb_id': 1091,
        'quality': 'Bluray-1080p', 'edition': ''
    },
    {
        'source': 'Blade Runner 1982/BR-final-cut.mkv',
        'title': 'Blade Runner', 'year': 1982, 'tmdb_id': 78,
        'quality': 'Bluray-1080p', 'edition': "Final Cut"
    },
    {
        'source': 'Crash 1996/Crash.mkv',
        'title': 'Crash', 'year': 1996, 'tmdb_id': 884,
        'quality': 'DVD', 'edition': ''
    },
    {
        'source': 'Crash 2004/Crash.mp4',
        'title': 'Crash', 'year': 2004, 'tmdb_id': 1640,
        'quality': 'WEBDL-1080p', 'edition': ''
    }
]
for item in fixtures:
    target = library / item['source']
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('synthetic class 48 fixture\n', encoding='utf-8')
(library / 'Arrival (2016)' / 'Arrival.2016.en.srt').write_text('1\n00:00:00,000 --> 00:00:01,000\nSynthetic subtitle\n', encoding='utf-8')
(library / 'Dune 2021' / 'poster.jpg').write_text('synthetic artwork fixture\n', encoding='utf-8')
(root / 'manifest.json').write_text(json.dumps(fixtures, indent=2), encoding='utf-8')
print(root)
print(f'Fixture records: {len(fixtures)}')
PY
### step
2

### title
Inventory the synthetic library

### instructions
Review every fixture path before proposing a change.

### command
find /opt/lab-classroom/class48/library -type f -printf '%P\n' | sort
### step
3

### title
Create a dry-run naming audit

### instructions
Create an audit program that derives proposed paths from manifest metadata, checks source existence, validates video extensions, examines Unicode normalization, and detects destination collisions.

### command
cat > /opt/lab-classroom/class48/audit_naming.py <<'PY'
from pathlib import Path
import csv
import json
import re
import unicodedata

ROOT = Path('/opt/lab-classroom/class48')
if str(ROOT) != '/opt/lab-classroom/class48':
    raise SystemExit('Unexpected lab root')
LIBRARY = ROOT / 'library'
REPORT = ROOT / 'reports' / 'naming-audit.csv'
SUMMARY = ROOT / 'reports' / 'summary.txt'
VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.m4v'}

def clean_component(value):
    value = unicodedata.normalize('NFC', value)
    value = re.sub(r'[\x00-\x1f]', '', value)
    value = value.replace('/', ' - ')
    return value.strip().rstrip('.')

records = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
rows = []
proposed_paths = {}
for record in records:
    source_relative = Path(record['source'])
    source = LIBRARY / source_relative
    title = clean_component(record['title'])
    year = int(record['year'])
    tmdb_id = int(record['tmdb_id'])
    quality = clean_component(record['quality'])
    edition = clean_component(record.get('edition', ''))
    folder = f'{title} ({year}) [tmdb-{tmdb_id}]'
    edition_text = f' - {edition}' if edition else ''
    filename = f'{title} ({year}){edition_text} - {quality}{source.suffix.lower()}'
    proposed = Path(folder) / filename
    warnings = []
    if not source.exists():
        warnings.append('SOURCE_MISSING')
    if source.suffix.lower() not in VIDEO_EXTENSIONS:
        warnings.append('UNEXPECTED_VIDEO_EXTENSION')
    if str(source_relative) != unicodedata.normalize('NFC', str(source_relative)):
        warnings.append('SOURCE_NOT_NFC')
    key = unicodedata.normalize('NFC', str(proposed)).casefold()
    proposed_paths.setdefault(key, []).append(str(source_relative))
    rows.append({
        'source': str(source_relative),
        'proposed': str(proposed),
        'status': 'WARN' if warnings else 'OK',
        'notes': ';'.join(warnings)
    })
collisions = {key: value for key, value in proposed_paths.items() if len(value) > 1}
for row in rows:
    key = unicodedata.normalize('NFC', row['proposed']).casefold()
    if key in collisions:
        row['status'] = 'BLOCK'
        row['notes'] = ';'.join(filter(None, [row['notes'], 'DESTINATION_COLLISION']))
REPORT.parent.mkdir(parents=True, exist_ok=True)
with REPORT.open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=['source', 'proposed', 'status', 'notes'])
    writer.writeheader()
    writer.writerows(rows)
summary_lines = [
    f'Records: {len(rows)}',
    f'OK: {sum(row["status"] == "OK" for row in rows)}',
    f'WARN: {sum(row["status"] == "WARN" for row in rows)}',
    f'BLOCK: {sum(row["status"] == "BLOCK" for row in rows)}',
    f'Collisions: {len(collisions)}',
    'No media paths were renamed.'
]
SUMMARY.write_text('\n'.join(summary_lines) + '\n', encoding='utf-8')
print('\n'.join(summary_lines))
PY
python3 /opt/lab-classroom/class48/audit_naming.py
### step
4

### title
Review the complete path mapping

### instructions
Inspect every source and proposed destination. Treat any BLOCK row as a stop condition for a real migration.

### command
python3 - <<'PY'
from pathlib import Path
import csv
report = Path('/opt/lab-classroom/class48/reports/naming-audit.csv')
with report.open(encoding='utf-8', newline='') as handle:
    for row in csv.DictReader(handle):
        print(f"{row['status']:5} | {row['source']} -> {row['proposed']} | {row['notes']}")
PY
### step
5

### title
Identify unmanaged sidecars

### instructions
Compare the complete filesystem inventory with the manifest's primary movie files. Sidecars are not automatically bad, but a cleanup plan must account for them.

### command
python3 - <<'PY'
from pathlib import Path
import json
root = Path('/opt/lab-classroom/class48')
library = root / 'library'
managed = {item['source'] for item in json.loads((root / 'manifest.json').read_text(encoding='utf-8'))}
all_files = {str(path.relative_to(library)) for path in library.rglob('*') if path.is_file()}
for path in sorted(all_files - managed):
    print(f'SIDECAR | {path}')
PY
### step
6

### title
Translate the audit into a Radarr change plan

### instructions
In a real Radarr instance, compare the policy with the live naming preview. Confirm token support, inspect unmapped files, correct metadata, select one low-impact movie as a pilot, and use Radarr's supported organize or rename workflow. Do not apply production changes as part of this lab.

## Expected results

- The directory /opt/lab-classroom/class48/ contains a synthetic library, manifest, audit program, and reports.
- The inventory lists six synthetic primary movie files and two sidecar files.
- The naming audit reports six records and states that no media paths were renamed.
- Every proposed movie folder includes a title, release year, and TMDB identifier derived from the fixture manifest.
- The two movies titled Crash produce different destinations because their years and identifiers differ.
- Blade Runner includes its Final Cut edition in the proposed file name.
- The sidecar audit identifies the subtitle and poster fixtures without classifying them as primary movie files.
- The supplied fixture set produces no destination collision; a future collision would be marked BLOCK.

## Verification

- [ ] Run `test -f /opt/lab-classroom/class48/reports/naming-audit.csv && echo PASS` and confirm that PASS is printed.
- [ ] Run `cat /opt/lab-classroom/class48/reports/summary.txt` and confirm that it ends with `No media paths were renamed.`
- [ ] Run `grep -c '^' /opt/lab-classroom/class48/reports/naming-audit.csv` and confirm that the result is 7: one header and six data rows.
- [ ] Run `grep -F 'Blade Runner (1982) - Final Cut - Bluray-1080p.mkv' /opt/lab-classroom/class48/reports/naming-audit.csv` and confirm that a matching row is returned.
- [ ] Run `grep -F '[tmdb-884]' /opt/lab-classroom/class48/reports/naming-audit.csv` and `grep -F '[tmdb-1640]' /opt/lab-classroom/class48/reports/naming-audit.csv`; confirm that both Crash records have distinct identifiers.
- [ ] Run `find /opt/lab-classroom/class48/library -type f -printf '%P\n' | sort` and confirm that original fixture names remain unchanged.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The setup command reports a permission error. | The current account cannot create or write within /opt/lab-classroom/class48/. | Have the lab administrator provision /opt/lab-classroom/class48/ for the student account, then rerun the setup. Do not redirect the exercise to a production media root. |
| The audit reports SOURCE_MISSING. | A fixture path was renamed, the manifest was edited, or setup did not finish. | Compare manifest.json with the library inventory and rerun the fixture setup to restore the expected synthetic source paths. |
| The report contains DESTINATION_COLLISION. | Two records normalize to the same case-insensitive proposed path, or their identity fields were duplicated. | Stop the migration plan. Verify metadata identifiers, years, editions, and template fields. Do not resolve the condition by allowing one file to replace another. |
| Radarr's naming preview does not recognize a token from an external guide. | The guide targets another Radarr release, the token was entered incorrectly, or that field is unavailable in the current naming context. | Use the token selector and preview presented by the installed Radarr version. Remove unsupported fields and test the revised format before saving. |
| A movie is renamed cleanly but now represents the wrong title. | The media file was associated with an incorrect Radarr movie record before naming was applied. | Correct the movie match and metadata association first. Reinspect the path preview before organizing the file again. |
| Subtitles no longer load after a production rename. | The subtitle base name no longer matches the renamed video, or the subtitle application retained the old path. | Review sidecar handling before further renames, restore the recorded path mapping if necessary, and rename or reimport subtitles using a controlled workflow. |
| A media server shows both old and new library entries. | Its database has not reconciled the path change, or both an old root and a new root are being scanned. | Confirm that only the intended library roots are configured, initiate the media server's supported library scan, and inspect unavailable entries before removing records. |
| Names that look identical are treated as different paths. | The strings use different Unicode normalization forms or visually similar characters. | Use the audit's normalized comparison, inspect exact metadata values, and test the proposed names on the actual destination filesystem before a production migration. |

## Security

### principles
Run Radarr with a dedicated service identity rather than an interactive administrator identity.
Grant the service only the access required for configured download and media paths.
Do not expose Radarr directly to an untrusted network; place remote access behind an authenticated and maintained access layer.
Protect API keys because they permit automation clients to query or change Radarr.
Limit write access to naming reports and migration maps because they disclose library structure.
Treat imported subtitle and metadata files as untrusted content even when they are not executable media.
Keep backups of the Radarr application data and database separate from the movie library.

### change_control
Export or record the current naming settings before changing them.
Review unmapped files, duplicate movie records, editions, and metadata mismatches before bulk organization.
Use a small pilot containing a noncritical movie and its sidecars.
Pause competing import or post-processing jobs during an approved production rename window.
Preserve a source-to-destination mapping and verify downstream applications before expanding the change.

### privacy_note
Library paths can reveal viewing interests and household information. Restrict access to audit reports, screenshots, logs, and support bundles.

## Rollback

### lab
The audit itself does not rename fixture media, so no media rollback is required.
To preserve an earlier report before rerunning the audit, move it within the lab workspace using `mv /opt/lab-classroom/class48/reports/naming-audit.csv /opt/lab-classroom/class48/backups/naming-audit-before-rerun.csv`.
Rerun the fixture setup if a synthetic source file was accidentally changed; all resulting writes remain under /opt/lab-classroom/class48/.

### production_plan
Stop after the pilot if any title match, edition, subtitle, link, permission, or media-server verification fails.
Use the recorded source-to-destination mapping to reverse only the affected paths through an approved application workflow.
Restore the previous Radarr naming formats from the recorded configuration.
Verify Radarr's movie path, the physical path, sidecars, playback, and media-server indexing after reversal.
Restoring the old naming template alone does not automatically reverse names that were already applied.

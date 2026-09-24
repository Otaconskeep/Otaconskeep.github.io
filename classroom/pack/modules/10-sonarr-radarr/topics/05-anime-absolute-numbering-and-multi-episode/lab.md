# Lab — Anime, Absolute Numbering, and Multi-Episode Files

**Module:** Sonarr & Radarr
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain the difference between absolute, season-based, aired, DVD, and metadata-provider episode orderings.

## Before you start

- Completion of a basic media-library naming lesson or equivalent familiarity with series, season, and episode folders.
- Ability to run shell commands and read simple regular expressions.
- Python 3 available on the lab host.
- An existing writable /opt/lab-classroom/ directory. The lab must not create or alter files outside /opt/lab-classroom/class44/.
- General familiarity with a media manager or server such as Sonarr, Jellyfin, Plex, or an equivalent application.

## Guided lab

### scope
This lab uses zero-byte mock media files. Every created, copied, written, or deleted object is confined to /opt/lab-classroom/class44/.

### preflight
Run: test -d /opt/lab-classroom && test -w /opt/lab-classroom
Run: test ! -e /opt/lab-classroom/class44
If the second command fails, stop and use the rollback procedure or have an instructor review the existing directory.

### steps
### step
1

### title
Create the isolated workspace

### commands
mkdir /opt/lab-classroom/class44
mkdir /opt/lab-classroom/class44/incoming /opt/lab-classroom/class44/library /opt/lab-classroom/class44/manifests
mkdir -p '/opt/lab-classroom/class44/library/Star Harbor/Season 00' '/opt/lab-classroom/class44/library/Star Harbor/Season 01'
### step
2

### title
Create fictional zero-byte source files

### commands
touch '/opt/lab-classroom/class44/incoming/Star Harbor - S01E01-E02 - Twin Arrival [WEB-1080p].mkv'
touch '/opt/lab-classroom/class44/incoming/Star Harbor - 003 - Beacon [WEB-1080p].mkv'
touch '/opt/lab-classroom/class44/incoming/Star Harbor - S00E01 - Prologue [BD-1080p].mkv'
touch '/opt/lab-classroom/class44/incoming/Star Harbor - 004-005 - Cloud Gate Pair [WEB-1080p].mkv'

### note
These are empty test files and are not playable media.
### step
3

### title
Record the explicit episode mapping

### commands
printf '%s\n' 'absolute,season,episode,title' '001,01,01,Twin Arrival Part One' '002,01,02,Twin Arrival Part Two' '003,01,03,Beacon' '004,01,04,Cloud Gate Part One' '005,01,05,Cloud Gate Part Two' > /opt/lab-classroom/class44/manifests/episode-map.csv

### note
The prologue is already identified as S00E01 and is intentionally excluded from the numeric absolute map.
### step
4

### title
Create and run a dry-run normalization tool

### commands
cat > /opt/lab-classroom/class44/normalize.py <<'PY'
from pathlib import Path
import csv
import re

root = Path('/opt/lab-classroom/class44').resolve()
incoming = root / 'incoming'
map_path = root / 'manifests' / 'episode-map.csv'
report_path = root / 'manifests' / 'normalization-report.txt'

mapping = {}
with map_path.open(newline='', encoding='utf-8') as handle:
    for row in csv.DictReader(handle):
        key = int(row['absolute'])
        value = (int(row['season']), int(row['episode']), row['title'])
        if key in mapping:
            raise SystemExit(f'Duplicate absolute number in map: {key:03d}')
        mapping[key] = value

season_pattern = re.compile(r' - S(?P<season>\d{2})E(?P<first>\d{2})(?:-E(?P<last>\d{2}))? - ')
absolute_pattern = re.compile(r' - (?P<first>\d{3})(?:-(?P<last>\d{3}))? - ')
lines = []
errors = []

for path in sorted(incoming.iterdir()):
    name = path.name
    season_match = season_pattern.search(name)
    if season_match:
        first = int(season_match.group('first'))
        last = int(season_match.group('last') or first)
        if last < first:
            errors.append(f'ERROR reversed season range: {name}')
        else:
            lines.append(f'KEEP {name}')
        continue

    absolute_match = absolute_pattern.search(name)
    if not absolute_match:
        errors.append(f'ERROR unrecognized numbering: {name}')
        continue

    first_absolute = int(absolute_match.group('first'))
    last_absolute = int(absolute_match.group('last') or first_absolute)
    absolute_numbers = list(range(first_absolute, last_absolute + 1))
    missing = [number for number in absolute_numbers if number not in mapping]
    if missing:
        errors.append(f"ERROR unmapped absolute numbers {','.join(f'{number:03d}' for number in missing)}: {name}")
        continue

    mapped = [mapping[number] for number in absolute_numbers]
    seasons = {item[0] for item in mapped}
    episodes = [item[1] for item in mapped]
    if len(seasons) != 1:
        errors.append(f'ERROR range crosses provider seasons: {name}')
        continue
    if episodes != list(range(episodes[0], episodes[-1] + 1)):
        errors.append(f'ERROR range is not contiguous in provider order: {name}')
        continue

    season = mapped[0][0]
    token = f'S{season:02d}E{episodes[0]:02d}'
    if len(episodes) > 1:
        token += f'-E{episodes[-1]:02d}'
    target = name[:absolute_match.start()] + f' - {token} - ' + name[absolute_match.end():]
    lines.append(f'RENAME {name} -> {target}')

report_path.write_text('\n'.join(lines + errors) + '\n', encoding='utf-8')
if errors:
    raise SystemExit(1)
PY
python3 /opt/lab-classroom/class44/normalize.py
cat /opt/lab-classroom/class44/manifests/normalization-report.txt
### step
5

### title
Stage the reviewed canonical names

### commands
cp -- '/opt/lab-classroom/class44/incoming/Star Harbor - S00E01 - Prologue [BD-1080p].mkv' '/opt/lab-classroom/class44/library/Star Harbor/Season 00/Star Harbor - S00E01 - Prologue [BD-1080p].mkv'
cp -- '/opt/lab-classroom/class44/incoming/Star Harbor - S01E01-E02 - Twin Arrival [WEB-1080p].mkv' '/opt/lab-classroom/class44/library/Star Harbor/Season 01/Star Harbor - S01E01-E02 - Twin Arrival [WEB-1080p].mkv'
cp -- '/opt/lab-classroom/class44/incoming/Star Harbor - 003 - Beacon [WEB-1080p].mkv' '/opt/lab-classroom/class44/library/Star Harbor/Season 01/Star Harbor - S01E03 - Beacon [WEB-1080p].mkv'
cp -- '/opt/lab-classroom/class44/incoming/Star Harbor - 004-005 - Cloud Gate Pair [WEB-1080p].mkv' '/opt/lab-classroom/class44/library/Star Harbor/Season 01/Star Harbor - S01E04-E05 - Cloud Gate Pair [WEB-1080p].mkv'

### note
The source files remain unchanged. Copying models a reviewable staging workflow rather than an in-place bulk rename.
### step
6

### title
Inspect the staged result

### commands
find /opt/lab-classroom/class44 -type f -printf '%P\n' | sort
find /opt/lab-classroom/class44/library -type f -size +0c -print

### note
The final command should print nothing because all mock media files are zero bytes.

## Expected results

- The incoming directory contains four untouched mock source files.
- The normalization report marks the two already season-based names with KEEP.
- The report proposes that absolute episode 003 become S01E03.
- The report proposes that absolute range 004-005 become S01E04-E05.
- The staged Season 00 directory contains the S00E01 prologue.
- The staged Season 01 directory contains S01E01-E02, S01E03, and S01E04-E05 files.
- No object outside /opt/lab-classroom/class44/ is created, modified, renamed, or deleted by the lab commands.
- The source absolute names remain available for comparison and recovery.

## Verification

- [ ] Run `test -f '/opt/lab-classroom/class44/library/Star Harbor/Season 00/Star Harbor - S00E01 - Prologue [BD-1080p].mkv'` and confirm an exit status of zero.
- [ ] Run `test -f '/opt/lab-classroom/class44/library/Star Harbor/Season 01/Star Harbor - S01E01-E02 - Twin Arrival [WEB-1080p].mkv'` and confirm an exit status of zero.
- [ ] Run `test -f '/opt/lab-classroom/class44/library/Star Harbor/Season 01/Star Harbor - S01E03 - Beacon [WEB-1080p].mkv'` and confirm an exit status of zero.
- [ ] Run `test -f '/opt/lab-classroom/class44/library/Star Harbor/Season 01/Star Harbor - S01E04-E05 - Cloud Gate Pair [WEB-1080p].mkv'` and confirm an exit status of zero.
- [ ] Run `grep -F 'RENAME Star Harbor - 003 - Beacon [WEB-1080p].mkv -> Star Harbor - S01E03 - Beacon [WEB-1080p].mkv' /opt/lab-classroom/class44/manifests/normalization-report.txt` and confirm that the expected line is returned.
- [ ] Run `grep -F 'RENAME Star Harbor - 004-005 - Cloud Gate Pair [WEB-1080p].mkv -> Star Harbor - S01E04-E05 - Cloud Gate Pair [WEB-1080p].mkv' /opt/lab-classroom/class44/manifests/normalization-report.txt` and confirm that the expected line is returned.
- [ ] Run `find /opt/lab-classroom/class44/incoming -type f | wc -l` and confirm that the result is 4.
- [ ] Run `find /opt/lab-classroom/class44/library -type f | wc -l` and confirm that the result is 4.
- [ ] If testing with a media server, use a separate test library and verify the detected episode identities manually; do not infer success only from filenames.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The preflight check reports that /opt/lab-classroom is missing or not writable. | The classroom base directory was not provisioned, or the learner does not have the required lab permissions. | Stop the lab and ask the platform administrator to provision a writable /opt/lab-classroom directory. Do not redirect the exercise into a production media path. |
| The preflight check finds an existing class44 directory. | A previous lab run was not rolled back. | Inspect the existing directory, preserve any desired report, and then use the documented rollback procedure before starting again. |
| The normalization script reports unmapped absolute numbers. | The CSV does not contain every absolute episode represented by the filename range. | Verify the selected metadata order, add reviewed mappings for the missing numbers, and rerun the dry run. Do not invent mappings from arithmetic. |
| The normalization script reports that a range crosses provider seasons. | The source file contains episodes that map to different seasons under the chosen order. | Do not generate a single same-season range. Determine whether the file should be split, retained with a scanner-supported cross-season form, or handled manually. |
| A media server identifies S01E01-E02 as only one episode. | The server does not support that range syntax, the library type is incorrect, or the active metadata order differs from the manifest. | Check the current naming documentation for that server, confirm the show library type and episode order, and test the documented multi-episode syntax in an isolated library. |
| Both episode entries begin at the start of a multi-episode file. | Naming associates multiple episode records with one container but does not provide internal playback boundaries. | Accept the shared-file behavior, use chapters where supported, or create separate episode files through a reviewed media-processing workflow. |
| A special is matched as a regular episode. | The local S00 assignment does not agree with the selected metadata provider or its configured episode order. | Look up the special in the active provider, update the manifest to its actual provider identity, and rescan only after reviewing the proposed filename. |
| The script exits with a duplicate absolute number error. | The mapping CSV contains more than one row for the same absolute identifier. | Resolve the conflict by selecting the correct provider identity and retain only one authoritative row for that absolute number. |

## Security

### principles
Keep acquisition, staging, and production library paths separate.
Treat filenames and downloaded sidecar metadata as untrusted input.
Preview all parser and rename operations before enabling automatic organization.
Grant automation accounts write access only to directories they must manage.
Preserve an external manifest or backup before changing a production library.
Do not test numbering changes directly against the only copy of a media collection.

### path_safety
All lab paths are absolute and rooted under /opt/lab-classroom/class44/. Quoted filenames prevent spaces and bracket characters from being interpreted unexpectedly by the shell.

### privacy
Real filenames can reveal viewing habits, usernames, release sources, and storage layout. Remove such information before sharing logs or screenshots.

### integrity
A successful filename parse does not prove the file contains the claimed episode. For real media, compare duration, chapters, embedded titles, and actual content against the manifest before import.

## Rollback

### precondition
Confirm that the resolved target is exactly /opt/lab-classroom/class44 and inspect its contents before deletion.

### commands
test "$(realpath /opt/lab-classroom/class44)" = '/opt/lab-classroom/class44'
find /opt/lab-classroom/class44 -mindepth 1 -maxdepth 5 -print
find /opt/lab-classroom/class44 -depth -mindepth 1 -delete
rmdir /opt/lab-classroom/class44

### result
The class44 workspace and its mock files are removed. No production media or files outside the class workspace are affected.

### recovery_note
Deletion is not reversible from this procedure. Because the lab contains only generated mock files, recovery consists of recreating the workspace and repeating the lesson.

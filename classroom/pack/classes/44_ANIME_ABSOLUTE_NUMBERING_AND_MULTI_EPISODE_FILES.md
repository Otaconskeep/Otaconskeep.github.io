# Class 44: Anime, Absolute Numbering, and Multi-Episode Files

**Learning objective:** Explain the difference between absolute, season-based, aired, DVD, and metadata-provider episode orderings.; Translate absolute episode numbers into season-and-episode identifiers by using an explicit mapping rather than arithmetic assumptions.; Name contiguous multi-episode files with an unambiguous episode range.; Recognize why specials, split cours, remasters, and provider-order changes can invalidate automatic numbering assumptions.; Create and verify a dry-run normalization plan before copying or renaming media.; Describe the playback, progress-tracking, and metadata limitations of one file representing multiple episodes.
**Bloom level:** Understand / Apply
**Track:** Media Management and Library Automation · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach administrators how to reconcile anime absolute numbering with season-based metadata, name multi-episode files predictably, and stage changes without exposing the production media library to destructive bulk renames.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-14
**Compatibility:** ### operating_systems
Linux systems providing a POSIX-compatible shell, GNU find utilities, and Python 3

### media_software
Concepts apply to Sonarr, Jellyfin, Plex, and comparable season-oriented media systems.
Parser syntax, metadata agents, multi-episode playback behavior, and supported episode orders vary by software version and configuration.

### filesystem_notes
The sample filenames require support for spaces, square brackets, and hyphens.
Case-sensitive and case-insensitive filesystems can behave differently when names differ only by letter case.
The lab assumes /opt/lab-classroom already exists and is writable by the learner.

### version_policy
Consult the current documentation and preview parser output for the installed application version before applying these conventions to production media.

## Learning objective

- Explain the difference between absolute, season-based, aired, DVD, and metadata-provider episode orderings.
- Translate absolute episode numbers into season-and-episode identifiers by using an explicit mapping rather than arithmetic assumptions.
- Name contiguous multi-episode files with an unambiguous episode range.
- Recognize why specials, split cours, remasters, and provider-order changes can invalidate automatic numbering assumptions.
- Create and verify a dry-run normalization plan before copying or renaming media.
- Describe the playback, progress-tracking, and metadata limitations of one file representing multiple episodes.

## Why this matters

Teach administrators how to reconcile anime absolute numbering with season-based metadata, name multi-episode files predictably, and stage changes without exposing the production media library to destructive bulk renames.

## Prerequisites

- Completion of a basic media-library naming lesson or equivalent familiarity with series, season, and episode folders.
- Ability to run shell commands and read simple regular expressions.
- Python 3 available on the lab host.
- An existing writable /opt/lab-classroom/ directory. The lab must not create or alter files outside /opt/lab-classroom/class44/.
- General familiarity with a media manager or server such as Sonarr, Jellyfin, Plex, or an equivalent application.

## Required reading

- Sonarr documentation: Series Types, Anime, and Episode Naming.
- Jellyfin documentation: Shows and season-based television naming.
- Plex support documentation: Naming and organizing television show files.
- TheTVDB documentation: Episode orders and alternate ordering models.
- Documentation for the metadata provider selected in the learner's own media server.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Absolute numbering | A numbering scheme that identifies episodes with a continuous sequence across the series, such as 001, 002, and 003, instead of restarting at each season. |
| Season-based numbering | A scheme that identifies an episode with a season and episode pair, commonly written as S01E03. |
| Episode order | The authoritative arrangement used to map media to metadata. Examples include aired, DVD, production, streaming, and absolute orders. |
| Cour | A broadcast block commonly lasting roughly one television season. A split-cour production may be marketed as one work while metadata providers divide it into multiple seasons or parts. |
| Special | Content such as an OVA, recap, prologue, short, or bonus episode that may not belong in the regular episode sequence. Season-based libraries commonly place specials in season 00. |
| Multi-episode file | One media container that contains the complete playable content for two or more episodes, usually represented by a contiguous range such as S01E01-E02. |
| Scene numbering | Numbering chosen by a release group or distribution community. It may differ from the numbering used by a metadata provider. |
| Canonical name | The selected stable filename format used by the local library after source names have been mapped to the chosen metadata order. |
| Dry run | A preview that reports proposed actions without modifying source media. |
| Sidecar metadata | A file stored beside media, such as an NFO or image, that supplies or overrides metadata and must remain aligned with the media filename. |

## Instruction

Anime libraries are difficult when three identities are treated as if they were interchangeable: the title printed by a release group, the episode number embedded in a source filename, and the episode identity exposed by a metadata provider. Absolute episode 027 does not inherently mean S02E03. That conversion is only valid if an authoritative episode-order table says so. Specials, recaps, unaired episodes, split cours, licensing seasons, and provider revisions can all shift the relationship. Select a metadata provider and episode order first, record that decision, and then build an explicit mapping from each source identifier to the provider's season and episode pair. Leading zeroes improve sorting but do not establish identity.

For a season-oriented library, a single episode is commonly named with a token such as S01E03. A file containing two complete, adjacent episodes can be represented as S01E01-E02. The exact syntax supported by a scanner must be checked in that scanner's current documentation; superficially similar forms are not guaranteed to parse identically. Do not label an ordinary long episode as two episodes merely because its runtime is unusual. Conversely, do not assign two independent media files to the same multi-episode identity. A range should normally be contiguous, belong to one provider season, and reflect content actually present in the container.

Multi-episode files have operational limitations. A media server may create two episode records that both point to the same file. Depending on the server and client, both records can show the full file duration, share a resume position, or begin playback at the start rather than at an internal episode boundary. Naming communicates identity; it does not create chapter boundaries or split the container. If independent progress and episode-level playback are required, retain separate source files or split the container only with a deliberate media-processing workflow that preserves streams and timestamps.

Specials require explicit decisions. A prologue may be absolute episode 000, a provider special, or regular episode 1 under different orders. Many season-based layouts use S00E01, but that convention must match the selected provider. Avoid forcing a special into the regular absolute sequence merely to make arithmetic convenient. Likewise, do not merge two ranges across a season boundary. A source labeled 012-013 could map to S01E12 and S02E01; that should be represented by separate files or handled according to documented scanner behavior, not guessed as S01E12-E13.

A safe workflow is identify, map, preview, stage, verify, and only then import. Preserve original source names until the proposed mapping has been reviewed. Use a manifest that records the source name, absolute identity, target season identity, selected order, and reason for any exception. Preview the media manager's parser before enabling automatic rename. Test a small sample in an isolated library, inspect episode matches and specials, and keep the manifest with operational records. Never use filename arithmetic as a substitute for metadata verification.

## Architecture

### workflow
Release or acquisition names enter an isolated incoming directory.
A pinned metadata provider and episode order act as the identity authority.
An episode map translates source or absolute identifiers into season-based identifiers.
A dry-run normalizer produces proposed canonical names without altering source files.
Reviewed files are copied into a staging library using canonical names.
A media manager or server scans the staging library and resolves episode metadata.
The administrator verifies titles, specials, ranges, playback behavior, and progress handling before production import.

### example_layout
/opt/lab-classroom/class44/incoming/ contains untouched mock source names.
/opt/lab-classroom/class44/manifests/episode-map.csv records explicit identity mappings.
/opt/lab-classroom/class44/manifests/normalization-report.txt records proposed actions.
/opt/lab-classroom/class44/library/Star Harbor/Season 00/ contains the staged special.
/opt/lab-classroom/class44/library/Star Harbor/Season 01/ contains staged regular episodes.

### identity_rule
The selected metadata order and reviewed mapping are authoritative. Neither source filename numbering nor arithmetic conversion is authoritative by itself.

### multi_episode_rule
Use a range only when one file contains all identified episodes, the episodes are contiguous in the selected order, and the scanner documents support for the chosen range syntax.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Choose one legally owned series in a non-production worksheet and document the metadata provider and episode order used by your media server.
Create a mapping for ten consecutive source identifiers, including at least one special or other exception if the selected series has one.
Draft canonical names for one single episode and one hypothetical contiguous multi-episode file.
Document how your chosen media server represents multi-episode runtime, watched state, and resume position according to current documentation or an isolated test.
Write a rollback plan that preserves original names and sidecar metadata before any production rename.

## Feynman teach-back

### prompt
Explain the workflow to a friend who thinks absolute episode 027 can always be converted by dividing by a season length.

### model_explanation
Absolute 027 is only a label in one ordering system. Seasons may have different lengths, and specials or provider decisions can shift later numbers. I first choose the metadata provider and its order, then look up absolute 027 in a mapping table. If that table says it is season 2 episode 3, I can name it S02E03. If one file contains two adjacent mapped episodes, I can use a supported range such as S02E03-E04. The name helps the server associate records with the file, but it does not split the video or guarantee separate resume positions.

### self_check
Can the learner explain why arithmetic conversion is unsafe?
Can the learner distinguish an episode identity from a filename format?
Can the learner explain why one file may create multiple metadata records but still have one playback timeline?
Can the learner state why specials require explicit mapping?

## Retrieval check

1. Why is absolute episode 027 not sufficient by itself to determine a season-based identifier?
2. What does the filename token S01E04-E05 claim about the media file?
3. Should a long runtime alone cause a file to be named as a multi-episode range?
4. Why should a multi-episode range normally remain within one provider season?
5. What is the purpose of a dry-run normalization report?
6. How are specials commonly represented in a season-based library, and why is that convention not universal?
7. Does a multi-episode filename create separate playback timelines inside the media container?
8. What should be treated as authoritative when a release group's numbering conflicts with the selected metadata provider?
9. Why were the lab files copied into a staging library instead of renaming the incoming files in place?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

Begin by showing three labels for the same fictional episode: a release name using 003, a metadata record using season 1 episode 3, and a canonical filename using S01E03. Emphasize that the conversion comes from a mapping table, not from arithmetic. Next, compare a single episode with the S01E01-E02 multi-episode file. Explain that the range says what content is in the container but does not split playback. Walk through the isolated directory tree and point out that incoming names remain untouched. Create the mapping CSV, then run the normalization script and read each KEEP and RENAME line aloud. Highlight the validation checks for missing mappings, season boundaries, and noncontiguous provider episodes. Copy the mock files into Season 00 and Season 01 staging directories, then verify the exact resulting names. Close by explaining that a real deployment adds a media-manager preview, a separate test library, content inspection, and a preserved rollback manifest before any production import.

## References

- Sonarr Wiki, Series Types and Anime: https://wiki.servarr.com/sonarr/faq
- Sonarr Wiki, Settings and Media Management: https://wiki.servarr.com/sonarr/settings
- Jellyfin Documentation, Shows naming guidance: https://jellyfin.org/docs/general/server/media/shows/
- Plex Support, Naming and Organizing Your TV Show Files: https://support.plex.tv/articles/naming-and-organizing-your-tv-show-files/
- TheTVDB API Documentation: https://thetvdb.github.io/v4-api/
- Python Standard Library, csv module: https://docs.python.org/3/library/csv.html
- Python Standard Library, re module: https://docs.python.org/3/library/re.html

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

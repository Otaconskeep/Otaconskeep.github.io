# Class 48: Radarr Naming and Movie Library Hygiene

**Learning objective:** Explain the difference between a movie folder format and a movie file format in Radarr.; Design a naming policy that preserves title, year, edition, quality, and stable metadata identity where appropriate.; Explain why stable identifiers reduce ambiguity when titles are duplicated, translated, or remade.; Audit a movie library for missing years, duplicate proposed paths, unexpected extensions, Unicode normalization issues, and unmanaged sidecar files.; Use Radarr previews and dry-run reports before enabling automatic renaming.; Plan a staged library cleanup that avoids destructive bulk changes and preserves rollback information.; Distinguish cosmetic naming inconsistencies from conditions that can break imports, upgrades, subtitles, or external integrations.
**Bloom level:** Understand / Apply
**Track:** Media Automation · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach administrators how to design predictable Radarr movie folder and file naming, audit an existing library safely, preserve stable movie identity, detect naming collisions, and plan cleanup without disrupting playback or deleting media.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### radarr
Applicable to current Radarr releases that provide Media Management naming formats and naming previews. Exact token names and available fields must be verified in the installed version.

### operating_system
The hands-on commands target Linux with Python 3, GNU find, and write access to /opt/lab-classroom/class48/.

### filesystems
The policy concepts apply broadly, but case sensitivity, Unicode behavior, reserved characters, maximum path length, hard-link behavior, and cross-filesystem moves vary by platform and storage backend.

### containers
For containerized Radarr, host and container paths must map consistently. The lab does not require a Radarr container or alter container mounts.

### media_servers
Applicable to common media servers, but library refresh and unavailable-item behavior must be validated using the documentation for the deployed server.

## Learning objective

- Explain the difference between a movie folder format and a movie file format in Radarr.
- Design a naming policy that preserves title, year, edition, quality, and stable metadata identity where appropriate.
- Explain why stable identifiers reduce ambiguity when titles are duplicated, translated, or remade.
- Audit a movie library for missing years, duplicate proposed paths, unexpected extensions, Unicode normalization issues, and unmanaged sidecar files.
- Use Radarr previews and dry-run reports before enabling automatic renaming.
- Plan a staged library cleanup that avoids destructive bulk changes and preserves rollback information.
- Distinguish cosmetic naming inconsistencies from conditions that can break imports, upgrades, subtitles, or external integrations.

## Why this matters

Teach administrators how to design predictable Radarr movie folder and file naming, audit an existing library safely, preserve stable movie identity, detect naming collisions, and plan cleanup without disrupting playback or deleting media.

## Prerequisites

- Basic familiarity with Radarr movies, root folders, and the Media Management settings page
- Ability to run shell and Python 3 commands on a Linux host
- Understanding of files, directories, extensions, hard links, and symbolic links
- Completion of introductory storage and media-library organization lessons
- Write access to /opt/lab-classroom/class48/

## Required reading

- Radarr documentation: Settings, especially the Media Management and movie naming sections.
- Radarr documentation: Library organization, importing, and root folder behavior.
- TRaSH Guides: Radarr recommended naming scheme.
- Python documentation: pathlib for safe path inspection and construction.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Movie folder format | The Radarr template used to construct the directory assigned to one movie, such as a title, release year, and metadata identifier. |
| Standard movie format | The Radarr template used to construct the primary movie file name inside its movie folder. |
| Naming token | A field in braces that Radarr replaces with metadata, such as movie title, release year, quality, edition, or an external database identifier. |
| Stable identifier | An external catalog identifier, such as a TMDB or IMDb identifier, that remains more reliable than title text for distinguishing movies. |
| Edition | A specific cut or presentation of a movie, such as a director's cut, final cut, theatrical cut, or extended edition. |
| Quality | Radarr's classification of the source and resolution associated with a release, which can be represented in a file name using an appropriate token. |
| Root folder | A top-level path registered with Radarr under which individual movie folders are stored. |
| Sidecar file | A related non-video file stored beside a movie, such as subtitles, artwork, metadata, chapters, or checksums. |
| Collision | A condition in which two source records would produce the same destination path under the proposed naming policy. |
| Dry run | An inspection that calculates and reports proposed changes without applying them to the media library. |
| Unicode normalization | The standardized representation of Unicode characters so that visually identical names do not have different underlying byte sequences. |
| Library hygiene | The ongoing practice of maintaining consistent paths, valid metadata associations, predictable permissions, unique identities, and controlled handling of sidecars. |

## Instruction

Radarr naming has two related but separate layers: the movie folder and the movie file. A folder identifies the logical movie managed by Radarr, while a file identifies a particular media asset currently satisfying that movie. A durable policy usually gives the folder a human-readable title, the release year, and, where supported by the surrounding tools, a stable external identifier. A conceptual folder could therefore resemble `Arrival (2016) [tmdb-329865]`. The year distinguishes many remakes, while the identifier resolves cases involving alternate titles, localization, punctuation, or two movies released in the same year. The media file may additionally carry quality and edition information because those properties describe the asset rather than merely the movie record.

Consistency matters more than decorative complexity. Every added token creates another dependency on metadata quality and tool compatibility. Before adopting a template, confirm that the installed Radarr version recognizes every token, inspect the example shown in the naming settings, and verify that media players, backup tools, subtitle applications, and indexers tolerate the resulting characters. Avoid manually typing identifier text into templates as if it were ordinary metadata; use supported Radarr tokens so each movie receives its own value. Token names and formatting capabilities can change across releases, so the live naming preview is authoritative for the installed instance.

Renaming is not the same as rediscovering metadata. Radarr renames files according to the movie records and media files it already knows. If a file is matched to the wrong movie, a perfectly formatted name can make that incorrect match look legitimate. Resolve unmatched files, duplicate records, incorrect editions, and bad metadata before bulk organization. The safest workflow is inventory, preview, small pilot, verification, and then staged expansion. Record current and proposed paths before making changes. A path mapping is useful for rollback, audit review, and diagnosing applications that retained an old path.

Folder and file changes can affect more than Radarr. A media server may need to rescan paths. Subtitle files can become detached when their base name no longer follows the movie file. Automation scripts may depend on old directories. Hard links remain links to the same inode when renamed on one filesystem, but a workflow that copies across filesystems behaves differently. Symbolic links can become stale when their stored target path changes. Backups may treat a mass rename as a large deletion and addition even when content bytes did not change. These consequences are why this class uses a synthetic library and generates proposals rather than changing a production collection.

A hygiene audit should separate warnings from confirmed faults. A missing year is an ambiguity warning, not proof that a movie is wrong. An unexpected extension may be a legitimate sidecar. A duplicate proposed target is a blocking fault because applying both mappings would overwrite or merge identities. Control characters, trailing spaces, platform-reserved characters, and inconsistent Unicode forms may cause portability problems. Edition labels should be explicit and consistently sourced instead of inferred from arbitrary release text. Quality labels are useful for humans and recovery, but Radarr's database remains the primary authority for upgrade decisions.

A practical naming policy should be deterministic: the same metadata should always produce the same path. It should also be reversible enough that an administrator can identify the movie from the path if the application database is unavailable. Keep folders stable when possible and allow asset-specific information to live in file names. Do not use a naming cleanup as a substitute for backups, metadata correction, permission design, or storage monitoring. Naming is one layer of library integrity, not the entire integrity model.

## Architecture

### components
### name
Radarr database

### role
Stores movie identity, metadata associations, monitored state, media-file records, quality information, and configured paths.
### name
Radarr naming engine

### role
Expands supported naming tokens into proposed folder and file names.
### name
Movie root folder

### role
Contains one managed directory per movie and must be accessible to Radarr and downstream media services.
### name
Download or import workflow

### role
Supplies releases that Radarr matches, imports, and optionally renames.
### name
Media server

### role
Indexes the organized library and may need a scan after controlled path changes.
### name
Lab audit workspace

### role
Provides a synthetic library, authoritative fixture manifest, and dry-run reports under /opt/lab-classroom/class48/.

### data_flow
Radarr associates a release with a movie record.
Import processing evaluates the source file, quality, edition, and destination root.
The naming engine expands the configured format using known metadata.
The file is linked, moved, or copied according to the configured import environment.
Radarr records the resulting managed path.
The media server discovers the organized path during its library scan.

### policy_example
### folder_intent
Title, release year, and stable movie identifier

### file_intent
Title, release year, optional edition, quality, and original media extension

### important_note
Use only tokens confirmed by the naming preview in the installed Radarr version; the example expresses policy intent rather than guaranteeing identical token syntax in every release.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Draft a folder and file naming policy for your homelab. State which fields identify the movie and which fields describe the media asset.
Inventory one read-only sample of your own library and classify issues as cosmetic, warning, or blocking. Do not rename files for this assignment.
Document how your media server, subtitle tools, backup system, and download workflow would react to a path change.
Create a pilot checklist that includes metadata match, proposed destination, collision check, sidecars, playback, media-server scan, backup impact, and rollback evidence.
Review the naming token selector in your installed Radarr version and note any differences from external examples.

## Feynman teach-back

### prompt
Explain Radarr naming to a household member who knows folders but has never used media automation.

### model_explanation
Radarr keeps a catalog entry for each movie and connects that entry to a file. The naming template is a recipe that turns trusted catalog facts into a predictable folder and file name. The title makes the path readable, the year separates many remakes, and an external identifier settles cases where text is ambiguous. Quality and edition describe the particular file. Before changing names, we calculate every destination and make sure two movies will not land in the same place. We then test one movie and confirm that subtitles and the media server still follow it.

### self_check
Can you explain why the year is helpful but not always sufficient?
Can you explain why a clean name does not prove that the movie was matched correctly?
Can you explain why a path report is required before a bulk rename?
Can you explain the difference between movie identity and media-file properties without using Radarr jargon?

## Retrieval check

1. 1. What is the main difference between a movie folder format and a standard movie file format?
2. 2. Why should a stable external identifier be considered in a movie folder naming policy?
3. 3. Does a correctly formatted file name prove that Radarr matched the file to the correct movie?
4. 4. What should happen when two records produce the same normalized destination path?
5. 5. Why should sidecar files be inventoried before a bulk rename?
6. 6. Which information usually belongs more naturally in a file name than in the stable movie folder: release year or media quality?
7. 7. Why is Radarr's live naming preview more authoritative than a copied template from a guide?
8. 8. What is the purpose of recording source-to-destination mappings?
9. 9. Why can a mass rename create significant backup activity even when movie content has not changed?
10. 10. What is the safest sequence for introducing a new naming policy?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

Welcome to Class 48, Radarr Naming and Movie Library Hygiene. In this lesson, we are treating file naming as an integrity process rather than a cosmetic exercise. Radarr has a movie record, a movie folder, and a managed media file. Those objects are related, but they do not carry exactly the same information. A folder should provide a stable, recognizable identity for the movie. A file can additionally describe the quality and edition of the particular asset.

A title by itself is weak identity. Movies can be remade, translated, or released with alternate punctuation. Adding the release year resolves many cases, but not every possible ambiguity. A supported metadata identifier provides a stronger link to the catalog record. Always confirm token syntax using the naming controls and preview in your installed Radarr version.

The greatest operational mistake is enabling a complex format and immediately organizing an entire library. Naming does not validate the underlying movie match. If the file is attached to the wrong record, Radarr can produce a polished name for the wrong movie. Start by checking unmatched files, duplicates, editions, and metadata.

Our lab creates only synthetic text fixtures under the class workspace. We inventory those files and use a manifest as the authoritative metadata source. The audit calculates destination paths but does not apply them. It normalizes names, checks extensions and source existence, and detects collisions using a case-insensitive comparison. Notice that the two Crash movies remain distinct because they have different years and identifiers. Also notice that Blade Runner carries an edition label in the file name.

Next, we inventory sidecars. A subtitle or poster may need separate handling during a real cleanup. A primary movie file can be renamed successfully while a subtitle is left behind with an obsolete base name. Similar concerns apply to symbolic links, media-server databases, scripts, and backup tools.

For production work, record the current settings and every proposed path. Test one low-impact movie. Verify the Radarr record, physical file, subtitles, playback, media-server scan, and backup behavior. If anything is unexpected, stop and use the mapping to reverse the pilot. A good naming policy is deterministic, readable, compatible with your tools, and based on verified metadata. A good migration is staged, observable, and reversible.

## References

- Radarr Wiki — Settings: https://wiki.servarr.com/radarr/settings
- Radarr Wiki — Radarr documentation index: https://wiki.servarr.com/radarr
- TRaSH Guides — Radarr recommended naming scheme: https://trash-guides.info/Radarr/Radarr-recommended-naming-scheme/
- Python documentation — pathlib: https://docs.python.org/3/library/pathlib.html
- Unicode Standard Annex #15 — Unicode Normalization Forms: https://unicode.org/reports/tr15/

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

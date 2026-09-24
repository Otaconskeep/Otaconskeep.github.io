# Class 43 — Sonarr Naming and Library Hygiene

**Learning objective:** Explain how Sonarr turns parsed release information into season folders and episode filenames.; Select naming tokens that preserve series title, season and episode identity, episode title, quality, release group, and edition information.; Distinguish download-client staging paths from Sonarr-managed library paths.; Explain how copy, hardlink, and move import behavior affects seeding, storage use, and cleanup.; Identify ambiguous, duplicate, unparseable, and misplaced episode files.; Build a safe audit workflow that does not rename production media blindly.; Describe why manual changes inside a managed library should be coordinated with Sonarr.; Verify that naming and path changes produce the expected result before applying them to a real library.
**Bloom level:** Understand / Apply
**Track:** Media Automation · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach operators how to design predictable Sonarr naming rules, preserve useful release metadata, separate download staging from the managed library, and detect library hygiene problems before they cause failed upgrades, duplicate episodes, or difficult recovery.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### sonarr
Concepts apply to current Sonarr releases that provide Media Management naming templates, root folders, import handling, and rename previews. Confirm available tokens in the interface for the installed version.

### operating_system
Lab commands target a Linux environment with a POSIX-compatible shell, GNU find, core utilities, and Python 3.9 or newer.

### containers
Applicable to native and containerized deployments. Container users must translate application paths to the underlying host filesystem when evaluating hardlink eligibility.

### filesystem
The lab itself does not require hardlink support. Production hardlinks require source and destination to reside on the same filesystem with compatible access.

### media
Lab fixtures are plain text files with media-like names and are not playable media.

## Learning objective

- Explain how Sonarr turns parsed release information into season folders and episode filenames.
- Select naming tokens that preserve series title, season and episode identity, episode title, quality, release group, and edition information.
- Distinguish download-client staging paths from Sonarr-managed library paths.
- Explain how copy, hardlink, and move import behavior affects seeding, storage use, and cleanup.
- Identify ambiguous, duplicate, unparseable, and misplaced episode files.
- Build a safe audit workflow that does not rename production media blindly.
- Describe why manual changes inside a managed library should be coordinated with Sonarr.
- Verify that naming and path changes produce the expected result before applying them to a real library.

## Why this matters

Teach operators how to design predictable Sonarr naming rules, preserve useful release metadata, separate download staging from the managed library, and detect library hygiene problems before they cause failed upgrades, duplicate episodes, or difficult recovery.

## Prerequisites

- Basic familiarity with Sonarr series, episodes, root folders, and download clients.
- Ability to run shell commands and read file paths.
- Understanding that the download directory and the final media library serve different purposes.
- Permission to create and modify files only under /opt/lab-classroom/class43/ for this lab.
- Recommended completion of earlier lessons covering filesystem permissions, containers, and media automation.

## Required reading

- Sonarr Media Management settings: https://wiki.servarr.com/sonarr/settings#media-management
- Sonarr FAQ: https://wiki.servarr.com/sonarr/faq
- TRaSH Guides recommended Sonarr naming scheme: https://trash-guides.info/Sonarr/Sonarr-recommended-naming-scheme/
- TRaSH Guides hardlinks and instant moves: https://trash-guides.info/Hardlinks/Hardlinks-and-Instant-Moves/

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Root folder | A top-level directory registered with Sonarr as a destination for managed series folders. A root folder should represent the library, not the download client's incomplete or completed staging directory. |
| Series folder format | The template Sonarr uses to create the directory belonging to a series, commonly including the series title and year to distinguish similarly named shows. |
| Standard episode format | The template used to name ordinary episode files after import. |
| Multi-episode file | One media file that contains more than one episode and therefore needs a filename that identifies every represented episode. |
| Release group | The group identifier parsed from a release name. Preserving it can help troubleshooting, matching, and later quality decisions. |
| Quality token | A naming token that records the quality Sonarr associated with a file, such as a source and resolution classification. |
| Hardlink | A second directory entry pointing to the same filesystem data. A hardlinked download and library file appear as separate paths but do not consume a second full copy of the content. |
| Atomic move | A rename operation completed within one filesystem without copying file contents. Crossing filesystems generally prevents an atomic move. |
| Import | The operation in which Sonarr recognizes a downloaded release and places or links its episode files into the managed library. |
| Library hygiene | The practice of keeping media paths predictable, uniquely identifiable, free from unexplained duplicates, and aligned with Sonarr's database. |
| Rescan | A Sonarr operation that compares the filesystem with the files recorded for a series. |
| Refresh and Scan | A Sonarr action that refreshes series metadata and scans the associated series folder for media files. |

## Instruction

Sonarr is not merely a downloader; it maintains a database that maps a series, season, episode, quality, and release history to files in a managed library. Good naming makes that relationship visible even when the database, application, or backup catalog is unavailable. A durable episode name normally includes a recognizable series title, season and episode numbering, an episode title when available, quality information, and release-group information when Sonarr can parse it. Including the series year in the series folder is especially useful when two productions share a title. The exact template is a policy choice, but consistency is more important than cosmetic preferences.

The download directory and library root must be treated as separate logical roles. A download client owns its active and completed job paths. Sonarr imports from those paths into a root folder that it manages. Pointing both applications at the same undifferentiated directory can leave release folders in the library, expose partial downloads to media servers, and make cleanup unsafe. In a container deployment, the paths visible inside each container may differ from host paths; Sonarr must still be able to resolve the path reported by the download client. Remote path mappings are translation rules for genuinely different path views, not a general repair for poor volume layout.

Import behavior depends on filesystem topology and download state. A completed torrent that must continue seeding is commonly hardlinked into the library when the source and destination are on the same filesystem and hardlinks are enabled. If hardlinking is impossible, import may copy the file, consuming additional storage. A completed non-seeding download can often be moved. Moving within one filesystem can be effectively instantaneous because only directory metadata changes, while moving across filesystems normally becomes a copy followed by source removal. Operators should validate mount points and link counts instead of assuming an import method from how quickly it appeared.

Renaming should be performed through Sonarr when the files belong to a managed series. An external bulk rename can leave Sonarr's stored path stale until a scan, can erase release metadata, and can create collisions. Before any production rename, preview the proposed names, confirm that multi-episode files remain identifiable, check free space and backups, and test one series. Naming tokens cannot recover information that was never parsed, so preserving the original release title in history and retaining release-group and quality tokens are useful safeguards.

Library hygiene also means detecting orphaned season folders, duplicate episode identities, unexpected extensions, samples, files stored directly under a root, and paths that differ only by case. No single filename audit proves that media content is correct; filenames provide evidence, while Sonarr's episode mapping, media analysis, and operator review establish confidence. The lab therefore uses harmless text fixtures to practice classification and previewing without touching a real Sonarr instance or media library.

## Architecture

### components
Download client staging area
Sonarr parser and episode mapper
Sonarr import process
Managed series root folder
Media server scanner
Backup and audit process

### data_flow
The download client writes a release into its staging or completed-download path.
The download client reports completion and a source path to Sonarr.
Sonarr parses the release, matches files to episodes, and chooses an import operation.
Sonarr creates the series and season path according to configured templates.
Sonarr moves, copies, or hardlinks the media file into the managed library.
The media server scans the stable library path rather than the staging path.
Audit and backup processes inspect the managed library and Sonarr configuration.

### recommended_boundaries
Keep incomplete downloads outside the media server's library scan scope.
Give Sonarr and the download client compatible access to the completed-download path.
Use one consistent shared filesystem layout when hardlinks are required.
Keep each series under exactly one intended Sonarr root folder.
Coordinate file renames and moves through Sonarr after reviewing its preview.

### sample_naming_policy
### series_folder
Series Title (Year)

### season_folder
Season 01

### episode_file
Series Title (Year) - S01E01 - Episode Title [Quality] - ReleaseGroup.ext

### policy_note
The displayed names are conceptual examples. In Sonarr, select supported naming tokens from the Media Management interface and use Sonarr's preview because token spelling and rendered values depend on the installed version.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Write a proposed Sonarr naming policy for your environment, including series folder, season folder, standard episode, daily episode, anime episode, and multi-episode formats.
Explain which metadata your policy preserves and why each element is useful during recovery.
Draw the host and container paths used by your download client, Sonarr, and media server. Mark the download staging area and final library.
Determine whether your intended source and destination are on the same filesystem using read-only inspection appropriate to your platform.
Select one noncritical series and document Sonarr's proposed rename output without applying it.
Create a checklist for identifying duplicate episode identities, unexpected samples, orphaned files, and series stored under the wrong root.
Document how you would restore Sonarr's database and naming configuration if a bulk rename produced incorrect mappings.

## Feynman teach-back

### prompt
Explain Sonarr library hygiene to someone who thinks filenames do not matter because the media server already has a database.

### model_explanation
The database is like a catalog, while the files are the items on the shelves. If every item has a clear label, you can rebuild the catalog, identify duplicates, and recover after moving to a new system. Sonarr receives a downloaded file, decides which episode it represents, and places it on the correct shelf using a naming rule. The download shelf and permanent library shelf should remain separate. A hardlink can put the same data on both shelves without storing two full copies, but only when both paths use the same filesystem. Renaming through Sonarr keeps the catalog and shelf labels synchronized. Clear names do not replace backups or episode matching, but they make mistakes visible and recovery much safer.

## Retrieval check

1. 1. Why should a Sonarr root folder normally be separate from the download client's staging directory?
2. 2. What filesystem condition is required for a hardlink between a completed download and a library file?
3. 3. Why is the series year useful in a series folder name?
4. 4. What is the main risk of bulk-renaming managed episode files outside Sonarr?
5. 5. Why should quality and release-group information be preserved when available?
6. 6. What does a duplicate S01E01 filename finding prove, and what does it not prove?
7. 7. When is a remote path mapping appropriate in Sonarr?
8. 8. What should an operator do before applying a new naming scheme to an entire production library?

## Guided lab

### scope
Create a simulated download area and managed library entirely under /opt/lab-classroom/class43/, audit intentionally inconsistent filenames, and generate a proposed rename report without changing any production media.

### safety_constraints
Do not substitute a production library path for the classroom path.
Do not point Sonarr or a media server at the fixtures.
All created and modified files remain under /opt/lab-classroom/class43/.
The exercise previews normalized names but does not overwrite source fixtures.

### steps
### step
1

### instruction
Create isolated download and library directories.

### command
mkdir -p /opt/lab-classroom/class43/downloads/Example.Show.2024.S01 /opt/lab-classroom/class43/library/'Example Show (2024)'/'Season 01' /opt/lab-classroom/class43/reports
### step
2

### instruction
Create harmless fixture files representing a release, one well-named library episode, and several hygiene problems.

### command
printf 'fixture: source episode 1\n' > /opt/lab-classroom/class43/downloads/Example.Show.2024.S01/Example.Show.2024.S01E01.1080p.WEB-DL-GROUP.mkv
printf 'fixture: clean episode 1\n' > "/opt/lab-classroom/class43/library/Example Show (2024)/Season 01/Example Show (2024) - S01E01 - Arrival [1080p WEB-DL] - GROUP.mkv"
printf 'fixture: ambiguous episode 2\n' > "/opt/lab-classroom/class43/library/Example Show (2024)/Season 01/episode2.mkv"
printf 'fixture: duplicate identity\n' > "/opt/lab-classroom/class43/library/Example Show (2024)/Season 01/Example.Show.S01E01-copy.mkv"
printf 'fixture: sample\n' > "/opt/lab-classroom/class43/library/Example Show (2024)/Season 01/sample.mkv"
printf 'fixture: subtitle\n' > "/opt/lab-classroom/class43/library/Example Show (2024)/Season 01/Example Show (2024) - S01E01 - Arrival.en.srt"
### step
3

### instruction
Capture a sorted inventory of the isolated fixture tree.

### command
find /opt/lab-classroom/class43 -type f -printf '%P\n' | sort > /opt/lab-classroom/class43/reports/inventory.txt
### step
4

### instruction
Create an audit script that classifies video filenames by episode-token visibility, sample naming, and duplicate season/episode identity.

### command
cat > /opt/lab-classroom/class43/audit.py <<'PY'
from pathlib import Path
import re
from collections import defaultdict
root = Path('/opt/lab-classroom/class43/library')
report = Path('/opt/lab-classroom/class43/reports/audit.txt')
video_exts = {'.mkv', '.mp4', '.avi', '.m4v'}
episode_pattern = re.compile(r'(?i)S(\d{2})E(\d{2})')
identities = defaultdict(list)
lines = []
for path in sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in video_exts):
    rel = path.relative_to(root)
    match = episode_pattern.search(path.name)
    flags = []
    if 'sample' in path.stem.lower():
        flags.append('SAMPLE_NAME')
    if not match:
        flags.append('NO_STANDARD_EPISODE_TOKEN')
    else:
        identity = f'S{match.group(1)}E{match.group(2)}'
        identities[identity].append(str(rel))
    if not flags:
        flags.append('TOKEN_VISIBLE')
    lines.append(f'{rel} | {",".join(flags)}')
for identity, paths in sorted(identities.items()):
    if len(paths) > 1:
        lines.append(f'DUPLICATE_IDENTITY {identity} | ' + ' ; '.join(paths))
report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
PY
python3 /opt/lab-classroom/class43/audit.py
### step
5

### instruction
Create a proposed rename plan for the ambiguous episode without changing it.

### command
printf '%s\n' 'CURRENT: Example Show (2024)/Season 01/episode2.mkv' 'PROPOSED: Example Show (2024)/Season 01/Example Show (2024) - S01E02 - Second Signal [Unknown Quality] - Unknown Group.mkv' 'REVIEW: Confirm episode mapping, quality, and release group in Sonarr before renaming.' > /opt/lab-classroom/class43/reports/rename-preview.txt
### step
6

### instruction
Review the inventory, audit findings, and proposed rename plan.

### command
cat /opt/lab-classroom/class43/reports/inventory.txt /opt/lab-classroom/class43/reports/audit.txt /opt/lab-classroom/class43/reports/rename-preview.txt
### step
7

### instruction
Relate the simulation to Sonarr without changing Sonarr: inspect Media Management naming settings, note the active series, season, and episode templates, and compare Sonarr's example output with the policy used in this lesson.

### command
printf '%s\n' 'Manual review completed only after inspecting Sonarr naming previews; no production setting was changed by this lab.' > /opt/lab-classroom/class43/reports/operator-note.txt

## Expected results

- The inventory lists one source fixture under downloads, four video fixtures under the simulated library, one subtitle fixture, and generated report files as the exercise progresses.
- The audit marks the conventionally named S01E01 file as TOKEN_VISIBLE.
- The audit marks episode2.mkv and sample.mkv as NO_STANDARD_EPISODE_TOKEN.
- The audit additionally marks sample.mkv as SAMPLE_NAME.
- The audit reports a DUPLICATE_IDENTITY finding for S01E01 because two library filenames expose that identity.
- The rename preview proposes an explicit S01E02 destination but labels quality and release group as unknown rather than inventing metadata.
- No production Sonarr configuration, download directory, or media library is modified.

## Verification checkpoints

- [ ] Run: test -f /opt/lab-classroom/class43/reports/audit.txt && echo PASS
- [ ] Run: grep -F 'DUPLICATE_IDENTITY S01E01' /opt/lab-classroom/class43/reports/audit.txt
- [ ] Run: grep -F 'episode2.mkv | NO_STANDARD_EPISODE_TOKEN' /opt/lab-classroom/class43/reports/audit.txt
- [ ] Run: grep -F 'sample.mkv | SAMPLE_NAME,NO_STANDARD_EPISODE_TOKEN' /opt/lab-classroom/class43/reports/audit.txt
- [ ] Run: grep -F 'PROPOSED: Example Show (2024)/Season 01/Example Show (2024) - S01E02' /opt/lab-classroom/class43/reports/rename-preview.txt
- [ ] Run: find /opt/lab-classroom/class43 -type f -printf '%P\n' | sort and confirm every displayed path remains inside the classroom directory.
- [ ] In Sonarr, inspect Settings, Media Management, Episode Naming and confirm that the filename preview visibly identifies the series and episode before considering any production change.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The audit script reports that python3 is unavailable. | The classroom host does not have a Python 3 interpreter installed or it is not available in the current command path. | Run the lab on a compatible host with Python 3.9 or newer. Do not install packages as part of this exercise unless your separate change-control process authorizes it. |
| Creating the classroom directories returns a permission-denied error. | The current account cannot write beneath /opt/lab-classroom/. | Have the lab administrator pre-create /opt/lab-classroom/class43/ with suitable ownership. Do not broaden permissions on unrelated directories. |
| The duplicate finding does not appear. | One fixture was not created, its filename changed, or the audit script was copied incorrectly. | Inspect the sorted inventory, confirm that both S01E01 video filenames exist, then compare audit.py with the lesson and rerun it. |
| Sonarr imports by copying even though hardlinks are enabled. | The source and destination are on different filesystems, the container paths resolve to separate mounts, permissions prevent link creation, or the download is not eligible for hardlink handling. | Compare filesystem and mount identity for the source and destination, inspect Sonarr's import log, and verify compatible ownership and access. Do not infer hardlink behavior only from path names. |
| Sonarr reports that a download path does not exist. | The path reported by the download client is not visible at the same path inside Sonarr, or an appropriate remote path mapping is absent. | Document the host and container path mappings for both applications. Correct the shared volume layout or add a narrowly scoped remote path mapping when the clients genuinely use different path views. |
| A renamed file appears missing in Sonarr. | The file was renamed outside Sonarr, Sonarr still has the prior path recorded, or the new filename no longer maps cleanly to the episode. | Restore the known prior name if safe, run Refresh and Scan for the affected series, inspect manual import matching, and use Sonarr's Organize and Rename preview for future changes. |
| A media server shows duplicate episodes after import. | Both staging and library paths are being scanned, duplicate files exist, or the media server has stale metadata. | Ensure the media server scans only the managed library, resolve duplicate files through Sonarr after reviewing history, and then refresh the media server library. |

## Security considerations

### principles
Grant Sonarr only the access required to read completed downloads and manage its designated library roots.
Do not expose incomplete-download directories to media-server scanners or untrusted users.
Use consistent service identities or shared groups rather than globally writable media directories.
Treat filenames as untrusted input because release names can contain awkward characters and should never be interpolated unsafely into shell commands.
Back up Sonarr's database and configuration before changing production naming policy or performing a large rename.
Review path mappings carefully so a container cannot unexpectedly reach unrelated host data.
Do not publish real library inventories without review because filenames may reveal viewing habits, account names, mount layouts, or unreleased content.

### production_change_gate
Capture the current naming templates.
Confirm a recent Sonarr configuration and database backup.
Preview proposed names in Sonarr.
Test one noncritical series.
Check subtitle and sidecar handling.
Verify media-server visibility after the change.
Record the approved naming policy and date.

## Rollback

### lab_cleanup
Remove only the classroom exercise contents with a bounded Python cleanup, then recreate the empty class directory if the course runner expects it to remain.

### lab_cleanup_command
python3 - <<'PY'
from pathlib import Path
import shutil
root = Path('/opt/lab-classroom/class43')
if root.exists() and root.resolve() == Path('/opt/lab-classroom/class43'):
    for child in root.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()
PY

### production_guidance
Do not use the classroom cleanup procedure on a production path.
If a production naming change was only saved but no rename ran, restore the previously recorded templates.
If Sonarr renamed files, use Sonarr's own preview and rename workflow to restore the prior policy where possible.
If mappings are uncertain, stop automated changes, compare Sonarr history with backups, and restore only after episode identity is confirmed.
After restoring names, run Refresh and Scan for affected series and verify the media server's entries.

## Video narration notes

In this class, we are treating naming as operational metadata rather than decoration. Sonarr maintains a database, but a well-structured filesystem remains valuable when migrating servers, restoring backups, inspecting duplicates, or diagnosing a failed import. Begin with the boundary between downloads and the library. The download client writes incomplete and completed jobs into a staging area. Sonarr reads the completed job, maps it to episodes, and imports it into a managed root folder. The media server should scan the managed library, not the active download area.

Next, consider what a filename must communicate. A useful name visibly identifies the series, the season and episode, and often the episode title. Quality and release-group information should be retained when Sonarr has parsed them because they help explain what the file is and support future upgrade decisions. A year in the series folder disambiguates productions that share a title. Multi-episode files require special attention so that every represented episode remains visible to the automation stack.

Import mechanics matter as much as naming. If a torrent must continue seeding and the download and library paths share one filesystem, Sonarr may create a hardlink. The two paths then reference the same underlying data. If the paths cross filesystems, a hardlink cannot be created and a copy may consume additional space. Container operators must reason about the underlying host mounts rather than only the path strings visible inside containers.

The classroom exercise creates text fixtures with media-like extensions under the dedicated class directory. One file follows the policy, one has an ambiguous name, one exposes a duplicate episode identity, and one looks like a sample. The audit script does not claim to inspect media content. It identifies naming evidence that deserves operator review. The rename report also refuses to invent missing quality and release-group metadata. That restraint is important: a tidy filename containing false information is worse than an honest filename marked for review.

For production, use Sonarr's preview before renaming. Capture current templates, back up the application database and configuration, test one noncritical series, and verify subtitles and media-server visibility. If a file has already been renamed outside Sonarr, stop further bulk changes and reconcile the filesystem with Sonarr before proceeding. The goal is not merely attractive filenames. The goal is a library whose paths, application records, and operational history agree.

## References

- Sonarr Media Management settings: https://wiki.servarr.com/sonarr/settings#media-management
- Sonarr FAQ: https://wiki.servarr.com/sonarr/faq
- Sonarr Docker guidance: https://wiki.servarr.com/docker-guide
- TRaSH Guides Sonarr recommended naming scheme: https://trash-guides.info/Sonarr/Sonarr-recommended-naming-scheme/
- TRaSH Guides hardlinks and instant moves: https://trash-guides.info/Hardlinks/Hardlinks-and-Instant-Moves/
- Python pathlib documentation: https://docs.python.org/3/library/pathlib.html
- GNU findutils manual: https://www.gnu.org/software/findutils/manual/html_mono/find.html

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

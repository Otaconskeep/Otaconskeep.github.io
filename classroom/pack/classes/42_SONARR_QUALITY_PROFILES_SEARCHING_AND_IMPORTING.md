# Class 42 — Sonarr Quality Profiles, Searching, and Importing

**Learning objective:** Explain the difference between a quality definition, quality profile, custom format, and release score.; Describe how monitoring, RSS processing, automatic search, and interactive search differ.; Predict whether a candidate release is allowed, rejected, or considered an upgrade.; Explain why quality ranking and custom-format scoring must be considered separately.; Distinguish automatic import, manual import, copy-based import, move-based import, and hardlink-based import.; Verify a hardlink import by comparing device numbers, inode numbers, and link counts.; Identify common reasons a download remains in Sonarr's activity queue without importing.; Apply safe path, permission, and download-client practices to Sonarr imports.
**Bloom level:** Understand / Apply
**Track:** Media Automation · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach administrators how Sonarr evaluates quality profiles, ranks search results, decides whether an episode is an upgrade, and imports a selected download into a series library. The lab uses a self-contained simulation so that students can inspect every decision without changing a production Sonarr database, download client, or media library.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### primary
Sonarr v4 concepts and terminology

### notes
The lab is an educational decision model and does not call Sonarr's API or reproduce every release-comparison tie-break rule.
Sonarr v3 installations may display different labels or place profile controls in different interface locations.
Custom-format behavior depends on the scores configured in the quality profile assigned to a series.
Import behavior depends on operating system, filesystem, container mounts, download protocol, download-client state, and Sonarr settings.
Hardlink verification commands use GNU stat syntax commonly available on Linux.

## Learning objective

- Explain the difference between a quality definition, quality profile, custom format, and release score.
- Describe how monitoring, RSS processing, automatic search, and interactive search differ.
- Predict whether a candidate release is allowed, rejected, or considered an upgrade.
- Explain why quality ranking and custom-format scoring must be considered separately.
- Distinguish automatic import, manual import, copy-based import, move-based import, and hardlink-based import.
- Verify a hardlink import by comparing device numbers, inode numbers, and link counts.
- Identify common reasons a download remains in Sonarr's activity queue without importing.
- Apply safe path, permission, and download-client practices to Sonarr imports.

## Why this matters

Teach administrators how Sonarr evaluates quality profiles, ranks search results, decides whether an episode is an upgrade, and imports a selected download into a series library. The lab uses a self-contained simulation so that students can inspect every decision without changing a production Sonarr database, download client, or media library.

## Prerequisites

- Completion of introductory Sonarr configuration and series-management lessons.
- Basic understanding of seasons, episode numbering, release names, and video resolutions.
- Ability to run shell commands and read JSON files.
- Python 3, stat, install, printf, and ln available on the lab host.
- Write access to /opt/lab-classroom/class42/.

## Required reading

- Sonarr Settings documentation: https://wiki.servarr.com/sonarr/settings
- Sonarr FAQ: https://wiki.servarr.com/sonarr/faq
- Sonarr troubleshooting guide: https://wiki.servarr.com/sonarr/troubleshooting
- TRaSH Guides Sonarr collection: https://trash-guides.info/Sonarr/

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Quality definition | A named source and resolution category, such as WEBDL-1080p or Bluray-1080p, together with configurable file-size limits. |
| Quality profile | A policy assigned to a series that identifies allowed qualities, their preference order, whether upgrades are permitted, and when quality upgrades should stop. |
| Custom format | A set of matching conditions used to classify release characteristics such as codec, release group, audio format, streaming service, or unwanted attributes. |
| Custom-format score | The sum of the scores assigned by the active quality profile to all custom formats matched by a release. |
| Minimum custom-format score | The lowest acceptable custom-format score. A release below this threshold is ineligible even when its quality is allowed. |
| Upgrade-until quality | The quality level at which Sonarr no longer needs to seek a higher quality for an existing episode file. |
| Upgrade-until custom-format score | The custom-format score target used when determining whether further score-based upgrades remain desirable within the applicable quality rules. |
| Monitored episode | An episode Sonarr is permitted to consider for grabbing when an eligible release is discovered or a search is initiated. |
| RSS sync | Periodic processing of newly announced releases from configured indexers. It does not perform a historical search of the indexer's entire catalog. |
| Automatic search | A search in which Sonarr evaluates results and attempts to grab the best eligible candidate without requiring the operator to choose a release. |
| Interactive search | A search that displays candidates, scores, rejection reasons, age, size, indexer, and other details so an operator can select a release. |
| Completed Download Handling | The Sonarr process that observes completed download-client jobs and imports recognized episode files into the configured series folder. |
| Remote path mapping | A mapping used when the download client reports a path that is valid in its environment but differs from the path through which Sonarr accesses the same files. |
| Hardlink | A second directory entry pointing to the same file data on one filesystem. A hardlink allows a seeding copy and a library copy to coexist without duplicating file content. |
| Manual import | An operator-guided import in which files are reviewed and mapped to series, season, episode, quality, and language information before being placed in the library. |

## Instruction

Sonarr makes acquisition decisions by combining several layers of policy. Quality definitions describe categories and size limits, while a quality profile says which categories are allowed and how they are ordered. A custom format does not create a quality category; it detects additional release characteristics and contributes a score configured in the selected profile. This distinction matters because an allowed quality can still be rejected for falling below the minimum custom-format score, exceeding a size limit, being blocklisted, being unparsable, or failing another eligibility rule.

Monitoring is permission, not an immediate search request. A monitored missing episode can be considered when RSS processing discovers a newly posted release, but RSS processing normally examines recent announcements rather than searching all historical results. An automatic search actively queries indexers and lets Sonarr select an eligible result. An interactive search exposes the candidates and rejection reasons to the operator. Interactive search is therefore the preferred diagnostic tool when a release exists but Sonarr does not choose it.

Upgrade behavior must be evaluated against the episode's current file. Sonarr considers whether upgrades are enabled, whether the candidate quality is preferred over the current quality, whether configured targets have already been reached, and whether custom-format scoring permits or favors replacement. Quality order remains meaningful; a large positive score should not be treated as permission to ignore every other profile rule. Administrators should inspect the rejection icons and decision details rather than assuming that the numerically highest score always wins.

After a download completes, Sonarr must be able to resolve the path reported by the download client, identify a video file, parse or otherwise map it to the correct episode, and write to the series folder. If Sonarr and the download client see different path namespaces, a remote path mapping may be required. Container deployments frequently fail here because the two applications mount the same storage at different internal paths. Consistent paths are simpler and reduce configuration mistakes.

An import can copy, move, or hardlink a file depending on download state, configuration, and filesystem layout. Hardlinks require the source and destination to reside on the same filesystem. They share an inode but remain independently named directory entries. Removing one name does not remove the underlying file while another hardlink remains. Hardlinks are especially useful when a completed torrent must continue seeding while the episode also appears under an organized library name. This lesson models the decision and hardlink import process entirely under the class sandbox; it does not claim to reproduce every Sonarr protocol or tie-break rule.

## Architecture

### components
Indexer: returns release metadata to Sonarr through a configured integration.
Sonarr decision engine: applies monitoring state, quality rules, custom formats, scores, size limits, history, and rejection rules.
Download client: retrieves the selected release and reports its state and output path.
Completed Download Handling: associates a completed job with a Sonarr grab and evaluates files for import.
Library filesystem: stores the organized series, season, and episode paths used by media servers.
Media server: scans the library after Sonarr has imported or renamed files.

### decision_flow
A release is discovered through RSS processing or an explicit search.
Sonarr parses the title and associates it with a series and episode.
The assigned quality profile determines whether the parsed quality is allowed.
Size limits, language rules, custom formats, scores, history, and other restrictions are evaluated.
An eligible release may be sent to the download client.
The download client reports completion and a path.
Sonarr resolves the path, verifies episode mapping, and imports the media file.
The imported name and location are recorded in Sonarr's database, and configured downstream notifications may run.

### lab_boundary
All generated profiles, candidate metadata, simulated downloads, library entries, reports, and rollback artifacts remain below /opt/lab-classroom/class42/. The lab does not contact indexers, modify a Sonarr database, or alter a real media library.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Create a second profile design on paper or as /opt/lab-classroom/class42/config/homework-profile.json that allows 720p and 1080p releases but stops quality upgrades at WEBDL-1080p.
Add one simulated candidate with an allowed quality but a score below the minimum. Predict the rejection reason before running the decision script.
Add two candidates of the same quality with different custom-format scores and explain which candidate the class model selects.
Document three real-world custom formats you would consider useful and state whether each should receive a positive, zero, or negative score. Do not assign arbitrary production values without reviewing release-policy requirements.
Draw the path seen by a download client, the path seen by Sonarr, and the final library path for a containerized deployment. Identify whether a remote path mapping would be necessary.
Write a short incident checklist for a completed download that is stuck in Sonarr's activity queue.

## Feynman teach-back

### prompt
Explain Sonarr's workflow to a new administrator without using the phrases quality magic or best release.

### model_explanation
Sonarr first needs permission to manage an episode, which is represented by monitoring. It discovers releases through recent-feed processing or an explicit search. It parses each release, checks whether the quality is allowed, applies custom-format scores and other restrictions, and rejects anything that violates the profile. If a release is selected, Sonarr asks the download client to retrieve it. After completion, Sonarr must be able to see the reported path and identify the episode file. It then places the file in the organized series directory by copying, moving, or hardlinking it. A hardlink is possible only when source and destination are on the same filesystem. The operator can understand a surprising decision by checking interactive-search rejection reasons, the activity queue, history, and logs.

### self_check
Can you explain why monitoring does not immediately search old indexer results?
Can you explain why an allowed quality may still be rejected?
Can you explain why a high custom-format score does not make a disallowed quality eligible?
Can you explain why matching inode numbers demonstrate a hardlink?
Can you explain how inconsistent container paths interrupt Completed Download Handling?

## Retrieval check

1. 1. What is the functional difference between a quality definition and a quality profile?
2. 2. Does monitoring a missing episode immediately perform a historical search?
3. 3. Why can an allowed Bluray-1080p release still be rejected?
4. 4. What is the primary diagnostic advantage of interactive search over automatic search?
5. 5. What two filesystem values should match when verifying that two paths are hardlinks to the same file?
6. 6. Why can a hardlink not normally be created across two filesystems?
7. 7. What problem does a remote path mapping solve?
8. 8. In the lab, why is the Atlas WEBDL-1080p release selected instead of Northstar?
9. 9. In the lab, why is the 2160p candidate rejected despite its score of 100?
10. 10. Name three broad conditions Sonarr must satisfy before a completed download can be imported.

## Guided lab

### scenario
Harbor Lights S01E03 currently exists at HDTV-720p. Four search candidates are evaluated against a simulated profile. The selected WEBDL-1080p release is then hardlinked from a simulated completed-download directory into an organized series directory.

### safety_constraints
Run the commands exactly as written.
Do not substitute a production download or media path.
Do not point Sonarr itself at the simulated files.
All writes must remain under /opt/lab-classroom/class42/.

### steps
### step
1

### title
Create the isolated profile, candidates, and simulated download

### command
install -d /opt/lab-classroom/class42/config /opt/lab-classroom/class42/downloads/harbor-lights-s01e03 /opt/lab-classroom/class42/library/Harbor_Lights/Season_01 /opt/lab-classroom/class42/reports /opt/lab-classroom/class42/rollback
python3 - <<'PY'
import json
from pathlib import Path
root = Path('/opt/lab-classroom/class42')
profile = {
    'name': 'HD Preferred',
    'upgrades_allowed': True,
    'allowed_qualities_low_to_high': [
        'HDTV-720p',
        'WEBDL-720p',
        'WEBDL-1080p',
        'Bluray-1080p'
    ],
    'upgrade_until_quality': 'Bluray-1080p',
    'minimum_custom_format_score': 0,
    'upgrade_until_custom_format_score': 50
}
state = {
    'series': 'Harbor Lights',
    'episode': 'S01E03',
    'current_quality': 'HDTV-720p',
    'current_custom_format_score': 0
}
candidates = [
    {
        'title': 'Northstar.Harbor.Lights.S01E03.1080p.WEB-DL.DDP5.1.H.264',
        'quality': 'WEBDL-1080p',
        'custom_format_score': 25,
        'revision': 1
    },
    {
        'title': 'Atlas.Harbor.Lights.S01E03.1080p.WEB-DL.DDP5.1.HEVC',
        'quality': 'WEBDL-1080p',
        'custom_format_score': 75,
        'revision': 1
    },
    {
        'title': 'Legacy.Harbor.Lights.S01E03.1080p.BluRay.x264',
        'quality': 'Bluray-1080p',
        'custom_format_score': -50,
        'revision': 1
    },
    {
        'title': 'Ultra.Harbor.Lights.S01E03.2160p.WEB-DL.HEVC',
        'quality': 'WEBDL-2160p',
        'custom_format_score': 100,
        'revision': 1
    }
]
(root / 'config/profile.json').write_text(json.dumps(profile, indent=2) + '\n', encoding='utf-8')
(root / 'config/state.json').write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
(root / 'config/candidates.json').write_text(json.dumps(candidates, indent=2) + '\n', encoding='utf-8')
source = root / 'downloads/harbor-lights-s01e03/Atlas.Harbor.Lights.S01E03.1080p.WEB-DL.DDP5.1.HEVC.mkv'
source.write_text('Class 42 simulated media file; this is not playable video.\n', encoding='utf-8')
PY
### step
2

### title
Evaluate candidate eligibility and ranking

### command
python3 - <<'PY' | tee /opt/lab-classroom/class42/reports/search-decision.txt
import json
from pathlib import Path
root = Path('/opt/lab-classroom/class42')
profile = json.loads((root / 'config/profile.json').read_text(encoding='utf-8'))
state = json.loads((root / 'config/state.json').read_text(encoding='utf-8'))
candidates = json.loads((root / 'config/candidates.json').read_text(encoding='utf-8'))
order = profile['allowed_qualities_low_to_high']
rank = {quality: position for position, quality in enumerate(order)}
current_rank = rank[state['current_quality']]
target_rank = rank[profile['upgrade_until_quality']]
eligible = []
for candidate in candidates:
    quality = candidate['quality']
    reason = None
    if quality not in rank:
        reason = 'quality is not allowed by the profile'
    elif candidate['custom_format_score'] < profile['minimum_custom_format_score']:
        reason = 'custom-format score is below the minimum'
    elif not profile['upgrades_allowed'] and rank[quality] > current_rank:
        reason = 'upgrades are disabled'
    elif rank[quality] <= current_rank and candidate['custom_format_score'] <= state['current_custom_format_score']:
        reason = 'candidate is not an improvement over the current file'
    elif rank[quality] > target_rank:
        reason = 'quality is above the configured upgrade target'
    if reason:
        print(f"REJECT {candidate['title']} :: {reason}")
    else:
        eligible.append(candidate)
        print(f"ACCEPT {candidate['title']} :: quality={quality} score={candidate['custom_format_score']}")
if not eligible:
    raise SystemExit('No eligible candidate')
selected = max(eligible, key=lambda item: (rank[item['quality']], item['custom_format_score'], item['revision']))
print(f"SELECT {selected['title']}")
(root / 'reports/selected-release.json').write_text(json.dumps(selected, indent=2) + '\n', encoding='utf-8')
PY
### step
3

### title
Review why each candidate was accepted or rejected

### command
cat /opt/lab-classroom/class42/reports/search-decision.txt && printf '\nSelected release metadata:\n' && cat /opt/lab-classroom/class42/reports/selected-release.json
### step
4

### title
Confirm that source and destination directories share a filesystem

### command
stat -c 'device=%d path=%n' /opt/lab-classroom/class42/downloads/harbor-lights-s01e03 /opt/lab-classroom/class42/library/Harbor_Lights/Season_01
### step
5

### title
Perform the simulated hardlink import and record its metadata

### command
python3 - <<'PY'
import json
import os
from pathlib import Path
root = Path('/opt/lab-classroom/class42')
source = root / 'downloads/harbor-lights-s01e03/Atlas.Harbor.Lights.S01E03.1080p.WEB-DL.DDP5.1.HEVC.mkv'
destination = root / 'library/Harbor_Lights/Season_01/Harbor Lights - S01E03 - Breakwater [WEBDL-1080p].mkv'
if not destination.exists():
    os.link(source, destination)
selected = json.loads((root / 'reports/selected-release.json').read_text(encoding='utf-8'))
manifest = {
    'series': 'Harbor Lights',
    'season': 1,
    'episode': 3,
    'episode_title': 'Breakwater',
    'source_path': str(source),
    'library_path': str(destination),
    'quality': selected['quality'],
    'custom_format_score_at_grab': selected['custom_format_score'],
    'import_method': 'hardlink'
}
(root / 'reports/import-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
PY
cat /opt/lab-classroom/class42/reports/import-manifest.json
### step
6

### title
Verify that the import is a hardlink rather than an independent copy

### command
stat -c 'device=%d inode=%i links=%h path=%n' /opt/lab-classroom/class42/downloads/harbor-lights-s01e03/Atlas.Harbor.Lights.S01E03.1080p.WEB-DL.DDP5.1.HEVC.mkv '/opt/lab-classroom/class42/library/Harbor_Lights/Season_01/Harbor Lights - S01E03 - Breakwater [WEBDL-1080p].mkv'
### step
7

### title
Validate the manifest and filesystem relationship programmatically

### command
python3 - <<'PY'
import json
import os
from pathlib import Path
root = Path('/opt/lab-classroom/class42')
manifest = json.loads((root / 'reports/import-manifest.json').read_text(encoding='utf-8'))
source = Path(manifest['source_path'])
destination = Path(manifest['library_path'])
assert source.exists(), 'Simulated download is missing'
assert destination.exists(), 'Imported library entry is missing'
source_stat = source.stat()
destination_stat = destination.stat()
assert source_stat.st_dev == destination_stat.st_dev, 'Paths are on different filesystems'
assert source_stat.st_ino == destination_stat.st_ino, 'Import is not a hardlink'
assert source_stat.st_nlink >= 2, 'Expected at least two hardlinks'
assert manifest['quality'] == 'WEBDL-1080p', 'Unexpected imported quality'
assert manifest['custom_format_score_at_grab'] == 75, 'Unexpected custom-format score'
print('PASS: decision manifest and hardlink import are consistent')
PY

### discussion_prompts
Why was the Bluray-1080p candidate rejected even though Bluray-1080p is the highest allowed quality?
Why was the 2160p release rejected despite having the highest custom-format score?
What would change if the minimum custom-format score were lowered to -100?
What operational condition would prevent the hardlink operation even when both paths are writable?
Why should an operator use interactive search before weakening a quality profile?

## Expected results

- The class directory contains config, downloads, library, reports, and rollback subdirectories.
- The Northstar WEBDL-1080p candidate is accepted with a custom-format score of 25.
- The Atlas WEBDL-1080p candidate is accepted with a custom-format score of 75 and selected over Northstar.
- The Legacy Bluray-1080p candidate is rejected because its score of -50 is below the configured minimum of 0.
- The Ultra WEBDL-2160p candidate is rejected because WEBDL-2160p is not allowed by the profile.
- The selected-release report identifies Atlas.Harbor.Lights.S01E03.1080p.WEB-DL.DDP5.1.HEVC.
- The library filename identifies Harbor Lights S01E03, episode title Breakwater, and quality WEBDL-1080p.
- The simulated download and library entry report the same device number and inode number.
- The link count is at least two after import.
- The final validation prints PASS: decision manifest and hardlink import are consistent.

## Verification checkpoints

- [ ] Run: cat /opt/lab-classroom/class42/reports/search-decision.txt
- [ ] Confirm the final line is: SELECT Atlas.Harbor.Lights.S01E03.1080p.WEB-DL.DDP5.1.HEVC
- [ ] Run: cat /opt/lab-classroom/class42/reports/import-manifest.json
- [ ] Confirm import_method is hardlink, quality is WEBDL-1080p, and custom_format_score_at_grab is 75.
- [ ] Run: stat -c '%d %i %h %n' /opt/lab-classroom/class42/downloads/harbor-lights-s01e03/Atlas.Harbor.Lights.S01E03.1080p.WEB-DL.DDP5.1.HEVC.mkv '/opt/lab-classroom/class42/library/Harbor_Lights/Season_01/Harbor Lights - S01E03 - Breakwater [WEBDL-1080p].mkv'
- [ ] Confirm both files have identical device and inode values and a link count of at least two.
- [ ] Run the validation command from lab step 7 and confirm that it exits successfully with the documented PASS message.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The setup command reports permission denied under /opt/lab-classroom/class42/. | The current lab account does not have permission to create or update the assigned classroom directory. | Have the lab administrator grant the assigned account access to /opt/lab-classroom/class42/ without broadening access to production Sonarr or media directories. |
| The decision script reports that no eligible candidate exists. | The profile or candidate JSON was edited so every release violates an allowed-quality, score, target, or upgrade rule. | Compare profile.json and candidates.json with the lesson values. Confirm WEBDL-1080p is in allowed_qualities_low_to_high and the minimum custom-format score is 0. |
| The selected candidate is Northstar instead of Atlas. | Atlas's score was changed, the quality order was edited, or selected-release.json contains output from a modified run. | Confirm both candidates are WEBDL-1080p, Northstar has score 25, Atlas has score 75, and then rerun the decision step. |
| The hardlink import fails with an invalid cross-device link error. | The source and destination resolve to different filesystems or mounts. | Use the stat device-number check. In a real deployment, align the download and library paths on one filesystem for hardlinks or permit Sonarr to copy when separate filesystems are intentional. |
| A real Sonarr download remains in the activity queue with an import warning. | Sonarr cannot access the download-client path, cannot parse the file, cannot write to the series folder, or lacks a matching download history record. | Inspect the activity warning and Sonarr logs. Verify path visibility from Sonarr's runtime environment, filesystem access, episode parsing, category configuration, and download-client history. |
| A real download client reports a path that does not exist inside the Sonarr container. | The applications use inconsistent container mount paths. | Prefer consistent internal paths for shared storage. If that is not possible, configure a narrowly scoped remote path mapping from the download client's reported path to Sonarr's accessible path. |
| A release is visible in interactive search but has a rejection icon. | The release violates a quality, size, language, score, history, availability, or parsing rule. | Open the rejection details and correct the specific policy or metadata issue. Do not weaken unrelated profile controls merely to force a grab. |
| The source and destination have different inode numbers. | The destination was copied, replaced after linking, or created on another filesystem. | Confirm both directories report the same device number, move the existing destination into the class rollback directory, and repeat the import step. |

## Security considerations

Run Sonarr and the download client as dedicated service identities rather than as an unrestricted administrative account.
Grant Sonarr only the access needed to read completed downloads and manage the intended library roots.
Do not grant a download client unrestricted write access to the organized media library when Sonarr is responsible for imports.
Treat release names, archive contents, subtitle files, and indexer metadata as untrusted input.
Keep download staging paths separate from application configuration and operating-system directories.
Use consistent, explicit container mounts so that remote path mappings do not accidentally expose broader host paths.
Review custom formats with negative scores and minimum score rules before enabling automatic searches across a large monitored library.
Back up the Sonarr configuration and database before making broad production profile changes.
Use Sonarr's interactive search and history views to investigate decisions rather than bypassing rejection rules.
Retain logs long enough to trace grab, download, and import events, while protecting logs that may contain indexer URLs, API keys, or private release information.

## Rollback

### scope
The lesson does not alter a live Sonarr instance. Rollback returns the sandbox to its pre-import state while preserving generated evidence inside the same class directory.

### command
python3 - <<'PY'
from pathlib import Path
root = Path('/opt/lab-classroom/class42').resolve()
allowed = Path('/opt/lab-classroom/class42').resolve()
if root != allowed:
    raise SystemExit('Refusing rollback outside the Class 42 sandbox')
rollback = root / 'rollback'
rollback.mkdir(parents=True, exist_ok=True)
items = [
    root / 'library/Harbor_Lights/Season_01/Harbor Lights - S01E03 - Breakwater [WEBDL-1080p].mkv',
    root / 'reports/import-manifest.json'
]
for item in items:
    if item.exists():
        destination = rollback / item.name
        if destination.exists():
            raise SystemExit(f'Rollback destination already exists: {destination}')
        item.rename(destination)
        print(f'MOVED {item} -> {destination}')
PY

### verification
Confirm that the simulated source remains in /opt/lab-classroom/class42/downloads/harbor-lights-s01e03/ and that the imported library entry has moved to /opt/lab-classroom/class42/rollback/.

### production_guidance
For a live Sonarr deployment, restore the saved profile values through Sonarr's interface or API, verify the affected series assignments, and avoid deleting imported media until history, seeding requirements, and backups have been reviewed.

## Video narration notes

Welcome to Class 42. This class focuses on the decisions between discovering a release and placing an episode in a Sonarr-managed library.
Begin by separating four concepts. Quality definitions describe categories and size boundaries. Quality profiles determine which categories are allowed and preferred. Custom formats detect release characteristics. Profile-specific scores express how desirable or undesirable those characteristics are.
Monitoring does not mean search now. It means Sonarr may acquire the episode when an eligible release is discovered. RSS processing watches recent announcements, while automatic and interactive searches query for existing results.
When a candidate appears, Sonarr parses its series, episode, quality, language, and other attributes. The assigned profile must permit the quality. Custom formats are evaluated, scores are totaled, and additional restrictions are applied. An attractive score cannot make a disallowed quality valid.
Interactive search is one of the best diagnostic tools because it exposes rejected releases and their reasons. Before changing a profile, read those reasons and decide whether the policy or the release is wrong.
The lab models a current HDTV-720p episode and four candidates. Two WEBDL-1080p releases are eligible. The Atlas release wins within the class model because it has the higher custom-format score. A Bluray candidate is rejected for falling below the minimum score, and a 2160p candidate is rejected because its quality is not allowed.
After selection, the download client retrieves the release. Completed Download Handling then needs a usable path, a recognizable episode file, and write access to the destination. Container path mismatches are a frequent source of import failures.
The lab performs a hardlink import. The source and destination names differ, but stat reports the same device and inode. That proves both names refer to the same underlying file data. The link count shows that more than one directory entry exists.
In production, use consistent paths, dedicated service identities, narrow storage access, and backups before broad profile changes. Diagnose with interactive search, activity details, history, and logs rather than bypassing rejection rules.

## References

- Sonarr official site: https://sonarr.tv/
- Sonarr Settings documentation: https://wiki.servarr.com/sonarr/settings
- Sonarr FAQ: https://wiki.servarr.com/sonarr/faq
- Sonarr troubleshooting documentation: https://wiki.servarr.com/sonarr/troubleshooting
- TRaSH Guides for Sonarr: https://trash-guides.info/Sonarr/
- GNU Coreutils stat documentation: https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html
- Linux man-pages link documentation: https://man7.org/linux/man-pages/man2/link.2.html

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

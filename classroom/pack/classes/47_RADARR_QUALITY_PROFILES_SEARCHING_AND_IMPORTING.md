# Class 47: Radarr Quality Profiles, Searching, and Importing

**Learning objective:** Explain the difference between a quality definition, quality profile, custom format, and release restriction; Describe the difference between automatic search, interactive search, RSS-style monitoring, and manual import; Predict whether Radarr will consider an existing file eligible for an upgrade; Identify common reasons that a release is rejected before download; Explain how completed download handling connects a download-client item to a Radarr movie; Recognize import failures caused by ambiguous naming, inaccessible paths, permissions, or cross-filesystem behavior; Use a sandbox policy model to compare candidate releases without changing a production Radarr configuration; Verify that an imported movie is matched to the correct title, year, edition, quality, and destination
**Bloom level:** Understand / Apply
**Track:** Media Automation · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach students how Radarr uses quality profiles, release metadata, custom formats, monitored status, searches, download-client history, and import matching to select and organize movie files. The lab uses an isolated policy simulator under /opt/lab-classroom/class47/ so students can practice evaluating releases and import decisions without changing a live Radarr instance.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### radarr
Concepts apply to current supported Radarr releases. Menu names, sorting details, and custom-format controls may vary by installed version.

### operating_systems
Linux
Windows
macOS
Containerized deployments

### lab_runtime
The isolated exercise requires a POSIX-compatible shell, Python 3, and write access to /opt/lab-classroom/class47/.

### notes
The evaluator is a simplified educational model and must not be treated as an exact implementation of Radarr's internal release-ranking algorithm.

## Learning objective

- Explain the difference between a quality definition, quality profile, custom format, and release restriction
- Describe the difference between automatic search, interactive search, RSS-style monitoring, and manual import
- Predict whether Radarr will consider an existing file eligible for an upgrade
- Identify common reasons that a release is rejected before download
- Explain how completed download handling connects a download-client item to a Radarr movie
- Recognize import failures caused by ambiguous naming, inaccessible paths, permissions, or cross-filesystem behavior
- Use a sandbox policy model to compare candidate releases without changing a production Radarr configuration
- Verify that an imported movie is matched to the correct title, year, edition, quality, and destination

## Why this matters

Teach students how Radarr uses quality profiles, release metadata, custom formats, monitored status, searches, download-client history, and import matching to select and organize movie files. The lab uses an isolated policy simulator under /opt/lab-classroom/class47/ so students can practice evaluating releases and import decisions without changing a live Radarr instance.

## Prerequisites

- Completion of introductory Radarr installation and library-management lessons
- Basic familiarity with indexers, download clients, and media library folders
- Ability to read JSON and run Python 3 from a terminal
- Understanding of absolute paths, file ownership, and filesystem permissions
- A conceptual understanding of movie titles, release years, resolutions, codecs, and release names

## Required reading

- Servarr Wiki: Radarr overview — https://wiki.servarr.com/radarr
- Servarr Wiki: Radarr settings — https://wiki.servarr.com/radarr/settings
- Servarr Wiki: Radarr library and movie management — https://wiki.servarr.com/radarr/library
- Servarr Wiki: Radarr FAQ — https://wiki.servarr.com/radarr/faq

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Quality definition | A definition of a named source or resolution class, such as WEB-DL 1080p or Bluray-1080p, together with permitted file-size ranges. |
| Quality profile | A policy assigned to a movie that declares allowed qualities, their preference order or grouping, upgrade behavior, cutoff behavior, and custom-format score requirements. |
| Cutoff | The quality level at which Radarr considers the quality goal satisfied. A movie may stop receiving quality-based upgrades after reaching this point, although custom-format upgrade behavior can add further conditions. |
| Custom format | A set of release-name or metadata conditions used to identify characteristics such as codec, audio format, release group, edition, source attribute, or unwanted feature. |
| Custom-format score | A numeric preference associated with a matching custom format inside a quality profile. Positive scores express preference, negative scores express avoidance, and the profile can enforce a minimum acceptable total. |
| Monitored movie | A movie for which Radarr is permitted to watch for releases and evaluate upgrades according to its assigned profile. |
| Automatic search | A search in which Radarr queries configured indexers, evaluates results, and normally selects an acceptable candidate without requiring the user to choose a specific release. |
| Interactive search | A search that displays candidate releases and rejection reasons so an operator can inspect and deliberately choose a release. |
| RSS or feed processing | Periodic processing of newly announced releases from indexers. It is not a search of all historical releases and only helps monitored movies when a suitable new release appears. |
| Completed Download Handling | The workflow through which Radarr observes completed items from a configured download client, identifies the associated movie, and imports an eligible media file. |
| Manual import | An operator-guided workflow that scans an existing file or directory and allows its movie, quality, language, and other metadata to be reviewed before import. |
| Hardlink | A second directory entry referencing the same underlying file data. Hardlinks require source and destination to be on the same filesystem and avoid duplicating file data. |
| Remote path mapping | A translation used when a download client reports a path that is valid from its own perspective but differs from the path Radarr must use to access the same files. |
| Minimum availability | The release-state threshold, such as announced, in cinemas, or released, that influences when Radarr is allowed to search for or acquire a movie. |

## Instruction

Radarr separates the decision to look for a movie from the decision to accept a particular release. A movie must first be known to Radarr, assigned a root folder and quality profile, and usually be monitored. A quality profile defines the qualities that are allowed, their relative preference, whether upgrades are enabled, and the point at which the desired quality has been reached. Quality definitions are related but separate: they place size boundaries on named qualities. A release can therefore use an allowed quality and still be rejected because its reported size falls outside the configured definition.

Custom formats add preference information that basic source and resolution labels cannot express. They can recognize attributes such as codec, audio format, release group, edition, HDR variant, or an unwanted naming pattern. Each profile assigns scores to matching custom formats. A negative score does not universally mean an automatic rejection; rejection depends on the resulting total and the profile's minimum custom-format score. Likewise, a high score does not override every hard rejection. A release may still be rejected because the quality is not allowed, the movie is not a match, the size is invalid, the indexer is unavailable, a required term is missing, or another policy condition fails. Operators should read the rejection explanations shown by interactive search instead of assuming that the highest visible score always wins.

An automatic search asks configured indexers for available releases and lets Radarr choose according to its rules. Interactive search asks the same broad question but exposes candidates and rejection reasons to the operator. Feed processing is different: it evaluates newly announced releases and does not search all historical indexer content. Enabling monitoring does not immediately guarantee a search, and assigning a stronger profile does not itself download a replacement. A separate search, a new feed announcement, or another configured trigger must present a candidate.

Importing is a distinct stage from searching and downloading. Radarr must associate the completed download with a known movie, identify a usable movie file, infer or receive its quality, and access both the download location and library destination. Completed Download Handling commonly uses download-client history and the category assigned to Radarr. If the client reports a path that Radarr cannot see, the import fails even though the download completed successfully. Container deployments frequently expose this problem when two applications mount the same storage under different internal paths. Consistent paths are preferable; remote path mappings should be used only when the client genuinely reports a different path namespace.

A successful import can use a hardlink, copy, or move depending on configuration and download type. Hardlinks require source and destination to reside on the same filesystem. They are especially useful when a seeding torrent must remain in the download directory while the organized library also presents the file. If a hardlink cannot be created, an application may copy instead, increasing storage consumption. Permissions must allow Radarr to traverse the source path, read the file, create entries in the destination, and apply the intended naming behavior. Granting broad permissions is not a substitute for aligning service users, groups, ownership, and directory modes.

Manual import is appropriate for pre-existing media, downloads that lost their client association, or ambiguous files requiring operator review. The operator should verify the matched movie, year, edition, quality, language, and destination before approving an import. Samples, trailers, extras, and unrelated videos should not be mistaken for the main feature. An ambiguous filename should be mapped explicitly rather than accepted based only on a partial title. The most reliable troubleshooting sequence follows the pipeline: confirm the movie is monitored and available, inspect the quality profile, inspect search rejection reasons, confirm the download-client category and history entry, verify the path visible to Radarr, check permissions, and finally review the proposed import mapping.

## Architecture

### flow
Movie entry and monitoring policy -> search trigger or indexer feed -> indexer candidates -> quality and custom-format evaluation -> download-client submission -> completed client item -> import matching -> library naming and placement

### components
### name
Radarr movie database

### role
Stores the movie identity, monitored status, availability, assigned quality profile, existing file metadata, and root folder.
### name
Quality profile evaluator

### role
Determines whether qualities are allowed, whether an existing file can be upgraded, whether the cutoff is met, and whether custom-format scores satisfy policy.
### name
Indexer

### role
Returns release metadata and a download reference. Its results may be incomplete, incorrectly named, or temporarily unavailable.
### name
Download client

### role
Acquires the selected release and reports status, category, and completed path.
### name
Import processor

### role
Matches completed files to movies, determines quality and metadata, rejects unsuitable files, and creates the organized library entry.
### name
Filesystem

### role
Provides the download and library paths. Mount layout, ownership, permissions, and filesystem boundaries affect import behavior.

### decision_boundaries
Searching finds candidates but does not prove they can be imported.
Downloading acquires data but does not prove Radarr can see the completed path.
Importing validates identity and filesystem access before updating the library.
Renaming controls the organized filename and does not repair an incorrect movie match.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Design a 1080p quality profile on paper with at least two allowed qualities, a cutoff, an upgrade policy, and a minimum custom-format score. Explain every choice.
Create three hypothetical releases for one movie: one acceptable release, one quality rejection, and one custom-format rejection. State the exact reason for each outcome.
Draw a path map for a containerized Radarr and download client. Show the host path and the path visible inside each application, then identify whether a remote path mapping would be necessary.
Write a manual-import checklist covering movie identity, year, edition, quality, language, main-feature status, source path, destination, and permissions.
Explain why a monitored movie can remain missing even when its quality profile allows several qualities.
Compare hardlink, copy, and move behavior for a completed torrent that must continue seeding.

## Feynman teach-back

### prompt
Explain the Radarr pipeline to someone who believes a quality profile downloads and organizes a movie by itself.

### model_explanation
A quality profile is a rulebook, not a downloader. First, Radarr needs a movie entry and a reason to look, such as an automatic search, an interactive search, or a new indexer-feed item. It compares each candidate with the profile and other restrictions. If a candidate is accepted, Radarr sends it to a download client. After the client finishes, Radarr must still recognize the completed item, reach its path, identify the correct movie file, and import that file into the library. A failure in searching, downloading, path access, matching, or permissions can stop the pipeline even when the profile itself is correct.

### self_check
The explanation should distinguish discovery, candidate evaluation, downloading, completed-download recognition, and filesystem import as separate stages.

## Retrieval check

1. 1. What is the difference between a quality definition and a quality profile?
2. 2. Does assigning a quality profile automatically initiate a search? Explain.
3. 3. How does an interactive search differ from an automatic search?
4. 4. Why can a release with a positive custom-format score still be rejected?
5. 5. What does a quality cutoff represent?
6. 6. Why might a completed download remain in Radarr's activity queue instead of importing?
7. 7. Under what storage condition can Radarr create a hardlink between a download and library entry?
8. 8. Why is a remote path mapping sometimes required?
9. 9. What details should be checked before approving a manual import?
10. 10. Why is an indexer feed not equivalent to a historical search?

## Guided lab

### name
Evaluate release candidates and manual-import mappings in an isolated sandbox

### scope
All created or modified files remain under /opt/lab-classroom/class47/. The exercise does not contact indexers, download clients, or a live Radarr instance.

### steps
### step
1

### instruction
Create the isolated classroom directory and its input files.

### command
mkdir -p /opt/lab-classroom/class47 && cat > /opt/lab-classroom/class47/profile.json <<'JSON'
{
  "name": "Class47 1080p",
  "allowed_qualities": ["WEBDL-1080p", "Bluray-1080p"],
  "quality_order": ["WEBDL-1080p", "Bluray-1080p"],
  "cutoff": "Bluray-1080p",
  "upgrades_allowed": true,
  "minimum_custom_format_score": 0,
  "maximum_size_gb": 18
}
JSON
cat > /opt/lab-classroom/class47/candidates.json <<'JSON'
[
  {
    "release": "Example.Movie.2024.1080p.WEB-DL.DDP5.1.H.264-GROUPA",
    "movie_match": true,
    "quality": "WEBDL-1080p",
    "custom_format_score": 20,
    "size_gb": 7.8
  },
  {
    "release": "Example.Movie.2024.1080p.BluRay.DTS.x264-GROUPB",
    "movie_match": true,
    "quality": "Bluray-1080p",
    "custom_format_score": 30,
    "size_gb": 12.4
  },
  {
    "release": "Example.Movie.2024.2160p.REMUX.HEVC-GROUPC",
    "movie_match": true,
    "quality": "Remux-2160p",
    "custom_format_score": 50,
    "size_gb": 55.0
  },
  {
    "release": "Example.Movie.2024.720p.WEB-DL-GROUPD",
    "movie_match": true,
    "quality": "WEBDL-720p",
    "custom_format_score": 5,
    "size_gb": 3.2
  },
  {
    "release": "Different.Movie.2024.1080p.BluRay-GROUPE",
    "movie_match": false,
    "quality": "Bluray-1080p",
    "custom_format_score": 40,
    "size_gb": 10.2
  }
]
JSON
cat > /opt/lab-classroom/class47/imports.json <<'JSON'
[
  {
    "path": "/opt/lab-classroom/class47/downloads/Example.Movie.2024/Example.Movie.2024.1080p.BluRay.mkv",
    "title_match": true,
    "year_match": true,
    "is_main_feature": true,
    "quality_known": true
  },
  {
    "path": "/opt/lab-classroom/class47/downloads/Example.Movie/feature.mkv",
    "title_match": true,
    "year_match": false,
    "is_main_feature": true,
    "quality_known": false
  },
  {
    "path": "/opt/lab-classroom/class47/downloads/Example.Movie.2024/sample.mkv",
    "title_match": true,
    "year_match": true,
    "is_main_feature": false,
    "quality_known": true
  }
]
JSON
### step
2

### instruction
Create a simplified teaching model. This model demonstrates policy boundaries but is not intended to reproduce every internal Radarr sorting rule.

### command
cat > /opt/lab-classroom/class47/evaluate.py <<'PY'
import json
from pathlib import Path

ROOT = Path("/opt/lab-classroom/class47")
profile = json.loads((ROOT / "profile.json").read_text())
candidates = json.loads((ROOT / "candidates.json").read_text())
imports = json.loads((ROOT / "imports.json").read_text())

quality_rank = {name: rank for rank, name in enumerate(profile["quality_order"], start=1)}
accepted = []

print("RELEASE EVALUATION")
for candidate in candidates:
    reasons = []
    if not candidate["movie_match"]:
        reasons.append("movie identity does not match")
    if candidate["quality"] not in profile["allowed_qualities"]:
        reasons.append("quality is not allowed by the profile")
    if candidate["custom_format_score"] < profile["minimum_custom_format_score"]:
        reasons.append("custom-format score is below the profile minimum")
    if candidate["size_gb"] > profile["maximum_size_gb"]:
        reasons.append("reported size exceeds the classroom limit")

    if reasons:
        print(f"REJECT: {candidate['release']}")
        for reason in reasons:
            print(f"  - {reason}")
    else:
        accepted.append(candidate)
        print(f"ACCEPTABLE: {candidate['release']}")

if accepted:
    selected = max(
        accepted,
        key=lambda item: (quality_rank[item["quality"]], item["custom_format_score"])
    )
    print(f"SELECTED BY CLASSROOM POLICY: {selected['release']}")
    existing_quality = "WEBDL-1080p"
    cutoff_rank = quality_rank[profile["cutoff"]]
    existing_rank = quality_rank[existing_quality]
    selected_rank = quality_rank[selected["quality"]]
    upgrade = profile["upgrades_allowed"] and selected_rank > existing_rank and selected_rank <= cutoff_rank
    print(f"UPGRADE FROM {existing_quality}: {'YES' if upgrade else 'NO'}")

print("\nMANUAL IMPORT REVIEW")
for item in imports:
    reasons = []
    if not item["title_match"]:
        reasons.append("title is not matched")
    if not item["year_match"]:
        reasons.append("year is ambiguous or mismatched")
    if not item["is_main_feature"]:
        reasons.append("file appears to be an extra or sample")
    if not item["quality_known"]:
        reasons.append("quality needs operator confirmation")

    if reasons:
        print(f"REVIEW: {item['path']}")
        for reason in reasons:
            print(f"  - {reason}")
    else:
        print(f"READY: {item['path']}")
PY
### step
3

### instruction
Run the evaluator and inspect every acceptance, rejection, and manual-import decision.

### command
PYTHONDONTWRITEBYTECODE=1 python3 /opt/lab-classroom/class47/evaluate.py
### step
4

### instruction
Inspect the profile independently and identify the allowed qualities, cutoff, minimum custom-format score, and size ceiling.

### command
python3 -m json.tool /opt/lab-classroom/class47/profile.json
### step
5

### instruction
Perform a controlled policy experiment by changing minimum_custom_format_score from 0 to 25 in the sandbox profile, rerunning the evaluator, and observing that the WEB-DL candidate is no longer acceptable while the Bluray candidate remains acceptable.

### command
python3 - <<'PY'
import json
from pathlib import Path
path = Path("/opt/lab-classroom/class47/profile.json")
data = json.loads(path.read_text())
data["minimum_custom_format_score"] = 25
path.write_text(json.dumps(data, indent=2) + "\n")
PY
PYTHONDONTWRITEBYTECODE=1 python3 /opt/lab-classroom/class47/evaluate.py
### step
6

### instruction
Restore the original classroom policy by setting minimum_custom_format_score back to 0 and verify the restored value.

### command
python3 - <<'PY'
import json
from pathlib import Path
path = Path("/opt/lab-classroom/class47/profile.json")
data = json.loads(path.read_text())
data["minimum_custom_format_score"] = 0
path.write_text(json.dumps(data, indent=2) + "\n")
print(data["minimum_custom_format_score"])
PY

## Expected results

- The sandbox contains profile.json, candidates.json, imports.json, and evaluate.py under /opt/lab-classroom/class47/.
- The WEB-DL 1080p and Bluray-1080p releases are initially reported as acceptable.
- The 2160p remux is rejected because its quality is not allowed and its reported size exceeds the classroom limit.
- The 720p release is rejected because its quality is not allowed by the profile.
- The differently titled release is rejected because the movie identity does not match.
- The classroom policy selects the Bluray-1080p candidate and reports that it can upgrade the simulated existing WEB-DL 1080p file.
- Only the fully matched main-feature import is reported as ready without review.
- The ambiguous feature file requires review because its year is not matched and its quality is unknown.
- The sample file requires review because it is not the main feature.
- After the minimum custom-format score is raised to 25, the candidate with a score of 20 is rejected; restoring the value to 0 returns the original policy.

## Verification checkpoints

- [ ] Run: test -f /opt/lab-classroom/class47/profile.json && test -f /opt/lab-classroom/class47/candidates.json && test -f /opt/lab-classroom/class47/imports.json && test -f /opt/lab-classroom/class47/evaluate.py
- [ ] Run: python3 -m json.tool /opt/lab-classroom/class47/profile.json and confirm that the JSON is valid.
- [ ] Run: PYTHONDONTWRITEBYTECODE=1 python3 /opt/lab-classroom/class47/evaluate.py and confirm that no Python exception is displayed.
- [ ] Confirm that the output contains SELECTED BY CLASSROOM POLICY followed by the Bluray-1080p release.
- [ ] Confirm that the output contains UPGRADE FROM WEBDL-1080p: YES.
- [ ] Confirm that the 2160p remux output lists both an unallowed quality and excessive size.
- [ ] Confirm that the manual-import section reports one READY item and two REVIEW items.
- [ ] Run: python3 -c 'import json; print(json.load(open("/opt/lab-classroom/class47/profile.json"))["minimum_custom_format_score"])' and confirm the final value is 0.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The shell reports permission denied while creating /opt/lab-classroom/class47/. | The current classroom account does not have permission to create the assigned lab directory. | Use the classroom's approved privileged workflow to create and assign the directory to the student account. Do not redirect the exercise into a production application directory. |
| Python reports that profile.json or another input file does not exist. | Step 1 was skipped, a heredoc was not completed, or the file was created outside the required sandbox path. | Repeat Step 1 exactly and verify each file under /opt/lab-classroom/class47/ before running the evaluator. |
| Python reports a JSON decoding error. | A JSON file was edited with a missing comma, quote, bracket, or valid literal. | Run python3 -m json.tool against the named file, correct the location reported by the parser, and rerun the evaluator. |
| The classroom evaluator selects an unexpected release. | The profile or candidate fixtures were modified, or the quality order was reversed. | Compare the current JSON values with Step 1. Remember that later entries in the classroom quality_order list receive a higher rank. |
| A live Radarr interactive search shows different ordering from the classroom evaluator. | The evaluator is intentionally simplified, while Radarr also considers its release-ranking rules, protocols, age, seeders, languages, indexer priorities, custom-format behavior, and other configured constraints. | Treat the lab as a policy-boundary exercise. In Radarr, inspect each candidate's rejection reasons and use the documentation for the installed release. |
| A live download completes but remains in the activity queue without importing. | Radarr cannot associate the client item, cannot access the reported path, lacks suitable permissions, or cannot identify an eligible movie file. | Check the download-client category and history, inspect the path reported to Radarr, verify that Radarr can traverse and read the source, and review the queue warning without manually forcing an uncertain match. |
| A hardlink is expected, but storage usage indicates that a copy was created. | The download and library paths are on different filesystems, or the application cannot create a hardlink with its current access. | Compare the underlying filesystem or mount for both paths and align the storage layout and service permissions. Do not assume that similar-looking container paths refer to the same filesystem. |
| Manual import proposes the wrong movie. | The filename lacks a reliable title, year, or edition marker, or the selected directory contains media from multiple movies. | Stop before approval, select the correct movie explicitly, verify the year and edition, and process unrelated files separately. |

## Security considerations

Treat Radarr API keys, indexer credentials, and download-client credentials as secrets. Do not place them in lesson notes, screenshots, shell history, or shared configuration examples.
Give Radarr only the filesystem access required for its download and library paths. Align service accounts and groups instead of granting unrestricted access.
Do not import an ambiguous file merely to clear an activity warning. A wrong match can mislabel content and replace a correct library item.
Review release names and source trust before acquisition. Automation does not establish that an uploaded file is safe or authentic.
Keep the download client's Radarr category distinct from unrelated downloads so Completed Download Handling does not inspect unintended items.
Use consistent container paths where practical. Incorrect path mappings can expose unintended directories or make troubleshooting unnecessarily complex.
Before approving manual imports, verify the title, year, edition, quality, language, destination, and whether the file is the main feature.
The classroom fixtures contain no real credentials, network calls, or production media. Keep all lab modifications inside /opt/lab-classroom/class47/.

## Rollback

### production_impact
None expected. The lab does not change Radarr, an indexer, a download client, or a media library.

### restore_lab_state
Repeat Step 1 to overwrite the sandbox fixtures with the original classroom values.

### partial_change_recovery
If an experiment is interrupted, validate each JSON file with python3 -m json.tool and then repeat Step 1 before rerunning evaluate.py.

### cleanup_guidance
After instructor verification, the classroom directory may be removed using the institution's approved workspace-cleanup procedure. Confirm that the target is exactly /opt/lab-classroom/class47/ before authorizing deletion.

## Video narration notes

Begin by showing the pipeline from a Radarr movie entry to an organized library file. Emphasize that a quality profile is a decision policy rather than a search engine or downloader. Open a representative profile and identify allowed qualities, their order, upgrade permission, the cutoff, and custom-format score requirements. Next, contrast quality definitions with profiles: definitions govern acceptable size ranges for a named quality, while profiles govern which qualities and preferences apply to a movie. Demonstrate an interactive-search result conceptually and point out that rejection explanations are more useful than guessing from a release name. Explain that automatic search can choose a candidate, while interactive search allows an operator to inspect and select. Then distinguish both from periodic indexer-feed processing, which evaluates newly announced releases rather than searching all history. Move to the download stage and show how Radarr submits an accepted release to a configured client using a category. After completion, explain that Completed Download Handling must associate the client item with a movie and access the reported path. Use a container path example to show how the same host directory can appear under different internal paths and why consistent mounts are preferable. Discuss hardlinks, copies, and moves, noting that hardlinks require one filesystem. Finally, run the isolated class evaluator, read each rejection reason, raise the minimum score, and rerun it. Close with the manual-import examples: approve only the clearly matched main feature, review the ambiguous year and unknown quality, and reject or separately manage the sample. Reinforce the troubleshooting order: movie state, profile, search rejection, client association, path visibility, permissions, and import mapping.

## References

- Radarr project site — https://radarr.video/
- Radarr source repository — https://github.com/Radarr/Radarr
- Servarr Wiki: Radarr — https://wiki.servarr.com/radarr
- Servarr Wiki: Radarr Settings — https://wiki.servarr.com/radarr/settings
- Servarr Wiki: Radarr Library — https://wiki.servarr.com/radarr/library
- Servarr Wiki: Radarr FAQ — https://wiki.servarr.com/radarr/faq
- Servarr Wiki: Docker Guide — https://wiki.servarr.com/docker-guide

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

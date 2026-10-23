# Class 50: Download Categories, Paths, and ARR Integration

**Learning objective:** Explain how an ARR application assigns a download category when submitting a job to a download client.; Distinguish a download directory from an ARR library root folder.; Design paths that are consistently visible to the downloader and ARR application.; Explain why remote path mappings translate paths but do not move files.; Identify when remote path mapping is necessary and when it masks a poor container mount design.; Verify whether a source file and imported library file are hardlinks by comparing device and inode values.; Recognize common category, permission, mount, and completed-download-handling failures.
**Bloom level:** Understand / Apply
**Track:** Media Automation · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach learners how download-client categories, completed-download paths, library root folders, and Sonarr or Radarr import behavior fit together. The lesson emphasizes predictable path design, same-filesystem hardlinking, and the limited circumstances in which remote path mappings are appropriate.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux systems with a POSIX-style filesystem
Linux containers when /opt/lab-classroom/class50/ is writable

### required_tools
POSIX-compatible shell
mkdir
printf
python3
ln
stat
find
mv

### filesystem_requirements
The hardlink demonstration requires the source and destination paths beneath the lab tree to reside on the same filesystem and requires hardlink support.

### arr_scope
Sonarr v4 concepts
Radarr v5 concepts

### download_client_scope
The category and path concepts apply broadly to clients such as qBittorrent, Deluge, Transmission, SABnzbd, and NZBGet, although field names and category behavior differ by client.

### limitations
This is a configuration simulation. It does not contact a real downloader, indexer, Sonarr instance, or Radarr instance.

## Learning objective

- Explain how an ARR application assigns a download category when submitting a job to a download client.
- Distinguish a download directory from an ARR library root folder.
- Design paths that are consistently visible to the downloader and ARR application.
- Explain why remote path mappings translate paths but do not move files.
- Identify when remote path mapping is necessary and when it masks a poor container mount design.
- Verify whether a source file and imported library file are hardlinks by comparing device and inode values.
- Recognize common category, permission, mount, and completed-download-handling failures.

## Why this matters

Teach learners how download-client categories, completed-download paths, library root folders, and Sonarr or Radarr import behavior fit together. The lesson emphasizes predictable path design, same-filesystem hardlinking, and the limited circumstances in which remote path mappings are appropriate.

## Prerequisites

- Basic familiarity with Sonarr or Radarr terminology.
- Basic command-line navigation and file inspection skills.
- An understanding of files, directories, mounts, and absolute paths.
- Permission to create files beneath /opt/lab-classroom/class50/.
- No running download client or ARR application is required because the lab uses isolated mock configuration files.

## Required reading

- Sonarr Wiki: Download Clients — https://wiki.servarr.com/sonarr/settings#download-clients
- Radarr Wiki: Download Clients — https://wiki.servarr.com/radarr/settings#download-clients
- Sonarr Wiki: Docker Guide — https://wiki.servarr.com/docker-guide
- TRaSH Guides: Hardlinks and Instant Moves — https://trash-guides.info/File-and-Folder-Structure/Hardlinks-and-Instant-Moves/

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| ARR application | A media automation application such as Sonarr or Radarr that searches for releases, sends jobs to a downloader, monitors completion, and imports completed files. |
| Category | A downloader-side label, such as tv or movies, supplied by an ARR application to identify and often route its jobs. |
| Download directory | A working or completed-data location managed by the download client. It is not the final media library. |
| Library root folder | A destination managed by an ARR application where organized series or movie directories are created. |
| Completed Download Handling | ARR behavior that monitors completed jobs, validates their files, and imports suitable media into the configured library. |
| Import | The operation by which an ARR application places a completed media file into the library using a copy, move, or hardlink as appropriate. |
| Hardlink | A second directory entry referencing the same file data on the same filesystem. Both names have the same device and inode values. |
| Bind mount | A host directory exposed at another path, commonly used to present selected host storage to a container. |
| Path namespace | The set of path names visible from a particular host, container, virtual machine, or application. |
| Remote path mapping | An ARR rule that translates a path reported by a specific download-client host into the equivalent path visible to ARR. |
| Atomic move | A same-filesystem rename operation that updates directory metadata without copying all file data. |
| Seeding | Continuing to make torrent data available after download completion, which normally requires the original download path to remain intact. |

## Instruction

An ARR workflow has two distinct storage responsibilities. The download client owns the download area, while Sonarr or Radarr owns the organized library. For example, a downloader may place a Sonarr job under /data/downloads/complete/tv, and Sonarr may import its episode into /data/media/tv/Series Name/Season 01. These locations should not be the same directory. If the library is used as the download destination, partial files, release names, unwanted extras, and unmanaged content can leak into the library.

A category is coordination metadata. Sonarr can submit a job with the category tv, while Radarr can submit one with movies. The downloader may use those categories to select completed paths, and each ARR application uses its configured category to recognize jobs that belong to it. Category spelling and case must agree between the applications. A category does not itself grant filesystem access, create a container mount, or teach ARR where a path exists.

When a download completes, the client reports both status and a path. ARR must be able to access that reported path in its own path namespace. On a native installation, both programs might see /data/downloads/complete/tv. In a well-designed container deployment, the host can expose a common parent such as /data to both containers at the same internal path. Sonarr then sees /data/downloads and /data/media exactly as the downloader does. This arrangement is easier to reason about and allows ARR to recognize that the download and library are on the same filesystem.

A remote path mapping is needed only when the download client reports a path that is valid for the client but not valid for ARR. A mapping is selected by the configured download-client host and replaces a remote path prefix with a local path prefix. For example, a client may report /downloads/complete/tv while Sonarr sees the same underlying directory as /data/downloads/complete/tv. The mapping translates the name; it does not mount storage, copy data, change ownership, or repair permissions. If both applications can be given a consistent path layout, that is generally preferable to adding mappings.

Hardlinks provide an efficient import method for torrents that must continue seeding. The original download name and the organized library name can reference the same underlying data. Hardlinks require the source and destination to be on the same filesystem. A path layout that places downloads and media beneath one shared storage root helps preserve this capability. Separate container mounts can make one physical filesystem appear fragmented to applications or can accidentally point to different filesystems. Comparing both the device number and inode number is the reliable basic check for two paths being hardlinks.

Usenet imports often move completed files because they do not need to remain available for seeding. Torrent imports commonly retain the source and create a hardlink when possible. If hardlinking is unavailable, an import can become a full copy, consuming additional space until the torrent is removed. ARR logs should be consulted to distinguish a successful hardlink, a copy fallback, a path-not-found error, and a permission failure.

The central troubleshooting sequence is therefore: confirm the job has the expected category; inspect the exact completed path reported by the client; verify that ARR can see that same data; confirm ARR can read the download and write to the library; check that source and destination are on the same filesystem if hardlinks are expected; and add a remote path mapping only when there is a genuine path-namespace mismatch. This sequence avoids random permission changes and unnecessary mappings.

## Architecture

### components
Sonarr submits television jobs with the tv category.
Radarr submits movie jobs with the movies category.
The download client stores completed jobs in category-specific directories.
ARR Completed Download Handling reads the completed path and imports media into a separate library root.
A shared storage parent keeps downloads and libraries in one coherent filesystem layout.

### recommended_layout
/data/downloads/incomplete
/data/downloads/complete/tv
/data/downloads/complete/movies
/data/media/tv
/data/media/movies

### flow
ARR search or RSS decision -> job submitted with category -> downloader writes data -> downloader reports completion and path -> ARR resolves the path in its namespace -> ARR validates and imports the media -> downloader retains or removes its source according to protocol and client policy.

### path_mapping_rule
Use no mapping when the client and ARR report and consume the same path. Use a host-specific remote path mapping only when different path strings identify the same underlying storage.

### separation_rule
Download directories are staging areas controlled by the downloader. Library root folders are organized destinations controlled by Sonarr or Radarr.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Design a path matrix for Sonarr, Radarr, one torrent client, and one Usenet client. Include each application's visible download and library paths.
Mark which paths refer to the same underlying host storage and identify any namespace mismatch.
Choose categories for television and movies, and document exact spelling and case.
State whether remote path mappings are needed. Justify every proposed mapping using a remote prefix and a local prefix.
Describe how your design supports torrent seeding without duplicating file data.
Write a six-step troubleshooting checklist beginning with category verification and ending with application log review.
Do not modify any path outside /opt/lab-classroom/class50/ while testing homework examples.

## Feynman teach-back

### prompt
Explain the workflow to someone who understands folders but has never used Sonarr, Radarr, or a download client.

### model_explanation
Sonarr asks a downloader to fetch an episode and attaches the label tv. The downloader uses that label to store the finished data in its tv download folder. When the job finishes, Sonarr reads the path reported by the downloader. Sonarr must be able to see that same file. It then gives the episode an organized library name and places it under the show's library folder. If both locations are on the same filesystem, Sonarr may create a hardlink so the download name and library name share one set of data while the torrent continues seeding. A remote path mapping is only a translation rule for cases where the downloader and Sonarr use different names for the same storage. It does not move the file or make an unavailable directory accessible.

### self_check
Can you explain why tv is metadata rather than a permission?
Can you explain why the download directory should not be the library root?
Can you explain why a remote path mapping cannot repair a missing mount?
Can you explain how matching device and inode values demonstrate a hardlink?

## Retrieval check

1. 1. What purpose does a download category serve in an ARR workflow?
2. 2. Why should a downloader's completed directory not be the same directory as an ARR library root?
3. 3. What does a remote path mapping do, and what does it not do?
4. 4. Under what condition can two pathnames be hardlinks to the same file data?
5. 5. What two stat values should match when verifying that two pathnames are hardlinks?
6. 6. Why is a common storage parent useful in containerized ARR deployments?
7. 7. Sonarr expects category tv, but the download client receives jobs under TV. What is the likely problem?
8. 8. A downloader reports /downloads/complete/tv, while Sonarr sees the same storage at /data/downloads/complete/tv. What are the two preferred remedies?
9. 9. Why might a torrent import use additional allocated storage even when the import succeeds?
10. 10. Does a remote path mapping grant Sonarr permission to read a completed file?

## Guided lab

### scope
This simulation creates mock downloader and ARR configuration files, a sample completed download, and a hardlinked library import. Every created or modified object remains beneath /opt/lab-classroom/class50/.

### steps
### step
1

### title
Create the isolated classroom layout

### command
mkdir -p /opt/lab-classroom/class50/active/config /opt/lab-classroom/class50/active/data/downloads/incomplete /opt/lab-classroom/class50/active/data/downloads/complete/tv /opt/lab-classroom/class50/active/data/downloads/complete/movies /opt/lab-classroom/class50/active/data/media/tv/DemoSeries/Season-01 /opt/lab-classroom/class50/active/data/media/movies

### explanation
The active directory acts as the complete lab environment. Downloads and media share the active/data parent while remaining operationally separate.
### step
2

### title
Create a mock download-client configuration

### command
printf '%s\n' '{' '  "name": "mock-downloader",' '  "default_incomplete_path": "/opt/lab-classroom/class50/active/data/downloads/incomplete",' '  "categories": {' '    "tv": "/opt/lab-classroom/class50/active/data/downloads/complete/tv",' '    "movies": "/opt/lab-classroom/class50/active/data/downloads/complete/movies"' '  }' '}' > /opt/lab-classroom/class50/active/config/downloader.json

### explanation
The tv and movies categories route completed data to distinct staging directories.
### step
3

### title
Create a mock Sonarr integration configuration

### command
printf '%s\n' '{' '  "application": "Sonarr",' '  "download_client_host": "mock-downloader",' '  "category": "tv",' '  "completed_download_handling": true,' '  "reported_download_path": "/opt/lab-classroom/class50/active/data/downloads/complete/tv",' '  "library_root": "/opt/lab-classroom/class50/active/data/media/tv",' '  "remote_path_mappings": []' '}' > /opt/lab-classroom/class50/active/config/sonarr.json

### explanation
No remote path mapping is present because the mock downloader and Sonarr configuration use the same absolute path.
### step
4

### title
Validate category and path separation

### command
python3 - <<'PY'
import json
from pathlib import Path
base = Path('/opt/lab-classroom/class50/active/config')
downloader = json.loads((base / 'downloader.json').read_text())
sonarr = json.loads((base / 'sonarr.json').read_text())
category = sonarr['category']
reported = sonarr['reported_download_path']
library = sonarr['library_root']
assert category in downloader['categories'], 'ARR category is absent from downloader configuration'
assert downloader['categories'][category] == reported, 'Category path and reported path disagree'
assert reported != library, 'Download path and library root must be separate'
assert sonarr['completed_download_handling'] is True, 'Completed Download Handling is disabled'
assert sonarr['remote_path_mappings'] == [], 'A mapping is unnecessary in this shared namespace'
print('Category match: PASS')
print('Shared path namespace: PASS')
print('Download/library separation: PASS')
print('Unnecessary mapping absent: PASS')
PY

### explanation
The validator checks the relationships among the category, completed path, library root, and mapping list.
### step
5

### title
Create a simulated completed download

### command
printf '%s\n' 'Class 50 simulated media payload' > /opt/lab-classroom/class50/active/data/downloads/complete/tv/DemoSeries.S01E01.mkv

### explanation
The file is harmless text with a media-style filename. It represents a completed downloader payload.
### step
6

### title
Simulate a hardlink import

### command
ln /opt/lab-classroom/class50/active/data/downloads/complete/tv/DemoSeries.S01E01.mkv /opt/lab-classroom/class50/active/data/media/tv/DemoSeries/Season-01/DemoSeries-S01E01.mkv

### explanation
The library receives an organized name while the downloader path remains available. The two names reference one underlying file.
### step
7

### title
Verify the import relationship

### command
stat -c '%d:%i %h %n' /opt/lab-classroom/class50/active/data/downloads/complete/tv/DemoSeries.S01E01.mkv /opt/lab-classroom/class50/active/data/media/tv/DemoSeries/Season-01/DemoSeries-S01E01.mkv

### explanation
Matching device and inode values prove that the entries are hardlinks. A link count of two confirms that two names reference the file.
### step
8

### title
Inspect the completed classroom tree

### command
find /opt/lab-classroom/class50/active -maxdepth 8 -print

### explanation
The output should show separate configuration, download, and library locations under the single permitted lab root.

## Expected results

- The downloader configuration contains separate tv and movies categories.
- The Sonarr category is tv and matches a category defined by the downloader.
- The mock completed-download path differs from the Sonarr library root.
- The validator prints four PASS lines and exits without an assertion error.
- The simulated source file remains in the completed tv directory.
- The organized library filename appears beneath data/media/tv/DemoSeries/Season-01.
- The source and library entries have matching device and inode values and each reports a link count of two.
- No remote path mapping is configured because both mock applications use the same path namespace.

## Verification checkpoints

- [ ] Run: python3 -m json.tool /opt/lab-classroom/class50/active/config/downloader.json
- [ ] Run: python3 -m json.tool /opt/lab-classroom/class50/active/config/sonarr.json
- [ ] Run: find /opt/lab-classroom/class50/active/data/downloads/complete -type f -print
- [ ] Run: find /opt/lab-classroom/class50/active/data/media -type f -print
- [ ] Run: stat -c '%d:%i %h %n' /opt/lab-classroom/class50/active/data/downloads/complete/tv/DemoSeries.S01E01.mkv /opt/lab-classroom/class50/active/data/media/tv/DemoSeries/Season-01/DemoSeries-S01E01.mkv
- [ ] Confirm that both stat records begin with the same device and inode pair.
- [ ] Confirm that the download source and library destination are separate pathnames.
- [ ] Confirm that every lab artifact is beneath /opt/lab-classroom/class50/.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The validator reports that the ARR category is absent from the downloader configuration. | The category configured in Sonarr does not exactly match a downloader category. | Make category spelling and case consistent. For this lab, both configurations must use tv. |
| The validator reports that the category path and reported path disagree. | The downloader routes the category to one directory while the mock ARR configuration expects another. | Set the reported path to the exact category destination or correct the downloader category destination. |
| The hardlink command reports that the destination already exists. | The import step was run more than once in the same active lab directory. | Use the rollback procedure to archive the active directory, then rerun the lab from step 1. |
| The hardlink command reports an invalid cross-device link. | The source and destination resolve to different filesystems. | Place downloads and media on one filesystem when hardlinks are required, or accept a copy-based import. In the prescribed lab layout, both locations should be under the same active/data tree. |
| A real ARR application reports that the completed path does not exist. | ARR cannot see the path reported by the download client, often because container mounts or path namespaces differ. | First align the storage mounts and internal paths. If the different path names are intentional and point to the same storage, add a host-specific remote path mapping. |
| ARR can see a completed file but cannot import it. | The ARR service identity lacks read access to the download or write access to the library. | Align service users and groups, directory ownership, and inherited permissions according to the platform. Avoid granting unrestricted access as a shortcut. |
| A torrent import consumes approximately another file's worth of allocated storage. | ARR copied the file instead of creating a hardlink, often because the locations are on different filesystems or are exposed as unrelated mounts. | Check ARR logs, compare filesystem device identifiers, and redesign mounts so downloads and media share a common storage parent if hardlinking is desired. |
| Files appear directly in the final library before ARR imports them. | The downloader's category destination was incorrectly set to the ARR library root. | Restore a dedicated download staging directory and keep the library root exclusively under ARR management. |
| The configuration file cannot be parsed as JSON. | A command was copied incompletely or the file was manually edited with invalid punctuation. | Archive the active lab using the rollback procedure and recreate the configuration from the documented steps. |

## Security considerations

Grant the downloader write access only to its download workspace and any directories specifically required by its operation.
Grant Sonarr or Radarr read access to completed downloads and write access to their intended library roots.
Use a shared service group or equivalent access-control design instead of broad world-writable permissions.
Do not expose downloader or ARR administrative interfaces directly to untrusted networks.
Store downloader credentials and API keys in protected application secrets rather than lesson files or public configuration repositories.
Treat downloaded content as untrusted input. ARR import automation does not establish that a file is safe.
Keep download staging directories separate from media libraries so incomplete and unmanaged files are not served accidentally.
A remote path mapping is not an access-control feature and cannot compensate for missing mounts or insufficient permissions.
Review service logs for paths and filenames that may reveal private library information before sharing diagnostics.

## Rollback

### goal
Deactivate the lab without deleting its evidence and without changing anything outside the permitted class directory.

### commands
mkdir -p /opt/lab-classroom/class50/rollback-state
mv /opt/lab-classroom/class50/active /opt/lab-classroom/class50/rollback-state/active-class50

### result
The active lab path is removed from service by moving it into a retained rollback-state directory. All artifacts remain available for review beneath /opt/lab-classroom/class50/.

### rerun_note
After rollback, step 1 can create a new active directory. If active-class50 already exists in rollback-state, rename that retained directory to another unique name within /opt/lab-classroom/class50/ before repeating the rollback.

## Video narration notes

Welcome to Class 50: Download Categories, Paths, and ARR Integration. In this lesson, we are separating four ideas that are often incorrectly treated as one setting: categories, download paths, library roots, and remote path mappings.

Start with the category. Sonarr might submit a job as tv, while Radarr submits a job as movies. The downloader can use those labels to route completed jobs into different directories. The label also helps each ARR application recognize the jobs it owns. The spelling must match exactly, but the category itself does not create a directory mount or grant access.

Next, separate the download workspace from the media library. The downloader owns incomplete and completed download directories. Sonarr and Radarr own organized library roots. A finished release in the download area may have a release-oriented filename, while the imported library file receives a clean series, season, episode, or movie name. Pointing the downloader directly at the library bypasses this important boundary.

When a job completes, the downloader reports a path. Sonarr or Radarr must be able to open that path. The cleanest design presents shared storage with the same path inside both applications. If the downloader sees /data/downloads, Sonarr should ideally see /data/downloads too. Downloads and media can then live under one common storage parent while remaining in separate subdirectories.

Remote path mappings are exception-handling rules. If the downloader reports /downloads but Sonarr sees the same underlying storage as /data/downloads, Sonarr can translate one prefix to the other. The mapping does not copy data, mount a directory, or repair access controls. If Sonarr cannot see the storage at all, a mapping cannot solve the problem.

The lab creates an isolated model beneath the class directory. We define tv and movies categories, configure a mock Sonarr instance for tv, validate that the paths agree, create a sample completed file, and import it under an organized library name using a hardlink. The final stat command displays each entry's device, inode, and link count. Matching device and inode values show that both names reference the same data.

Remember the troubleshooting order: verify the category, inspect the exact reported path, verify that ARR sees the data, check read and write access, confirm filesystem boundaries, and only then consider a remote path mapping. A disciplined path model is easier to secure, troubleshoot, migrate, and back up than a collection of one-off fixes.

## References

- Servarr Wiki, Sonarr Settings: https://wiki.servarr.com/sonarr/settings
- Servarr Wiki, Radarr Settings: https://wiki.servarr.com/radarr/settings
- Servarr Wiki, Docker Guide: https://wiki.servarr.com/docker-guide
- TRaSH Guides, Hardlinks and Instant Moves: https://trash-guides.info/File-and-Folder-Structure/Hardlinks-and-Instant-Moves/
- Docker Documentation, Storage and Volumes: https://docs.docker.com/engine/storage/
- GNU Coreutils Manual, stat invocation: https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html
- Linux man-pages, link(2): https://man7.org/linux/man-pages/man2/link.2.html

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

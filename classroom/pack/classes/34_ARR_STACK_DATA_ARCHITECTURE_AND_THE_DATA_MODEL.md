# Class 34: ARR Stack Data Architecture and the /data Model

**Learning objective:** Explain why download and media paths should share one visible /data namespace.; Design separate locations for torrent, Usenet, and organized media data without creating incompatible container paths.; Distinguish application configuration data from bulk media and download data.; Explain the requirements for hardlinks and atomic moves.; Map Sonarr, Radarr, a download client, and a media server to consistent paths.; Use inode, link-count, device, and canonical-path checks to verify storage behavior.; Identify permission, ownership, mount-boundary, category, and remote-path errors.; Document a storage contract before deploying an ARR stack.
**Bloom level:** Understand / Apply
**Track:** Media Automation and Storage · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach a predictable storage architecture for Sonarr, Radarr, download clients, and media servers by exposing one shared /data hierarchy. The lesson emphasizes consistent container paths, category separation, same-filesystem imports, atomic moves, hardlinks, identity alignment, and verification before deployment.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux hosts with a POSIX-style filesystem and GNU coreutils
Container hosts running Docker Engine or a compatible bind-mount implementation

### filesystems
The hardlink exercise requires a filesystem that supports hardlinks. Source and destination must reside on the same filesystem device. Network and pooled storage implementations may impose additional semantics that must be verified with the storage vendor's documentation.

### container_images
The architecture is image-agnostic, but environment variable names for UID, GID, and umask differ between image publishers.

### shell
Commands are written for a Bourne-compatible shell with GNU stat and GNU find.

### limitations
The lab validates filesystem concepts with synthetic files. It does not deploy Sonarr, Radarr, a media server, or a download client, and it does not measure storage performance.

## Learning objective

- Explain why download and media paths should share one visible /data namespace.
- Design separate locations for torrent, Usenet, and organized media data without creating incompatible container paths.
- Distinguish application configuration data from bulk media and download data.
- Explain the requirements for hardlinks and atomic moves.
- Map Sonarr, Radarr, a download client, and a media server to consistent paths.
- Use inode, link-count, device, and canonical-path checks to verify storage behavior.
- Identify permission, ownership, mount-boundary, category, and remote-path errors.
- Document a storage contract before deploying an ARR stack.

## Why this matters

Teach a predictable storage architecture for Sonarr, Radarr, download clients, and media servers by exposing one shared /data hierarchy. The lesson emphasizes consistent container paths, category separation, same-filesystem imports, atomic moves, hardlinks, identity alignment, and verification before deployment.

## Prerequisites

- Basic Linux shell navigation and file inspection skills
- A conceptual understanding of containers, bind mounts, and persistent application configuration
- Familiarity with Sonarr or Radarr terminology such as root folder, download client, category, and import
- Permission to create files and directories under /opt/lab-classroom/class34/
- GNU coreutils commands including stat, find, mkdir, ln, mv, printf, and readlink

## Required reading

- Docker documentation, Bind mounts: https://docs.docker.com/engine/storage/bind-mounts/
- Sonarr Wiki, Docker Guide: https://wiki.servarr.com/docker-guide
- Radarr Wiki, Docker Guide: https://wiki.servarr.com/docker-guide
- TRaSH Guides, Hardlinks and Instant Moves: https://trash-guides.info/File-and-Folder-Structure/Hardlinks-and-Instant-Moves/
- GNU Coreutils manual, stat invocation: https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| ARR stack | An informal name for media automation applications such as Sonarr and Radarr, often used with download clients and media servers. |
| Data root | The shared top-level path, /data in this model, beneath which downloads and organized media are placed. |
| Application configuration | Databases, settings, logs, and state belonging to an application. These files are persistent but should remain separate from bulk media data. |
| Root folder | A Sonarr or Radarr destination containing an organized media library, such as /data/media/tv or /data/media/movies. |
| Download category | A download-client label or category used to route jobs into an application-specific location, such as movies or tv. |
| Hardlink | An additional directory entry that references the same inode and file data as another name on the same filesystem. |
| Atomic move | A same-filesystem rename operation that changes directory entries without copying the file contents. |
| Filesystem device | The storage filesystem identified by a device number. Hardlinks cannot cross from one filesystem device to another. |
| Container path contract | The agreed internal paths that every participating container uses to describe the same files. |
| Remote path mapping | A Sonarr or Radarr translation used when a remote download client reports a path that is genuinely different from the path visible to the automation application. |
| PUID and PGID | Common container-image environment variables used to select the host user and group identity under which an application writes files. |
| UMASK | A process setting that removes permission bits from newly created files and directories. |

## Instruction

The central design rule is that applications participating in an import should describe shared files with one consistent namespace. In the /data model, download clients write beneath /data/torrents or /data/usenet, while Sonarr and Radarr organize completed media beneath /data/media. A typical layout is /data/torrents/tv, /data/torrents/movies, /data/usenet/complete/tv, /data/usenet/complete/movies, /data/media/tv, and /data/media/movies. The application configuration directories are not placed inside this tree; each service instead receives a separate configuration location because databases and settings have different backup, access, and lifecycle requirements from large media files.

Consistency is more important than inventing a unique path for every container. If a download client reports /data/torrents/tv/Episode.mkv, Sonarr should be able to inspect that exact path. Mounting the host download directory as /downloads in one container and as /data/torrents in another creates a translation problem. It also encourages separate container mount points that can prevent efficient imports. A unified /data bind mount gives the participating applications a shared view. The applications may receive read-only or narrower access where their role permits it, but an importer must be able to read the completed download and write into its library destination.

Hardlinks are especially useful for torrents. A torrent client must retain its original path while seeding, but the media server expects a clean library path and filename. A hardlink allows both names to reference one inode, so deleting one name does not remove the data while another link remains. Hardlinks require source and destination to be on the same filesystem and cannot be created across filesystem boundaries. They also require suitable permissions on the source and destination directories. The inode number and device number reported by stat can prove whether two paths are hardlinks. A link count of two or greater shows that the inode has multiple names.

Atomic moves provide another benefit of a unified filesystem. When an application renames a completed file within one filesystem, the operation can update directory metadata rather than copying the file and then deleting the original. If source and destination are on different filesystems, the workflow becomes a copy followed by deletion and is no longer an atomic rename. Usenet workflows commonly move completed files because continued seeding is not required, while torrent workflows commonly preserve the download and create a hardlink into the library.

Path design does not replace identity and permission design. Sonarr, Radarr, and download clients should use compatible user and group identities, and shared directories should be group-writable where collaboration is required. Broad access is not a substitute for understanding ownership. Categories must also agree: a Sonarr category such as tv should correspond to the download client's /data/torrents/tv or /data/usenet/complete/tv location, while Radarr should use movies. Remote path mappings should be reserved for genuinely remote or legacy path differences; they should not be used to conceal a poor local container mount design. Before deployment, document the host path, container path, writer, reader, ownership expectation, backup policy, and deletion authority for every directory.

## Architecture

### design_principles
Expose one shared /data namespace to applications that exchange download and media paths.
Keep application configuration outside the bulk /data hierarchy.
Keep downloads and organized libraries as sibling branches of the same data root.
Place hardlink source and destination on the same filesystem.
Use categories to separate television, movie, and music workflows.
Assign deletion authority deliberately; a media server generally does not need to modify downloads.
Use matching service identities or a deliberate shared-group policy.

### canonical_tree
/data/torrents/tv
/data/torrents/movies
/data/torrents/music
/data/usenet/incomplete
/data/usenet/complete/tv
/data/usenet/complete/movies
/data/usenet/complete/music
/data/media/tv
/data/media/movies
/data/media/music

### service_path_contract
### sonarr
### shared_data_path
/data

### root_folder
/data/media/tv

### torrent_category
tv

### expected_torrent_path
/data/torrents/tv

### expected_usenet_path
/data/usenet/complete/tv

### radarr
### shared_data_path
/data

### root_folder
/data/media/movies

### torrent_category
movies

### expected_torrent_path
/data/torrents/movies

### expected_usenet_path
/data/usenet/complete/movies

### torrent_client
### shared_data_path
/data

### tv_destination
/data/torrents/tv

### movie_destination
/data/torrents/movies

### retention_reason
Original download names and locations remain available for seeding.

### usenet_client
### shared_data_path
/data

### incomplete_destination
/data/usenet/incomplete

### tv_destination
/data/usenet/complete/tv

### movie_destination
/data/usenet/complete/movies

### media_server
### library_paths
/data/media/tv
/data/media/movies
/data/media/music

### recommended_access
Read-only access is preferred unless the server must intentionally write metadata, subtitles, or optimized versions beside media.

### host_mapping_example
### host_bulk_data
/srv/storage/data

### container_bulk_data
/data

### sonarr_config
/srv/appdata/sonarr

### radarr_config
/srv/appdata/radarr

### principle
The host locations are examples for architecture discussion only. This class lab does not create or modify them.

### data_flow
A download request is sent to a client with the tv or movies category.
The client writes beneath the corresponding /data download branch.
The automation application receives the completed path using the same /data namespace.
The automation application validates, renames, and imports the file into its /data/media root folder.
A torrent import may retain the source name through a hardlink; a Usenet import may use a same-filesystem move.
The media server scans the organized library branch rather than the download branch.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Draw a proposed /data tree for television, movies, and music, including both torrent and Usenet workflows.
Create a service matrix listing the host path, container path, access mode, UID, GID, category, and deletion authority for Sonarr, Radarr, the download clients, and the media server.
For an existing nonproduction stack, record the device number of each download and library directory using stat without changing any files.
Identify every remote path mapping in the existing design and justify whether it represents a genuinely remote path or masks inconsistent local mounts.
Write a backup policy that separates application configuration, active downloads, and organized media.

## Feynman teach-back

### prompt
Explain the /data model to a new administrator without using the words efficient, Docker, or magic.

### model_explanation
The downloader and media organizer must agree on where a file lives. Both are given one shared cabinet called /data. Incoming torrent files go in one drawer, completed Usenet files go in another, and neatly named library files go in a media drawer. Because the drawers are in the same cabinet, the organizer can rename a file quickly or give the same stored file a second name. A torrent can therefore keep its original seeding name while the media library uses a clean title. Configuration files stay in a different cabinet because they contain application state and require a separate backup and security policy.

### self_check_questions
Can you explain why /downloads in one application and /data/torrents in another creates operational complexity?
Can you explain why matching filenames do not prove that two files are hardlinks?
Can you state the two core requirements for a hardlink: the same filesystem and sufficient access?
Can you explain why application configuration and media data have different backup requirements?

## Retrieval check

1. 1. Why should Sonarr, Radarr, and download clients use the same /data path for shared files?
2. 2. What two filesystem values should match when proving that two names are hardlinks to the same file?
3. 3. Why are hardlinks commonly useful for torrent imports?
4. 4. What happens when a move must cross a filesystem boundary?
5. 5. Where should a Radarr movie root folder be placed in the canonical model?
6. 6. Why should application configuration remain separate from /data/media and /data/torrents?
7. 7. When is a remote path mapping appropriate?
8. 8. What is wrong with pointing a media-server library at the entire /data directory?

## Guided lab

### scope
All lab-created directories and files remain under /opt/lab-classroom/class34/. The exercise models the production /data hierarchy without touching a real media library or container deployment.

### steps
### step
1

### name
Create the isolated model

### commands
mkdir -p /opt/lab-classroom/class34/data/torrents/tv
mkdir -p /opt/lab-classroom/class34/data/torrents/movies
mkdir -p /opt/lab-classroom/class34/data/usenet/incomplete
mkdir -p /opt/lab-classroom/class34/data/usenet/complete/tv
mkdir -p /opt/lab-classroom/class34/data/usenet/complete/movies
mkdir -p /opt/lab-classroom/class34/data/media/tv
mkdir -p /opt/lab-classroom/class34/data/media/movies
mkdir -p /opt/lab-classroom/class34/config/sonarr
mkdir -p /opt/lab-classroom/class34/config/radarr

### explanation
The model separates application configuration from bulk data while keeping downloads and libraries beneath one data root.
### step
2

### name
Record the path contract

### commands
printf '%s\n' 'sonarr_root=/data/media/tv' 'radarr_root=/data/media/movies' 'torrent_tv=/data/torrents/tv' 'torrent_movies=/data/torrents/movies' 'usenet_tv=/data/usenet/complete/tv' 'usenet_movies=/data/usenet/complete/movies' > /opt/lab-classroom/class34/path-contract.txt
cat /opt/lab-classroom/class34/path-contract.txt

### explanation
The contract records paths as applications should see them, independent of the lab's host-side prefix.
### step
3

### name
Create a simulated completed torrent

### commands
printf '%s\n' 'Class 34 synthetic media payload' > /opt/lab-classroom/class34/data/torrents/movies/example-release.mkv
stat -c 'device=%d inode=%i links=%h size=%s path=%n' /opt/lab-classroom/class34/data/torrents/movies/example-release.mkv

### explanation
This small text payload represents a completed media file. It is not actual media and no performance conclusion should be drawn from it.
### step
4

### name
Simulate a Radarr hardlink import

### commands
ln /opt/lab-classroom/class34/data/torrents/movies/example-release.mkv '/opt/lab-classroom/class34/data/media/movies/Example Movie (2024).mkv'
stat -c 'device=%d inode=%i links=%h size=%s path=%n' /opt/lab-classroom/class34/data/torrents/movies/example-release.mkv '/opt/lab-classroom/class34/data/media/movies/Example Movie (2024).mkv'

### explanation
Both names should report the same device and inode, and the link count should become two.
### step
5

### name
Demonstrate that two names reference the same data

### commands
printf '%s\n' 'Metadata appended through library name' >> '/opt/lab-classroom/class34/data/media/movies/Example Movie (2024).mkv'
tail -n 1 /opt/lab-classroom/class34/data/torrents/movies/example-release.mkv
stat -c 'device=%d inode=%i links=%h size=%s path=%n' /opt/lab-classroom/class34/data/torrents/movies/example-release.mkv '/opt/lab-classroom/class34/data/media/movies/Example Movie (2024).mkv'

### explanation
Because both names reference the same inode, content appended through one name is visible through the other.
### step
6

### name
Simulate a same-filesystem Usenet move

### commands
printf '%s\n' 'Class 34 synthetic episode payload' > /opt/lab-classroom/class34/data/usenet/complete/tv/example-episode.mkv
stat -c 'before device=%d inode=%i links=%h path=%n' /opt/lab-classroom/class34/data/usenet/complete/tv/example-episode.mkv
mv /opt/lab-classroom/class34/data/usenet/complete/tv/example-episode.mkv '/opt/lab-classroom/class34/data/media/tv/Example Show - S01E01.mkv'
stat -c 'after device=%d inode=%i links=%h path=%n' '/opt/lab-classroom/class34/data/media/tv/Example Show - S01E01.mkv'

### explanation
Record the before and after inode values. An unchanged device and inode are consistent with a rename inside one filesystem.
### step
7

### name
Inspect the completed model

### commands
find /opt/lab-classroom/class34 -mindepth 1 -printf '%y %p\n' | sort
find /opt/lab-classroom/class34/data -type f -exec stat -c 'device=%d inode=%i links=%h path=%n' {} \;

### explanation
The final inventory should show configuration directories outside the data branch, download branches beside media branches, and matching inode values for the torrent hardlink pair.

## Expected results

- The directory /opt/lab-classroom/class34/data contains separate torrents, usenet, and media branches.
- The directories /opt/lab-classroom/class34/config/sonarr and /opt/lab-classroom/class34/config/radarr exist outside the data branch.
- The path-contract file assigns Sonarr to /data/media/tv and Radarr to /data/media/movies.
- The simulated torrent source and organized movie name have the same device number and inode number.
- The simulated torrent source and organized movie name each report a link count of at least two.
- Text appended through the organized movie name is visible when reading the torrent source name.
- The simulated Usenet episode exists in the media/tv branch after the move and no longer exists under usenet/complete/tv.
- The moved episode retains its inode when the source and destination are on the same filesystem.

## Verification checkpoints

- [ ] Run: test -d /opt/lab-classroom/class34/data/torrents/movies && echo PASS-torrent-directory
- [ ] Run: test -d /opt/lab-classroom/class34/data/media/movies && echo PASS-movie-directory
- [ ] Run: test -d /opt/lab-classroom/class34/config/sonarr && echo PASS-config-separation
- [ ] Run: grep -Fx 'sonarr_root=/data/media/tv' /opt/lab-classroom/class34/path-contract.txt
- [ ] Run: grep -Fx 'radarr_root=/data/media/movies' /opt/lab-classroom/class34/path-contract.txt
- [ ] Run: test /opt/lab-classroom/class34/data/torrents/movies/example-release.mkv -ef '/opt/lab-classroom/class34/data/media/movies/Example Movie (2024).mkv' && echo PASS-hardlink-identity
- [ ] Run: test "$(stat -c %h /opt/lab-classroom/class34/data/torrents/movies/example-release.mkv)" -ge 2 && echo PASS-link-count
- [ ] Run: grep -Fx 'Metadata appended through library name' /opt/lab-classroom/class34/data/torrents/movies/example-release.mkv
- [ ] Run: test ! -e /opt/lab-classroom/class34/data/usenet/complete/tv/example-episode.mkv && echo PASS-source-moved
- [ ] Run: test -f '/opt/lab-classroom/class34/data/media/tv/Example Show - S01E01.mkv' && echo PASS-tv-import

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The ln command reports an invalid cross-device link. | The source and destination resolve to different filesystems or mount points. | Compare device values with stat -c '%d %n' for both parent directories. Redesign the storage so download and media branches share one filesystem and are exposed through one /data mount. |
| The ln command reports that the destination already exists. | The lab was run previously and the organized movie name is already present. | Inspect both paths with stat. If they already have the same device and inode, continue with verification. Otherwise perform the documented rollback and repeat the lab. |
| A command reports permission denied under the class directory. | The current account does not own the lab directory or lacks write and traversal permission. | Ask the lab administrator to assign the class directory to the intended lab identity. Do not broaden permissions indiscriminately. |
| Sonarr or Radarr reports that a downloaded path does not exist. | The download client and automation application use different container paths for the same host data, or the shared data mount is missing. | Inspect each container's mounts and make the same host data visible as /data. Confirm that the path reported by the client is directly visible inside Sonarr or Radarr. |
| Imports work but files are copied instead of hardlinked. | Source and destination are on different filesystems, separate container mount boundaries are being used, hardlink import is disabled, or permissions prevent link creation. | Compare device and inode information, consolidate the data mount, confirm hardlink behavior is enabled in the application, and verify directory ownership and group write access. |
| A movie is sent to the television download directory. | Download categories are missing, duplicated, or mapped to the wrong save path. | Assign distinct tv and movies categories and verify their destination paths in both the automation application and download client. |
| The media server sees downloads or partial files as library items. | The server library points at /data or a download branch instead of an organized media branch. | Configure media-server libraries with specific roots such as /data/media/tv and /data/media/movies. |
| A remote path mapping appears necessary even though all services run on the same container host. | Inconsistent internal bind-mount paths are being treated as a remote-host problem. | Standardize the local container mount as /data first. Use remote path mapping only when a genuinely remote client reports a path that cannot be made identical. |

## Security considerations

### principles
Grant each service only the access required by its role.
Keep application databases and credentials in dedicated configuration locations rather than in the shared media tree.
Use a deliberate shared group for applications that must collaborate on downloads and imports.
Prefer read-only library access for media servers that do not need to write beside media.
Do not expose incomplete downloads to media-server library scans.
Treat download clients as network-facing applications and avoid giving them unnecessary access to application configuration or unrelated host directories.
Protect API keys, download-client credentials, and indexer credentials in secrets or restricted configuration files.
Back up application configuration independently from replaceable download data and large media datasets.

### identity_guidance
Choose one documented UID and GID strategy. Services may run as the same unprivileged identity or as separate users sharing a controlled media group. Verify ownership and effective access from inside each container rather than relying only on host-side names.

### deletion_boundaries
Define which service may delete incomplete downloads, completed downloads, and organized media. A mistaken broad mount combined with broad write access can allow one compromised service to alter the entire library.

### validation
Before enabling automated deletion, test imports with synthetic files and confirm the source-retention behavior for torrents and the move behavior for Usenet.

## Rollback

### scope
Rollback removes only artifacts created inside /opt/lab-classroom/class34/ and does not affect any production path.

### commands
unlink '/opt/lab-classroom/class34/data/media/movies/Example Movie (2024).mkv'
unlink /opt/lab-classroom/class34/data/torrents/movies/example-release.mkv
unlink '/opt/lab-classroom/class34/data/media/tv/Example Show - S01E01.mkv'
unlink /opt/lab-classroom/class34/path-contract.txt
rmdir /opt/lab-classroom/class34/data/torrents/tv
rmdir /opt/lab-classroom/class34/data/torrents/movies
rmdir /opt/lab-classroom/class34/data/torrents
rmdir /opt/lab-classroom/class34/data/usenet/incomplete
rmdir /opt/lab-classroom/class34/data/usenet/complete/tv
rmdir /opt/lab-classroom/class34/data/usenet/complete/movies
rmdir /opt/lab-classroom/class34/data/usenet/complete
rmdir /opt/lab-classroom/class34/data/usenet
rmdir /opt/lab-classroom/class34/data/media/tv
rmdir /opt/lab-classroom/class34/data/media/movies
rmdir /opt/lab-classroom/class34/data/media
rmdir /opt/lab-classroom/class34/data
rmdir /opt/lab-classroom/class34/config/sonarr
rmdir /opt/lab-classroom/class34/config/radarr
rmdir /opt/lab-classroom/class34/config

### verification
Run find /opt/lab-classroom/class34 -mindepth 1 -print. No output means all lesson artifacts were removed while the class directory itself was retained.

### notes
If an unlink command reports that a file does not exist, inspect the path and continue. If an rmdir command reports that a directory is not empty, inspect its contents before removing anything; an unexpected file may not belong to this exercise.

## Video narration notes

Begin with a diagram showing one /data root divided into torrents, Usenet, and media branches. Emphasize that the tree is a contract between applications, not merely a preference for tidy folders. Show Sonarr using /data/media/tv, Radarr using /data/media/movies, and the download client returning paths under the same /data namespace. Next, contrast this with an inconsistent layout where one container reports /downloads and another expects /data/torrents. Explain that path translation may make a file discoverable but does not repair an underlying filesystem or mount-boundary problem. Demonstrate the isolated class tree and create the synthetic torrent payload. After creating the organized movie hardlink, place the two stat results side by side and highlight the matching device, matching inode, and increased link count. Append text through the library name and read it through the torrent name to show that the names refer to one underlying file. Then create the synthetic Usenet payload, record its inode, move it into the television library, and confirm that the inode remains unchanged within the lab filesystem. Close by reviewing identity alignment, category routing, least-privilege mounts, configuration separation, deletion authority, and the rule that production changes should follow a written path contract and a tested rollback plan.

## References

- Docker Docs, Bind mounts: https://docs.docker.com/engine/storage/bind-mounts/
- Docker Docs, Storage overview: https://docs.docker.com/engine/storage/
- Servarr Wiki, Docker Guide: https://wiki.servarr.com/docker-guide
- Sonarr Wiki: https://wiki.servarr.com/sonarr
- Radarr Wiki: https://wiki.servarr.com/radarr
- TRaSH Guides, File and Folder Structure: https://trash-guides.info/File-and-Folder-Structure/
- TRaSH Guides, Hardlinks and Instant Moves: https://trash-guides.info/File-and-Folder-Structure/Hardlinks-and-Instant-Moves/
- GNU Coreutils manual, ln invocation: https://www.gnu.org/software/coreutils/manual/html_node/ln-invocation.html
- GNU Coreutils manual, stat invocation: https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html
- Linux man-pages, link(2): https://man7.org/linux/man-pages/man2/link.2.html
- Linux man-pages, rename(2): https://man7.org/linux/man-pages/man2/rename.2.html

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

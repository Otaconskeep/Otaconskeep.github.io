# Class 58: Jellyfin Installation and Library Design

**Learning objective:** Describe the roles of Jellyfin configuration, cache, metadata, and media storage; Deploy Jellyfin while keeping all lab-authored persistent data under /opt/lab-classroom/class58/; Explain why media should be mounted read-only when Jellyfin does not need to modify source files; Create a predictable directory and file-naming plan for movies, episodic television, music, and home videos; Complete the initial Jellyfin setup wizard and create logically separated libraries; Verify container status, browser access, persistent configuration, and media mount behavior; Identify common causes of startup, permission, port, and media-discovery failures; Explain which data must be backed up and which data can normally be regenerated
**Bloom level:** Understand / Apply
**Track:** Media Services · **Difficulty:** beginner · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Install an isolated Jellyfin server with containerized deployment, understand its configuration and cache boundaries, and design media libraries that support reliable identification, metadata retrieval, permissions, backup, and future growth.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2026-03-17
**Compatibility:** ### target_platform
Linux host with Docker Engine and Docker Compose plugin

### container_image
jellyfin/jellyfin:10.10.7

### cpu_architectures
amd64
arm64 when the declared image is available for the host platform

### network_assumption
The browser runs on the Jellyfin host because the service is bound to 127.0.0.1.

### storage_assumption
The filesystem containing /opt/lab-classroom/class58 supports normal Linux ownership and permissions.

### excluded_features
Hardware-accelerated transcoding
Direct network access from other hosts
Automatic discovery protocols
Production encrypted ingress
External identity providers
Shared storage outside the class58 directory

### upgrade_note
Later Jellyfin versions may change setup screens, image behavior, or configuration details. Back up the config directory, read the release notes, and test an updated image as a separate controlled change.

## Learning objective

- Describe the roles of Jellyfin configuration, cache, metadata, and media storage
- Deploy Jellyfin while keeping all lab-authored persistent data under /opt/lab-classroom/class58/
- Explain why media should be mounted read-only when Jellyfin does not need to modify source files
- Create a predictable directory and file-naming plan for movies, episodic television, music, and home videos
- Complete the initial Jellyfin setup wizard and create logically separated libraries
- Verify container status, browser access, persistent configuration, and media mount behavior
- Identify common causes of startup, permission, port, and media-discovery failures
- Explain which data must be backed up and which data can normally be regenerated

## Why this matters

Install an isolated Jellyfin server with containerized deployment, understand its configuration and cache boundaries, and design media libraries that support reliable identification, metadata retrieval, permissions, backup, and future growth.

## Prerequisites

- A Linux homelab host with Docker Engine and the Docker Compose plugin installed
- Permission to run Docker commands without changing host-wide configuration
- At least 2 GB of available storage for the image, configuration, cache, and lab artifacts
- A web browser running on the Jellyfin host or another approved way to access a loopback-bound web service
- Basic familiarity with Linux paths, containers, ports, and YAML
- Only legally owned or otherwise authorized media may be used in the lab

## Required reading

- Jellyfin documentation home: https://jellyfin.org/docs/
- Jellyfin container installation documentation: https://jellyfin.org/docs/general/installation/container/
- Jellyfin media organization documentation: https://jellyfin.org/docs/general/server/media/movies/
- Jellyfin television organization documentation: https://jellyfin.org/docs/general/server/media/shows/
- Docker Compose file reference: https://docs.docker.com/reference/compose-file/

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Library | A logical Jellyfin collection that maps one or more filesystem paths to a content type such as movies, shows, music, or home videos. |
| Metadata | Descriptive information such as titles, release years, cast, summaries, artwork, episode numbers, and external database identifiers. |
| Direct play | Playback in which the client consumes the stored media without the server changing its container, video stream, or audio stream. |
| Remux | Playback in which streams are moved into a different media container without re-encoding the underlying audio or video. |
| Transcoding | Real-time conversion of video, audio, subtitles, bitrate, or resolution to satisfy client and network requirements. |
| Bind mount | A mapping that presents a host directory at a chosen path inside a container. |
| Persistent data | Data that must remain after a container is recreated, including Jellyfin configuration, users, library records, and selected metadata. |
| Cache | Regenerable working data used to improve operation or hold temporary transcode output; it should be separated from irreplaceable configuration. |
| Media root | A top-level directory beneath which source media is organized into stable content-specific folders. |
| Least privilege | Granting a service only the identities, filesystem access, network reachability, and capabilities it actually requires. |

## Instruction

Jellyfin is an open-source media server that catalogs media files and presents them through web, television, mobile, and other compatible clients. An installation is more than starting an application: it establishes boundaries among application configuration, regenerable cache, valuable source media, and network access. In this class, Jellyfin runs in a container, while every lab-owned persistent path is located under /opt/lab-classroom/class58/. The container can therefore be replaced without losing the setup wizard results, users, libraries, or database. The configuration directory is the important stateful component. The cache directory is separated because it may grow, is frequently written, and can usually be regenerated. The media directory contains source content and is mounted read-only so a compromised or misconfigured Jellyfin process cannot rename, overwrite, or delete source files.

Library design directly affects identification quality. A movie should normally have its own directory and include the release year in both the directory and filename, for example Movies/Example Film (2020)/Example Film (2020).mkv. A show should have a stable series directory, optional release year, season directories, and season-and-episode notation such as Shows/Example Series (2021)/Season 01/Example Series (2021) S01E01.mkv. Specials commonly use Season 00 when supported by the selected metadata source. Music organization normally follows artist, album, and track order, but embedded tags remain especially important for music identification. Home videos should be placed in a separate library because personal recordings generally cannot be matched against public entertainment databases.

Do not combine unrelated media types merely because they share a storage device. Separate Jellyfin libraries allow each content type to use the correct scanner, metadata behavior, display layout, and permissions. The filesystem may still have one media root, but Movies, Shows, Music, and Home-Videos should be distinct children. Avoid vague names, inconsistent years, episode filenames without season and episode numbers, and large directories containing hundreds of unrelated files. Sidecar subtitles should use the same base filename as their video, with language and optional disposition components added before the extension.

The lab binds Jellyfin only to 127.0.0.1:8096. This intentionally prevents direct access from other machines and keeps the exercise focused on installation and data design. Production remote access requires a separately designed ingress path, encrypted transport, authentication policy, trusted name resolution, and explicit network controls. Those production concerns should not be improvised during an introductory installation. Hardware acceleration is also excluded because device paths, drivers, container permissions, and codec support vary by platform. Begin with a correct software-only deployment, observe actual playback needs, and add acceleration later as a deliberate design change.

A successful deployment is verified at several layers. Docker Compose must parse the file, the container must remain running, the browser must display the setup wizard or login page, and Jellyfin must create files in the host configuration directory. Library paths selected in the wizard must use container paths such as /media/Movies rather than host paths. If the host directory is entered in the wizard, Jellyfin will not find it because the application sees the container filesystem. Finally, persistence should be tested by restarting or recreating the container and confirming that the configured administrator and libraries remain present.

## Architecture

### components
### name
Jellyfin container

### role
Runs the Jellyfin server from the pinned jellyfin/jellyfin:10.10.7 image and publishes the web interface only on the host loopback address.
### name
/opt/lab-classroom/class58/config

### role
Stores Jellyfin application state, the server database, users, settings, library definitions, and downloaded metadata.
### name
/opt/lab-classroom/class58/cache

### role
Stores regenerable cache and temporary processing data separately from configuration.
### name
/opt/lab-classroom/class58/media

### role
Provides content-specific source directories mounted read-only at /media inside the container.
### name
Browser

### role
Connects to http://127.0.0.1:8096 to complete setup and administer the local lab server.

### data_flow
The browser sends local HTTP requests to 127.0.0.1:8096.
Docker forwards the loopback-bound host port to port 8096 in the Jellyfin container.
Jellyfin reads and writes persistent application state through the /config bind mount.
Jellyfin writes regenerable working data through the /cache bind mount.
Jellyfin reads source media through the read-only /media bind mount.
During scanning, Jellyfin records library and metadata information in configuration storage without changing source media.

### library_layout
/opt/lab-classroom/class58/media/Movies/Movie Title (Year)/Movie Title (Year).ext
/opt/lab-classroom/class58/media/Shows/Series Title (Year)/Season 01/Series Title (Year) S01E01.ext
/opt/lab-classroom/class58/media/Music/Artist/Album/01 - Track Title.ext
/opt/lab-classroom/class58/media/Home-Videos/Event or Date/Descriptive Filename.ext

### trust_boundaries
The container is isolated from arbitrary host paths and receives only the three declared bind mounts.
The media mount is read-only, while configuration and cache mounts are writable.
The published web port accepts connections only through the host loopback interface.
The service runs with the UID and GID of the account that prepares the lab directories.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Create a library design document at /opt/lab-classroom/class58/library-plan.txt for a hypothetical household with movies, episodic shows, music, family videos, and children's content.

### requirements
List the proposed directory tree beneath the class58 media directory.
Provide two correctly formatted movie examples and two episodic-show examples.
State which libraries may use public metadata providers and which should not.
Describe read-only versus writable storage requirements.
Classify config, cache, metadata, and source media by backup priority.
Describe how administrator and playback accounts should be separated.
Document how future storage expansion could preserve stable container paths.

### success_criteria
The plan separates content types, uses predictable names, protects source media, distinguishes backups from cache regeneration, and does not require moving any lab artifact outside /opt/lab-classroom/class58/.

## Feynman teach-back

### prompt
Explain the installation to a learner who understands folders but has never used containers. Your explanation must cover why Jellyfin sees /media instead of the longer host path, why config survives replacement of the container, and why media is read-only.

### model_explanation
The container is like a room with labeled windows into selected host folders. The host's class58/config folder appears through a window labeled /config, and the media folder appears through another window labeled /media. Jellyfin only knows the labels inside its room, so its library uses /media/Movies instead of the host's longer path. The container itself can be replaced, but the host config folder stays in place, so the new container reads the same accounts and library database. The media window is read-only: Jellyfin can inspect and stream files through it, but it cannot alter the originals.

### self_check
Can you identify which directory contains irreplaceable application state?
Can you explain why cache and configuration are separate?
Can you predict what happens if a host path is entered in the Jellyfin library wizard?
Can you explain how consistent movie and episode names reduce incorrect metadata matches?

## Retrieval check

1. 1. Why does the Jellyfin wizard use /media/Movies rather than /opt/lab-classroom/class58/media/Movies?
2. 2. Which class58 directory contains the most important Jellyfin application state?
3. 3. Why is the media bind mount declared read-only?
4. 4. What naming information most helps distinguish two movies with the same title?
5. 5. What filename notation identifies season 2, episode 4 of an episodic series?
6. 6. What is the difference between direct play and transcoding?
7. 7. Why should home videos normally use a separate library from commercial movies?
8. 8. Which data is generally more practical to regenerate: the cache or the original media?
9. 9. Why is port 8096 bound to 127.0.0.1 in this lab?
10. 10. What should be checked first when the container repeatedly exits during startup?

## Guided lab

### scope
All directories and files explicitly created by the lab are located under /opt/lab-classroom/class58/. Docker will manage the runtime container and its normal engine-managed image data, but no host configuration file is edited.

### steps
### step
1

### title
Create the isolated lab directory structure

### commands
install -d -m 0750 /opt/lab-classroom/class58/config /opt/lab-classroom/class58/cache /opt/lab-classroom/class58/media/Movies /opt/lab-classroom/class58/media/Shows /opt/lab-classroom/class58/media/Music /opt/lab-classroom/class58/media/Home-Videos

### notes
Run the command as an account that is permitted to create the assigned classroom path. Do not redirect any lab output to another directory.
### step
2

### title
Record the current account identity for the container

### commands
printf 'JELLYFIN_UID=%s\nJELLYFIN_GID=%s\n' "$(id -u)" "$(id -g)" > /opt/lab-classroom/class58/.env

### notes
Running the service with the preparing account's numeric identity allows it to write configuration and cache data without granting access as the container root user.
### step
3

### title
Create the Docker Compose definition

### commands
cat > /opt/lab-classroom/class58/compose.yaml <<'YAML'
services:
  jellyfin:
    image: jellyfin/jellyfin:10.10.7
    container_name: class58-jellyfin
    user: "${JELLYFIN_UID}:${JELLYFIN_GID}"
    ports:
      - "127.0.0.1:8096:8096"
    environment:
      JELLYFIN_PublishedServerUrl: "http://127.0.0.1:8096"
    volumes:
      - ./config:/config
      - ./cache:/cache
      - ./media:/media:ro
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    restart: unless-stopped
YAML

### notes
Relative bind-mount sources are resolved from the directory containing compose.yaml. The media mount is deliberately read-only.
### step
4

### title
Validate the rendered Compose configuration

### commands
docker compose --env-file /opt/lab-classroom/class58/.env -f /opt/lab-classroom/class58/compose.yaml config

### notes
Review the rendered port, user, image, and mount paths before starting the service. Correct validation errors rather than bypassing them.
### step
5

### title
Start Jellyfin

### commands
docker compose --env-file /opt/lab-classroom/class58/.env -f /opt/lab-classroom/class58/compose.yaml up -d

### notes
The first start may pull the declared image. The web service remains limited to the host itself.
### step
6

### title
Inspect startup status

### commands
docker compose --env-file /opt/lab-classroom/class58/.env -f /opt/lab-classroom/class58/compose.yaml ps
docker compose --env-file /opt/lab-classroom/class58/.env -f /opt/lab-classroom/class58/compose.yaml logs --tail=100 jellyfin

### notes
The container should remain running. Initial informational messages about database creation and startup are expected.
### step
7

### title
Complete the setup wizard

### commands


### notes
Open http://127.0.0.1:8096 in a browser on the Jellyfin host. Select a language, create a unique administrator name and strong password, and add separate libraries using /media/Movies, /media/Shows, /media/Music, and /media/Home-Videos. Choose the matching content type for each path. Do not use /opt/lab-classroom/class58/media in the wizard because that host path does not exist inside the container.
### step
8

### title
Optionally add authorized test media

### commands


### notes
Copy only media you are authorized to use into the appropriate directory under /opt/lab-classroom/class58/media/. Use the naming patterns taught in this lesson. The destination must remain inside the class58 lab tree.
### step
9

### title
Run a library scan and inspect identification

### commands


### notes
From the Jellyfin dashboard, scan all libraries. If test media was added, verify the title, release year, season, episode, and artwork. Correct source naming before manually overriding large numbers of mismatches.
### step
10

### title
Confirm persistent files were created

### commands
find /opt/lab-classroom/class58/config -maxdepth 2 -type f -print | head -n 20
find /opt/lab-classroom/class58/media -maxdepth 3 -type d -print

### notes
The first command should display Jellyfin-created configuration or database files. The second should display the planned library directory hierarchy.

## Expected results

- The Compose configuration validates without unresolved JELLYFIN_UID or JELLYFIN_GID variables.
- The class58-jellyfin container remains in a running state after startup.
- The Jellyfin setup wizard or login page is available at http://127.0.0.1:8096 on the host.
- Jellyfin creates persistent state beneath /opt/lab-classroom/class58/config/.
- Cache activity is confined to /opt/lab-classroom/class58/cache/ for the declared cache mount.
- The Movies, Shows, Music, and Home-Videos directories are visible inside Jellyfin through their /media paths.
- Jellyfin can read authorized media placed in the library directories but cannot write to the read-only media mount.
- An empty library remains valid and simply shows no titles until supported media files are added.
- Container recreation preserves the administrator account and library definitions because configuration is bind-mounted.

## Verification checkpoints

- [ ] Run `docker compose --env-file /opt/lab-classroom/class58/.env -f /opt/lab-classroom/class58/compose.yaml config` and confirm that the rendered configuration contains only the intended class58 bind mounts.
- [ ] Run `docker compose --env-file /opt/lab-classroom/class58/.env -f /opt/lab-classroom/class58/compose.yaml ps` and confirm that class58-jellyfin is running.
- [ ] Open http://127.0.0.1:8096 and confirm that the setup wizard or authenticated Jellyfin interface loads.
- [ ] Open the Jellyfin dashboard, inspect the libraries, and confirm that their container paths begin with /media/.
- [ ] Inspect /opt/lab-classroom/class58/config/ and confirm that Jellyfin created persistent files after first start.
- [ ] Inspect the Compose file and confirm that the media mapping ends with `:ro`.
- [ ] Restart the service with `docker compose --env-file /opt/lab-classroom/class58/.env -f /opt/lab-classroom/class58/compose.yaml restart jellyfin`, then confirm that the configured account and libraries remain present.
- [ ] If authorized sample media was added, initiate a scan and confirm that well-named items appear in the matching library rather than an unrelated content type.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Docker Compose reports that JELLYFIN_UID or JELLYFIN_GID is unset. | The .env file was not created, was written to another directory, or was not supplied with the command. | Inspect /opt/lab-classroom/class58/.env, regenerate it using the lesson command, and include the documented --env-file argument. |
| The container exits immediately or repeatedly restarts. | Jellyfin cannot write to the configuration or cache bind mount, or the Compose file contains an invalid customization. | Read the container logs, confirm that config and cache are owned and writable by the UID and GID recorded in .env, and compare the rendered Compose configuration with the lesson definition. |
| The browser cannot connect to 127.0.0.1:8096. | The container is not running, another process already uses port 8096, or the browser is not running on the Jellyfin host. | Check Compose status and logs. Confirm that the browser is local to the host. If port 8096 is occupied, choose an unused loopback host port in compose.yaml while leaving the container-side port as 8096. |
| Jellyfin reports that a library path does not exist. | A host path such as /opt/lab-classroom/class58/media/Movies was entered in the wizard instead of the container path. | Edit the library and use /media/Movies, /media/Shows, /media/Music, or /media/Home-Videos as appropriate. |
| Media directories exist, but titles are not discovered. | The directory is empty, files use unsupported formats, the service identity lacks read and traversal access, or the scan has not run. | Confirm that authorized files exist beneath the expected path, verify that the recorded UID and GID can read them, and initiate a library scan. |
| A movie or episode is matched to the wrong title. | The filename is ambiguous, the release year is absent, or season and episode notation is inconsistent. | Rename the source within the class58 media tree using the documented movie or series pattern, scan the library again, and use manual identification only when naming cannot disambiguate the item. |
| Bind mounts are denied on a host with mandatory access controls enabled. | The container runtime is not permitted to access the current labels on the class58 directories. | Follow the host platform's documented container-labeling procedure. If the platform supports the Compose `Z` bind option, apply it only to the three class58 bind mounts and revalidate the rendered configuration. |
| Playback starts but consumes substantial CPU or fails for a particular client. | The client cannot direct play the stored streams and Jellyfin is attempting software transcoding. | Inspect the Jellyfin playback information to determine whether direct play, remuxing, or transcoding is occurring. Treat hardware acceleration as a separate future change rather than adding unverified host devices during this lab. |
| Jellyfin cannot save artwork beside the media files. | The media bind mount is intentionally read-only. | Keep downloaded metadata in Jellyfin's configuration storage for this lab. Do not make source media writable merely to store artwork beside it. |

## Security considerations

### principles
The web port is bound to 127.0.0.1 instead of all host interfaces.
The container runs with the preparing user's numeric UID and GID rather than the container root identity.
All Linux capabilities are dropped and no-new-privileges is enabled.
Source media is mounted read-only.
Only configuration and cache paths are writable by Jellyfin.
A unique administrator account and strong password are required during setup.
The deployment does not expose host hardware devices or unrelated host directories.
Production access should use an independently reviewed encrypted ingress design rather than directly publishing this classroom service.

### data_protection
Back up the configuration directory before upgrades or significant library changes. Source media requires its own backup strategy because the Jellyfin database and metadata do not replace the original files. Cache is generally lower priority because it can be regenerated.

### privacy
Media names, watch history, user names, images, and metadata can reveal personal interests or household information. Restrict administrative access and avoid uploading private home-video information to unnecessary external metadata services.

### account_guidance
Do not reuse an infrastructure administrator password. Create individual non-administrator users for routine playback and reserve the Jellyfin administrator account for management.

### scope_constraint
Do not add host root directories, personal home directories, device nodes, or container-engine control interfaces as Jellyfin mounts.

## Rollback

### preserve_data
Stop and remove the classroom container while retaining all bind-mounted configuration, cache, and media files under /opt/lab-classroom/class58/.

### command
docker compose --env-file /opt/lab-classroom/class58/.env -f /opt/lab-classroom/class58/compose.yaml down

### restart_after_rollback
Run the documented Compose up command again. Jellyfin should recover its prior account and library configuration from the preserved config directory.

### full_reset_guidance
A full reset requires first stopping the container and then deliberately removing only selected contents beneath /opt/lab-classroom/class58/. Preserve authorized source media and copy any required configuration backup before resetting. No deletion command is provided because reset requirements differ and accidental selection of the media directory would destroy source files.

## Video narration notes

Welcome to Class 58, Jellyfin Installation and Library Design. In this lesson, we will deploy a deliberately isolated Jellyfin server and focus on a principle that matters more than the initial setup wizard: preserving clear boundaries among application state, cache, and source media.

Our entire classroom layout is rooted at /opt/lab-classroom/class58. The config directory holds Jellyfin's durable application state. The cache directory holds working data that is normally less valuable and can often be regenerated. The media directory contains four content-specific roots: Movies, Shows, Music, and Home-Videos. Jellyfin receives write access to config and cache, but the media tree is mounted read-only. That means the server can identify and stream files without receiving permission to alter the originals.

The Compose definition binds the web interface to 127.0.0.1 on port 8096. This is intentional. It gives us a local administration surface without turning an introductory exercise into a remotely exposed service. The container also runs with the numeric identity of the account that prepared the lab, drops Linux capabilities, and enables no-new-privileges.

After validating the Compose definition, start the service and inspect its status and recent logs. Open the local web interface and complete the setup wizard. Remember that the wizard operates inside the container. The host folder ending in media/Movies appears to Jellyfin as /media/Movies. The same relationship applies to Shows, Music, and Home-Videos.

Library organization is part of the installation, not an afterthought. Give each movie its own directory and include the release year. Give each series a stable title directory, season directories, and episode filenames with season-and-episode notation. Keep music organized by artist and album while maintaining accurate embedded tags. Separate home videos because public entertainment metadata is usually inappropriate for private recordings.

When the setup is complete, verify the deployment at multiple layers. Confirm that the container remains running, the browser interface opens, configuration files appear under the class58 config directory, and every Jellyfin library points to a path under /media. If you add authorized test content, scan the libraries and inspect the match quality. Fix ambiguous source naming before relying on repeated manual corrections.

Finally, remember the backup distinction. Configuration preserves accounts, preferences, databases, and library definitions. Cache is usually replaceable. Source media is independently valuable and needs its own protection strategy. A container image is not a backup of either configuration or media. By separating these concerns now, you create an installation that is easier to troubleshoot, migrate, secure, and upgrade.

## References

- Jellyfin Documentation: https://jellyfin.org/docs/
- Jellyfin Container Installation: https://jellyfin.org/docs/general/installation/container/
- Jellyfin Movie Naming: https://jellyfin.org/docs/general/server/media/movies/
- Jellyfin Show Naming: https://jellyfin.org/docs/general/server/media/shows/
- Jellyfin Music Organization: https://jellyfin.org/docs/general/server/media/music/
- Jellyfin Networking Documentation: https://jellyfin.org/docs/general/networking/
- Jellyfin Hardware Acceleration Documentation: https://jellyfin.org/docs/general/post-install/transcoding/hardware-acceleration/
- Docker Compose Documentation: https://docs.docker.com/compose/
- Docker Bind Mount Documentation: https://docs.docker.com/engine/storage/bind-mounts/

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

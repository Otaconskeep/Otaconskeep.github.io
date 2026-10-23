# Reading: Jellyfin Installation and Library Design

**Module:** Requests & Media Servers
**Activity type:** Reading (Learn)
**Objective:** Describe the roles of Jellyfin configuration, cache, metadata, and media storage

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

## Required reading

- Jellyfin documentation home: https://jellyfin.org/docs/
- Jellyfin container installation documentation: https://jellyfin.org/docs/general/installation/container/
- Jellyfin media organization documentation: https://jellyfin.org/docs/general/server/media/movies/
- Jellyfin television organization documentation: https://jellyfin.org/docs/general/server/media/shows/
- Docker Compose file reference: https://docs.docker.com/reference/compose-file/

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

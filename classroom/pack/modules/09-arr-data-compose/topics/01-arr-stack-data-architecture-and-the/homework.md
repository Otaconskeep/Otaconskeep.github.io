# Homework: ARR Stack Data Architecture and the /data Model

**Module:** ARR Data Model & Compose
**Activity type:** Homework / independent application
**Objective:** Explain why download and media paths should share one visible /data namespace.

## Requirements

Draw a proposed /data tree for television, movies, and music, including both torrent and Usenet workflows.
Create a service matrix listing the host path, container path, access mode, UID, GID, category, and deletion authority for Sonarr, Radarr, the download clients, and the media server.
For an existing nonproduction stack, record the device number of each download and library directory using stat without changing any files.
Identify every remote path mapping in the existing design and justify whether it represents a genuinely remote path or masks inconsistent local mounts.
Write a backup policy that separates application configuration, active downloads, and organized media.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

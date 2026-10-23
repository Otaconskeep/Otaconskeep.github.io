# Lab: Jellyfin Installation and Library Design

**Module:** Requests & Media Servers
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Describe the roles of Jellyfin configuration, cache, metadata, and media storage

## Before you start

- A Linux homelab host with Docker Engine and the Docker Compose plugin installed
- Permission to run Docker commands without changing host-wide configuration
- At least 2 GB of available storage for the image, configuration, cache, and lab artifacts
- A web browser running on the Jellyfin host or another approved way to access a loopback-bound web service
- Basic familiarity with Linux paths, containers, ports, and YAML
- Only legally owned or otherwise authorized media may be used in the lab

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

## Verification

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

## Security

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

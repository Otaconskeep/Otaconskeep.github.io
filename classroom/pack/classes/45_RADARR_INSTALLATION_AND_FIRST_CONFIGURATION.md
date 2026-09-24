# Class 45: Radarr Installation and First Configuration

**Learning objective:** Explain Radarr's role in a media automation architecture; Deploy Radarr with Docker Compose while keeping lesson-created persistent files under /opt/lab-classroom/class45/; Map Radarr configuration, movie library, and download-staging directories into the container; Complete the initial authentication and media-management configuration; Add and validate a movie root folder; Explain why Radarr and a download client must agree on filesystem paths; Verify container status, web access, persistence, and basic application health; Stop the deployment and disable its Compose definition without deleting classroom data
**Bloom level:** Understand / Apply
**Track:** Media Automation · **Difficulty:** beginner · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Install Radarr as a containerized service, create persistent application and media directories, complete the initial web configuration, and understand how Radarr coordinates movie monitoring, indexers, download clients, and media imports.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### host_platform
Linux host capable of running Docker Engine and the Docker Compose plugin

### container_image
lscr.io/linuxserver/radarr:latest

### application_interface
Radarr web interface on container TCP port 7878

### architecture_notes
Image architecture availability depends on the image publisher's current manifest. Confirm support for the host architecture before deployment.

### version_notes
Radarr interface labels and initial authentication prompts can change between releases. Use the current official documentation when the interface differs from this lesson.

### production_note
The classroom file uses a moving image tag for accessibility. Production deployments should pin a reviewed version or immutable digest and test upgrades against a backup.

### scope
The lesson configures Radarr only. Indexers, indexer managers, download clients, reverse proxies, and production media shares are outside this class.

## Learning objective

- Explain Radarr's role in a media automation architecture
- Deploy Radarr with Docker Compose while keeping lesson-created persistent files under /opt/lab-classroom/class45/
- Map Radarr configuration, movie library, and download-staging directories into the container
- Complete the initial authentication and media-management configuration
- Add and validate a movie root folder
- Explain why Radarr and a download client must agree on filesystem paths
- Verify container status, web access, persistence, and basic application health
- Stop the deployment and disable its Compose definition without deleting classroom data

## Why this matters

Install Radarr as a containerized service, create persistent application and media directories, complete the initial web configuration, and understand how Radarr coordinates movie monitoring, indexers, download clients, and media imports.

## Prerequisites

- A Linux homelab host with Docker Engine and the Docker Compose plugin already installed
- Permission to run Docker commands without changing host-wide configuration
- A web browser that can reach the homelab host on TCP port 7878
- The directory /opt/lab-classroom must already exist and be writable by the learner
- Basic familiarity with containers, bind mounts, ports, and YAML
- No existing service may be using the selected host port

## Required reading

- Radarr documentation: https://wiki.servarr.com/radarr
- Radarr quick start guide: https://wiki.servarr.com/radarr/quick-start-guide
- Radarr Docker guidance: https://wiki.servarr.com/docker-guide
- Docker Compose documentation: https://docs.docker.com/compose/
- LinuxServer.io Radarr image documentation: https://docs.linuxserver.io/images/docker-radarr/

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Radarr | A movie collection manager that monitors desired movies, evaluates releases, communicates with download clients, and imports completed files into a movie library. |
| Root folder | The top-level library directory beneath which Radarr creates and manages individual movie folders. |
| Quality profile | A policy defining acceptable movie qualities, their preference order, and the quality at which Radarr should stop seeking upgrades. |
| Indexer | A searchable source of release metadata. Radarr queries configured indexers directly or through an indexer manager. |
| Download client | An external application that receives download requests from Radarr and reports their status. |
| Completed Download Handling | Radarr's process for detecting completed jobs, importing eligible files, renaming them when configured, and placing them in the movie library. |
| Bind mount | A mapping that exposes a specific host directory at a defined path inside a container. |
| Path mapping | The relationship between a host path and its container-visible path. Consistent mappings are important when multiple applications exchange file locations. |
| PUID and PGID | LinuxServer.io container variables that select the numeric user and group identities used by the application process for file access. |
| API key | A secret token used by authorized applications to call the Radarr API. It should be protected like a password. |

## Instruction

Radarr does not download movies by itself. It acts as an automation and policy layer between a movie catalog, release indexers, a download client, and the final media library. A user adds a movie and selects a root folder, monitoring state, and quality profile. Radarr searches configured indexers, compares releases against the profile and other rules, and can send an accepted release to a separate download client. After the client finishes, Radarr evaluates the completed files and imports them into the movie library. This separation of responsibilities is central to troubleshooting: search failures usually involve indexers, transfer failures involve the download client, and import failures commonly involve permissions or incompatible paths.

Container deployment makes path design especially important. The host directories in this lesson are exposed inside Radarr as /config, /movies, and /downloads. Radarr stores its database, settings, logs, and API key under /config. The /movies path is the managed library root. The /downloads path represents a staging area that could later be shared with a download client. If another container reports a completed file as /data/example.mkv while Radarr can see that same file only as /downloads/example.mkv, the import will fail unless the mappings are made consistent or an appropriate remote path mapping is configured. Using the same container-side download path across cooperating applications is normally easier to reason about.

The initial configuration should establish authentication before the service is exposed beyond a trusted administrative network. Quality profiles should express intentional policy rather than simply enabling every quality. Enabling upgrades allows Radarr to replace an existing file until the profile's cutoff is reached. Renaming can produce a consistent library, but learners should preview naming choices before applying them to an established collection. The root folder must be the library destination, not the download staging directory. Radarr should be permitted to organize the library, while human users and other services should avoid making conflicting changes during imports.

This class deploys only Radarr. It does not configure a real indexer or download client because those services require separate credentials, connectivity, and policy decisions. Warnings about missing indexers or download clients are therefore expected in this isolated first-configuration lab. The goal is to establish a durable application configuration, a valid root folder, authentication, and a clear model of the data flow. All lesson-created persistent host files remain under /opt/lab-classroom/class45/ so the exercise is isolated and can be stopped without altering unrelated application directories.

## Architecture

### components
A browser used for Radarr administration
A Docker host running the Radarr container
A persistent configuration directory mounted at /config
A movie library directory mounted at /movies
A download-staging directory mounted at /downloads
Future external indexer and download-client services

### request_flow
The browser connects to the Docker host on the selected host port.
Docker publishes the host port to Radarr's container port 7878.
Radarr reads its database and settings from /config.
Radarr treats /movies as the destination root for organized movie files.
A future download client would place completed data where Radarr can access it through /downloads.

### host_paths
### compose_definition
/opt/lab-classroom/class45/compose.yaml

### environment_file
/opt/lab-classroom/class45/.env

### radarr_configuration
/opt/lab-classroom/class45/config/

### movie_library
/opt/lab-classroom/class45/media/movies/

### download_staging
/opt/lab-classroom/class45/downloads/

### container_paths
### /config
Persistent Radarr database, configuration, logs, and internal metadata

### /movies
Movie library root managed by Radarr

### /downloads
Staging location intended for completed downloads

### networking
The Compose project publishes a configurable host port, defaulting to 7878, to TCP port 7878 in the Radarr container. No indexer or download-client container is created in this class.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Draw a diagram showing a browser, Radarr, an indexer manager, a download client, a staging directory, and a movie library. Label each control and file-data flow.
Write a proposed path-mapping table for a future download-client container that uses the same /downloads path as Radarr.
Compare two Radarr quality profiles in the web interface and explain how upgrade behavior and cutoff differ.
Document which parts of this deployment are configuration state, temporary transfer data, and final library data.
Propose a backup plan for /opt/lab-classroom/class45/config/ that includes backup frequency, retention, restoration testing, and secret handling.
Research how to pin the LinuxServer.io Radarr image to a reviewed version or immutable digest, but do not modify the class deployment.

## Feynman teach-back

Explain Radarr as if teaching someone who has never used media automation: Radarr is the coordinator, not the downloader. A user tells it which movie is wanted and what quality is acceptable. Radarr asks an indexer what releases exist, chooses an allowed release, and gives that request to a download client. When the download client finishes, Radarr needs to see the same completed file path so it can import the file into the organized movie library. In this lab, /config remembers Radarr's settings, /downloads is the staging area, and /movies is the final library. If /config is not persistent, Radarr forgets its setup. If /downloads is not consistently mapped, imports fail. If /movies is not writable, Radarr cannot organize the library.

## Retrieval check

1. 1. Does Radarr download movie data directly, and what component normally performs that task?
2. 2. What is stored in the /config bind mount, and why must it persist?
3. 3. Why is /movies the correct root folder while /downloads is not?
4. 4. What problem can occur if a download client reports /data/film.mkv but Radarr can see the file only as /downloads/film.mkv?
5. 5. What do PUID and PGID control in the LinuxServer.io container?
6. 6. Why can missing indexer and download-client health notices be acceptable in this class?
7. 7. Which setting determines the qualities Radarr accepts and the quality at which it stops seeking upgrades?
8. 8. What should be verified after restarting the Radarr container?
9. 9. Why should the API key be treated as a secret?
10. 10. What is the safer production practice regarding container image versions?

## Guided lab

### scope_guard
Every file or directory created by the lesson commands is located under /opt/lab-classroom/class45/. Do not substitute production media directories during this classroom exercise.

### steps
### step
1

### title
Confirm Docker and Compose availability

### commands
docker --version
docker compose version
id -u
id -g

### instructions
Run the checks without installing or reconfiguring anything. Record the numeric user and group identifiers if you want to compare them with the generated environment file.
### step
2

### title
Create isolated persistent directories

### commands
mkdir -p /opt/lab-classroom/class45/config /opt/lab-classroom/class45/media/movies /opt/lab-classroom/class45/downloads

### instructions
These directories contain all lesson-created persistent application data and media placeholders.
### step
3

### title
Create the Compose environment file

### commands
printf 'PUID=%s\nPGID=%s\nTZ=Etc/UTC\nHOST_PORT=7878\n' "$(id -u)" "$(id -g)" > /opt/lab-classroom/class45/.env

### instructions
The generated PUID and PGID match the current shell user. If port 7878 is already allocated, edit only HOST_PORT in this file and use the new port in subsequent browser instructions. Set TZ to a valid timezone name if local timestamps are preferred.
### step
4

### title
Create the Radarr Compose definition

### commands
cat > /opt/lab-classroom/class45/compose.yaml <<'EOF'
services:
  radarr:
    image: lscr.io/linuxserver/radarr:latest
    container_name: class45-radarr
    environment:
      PUID: ${PUID}
      PGID: ${PGID}
      TZ: ${TZ}
    volumes:
      - /opt/lab-classroom/class45/config:/config
      - /opt/lab-classroom/class45/media/movies:/movies
      - /opt/lab-classroom/class45/downloads:/downloads
    ports:
      - "${HOST_PORT:-7878}:7878"
    restart: unless-stopped
EOF

### instructions
The three bind mounts use explicit host paths so there is no ambiguity about where classroom data is stored.
### step
5

### title
Validate the resolved Compose model

### commands
docker compose --project-directory /opt/lab-classroom/class45 --env-file /opt/lab-classroom/class45/.env -f /opt/lab-classroom/class45/compose.yaml config

### instructions
Inspect the rendered output. Confirm that the service has three expected bind mounts and that the selected host port maps to container port 7878 before starting it.
### step
6

### title
Start Radarr

### commands
docker compose --project-directory /opt/lab-classroom/class45 --env-file /opt/lab-classroom/class45/.env -f /opt/lab-classroom/class45/compose.yaml up -d
docker compose --project-directory /opt/lab-classroom/class45 --env-file /opt/lab-classroom/class45/.env -f /opt/lab-classroom/class45/compose.yaml ps
docker compose --project-directory /opt/lab-classroom/class45 --env-file /opt/lab-classroom/class45/.env -f /opt/lab-classroom/class45/compose.yaml logs --tail 100 radarr

### instructions
Wait until the logs show that Radarr has started listening. Image download and first initialization duration depends on the host and network, so no fixed startup time is assumed.
### step
7

### title
Complete initial authentication

### commands


### instructions
Open http://HOST_ADDRESS:7878 in a browser, replacing HOST_ADDRESS and the port if necessary. When prompted, select an authentication method suitable for interactive administration, create a unique username and strong password, and save. Do not reuse another service's credentials. If the version presents authentication under Settings, open Settings, General, configure authentication, and save.
### step
8

### title
Review media-management settings

### commands


### instructions
Open Settings, Media Management. Review movie naming, folder naming, and Completed Download Handling. Leave destructive or large-scale rename actions unused in this empty classroom deployment. Save only settings you understand.
### step
9

### title
Add the movie root folder

### commands


### instructions
Open Settings, Media Management, then Root Folders. Add /movies as the root folder. Do not select /downloads: it is a staging path, not the organized library destination.
### step
10

### title
Inspect quality profiles

### commands


### instructions
Open Settings, Profiles and inspect an existing quality profile. Identify its accepted qualities, upgrade setting, and cutoff. A production policy should be chosen according to storage, client compatibility, and content preferences; this lab does not prescribe a universal profile.
### step
11

### title
Review system health

### commands


### instructions
Open System, Status and System, Health. Record the displayed Radarr version and container-relevant paths. Missing indexer and download-client notices are expected because those integrations are intentionally outside this class.
### step
12

### title
Test persistence through a controlled restart

### commands
docker compose --project-directory /opt/lab-classroom/class45 --env-file /opt/lab-classroom/class45/.env -f /opt/lab-classroom/class45/compose.yaml restart radarr
docker compose --project-directory /opt/lab-classroom/class45 --env-file /opt/lab-classroom/class45/.env -f /opt/lab-classroom/class45/compose.yaml ps

### instructions
After Radarr is available again, sign in and confirm that /movies remains configured as the root folder.

## Expected results

- The Compose model resolves without a YAML or interpolation error.
- The class45-radarr container is running and publishes the selected host port to container port 7878.
- The Radarr web interface is reachable from the learner's browser.
- Administrative authentication is enabled with learner-selected credentials.
- Radarr accepts /movies as a root folder.
- Configuration files appear beneath /opt/lab-classroom/class45/config/ after first startup.
- The /movies root folder remains configured after a controlled container restart.
- System Health may report missing indexers or download clients because those integrations are intentionally not configured.

## Verification checkpoints

- [ ] Run: docker compose --project-directory /opt/lab-classroom/class45 --env-file /opt/lab-classroom/class45/.env -f /opt/lab-classroom/class45/compose.yaml ps
- [ ] Confirm that class45-radarr is listed as running and that the displayed port mapping ends in container port 7878.
- [ ] Run: docker compose --project-directory /opt/lab-classroom/class45 --env-file /opt/lab-classroom/class45/.env -f /opt/lab-classroom/class45/compose.yaml logs --tail 100 radarr
- [ ] Confirm that the recent logs do not show a repeating startup crash, database-open failure, or permission-denied loop.
- [ ] Sign in through the web interface and confirm that Settings, Media Management lists /movies as a root folder.
- [ ] Open System, Status and confirm that Radarr reports an application version and uses /config for application data.
- [ ] Restart the service with Docker Compose, sign in again, and confirm that authentication and the /movies root folder persist.
- [ ] Run: find /opt/lab-classroom/class45 -maxdepth 2 -type d -print
- [ ] Confirm that the classroom configuration, media, and download directories remain under /opt/lab-classroom/class45/.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Docker Compose reports that the host port is already allocated. | Another process or container is already listening on the HOST_PORT value. | Edit /opt/lab-classroom/class45/.env, assign an unused high port to HOST_PORT, start the Compose project again, and browse to the revised port. |
| The browser cannot connect even though the container was started. | Radarr is still initializing, the wrong host address or host port was used, or the container exited. | Check Docker Compose status and recent Radarr logs. Verify the HOST_PORT value in the environment file and use the Docker host's reachable address rather than the container's internal address. |
| The container repeatedly restarts and logs show permission-denied errors under /config. | The PUID or PGID does not represent an identity that can write to the classroom directories, or the directories were created by a different account. | Stop the Compose project, inspect directory ownership and the numeric values in .env, then have the lab administrator assign the classroom directory to the intended lab account. Do not broaden permissions indiscriminately. |
| Radarr refuses to add /movies or reports that the folder is not writable. | The movie bind mount is missing, incorrectly typed, or inaccessible to the configured container identity. | Run the Compose configuration validation command, confirm the host path maps to /movies, inspect recent logs, and correct the mapping or classroom-directory ownership before recreating the service. |
| The selected root folder disappears after a restart. | The /config mount was omitted, changed, or not writable, so Radarr used nonpersistent container storage or could not save its database. | Confirm that /opt/lab-classroom/class45/config maps to /config and that startup logs show no database-write errors. Restore the expected mapping and start the service again. |
| System Health reports that no indexers or download clients are available. | This introductory deployment intentionally does not configure those external services. | Treat these notices as expected for this class. Configure approved indexer and download-client integrations in later classes before expecting automated searches or transfers. |
| A future download completes but Radarr cannot import the reported file. | Radarr and the download client refer to the shared data using different container paths, or Radarr lacks access to the completed file. | Prefer consistent shared container paths between the applications. If the download client is remote and consistency is impossible, configure a carefully tested remote path mapping and verify access permissions. |
| The learner cannot sign in after initial setup. | The username, password, or selected authentication method was recorded incorrectly. | First verify the exact address and credentials. For classroom recovery, stop the service and follow the version-appropriate official Radarr authentication recovery documentation; preserve a copy of the configuration directory before editing application configuration. |

## Security considerations

Keep the Radarr administrative interface on a trusted management network and do not publish it directly to the public internet.
Enable authentication during first configuration and use a unique, strong password.
Treat the Radarr API key as a secret because it authorizes programmatic control of the application.
Grant the container identity write access only to the configuration, intended library, and staging directories it requires.
Do not solve permission problems by granting unrestricted access to every local user.
Review release sources and integrations before entering credentials or API keys.
Use encrypted transport through a properly managed reverse proxy if administration must cross an untrusted network.
Pin a tested image version or immutable digest for a production deployment instead of accepting unreviewed image changes automatically.
Back up the persistent /config directory before upgrades or database recovery work.
Do not point this classroom instance at an existing production movie library.

## Rollback

### goal
Stop Radarr and disable accidental relaunch while preserving all classroom data for inspection or later recovery.

### steps
Run: docker compose --project-directory /opt/lab-classroom/class45 --env-file /opt/lab-classroom/class45/.env -f /opt/lab-classroom/class45/compose.yaml down
Run: mv /opt/lab-classroom/class45/compose.yaml /opt/lab-classroom/class45/compose.yaml.disabled
Confirm that class45-radarr no longer appears in: docker ps --filter name=class45-radarr
Leave /opt/lab-classroom/class45/config/, /opt/lab-classroom/class45/media/, and /opt/lab-classroom/class45/downloads/ intact.

### restore
Run: mv /opt/lab-classroom/class45/compose.yaml.disabled /opt/lab-classroom/class45/compose.yaml
Validate the Compose model again.
Start the project with the same Docker Compose command used in the lab.
Sign in and confirm that the persisted root-folder configuration is present.

## Video narration notes

Welcome to Class 45, Radarr Installation and First Configuration. In this lesson we will deploy Radarr with Docker Compose and keep every lesson-created persistent file under the class45 classroom directory. Before starting, remember that Radarr is not itself a download client. It manages movie requests and policies, searches through configured indexers, sends approved releases to a download client, and imports completed files into an organized library.

We begin by checking Docker, Docker Compose, and our numeric user and group identifiers. Next, we create separate directories for Radarr configuration, the movie library, and download staging. This separation is intentional. Configuration must persist so that the application remembers its database and settings. The movie directory is the final organized library. The downloads directory is only a staging location for a future download client.

The environment file records the current user's numeric identity, the timezone, and the host port. The Compose definition then maps the classroom configuration directory to /config, the library to /movies, and staging to /downloads. Before starting anything, we render the Compose configuration and inspect the resolved paths and port mapping. This validation catches common YAML, variable, and path errors early.

After starting the service, we inspect its status and recent logs. We then open the web interface and establish authentication. Use a unique password and keep the service on a trusted administrative network. Within Media Management, we review naming and import options, then add /movies as the root folder. We do not add /downloads as a root folder because staging data and organized library data serve different purposes.

We also inspect quality profiles. A quality profile is a policy, not merely a list of formats. It determines which qualities are acceptable, whether upgrades are allowed, and when Radarr should stop looking for a better release. This isolated class does not connect a real indexer or download client, so related health warnings are expected.

Finally, we restart Radarr and confirm that authentication and the root-folder setting persist. If they do not, the first place to investigate is the /config bind mount and its write permissions. At the end of the lesson, you should be able to explain Radarr's role, distinguish staging from library storage, and describe why consistent paths are essential when Radarr exchanges completed-download information with another container.

## References

- Radarr official site: https://radarr.video/
- Servarr Radarr documentation: https://wiki.servarr.com/radarr
- Servarr Radarr quick start guide: https://wiki.servarr.com/radarr/quick-start-guide
- Servarr Docker guide: https://wiki.servarr.com/docker-guide
- LinuxServer.io Radarr container documentation: https://docs.linuxserver.io/images/docker-radarr/
- Docker Compose file reference: https://docs.docker.com/reference/compose-file/
- Docker bind mount documentation: https://docs.docker.com/engine/storage/bind-mounts/

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

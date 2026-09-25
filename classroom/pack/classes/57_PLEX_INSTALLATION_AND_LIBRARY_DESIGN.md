# Class 57: Plex Installation and Library Design

**Learning objective:** Explain the roles of Plex configuration, transcode, and media storage.; Design separate movie, television, music, and home-video libraries.; Prepare a Compose specification that uses explicit bind mounts and read-only media access.; Describe how host numeric user and group IDs affect Plex access to mounted files.; Explain why configuration data requires backup while transcode data usually does not.; Validate a staged Plex deployment without launching a container.; Identify safe network exposure and remote-access decisions for Plex.
**Bloom level:** Understand / Apply
**Track:** Media Services · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Design a maintainable Plex Media Server deployment, prepare a container-oriented installation bundle, and organize media libraries so Plex can scan them reliably without exposing secrets or granting unnecessary write access. The classroom lab stages configuration only inside /opt/lab-classroom/class57/ and does not start a container or alter the host container runtime.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### host_platforms
Linux hosts with a POSIX-compatible filesystem
Docker Compose implementations supporting the Compose Specification
Podman Compose environments after platform-specific review

### plex_image
The staged example uses plexinc/pms-docker:public. Production administrators must review current publisher guidance and apply their organization's image pinning and update policy.

### architecture_notes
The manifest does not assume a particular CPU architecture beyond support offered by the selected image. Hardware transcoding is intentionally excluded.

### filesystem_notes
Plex configuration storage should support normal database locking, ownership, and permission semantics. Network filesystems require platform-specific validation before they are used for application configuration.

### lab_boundary
Only /opt/lab-classroom/class57/ may be mutated. Starting the Compose project, pulling an image, installing host packages, or creating runtime resources is outside this lab.

## Learning objective

- Explain the roles of Plex configuration, transcode, and media storage.
- Design separate movie, television, music, and home-video libraries.
- Prepare a Compose specification that uses explicit bind mounts and read-only media access.
- Describe how host numeric user and group IDs affect Plex access to mounted files.
- Explain why configuration data requires backup while transcode data usually does not.
- Validate a staged Plex deployment without launching a container.
- Identify safe network exposure and remote-access decisions for Plex.

## Why this matters

Design a maintainable Plex Media Server deployment, prepare a container-oriented installation bundle, and organize media libraries so Plex can scan them reliably without exposing secrets or granting unnecessary write access. The classroom lab stages configuration only inside /opt/lab-classroom/class57/ and does not start a container or alter the host container runtime.

## Prerequisites

- Comfort using a Linux shell and reading YAML.
- Basic understanding of containers, bind mounts, TCP ports, users, groups, and file permissions.
- A pre-created, writable /opt/lab-classroom/class57/ directory.
- Python 3 for local validation.
- Optional Docker Compose or Podman Compose installation for syntax inspection only; the lab does not start Plex.

## Required reading

- Plex Support: Naming and Organizing Your Movie Media Files — https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/
- Plex Support: Naming and Organizing Your TV Show Files — https://support.plex.tv/articles/naming-and-organizing-your-tv-show-files/
- Plex Support: What Network Ports Do I Need to Allow Through My Firewall? — https://support.plex.tv/articles/200931138-troubleshooting-remote-access/
- Docker documentation: Bind mounts — https://docs.docker.com/engine/storage/bind-mounts/
- Compose Specification — https://compose-spec.io/

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Library | A logical Plex collection associated with a media type and one or more filesystem locations, such as Movies mapped to /media/movies. |
| Scanner | The Plex component that examines directory names and filenames to identify media items. |
| Metadata agent | The component that associates scanned media with titles, artwork, descriptions, cast information, and other metadata. |
| Direct Play | Playback in which the client consumes the stored container, codecs, bitrate, and subtitles without server-side conversion. |
| Direct Stream | Playback that repackages compatible audio and video streams into a different container without fully transcoding them. |
| Transcode | Server-side conversion of video, audio, subtitles, bitrate, or resolution to satisfy client or network limitations. |
| Bind mount | A mapping that exposes a specific host path at a specific path inside a container. |
| PUID and PGID | Common environment-variable names used by container images to select the numeric user and group identities under which an application operates. |
| Claim token | A short-lived credential used during some Plex server enrollment workflows; it must be treated as a secret and must not be committed to a manifest. |
| Configuration database | The persistent Plex application state containing library definitions, metadata, preferences, watch state, and related records. |

## Instruction

A durable Plex installation begins with storage and identity design, not with starting a container. Plex has three storage classes with different lifecycles. The configuration path is persistent and important because it holds server preferences, databases, metadata, posters, and watch state. It should reside on reliable storage and be backed up while Plex is stopped or while an application-consistent backup method is used. The transcode path is temporary workspace. It must be writable, should have adequate free space, and can usually be recreated after a failure. Media paths contain the source library and should normally be mounted read-only into Plex. Read-only media mounts reduce the consequences of an application defect or compromised service account, although a separate media-management workflow may still require write access elsewhere.

Library organization directly affects matching accuracy. A movie should normally have its own directory, such as Movies/Arrival (2016)/Arrival (2016).mkv. Episodes should follow a season-aware layout such as TV/The Expanse (2015)/Season 01/The Expanse (2015) - S01E01.mkv. Consistent titles, years, seasons, and episode numbers reduce ambiguity. Extras, multi-part media, subtitles, and editions should follow the current Plex naming guidance rather than an improvised convention. Keep unrelated media types in separate roots so a movie scanner is not asked to interpret television episodes or personal recordings.

Container access is governed by numeric identities and directory permissions, not merely by matching account names. Before production deployment, determine the UID and GID used by the container image, confirm that the configuration and transcode paths are writable by that identity, and confirm that media paths are readable but not writable. Avoid making every path universally writable. The staged Compose file uses explicit bind mounts because they make host placement and backup scope visible. It maps only TCP port 32400, which is sufficient for direct web access and many manually configured clients. Automatic discovery and remote access may require additional network design, but those features should be enabled deliberately rather than by publishing every documented port.

The classroom does not run the Compose project because creating containers, networks, image layers, or runtime state would mutate locations outside the permitted lab directory. Instead, it builds an installation bundle, validates its structure, and records the production checks that must precede activation. In production, select a reviewed image tag, protect the configuration directory, keep enrollment credentials outside version control, and verify local playback before considering remote exposure. Hardware transcoding is an optional later enhancement because device passthrough, driver compatibility, Plex account requirements, and platform-specific permissions add complexity that should not be mixed into the initial installation.

## Architecture

### diagram
Client devices -> TCP 32400 -> Plex container -> /config, /transcode, and read-only /media mounts

### components
### name
Plex service

### role
Indexes libraries, serves the web interface, and streams media to clients.
### name
Configuration storage

### host_path
/opt/lab-classroom/class57/config

### container_path
/config

### access
read-write

### persistence
persistent and backed up
### name
Transcode storage

### host_path
/opt/lab-classroom/class57/transcode

### container_path
/transcode

### access
read-write

### persistence
temporary and reproducible
### name
Movie library

### host_path
/opt/lab-classroom/class57/media/movies

### container_path
/media/movies

### access
read-only

### persistence
source media
### name
Television library

### host_path
/opt/lab-classroom/class57/media/tv

### container_path
/media/tv

### access
read-only

### persistence
source media
### name
Music library

### host_path
/opt/lab-classroom/class57/media/music

### container_path
/media/music

### access
read-only

### persistence
source media

### design_decisions
Use bridge networking with an explicit TCP 32400 publication rather than unrestricted host networking.
Keep configuration, temporary transcode data, and source media in separate directories.
Mount source media read-only.
Do not store a Plex claim token in the Compose file.
Do not pass graphics devices into the initial deployment.
Do not start the staged project inside the classroom because the runtime would create state outside the allowed lab directory.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Extend the staged design without starting Plex.

### tasks
Add a read-only /media/home-videos bind mount rooted at /opt/lab-classroom/class57/media/home-videos.
Create three empty sample files demonstrating a consistent personal-video naming convention.
Write /opt/lab-classroom/class57/docs/backup-plan.txt describing configuration backup timing, retention, restore testing, and why transcode data is excluded.
Write /opt/lab-classroom/class57/docs/identity-plan.txt documenting the intended numeric UID, numeric GID, and required access for each mounted directory.
Update the validator so it confirms that all four media mounts are read-only and that no credential-like key appears in compose.yaml.

### submission_criteria
All submitted files remain under /opt/lab-classroom/class57/.
The design keeps media mounts read-only.
The backup plan distinguishes persistent application state from disposable cache data.
The identity plan uses numeric identities rather than relying only on account names.
No real credential, token, private media, or personally identifying filename is included.

## Feynman teach-back

### prompt
Explain the deployment to a new administrator without using the words container, volume, or permission.

### model_explanation
Plex needs one durable workspace for its catalog and settings, one disposable workspace for temporary conversions, and several source shelves containing movies, television, and music. Plex must be able to update its durable and temporary workspaces, but it only needs to read the source shelves. Clear filenames tell the scanner what each item is. Client devices contact Plex on its primary service port, and broader internet access is a separate decision.

### self_check
Can you explain why configuration data and transcode data have different backup requirements?
Can you explain why readable media is sufficient for normal scanning and playback?
Can you identify the naming information that distinguishes a television episode from a movie?
Can you explain why numeric identities matter even when account names look correct?
Can you describe why the classroom stages but does not start the service?

## Retrieval check

1. 1. Which Plex path usually contains the catalog, metadata, preferences, and watch state?
2. 2. Why should source media normally be mounted read-only inside the Plex service?
3. 3. What information should a television episode filename contain for reliable matching?
4. 4. What is the operational difference between Direct Play and transcoding?
5. 5. Why are matching usernames on the host and in a container insufficient to guarantee access?
6. 6. Which staged directory is normally safe to exclude from backups: config, transcode, or media?
7. 7. Why does this classroom lab not start the Compose project?
8. 8. Should a Plex claim token be stored permanently in compose.yaml?
9. 9. What port does the staged design publish for the primary Plex web and streaming service?
10. 10. Why should hardware transcoding be introduced as a separate change?

## Guided lab

### scope
Create and validate a Plex installation bundle entirely under /opt/lab-classroom/class57/. Do not launch the service.

### steps
### step
1

### title
Confirm the classroom root

### commands
test -d /opt/lab-classroom/class57/
test -w /opt/lab-classroom/class57/
python3 -c "from pathlib import Path; p=Path('/opt/lab-classroom/class57').resolve(); assert str(p) == '/opt/lab-classroom/class57', p; print(p)"

### notes
Stop if any check fails. Do not substitute another path because all lab mutations are restricted to this classroom root.
### step
2

### title
Create the storage layout

### commands
mkdir -p /opt/lab-classroom/class57/config /opt/lab-classroom/class57/transcode /opt/lab-classroom/class57/media/movies '/opt/lab-classroom/class57/media/tv' /opt/lab-classroom/class57/media/music /opt/lab-classroom/class57/docs

### notes
These directories represent separate data lifecycles even though they share one classroom root.
### step
3

### title
Create representative media names

### commands
mkdir -p '/opt/lab-classroom/class57/media/movies/Arrival (2016)'
mkdir -p '/opt/lab-classroom/class57/media/tv/The Expanse (2015)/Season 01'
touch '/opt/lab-classroom/class57/media/movies/Arrival (2016)/Arrival (2016).mkv'
touch '/opt/lab-classroom/class57/media/tv/The Expanse (2015)/Season 01/The Expanse (2015) - S01E01.mkv'

### notes
The zero-byte files are naming examples, not playable media and not benchmark inputs.
### step
4

### title
Write the staged Compose specification

### commands
python3 - <<'PY'
from pathlib import Path
root = Path('/opt/lab-classroom/class57').resolve()
assert str(root) == '/opt/lab-classroom/class57'
content = '''services:
  plex:
    image: plexinc/pms-docker:public
    container_name: class57-plex
    restart: unless-stopped
    environment:
      TZ: Etc/UTC
    ports:
      - "32400:32400/tcp"
    volumes:
      - type: bind
        source: /opt/lab-classroom/class57/config
        target: /config
      - type: bind
        source: /opt/lab-classroom/class57/transcode
        target: /transcode
      - type: bind
        source: /opt/lab-classroom/class57/media/movies
        target: /media/movies
        read_only: true
      - type: bind
        source: /opt/lab-classroom/class57/media/tv
        target: /media/tv
        read_only: true
      - type: bind
        source: /opt/lab-classroom/class57/media/music
        target: /media/music
        read_only: true
'''
(root / 'compose.yaml').write_text(content, encoding='utf-8')
PY

### notes
The public image channel is shown as a portable example. Before production activation, review the image publisher's current tag policy and choose an approved tag or digest according to local change-management requirements.
### step
5

### title
Write the deployment checklist

### commands
python3 - <<'PY'
from pathlib import Path
root = Path('/opt/lab-classroom/class57').resolve()
assert str(root) == '/opt/lab-classroom/class57'
text = '''Plex production activation checklist

1. Confirm the selected container image source and tag or digest.
2. Record the container UID and GID and test host path access with those numeric identities.
3. Confirm that /config and /transcode are writable by Plex.
4. Confirm that every /media mount is readable and not writable by Plex.
5. Back up /config before upgrades and restore tests.
6. Keep claim tokens and account credentials outside Compose and source control.
7. Confirm TCP 32400 is reachable only from intended networks.
8. Start locally, complete enrollment, create libraries, and test Direct Play.
9. Enable remote access only after local operation and account security are verified.
10. Add hardware transcoding only as a separately tested change.
'''
(root / 'docs' / 'deployment-checklist.txt').write_text(text, encoding='utf-8')
PY

### notes
This separates a safe staged design from production activation.
### step
6

### title
Run local structural validation

### commands
python3 - <<'PY'
from pathlib import Path
root = Path('/opt/lab-classroom/class57').resolve()
assert str(root) == '/opt/lab-classroom/class57'
required = [
    root / 'compose.yaml',
    root / 'config',
    root / 'transcode',
    root / 'media/movies',
    root / 'media/tv',
    root / 'media/music',
    root / 'docs/deployment-checklist.txt'
]
missing = [str(p) for p in required if not p.exists()]
assert not missing, f'Missing: {missing}'
compose = (root / 'compose.yaml').read_text(encoding='utf-8')
assert '32400:32400/tcp' in compose
assert compose.count('read_only: true') == 3
assert 'PLEX_CLAIM' not in compose
assert '/opt/lab-classroom/class57/' in compose
print('Class 57 bundle validation passed')
PY
find /opt/lab-classroom/class57/ -maxdepth 5 -print

### notes
If a Compose implementation is available, its configuration parser may additionally be used in a read-only validation workflow, but this lesson does not require or authorize starting the project.

## Expected results

- The directories config, transcode, media/movies, media/tv, media/music, and docs exist beneath /opt/lab-classroom/class57/.
- The staged compose.yaml publishes only TCP port 32400.
- The configuration and transcode mounts are read-write because Plex must update them.
- All three source-media mounts are marked read-only.
- The Compose file contains no Plex claim token or account credential.
- The sample movie and television paths use title, year, season, and episode naming conventions.
- The local validator prints Class 57 bundle validation passed.
- No Plex container, container network, image layer, host package, or service is created by the lab.

## Verification checkpoints

- [ ] Run: python3 -c "from pathlib import Path; p=Path('/opt/lab-classroom/class57').resolve(); assert str(p) == '/opt/lab-classroom/class57'; print('root verified')"
- [ ] Run: test -f /opt/lab-classroom/class57/compose.yaml && echo 'compose file present'
- [ ] Run: test -f /opt/lab-classroom/class57/docs/deployment-checklist.txt && echo 'checklist present'
- [ ] Run: grep -F '32400:32400/tcp' /opt/lab-classroom/class57/compose.yaml
- [ ] Run: test "$(grep -c 'read_only: true' /opt/lab-classroom/class57/compose.yaml)" -eq 3 && echo 'media mounts are read-only'
- [ ] Run: if grep -q 'PLEX_CLAIM' /opt/lab-classroom/class57/compose.yaml; then echo 'unexpected secret field'; exit 1; else echo 'no claim token field'; fi
- [ ] Run: test -f '/opt/lab-classroom/class57/media/movies/Arrival (2016)/Arrival (2016).mkv' && echo 'movie naming example present'
- [ ] Run: test -f '/opt/lab-classroom/class57/media/tv/The Expanse (2015)/Season 01/The Expanse (2015) - S01E01.mkv' && echo 'episode naming example present'

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The initial directory test fails. | The classroom root was not pre-created or the current user does not have access. | Have the lab administrator create and delegate /opt/lab-classroom/class57/. Do not redirect the exercise to another filesystem path. |
| The Python path assertion reports a different resolved location. | The classroom path is a symbolic link or resolves through an unexpected mount. | Stop the lab and ask the administrator to provide the required literal path. The assertion prevents accidental writes outside the authorized root. |
| The read-only mount count is not three. | A read_only property was omitted, duplicated, or indented under the wrong mount. | Compare the three media mount entries with the lesson specification. Each media entry must independently contain read_only: true. |
| A production Plex server can see directories but cannot scan media files. | The container's numeric user or group can traverse the directory tree but cannot read one or more files. | Inspect numeric ownership and permissions on every path component, then grant the dedicated Plex group the minimum read and traversal access required. |
| A production Plex container repeatedly fails while creating its database. | The configuration mount is read-only, owned by an incompatible numeric identity, or located on storage with unsuitable locking behavior. | Confirm that /config is a persistent read-write mount supported by the deployment platform and writable by the container identity. |
| A movie or episode appears under the wrong title. | The filename is ambiguous, the year is missing, or television season and episode numbers do not follow the expected pattern. | Rename the item according to current Plex naming guidance, rescan the library, and use manual matching only when correct naming remains ambiguous. |
| Playback triggers unexpected transcoding. | The client does not support the stored codec, container, bitrate, audio format, or subtitle mode, or the client quality setting is lower than the source. | Inspect the Plex playback dashboard, verify client quality settings, and compare the file's media characteristics with client capabilities before changing server resources. |
| A remote client cannot connect while local clients work. | Remote-access routing, address translation, port publication, or account configuration is incomplete. | Keep local service verified, then follow the official Plex remote-access troubleshooting sequence. Do not expose additional ports without understanding their purpose. |

## Security considerations

### principles
Run Plex with a dedicated, non-administrative identity and verify numeric UID and GID behavior.
Mount source media read-only unless a documented workflow absolutely requires writes.
Treat the configuration directory as sensitive because it contains server state and may contain tokens.
Never commit claim tokens, account credentials, or exported configuration archives to source control.
Restrict TCP 32400 exposure to intended networks until remote access is explicitly approved.
Use a strong unique Plex account password and enable multi-factor authentication where supported.
Review image provenance and update policy before deployment; test upgrades against a configuration backup.
Do not add graphics devices or other host devices until hardware transcoding is separately designed and tested.
Do not assume TLS on an upstream proxy automatically secures unencrypted internal paths, administrative access, or account credentials.
Keep Plex configuration backups protected because watch history, library metadata, server identity, and access-related state may be sensitive.

### secret_handling
If enrollment requires a short-lived claim token, supply it through a temporary secret-handling mechanism supported by the deployment environment. Remove it after enrollment, avoid shell history and committed files, and rotate or invalidate it if exposed.

### network_posture
Begin with local access on TCP 32400. Add discovery, companion, or remote-access behavior only when each required path and trust boundary is understood. Publishing fewer interfaces and ports reduces accidental exposure.

### backup_posture
Back up the configuration directory using an application-consistent procedure. Media backup policy depends on whether the source is replaceable. Transcode data is temporary and should generally be excluded.

## Rollback

### normal_state
The lab starts no service, so rollback does not require stopping Plex or removing container-runtime resources.

### preserve_option
Retain /opt/lab-classroom/class57/ as an auditable design artifact, or copy its non-secret text files to an approved classroom archive before cleanup.

### cleanup_command
python3 - <<'PY'
from pathlib import Path
import shutil
root = Path('/opt/lab-classroom/class57').resolve()
assert str(root) == '/opt/lab-classroom/class57'
for child in root.iterdir():
    if child.is_symlink() or child.is_file():
        child.unlink()
    elif child.is_dir():
        shutil.rmtree(child)
print('Class 57 contents removed; classroom root retained')
PY

### cleanup_effect
Deletes all lesson-created contents beneath the verified classroom root while retaining /opt/lab-classroom/class57/ itself.

### recovery
Rerun the lab steps to regenerate the staged files. The zero-byte media examples contain no recoverable media content.

## Video narration notes

Welcome to Class 57, Plex Installation and Library Design. In this lesson, installation means more than launching an image. We begin by deciding where Plex state lives, which data must survive a rebuild, and which access the service actually requires. The configuration directory stores the server database, metadata, preferences, and watch state, so it is persistent and should be protected by tested backups. The transcode directory is writable temporary space and is generally reproducible. The media roots contain source files and are mounted read-only so Plex can scan and stream them without receiving unnecessary modification rights.

Next, examine library structure. Movies receive a movie root and use title-and-year naming. Television receives a separate root with series, season, and episode identifiers. Music is isolated under its own root. Separating these types lets each Plex scanner interpret only the content it understands. Clear naming improves matching before manual corrections become necessary.

The Compose specification publishes TCP port 32400 and defines explicit host bind mounts. It does not contain a claim token. It does not request graphics devices. It also avoids enabling every optional discovery feature during the initial design. Before production activation, an administrator must select an approved image reference, identify the numeric user and group used by Plex, and test whether that identity can write configuration and transcode data while only reading media.

The classroom constraint is important: every mutation must remain under /opt/lab-classroom/class57/. Starting a container would create runtime state elsewhere, so this lab stages and validates the installation bundle without launching it. This is still meaningful operational work. A strong deployment review should be able to detect incorrect mounts, writable media, embedded secrets, missing backup plans, and unclear identity assumptions before a service is started. Finish by running the structural validator and explaining the design in plain language. If you can explain why each path exists, who may modify it, and whether it must be backed up, you understand the foundation of a maintainable Plex installation.

## References

- Plex Support: Naming and Organizing Your Movie Media Files — https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/
- Plex Support: Naming and Organizing Your TV Show Files — https://support.plex.tv/articles/naming-and-organizing-your-tv-show-files/
- Plex Support: Adding Music Media From Folders — https://support.plex.tv/articles/200265296-adding-music-media-from-folders/
- Plex Support: Remote Access — https://support.plex.tv/articles/200289506-remote-access/
- Plex Support: Troubleshooting Remote Access — https://support.plex.tv/articles/200931138-troubleshooting-remote-access/
- Plex Docker image repository — https://github.com/plexinc/pms-docker
- Docker documentation: Bind mounts — https://docs.docker.com/engine/storage/bind-mounts/
- Docker documentation: Compose file reference — https://docs.docker.com/reference/compose-file/
- Compose Specification — https://compose-spec.io/

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

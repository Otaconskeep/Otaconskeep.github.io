# Class 61: Bazarr and Subtitle Automation

**Learning objective:** Describe Bazarr's role in a media automation architecture; Explain how Bazarr discovers series and movies through Sonarr and Radarr; Distinguish media-manager API access from filesystem access; Design volume mappings that keep Bazarr's internal and external paths consistent; Explain language profiles, forced subtitles, hearing-impaired subtitles, and subtitle scoring; Prepare a loopback-bound Docker Compose manifest with explicit media paths; Validate a proposed Bazarr deployment before starting any container; Identify security and reliability risks associated with API keys, writable media mounts, and subtitle providers
**Bloom level:** Understand / Apply
**Track:** Media Automation · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Explain how Bazarr integrates with Sonarr, Radarr, media storage, and subtitle providers, then build and validate a least-privilege deployment manifest without starting containers or changing an existing media stack.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux hosts capable of running Python 3
Linux hosts with Docker Compose v2 for optional manifest validation

### bazarr
The architectural concepts apply to current Bazarr releases that integrate with Sonarr and Radarr. Interface labels and provider options can vary by release.

### sonarr_radarr
Use supported Sonarr and Radarr releases with API access enabled. Exact settings locations may differ across application versions.

### container_runtime
The required lab validation uses Python 3 and does not require a running container engine. The optional Compose syntax check expects Docker Compose v2.

### image_policy
The staged manifest uses a floating image reference for syntax demonstration only and does not pull it. Production deployments should use a locally reviewed and tested version or immutable digest.

### storage
Production media storage must support the ownership, permissions, filenames, and sidecar subtitle behavior expected by Bazarr and the selected media players.

## Learning objective

- Describe Bazarr's role in a media automation architecture
- Explain how Bazarr discovers series and movies through Sonarr and Radarr
- Distinguish media-manager API access from filesystem access
- Design volume mappings that keep Bazarr's internal and external paths consistent
- Explain language profiles, forced subtitles, hearing-impaired subtitles, and subtitle scoring
- Prepare a loopback-bound Docker Compose manifest with explicit media paths
- Validate a proposed Bazarr deployment before starting any container
- Identify security and reliability risks associated with API keys, writable media mounts, and subtitle providers

## Why this matters

Explain how Bazarr integrates with Sonarr, Radarr, media storage, and subtitle providers, then build and validate a least-privilege deployment manifest without starting containers or changing an existing media stack.

## Prerequisites

- Basic familiarity with Docker Compose syntax
- A conceptual understanding of Sonarr and Radarr libraries
- Comfort with Linux paths, file ownership, and environment variables
- Python 3 for the local validation exercise
- Write access to /opt/lab-classroom/class61/

## Required reading

- Bazarr documentation: https://wiki.bazarr.media/
- Bazarr setup documentation: https://wiki.bazarr.media/Getting-Started/Setup-Guide/
- Docker Compose file reference: https://docs.docker.com/reference/compose-file/
- Sonarr FAQ and documentation: https://wiki.servarr.com/sonarr
- Radarr FAQ and documentation: https://wiki.servarr.com/radarr

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Bazarr | A companion application for Sonarr and Radarr that searches for, downloads, upgrades, and manages subtitle files. |
| Language profile | A policy describing which subtitle languages and variants are wanted for a movie or series. |
| Forced subtitle | A subtitle track intended mainly for foreign-language or otherwise untranslated dialogue within predominantly different-language content. |
| Hearing-impaired subtitle | A subtitle variant that can include speaker labels, sound descriptions, and other accessibility cues. |
| Provider | An external subtitle source queried by Bazarr, often requiring credentials, rate-limit awareness, or account-specific configuration. |
| Subtitle score | Bazarr's assessment of how well a candidate subtitle matches the requested title, release, language, episode, and other preferences. |
| Path mapping | A translation used when Bazarr and a media manager refer to the same files through different filesystem paths. |
| Embedded subtitle | A subtitle stream stored inside a media container rather than as a separate sidecar file. |
| Sidecar subtitle | A separate subtitle file, such as an SRT file, stored alongside its corresponding media file. |
| API key | A secret token used by Bazarr to authenticate requests to Sonarr or Radarr. |

## Instruction

Bazarr does not replace Sonarr or Radarr. Sonarr remains responsible for series and episode records, while Radarr remains responsible for movie records. Bazarr connects to their APIs, learns what titles are monitored, receives the file paths those applications know about, and then evaluates subtitle requirements against configured language profiles. It also needs filesystem access to the same media files. These are two separate dependencies: an API connection supplies metadata and monitoring state, while a media mount supplies access to inspect media and write sidecar subtitles.

Path consistency is one of the most important design concerns. If Radarr reports a movie at /movies/Example/Example.mkv, Bazarr must be able to find that file at the reported path or translate it with an intentional path mapping. Using matching container paths across the media stack is generally easier to reason about than adding translations. A mapping can solve a legitimate difference, but it can also hide a poor storage design and make troubleshooting harder.

Bazarr normally writes subtitle files next to media, so a read-only media mount supports inspection but prevents complete automation. Production write access should therefore be narrow rather than broad: run Bazarr as a dedicated unprivileged identity and grant that identity only the permissions required for relevant movie and series directories. Do not grant access to unrelated storage. Existing media ownership and group strategy should be understood before enabling writes.

Language profiles express intent. A household may require one language for all titles, prefer another language when available, request forced subtitles, or choose hearing-impaired variants. Profiles should be tested on a small library subset before broad assignment. Provider limits and authentication also matter. Aggressive searches can cause throttling or account restrictions, and a poorly matched result may have incorrect timing or release characteristics. Bazarr's scoring, minimum score, upgrade behavior, and provider selection should be treated as quality controls rather than bypassed merely to obtain any result.

The safest rollout is staged. First validate networking, paths, ownership, and API reachability. Next connect Sonarr and Radarr and confirm that their libraries appear without launching a broad search. Then configure one provider and one language profile. Test a small number of known titles, inspect the resulting filenames and timing, and only then enable scheduled searches or upgrades. Back up Bazarr's configuration before major profile, provider, or path changes. This class stages and validates a deployment definition but deliberately does not start a container, pull an image, contact subtitle providers, or modify an existing media library.

## Architecture

### components
### name
Bazarr

### role
Evaluates subtitle requirements, queries configured providers, and manages sidecar subtitle files.
### name
Sonarr

### role
Supplies series, episode, monitoring, and media-file metadata through its API.
### name
Radarr

### role
Supplies movie, monitoring, and media-file metadata through its API.
### name
Media storage

### role
Contains movie and series files and, when authorized, the subtitle sidecar files written by Bazarr.
### name
Subtitle providers

### role
Supply subtitle candidates subject to provider credentials, policies, availability, and rate limits.
### name
Administrator browser

### role
Accesses the Bazarr web interface through a trusted local path or an authenticated reverse proxy.

### data_flows
Bazarr uses a Sonarr API key to retrieve monitored series, episodes, and file paths.
Bazarr uses a Radarr API key to retrieve monitored movies and file paths.
Bazarr reads media metadata and writes approved sidecar subtitles through mounted media paths.
Bazarr queries explicitly enabled subtitle providers and records search and download outcomes.
The administrator configures providers, language profiles, scoring, and media-manager connections through the web interface.

### lab_boundary
All files created or modified by this lab remain under /opt/lab-classroom/class61/. The lab does not start Bazarr, create containers, pull images, alter an existing media library, or contact external subtitle services.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Draw the API and filesystem data flows among Bazarr, Sonarr, Radarr, media storage, and subtitle providers.
Write a language-profile policy for a multilingual household, including forced and hearing-impaired preferences.
Describe when a Bazarr path mapping is justified and when matching container paths would be simpler.
Create a credential-rotation checklist for Sonarr and Radarr API keys without recording any real secret.
Propose a staged rollout for a large library that limits provider traffic and allows subtitle-quality review.
Research how the media players used in your homelab name and select language-tagged sidecar subtitles.

## Feynman teach-back

Explain Bazarr to a peer as a subtitle librarian that depends on two kinds of access. Sonarr and Radarr tell it which movies and episodes exist, which are monitored, and where their files should be. Filesystem mounts let it inspect those files and place matching subtitle sidecars beside them. If the API works but the paths do not match, Bazarr knows about a title but cannot reach its file. If the paths work but permissions are read-only, Bazarr can inspect the library but cannot save subtitles. Language profiles define what the household wants, providers offer candidates, and scoring helps avoid weak matches. A safe rollout begins with narrow permissions, consistent paths, one profile, one provider, and a small test set.

## Retrieval check

1. 1. What two kinds of access does Bazarr normally need from a media automation environment?
2. 2. Why can Bazarr list a movie successfully yet still report that its media file is missing?
3. 3. Why is a read-only media mount insufficient for full sidecar subtitle automation?
4. 4. What is the purpose of a Bazarr language profile?
5. 5. What problem does a path mapping solve?
6. 6. Why is binding the Bazarr port to 127.0.0.1 safer than publishing it on every host interface?
7. 7. Why should broad library searches be delayed during initial deployment?
8. 8. What is the difference between forced subtitles and hearing-impaired subtitles?
9. 9. Which secrets should not be embedded in a shared Compose file?
10. 10. Did this lesson start a Bazarr container or contact a subtitle provider?

## Guided lab

### title
Stage and validate a Bazarr Compose definition

### objective
Create a local deployment manifest, safe fixture directories, and a validation report while keeping every lab mutation inside the class directory.

### steps
### step
1

### instruction
Create the isolated class directory structure.

### command
install -d /opt/lab-classroom/class61/config /opt/lab-classroom/class61/media/movies /opt/lab-classroom/class61/media/tv /opt/lab-classroom/class61/artifacts
### step
2

### instruction
Record the current numeric user and group identifiers for the staged container configuration.

### command
printf 'PUID=%s\nPGID=%s\nTZ=Etc/UTC\n' "$(id -u)" "$(id -g)" > /opt/lab-classroom/class61/.env
### step
3

### instruction
Create the Compose definition. It binds the web interface to loopback, avoids privileged mode and host networking, and maps only class fixture directories.

### command
cat > /opt/lab-classroom/class61/compose.yml <<'EOF'
services:
  bazarr:
    image: lscr.io/linuxserver/bazarr:latest
    container_name: class61-bazarr
    environment:
      PUID: ${PUID}
      PGID: ${PGID}
      TZ: ${TZ}
    ports:
      - "127.0.0.1:6767:6767"
    volumes:
      - /opt/lab-classroom/class61/config:/config
      - /opt/lab-classroom/class61/media/movies:/movies
      - /opt/lab-classroom/class61/media/tv:/tv
    restart: unless-stopped
EOF
### step
4

### instruction
Create an explicit inventory fixture. These are descriptive records, not playable media files.

### command
cat > /opt/lab-classroom/class61/artifacts/media-inventory.json <<'EOF'
{
  "movies": [
    {
      "title": "Training Movie",
      "manager_path": "/movies/Training Movie/Training Movie.mkv",
      "desired_languages": ["en"],
      "existing_sidecars": []
    }
  ],
  "episodes": [
    {
      "series": "Training Series",
      "episode": "S01E01",
      "manager_path": "/tv/Training Series/Season 01/Training Series - S01E01.mkv",
      "desired_languages": ["en"],
      "existing_sidecars": ["Training Series - S01E01.en.srt"]
    }
  ]
}
EOF
### step
5

### instruction
Create a validator that checks the staged manifest for required path, port, identity, and privilege controls.

### command
cat > /opt/lab-classroom/class61/validate.py <<'PY'
from pathlib import Path
import json

root = Path('/opt/lab-classroom/class61')
compose_path = root / 'compose.yml'
env_path = root / '.env'
inventory_path = root / 'artifacts' / 'media-inventory.json'

compose = compose_path.read_text(encoding='utf-8')
env_lines = env_path.read_text(encoding='utf-8').splitlines()
env = dict(line.split('=', 1) for line in env_lines if '=' in line)
inventory = json.loads(inventory_path.read_text(encoding='utf-8'))

checks = {
    'loopback_port_binding': '127.0.0.1:6767:6767' in compose,
    'config_path_scoped': '/opt/lab-classroom/class61/config:/config' in compose,
    'movie_path_scoped': '/opt/lab-classroom/class61/media/movies:/movies' in compose,
    'tv_path_scoped': '/opt/lab-classroom/class61/media/tv:/tv' in compose,
    'puid_present': env.get('PUID', '').isdigit(),
    'pgid_present': env.get('PGID', '').isdigit(),
    'timezone_present': bool(env.get('TZ')),
    'not_privileged': 'privileged: true' not in compose.lower(),
    'no_host_network': 'network_mode: host' not in compose.lower(),
    'inventory_has_movie': len(inventory.get('movies', [])) == 1,
    'inventory_has_episode': len(inventory.get('episodes', [])) == 1
}

report = {
    'status': 'PASS' if all(checks.values()) else 'FAIL',
    'checks': checks,
    'containers_started': False,
    'external_services_contacted': False
}
output = root / 'artifacts' / 'validation-report.json'
output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['status'] == 'PASS' else 1)
PY
python3 /opt/lab-classroom/class61/validate.py
### step
6

### instruction
If Docker Compose is installed, render and validate the Compose model without starting a service. If it is not installed, retain the Python validation result.

### command
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then docker compose --env-file /opt/lab-classroom/class61/.env -f /opt/lab-classroom/class61/compose.yml config --quiet; else printf '%s\n' 'Docker Compose unavailable; Python validation remains authoritative for this isolated lab.'; fi
### step
7

### instruction
Save known-good copies that can be used to reverse later edits during the exercise.

### command
cp /opt/lab-classroom/class61/compose.yml /opt/lab-classroom/class61/artifacts/compose.known-good.yml && cp /opt/lab-classroom/class61/.env /opt/lab-classroom/class61/artifacts/env.known-good
### step
8

### instruction
Review the generated validation report and confirm that no container was started.

### command
cat /opt/lab-classroom/class61/artifacts/validation-report.json

### production_follow_up
Pin the container image to a version or immutable digest tested in the local environment rather than accepting unreviewed changes indefinitely.
Back up the Bazarr configuration before upgrades or broad profile changes.
Confirm that Bazarr, Sonarr, and Radarr use consistent container paths or document each required path mapping.
Use dedicated Sonarr and Radarr API keys and protect them as secrets.
Test one language profile and a small title set before enabling scheduled searches for a full library.
Verify media ownership and group permissions before granting Bazarr write access.
Place remote access behind authenticated HTTPS rather than exposing the application port directly.

## Expected results

- /opt/lab-classroom/class61/compose.yml exists and describes one Bazarr service.
- /opt/lab-classroom/class61/.env contains numeric PUID and PGID values plus a timezone.
- The proposed web port is bound to 127.0.0.1 rather than all host interfaces.
- Every host-side volume in the staged manifest is located under /opt/lab-classroom/class61/.
- The validation report has a top-level status of PASS.
- The validation report states that no containers were started and no external services were contacted.
- The inventory demonstrates that one title lacks an English sidecar while another already records one.
- Known-good copies of the Compose and environment files exist under the artifacts directory.

## Verification checkpoints

- [ ] Run `python3 /opt/lab-classroom/class61/validate.py`; it should exit successfully and print a report with status PASS.
- [ ] Run `python3 -m json.tool /opt/lab-classroom/class61/artifacts/validation-report.json`; it should print valid JSON without an error.
- [ ] Run `grep -F '127.0.0.1:6767:6767' /opt/lab-classroom/class61/compose.yml`; it should display the loopback-bound port line.
- [ ] Run `grep -F '/opt/lab-classroom/class61/media/movies:/movies' /opt/lab-classroom/class61/compose.yml`; it should display the movie mapping.
- [ ] Run `grep -F '/opt/lab-classroom/class61/media/tv:/tv' /opt/lab-classroom/class61/compose.yml`; it should display the series mapping.
- [ ] Run `grep -E '^(PUID|PGID)=[0-9]+$' /opt/lab-classroom/class61/.env`; it should return both identity lines.
- [ ] Run `test -f /opt/lab-classroom/class61/artifacts/compose.known-good.yml && test -f /opt/lab-classroom/class61/artifacts/env.known-good`; it should exit with status zero.
- [ ] If Docker Compose is installed, run `docker compose --env-file /opt/lab-classroom/class61/.env -f /opt/lab-classroom/class61/compose.yml config --quiet`; it should return without starting a container.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Creating the class directories reports permission denied. | The current account does not have write access to /opt/lab-classroom/. | Have the lab administrator pre-create /opt/lab-classroom/class61/ with ownership assigned to the student account. Do not redirect the exercise into an existing Bazarr configuration directory. |
| The validator reports that PUID or PGID is missing. | The environment file was not created, was edited incorrectly, or contains nonnumeric identity values. | Repeat the environment-file creation step using `id -u` and `id -g`, then rerun the validator. |
| Docker Compose reports an unresolved PUID, PGID, or TZ variable. | The Compose validation command was run without the class environment file. | Include `--env-file /opt/lab-classroom/class61/.env` in the validation command. |
| The validator reports that a media path is not scoped correctly. | A host-side volume path was changed to an existing production location or to a relative path. | Restore the known-good Compose file from the artifacts directory and rerun validation. |
| A future Bazarr deployment can list titles but reports that media files do not exist. | Sonarr or Radarr reports paths that do not exist inside the Bazarr container. | Align container media paths across the applications or configure an intentional Bazarr path mapping after documenting both path forms. |
| A future Bazarr deployment finds subtitles but cannot save them. | The media mount is read-only, the Bazarr identity lacks directory write permission, or ownership does not match the configured PUID and PGID. | Inspect the exact destination directory and grant the dedicated Bazarr identity only the required group-based write access. Avoid broad permission changes. |
| Downloaded subtitles do not match dialogue timing. | The selected candidate targets a different release, cut, frame rate, or source. | Review provider selection, candidate score, release matching, minimum score, and upgrade settings. Test changes against a small title set. |
| A provider rejects requests or temporarily stops returning results. | Credentials are invalid, the provider is unavailable, or account and rate limits were exceeded. | Check the provider-specific status and Bazarr logs, verify credentials without exposing them, and reduce search frequency rather than repeatedly retrying. |

## Security considerations

### principles
Treat Sonarr, Radarr, and subtitle-provider credentials as secrets.
Bind the direct application port to loopback unless a documented network policy requires otherwise.
Use authenticated HTTPS through a trusted reverse proxy for remote access.
Run Bazarr as an unprivileged dedicated identity with no access to unrelated files.
Grant media write access only where sidecar subtitles must be stored.
Avoid privileged containers, host networking, host device mappings, and broad host filesystem mounts.
Back up configuration before upgrades because provider, profile, and database state reside in the configuration volume.
Review subtitle files as untrusted downloaded content and keep media clients updated.

### credential_handling
Do not commit API keys, provider passwords, cookies, or tokens into Compose files or shared lesson artifacts. Enter them through the protected application interface or an approved secret-management mechanism. Redact credentials from logs and screenshots.

### network_exposure
The staged manifest publishes Bazarr only on 127.0.0.1:6767. This allows same-host administration or reverse-proxy access without directly listening on every host interface.

### filesystem_access
Bazarr generally requires write access to media directories to create and upgrade sidecar subtitles. Use a dedicated group and verify directory-level access instead of granting unrestricted host access.

### supply_chain
The lesson uses a readable image reference only to demonstrate structure and does not pull it. A production operator should select a reviewed release and pin the tested image version or immutable digest according to local update policy.

## Rollback

### scope
No container or external service is started by this lesson. Rollback therefore consists of restoring the staged files within the class directory.

### commands
cp /opt/lab-classroom/class61/artifacts/compose.known-good.yml /opt/lab-classroom/class61/compose.yml
cp /opt/lab-classroom/class61/artifacts/env.known-good /opt/lab-classroom/class61/.env
python3 /opt/lab-classroom/class61/validate.py

### confirmation
The final validator run should return status PASS. The report should continue to state that no container was started and no external service was contacted.

## Video narration notes

Welcome to Class 61, Bazarr and Subtitle Automation. Bazarr is a companion to Sonarr and Radarr rather than a replacement for either application. Sonarr and Radarr remain the systems of record for monitored series, episodes, movies, and media-file locations. Bazarr reads that information through their APIs and evaluates it against subtitle language profiles.

There is a second dependency that is just as important as API connectivity: filesystem access. Knowing that a movie exists does not mean Bazarr can reach its file. The path reported by Radarr must be valid inside Bazarr, or an intentional path mapping must translate it. Consistent container paths are normally the simplest design. Bazarr also needs carefully scoped write permission when it is expected to create sidecar subtitle files next to media.

In this lab we stage a Compose definition under the isolated class directory. We bind port 6767 to loopback, provide an unprivileged numeric identity, and map only fixture directories under the lab root. We do not start a container, pull an image, contact a provider, or modify an existing media library. A Python validator checks the intended controls and writes a machine-readable report.

For a production rollout, proceed gradually. Confirm Sonarr and Radarr connectivity, verify path consistency, create one language profile, enable one provider, and test a few known titles. Review subtitle timing, language tags, forced and hearing-impaired behavior, and filename compatibility with your media players. Only after those checks should scheduled searches or broad profile assignments be enabled. Keep credentials secret, use authenticated HTTPS for remote access, maintain configuration backups, respect provider limits, and grant Bazarr only the filesystem permissions it actually requires.

## References

- Bazarr documentation: https://wiki.bazarr.media/
- Bazarr setup guide: https://wiki.bazarr.media/Getting-Started/Setup-Guide/
- Bazarr troubleshooting documentation: https://wiki.bazarr.media/Troubleshooting/
- LinuxServer.io Bazarr image documentation: https://docs.linuxserver.io/images/docker-bazarr/
- Docker Compose file reference: https://docs.docker.com/reference/compose-file/
- Docker bind mount documentation: https://docs.docker.com/engine/storage/bind-mounts/
- Sonarr documentation: https://wiki.servarr.com/sonarr
- Radarr documentation: https://wiki.servarr.com/radarr

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

# Lab: Bazarr and Subtitle Automation

**Module:** Requests & Media Servers
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Describe Bazarr's role in a media automation architecture

## Before you start

- Basic familiarity with Docker Compose syntax
- A conceptual understanding of Sonarr and Radarr libraries
- Comfort with Linux paths, file ownership, and environment variables
- Python 3 for the local validation exercise
- Write access to /opt/lab-classroom/class61/

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

## Verification

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

## Security

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

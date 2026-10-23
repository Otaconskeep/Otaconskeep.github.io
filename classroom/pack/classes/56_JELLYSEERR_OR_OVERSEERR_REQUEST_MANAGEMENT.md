# Class 56: Jellyseerr or Overseerr Request Management

**Learning objective:** Explain the role of Jellyseerr or Overseerr between users, a media server, and download automation; Identify the metadata API, media-server connection, and user synchronization dependencies that can block first-run setup; Differentiate request-manager availability synchronization from a media-server library scan; Create and validate a loopback-bound Docker Compose definition; Detect and repair an intentionally unsafe request policy; Apply least-privilege roles, manual approval, request limits, and environment-based secret sourcing; Verify both expected validation failure and successful policy remediation; Remove all class artifacts with an exact, verifiable rollback procedure
**Bloom level:** Understand / Apply
**Track:** Media Services and Automation · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach learners how to design, validate, and safely operate a media request-management service using Jellyseerr or Overseerr. The class emphasizes first-run dependencies, least-privilege request policy, media-server user synchronization, request approval, availability synchronization, Docker Compose validation, secret handling, and the distinction between detecting available media and initiating a library scan.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### platforms
Jellyseerr deployments using the official project container image
Overseerr deployments with equivalent request, role, media-server, and metadata concepts
Linux classroom systems with Python 3
Docker Compose v2 for optional Compose rendering

### notes
Jellyseerr and Overseerr interfaces and integration labels may differ, but the least-privilege and synchronization principles remain applicable.
The classroom uses a floating image reference only for syntax validation and does not pull or start it. Production operators should select and test a reviewed release or digest.
The policy JSON and validator are classroom artifacts, not native Jellyseerr or Overseerr import formats.
A real TMDB credential is intentionally excluded from the lab.
If Docker Compose is unavailable, the policy exercise remains valid, but Compose verification must be recorded as not executed.

## Learning objective

- Explain the role of Jellyseerr or Overseerr between users, a media server, and download automation
- Identify the metadata API, media-server connection, and user synchronization dependencies that can block first-run setup
- Differentiate request-manager availability synchronization from a media-server library scan
- Create and validate a loopback-bound Docker Compose definition
- Detect and repair an intentionally unsafe request policy
- Apply least-privilege roles, manual approval, request limits, and environment-based secret sourcing
- Verify both expected validation failure and successful policy remediation
- Remove all class artifacts with an exact, verifiable rollback procedure

## Why this matters

Teach learners how to design, validate, and safely operate a media request-management service using Jellyseerr or Overseerr. The class emphasizes first-run dependencies, least-privilege request policy, media-server user synchronization, request approval, availability synchronization, Docker Compose validation, secret handling, and the distinction between detecting available media and initiating a library scan.

## Prerequisites

- Basic familiarity with Docker containers and YAML
- A Linux host or classroom environment with Python 3
- Docker Compose v2 is recommended for Compose validation
- General understanding of a Plex or Jellyfin media library
- Permission to create files under /opt/lab-classroom/class56/
- No production media-server, download-client, or request-manager credentials are required for this lab

## Required reading

- Docker Docs: Compose file reference — https://docs.docker.com/reference/compose-file/
- Docker Docs: Interpolation and environment variables in Compose — https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
- Jellyseerr documentation — https://docs.jellyseerr.dev/
- Jellyseerr GitHub repository — https://github.com/Fallenbagel/jellyseerr
- Overseerr documentation — https://docs.overseerr.dev/
- The Movie Database API documentation — https://developer.themoviedb.org/docs/getting-started

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Request manager | A service that accepts user searches and media requests, applies approval and quota policy, and forwards approved requests to automation services. |
| TMDB | The Movie Database, a metadata provider commonly used by request managers for titles, artwork, release information, and search results. Initial setup requires a valid API credential or supported application authentication flow. |
| User synchronization | Importing or matching media-server users in the request manager so that request roles and permissions can be assigned to recognized identities. |
| Availability synchronization | Updating the request manager's view of which titles already exist in the media server. This does not inherently force the media server to scan storage. |
| Library scan | A media-server operation that examines configured library paths to discover, update, or remove media records. |
| Manual approval | A policy requiring an authorized operator to approve a request before it is sent to downstream automation. |
| Least privilege | Granting each user only the permissions needed for their role instead of assigning administrator access by default. |
| Compose interpolation | Docker Compose substitution of values such as image references and time zones from environment variables. |
| Webhook | An outbound HTTP callback used for notifications or integration events; webhook URLs frequently contain secret tokens and must be protected. |

## Instruction

Jellyseerr and Overseerr provide a user-facing request layer rather than replacing a media server or download automation. A typical request begins with a metadata search, passes through authorization and approval policy, and is then sent to an appropriate movie or television automation service. The request manager also queries the media server so that users do not request content that is already available. Several first-run dependencies are easy to overlook. Metadata search normally depends on TMDB access, so an absent, invalid, restricted, or improperly stored API credential can prevent useful searches even when the web interface itself loads. The credential must be obtained through the provider's legitimate process and should be supplied through the application's supported secret mechanism rather than committed to a Compose file or repository.

The media-server connection is a separate dependency. An administrator must provide the correct server URL, authentication material, and library selections. If media-server users are synchronized, imported users must still be mapped to deliberate request-manager roles. Synchronization proves identity association; it does not justify assigning administrator privileges. A safe default is a requester role with bounded request limits, while administrative and approval rights are assigned only to designated operators. Existing users should be reviewed after every synchronization because renamed, removed, or newly imported accounts may not inherit the intended policy.

Availability synchronization and library scanning are related but distinct. Availability synchronization asks the media server what it currently knows and marks matching titles as available in the request manager. A library scan tells the media server to inspect storage. Marking an item available cannot discover an unscanned file, and repeatedly triggering scans from the request layer can create unnecessary work or obscure ownership of the ingest workflow. Download automation, file import, media-server scanning, and request-manager availability refresh should therefore be treated as separate stages with separate logs.

Docker Compose documents the container image, environment, bind address, restart behavior, and persistent configuration path. In this lab, Compose interpolation supplies a real time zone and image reference from an environment file. The published port binds to 127.0.0.1, which avoids exposing the demonstration service on every network interface. The lab validates the Compose model but does not start the container or connect to production systems. Production deployments should pin a reviewed version or digest, protect the configuration directory, place remote access behind authenticated TLS, and back up application state before upgrades.

The policy exercise begins in an intentionally unsafe state: requests are automatically approved, the default role is administrative, limits are disabled, user synchronization is off, the metadata credential source is absent, inline secrets are allowed, and availability updates are incorrectly treated as scan triggers. The validator must reject that state. The learner then repairs the policy by interpreting requirements rather than pasting a golden file. A passing result demonstrates that the configured controls satisfy the validator, not that the entire production service is secure. Real deployment also requires application-level testing, authentication review, notification testing, downstream permission checks, and recovery planning.

## Architecture

### components
### name
Requesting user

### responsibility
Searches metadata, submits requests, and observes request or availability status without receiving administrative access.
### name
Jellyseerr or Overseerr

### responsibility
Authenticates users, applies roles and request limits, manages approval state, queries metadata, and coordinates downstream requests.
### name
TMDB metadata service

### responsibility
Provides searchable title metadata and artwork through an authorized API integration.
### name
Plex or Jellyfin media server

### responsibility
Maintains libraries and user identities and reports media already known to the server.
### name
Movie and television automation

### responsibility
Accepts approved requests and manages acquisition and import according to its own quality and path policies.
### name
Download client

### responsibility
Performs transfers requested by authorized automation services; it should not be exposed directly to ordinary request users.
### name
Notification service

### responsibility
Receives optional status events through protected webhook or provider credentials.
### name
Reverse proxy or secure access layer

### responsibility
Provides TLS, controlled remote access, and optionally additional authentication or access restrictions.

### request_flow
The user authenticates to the request manager.
The request manager searches TMDB using its configured metadata integration.
The request manager checks its synchronized view of media-server availability.
Request policy determines whether the request is denied, queued for approval, or approved.
An approved request is sent to the appropriate automation service.
Automation acquires and imports the media through its configured download workflow.
The media server scans or refreshes its library through the ingest workflow.
The request manager later synchronizes availability from the media server.

### trust_boundaries
User browser to request-manager web interface
Request manager to external metadata provider
Request manager to media-server API
Request manager to automation APIs
Request manager to notification endpoints
Reverse proxy to the loopback-bound application port

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### submission_location
/opt/lab-classroom/class56/homework.json

### instructions
Create a JSON document at the submission location. Do not include real hostnames, public addresses, usernames, API keys, tokens, webhook URLs, or other credentials. The document must parse as JSON and contain every required key shown in the schema.

### schema
### type
object

### required
class_id
chosen_platform
default_role
approval_mode
weekly_request_limit
tmdb_secret_source
user_sync_review
availability_explanation
compose_exposure
incident_response

### properties
### class_id
Integer equal to 56

### chosen_platform
String equal to jellyseerr or overseerr

### default_role
String equal to requester

### approval_mode
String equal to manual

### weekly_request_limit
Integer from 1 through 10

### tmdb_secret_source
String describing a supported environment or secret-manager source without including a credential

### user_sync_review
Array of at least three strings describing post-sync account checks

### availability_explanation
String explaining why availability synchronization is not a library scan

### compose_exposure
String describing the loopback binding and intended secure access path

### incident_response
Array of at least three ordered strings describing response to a leaked request-manager credential

### example_document
### class_id
56

### chosen_platform
jellyseerr

### default_role
requester

### approval_mode
manual

### weekly_request_limit
5

### tmdb_secret_source
An environment variable injected by the deployment secret mechanism

### user_sync_review
Confirm each imported identity belongs to a current media-server user
Confirm requester is the default role
Remove administrative or approval rights that lack an operational justification

### availability_explanation
Availability synchronization reads what the media server already knows; a library scan makes the media server inspect its configured storage paths.

### compose_exposure
The application listens through a host port bound to 127.0.0.1 and remote access is provided only through an authenticated TLS endpoint.

### incident_response
Revoke or rotate the exposed credential at its issuing service
Update the protected deployment secret and restart only the affected integration as required
Review access and application logs for unauthorized use

### grading_criteria
The file is valid JSON and contains all required keys.
class_id is 56 and chosen_platform is jellyseerr or overseerr.
The default role is requester and approval mode is manual.
The weekly limit is an integer from 1 through 10.
The TMDB secret source describes protected injection without disclosing a credential.
The user synchronization review contains at least three meaningful checks.
The availability explanation clearly separates synchronization from scanning.
The exposure statement includes loopback binding and a secure remote-access path.
The incident response includes revocation or rotation, protected redeployment, and log review.

## Feynman teach-back

### prompt
Explain the system to a household member who can request a movie but does not administer the server.

### model_explanation
The request manager is a front desk. It searches a catalog, checks whether the media server already knows about the title, and applies rules to the request. A normal user can ask for an item, but an operator approves it. After approval, automation may obtain and import it. The media server must then notice the imported file through its own library process. Only after that can the request manager synchronize and show the title as available. Giving the front desk an updated availability list is not the same as asking the media server to inspect all of its shelves.

### self_check
Can the learner explain why metadata search needs a separate provider integration?
Can the learner explain why synchronized users still need role review?
Can the learner distinguish an availability refresh from a library scan?
Can the learner explain why a loopback bind reduces exposure?
Can the learner describe why the intentionally unsafe policy must fail before remediation is accepted?

## Retrieval check

1. 1. Why can the Jellyseerr or Overseerr web interface load while metadata search still fails?
2. 2. What role should newly synchronized media-server users receive by default under least privilege?
3. 3. Does request-manager availability synchronization cause the media server to inspect its storage paths?
4. 4. Why does the lab bind port 5055 to 127.0.0.1 instead of every host interface?
5. 5. What result must the intentionally unsafe policy produce before the learner repairs it?
6. 6. Which production data must not be committed directly to the Compose file or homework submission?
7. 7. What does `docker compose config` demonstrate in this lab, and what does it not demonstrate?

## Guided lab

### scope
All created or modified filesystem content is confined to /opt/lab-classroom/class56/. The exercise does not start containers, contact TMDB, or modify a production service.

### steps
### step
1

### title
Create the isolated workspace

### instructions
Create directories for the Compose project and its future application configuration.

### commands
mkdir -p /opt/lab-classroom/class56/config
### step
2

### title
Create and inspect the Compose model

### instructions
Write the following content to /opt/lab-classroom/class56/compose.yaml. The loopback port prevents direct LAN exposure, and the persistent path remains inside the class workspace.

### file
/opt/lab-classroom/class56/compose.yaml

### content
services:
  jellyseerr:
    image: ${JELLYSEERR_IMAGE:?JELLYSEERR_IMAGE must be set}
    restart: unless-stopped
    environment:
      TZ: ${TZ:?TZ must be set}
      LOG_LEVEL: info
    ports:
      - "127.0.0.1:5055:5055"
    volumes:
      - /opt/lab-classroom/class56/config:/app/config

### step
3

### title
Provide non-secret Compose interpolation values

### instructions
Write the following content to /opt/lab-classroom/class56/.env.example. This file intentionally contains no TMDB, media-server, automation, or webhook credential.

### file
/opt/lab-classroom/class56/.env.example

### content
JELLYSEERR_IMAGE=ghcr.io/fallenbagel/jellyseerr:latest
TZ=Etc/UTC

### step
4

### title
Validate the Docker Compose definition

### instructions
If Docker Compose v2 is installed, render the effective model. This validates interpolation and YAML structure without starting a container. If Docker Compose is unavailable, record that limitation and manually inspect the bind address, volume path, image interpolation, and environment interpolation.

### commands
cd /opt/lab-classroom/class56 && docker compose --env-file .env.example config

### success_conditions
The rendered service uses the Jellyseerr image reference supplied by .env.example.
The published address is 127.0.0.1:5055 rather than an all-interface binding.
The only host volume path is /opt/lab-classroom/class56/config.
No credential appears in compose.yaml or .env.example.
### step
5

### title
Create the intentionally unsafe policy

### instructions
Write the following policy to /opt/lab-classroom/class56/request-policy.json. Do not repair it yet. It is intentionally unacceptable and exists to prove that the validator rejects unsafe settings.

### file
/opt/lab-classroom/class56/request-policy.json

### content
{
  "approval": {
    "manual_required": false,
    "auto_approve": true
  },
  "roles": {
    "default": "administrator",
    "synced_user_role": "administrator"
  },
  "limits": {
    "weekly_requests": 0
  },
  "integrations": {
    "tmdb": {
      "api_key_source": "missing"
    },
    "media_server": {
      "user_sync": false
    }
  },
  "availability": {
    "sync_marks_existing": true,
    "triggers_library_scan": true
  },
  "secrets_inline": true
}

### step
6

### title
Create the policy validator

### instructions
Write the following Python program to /opt/lab-classroom/class56/validate_policy.py. The validator reports every failed control and exits nonzero when any control fails.

### file
/opt/lab-classroom/class56/validate_policy.py

### content
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/lab-classroom/class56/request-policy.json")
try:
    policy = json.loads(path.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"FAIL: cannot parse {path}: {exc}")
    raise SystemExit(2)

checks = [
    (policy.get("approval", {}).get("manual_required") is True, "manual approval must be required"),
    (policy.get("approval", {}).get("auto_approve") is False, "automatic approval must be disabled"),
    (policy.get("roles", {}).get("default") == "requester", "default role must be requester"),
    (policy.get("roles", {}).get("synced_user_role") == "requester", "synchronized users must default to requester"),
    (isinstance(policy.get("limits", {}).get("weekly_requests"), int) and not isinstance(policy.get("limits", {}).get("weekly_requests"), bool) and 1 <= policy.get("limits", {}).get("weekly_requests") <= 10, "weekly request limit must be an integer from 1 through 10"),
    (policy.get("integrations", {}).get("tmdb", {}).get("api_key_source") == "env:TMDB_API_KEY", "TMDB credential source must be env:TMDB_API_KEY"),
    (policy.get("integrations", {}).get("media_server", {}).get("user_sync") is True, "media-server user synchronization must be enabled"),
    (policy.get("availability", {}).get("sync_marks_existing") is True, "availability synchronization must mark existing media"),
    (policy.get("availability", {}).get("triggers_library_scan") is False, "availability synchronization must not be treated as a library-scan trigger"),
    (policy.get("secrets_inline") is False, "inline secrets must be prohibited")
]

failures = [message for passed, message in checks if not passed]
if failures:
    for message in failures:
        print(f"FAIL: {message}")
    print(f"RESULT: rejected with {len(failures)} policy violation(s)")
    raise SystemExit(1)

print("PASS: policy satisfies all classroom controls")

### step
7

### title
Prove the unsafe policy fails

### instructions
Run the validator through a shell condition that treats rejection as the expected result. This is the required negative test.

### commands
cd /opt/lab-classroom/class56 && if python3 validate_policy.py request-policy.json; then echo 'UNEXPECTED: unsafe policy passed'; exit 1; else echo 'EXPECTED: unsafe policy was rejected'; fi

### success_conditions
The validator prints one or more FAIL lines.
The shell prints EXPECTED: unsafe policy was rejected.
The unsafe policy is not mistaken for a deployable configuration.
### step
8

### title
Repair the policy without copying a golden document

### instructions
Edit /opt/lab-classroom/class56/request-policy.json using an editor available in the classroom. Require manual approval, disable automatic approval, assign requester as both the default and synchronized-user role, choose an integer weekly request limit from 1 through 10, set the TMDB credential source to env:TMDB_API_KEY, enable media-server user synchronization, retain availability marking, disable library-scan triggering, and prohibit inline secrets. The range intentionally permits an operator policy decision rather than one fixed answer.

### required_controls
approval.manual_required is true
approval.auto_approve is false
roles.default is requester
roles.synced_user_role is requester
limits.weekly_requests is an integer from 1 through 10
integrations.tmdb.api_key_source is env:TMDB_API_KEY
integrations.media_server.user_sync is true
availability.sync_marks_existing is true
availability.triggers_library_scan is false
secrets_inline is false
### step
9

### title
Validate the repaired policy

### instructions
Run the validator again. Do not continue until it returns exit status zero.

### commands
cd /opt/lab-classroom/class56 && python3 validate_policy.py request-policy.json
cd /opt/lab-classroom/class56 && python3 -m json.tool request-policy.json >/dev/null

### success_conditions
The validator prints PASS: policy satisfies all classroom controls.
The JSON parser exits successfully.
No actual API credential has been written into the policy.
### step
10

### title
Review first-run operational gates

### instructions
Before any later deployment, document that a legitimate TMDB credential must be supplied through the supported secret mechanism, the media-server URL and token must be tested, synchronized users must be reviewed for role assignment, libraries must be selected, and availability synchronization must not be confused with the media server's scan operation. Do not place real credentials in the class directory.

## Expected results

- The workspace contains compose.yaml, .env.example, validate_policy.py, request-policy.json, and an empty or unused config directory.
- Docker Compose validation succeeds when Docker Compose v2 is available, while no Jellyseerr container is started.
- The initial unsafe policy produces a nonzero validator result and multiple explicit policy failures.
- The repaired policy parses as JSON and produces a zero validator result.
- The repaired policy uses requester roles, manual approval, a bounded weekly limit, media-server user synchronization, and environment-based TMDB credential sourcing.
- The repaired policy represents availability synchronization and library scanning as separate operations.
- No real TMDB, media-server, automation, download-client, or webhook credential is stored in the lab files.

## Verification checkpoints

- [ ] Run `test -d /opt/lab-classroom/class56/config && test -f /opt/lab-classroom/class56/compose.yaml && test -f /opt/lab-classroom/class56/.env.example && test -f /opt/lab-classroom/class56/validate_policy.py && test -f /opt/lab-classroom/class56/request-policy.json` and confirm exit status zero.
- [ ] Run `cd /opt/lab-classroom/class56 && docker compose --env-file .env.example config` when Docker Compose v2 is available; confirm that interpolation succeeds and the published port begins with 127.0.0.1.
- [ ] For the required negative check, temporarily copy the original unsafe policy content into `/opt/lab-classroom/class56/negative-test.json`, run `cd /opt/lab-classroom/class56 && python3 validate_policy.py negative-test.json`, and confirm a nonzero exit status before deleting only negative-test.json with `python3 -c "from pathlib import Path; Path('/opt/lab-classroom/class56/negative-test.json').unlink()"`.
- [ ] Run `cd /opt/lab-classroom/class56 && python3 validate_policy.py request-policy.json` and confirm the repaired policy prints PASS and exits zero.
- [ ] Run `grep -RniE 'api[_-]?key[[:space:]]*[:=][[:space:]]*[^[:space:]]+|token[[:space:]]*[:=][[:space:]]*[^[:space:]]+' /opt/lab-classroom/class56 --exclude=validate_policy.py` and manually investigate any match; the policy may name an environment source but must not contain a credential value.
- [ ] After performing rollback, run `test ! -e /opt/lab-classroom/class56 && echo 'ROLLBACK COMPLETE'` and confirm that ROLLBACK COMPLETE is printed.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Docker reports that the compose command is unknown. | Docker Compose v2 is not installed or the environment uses a different Compose invocation. | Record the missing dependency, perform the documented manual Compose inspection, and install or enable Docker Compose v2 through the platform's approved package-management process before deployment. |
| Compose reports that JELLYSEERR_IMAGE or TZ must be set. | The --env-file .env.example option was omitted, the command was run from another directory, or .env.example was not created correctly. | Run the command from /opt/lab-classroom/class56 with `docker compose --env-file .env.example config` and verify the two assignments in .env.example. |
| The unsafe policy unexpectedly passes. | The unsafe file was repaired before the negative test, the wrong file was validated, or the validator was altered. | Restore the intentionally unsafe content from Step 5, confirm the command names request-policy.json, and compare validate_policy.py with Step 6 before repeating the negative test. |
| The repaired policy still fails validation. | A Boolean was written as a quoted string, a key is misspelled, the request limit is outside the accepted range, or a required nested object is missing. | Run `python3 -m json.tool /opt/lab-classroom/class56/request-policy.json`, then compare each reported validator message with the required controls in Step 8. |
| Jellyseerr or Overseerr loads but metadata searches fail in a future deployment. | TMDB authentication is absent, invalid, restricted, or not visible to the application process. | Obtain a legitimate credential through TMDB, supply it using the application's supported secret mechanism, verify process access without printing the value, and retest metadata search. |
| Media-server users do not appear or receive unexpected permissions. | User synchronization is disabled, media-server authentication failed, or imported users inherited an unsuitable default role. | Test the media-server connection, enable synchronization, rerun synchronization, and review every imported account with requester as the safe default. |
| A downloaded file is not shown as available. | The file was not imported, the media server has not scanned the correct library path, or availability synchronization has not run after the media-server update. | Check the automation import first, then the media-server library scan and path mapping, and finally refresh request-manager availability. Do not assume availability synchronization scans storage. |
| The rollback verification still finds the class directory. | The rollback command was not executed, failed due to permissions, or targeted a different path. | Confirm the exact target is /opt/lab-classroom/class56, rerun the documented Python rollback command with appropriate authorized privileges, and repeat the absence test. |

## Security considerations

### controls
Bind the application port to 127.0.0.1 when access is intended to pass through a reverse proxy or secure tunnel.
Use TLS and authenticated access for any remote deployment.
Do not store TMDB, media-server, automation, download-client, or webhook credentials in Compose files, screenshots, source control, or homework submissions.
Assign requester as the default role for local and synchronized users.
Restrict approval and administrative rights to designated operators.
Apply bounded request limits to reduce accidental or abusive request volume.
Review imported users after synchronization and disable stale accounts.
Grant the request manager only the downstream API permissions it requires.
Treat webhook URLs as secrets because they may embed authentication tokens.
Back up application configuration before upgrades and pin a reviewed image version or digest for production instead of relying indefinitely on a floating tag.
Keep download clients and automation APIs off untrusted networks and do not expose them merely because the request interface is user-facing.
Review logs for request denials, approval changes, failed API authentication, synchronization failures, and unexpected administrator assignments.

### secret_handling
The classroom policy records only the source name env:TMDB_API_KEY. It does not require or permit a real credential in the class directory. Production operators should use the application's documented secret mechanism, a protected environment injection method, or an approved secret manager and should verify file permissions and backup handling.

### identity_note
Media-server user synchronization creates or associates request-manager identities, but authorization remains a separate decision. Newly synchronized users should not become administrators automatically.

## Rollback

### scope
Remove the complete class workspace and every artifact created by the lab. This does not affect a container because the lab never starts one.

### file_list
/opt/lab-classroom/class56/compose.yaml
/opt/lab-classroom/class56/.env.example
/opt/lab-classroom/class56/request-policy.json
/opt/lab-classroom/class56/validate_policy.py
/opt/lab-classroom/class56/negative-test.json if it remains from verification
/opt/lab-classroom/class56/homework.json if created
/opt/lab-classroom/class56/config/
/opt/lab-classroom/class56/

### precheck_commands
test -d /opt/lab-classroom/class56 && find /opt/lab-classroom/class56 -maxdepth 3 -print

### rollback_commands
python3 -c "import shutil; shutil.rmtree('/opt/lab-classroom/class56')"

### postcheck_commands
test ! -e /opt/lab-classroom/class56 && echo 'ROLLBACK COMPLETE'

### expected_postcheck
The postcheck prints ROLLBACK COMPLETE and returns exit status zero.

## Video narration notes

### estimated_minutes
12

### segments
### title
Role of the request manager

### narration
Jellyseerr and Overseerr sit between users and media automation. They provide search, request policy, approval, and status. They do not replace the media server, download client, or movie and television automation services.
### title
First-run blockers

### narration
A working web page is not a completed setup. Metadata search requires valid TMDB access. The media-server connection requires a reachable URL and valid authentication. User synchronization must run successfully, and imported identities must receive reviewed roles rather than automatic administrative access.
### title
Availability versus scanning

### narration
Availability synchronization asks the media server which titles it already knows. A library scan asks the media server to inspect storage. If an imported file has not been scanned, an availability refresh cannot discover it on its own.
### title
Compose safety

### narration
The class Compose file uses environment interpolation, persistent configuration beneath the class directory, and a loopback port binding. We validate the model without starting a service. A real deployment should use protected secrets, authenticated TLS access, backups, and a reviewed image version or digest.
### title
Negative test

### narration
The initial policy is intentionally unsafe. It automatically approves requests, assigns administrator roles, disables useful limits and synchronization, lacks a valid metadata credential source, permits inline secrets, and confuses availability updates with library scans. The validator must reject this file.
### title
Policy repair and rollback

### narration
The learner repairs each control and chooses a bounded request limit. A successful validation confirms the classroom policy requirements. Finally, the rollback command removes the isolated workspace, and an explicit absence test confirms that cleanup is complete.

## References

- Jellyseerr documentation — https://docs.jellyseerr.dev/
- Jellyseerr GitHub repository — https://github.com/Fallenbagel/jellyseerr
- Overseerr documentation — https://docs.overseerr.dev/
- Overseerr GitHub repository — https://github.com/sct/overseerr
- Docker Compose file reference — https://docs.docker.com/reference/compose-file/
- Docker Compose environment variable interpolation — https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
- TMDB API documentation — https://developer.themoviedb.org/docs/getting-started

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

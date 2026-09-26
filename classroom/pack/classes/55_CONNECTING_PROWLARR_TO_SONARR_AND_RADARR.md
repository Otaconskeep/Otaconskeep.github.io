# Class 55: Connecting Prowlarr to Sonarr and Radarr

**Learning objective:** Explain why Prowlarr connects to Sonarr and Radarr through their APIs; Select application URLs that are reachable from Prowlarr rather than merely reachable from a browser; Locate and protect Sonarr and Radarr API keys; Describe Full Sync and Add and Remove Only synchronization behavior; Recognize category, tag, authentication, DNS, proxy, and base URL problems; Verify an integration without exposing credentials in logs or screenshots; Create and validate an integration plan inside an isolated classroom directory
**Bloom level:** Understand / Apply
**Track:** Media Automation · **Difficulty:** intermediate · **Duration:** ~55 minutes · **Lab risk:** low
**Build output:** Teach learners how Prowlarr integrates with Sonarr and Radarr, how application URLs and API credentials are evaluated, how indexer synchronization works, and how to verify the design safely before changing a production media automation stack.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### applications
Prowlarr releases that provide Settings and Apps integration for Sonarr and Radarr
Sonarr releases exposing the supported Servarr API and API-key settings
Radarr releases exposing the supported Servarr API and API-key settings

### lab_runtime
Python 3.8 or newer

### notes
Menu labels and synchronization options may vary by installed release.
Default examples use Prowlarr port 9696, Sonarr port 8989, and Radarr port 7878; deployed ports and base URLs take precedence.
Container service names are examples and are valid only when runtime networking and name resolution provide those names.
The classroom validator performs structural checks only and does not claim live network compatibility.

## Learning objective

- Explain why Prowlarr connects to Sonarr and Radarr through their APIs
- Select application URLs that are reachable from Prowlarr rather than merely reachable from a browser
- Locate and protect Sonarr and Radarr API keys
- Describe Full Sync and Add and Remove Only synchronization behavior
- Recognize category, tag, authentication, DNS, proxy, and base URL problems
- Verify an integration without exposing credentials in logs or screenshots
- Create and validate an integration plan inside an isolated classroom directory

## Why this matters

Teach learners how Prowlarr integrates with Sonarr and Radarr, how application URLs and API credentials are evaluated, how indexer synchronization works, and how to verify the design safely before changing a production media automation stack.

## Prerequisites

- A basic understanding of Sonarr, Radarr, and Prowlarr responsibilities
- Administrative access to the Prowlarr, Sonarr, and Radarr web interfaces for later production implementation
- Knowledge of the hostnames, ports, and base URL settings used by each service
- A working Python 3 interpreter for the isolated classroom lab
- Permission to create files under /opt/lab-classroom/class55/

## Required reading

- Prowlarr documentation: https://wiki.servarr.com/prowlarr
- Sonarr settings documentation: https://wiki.servarr.com/sonarr/settings
- Radarr settings documentation: https://wiki.servarr.com/radarr/settings
- Servarr Docker guide: https://wiki.servarr.com/docker-guide

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Application integration | A Prowlarr configuration that permits Prowlarr to create and maintain compatible indexer entries in Sonarr or Radarr. |
| API key | A secret value used by one service to authenticate API requests to another service. |
| Application URL | The network address Prowlarr uses to contact Sonarr or Radarr. It must be valid from Prowlarr's network context. |
| Prowlarr URL | The address that Sonarr or Radarr can use when sending indexer queries through Prowlarr. |
| Full Sync | A synchronization mode in which Prowlarr can add, update, and remove managed indexer definitions in the connected application. |
| Add and Remove Only | A synchronization mode in which Prowlarr manages the presence of indexers but avoids synchronizing every editable indexer setting. |
| Base URL | An optional path prefix, such as /sonarr, used when an application is published beneath a subpath. |
| Category | A protocol-specific identifier used to distinguish content types such as television or movies. |
| Tag | A label that can limit which Prowlarr indexers are synchronized to a particular application. |
| Test action | A connection check performed before saving an application integration. |

## Instruction

Prowlarr centralizes indexer management while Sonarr and Radarr remain responsible for monitoring titles, selecting releases, and sending downloads to a download client. Connecting the applications does not merge their libraries or transfer media files. Instead, Prowlarr authenticates to the Sonarr and Radarr APIs and creates compatible indexer definitions for them.

The most important addressing rule is that an application URL must work from Prowlarr's network context. A URL that opens in an administrator's browser is not automatically usable by Prowlarr. For example, http://localhost:8989 means the system or container making the request. If Prowlarr and Sonarr are separate containers, localhost inside Prowlarr refers to Prowlarr itself rather than Sonarr. On a shared container network, a service name such as http://sonarr:8989 is often appropriate. If services use host networking, separate systems, or a reverse proxy, the correct address may instead be a host address or internal DNS name. The same rule applies to Radarr on its configured port.

The Prowlarr URL has the opposite direction of concern: it must be usable by Sonarr or Radarr when they query an indexer managed through Prowlarr. Internal service names are generally preferable when all participants share the same trusted network. Public proxy addresses can work, but they add dependencies involving DNS, TLS certificates, authentication middleware, and proxy routing. Base URLs must be represented consistently. If Sonarr is configured with /sonarr, an address that omits that path may reach a proxy but still return a not-found response.

To prepare a real connection, retrieve the API key from the target application's General settings and treat it as a credential. In Prowlarr, open Settings, then Apps, add the appropriate Sonarr or Radarr application type, enter a descriptive name, synchronization level, application URL, Prowlarr URL, and the target application's API key. Use the Test action before Save. A successful test confirms basic addressability, API authentication, and API compatibility; it does not prove that every indexer supports the desired media categories.

Tags control scope. With no restrictive tags, eligible indexers can be synchronized broadly. If an application entry has tags, only appropriately tagged indexers are selected. This is useful when one tracker should provide television results but not movie results, or when separate applications require different indexer policies. A tag mismatch can therefore produce an apparently healthy application connection with no useful synchronized indexers.

Full Sync gives Prowlarr stronger authority over managed indexer definitions. Changes made directly to a Prowlarr-managed indexer in Sonarr or Radarr may be overwritten during a later synchronization. Add and Remove Only is useful when local tuning should remain under the target application's control, although exact options can vary by release. Choose ownership deliberately instead of treating the sync level as a cosmetic setting.

After saving a production integration, inspect the target application's Indexers page and identify the entries managed through Prowlarr. Run a test from the target application, then perform an interactive search for a known monitored title. Do not immediately enable automatic searching across a large library. A staged check makes authentication, category, rate-limit, and quality-profile mistakes easier to isolate. This lesson's executable lab does not alter live applications; it builds and validates an integration plan entirely under the required classroom directory.

## Architecture

### components
Prowlarr stores indexer definitions and application integration records.
Sonarr manages television monitoring, release selection, and import workflows.
Radarr manages movie monitoring, release selection, and import workflows.
Indexers provide searchable release metadata.
A download client receives approved download requests from Sonarr or Radarr.

### control_flow
An administrator configures Sonarr and Radarr application records in Prowlarr.
Prowlarr authenticates to the target application API and synchronizes eligible indexer definitions.
Sonarr or Radarr sends a search request through the synchronized Prowlarr-backed indexer endpoint.
Prowlarr queries eligible upstream indexers and returns normalized results.
Sonarr or Radarr evaluates the results and can submit an accepted release to its configured download client.

### trust_boundaries
API keys cross the boundary from Prowlarr to the target application.
Indexer credentials remain under Prowlarr's management.
Application-to-application traffic must use addresses valid on the participating services' network.
Reverse proxies and identity gateways can introduce additional authentication and routing boundaries.

### example_internal_addresses
### prowlarr
http://prowlarr:9696

### sonarr
http://sonarr:8989

### radarr
http://radarr:7878

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Draw the request path for an interactive Sonarr search, labeling every hostname and trust boundary.
Document the real internal application URLs used by Prowlarr in your environment without recording API keys.
Choose Full Sync or Add and Remove Only for your environment and justify who should own indexer settings.
Design a tag policy that separates television and movie indexers.
Create a credential-rotation procedure covering both the target application and its Prowlarr record.
Record a staged production verification plan that tests one application and one indexer before wider rollout.

## Feynman teach-back

### prompt
Explain the integration to a learner who believes Sonarr connects directly to every tracker after Prowlarr is installed.

### model_explanation
Prowlarr acts like a directory and translator for indexers. An administrator teaches Prowlarr about indexers and gives it permission to configure Sonarr and Radarr through their APIs. Prowlarr then creates compatible indexer entries in those applications. When Sonarr wants television results or Radarr wants movie results, it uses the synchronized entry to ask Prowlarr, and Prowlarr asks the eligible indexers. The address entered for Sonarr must be reachable from Prowlarr, while the Prowlarr address must be reachable from Sonarr. API keys prove that Prowlarr is allowed to configure the target application, and tags decide which indexers are sent where.

## Retrieval check

1. 1. Why can http://localhost:8989 be incorrect when entered as Sonarr's application URL in Prowlarr?
2. 2. What does the Sonarr or Radarr API key allow Prowlarr to do?
3. 3. What is the main ownership consequence of choosing Full Sync?
4. 4. A Prowlarr application test succeeds, but no indexers appear in Radarr. Name two configuration areas to inspect.
5. 5. Which service must be able to reach the application URL entered for Sonarr?
6. 6. Which systems must be able to reach the Prowlarr URL used by synchronized indexer definitions?
7. 7. Why should a successful connection test be followed by an indexer test and a manual search?
8. 8. What should be done if an API key appears in a screenshot or committed configuration file?

## Guided lab

### scope
This lab creates a non-secret integration worksheet and a validator. It does not contact or modify live Prowlarr, Sonarr, Radarr, proxy, DNS, or download-client services.

### mutation_boundary
/opt/lab-classroom/class55/

### steps
### step
1

### instruction
Create the isolated classroom directory and write a synthetic integration plan. The records deliberately state that credentials must be entered interactively rather than stored in the worksheet.

### command
python3 - <<'PY'
import json
from pathlib import Path
root = Path('/opt/lab-classroom/class55')
root.mkdir(parents=True, exist_ok=True)
plan = {
    'prowlarr_url': 'http://prowlarr:9696',
    'credential_policy': 'Enter API keys interactively in Prowlarr; do not store them in this worksheet.',
    'applications': [
        {
            'name': 'Sonarr Internal',
            'type': 'sonarr',
            'application_url': 'http://sonarr:8989',
            'sync_level': 'full-sync',
            'required_categories': ['tv'],
            'tags': ['television']
        },
        {
            'name': 'Radarr Internal',
            'type': 'radarr',
            'application_url': 'http://radarr:7878',
            'sync_level': 'full-sync',
            'required_categories': ['movies'],
            'tags': ['movies']
        }
    ]
}
(root / 'integration-plan.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
PY
### step
2

### instruction
Create a validator that checks URL structure, application uniqueness, media categories, tags, synchronization levels, and credential-handling policy.

### command
cat > /opt/lab-classroom/class55/validate_plan.py <<'PY'
import json
from pathlib import Path
from urllib.parse import urlparse

root = Path('/opt/lab-classroom/class55')
plan = json.loads((root / 'integration-plan.json').read_text(encoding='utf-8'))
errors = []
allowed_types = {'sonarr', 'radarr'}
allowed_sync = {'full-sync', 'add-remove-only'}
expected_category = {'sonarr': 'tv', 'radarr': 'movies'}

prowlarr = urlparse(plan.get('prowlarr_url', ''))
if prowlarr.scheme not in {'http', 'https'} or not prowlarr.hostname:
    errors.append('Prowlarr URL must contain an HTTP or HTTPS scheme and hostname.')

policy = plan.get('credential_policy', '').lower()
if 'interactively' not in policy or 'do not store' not in policy:
    errors.append('Credential policy must require interactive entry and prohibit worksheet storage.')

apps = plan.get('applications', [])
if not isinstance(apps, list) or not apps:
    errors.append('At least one application is required.')

seen_names = set()
seen_types = set()
for app in apps:
    name = app.get('name', '')
    app_type = app.get('type', '')
    parsed = urlparse(app.get('application_url', ''))
    if not name or name in seen_names:
        errors.append('Application names must be present and unique.')
    seen_names.add(name)
    if app_type not in allowed_types:
        errors.append(f'{name or "Unnamed application"} has an unsupported type.')
    else:
        seen_types.add(app_type)
        if expected_category[app_type] not in app.get('required_categories', []):
            errors.append(f'{name} is missing its expected media category.')
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname:
        errors.append(f'{name or "Unnamed application"} has an invalid application URL.')
    if parsed.hostname in {'localhost', '127.0.0.1'}:
        errors.append(f'{name} uses a loopback address that is unsafe for a separate-service design.')
    if app.get('sync_level') not in allowed_sync:
        errors.append(f'{name} has an unsupported synchronization level.')
    tags = app.get('tags')
    if not isinstance(tags, list) or not tags or not all(isinstance(tag, str) and tag for tag in tags):
        errors.append(f'{name} must have at least one non-empty tag.')
    if any(key in app for key in ('api_key', 'apikey', 'token', 'password')):
        errors.append(f'{name} stores a credential-like field in the worksheet.')

if seen_types != allowed_types:
    errors.append('The plan must contain one Sonarr design and one Radarr design.')

if errors:
    print('PLAN INVALID')
    for error in errors:
        print(f'- {error}')
    raise SystemExit(1)

print('PLAN VALID')
print(f'Applications checked: {len(apps)}')
print('Credential-like fields stored: 0')
for app in apps:
    print(f"{app['type']}: {app['application_url']} -> {app['sync_level']}")
PY
### step
3

### instruction
Run the validator from the classroom directory.

### command
cd /opt/lab-classroom/class55 && python3 validate_plan.py
### step
4

### instruction
Review the plan and explain which system must be able to resolve each hostname. This command only reads the classroom artifact.

### command
python3 -m json.tool /opt/lab-classroom/class55/integration-plan.json
### step
5

### instruction
As a controlled negative test, change Sonarr's synthetic URL to a loopback address, confirm that validation fails, and restore the valid plan.

### command
python3 - <<'PY'
import json
from pathlib import Path
path = Path('/opt/lab-classroom/class55/integration-plan.json')
plan = json.loads(path.read_text(encoding='utf-8'))
for app in plan['applications']:
    if app['type'] == 'sonarr':
        app['application_url'] = 'http://localhost:8989'
path.write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
PY
cd /opt/lab-classroom/class55
python3 validate_plan.py; test $? -eq 1
python3 - <<'PY'
import json
from pathlib import Path
path = Path('/opt/lab-classroom/class55/integration-plan.json')
plan = json.loads(path.read_text(encoding='utf-8'))
for app in plan['applications']:
    if app['type'] == 'sonarr':
        app['application_url'] = 'http://sonarr:8989'
path.write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
PY
python3 validate_plan.py

### production_transfer
Confirm that each proposed hostname resolves from the Prowlarr runtime environment.
Retrieve Sonarr and Radarr API keys through their authenticated administration interfaces.
Add one application integration at a time in Prowlarr.
Run the Prowlarr Test action before saving.
Save only after the test succeeds.
Inspect synchronized indexers in the target application.
Run one target-side indexer test and one manual search before expanding automation.

## Expected results

- The directory /opt/lab-classroom/class55/ contains integration-plan.json and validate_plan.py.
- The initial validation prints PLAN VALID.
- The valid plan contains one Sonarr record and one Radarr record.
- The valid plan does not contain API keys, passwords, tokens, or other credential values.
- The controlled loopback test prints PLAN INVALID and identifies the Sonarr loopback address.
- After restoration, the final validation prints PLAN VALID.

## Verification checkpoints

- [ ] Run: cd /opt/lab-classroom/class55 && python3 validate_plan.py
- [ ] Confirm that the validator reports exactly two checked applications.
- [ ] Run: python3 -m json.tool /opt/lab-classroom/class55/integration-plan.json
- [ ] Confirm that Sonarr uses http://sonarr:8989 and Radarr uses http://radarr:7878 in the synthetic internal-network design.
- [ ] Confirm that no credential-like field is present in integration-plan.json.
- [ ] For a separately authorized production implementation, confirm that Prowlarr's Test action succeeds for each application before saving.
- [ ] For a separately authorized production implementation, confirm that the target application's Indexers page shows the intended synchronized entries and that a manual search returns appropriately categorized results.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Prowlarr reports that the Sonarr or Radarr connection was refused. | The application is not listening at the configured address or port, the wrong network context was assumed, or the service is still starting. | Verify the target service status and choose an address reachable from Prowlarr. Do not assume that a browser-reachable address is valid from the Prowlarr runtime. |
| The connection test reports an unauthorized response. | The API key is incorrect, was copied with extra characters, was rotated, or belongs to a different application. | Retrieve the key again from the target application's authenticated settings, replace it in Prowlarr, and rerun the Test action without recording the key in notes or screenshots. |
| The application URL works in a browser but fails in Prowlarr. | The browser and Prowlarr use different DNS, routing, proxy, or container-network contexts. | Evaluate name resolution and reachability from Prowlarr's runtime environment, then use an internal service name or other address valid from that environment. |
| The connection succeeds, but no indexers appear in Sonarr or Radarr. | Tags exclude all indexers, synchronization has not run, or no configured indexer supports the target application's categories. | Review application tags, indexer tags, category support, and synchronization status. Trigger the application's supported synchronization or save workflow after correcting scope. |
| The target application receives not-found responses. | A configured base URL is missing, duplicated, or routed incorrectly by an intermediary. | Compare the application's configured base URL with both directions of the integration and ensure each address contains the path exactly once. |
| Manual indexer edits in Sonarr or Radarr disappear. | Prowlarr is using Full Sync and remains authoritative for the managed definition. | Make the change in Prowlarr or choose Add and Remove Only if local ownership is intentional and supported by the installed version. |
| The lab validator prints PLAN INVALID after the negative test. | The synthetic Sonarr URL was not restored from localhost to the service hostname. | Set the Sonarr application_url in /opt/lab-classroom/class55/integration-plan.json back to http://sonarr:8989 and rerun the validator. |
| The lab cannot create the classroom directory. | The learner lacks write permission for /opt/lab-classroom/. | Ask the lab administrator to pre-create /opt/lab-classroom/class55/ with appropriate ownership. Do not redirect the exercise into an unapproved directory. |

## Security considerations

Treat Sonarr and Radarr API keys as secrets because they authorize API operations in the corresponding applications.
Do not place real API keys in shell history, lesson notes, source control, screenshots, chat messages, or the classroom integration plan.
Prefer trusted internal names and encrypted transport when traffic crosses an untrusted network.
Restrict administrative web interfaces to authorized users and networks.
Do not publish Prowlarr, Sonarr, or Radarr directly to the public internet solely to make the integration work.
Rotate an API key if it is exposed and update the corresponding Prowlarr application record.
Use tags to enforce intended indexer scope rather than synchronizing every indexer to every application.
Review proxy authentication behavior carefully because machine-to-machine API traffic may not be compatible with an interactive sign-in page.
Redact URLs if they contain embedded credentials or sensitive internal naming information.

## Rollback

### lab
Remove only the files integration-plan.json and validate_plan.py from /opt/lab-classroom/class55/ if classroom cleanup is authorized.
Leave all live Prowlarr, Sonarr, and Radarr services unchanged because the executable lab never contacts them.

### production
Disable or remove the affected application record in Prowlarr.
Review the target application's Indexers page and remove only entries confirmed to be managed by the retired integration.
Restore the previous application URL, Prowlarr URL, tags, or synchronization level from an approved configuration record.
If a credential was exposed, rotate it in Sonarr or Radarr and update authorized integrations.
Retest one application at a time before re-enabling normal automation.

## Video narration notes

Begin with the architecture diagram and emphasize that Prowlarr centralizes indexers rather than replacing Sonarr or Radarr. Follow a television search from Sonarr to a synchronized Prowlarr-backed indexer and then to eligible upstream indexers. Repeat the direction for Radarr and movie categories. Next, compare browser context with service context. Show why localhost means the caller's own environment and why a service hostname is usually clearer on a shared application network. Explain the two directional addresses: Prowlarr must reach each application URL, while Sonarr and Radarr must reach the configured Prowlarr URL.

Move to the Prowlarr Apps workflow conceptually. Identify the application type, descriptive name, synchronization level, application URL, Prowlarr URL, API key, and tags. Explain that API keys must remain secret and should be entered directly into the authenticated interface. Demonstrate the reasoning behind Test before Save, then explain that a successful API test is only the first verification layer.

Discuss Full Sync as an ownership decision. Prowlarr-managed values may overwrite direct edits in the target application. Contrast that behavior with Add and Remove Only, while noting that available labels and details can vary across versions. Demonstrate how tags can intentionally select indexers and how a tag mismatch can produce an empty synchronization despite a healthy application connection.

For the executable lab, create the synthetic plan under /opt/lab-classroom/class55/, run the validator, and read each successful check. Perform the controlled negative test by changing only the synthetic Sonarr URL to localhost. Explain the resulting failure, restore the service hostname, and rerun validation. Close with the staged production method: connect one application, run the Prowlarr test, save, inspect synchronized indexers, run a target-side test, and perform a manual search before enabling broader automation.

## References

- Prowlarr documentation: https://wiki.servarr.com/prowlarr
- Prowlarr application settings documentation: https://wiki.servarr.com/prowlarr/settings
- Sonarr documentation: https://wiki.servarr.com/sonarr
- Radarr documentation: https://wiki.servarr.com/radarr
- Servarr Docker guide: https://wiki.servarr.com/docker-guide
- Python urllib.parse documentation: https://docs.python.org/3/library/urllib.parse.html
- Python json documentation: https://docs.python.org/3/library/json.html

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

# Lab: Connecting Prowlarr to Sonarr and Radarr

**Module:** Download Clients & Indexers
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain why Prowlarr connects to Sonarr and Radarr through their APIs

## Before you start

- A basic understanding of Sonarr, Radarr, and Prowlarr responsibilities
- Administrative access to the Prowlarr, Sonarr, and Radarr web interfaces for later production implementation
- Knowledge of the hostnames, ports, and base URL settings used by each service
- A working Python 3 interpreter for the isolated classroom lab
- Permission to create files under /opt/lab-classroom/class55/

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

## Verification

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

## Security

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

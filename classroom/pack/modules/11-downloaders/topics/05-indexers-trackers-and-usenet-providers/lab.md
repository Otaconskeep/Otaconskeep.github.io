# Lab: Indexers, Trackers, and Usenet Providers

**Module:** Download Clients & Indexers
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Differentiate a Usenet indexer, Usenet provider, torrent indexer, BitTorrent tracker, download client, and automation application.

## Before you start

- Basic understanding of client-server networking and HTTPS
- Basic familiarity with JSON configuration files
- Ability to run shell commands and Python 3
- Conceptual familiarity with download clients and media automation applications
- A lab environment in which /opt/lab-classroom/class53/ is writable

## Guided lab

### name
Classify synthetic discovery and transfer services

### objective
Create a local service catalog, classify each component, and generate a policy report without making any network requests.

### scope_rule
Every file created, modified, or removed by this lab is under /opt/lab-classroom/class53/. The supplied evaluator uses only Python standard-library modules and does not contact external systems.

### steps
### step
1

### instruction
Create the isolated lab and output directories.

### command
mkdir -p /opt/lab-classroom/class53/output
### step
2

### instruction
Create a synthetic catalog. The names describe fictional lab components and are not provider recommendations.

### command
cat > /opt/lab-classroom/class53/catalog.json <<'EOF'
[
  {
    "name": "Synthetic Usenet Catalog",
    "role": "usenet_indexer",
    "transport": "https",
    "authentication": "api_key",
    "returns": "nzb",
    "authorized_content_only": true
  },
  {
    "name": "Synthetic NNTP Access",
    "role": "usenet_provider",
    "transport": "nntps",
    "authentication": "account_secret",
    "returns": "article_bodies",
    "authorized_content_only": true
  },
  {
    "name": "Synthetic Torrent Catalog",
    "role": "torrent_indexer",
    "transport": "https",
    "authentication": "api_key",
    "returns": "torrent_metadata",
    "authorized_content_only": true
  },
  {
    "name": "Synthetic Peer Coordinator",
    "role": "torrent_tracker",
    "transport": "https",
    "authentication": "none",
    "returns": "peer_information",
    "authorized_content_only": true
  }
]
EOF
### step
3

### instruction
Create the offline evaluator. It validates allowed roles, checks transport and policy fields, and records the dependency associated with each role.

### command
cat > /opt/lab-classroom/class53/evaluate.py <<'PY'
import json
from pathlib import Path

root = Path('/opt/lab-classroom/class53')
source = root / 'catalog.json'
destination = root / 'output' / 'recommendations.json'

rules = {
    'usenet_indexer': {
        'expected_return': 'nzb',
        'dependency': 'usenet_provider and usenet_download_client',
        'purpose': 'discovery'
    },
    'usenet_provider': {
        'expected_return': 'article_bodies',
        'dependency': 'usenet_download_client',
        'purpose': 'transfer infrastructure'
    },
    'torrent_indexer': {
        'expected_return': 'torrent_metadata',
        'dependency': 'bittorrent_client',
        'purpose': 'discovery'
    },
    'torrent_tracker': {
        'expected_return': 'peer_information',
        'dependency': 'bittorrent_client and participating peers',
        'purpose': 'peer coordination'
    }
}

records = json.loads(source.read_text(encoding='utf-8'))
report = []
for record in records:
    role = record.get('role')
    findings = []
    rule = rules.get(role)
    if rule is None:
        findings.append('unknown role')
    else:
        if record.get('returns') != rule['expected_return']:
            findings.append('returned artifact does not match role')
        if record.get('transport') not in {'https', 'nntps'}:
            findings.append('encrypted transport not declared')
        if record.get('authorized_content_only') is not True:
            findings.append('authorization policy not affirmed')
    report.append({
        'name': record.get('name'),
        'role': role,
        'purpose': rule['purpose'] if rule else 'unknown',
        'dependency': rule['dependency'] if rule else 'manual review',
        'status': 'pass' if not findings else 'review',
        'findings': findings
    })

destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(f'Wrote {len(report)} classified records to {destination}')
PY
### step
4

### instruction
Run the evaluator. It reads and writes only within the class directory.

### command
python3 /opt/lab-classroom/class53/evaluate.py
### step
5

### instruction
Inspect the generated policy report.

### command
python3 -m json.tool /opt/lab-classroom/class53/output/recommendations.json
### step
6

### instruction
Confirm that each synthetic component passed and that discovery roles are distinct from transfer or coordination roles.

### command
python3 -c "import json; from pathlib import Path; p=Path('/opt/lab-classroom/class53/output/recommendations.json'); data=json.loads(p.read_text()); assert len(data)==4; assert all(x['status']=='pass' for x in data); assert {x['purpose'] for x in data}=={'discovery','transfer infrastructure','peer coordination'}; print('Class 53 verification passed')"

### extension
Make one reversible edit inside catalog.json, such as changing the synthetic tracker transport from https to http, rerun the evaluator, and observe that its status becomes review. Restore https and rerun the verification command. Do not add real service addresses or credentials.

## Expected results

- The evaluator reports that it wrote four classified records.
- The generated recommendations.json file contains two discovery records, one transfer-infrastructure record, and one peer-coordination record.
- The Usenet indexer record depends on both a Usenet provider and a Usenet download client.
- The Usenet provider record returns article bodies rather than NZB metadata.
- The torrent indexer record returns torrent metadata and depends on a BitTorrent client.
- The tracker record returns peer information and is classified as peer coordination rather than content hosting.
- All four unmodified synthetic records have a status of pass and an empty findings array.
- The final assertion prints Class 53 verification passed.

## Verification

- [ ] Run: python3 -m json.tool /opt/lab-classroom/class53/catalog.json
- [ ] Run: python3 -m json.tool /opt/lab-classroom/class53/output/recommendations.json
- [ ] Run: python3 -c "import json; from pathlib import Path; d=json.loads(Path('/opt/lab-classroom/class53/output/recommendations.json').read_text()); print([(x['role'], x['purpose'], x['status']) for x in d])"
- [ ] Verify that usenet_indexer maps to discovery and expects NZB metadata.
- [ ] Verify that usenet_provider maps to transfer infrastructure and expects article bodies.
- [ ] Verify that torrent_indexer maps to discovery while torrent_tracker maps to peer coordination.
- [ ] Run the step 6 assertion and confirm that it exits successfully.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| mkdir reports permission denied. | The current lab account is not allowed to create directories under /opt/lab-classroom. | Use the classroom account or environment that has been delegated access to /opt/lab-classroom. Do not redirect the exercise to an unrelated production path. |
| python3 is not found. | Python 3 is absent from the lab image or is not available through the current command search path. | Use a compatible lab image with Python 3 preinstalled. Do not install system packages as part of this exercise because that would mutate locations outside the permitted class directory. |
| The evaluator reports invalid JSON. | The catalog heredoc was copied incompletely, contains a missing comma, or contains typographic quotation marks. | Recreate catalog.json exactly as shown and validate it with python3 -m json.tool before rerunning the evaluator. |
| A record has status review and the finding says encrypted transport not declared. | The transport field was changed to a value other than https or nntps. | Restore the synthetic transport appropriate to the role, then rerun evaluate.py. |
| A record has status review and the finding says returned artifact does not match role. | The service role and returns fields describe incompatible responsibilities. | Use nzb for usenet_indexer, article_bodies for usenet_provider, torrent_metadata for torrent_indexer, or peer_information for torrent_tracker. |
| A real automation application can search but cannot download. | Discovery succeeded, but the download client, provider authentication, peer discovery, category mapping, or transfer path failed. | Test each boundary separately. Confirm the client API, then provider or peer connectivity, then category and path mapping. Do not treat a successful search as proof of transfer availability. |
| Usenet jobs fail with missing articles. | The selected provider may not have every referenced article, or the NZB may describe an incomplete posting. | Confirm that the metadata is valid and that the content is authorized. Review provider availability and the client's completion logs without exposing credentials. |
| A torrent remains idle even though metadata was accepted. | No reachable peers are available, tracker communication failed, DHT is unavailable or disallowed, or the torrent is no longer active. | Inspect client status and peer-discovery messages. Metadata acceptance proves only that the client understood the job; it does not guarantee available peers. |

## Security

### credential_handling
Store indexer, provider, and client API secrets in the application's secret mechanism rather than in shared examples or source control.
Use different credentials for different trust boundaries when the service supports that model.
Rotate any credential exposed in logs, screenshots, shell history, or support bundles.
Redact query strings and headers because some APIs place tokens in URLs or authorization headers.

### transport
Prefer encrypted HTTPS for indexer and client APIs.
Prefer NNTP protected by TLS when communicating with a Usenet provider.
Validate certificates rather than disabling certificate verification to conceal a trust problem.
Understand that BitTorrent peers can observe participating peer addresses even when control-plane services use HTTPS.

### service_exposure
Do not publish download-client administration interfaces directly to untrusted networks.
Require authentication on local service APIs and restrict which automation applications may reach them.
Separate untrusted download staging from curated libraries.
Treat imported archives, media containers, subtitles, scripts, and metadata as untrusted input.

### legal_and_policy
Use indexers, providers, trackers, and peers only for material you are authorized to access or distribute. Encryption, private membership, or a paid subscription does not replace authorization and does not override service terms or applicable law.

### lab_assurance
The lab uses fictional records, performs no network operations, contains no real credentials, and confines all mutations to /opt/lab-classroom/class53/.

## Rollback

### purpose
Remove only the files and directories created by this class.

### precheck
Inspect the target with: find /opt/lab-classroom/class53 -maxdepth 2 -print

### command
python3 -c "from pathlib import Path; root=Path('/opt/lab-classroom/class53').resolve(); expected=Path('/opt/lab-classroom/class53'); assert root==expected; files=[root/'output/recommendations.json',root/'evaluate.py',root/'catalog.json']; [p.unlink() for p in files if p.is_file()]; out=root/'output'; out.rmdir() if out.exists() and not any(out.iterdir()) else None; root.rmdir() if root.exists() and not any(root.iterdir()) else None"

### postcheck
Run: test ! -e /opt/lab-classroom/class53 && echo 'Class 53 artifacts removed' || find /opt/lab-classroom/class53 -maxdepth 2 -print

### note
The cleanup intentionally stops if unexpected content prevents a directory from being removed. Inspect unexpected content rather than broadening the deletion scope.

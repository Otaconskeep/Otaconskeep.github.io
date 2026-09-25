# Class 53: Indexers, Trackers, and Usenet Providers

**Learning objective:** Differentiate a Usenet indexer, Usenet provider, torrent indexer, BitTorrent tracker, download client, and automation application.; Explain why an NZB file is metadata rather than the downloaded payload.; Explain why a BitTorrent tracker coordinates peers but is not normally the searchable content catalog.; Map the dependencies required for a complete Usenet or BitTorrent automation path.; Evaluate transport encryption, authentication, credential scope, category support, and policy requirements.; Build and verify a local policy report using entirely synthetic service records.; Identify common integration failures without exposing credentials or contacting external services.
**Bloom level:** Understand / Apply
**Track:** Download Automation and Media Services · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach learners to distinguish content-discovery services from transfer infrastructure, understand how Usenet and BitTorrent components interact, evaluate provider and indexer requirements, and design a secure automation workflow without contacting real indexers, trackers, peers, or Usenet servers.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux environments with a writable /opt/lab-classroom directory

### runtime
Python 3.8 or newer using only the standard library

### shell
A POSIX-compatible shell supporting heredoc redirection

### network_required
False

### external_accounts_required
False

### container_required
False

### notes
The conceptual material applies across common Usenet clients, BitTorrent clients, indexer managers, and automation applications. Product interfaces and service policies vary, so current vendor documentation must be consulted before production deployment.

## Learning objective

- Differentiate a Usenet indexer, Usenet provider, torrent indexer, BitTorrent tracker, download client, and automation application.
- Explain why an NZB file is metadata rather than the downloaded payload.
- Explain why a BitTorrent tracker coordinates peers but is not normally the searchable content catalog.
- Map the dependencies required for a complete Usenet or BitTorrent automation path.
- Evaluate transport encryption, authentication, credential scope, category support, and policy requirements.
- Build and verify a local policy report using entirely synthetic service records.
- Identify common integration failures without exposing credentials or contacting external services.

## Why this matters

Teach learners to distinguish content-discovery services from transfer infrastructure, understand how Usenet and BitTorrent components interact, evaluate provider and indexer requirements, and design a secure automation workflow without contacting real indexers, trackers, peers, or Usenet servers.

## Prerequisites

- Basic understanding of client-server networking and HTTPS
- Basic familiarity with JSON configuration files
- Ability to run shell commands and Python 3
- Conceptual familiarity with download clients and media automation applications
- A lab environment in which /opt/lab-classroom/class53/ is writable

## Required reading

- RFC 3977, Network News Transfer Protocol (NNTP): https://www.rfc-editor.org/rfc/rfc3977
- RFC 4642, Using Transport Layer Security with Network News Transfer Protocol: https://www.rfc-editor.org/rfc/rfc4642
- BitTorrent Enhancement Proposal 3, The BitTorrent Protocol Specification: https://www.bittorrent.org/beps/bep_0003.html
- Prowlarr documentation, Indexers: https://wiki.servarr.com/prowlarr/indexers
- SABnzbd documentation: https://sabnzbd.org/wiki/

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Usenet provider | A service that supplies access to Usenet articles through NNTP or encrypted NNTP. The provider is the transfer-side infrastructure and is distinct from an indexer. |
| Usenet indexer | A searchable catalog that interprets Usenet postings and commonly returns NZB metadata describing the articles needed for a requested item. |
| NZB | An XML-based metadata document containing references to Usenet articles. It does not contain the final payload itself. |
| Retention | The period for which a Usenet provider makes articles available. Advertised retention does not guarantee that every requested article is complete or available. |
| Completion | Whether all articles required to reconstruct a requested Usenet post can be retrieved successfully. |
| Torrent indexer | A searchable discovery service that returns torrent metadata or magnet information. It is conceptually separate from peer coordination. |
| BitTorrent tracker | A coordination service that processes peer announcements and supplies peer information for a torrent swarm. It normally does not transfer the payload. |
| DHT | A distributed hash table that can assist peer discovery without relying exclusively on a centralized tracker. |
| Magnet URI | A URI that identifies content, commonly by an info hash, and can allow a BitTorrent client to obtain torrent metadata from the swarm. |
| Download client | Software that performs the actual NNTP article retrieval or BitTorrent peer transfer after receiving metadata. |
| Automation application | Software that searches configured indexers, applies quality and policy rules, submits a result to a download client, and monitors completion. |
| API key | A secret token used by software to authenticate to a service API. It must be protected like a password and scoped or rotated when supported. |
| Category mapping | The agreement between an indexer, automation application, and download client about labels used to route and process jobs. |

## Instruction

The most important design rule is to separate discovery from transfer. In a Usenet workflow, an automation application searches a Usenet indexer. The indexer returns an NZB document containing references to articles. An NZB-capable download client then authenticates to a Usenet provider and retrieves those articles through NNTP, preferably over TLS. The indexer does not normally provide the article bodies, and the provider does not normally offer the rich application-oriented search interface expected from an indexer. A complete Usenet path therefore requires both discovery and provider access.

A BitTorrent workflow has different components. A torrent indexer is a searchable catalog that returns torrent metadata or magnet information. A BitTorrent client interprets that metadata, discovers peers, and exchanges pieces with them. A tracker can assist peer discovery by receiving announcements and returning peer information, but it is not normally the searchable indexer and it does not act as the payload host. DHT and peer exchange may supplement or replace a centralized tracker for peer discovery, depending on the torrent and client policy.

Automation tools can hide these boundaries, which makes troubleshooting confusing. A successful search proves only that discovery works. It does not prove that the download client can authenticate to its transfer service, reach peers, retrieve every required article, write to its configured destination, or report completion. Likewise, a client connection test does not prove that an indexer query, category mapping, or API limit is correct. Diagnose the chain one boundary at a time: automation to indexer, automation to client, client to provider or peers, and client output back to the automation application.

Service evaluation must avoid treating marketing claims as guaranteed outcomes. Consider protocol support, encrypted transport, authentication method, credential rotation, API policies, category coverage, regional availability, provider independence, data retention practices, service terms, and local law. Never place production credentials in screenshots, shared configuration examples, public repositories, or support logs. Use only content that you are authorized to acquire or distribute. Privacy tools and encryption protect transport and metadata exposure; they do not create permission to obtain copyrighted material.

## Architecture

### usenet_path
Automation application -> HTTPS search request -> Usenet indexer -> NZB metadata -> automation application -> download client -> encrypted NNTP connection -> Usenet provider -> article retrieval -> local staging -> import

### bittorrent_path
Automation application -> HTTPS search request -> torrent indexer -> torrent metadata or magnet URI -> automation application -> BitTorrent client -> tracker, DHT, or peer exchange -> peers -> piece transfer -> local staging -> import

### trust_boundaries
Indexer API credentials cross the boundary between the automation application and the discovery service.
Download-client credentials cross the boundary between the automation application and the client API.
Usenet-provider credentials cross the boundary between the Usenet client and the NNTP service.
Torrent participation can reveal a peer address to other swarm participants.
Downloaded data crosses from an untrusted staging area into a managed library only after validation.

### diagnostic_order
Confirm local configuration syntax.
Confirm name resolution and encrypted transport.
Confirm authentication without printing secrets.
Test one discovery request.
Test one client submission using authorized content.
Confirm transfer status and category mapping.
Confirm final import permissions and path mapping.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Design two architecture plans on paper or in a local text file under /opt/lab-classroom/class53/: one for an authorized Usenet workflow and one for an authorized BitTorrent workflow.

### requirements
Label discovery, metadata, transfer, staging, and import boundaries.
Identify which components require credentials.
State which links require encrypted transport.
Describe how secrets are withheld from logs and source control.
Provide one failure test for every boundary.
Explain why a successful indexer query does not prove that a transfer can complete.
Include a policy statement limiting use to authorized content.

### challenge
Extend evaluate.py with a client role for each protocol and require each indexer record to identify a compatible client. Keep every generated file inside /opt/lab-classroom/class53/ and use only synthetic values.

## Feynman teach-back

Explain the system to a new administrator using a library analogy. The indexer is the searchable catalog, not the shelf holding the material. An NZB or torrent metadata result is like a retrieval slip describing what is needed. A Usenet provider is the infrastructure from which an NNTP client requests referenced articles. In BitTorrent, peers exchange pieces, while a tracker can help participants find one another. The automation application is the coordinator that searches the catalog and hands a selected result to the correct client. If your explanation claims that a tracker stores every payload, that an indexer performs all transfers, or that an NZB is the final payload, revise it until each responsibility and trust boundary is distinct.

## Retrieval check

1. 1. What is the primary function of a Usenet indexer?
2. 2. Why is a Usenet provider still required after an indexer returns an NZB?
3. 3. Does an NZB normally contain the final downloaded payload?
4. 4. What is the primary function of a BitTorrent tracker?
5. 5. How does a torrent indexer differ from a tracker?
6. 6. Why does a successful search not prove that a download will complete?
7. 7. Which transport protections should be preferred for indexer APIs and NNTP provider access?
8. 8. What information should never be included in public troubleshooting logs?
9. 9. What is category mapping used for in an automation stack?
10. 10. Does encrypted transport create legal authorization to acquire content?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

Begin with one sentence: discovery is not transfer. On the Usenet side, show an automation application searching an indexer over HTTPS. The response is an NZB, which is metadata describing article references. Follow that NZB to the download client, and then show the client connecting to a Usenet provider through encrypted NNTP to retrieve article bodies. Emphasize that the indexer and provider are complementary but separate services.

Next, show the BitTorrent path. The automation application searches a torrent indexer and receives torrent metadata or a magnet URI. The BitTorrent client interprets that information and discovers peers. A tracker can help by coordinating peer announcements, while DHT or peer exchange may provide additional discovery. The actual pieces move among peers, not from the tracker as though it were a file server.

Move to troubleshooting. A green search test confirms only the indexer boundary. A complete diagnosis checks automation-to-indexer authentication, automation-to-client access, client-to-provider or client-to-peer connectivity, category mapping, staging paths, and final import. Never paste secrets into logs while performing these tests.

Conclude with the offline lab. The synthetic catalog contains one example of each major role. The Python evaluator verifies the expected artifact, encrypted transport declaration, policy affirmation, purpose, and dependency. No real service is contacted. The generated report reinforces the central model: indexers discover, providers or peers supply data, trackers coordinate peers, clients perform transfers, and automation applications orchestrate the workflow.

## References

- IETF RFC 3977, Network News Transfer Protocol: https://www.rfc-editor.org/rfc/rfc3977
- IETF RFC 4642, Using Transport Layer Security with Network News Transfer Protocol: https://www.rfc-editor.org/rfc/rfc4642
- BitTorrent Enhancement Proposal 3, The BitTorrent Protocol Specification: https://www.bittorrent.org/beps/bep_0003.html
- BitTorrent Enhancement Proposal 5, DHT Protocol: https://www.bittorrent.org/beps/bep_0005.html
- Prowlarr documentation: https://wiki.servarr.com/prowlarr
- SABnzbd documentation: https://sabnzbd.org/wiki/
- Python json module documentation: https://docs.python.org/3/library/json.html
- Python pathlib documentation: https://docs.python.org/3/library/pathlib.html

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

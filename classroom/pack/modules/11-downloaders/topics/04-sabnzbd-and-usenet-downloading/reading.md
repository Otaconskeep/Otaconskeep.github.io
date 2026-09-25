# Reading: SABnzbd and Usenet Downloading

**Module:** Download Clients & Indexers
**Activity type:** Reading (Learn)
**Objective:** Describe the roles of a Usenet provider, an indexer, an NZB file, and SABnzbd.

## Vocabulary

| Term | Meaning |
|---|---|
| Usenet | A distributed discussion and article-distribution system. Binary content is commonly split into many encoded articles posted to newsgroups. |
| Usenet provider | A service that operates or resells access to Usenet servers and supplies credentials, retention, article availability, and a permitted number of concurrent connections. |
| Indexer | A service that catalogs Usenet posts and can produce NZB metadata. An indexer is distinct from the provider that serves the referenced articles. |
| NZB | An XML document containing message identifiers and metadata for a set of Usenet articles. It generally points to content rather than containing the content itself. |
| Article | An individual Usenet message. Large binary payloads are divided across many articles and must be retrieved and reassembled. |
| Retention | The approximate age range of articles a provider claims to keep. High advertised retention does not guarantee that every referenced article is available. |
| Completion | The practical availability of all articles needed for a post. Missing articles can prevent successful reconstruction even when the post is within the retention period. |
| PAR2 | Parity metadata and recovery blocks that can reconstruct a limited amount of missing or damaged data when sufficient recovery information exists. |
| Block account | A provider account purchased for a fixed amount of transferred data, often configured as a lower-priority backup to a subscription account. |
| Category | A SABnzbd label that can select a completion directory, processing behavior, priority, and integration workflow for a job. |
| Post-processing | Actions performed after article retrieval, such as verification, repair, archive extraction, renaming, script execution, and placement in a completed directory. |
| API key | A secret token used by automation clients to control SABnzbd. Possession may permit queue changes, job submission, history access, or configuration operations. |

## Instruction

SABnzbd is a queue-driven Usenet download client. It does not search the public internet for media and it does not normally discover posts by itself. An operator or an authorized automation client supplies an NZB document. That XML document lists message identifiers for articles stored by a Usenet provider. SABnzbd connects to the configured provider, authenticates, requests those articles, decodes their payloads, and reconstructs the files represented by the job. A complete system therefore has distinct roles: an indexer describes where articles are located, a provider serves the articles, SABnzbd performs retrieval and post-processing, and an optional library manager imports approved completed files.

The normal processing path is intake, queueing, article retrieval, verification, optional PAR2 repair, optional archive extraction, and placement in a completed destination. Incomplete data should remain separate from completed output. This prevents downstream applications from importing partial archives or files that have not passed verification. Categories provide a controlled handoff mechanism: a category such as documents, audio, or video can map to its own completed subdirectory and processing policy. Category names and paths must agree with any automation client that submits jobs.

Provider settings affect reliability and privacy. Use the provider's documented TLS endpoint and verify certificates. Port 563 is commonly used for NNTP over TLS, but the provider's documentation remains authoritative. A large connection limit is not automatically faster or better; exceeding the provider's allowance can cause authentication failures, throttling, or unstable transfers. Start conservatively and remain within the purchased plan. A second provider or block account may improve completion when it has a genuinely independent article source, but it should have a lower priority so it is used only when the primary cannot supply an article.

Retention and completion are different. Retention is an age claim, while completion describes whether the exact referenced articles still exist. A job may be young enough for the provider's retention window yet still fail because some articles were removed, never propagated, or are unavailable on that provider. PAR2 can repair only within the amount of available recovery data; it cannot recreate unlimited missing content.

The web interface is an administrative control plane. Bind it to loopback or a trusted internal address and place authenticated, encrypted access in front of it when remote administration is required. Protect provider credentials and API keys as secrets. Do not embed them in shared configuration examples, source repositories, NZB files, or logs. Review post-processing scripts especially carefully because they execute after handling untrusted downloaded input. This class uses a synthetic NZB containing no external payload and performs no network requests. The resulting policy report demonstrates path separation, local-only administration, provider TLS intent, conservative connection use, and category mapping before a real installation is configured.

## Architecture

### components
### name
Authorized NZB source

### role
Supplies NZB metadata selected by the operator or an approved automation client.
### name
SABnzbd intake and queue

### role
Parses NZB metadata, applies category and priority settings, and schedules article retrieval.
### name
Primary Usenet provider

### role
Serves articles over an authenticated TLS connection and is attempted first.
### name
Optional backup provider

### role
Supplies articles unavailable from the primary and is assigned lower priority.
### name
Incomplete workspace

### role
Holds partially downloaded, decoded, verification, repair, and extraction data.
### name
Completed category directories

### role
Receive successfully processed output for controlled import by downstream applications.
### name
Management interface and API

### role
Provides queue administration and automation; it should be reachable only from trusted systems.

### data_flow
An operator or authorized client submits an NZB and assigns a category.
SABnzbd parses message identifiers and schedules article requests.
The primary provider is queried over TLS; an optional lower-priority provider may supply missing articles.
Article payloads are decoded into the incomplete workspace.
SABnzbd verifies reconstructed files and uses available PAR2 recovery data when necessary.
Approved archives are extracted according to policy.
Successful output moves into the completed directory associated with the job category.
A downstream application may import only from completed category directories.

### trust_boundaries
NZB metadata and downloaded article content are untrusted input.
Provider credentials and SABnzbd API keys are secrets.
The management interface crosses a trust boundary whenever it is reachable beyond the local host.
Post-processing scripts cross from untrusted downloaded data into local command execution.
Completed output should not be treated as trusted solely because verification succeeded.

## Required reading

- SABnzbd documentation: https://sabnzbd.org/wiki/
- SABnzbd configuration documentation: https://sabnzbd.org/wiki/configuration/
- SABnzbd FAQ: https://sabnzbd.org/wiki/faq/
- Python XML security guidance: https://docs.python.org/3/library/xml.html#xml-vulnerabilities
- IETF TLS 1.3 specification, RFC 8446: https://www.rfc-editor.org/rfc/rfc8446

## References

- SABnzbd official site: https://sabnzbd.org/
- SABnzbd Wiki: https://sabnzbd.org/wiki/
- SABnzbd configuration guide: https://sabnzbd.org/wiki/configuration/
- SABnzbd FAQ: https://sabnzbd.org/wiki/faq/
- SABnzbd source repository: https://github.com/sabnzbd/sabnzbd
- NZB format DTD archive: https://sabnzbd.org/wiki/extra/nzb-spec
- Python configparser documentation: https://docs.python.org/3/library/configparser.html
- Python ElementTree documentation: https://docs.python.org/3/library/xml.etree.elementtree.html
- RFC 8446, The Transport Layer Security Protocol Version 1.3: https://www.rfc-editor.org/rfc/rfc8446

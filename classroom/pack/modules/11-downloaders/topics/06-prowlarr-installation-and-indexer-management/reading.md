# Reading: Prowlarr Installation and Indexer Management

**Module:** Download Clients & Indexers
**Activity type:** Reading (Learn)
**Objective:** Explain why Prowlarr centralizes indexer definitions for compatible media-management applications.

## Vocabulary

| Term | Meaning |
|---|---|
| Prowlarr | An indexer manager and proxy in the Servarr ecosystem that maintains indexer definitions and can synchronize compatible definitions to applications such as Sonarr and Radarr. |
| Indexer | A searchable source of release metadata. An indexer definition includes a protocol, endpoint, credentials when required, capabilities, categories, limits, and enablement settings. |
| Torznab | An HTTP API convention derived from Newznab that exposes capabilities and searchable torrent-oriented metadata in XML. |
| Newznab | An HTTP API convention commonly used for Usenet indexer capabilities and search results. |
| Capability query | A request such as t=caps that asks an indexer which searches, parameters, limits, and categories it supports. |
| Application connection | A configured relationship through which Prowlarr communicates with another automation application and synchronizes eligible indexer settings. |
| Sync profile | A policy controlling how an indexer is synchronized to connected applications and how changes are handled. |
| Download client | A separate service that accepts a selected release for retrieval. Prowlarr can test and use download-client connections, but it is not itself the downloader. |
| Indexer proxy | An optional proxy definition that selected indexers can use for outbound communication. |
| Application data directory | The persistent directory containing Prowlarr's database, configuration, logs, update data, and other runtime state. |

## Instruction

Prowlarr separates indexer management from the applications that consume indexer results. Without a central manager, an administrator may define the same endpoint, credentials, categories, and limits independently in several applications. That duplication increases configuration drift and makes credential rotation or endpoint changes harder. Prowlarr provides one administrative location for indexer definitions and can synchronize supported definitions to connected applications. It can also perform searches through its own interface, but it does not replace an automation application or a download client.

An indexer test is more than a simple check that a TCP port answers. Prowlarr may request the indexer's capabilities, verify the expected XML structure, test authentication, and compare the response with the configured implementation. A reachable endpoint can therefore still fail because its certificate is invalid, its API key is rejected, its URL base is wrong, the selected definition expects another protocol, or its response omits required fields. Categories matter as well: a search source may be healthy while returning no useful results because the selected categories do not overlap the categories requested by an application.

This lab deliberately uses a local Torznab-compatible teaching service. It returns synthetic metadata and never contacts a public content indexer. That design makes protocol behavior observable while avoiding dependence on third-party availability, accounts, rate limits, or content. Prowlarr is installed from an official GitHub release asset selected for the host architecture. The release API response and a locally calculated SHA-256 digest are retained in the workspace. A local digest detects later changes to the downloaded file, but it does not independently prove publisher authenticity unless it is compared with a trusted publisher-provided value or signature.

Prowlarr's state is as important as its executable. The launcher supplies an explicit data directory and redirects home, cache, configuration, temporary, and .NET CLI paths into /opt/lab-classroom/class54/. This supports repeatable rollback and prevents the exercise from intentionally writing configuration into the learner's normal home directory. In production, Prowlarr should run as a dedicated, minimally privileged service account, use protected credentials, have dependable backups of its application data, and be exposed only through an authenticated administrative path. Indexer use must comply with applicable law, provider terms, and organizational policy.

## Architecture

### components
A self-contained Prowlarr release extracted under /opt/lab-classroom/class54/app/.
Prowlarr persistent state under /opt/lab-classroom/class54/data/.
A Python teaching indexer listening on 127.0.0.1:18080.
The Prowlarr web interface listening on port 9696.
A browser used for first-run configuration, indexer management, testing, and log review.

### data_flow
The administrator opens the Prowlarr web interface.
Prowlarr requests capabilities from http://127.0.0.1:18080/api?t=caps.
The teaching indexer returns supported searches and category metadata as Torznab XML.
Prowlarr issues a test search to the teaching indexer.
The teaching indexer returns one synthetic result containing no downloadable media.
Prowlarr records configuration and operational events in its class-specific data directory.

### ports
### 9696/tcp
Prowlarr web interface.

### 18080/tcp
Loopback-only Torznab teaching indexer.

### persistence_boundary
/opt/lab-classroom/class54/

## Required reading

- Prowlarr documentation: https://wiki.servarr.com/prowlarr
- Prowlarr installation documentation: https://wiki.servarr.com/prowlarr/installation
- Prowlarr settings documentation: https://wiki.servarr.com/prowlarr/settings
- Prowlarr indexer documentation: https://wiki.servarr.com/prowlarr/indexers
- Torznab specification repository: https://github.com/torznab/spec-1.3

## References

- Prowlarr project repository: https://github.com/Prowlarr/Prowlarr
- Prowlarr documentation: https://wiki.servarr.com/prowlarr
- Prowlarr installation documentation: https://wiki.servarr.com/prowlarr/installation
- Prowlarr indexer documentation: https://wiki.servarr.com/prowlarr/indexers
- Prowlarr settings documentation: https://wiki.servarr.com/prowlarr/settings
- Torznab specification: https://github.com/torznab/spec-1.3
- GitHub REST API release documentation: https://docs.github.com/en/rest/releases/releases
- Python urllib.request documentation: https://docs.python.org/3/library/urllib.request.html
- Python tarfile documentation: https://docs.python.org/3/library/tarfile.html

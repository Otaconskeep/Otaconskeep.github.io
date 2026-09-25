# Reading: Indexers, Trackers, and Usenet Providers

**Module:** Download Clients & Indexers
**Activity type:** Reading (Learn)
**Objective:** Differentiate a Usenet indexer, Usenet provider, torrent indexer, BitTorrent tracker, download client, and automation application.

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

## Required reading

- RFC 3977, Network News Transfer Protocol (NNTP): https://www.rfc-editor.org/rfc/rfc3977
- RFC 4642, Using Transport Layer Security with Network News Transfer Protocol: https://www.rfc-editor.org/rfc/rfc4642
- BitTorrent Enhancement Proposal 3, The BitTorrent Protocol Specification: https://www.bittorrent.org/beps/bep_0003.html
- Prowlarr documentation, Indexers: https://wiki.servarr.com/prowlarr/indexers
- SABnzbd documentation: https://sabnzbd.org/wiki/

## References

- IETF RFC 3977, Network News Transfer Protocol: https://www.rfc-editor.org/rfc/rfc3977
- IETF RFC 4642, Using Transport Layer Security with Network News Transfer Protocol: https://www.rfc-editor.org/rfc/rfc4642
- BitTorrent Enhancement Proposal 3, The BitTorrent Protocol Specification: https://www.bittorrent.org/beps/bep_0003.html
- BitTorrent Enhancement Proposal 5, DHT Protocol: https://www.bittorrent.org/beps/bep_0005.html
- Prowlarr documentation: https://wiki.servarr.com/prowlarr
- SABnzbd documentation: https://sabnzbd.org/wiki/
- Python json module documentation: https://docs.python.org/3/library/json.html
- Python pathlib documentation: https://docs.python.org/3/library/pathlib.html

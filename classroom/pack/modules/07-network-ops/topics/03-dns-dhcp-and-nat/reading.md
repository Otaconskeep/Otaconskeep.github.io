# Reading — DNS, DHCP, and NAT

**Module:** Network Operations
**Activity type:** Reading (Learn)
**Objective:** Describe the separate responsibilities of DNS, DHCP, and NAT

## Vocabulary

| Term | Meaning |
|---|---|
| DNS | The Domain Name System, a distributed naming system that maps names to records such as IPv4 addresses, IPv6 addresses, mail exchangers, aliases, and service metadata. |
| Recursive resolver | A DNS service that performs or coordinates lookups on behalf of clients and normally caches the resulting answers. |
| Authoritative server | A DNS server that publishes definitive records for a DNS zone rather than merely returning cached recursive results. |
| TTL | Time to live; the duration for which a DNS answer may normally remain cached before it should be refreshed. |
| DHCP | The Dynamic Host Configuration Protocol, which supplies clients with network parameters such as an address, subnet prefix, gateway, DNS servers, and lease duration. |
| Lease | A time-bounded assignment of an IP address and related configuration to a DHCP client. |
| Reservation | A DHCP policy that consistently associates a known client identifier with a designated address. |
| DORA | A common mnemonic for DHCP Discover, Offer, Request, and Acknowledgment. |
| NAT | Network Address Translation, which rewrites address information as traffic passes between address realms. |
| PAT | Port Address Translation, a many-to-one NAT technique that distinguishes concurrent flows by translated transport ports. |
| Translation table | State that associates an internal flow with its translated external address and port. |
| Hairpin NAT | A translation path that allows an internal client to reach an internally hosted service through an address normally presented as external. |
| Split-horizon DNS | A design in which different clients receive different DNS answers for the same name, often based on whether they are inside or outside a network. |

## Instruction

DNS, DHCP, and NAT solve different problems even though a small home router may present them as one feature set. DHCP gives a client the information needed to participate on an IP network. A new client initially lacks a usable address and commonly begins with a broadcast DHCP Discover. A server responds with an Offer, the client sends a Request identifying the selected offer, and the server completes the exchange with an Acknowledgment. The resulting lease can include an address, prefix, default gateway, DNS server addresses, lease duration, and other options. A reservation is not the same thing as manually configuring an address: it remains server-managed but consistently maps a known client identifier to an intended address.

DNS answers naming questions. A client usually asks a recursive resolver for a record such as the A record for an IPv4 address or the AAAA record for an IPv6 address. If the answer is not cached, the resolver follows referrals through the DNS hierarchy until it reaches an authoritative source or another valid conclusion. Caching reduces delay and query volume, but it also means record changes are not instant. TTL values influence how long compliant caches may reuse an answer. A failed name lookup does not automatically mean that routing is broken; testing connectivity by address and then testing name resolution helps separate the two failure domains. Likewise, receiving a DNS server through DHCP does not prove that the DNS server is reachable or that it has the required records.

NAT rewrites packet addressing at a boundary. In a common IPv4 homelab, many private clients share one upstream address. Port Address Translation tracks combinations of protocol, source address, source port, destination address, and destination port, then assigns translated source ports so return traffic can be associated with the correct internal conversation. This state is normally created by outbound traffic and expires when it becomes idle or the protocol state ends. Inbound publishing requires an intentional static mapping or equivalent policy because an unsolicited packet has no existing translation entry that identifies an internal destination.

The normal dependency chain is: DHCP supplies an address, route, and resolver; DNS converts a service name into an address; routing sends packets toward the destination; and NAT may rewrite the flow at an address boundary. These services can also be deployed independently. Static clients do not require DHCP, direct address access does not require DNS, and globally routed networks may not require NAT. Troubleshooting should therefore test each layer independently rather than treating internet access as a single feature. Confirm the client configuration, test the local gateway, query the intended resolver, inspect the returned record, verify the route, and then inspect translation state where NAT is actually present. Finally, NAT must not be treated as a complete security control. Address rewriting can incidentally prevent some unsolicited traffic when no mapping exists, but access policy, service authentication, patching, segmentation, and logging remain separate responsibilities.

## Architecture

### logical_flow
Client requests network configuration from the DHCP service.
DHCP supplies an address from 192.168.24.100 through 192.168.24.105, a /24 prefix, gateway 192.168.24.1, and DNS server 192.168.24.2.
Client asks the DNS service to resolve names in the lab.home.arpa zone.
The simulated gateway creates a source translation entry when a client initiates an external flow.
Return traffic is associated with the originating client by the translation tuple.

### components
### client_segment
192.168.24.0/24

### gateway
192.168.24.1

### dns_service
192.168.24.2

### dhcp_pool
192.168.24.100-192.168.24.105

### simulated_external_address
198.51.100.24

### lab_storage
/opt/lab-classroom/class24/

### scope_note
All services in this lab are modeled in files and Python data structures. The host network configuration is not changed, no packets are transmitted, and every persistent mutation remains under /opt/lab-classroom/class24/.

## Required reading

- Review IPv4 subnetting, including network, broadcast, usable host, and default gateway addresses.
- Review the roles of UDP and TCP ports in identifying application conversations.
- Review RFC 1918 private IPv4 address ranges.
- Read the overview sections of RFC 1034 and RFC 1035 for DNS concepts.
- Read the DHCP message-flow overview in RFC 2131.
- Read the traditional NAT terminology in RFC 3022.

## References

- RFC 1034, Domain Names—Concepts and Facilities: https://www.rfc-editor.org/rfc/rfc1034
- RFC 1035, Domain Names—Implementation and Specification: https://www.rfc-editor.org/rfc/rfc1035
- RFC 2131, Dynamic Host Configuration Protocol: https://www.rfc-editor.org/rfc/rfc2131
- RFC 2132, DHCP Options and BOOTP Vendor Extensions: https://www.rfc-editor.org/rfc/rfc2132
- RFC 3022, Traditional IP Network Address Translator: https://www.rfc-editor.org/rfc/rfc3022
- RFC 1918, Address Allocation for Private Internets: https://www.rfc-editor.org/rfc/rfc1918
- RFC 5737, IPv4 Address Blocks Reserved for Documentation: https://www.rfc-editor.org/rfc/rfc5737
- RFC 8375, Special-Use Domain home.arpa: https://www.rfc-editor.org/rfc/rfc8375
- IANA Domain Name System Parameters: https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
- IANA BOOTP and DHCP Parameters: https://www.iana.org/assignments/bootp-dhcp-parameters/bootp-dhcp-parameters.xhtml

# Reading: Local DNS and Friendly Service Names

**Module:** Edge Access & VPN
**Activity type:** Reading (Learn)
**Objective:** Explain the roles of stub resolvers, recursive resolvers, authoritative data, and DNS caches.

## Vocabulary

| Term | Meaning |
|---|---|
| DNS | The Domain Name System, a distributed naming system that maps names to records such as IPv4 and IPv6 addresses. |
| Stub resolver | The client-side component that sends DNS questions to a configured resolver on behalf of applications. |
| Recursive resolver | A DNS service that obtains answers for clients, commonly by consulting other DNS servers and caching the results. |
| Authoritative data | DNS data served from the source responsible for a namespace rather than learned from another resolver. |
| A record | A DNS resource record that maps a name to an IPv4 address. |
| AAAA record | A DNS resource record that maps a name to an IPv6 address. |
| CNAME record | A record that aliases one DNS name to another DNS name. |
| PTR record | A record generally used for reverse lookup from an address-oriented DNS name to a host name. |
| FQDN | A fully qualified domain name that identifies a name within the complete DNS hierarchy, such as dashboard.home.arpa. |
| TTL | Time to live, the number of seconds for which a DNS response may normally be cached. |
| NXDOMAIN | A DNS response code indicating that the requested domain name does not exist. |
| Split DNS | A design in which the answer for a name depends on which resolver or network view receives the query. |
| home.arpa | The special-use domain reserved by RFC 8375 for names within residential home networks. |

## Instruction

People remember names more reliably than addresses. A bookmark such as https://dashboard.home.arpa is easier to recognize and maintain than https://10.20.30.40. DNS supplies the translation, but it does not create application connectivity, configure a reverse proxy, or guarantee that a service is healthy. It only returns records in response to questions. A typical application asks the operating system's stub resolver for an address. The stub resolver sends the question to a configured recursive resolver, which may answer from cache, consult authoritative servers, or return an error. In a homelab, one resolver can also hold private records for internal services.

Local naming should use a deliberate namespace. RFC 8375 reserves home.arpa for residential home networks. The local suffix should generally be avoided for ordinary unicast DNS because it is conventionally associated with multicast DNS and may be handled differently by operating systems. Public domains that you do not control are also poor choices because future public records can conflict with private assumptions. Organizations that own a public domain may instead delegate or privately serve a subdomain, but that requires disciplined administration.

An A record maps a name to an IPv4 address, while an AAAA record maps a name to an IPv6 address. A CNAME points one name at another name and is useful for aliases, although clients must still resolve the target. DNS record design should represent stable service identities. For example, dashboard.home.arpa can remain constant while its address changes. Update the central record rather than editing bookmarks and application configurations across many clients.

Caching improves speed and reduces repeated work, but it also explains why DNS changes do not always appear immediately. A cached answer can remain in use until its TTL expires. Multiple clients can see different answers when they use different resolvers, retain different cache entries, or bypass the intended LAN resolver. Troubleshooting should therefore identify the exact resolver being queried, test the full name, inspect the response code, and compare direct queries with application behavior.

This lab runs dnsmasq only on 127.0.0.1:1053 and supplies an explicit configuration file. Port 1053 avoids the privileged standard DNS port and prevents the exercise from replacing the machine's configured resolver. The no-resolv and no-hosts settings make the source of the lab answers clear: only records written into the lab configuration are available. The local directive declares home.arpa as locally answered, so a missing name under that suffix should produce NXDOMAIN instead of being forwarded elsewhere. Because clients are not reconfigured, every test explicitly selects the server and port with dig.

A production design normally places a redundant or highly available resolver at stable LAN addresses, distributes those addresses to clients through network configuration, restricts who may query or administer the service, maintains both IPv4 and IPv6 records where appropriate, and monitors response health. Friendly names also belong in service documentation and certificates. If an HTTPS certificate does not contain the friendly name, DNS may resolve correctly while the browser still reports an identity error. Treat DNS as one layer in the service path, not as a substitute for routing, transport security, access control, or application monitoring.

## Architecture

### components
A client shell running dig.
A dnsmasq process bound only to 127.0.0.1 on UDP and TCP port 1053.
A lab-owned configuration file containing records for dashboard.home.arpa and nas.home.arpa.
A query log and process identifier stored beneath /opt/lab-classroom/class65/.

### query_flow
dig sends a DNS question directly to 127.0.0.1 port 1053.
dnsmasq checks the records defined in the lab configuration.
A known name receives an A-record answer.
An unknown name under home.arpa receives an NXDOMAIN response.
No upstream DNS server is consulted because the lab disables resolver-file processing and treats home.arpa as local.

### scope
The exercise is loopback-only. It does not modify the operating system resolver configuration, advertise DNS to other clients, or listen on a LAN interface.

### diagram
dig client -> 127.0.0.1:1053 -> dnsmasq -> local host-record data -> DNS response

## Required reading

- RFC 1034, Domain Names—Concepts and Facilities: https://www.rfc-editor.org/rfc/rfc1034
- RFC 1035, Domain Names—Implementation and Specification: https://www.rfc-editor.org/rfc/rfc1035
- RFC 8375, Special-Use Domain home.arpa: https://www.rfc-editor.org/rfc/rfc8375
- dnsmasq manual page: https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html
- BIND 9 dig manual: https://bind9.readthedocs.io/en/latest/manpages.html#dig-dns-lookup-utility

## References

- RFC 1034, Domain Names—Concepts and Facilities: https://www.rfc-editor.org/rfc/rfc1034
- RFC 1035, Domain Names—Implementation and Specification: https://www.rfc-editor.org/rfc/rfc1035
- RFC 2308, Negative Caching of DNS Queries: https://www.rfc-editor.org/rfc/rfc2308
- RFC 6762, Multicast DNS: https://www.rfc-editor.org/rfc/rfc6762
- RFC 8375, Special-Use Domain home.arpa: https://www.rfc-editor.org/rfc/rfc8375
- IANA Special-Use Domain Names registry: https://www.iana.org/assignments/special-use-domain-names/special-use-domain-names.xhtml
- dnsmasq documentation: https://thekelleys.org.uk/dnsmasq/doc.html
- BIND 9 dig documentation: https://bind9.readthedocs.io/en/latest/manpages.html#dig-dns-lookup-utility

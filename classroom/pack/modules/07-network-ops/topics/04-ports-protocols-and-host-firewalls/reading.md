# Reading: Ports, Protocols, and Host Firewalls

**Module:** Network Operations
**Activity type:** Reading (Learn)
**Objective:** Distinguish an IP address, a transport protocol, and a port number

## Vocabulary

| Term | Meaning |
|---|---|
| port | A 16-bit transport-layer number used to identify an application endpoint. TCP and UDP each have their own port-number space. |
| socket | An operating-system communication endpoint commonly identified by an address, transport protocol, and port. |
| listening socket | A socket waiting for inbound traffic. A listener must exist before a TCP connection can be accepted or a UDP datagram can be received. |
| TCP | A connection-oriented transport protocol that provides ordered delivery, retransmission, flow control, and connection state. |
| UDP | A datagram-oriented transport protocol that does not establish a connection or guarantee delivery, ordering, or retransmission. |
| ingress | Traffic entering a host through a network path from the perspective of that host. |
| egress | Traffic leaving a host through a network path from the perspective of that host. |
| loopback | A local-only network path used for communication within the same host. IPv4 loopback commonly uses addresses in 127.0.0.0/8. |
| stateful firewall | A firewall that tracks connection state and can treat packets belonging to established traffic differently from unrelated new traffic. |
| default policy | The action taken when no explicit rule matches, commonly default deny for inbound traffic and a deliberately selected policy for outbound traffic. |
| least privilege | Allowing only the protocols, ports, sources, destinations, and directions required for a defined service. |
| attack surface | The set of reachable services and interfaces that could be probed, misconfigured, or exploited. |

## Instruction

A network service is not identified by a port number alone. A complete endpoint includes an address, a transport protocol, and a port. TCP port 443 and UDP port 443 are separate endpoints because TCP and UDP maintain separate port spaces. The address also matters: a process bound to 127.0.0.1 is reachable only through the local loopback path, while a process bound to an address assigned to a physical or virtual network interface may be reachable from other systems. A wildcard bind can cover multiple local interfaces and therefore creates a larger exposure than a loopback-only bind.

TCP is connection-oriented. Before application data is exchanged, endpoints establish a connection, and the operating system tracks its state. TCP provides ordered delivery and retransmits missing data, but those features do not make the application secure; confidentiality and authentication require higher-layer protections. UDP sends independent datagrams without a connection handshake. It has lower protocol overhead but does not guarantee that a datagram arrives, arrives once, or arrives in order. A stateful host firewall may still track a temporary flow for UDP even though UDP itself has no connection state.

A host firewall evaluates traffic at the individual machine. Its policy can consider direction, interface, source and destination addresses, protocol, ports, and observed connection state. Rules are commonly processed according to an implementation-defined order, so policy authors must understand precedence rather than merely collecting allow and deny statements. A useful baseline is to permit established return traffic, narrowly allow required new inbound services, and use an intentional default action for everything else. Outbound filtering may also be appropriate for servers, appliances, and tightly controlled environments.

A firewall allowance does not create a service. If TCP port 18080 is allowed but no process is listening, a client still cannot use the service. Conversely, a listening service is not proof that remote clients can reach it: the service may be bound only to loopback, blocked by a host policy, blocked elsewhere in the path, or hidden behind routing and address-translation boundaries. Troubleshooting should therefore separate four questions: is the application running, where is it bound, does local communication work, and does policy permit the intended path?

Rules should describe a service requirement rather than a vague desire to make an application work. For example, allowing new TCP traffic to one administration port from a dedicated management subnet is narrower than allowing every protocol and port from every address. Record the reason, owner, source scope, destination port, and expected lifetime of an exception. Test administrative access before and after any real firewall change, preferably with an independent recovery path. This class does not alter the real host firewall. Instead, it creates loopback listeners and evaluates sample packet descriptions against a deterministic policy model stored entirely under the classroom directory.

## Architecture

### scope
One Linux host using only loopback network traffic and files under /opt/lab-classroom/class25/.

### components
A TCP or UDP client implemented with the Python standard library
A loopback-only TCP or UDP listener implemented with the Python standard library
A JSON policy containing ordered rules and direction-specific defaults
A policy evaluator that compares synthetic packet descriptions with the ordered rules

### traffic_flow
The listener binds specifically to 127.0.0.1 and an unprivileged port.
The client sends a message to the matching protocol and port.
The listener returns an acknowledgment and exits after one exchange.
Separately, the evaluator reads synthetic packet metadata rather than intercepting real traffic.
The evaluator selects the first matching rule or the default for the packet direction.

### trust_boundaries
Loopback traffic remains on the local host.
A service bound to an external interface would cross into a less-trusted network boundary.
The policy simulator is educational and does not enforce operating-system traffic.

### policy_model
Established inbound traffic is accepted first. New loopback TCP traffic to port 18080 and new loopback UDP traffic to port 15353 are accepted. Other ingress traffic is dropped by default, while egress traffic is accepted by default.

## Required reading

- Review the TCP/IP model, especially the network and transport layers.
- Read the Python socket module overview: https://docs.python.org/3/library/socket.html
- Read the IANA service name and port number registry overview: https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
- Review IPv4 loopback addressing and the special role of 127.0.0.0/8.

## References

- IANA Service Name and Transport Protocol Port Number Registry: https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
- Python socket library documentation: https://docs.python.org/3/library/socket.html
- RFC 9293, Transmission Control Protocol: https://www.rfc-editor.org/rfc/rfc9293
- RFC 768, User Datagram Protocol: https://www.rfc-editor.org/rfc/rfc768
- RFC 1122, Requirements for Internet Hosts: https://www.rfc-editor.org/rfc/rfc1122
- RFC 6890, Special-Purpose IP Address Registries: https://www.rfc-editor.org/rfc/rfc6890
- NIST SP 800-41 Revision 1, Guidelines on Firewalls and Firewall Policy: https://csrc.nist.gov/pubs/sp/800/41/r1/final

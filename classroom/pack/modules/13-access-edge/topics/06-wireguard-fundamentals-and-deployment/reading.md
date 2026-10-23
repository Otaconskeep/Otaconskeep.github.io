# Reading: WireGuard Fundamentals and Deployment

**Module:** Edge Access & VPN
**Activity type:** Reading (Learn)
**Objective:** Explain how WireGuard uses public keys as peer identities.

## Vocabulary

| Term | Meaning |
|---|---|
| Peer | A WireGuard participant identified by a public key and associated with permitted tunnel addresses. |
| Interface | The local WireGuard device and its private-key, address, and listening-port configuration. |
| Private key | Secret identity material that must remain only on the peer that owns it. |
| Public key | A value derived from a private key and distributed to remote peers so they can identify the key owner. |
| Preshared key | Optional symmetric secret mixed into the peer relationship as an additional cryptographic layer; it does not replace the public-key identities. |
| AllowedIPs | A peer-specific list that participates in outbound peer selection and limits which inner source addresses are accepted from that peer. |
| Endpoint | The reachable outer IP address or DNS name and UDP port used to contact a remote peer. |
| Handshake | The authenticated cryptographic exchange used to establish fresh transport keys between peers. |
| Endpoint roaming | WireGuard's ability to update a peer's known endpoint after authenticated traffic arrives from a new source address. |
| PersistentKeepalive | An optional interval that causes periodic authenticated packets to preserve state in intervening NAT devices. |
| Split tunnel | A design in which only selected destination prefixes are routed through the tunnel. |
| Full tunnel | A design in which default IPv4 and possibly IPv6 routes are sent through the tunnel. |

## Instruction

WireGuard is a layer-3 encrypted tunnel. It transports IP packets between peers over UDP, but it does not assign users, issue certificates, provide application authentication, or automatically make a remote network routable. Every peer owns a private key and shares only its public key. A peer configuration therefore resembles a compact mapping between cryptographic identities and network prefixes.

The local Interface section contains the local private key and usually a tunnel address. A listening port is normally required on a stable server, while a roaming client can often use an automatically selected source port. Each Peer section identifies one remote system by public key. Endpoint tells the local system where to send the first encrypted packet. A stable client endpoint does not normally need to be configured on the server because the server can learn the client's current endpoint from authenticated traffic.

AllowedIPs is central to correct design. For outbound traffic, it helps select the peer that should receive a destination prefix. For inbound traffic, it limits which inner source addresses are valid for that peer. A server should generally assign a unique /32 IPv4 tunnel address to each remote-access peer rather than giving every peer the complete tunnel subnet. Overlapping entries can produce surprising peer selection and should be avoided unless the design has been carefully analyzed. AllowedIPs is not a substitute for an explicit authorization policy around services reachable through the tunnel.

PersistentKeepalive is not a generic performance setting. A value such as 25 seconds is useful when a peer behind NAT must keep an idle mapping available for unsolicited return traffic. Stable peers with direct reachability usually do not need it. Keepalive traffic also creates periodic metadata, so it should be enabled only where operationally necessary.

A split-tunnel client lists only the private destinations that belong in the tunnel. A full-tunnel client uses default prefixes, commonly 0.0.0.0/0 and ::/0, and requires deliberate planning for forwarding, DNS, IPv6, packet-filter policy, egress translation, and loss of access if the tunnel fails. Route symmetry matters in both designs: the destination network must know how to return traffic to the tunnel client, or an approved translation design must provide that return path.

A disciplined production deployment separates preparation from activation. First allocate nonconflicting addresses, document ownership, generate keys on the systems that will use them, exchange only public keys, and stage configurations with restrictive file permissions. Next validate peer key relationships, destination prefixes, endpoint resolution, UDP reachability, forwarding requirements, and return routes. Activate one peer during a maintenance window, confirm a recent handshake and bidirectional traffic, and then expand gradually. The laboratory deliberately stops before activation: it creates representative configuration artifacts under the class directory and verifies them without changing interfaces, routes, packet-filter state, services, or system configuration.

## Architecture

### scenario
A staged split-tunnel relationship between one stable gateway and one roaming client.

### components
Gateway tunnel address: 10.69.0.1/24.
Client tunnel address: 10.69.0.2/24.
Documentation-only gateway endpoint: vpn.example.invalid:51820.
Gateway peer authorization: client source address 10.69.0.2/32.
Client routed destination: 10.69.0.0/24.
Optional shared preshared key stored on both staged peers.

### control_plane
Administrators distribute public keys, assigned prefixes, endpoint information, and configuration metadata. Private keys remain local to their owners.

### data_plane
An inner IP packet matching a peer's AllowedIPs is encrypted and placed inside an outer UDP packet. The receiving peer authenticates and decrypts it before normal IP processing.

### traffic_flow
The client selects the gateway peer for destinations in 10.69.0.0/24.
The client sends encrypted UDP traffic to vpn.example.invalid:51820 in a real deployment.
The gateway authenticates the client and accepts only permitted inner source addresses.
Return traffic for 10.69.0.2 is selected for the client peer and sent to its most recently authenticated endpoint.

### trust_boundaries
Private-key files are high-value secrets.
The public network can observe outer addresses, ports, timing, and packet sizes but not the encrypted inner payload.
Tunnel authentication establishes peer identity, not user identity or application authorization.
Networks reached through the gateway remain separate trust zones and require their own access policy.

## Required reading

- WireGuard Quick Start: https://www.wireguard.com/quickstart/
- WireGuard protocol overview: https://www.wireguard.com/protocol/
- wg manual page: https://man7.org/linux/man-pages/man8/wg.8.html
- wg-quick manual page: https://man7.org/linux/man-pages/man8/wg-quick.8.html
- RFC 5737, IPv4 Address Blocks Reserved for Documentation: https://www.rfc-editor.org/rfc/rfc5737

## References

- WireGuard official site: https://www.wireguard.com/
- WireGuard Quick Start: https://www.wireguard.com/quickstart/
- WireGuard Protocol and Cryptography: https://www.wireguard.com/protocol/
- wg(8) manual: https://man7.org/linux/man-pages/man8/wg.8.html
- wg-quick(8) manual: https://man7.org/linux/man-pages/man8/wg-quick.8.html
- Linux kernel WireGuard documentation: https://www.kernel.org/doc/html/latest/networking/device_drivers/wireguard.html
- RFC 5737, IPv4 Address Blocks Reserved for Documentation: https://www.rfc-editor.org/rfc/rfc5737
- RFC 2606, Reserved Top Level DNS Names: https://www.rfc-editor.org/rfc/rfc2606

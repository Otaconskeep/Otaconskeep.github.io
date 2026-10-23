# Class 69: WireGuard Fundamentals and Deployment

**Learning objective:** Explain how WireGuard uses public keys as peer identities.; Distinguish the Interface and Peer sections of a WireGuard configuration.; Explain the routing and peer-selection effects of AllowedIPs.; Generate private keys, public keys, and optional preshared keys without printing private material.; Build a least-privilege split-tunnel configuration for two peers.; Describe endpoint roaming, keepalive behavior, NAT considerations, and route symmetry.; Validate staged configurations and key relationships before deployment.; Plan a production rollout, verification process, key rotation, and rollback procedure.
**Bloom level:** Understand / Apply
**Track:** Networking and Secure Remote Access · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Teach the cryptographic identity model, routing behavior, configuration structure, deployment planning, verification methods, and operational security considerations of WireGuard. The laboratory creates and validates a staged site-to-site configuration without changing host networking or activating a tunnel.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-26
**Compatibility:** ### operating_systems
Linux systems supported by the installed WireGuard implementation and wireguard-tools package.

### required_commands
wg
python3
install
stat
grep
find

### configuration_note
Address is commonly interpreted by wg-quick or an equivalent network manager rather than by the lower-level wg configuration parser itself.

### shell_assumption
Commands use a POSIX-compatible shell with standard command substitution and redirection.

### network_effect
The laboratory has no intended network effect because configurations are staged but never activated.

### endpoint_compatibility
vpn.example.invalid is reserved for documentation and must be replaced before any real deployment.

### ipv6_note
The exercise is IPv4-only for clarity. Production designs must explicitly decide whether IPv6 is tunneled, routed separately, or disabled according to policy.

## Learning objective

- Explain how WireGuard uses public keys as peer identities.
- Distinguish the Interface and Peer sections of a WireGuard configuration.
- Explain the routing and peer-selection effects of AllowedIPs.
- Generate private keys, public keys, and optional preshared keys without printing private material.
- Build a least-privilege split-tunnel configuration for two peers.
- Describe endpoint roaming, keepalive behavior, NAT considerations, and route symmetry.
- Validate staged configurations and key relationships before deployment.
- Plan a production rollout, verification process, key rotation, and rollback procedure.

## Why this matters

Teach the cryptographic identity model, routing behavior, configuration structure, deployment planning, verification methods, and operational security considerations of WireGuard. The laboratory creates and validates a staged site-to-site configuration without changing host networking or activating a tunnel.

## Prerequisites

- Comfort using a Linux shell and reading INI-style configuration files.
- Basic understanding of IPv4 addressing, CIDR notation, routing tables, UDP, and network address translation.
- A Linux lab host with Python 3 and the WireGuard command-line utility installed before class.
- Write access to /opt/lab-classroom/class69/.
- Understanding that the documentation-only endpoint vpn.example.invalid is intentionally nonfunctional.

## Required reading

- WireGuard Quick Start: https://www.wireguard.com/quickstart/
- WireGuard protocol overview: https://www.wireguard.com/protocol/
- wg manual page: https://man7.org/linux/man-pages/man8/wg.8.html
- wg-quick manual page: https://man7.org/linux/man-pages/man8/wg-quick.8.html
- RFC 5737, IPv4 Address Blocks Reserved for Documentation: https://www.rfc-editor.org/rfc/rfc5737

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

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

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### tasks
Design a three-client address plan using unique /32 IPv4 assignments and write the gateway-side Peer fields for each client without generating real keys.
Compare a split-tunnel design for 10.20.0.0/16 with a full-tunnel design. List the route, DNS, IPv6, forwarding, egress, monitoring, and rollback questions that differ.
Draw the outer and inner packet headers for a client packet sent to a private application through a gateway.
Write a key-rotation runbook that maintains administrative access and never transfers private keys between peers.
Explain how a handshake can succeed even when a destination service remains unreachable.

### submission
Submit the address plan, configuration sketches containing only invented labels rather than key material, packet-flow diagram, rotation runbook, and troubleshooting explanation.

## Feynman teach-back

### prompt
Explain WireGuard to a new administrator without using the words VPN, magic, or secure by default.

### model_explanation
Each machine has a secret number and a shareable public identity derived from it. A machine keeps a list of remote public identities and the IP addresses each identity is allowed to represent. When an inner packet matches one of those address lists, the machine encrypts it for that peer and sends it inside UDP. The receiver proves which key produced the packet, decrypts it, and rejects an inner source address that the configured peer is not allowed to claim. The tunnel protects packets between the peers, while routing, service authorization, DNS, forwarding, and recovery still have to be designed separately.

### self_check
Can you explain why two peers must not exchange private keys?
Can you describe both the outbound and inbound roles of AllowedIPs?
Can you explain why a successful handshake does not prove that an application is reachable?
Can you explain when PersistentKeepalive helps and why it should not be enabled thoughtlessly?

## Retrieval check

1. What cryptographic value identifies a WireGuard peer to another peer?
2. Why should a gateway commonly assign 10.69.0.2/32 rather than 10.69.0.0/24 to one client's AllowedIPs?
3. What two major roles does AllowedIPs perform?
4. When is PersistentKeepalive commonly useful?
5. Does a recent handshake prove that an application behind the peer is reachable? Explain.
6. What is the primary routing difference between split-tunnel and full-tunnel configurations?
7. Why does the server often omit Endpoint for a roaming client?
8. What information remains observable to the outer network even though the inner packet is encrypted?
9. What should happen if a peer's private key is suspected of compromise?
10. Why is vpn.example.invalid used in this laboratory?

## Guided lab

### scope
All persistent changes are confined to /opt/lab-classroom/class69/. The exercise does not create an interface, alter routing, contact the example endpoint, or modify host services.

### steps
### name
Confirm required tools

### commands
command -v wg
python3 --version

### notes
These commands are read-only. Stop if either required program is unavailable; do not install packages as part of this constrained laboratory.
### name
Create protected laboratory directories

### commands
install -d -m 700 /opt/lab-classroom/class69/keys /opt/lab-classroom/class69/configs

### notes
The directories are inside the only permitted mutation path.
### name
Generate peer keys and a preshared key

### commands
set -eu; umask 077; LAB=/opt/lab-classroom/class69; wg genkey > "$LAB/keys/gateway.private"; wg pubkey < "$LAB/keys/gateway.private" > "$LAB/keys/gateway.public"; wg genkey > "$LAB/keys/client.private"; wg pubkey < "$LAB/keys/client.private" > "$LAB/keys/client.public"; wg genpsk > "$LAB/keys/peer.psk"

### notes
Private values are redirected directly into protected files. Do not display private-key or preshared-key files in shared terminals, transcripts, tickets, or screenshots.
### name
Create the staged gateway configuration

### commands
set -eu; umask 077; LAB=/opt/lab-classroom/class69; GATEWAY_PRIVATE=$(cat "$LAB/keys/gateway.private"); CLIENT_PUBLIC=$(cat "$LAB/keys/client.public"); PEER_PSK=$(cat "$LAB/keys/peer.psk"); printf '%s\n' '[Interface]' "PrivateKey = $GATEWAY_PRIVATE" 'Address = 10.69.0.1/24' 'ListenPort = 51820' '' '[Peer]' "PublicKey = $CLIENT_PUBLIC" "PresharedKey = $PEER_PSK" 'AllowedIPs = 10.69.0.2/32' > "$LAB/configs/gateway.conf"; unset GATEWAY_PRIVATE CLIENT_PUBLIC PEER_PSK

### notes
The peer receives a unique /32 authorization on the gateway.
### name
Create the staged client configuration

### commands
set -eu; umask 077; LAB=/opt/lab-classroom/class69; CLIENT_PRIVATE=$(cat "$LAB/keys/client.private"); GATEWAY_PUBLIC=$(cat "$LAB/keys/gateway.public"); PEER_PSK=$(cat "$LAB/keys/peer.psk"); printf '%s\n' '[Interface]' "PrivateKey = $CLIENT_PRIVATE" 'Address = 10.69.0.2/24' '' '[Peer]' "PublicKey = $GATEWAY_PUBLIC" "PresharedKey = $PEER_PSK" 'Endpoint = vpn.example.invalid:51820' 'AllowedIPs = 10.69.0.0/24' 'PersistentKeepalive = 25' > "$LAB/configs/client.conf"; unset CLIENT_PRIVATE GATEWAY_PUBLIC PEER_PSK

### notes
The reserved .invalid name prevents accidental use as a real service endpoint. The selected prefix demonstrates split tunneling.
### name
Verify permissions and cryptographic relationships

### commands
stat -c '%a %n' /opt/lab-classroom/class69/keys /opt/lab-classroom/class69/configs /opt/lab-classroom/class69/keys/gateway.private /opt/lab-classroom/class69/keys/client.private /opt/lab-classroom/class69/keys/peer.psk /opt/lab-classroom/class69/configs/gateway.conf /opt/lab-classroom/class69/configs/client.conf
set -eu; LAB=/opt/lab-classroom/class69; test "$(wg pubkey < "$LAB/keys/gateway.private")" = "$(cat "$LAB/keys/gateway.public")"; test "$(wg pubkey < "$LAB/keys/client.private")" = "$(cat "$LAB/keys/client.public")"; echo 'Key derivation checks passed.'
set -eu; LAB=/opt/lab-classroom/class69; grep -Fqx 'AllowedIPs = 10.69.0.2/32' "$LAB/configs/gateway.conf"; grep -Fqx 'AllowedIPs = 10.69.0.0/24' "$LAB/configs/client.conf"; grep -Fqx 'Endpoint = vpn.example.invalid:51820' "$LAB/configs/client.conf"; echo 'Configuration policy checks passed.'

### notes
The checks avoid printing secret values. Directories should report mode 700, while generated files should report mode 600.

### deployment_plan
Replace documentation addresses and names with approved production values.
Generate each production private key on the peer that will own it.
Exchange and independently verify only public keys.
Confirm that tunnel and routed prefixes do not overlap existing networks.
Confirm outer UDP reachability, forwarding policy, return routing, DNS behavior, and IPv6 scope.
Capture a known-good out-of-band access method before activation.
Activate one peer during a change window and inspect handshake age, byte counters, routes, and application reachability.
Stop and revert if administrative access, expected routing, or policy enforcement changes unexpectedly.

## Expected results

- The directories /opt/lab-classroom/class69/keys and /opt/lab-classroom/class69/configs exist with mode 700.
- The key directory contains gateway.private, gateway.public, client.private, client.public, and peer.psk.
- The configuration directory contains gateway.conf and client.conf with mode 600.
- Deriving a public key from each private key reproduces the corresponding saved public key.
- The gateway configuration authorizes the client as 10.69.0.2/32.
- The client configuration routes only 10.69.0.0/24 through the staged peer.
- The client endpoint is vpn.example.invalid:51820 and is intentionally unsuitable for live use.
- No WireGuard interface, route, service, or host network policy is changed by the lab.

## Verification checkpoints

- [ ] Run: stat -c '%a %n' /opt/lab-classroom/class69/keys /opt/lab-classroom/class69/configs. Both directories should report 700.
- [ ] Run: stat -c '%a %n' /opt/lab-classroom/class69/keys/gateway.private /opt/lab-classroom/class69/keys/client.private /opt/lab-classroom/class69/keys/peer.psk /opt/lab-classroom/class69/configs/gateway.conf /opt/lab-classroom/class69/configs/client.conf. Each file should report 600.
- [ ] Run: test "$(wg pubkey < /opt/lab-classroom/class69/keys/gateway.private)" = "$(cat /opt/lab-classroom/class69/keys/gateway.public)" && echo PASS. The output should be PASS.
- [ ] Run: test "$(wg pubkey < /opt/lab-classroom/class69/keys/client.private)" = "$(cat /opt/lab-classroom/class69/keys/client.public)" && echo PASS. The output should be PASS.
- [ ] Run: grep -Fqx 'AllowedIPs = 10.69.0.2/32' /opt/lab-classroom/class69/configs/gateway.conf && echo PASS. The output should be PASS.
- [ ] Run: grep -Fqx 'AllowedIPs = 10.69.0.0/24' /opt/lab-classroom/class69/configs/client.conf && echo PASS. The output should be PASS.
- [ ] Run: grep -Fqx 'Endpoint = vpn.example.invalid:51820' /opt/lab-classroom/class69/configs/client.conf && echo PASS. The output should be PASS.
- [ ] Confirm through the host's normal read-only network inspection process that no interface or route was added for this staged exercise.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The wg command is not found. | The WireGuard command-line utilities were not installed before the constrained lab. | Stop the lab and ask the lab administrator to prepare the required package outside the exercise. Do not modify the host package set during this lab. |
| Key generation reports permission denied. | The learner cannot write to /opt/lab-classroom/class69/ or an existing directory has incompatible ownership. | Have the lab administrator correct ownership only within /opt/lab-classroom/class69/, then repeat the affected generation step. |
| A key derivation comparison fails. | A public-key file was copied from the wrong peer, a key file was altered, or an earlier command only partially completed. | Do not mix individual files from different attempts. Remove the staged artifacts using the documented rollback procedure, regenerate the complete key set, and rebuild both configurations. |
| A configuration policy check fails. | The configuration was manually edited, whitespace or capitalization changed, or gateway and client prefixes were reversed. | Review the intended roles, recreate the affected file from the lab command, and repeat the exact-match checks. |
| A future live deployment has no handshake. | Possible causes include mismatched public keys, mismatched preshared keys, an incorrect endpoint, blocked UDP traffic, an inactive listener, or incorrect system time. | Compare public-key fingerprints through a trusted channel, confirm both peers use the same preshared key, verify endpoint resolution and UDP reachability, and inspect listener and handshake state without exposing private material. |
| A future live deployment shows a handshake but cannot pass application traffic. | AllowedIPs, local routes, forwarding policy, destination-side return routes, address translation, MTU, or service authorization may be incorrect. | Trace the inner source and destination in both directions, inspect route selection on every hop, verify that each peer owns the claimed source prefix, test smaller packets for an MTU problem, and confirm the destination service permits the tunnel source. |
| A roaming client works briefly and then becomes unreachable while idle. | An intervening NAT mapping expires when no authenticated traffic is sent. | Apply PersistentKeepalive only to the NATed peer that needs inbound reachability and validate an interval appropriate for the environment. |
| Internet access unexpectedly follows the tunnel in a future deployment. | A default prefix was placed in the client's AllowedIPs, creating a full-tunnel route. | Restore the intended split-tunnel prefixes and verify both IPv4 and IPv6 route scope before reactivation. |

## Security considerations

### key_handling
Generate production private keys locally on the systems that will own them.
Never transmit, paste, log, or ticket private keys.
Treat a preshared key as secret on both peers and rotate it if either copy may be exposed.
Protect configurations because they commonly embed private and preshared keys.
Use an authenticated secondary channel to verify public-key fingerprints.

### least_privilege
Assign each client only the individual tunnel address and destination prefixes it needs.
Avoid broad AllowedIPs when a smaller set accurately represents the peer.
Apply service-level and network-level authorization in addition to tunnel authentication.
Separate administrative access from general user or application tunnels where practical.

### operational_guidance
WireGuard encrypts traffic between peers but does not make activity anonymous.
Outer IP addresses, UDP ports, packet sizes, and timing remain observable.
A recent handshake proves cryptographic peer contact, not successful application authorization.
Plan both IPv4 and IPv6 explicitly to avoid bypasses or accidental loss of connectivity.
Maintain an out-of-band recovery path before changing remote access or default routing.
Record peer ownership, assigned prefixes, key creation date, intended endpoint, and rotation history without recording private keys.

### rotation
Introduce a newly generated peer identity through a controlled configuration change, verify it, remove the old public-key authorization, and securely retire old secret material according to organizational policy. WireGuard peer identity changes are configuration changes rather than certificate renewals.

### incident_response
If a private or preshared key is suspected of exposure, treat the associated identity as compromised. Remove or replace its authorization, generate fresh secret material, verify the new public key through a trusted channel, review reachable services, and inspect available connection metadata for unexpected use.

## Rollback

### scope
Rollback deletes only artifacts created under /opt/lab-classroom/class69/. It cannot recover deleted keys; regeneration creates new identities.

### commands
find /opt/lab-classroom/class69 -type f -delete
find /opt/lab-classroom/class69 -depth -type d -empty -delete

### verification
Run: test ! -e /opt/lab-classroom/class69 && echo 'Rollback complete.'
If the top directory intentionally remains, run: find /opt/lab-classroom/class69 -mindepth 1 -print. Successful content cleanup produces no output.

### production_note
For a live deployment, rollback must also restore the previously approved peer configuration, route behavior, forwarding policy, name resolution, and service state through the environment's change-management system. The constrained lab performs none of those live changes.

## Video narration notes

Welcome to Class 69, WireGuard Fundamentals and Deployment. WireGuard builds encrypted layer-3 relationships between peers. Each peer owns a private key and distributes only its public key. The local Interface section describes the local identity and tunnel address. Each Peer section identifies a remote public key and states which network prefixes belong to that peer.

Pay special attention to AllowedIPs. When sending traffic, WireGuard uses matching prefixes to determine the peer. When receiving traffic, it checks whether the authenticated peer is allowed to claim the inner source address. This means an overly broad prefix is both a routing decision and an authorization mistake. A gateway should normally assign each client a unique host prefix.

Endpoint specifies where an initial outer UDP packet should be sent. A stable gateway commonly has a configured endpoint on clients. A roaming client's endpoint can be learned from authenticated traffic, so the gateway may not need a fixed endpoint for that client. PersistentKeepalive can maintain a NAT mapping, but it should be used because the path requires it, not because it sounds faster.

In this lab, we generate gateway and client identities, derive public keys, generate an optional preshared key, and build two staged configurations. The gateway permits only the client's individual tunnel address. The client routes the class subnet through the gateway and points to a deliberately invalid documentation endpoint. We then verify permissions, derive the public keys again, and test exact policy lines without displaying private values.

Nothing is activated. No interface or route is created, and no host network policy is changed. This separation reflects good production practice: prepare and inspect first, then activate during a controlled window with an independent recovery path. In production, confirm address allocation, key ownership, outer UDP reachability, return routing, forwarding, DNS, IPv6, MTU, service authorization, and rollback. Finally, remember that a handshake proves peer authentication and key agreement. It does not prove that every route or application beyond the peer is functioning.

## References

- WireGuard official site: https://www.wireguard.com/
- WireGuard Quick Start: https://www.wireguard.com/quickstart/
- WireGuard Protocol and Cryptography: https://www.wireguard.com/protocol/
- wg(8) manual: https://man7.org/linux/man-pages/man8/wg.8.html
- wg-quick(8) manual: https://man7.org/linux/man-pages/man8/wg-quick.8.html
- Linux kernel WireGuard documentation: https://www.kernel.org/doc/html/latest/networking/device_drivers/wireguard.html
- RFC 5737, IPv4 Address Blocks Reserved for Documentation: https://www.rfc-editor.org/rfc/rfc5737
- RFC 2606, Reserved Top Level DNS Names: https://www.rfc-editor.org/rfc/rfc2606

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

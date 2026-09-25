# Reading: VPN Binding, Kill Switches, and Leak Verification

**Module:** Download Clients & Indexers
**Activity type:** Reading (Learn)
**Objective:** Explain why an application bound to a VPN address is not automatically protected after that address or interface disappears.

## Vocabulary

| Term | Meaning |
|---|---|
| VPN tunnel | A logical network path that encapsulates traffic between peers. A tunnel can be operational even when individual applications are not using it. |
| Socket binding | Associating a socket with a local address or, on supported systems, a specific interface. Address binding constrains the local source address but is not a complete egress security policy. |
| Wildcard bind | A bind to all local addresses, commonly represented by 0.0.0.0 for IPv4 or :: for IPv6. For listeners this accepts traffic on multiple interfaces; for outbound applications, behavior depends on the application and operating system. |
| Policy routing | Route selection based on rules beyond the destination alone, such as source address, packet mark, or incoming interface. |
| Kill switch | A fail-closed network policy that prevents protected traffic from using an unauthorized path when the VPN is unavailable or misconfigured. |
| Control-plane exception | A narrowly scoped allowance needed to establish and maintain the VPN itself, such as traffic to a specific VPN endpoint through the physical uplink. |
| DNS leak | Name-resolution traffic reaching a resolver through an unauthorized interface or outside the intended encrypted path. |
| IPv6 leak | IPv6 traffic bypassing an IPv4-only tunnel or policy because IPv6 remains available through another interface. |
| Fail-open | A failure mode in which protected traffic falls back to an ordinary network path after the preferred secure path disappears. |
| Fail-closed | A failure mode in which protected traffic is denied when the authorized secure path is unavailable. |
| Negative test | A test that deliberately removes or breaks an expected dependency and confirms that prohibited behavior remains impossible. |
| Leak verification | Evidence-driven testing of addresses, routes, DNS paths, protocol families, and failure behavior rather than reliance on a VPN connected indicator. |

## Instruction

VPN privacy is a path-enforcement problem, not merely a tunnel-status problem. An application can report that it is bound to a VPN address while another subsystem still uses the ordinary uplink. Conversely, a host default route can point through a VPN while a policy-routing rule, container namespace, explicit proxy, IPv6 route, or privileged application selects another path. Treat application binding, route selection, and packet filtering as separate controls. Binding narrows where a socket may originate or listen. Routing determines the candidate path. A host packet filter enforces whether the selected path is permitted. Defense in depth uses all three where practical, but the packet filter is normally the final fail-closed control.

A useful kill-switch design begins with an explicit traffic inventory. Identify the protected process or service identity, the tunnel interface, the VPN endpoint address and port, DNS resolvers, local management networks, and any intentionally reachable LAN services. Start from deny-by-default for protected egress, then add narrow allowances. The VPN control-plane exception must normally use the physical uplink so the tunnel can be created. That exception should be limited to the actual endpoint, transport, and port rather than allowing arbitrary Internet traffic. Protected data traffic is then allowed only through the tunnel. If the endpoint is named rather than addressed directly, bootstrap DNS becomes part of the threat model and must be handled deliberately.

Binding to a VPN address is helpful but incomplete. If software cannot create a socket after the address disappears, it may fail safely; however, implementations differ, long-lived sockets may behave differently, and a restarted application may choose another address unless policy prevents it. Binding only IPv4 does not constrain IPv6. Binding a service listener also answers an inbound-exposure question, which is different from controlling outbound connections. Interface-based binding can be stronger on supported systems, but it may require privileges and still should not replace egress enforcement.

Verification must test both success and failure. While the VPN is healthy, inspect the selected route, local source address, resolver path, IPv4 behavior, IPv6 behavior, and application-specific proxy settings. Then remove the modeled VPN path and confirm that protected traffic stops rather than moving to the uplink. Repeat after application restart, VPN restart, address changes, and host reboot. Containers and virtual machines need separate inspection because they may have their own routes and packet-filter traversal. Browser WebRTC, encrypted DNS, and extension-managed proxies can also behave differently from ordinary command-line traffic. A public IP-check page is only one observation; it does not prove that DNS, IPv6, alternate processes, or failure transitions are protected. The lab below is deliberately a local policy simulation. It teaches test design without changing routes, interfaces, DNS, or host enforcement, and its report must not be represented as proof that the real host is leak-free.

## Architecture

### layers
### name
Application layer

### role
Selects the intended local VPN address or interface and avoids unrestricted fallback behavior.
### name
Routing layer

### role
Selects the tunnel for protected destinations and accounts for source-based rules, packet marks, and alternate routing tables.
### name
Enforcement layer

### role
Allows the VPN control plane through the uplink, permits protected data through the tunnel, and denies unauthorized egress.
### name
Name-resolution layer

### role
Ensures DNS requests use an approved resolver over an approved path.
### name
Verification layer

### role
Tests IPv4, IPv6, DNS, application traffic, restart behavior, and tunnel-loss behavior.

### reference_flow
The physical uplink reaches only the configured VPN endpoint for tunnel establishment, plus explicitly approved local-management destinations.
The VPN client creates the logical tunnel interface and installs or activates the intended routing policy.
The protected application uses a VPN-local source or is classified by a process, user, namespace, or packet mark.
Protected data may leave only through the VPN interface.
DNS follows the VPN path or is blocked if the approved resolver is unavailable.
When the tunnel disappears, protected traffic is denied rather than rerouted through the uplink.

### trust_boundaries
Between the protected application and the host networking stack.
Between the host routing decision and packet-filter enforcement.
Between the physical uplink and the VPN tunnel.
Between the host and container or virtual-machine network namespaces.
Between applications and any locally or remotely configured DNS resolver.

## Required reading

- Linux ip-route manual: https://man7.org/linux/man-pages/man8/ip-route.8.html
- Linux ip-rule manual: https://man7.org/linux/man-pages/man8/ip-rule.8.html
- Linux socket manual: https://man7.org/linux/man-pages/man7/socket.7.html
- WireGuard routing and namespace discussion: https://www.wireguard.com/netns/
- OpenVPN community documentation: https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/
- RFC 4193, Unique Local IPv6 Unicast Addresses: https://www.rfc-editor.org/rfc/rfc4193
- RFC 5737, IPv4 Address Blocks Reserved for Documentation: https://www.rfc-editor.org/rfc/rfc5737

## References

- Linux socket manual, including socket binding concepts: https://man7.org/linux/man-pages/man7/socket.7.html
- Linux ip-route manual: https://man7.org/linux/man-pages/man8/ip-route.8.html
- Linux ip-rule manual: https://man7.org/linux/man-pages/man8/ip-rule.8.html
- Linux network namespaces manual: https://man7.org/linux/man-pages/man7/network_namespaces.7.html
- WireGuard namespace and routing integration: https://www.wireguard.com/netns/
- WireGuard quick start: https://www.wireguard.com/quickstart/
- OpenVPN 2.6 reference manual: https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/
- nftables project documentation: https://wiki.nftables.org/wiki-nftables/index.php/Main_Page
- RFC 6724, Default Address Selection for IPv6: https://www.rfc-editor.org/rfc/rfc6724
- RFC 8305, Happy Eyeballs Version 2: https://www.rfc-editor.org/rfc/rfc8305
- RFC 7858, DNS over TLS: https://www.rfc-editor.org/rfc/rfc7858
- RFC 8484, DNS Queries over HTTPS: https://www.rfc-editor.org/rfc/rfc8484

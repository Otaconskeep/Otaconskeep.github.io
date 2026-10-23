# Reading: Tailscale for Homelab Remote Access

**Module:** Edge Access & VPN
**Activity type:** Reading (Learn)
**Objective:** Explain how Tailscale separates identity and policy decisions from encrypted peer-to-peer packet transport.

## Vocabulary

| Term | Meaning |
|---|---|
| Tailnet | The private Tailscale network containing authorized users, devices, policy, and administrative settings. |
| Coordination plane | The service that distributes identity, key, endpoint, and policy information so nodes can discover one another. It is distinct from the encrypted data path. |
| Data plane | The encrypted path carrying packets between Tailscale nodes, directly when possible or through a relay when a direct path cannot be established. |
| Group | A named collection of human identities used in access policy. Use a group when permissions follow a person's organizational role, such as administrators or operators. |
| Tag | A policy identity assigned to a non-human or role-based device. Use a tag for infrastructure such as a subnet router, not as a substitute for a human group. |
| Device approval | An administrative enrollment gate requiring a newly joined device to be approved before it participates normally. Use it to control device admission; do not treat it as a replacement for access policy. |
| Route approval | Administrative authorization for a route advertised by a subnet router. A device may be approved while one or more of its advertised routes remain unapproved. |
| Subnet router | A Tailscale node that advertises routes to selected devices or networks that do not run Tailscale themselves. |
| Exit node | A Tailscale node selected to carry a client's general internet-bound traffic. It is not required merely to reach a private homelab host through a subnet route. |
| CIDR prefix | An address and prefix length describing a routing range. A /32 IPv4 prefix selects exactly one address, while a /24 includes 256 addresses. |
| Least privilege | Granting only the identities, destinations, protocols, and services needed for a stated task. |
| Negative test | A test that is expected to be denied. Negative tests prove that unintended paths remain unavailable. |
| DERP relay | A Tailscale relay used when peers cannot establish a direct path. Traffic remains end-to-end encrypted while relayed. |

## Instruction

Tailscale creates an identity-aware private network on top of WireGuard-based encrypted tunnels. A device joins a tailnet, receives identity and policy information through the coordination plane, and then attempts to exchange data directly with authorized peers. If direct connectivity is unavailable, a relay can carry the encrypted packets without becoming the endpoint that decrypts them. This distinction matters operationally: policy distribution and peer discovery are control functions, while application packets belong to the data plane.

Remote access should start with identities and required flows rather than with an entire private network prefix. Human permissions belong in groups because people change roles and membership can be updated centrally. Infrastructure devices should normally receive tags because a router or service should not inherit the permissions of the person who enrolled it. Device approval answers whether a new device may join; route approval answers whether an advertised route may become usable; access policy answers which source may reach which destination and service. These controls complement one another rather than replacing one another.

A subnet router is appropriate when the destination cannot run Tailscale. In this class, only 192.168.50.10 must be reached, so the router advertises 192.168.50.10/32. Advertising 192.168.50.0/24 would expose routing potential for unrelated systems and is therefore rejected. An exit node is not needed because the objective is private-host access, not forwarding general internet traffic. The design must explicitly record exit_node_required as false so the distinction is testable.

Tailscale access policy is fundamentally allow-oriented: traffic without a matching permission remains unavailable. A design document may state intended denials, but an implementation should not invent a broad allow merely to compensate with a later deny. Verification must test both sides of the boundary. Administrators need management access, operators need the web service but not remote shell access, and contractors need no access to the host. A sixth route-scope test confirms that the rejected /24 is not treated as reachable. Rollout planning then adds approvals, success criteria, rollback triggers, and a route-withdrawal owner so access can be removed predictably if the design behaves unexpectedly.

## Architecture

### component
Human identity groups

### role
Represent administrators, operators, and contractors independently of their devices.

### design_rules
Use group:admins for Alice.
Use group:operators for Bob.
Use group:contractors for Carol.
Change group membership when a person's role changes rather than tagging a personal device as a human role.

### relationships
Groups are referenced by access intent.
The administrator group owns the subnet-router tag.
### component
Tagged subnet router

### role
Provides a route from the tailnet to the one legacy homelab host that cannot run Tailscale.

### design_rules
Assign tag:homelab-router.
Require device approval.
Advertise and approve only 192.168.50.10/32.
Record exit_node_required as false.

### relationships
The tag is owned by group:admins.
The device advertises the host route.
Route approval is separate from device approval.
### component
Access policy intent

### role
Defines the required identity-to-service relationships before any live policy is written.

### design_rules
Administrators may reach TCP port 22 and TCP port 443 on 192.168.50.10.
Operators may reach TCP port 443 but not TCP port 22.
Contractors may not reach TCP port 443 on the host.
Anything not granted remains unavailable.

### relationships
Sources are human groups.
The destination is reached through the tagged subnet router.
Negative tests verify missing permissions.
### component
Approval gates

### role
Prevent an enrolled device or advertised route from becoming trusted automatically.

### design_rules
Approve the router device only after its identity and ownership are checked.
Approve the /32 route only after the advertised prefix is reviewed.
Do not infer route approval from device approval.

### relationships
Device approval controls participation.
Route approval controls route availability.
Access policy still limits which identities may use the route.
### component
Validation and rollback plan

### role
Provides deterministic positive tests, negative tests, rollout phases, and withdrawal actions.

### design_rules
Maintain exactly six uniquely identified access tests.
Include three expected denials.
Define exactly three distinct rollback triggers.
Assign route withdrawal to group:admins.

### relationships
Tests validate the architecture document.
Rollout gates depend on test results.
Rollback removes route availability without broadening another permission.

## Required reading

- Tailscale, What is Tailscale?: https://tailscale.com/kb/1151/what-is-tailscale
- Tailscale, How Tailscale works: https://tailscale.com/blog/how-tailscale-works
- Tailscale, Access control lists: https://tailscale.com/kb/1018/acls
- Tailscale, Subnet routers: https://tailscale.com/kb/1019/subnets
- Tailscale, Device approval: https://tailscale.com/kb/1099/device-approval

## References

- Tailscale, What is Tailscale?: https://tailscale.com/kb/1151/what-is-tailscale
- Tailscale, How Tailscale works: https://tailscale.com/blog/how-tailscale-works
- Tailscale, Access control lists: https://tailscale.com/kb/1018/acls
- Tailscale, Subnet routers: https://tailscale.com/kb/1019/subnets
- Tailscale, Device approval: https://tailscale.com/kb/1099/device-approval
- Tailscale, Tags: https://tailscale.com/kb/1068/acl-tags
- Tailscale, Exit nodes: https://tailscale.com/kb/1103/exit-nodes
- Python documentation, json module: https://docs.python.org/3/library/json.html
- Python documentation, pathlib module: https://docs.python.org/3/library/pathlib.html

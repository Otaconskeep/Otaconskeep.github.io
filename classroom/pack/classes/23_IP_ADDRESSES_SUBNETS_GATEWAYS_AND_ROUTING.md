# Class 23 — IP Addresses, Subnets, Gateways, and Routing

**Learning objective:** Distinguish an IPv4 address from a subnet prefix, network address, broadcast address, and usable host range; Convert common CIDR prefixes into subnet masks and host capacities; Determine whether two addresses are in the same subnet; Explain why a default gateway must normally be reachable on a directly connected network; Read a routing table and identify destination prefixes, next hops, interfaces, and metrics; Apply longest-prefix matching to select a route; Explain the roles of connected routes, static routes, default routes, and dynamic routing; Inspect local addressing and routing without changing production or homelab networking
**Bloom level:** Understand / Apply
**Track:** Homelab Networking Foundations · **Difficulty:** beginner · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Build a practical mental model of IPv4 addressing, CIDR subnetting, default gateways, routing tables, and route selection. Learners will inspect their host configuration and use an offline Python model to calculate networks and predict routing decisions without changing any interface, route, DNS, or system networking configuration.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### primary_platform
Linux with Python 3 and iproute2

### linux
Use ip -brief address, ip -4 route show, and ip -4 route get ADDRESS.

### macos
For read-only inspection, use ifconfig, netstat -rn -f inet, and route -n get ADDRESS. The Python model is portable when Python 3 is installed.

### windows
For read-only inspection, use ipconfig, route print -4, and PowerShell Get-NetRoute -AddressFamily IPv4. Run the Python model only if Python 3 is installed and /opt/lab-classroom/class23/ is provided by the classroom environment, such as within a Linux training VM.

### containers
Container route and address output describes the container network namespace and may differ from the physical host.

### ipv6_scope
This class concentrates on IPv4. IPv6 uses prefix-based routing but does not use IPv4 broadcast addresses and has different neighbor-discovery behavior.

## Learning objective

- Distinguish an IPv4 address from a subnet prefix, network address, broadcast address, and usable host range
- Convert common CIDR prefixes into subnet masks and host capacities
- Determine whether two addresses are in the same subnet
- Explain why a default gateway must normally be reachable on a directly connected network
- Read a routing table and identify destination prefixes, next hops, interfaces, and metrics
- Apply longest-prefix matching to select a route
- Explain the roles of connected routes, static routes, default routes, and dynamic routing
- Inspect local addressing and routing without changing production or homelab networking

## Why this matters

Build a practical mental model of IPv4 addressing, CIDR subnetting, default gateways, routing tables, and route selection. Learners will inspect their host configuration and use an offline Python model to calculate networks and predict routing decisions without changing any interface, route, DNS, or system networking configuration.

## Prerequisites

- Basic command-line navigation
- Permission to read the host network configuration
- Python 3 installed for the offline subnet exercises
- Linux with iproute2 is preferred; equivalent read-only commands are documented for other platforms
- The directory /opt/lab-classroom/class23/ must already exist and be writable by the learner

## Required reading

- RFC 791, Internet Protocol: https://www.rfc-editor.org/rfc/rfc791
- RFC 4632, Classless Inter-domain Routing: https://www.rfc-editor.org/rfc/rfc4632
- RFC 3021, Using 31-Bit Prefixes on IPv4 Point-to-Point Links: https://www.rfc-editor.org/rfc/rfc3021
- Linux ip-route manual page: https://man7.org/linux/man-pages/man8/ip-route.8.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| IPv4 address | A 32-bit value assigned to a network interface or used to identify an IPv4 endpoint. Dotted-decimal notation divides the value into four octets, such as 192.168.50.77. |
| Prefix length | The number of leading bits that identify the network portion of an address. In 192.168.50.77/26, the prefix length is 26. |
| Subnet mask | A dotted-decimal representation of the network bits. A /26 prefix corresponds to 255.255.255.192. |
| Network address | The first address of a traditional IPv4 subnet, produced by setting all host bits to zero. It identifies the subnet rather than an ordinary host. |
| Broadcast address | The final address of a traditional IPv4 subnet, produced by setting all host bits to one. It addresses all IPv4 hosts on that broadcast domain. |
| Default gateway | A router address used as the next hop when no more-specific route matches a destination. |
| Routing table | A set of destination prefixes and forwarding instructions used by a host or router to choose where packets should go. |
| Next hop | The neighboring router to which a packet is sent so that it can continue toward its destination. |
| Connected route | A route created because an interface has an address within a directly attached prefix. |
| Default route | The least-specific route, written as 0.0.0.0/0 for IPv4, which matches any IPv4 destination not selected by a more-specific route. |
| Longest-prefix match | The routing rule that selects the matching route with the greatest prefix length, such as preferring /24 over /16 and /0. |
| Metric | A value used to choose among otherwise comparable routes. Its precise interpretation depends on the operating system or routing protocol. |
| Private IPv4 address | An address in 10.0.0.0/8, 172.16.0.0/12, or 192.168.0.0/16, as designated for private internets by RFC 1918. |

## Instruction

An IPv4 address is a 32-bit number. CIDR notation combines that address with a prefix length, such as 192.168.50.77/26. The first 26 bits identify the network and the remaining 6 bits identify positions within that network. A /26 therefore contains 2^6, or 64, total addresses. For an ordinary broadcast subnet, the all-zero host value is the network address and the all-one host value is the broadcast address, leaving 62 conventional host addresses. The four /26 boundaries inside 192.168.50.0/24 begin at .0, .64, .128, and .192. Consequently, 192.168.50.77/26 belongs to 192.168.50.64/26, has broadcast address 192.168.50.127, and has the conventional host range 192.168.50.65 through 192.168.50.126.

A subnet answers the local-delivery question: can the destination be reached directly on the local link, or must the packet be sent to a router? The sender compares the destination against its connected prefixes. If the destination is on-link, the sender resolves the destination's link-layer address and sends directly. If it is off-link, the sender searches its routing table. A default gateway is not automatically used for every packet; it is the next hop associated with the default route and is selected only when no more-specific route wins. The gateway must normally have an address reachable through a connected route, because the host needs a way to deliver the frame to that router before the router can forward the packet.

Routing follows longest-prefix matching. Suppose a host has routes for 10.0.0.0/8, 10.20.0.0/16, and 0.0.0.0/0. A packet for 10.20.30.40 matches all three, but /16 is the longest prefix and wins. A packet for 10.30.1.1 matches /8 and /0, so /8 wins. A packet for 203.0.113.20 matches only /0 and follows the default route. Metrics are usually consulted after prefix specificity and should not be treated as a way for a low-metric default route to override a more-specific route.

Routes may be connected, manually configured, learned through a routing protocol, or installed by network-management software. A host commonly has a connected LAN route, routes for local or special-purpose destinations, and a default route through the LAN router. A router has multiple interfaces and forwards traffic between prefixes according to its routing table and policy. Routing and address translation are separate concepts: routing chooses a path, while address translation may rewrite packet addresses at a boundary. The lab is deliberately observational and simulated. It reads current host state and performs calculations offline, but it does not add addresses, replace routes, restart network services, or affect connectivity.

## Architecture

### scenario
A workstation and two homelab services share a LAN, while a router connects the LAN to other networks.

### components
Workstation: 192.168.50.77/26
Local service: 192.168.50.100/26
Different-subnet service: 192.168.50.140/26
LAN router interface: 192.168.50.65/26
Example remote network behind a router: 10.20.0.0/16

### logical_flow
Traffic from 192.168.50.77 to 192.168.50.100 remains on 192.168.50.64/26 and is delivered directly.
Traffic from 192.168.50.77 to 192.168.50.140 is not local because 192.168.50.140 belongs to 192.168.50.128/26.
Off-link traffic is sent to a selected next hop, such as 192.168.50.65, when a matching route points to that gateway.
A route for 10.20.0.0/16 is preferred over 10.0.0.0/8 or 0.0.0.0/0 for destinations inside 10.20.0.0/16.

### route_selection_order
Collect every route whose destination prefix contains the target address.
Select the route with the longest prefix.
If equally specific routes remain, apply the operating system's route preference and metric rules.
Resolve and reach the selected next hop or directly connected destination through the chosen interface.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Calculate the network address, broadcast address, conventional first host, conventional last host, and conventional host count for 192.168.12.201/27.
Divide 10.10.0.0/24 into four equal subnets and list each resulting CIDR prefix.
Given routes 0.0.0.0/0, 172.16.0.0/12, 172.20.0.0/16, and 172.20.8.0/24, identify the selected prefix for 172.20.8.44, 172.20.9.44, 172.31.1.1, and 8.8.8.8.
Draw a diagram showing a host, local switch, default gateway, and remote subnet. Label where direct delivery ends and routed delivery begins.
In your own words, explain why changing a host from /24 to /16 without changing its address can alter which destinations it treats as local.

## Feynman teach-back

Explain the lesson using a postal analogy. An IP address is a destination, while the prefix describes the local neighborhood. A host first asks whether the destination is in its own neighborhood. If it is, delivery is direct. If not, the host consults a list of directions called the routing table and chooses the most-specific applicable direction. The default gateway is the general-purpose exit used only when no more-specific direction exists. Then test the explanation with 192.168.50.77/26: .100 is in the same .64-to-.127 block, but .140 is in the next block and therefore needs a router. If the explanation cannot show why a /16 route beats a /8 route for the same destination, revisit longest-prefix matching.

## Retrieval check

1. 1. What network contains 192.168.50.77/26, and what is its broadcast address?
2. 2. How many total addresses and conventional usable host addresses are in an ordinary IPv4 /27 subnet?
3. 3. A table contains 0.0.0.0/0, 10.0.0.0/8, and 10.20.0.0/16. Which prefix is selected for 10.20.30.40, and why?
4. 4. Why must a default gateway normally be reachable through a connected route?
5. 5. Does the route with the lowest numeric metric always win over every other matching route?
6. 6. Are 192.168.50.77/26 and 192.168.50.140/26 in the same subnet?
7. 7. What is the difference between routing and address translation?
8. 8. What does 0.0.0.0/0 represent in an IPv4 routing table?
9. 9. If a destination is inside a directly connected prefix, is the default gateway normally required to deliver the packet?
10. 10. What are the three RFC 1918 private IPv4 ranges?

## Guided lab

### name
Read-Only Network Inspection and Offline Route Modeling

### constraints
Do not change interface addresses, routes, DNS settings, network services, or router settings.
All created or modified lab artifacts must remain under /opt/lab-classroom/class23/.
The commands that inspect interfaces and routes are read-only.
The classroom directory must be provisioned before the lab begins; stop if it does not exist.

### steps
### step
1

### instruction
Confirm that the authorized lab directory already exists and enter it. Do not create a substitute elsewhere.

### commands
test -d /opt/lab-classroom/class23/ && test -w /opt/lab-classroom/class23/ && cd /opt/lab-classroom/class23/ && pwd
### step
2

### instruction
Inspect interface names, operational state, and assigned addresses without changing them.

### commands
ip -brief link
ip -brief address
### step
3

### instruction
Inspect the IPv4 routing table. Identify connected prefixes, any default route, its next hop, and the selected interface.

### commands
ip -4 route show
### step
4

### instruction
Ask the kernel which existing route it would use for two documentation addresses. This performs route lookup only and does not send application traffic or alter the table.

### commands
ip -4 route get 192.0.2.1
ip -4 route get 198.51.100.1
### step
5

### instruction
Run an offline Python exercise. It validates subnet boundaries and models longest-prefix route selection, then writes one JSON artifact inside the authorized directory.

### commands
python3 - <<'PY'
from ipaddress import ip_interface, ip_network, ip_address
from json import dumps
from pathlib import Path
base = Path('/opt/lab-classroom/class23')
if not base.is_dir():
    raise SystemExit('Authorized lab directory is missing')
examples = ['192.168.50.77/26', '10.20.30.140/27', '172.16.8.9/24']
subnets = []
for value in examples:
    iface = ip_interface(value)
    net = iface.network
    hosts = list(net.hosts())
    subnets.append({
        'input': value,
        'network': str(net),
        'netmask': str(net.netmask),
        'broadcast': str(net.broadcast_address),
        'first_host': str(hosts[0]),
        'last_host': str(hosts[-1]),
        'conventional_host_count': len(hosts)
    })
routes = [
    (ip_network('0.0.0.0/0'), '192.168.50.65', 'default'),
    (ip_network('10.0.0.0/8'), '192.168.50.66', 'private-summary'),
    (ip_network('10.20.0.0/16'), '192.168.50.67', 'site-route'),
    (ip_network('192.168.50.64/26'), None, 'connected')
]
def select_route(destination):
    target = ip_address(destination)
    matches = [route for route in routes if target in route[0]]
    chosen = max(matches, key=lambda route: route[0].prefixlen)
    return {
        'destination': destination,
        'selected_prefix': str(chosen[0]),
        'next_hop': chosen[1],
        'route_name': chosen[2]
    }
selections = [select_route(value) for value in ['192.168.50.100', '10.20.30.40', '10.30.1.1', '203.0.113.20']]
assert subnets[0]['network'] == '192.168.50.64/26'
assert subnets[0]['broadcast'] == '192.168.50.127'
assert selections[1]['selected_prefix'] == '10.20.0.0/16'
assert selections[2]['selected_prefix'] == '10.0.0.0/8'
assert selections[3]['selected_prefix'] == '0.0.0.0/0'
result = {'subnet_calculations': subnets, 'route_selections': selections}
out = base / 'model_results.json'
out.write_text(dumps(result, indent=2) + '\n', encoding='utf-8')
print(out.read_text(encoding='utf-8'))
PY
### step
6

### instruction
Validate the generated artifact and review the key modeled decisions.

### commands
python3 -m json.tool /opt/lab-classroom/class23/model_results.json
python3 - <<'PY'
import json
from pathlib import Path
p = Path('/opt/lab-classroom/class23/model_results.json')
data = json.loads(p.read_text(encoding='utf-8'))
assert data['subnet_calculations'][0]['network'] == '192.168.50.64/26'
assert data['subnet_calculations'][0]['first_host'] == '192.168.50.65'
assert data['subnet_calculations'][0]['last_host'] == '192.168.50.126'
assert data['route_selections'][1]['selected_prefix'] == '10.20.0.0/16'
print('Class 23 model verification passed')
PY

## Expected results

- The interface inspection lists one or more interfaces and shows IPv4 prefixes in address/prefix form when IPv4 is configured.
- The route table displays destination prefixes and may include a default route with a next hop and interface.
- Each route lookup reports the route the kernel would currently select; exact interfaces and gateways depend on the learner's host.
- The offline model identifies 192.168.50.64/26 as the network containing 192.168.50.77/26.
- The offline model identifies 192.168.50.127 as that subnet's broadcast address and .65 through .126 as its conventional host range.
- The modeled destination 10.20.30.40 selects 10.20.0.0/16 rather than 10.0.0.0/8 or 0.0.0.0/0.
- The modeled destination 10.30.1.1 selects 10.0.0.0/8.
- The modeled destination 203.0.113.20 selects 0.0.0.0/0.
- The final verification prints Class 23 model verification passed.

## Verification checkpoints

- [ ] Run test -f /opt/lab-classroom/class23/model_results.json to confirm that the expected artifact exists.
- [ ] Run python3 -m json.tool /opt/lab-classroom/class23/model_results.json to confirm that the artifact is valid JSON.
- [ ] Confirm that the first modeled network is 192.168.50.64/26 and its netmask is 255.255.255.192.
- [ ] Confirm that the modeled 10.20.30.40 decision selects 10.20.0.0/16.
- [ ] Confirm that the modeled 203.0.113.20 decision selects the default prefix 0.0.0.0/0.
- [ ] Run ip -4 route show again and confirm that inspection did not add, remove, or replace any route.
- [ ] Confirm that no lab-generated file exists outside /opt/lab-classroom/class23/.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The directory check fails. | The classroom directory was not provisioned or the current account cannot write to it. | Stop the lab and ask the lab administrator to provision /opt/lab-classroom/class23/ with appropriate ownership. Do not redirect artifacts to another location. |
| The ip command is not found. | The system does not have Linux iproute2 installed or the lab is being run on another operating system. | Use the compatibility commands for read-only inspection, or move to a supported Linux lab host. The offline Python portion can still run if Python 3 is available. |
| No default route appears. | The host may be isolated, use policy routing, be inside a restricted container, or have incomplete network configuration. | Do not add a route for this exercise. Record the observation and continue with the offline model. |
| The route lookup reports unreachable. | The selected network namespace or host has no route matching the documentation destination. | Treat the result as evidence about the current routing table. Do not alter networking; continue with the deterministic model. |
| Python reports ModuleNotFoundError for ipaddress. | The interpreter is obsolete or incomplete. | Use a supported Python 3 standard installation. The ipaddress module is part of the Python 3 standard library. |
| Writing model_results.json fails with PermissionError. | The current user cannot write to the authorized lab directory. | Stop and have the directory ownership corrected by the lab administrator. Do not use another path and do not elevate commands merely to bypass the classroom permissions. |
| The learner expects a lower route metric to beat a more-specific prefix. | Metric comparison has been confused with longest-prefix matching. | First choose the most-specific matching prefix. Compare route preferences or metrics only among routes considered equivalent under the platform's route-selection rules. |

## Security considerations

Interface and route output can reveal internal addressing, gateway addresses, interface names, virtual network design, and VPN presence. Redact this information before sharing screenshots or logs.
Use the documentation networks 192.0.2.0/24, 198.51.100.0/24, and 203.0.113.0/24 in examples rather than presenting real public targets as lab infrastructure.
A wrong prefix length can unintentionally classify a remote host as local or a local host as remote, causing outages or unexpected traffic paths.
An untrusted default gateway can observe or redirect traffic. Gateway configuration should be controlled through authenticated administrative processes.
Route inspection does not prove end-to-end reachability. Path policy, forwarding state, filtering, return routes, and service availability can all affect delivery.
Do not publish model_results.json if it has been modified to include real infrastructure details.
This lesson intentionally avoids privileged network changes so that an addressing mistake cannot disconnect the lab host.

## Rollback

### impact
The lab does not change networking. Rollback only removes the generated JSON artifact inside the authorized classroom directory.

### commands
python3 - <<'PY'
from pathlib import Path
p = Path('/opt/lab-classroom/class23/model_results.json')
if p.exists():
    p.unlink()
print('Lab artifact removed' if not p.exists() else 'Artifact still exists')
PY

### post_rollback_verification
test ! -e /opt/lab-classroom/class23/model_results.json
ip -4 route show

## Video narration notes

Begin with a 32-box diagram representing the bits of an IPv4 address. Shade the first 26 boxes to represent the prefix in 192.168.50.77/26, leaving six host bits. Show that six host bits produce 64 address positions, then place the example inside the 192.168.50.64 through 192.168.50.127 block. Label .64 as the network address, .127 as the broadcast address, and .65 through .126 as the conventional host range. Next, compare .77 with .100 and .140. Demonstrate that .77 and .100 share the same first 26 bits, while .140 belongs to the next /26. Introduce the default gateway as an on-link router used for off-link destinations rather than as a universal destination for every packet. Display a routing table containing connected, /16, /8, and default prefixes. Test 10.20.30.40 against every route and select /16 because it is the longest match. Repeat with 10.30.1.1 and a documentation address to show /8 and default-route selection. Finish by demonstrating the read-only inspection commands and the offline Python model, emphasizing that the lab does not alter live networking.

## References

- RFC 791, Internet Protocol: https://www.rfc-editor.org/rfc/rfc791
- RFC 1918, Address Allocation for Private Internets: https://www.rfc-editor.org/rfc/rfc1918
- RFC 3021, Using 31-Bit Prefixes on IPv4 Point-to-Point Links: https://www.rfc-editor.org/rfc/rfc3021
- RFC 4632, Classless Inter-domain Routing: https://www.rfc-editor.org/rfc/rfc4632
- RFC 5737, IPv4 Address Blocks Reserved for Documentation: https://www.rfc-editor.org/rfc/rfc5737
- Linux ip-address manual page: https://man7.org/linux/man-pages/man8/ip-address.8.html
- Linux ip-route manual page: https://man7.org/linux/man-pages/man8/ip-route.8.html
- Python ipaddress documentation: https://docs.python.org/3/library/ipaddress.html

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

# Class 51: VPN Binding, Kill Switches, and Leak Verification

**Learning objective:** Explain why an application bound to a VPN address is not automatically protected after that address or interface disappears.; Differentiate socket binding, route selection, policy routing, and packet-filter enforcement.; Describe a fail-closed kill switch that permits required tunnel establishment traffic while denying unauthorized clear-path egress.; Identify common DNS, IPv6, container, proxy, and browser leak paths.; Develop positive and negative tests that prove both normal VPN operation and safe behavior during failure.; Interpret a deterministic policy report without mistaking the simulation for proof about the host network.; Plan a controlled production validation with console access and a tested rollback procedure.
**Bloom level:** Understand / Apply
**Track:** Network Privacy and Secure Services · **Difficulty:** advanced · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Teach students to distinguish application binding, routing, and fail-closed packet filtering; design a layered VPN egress policy; and verify that application traffic, DNS, and IPv6 do not silently escape through a non-VPN path.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### lab_platforms
Linux hosts with Python 3 and write access to /opt/lab-classroom/class51/.
The simulation uses only Python standard-library modules.

### vpn_technologies
The concepts apply to routed VPN designs including WireGuard and OpenVPN.
Exact interface names, route installation, DNS integration, and endpoint exceptions vary by implementation.

### operating_system_notes
The active enforcement mechanism and route-inspection commands differ among Linux distributions, BSD systems, Windows, macOS, routers, containers, and hypervisors.
Interface binding support and privilege requirements vary by operating system and application.
IPv6 must be evaluated according to the actual platform rather than assumed to follow IPv4 policy.
The classroom lab does not require administrative network privileges because it does not alter the host network.

## Learning objective

- Explain why an application bound to a VPN address is not automatically protected after that address or interface disappears.
- Differentiate socket binding, route selection, policy routing, and packet-filter enforcement.
- Describe a fail-closed kill switch that permits required tunnel establishment traffic while denying unauthorized clear-path egress.
- Identify common DNS, IPv6, container, proxy, and browser leak paths.
- Develop positive and negative tests that prove both normal VPN operation and safe behavior during failure.
- Interpret a deterministic policy report without mistaking the simulation for proof about the host network.
- Plan a controlled production validation with console access and a tested rollback procedure.

## Why this matters

Teach students to distinguish application binding, routing, and fail-closed packet filtering; design a layered VPN egress policy; and verify that application traffic, DNS, and IPv6 do not silently escape through a non-VPN path.

## Prerequisites

- Comfort reading IP addresses, interface names, routing decisions, and transport-layer socket concepts.
- Basic understanding of VPN tunnels and the difference between a tunnel endpoint and traffic carried inside the tunnel.
- Ability to run Python 3 and basic shell commands.
- Completion of introductory networking, DNS, and Linux service-management lessons is recommended.
- Access to /opt/lab-classroom/class51/ with permission to create files there.

## Required reading

- Linux ip-route manual: https://man7.org/linux/man-pages/man8/ip-route.8.html
- Linux ip-rule manual: https://man7.org/linux/man-pages/man8/ip-rule.8.html
- Linux socket manual: https://man7.org/linux/man-pages/man7/socket.7.html
- WireGuard routing and namespace discussion: https://www.wireguard.com/netns/
- OpenVPN community documentation: https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/
- RFC 4193, Unique Local IPv6 Unicast Addresses: https://www.rfc-editor.org/rfc/rfc4193
- RFC 5737, IPv4 Address Blocks Reserved for Documentation: https://www.rfc-editor.org/rfc/rfc5737

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

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

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Create a traffic inventory for one homelab application. Include process or service identity, IPv4 requirements, IPv6 requirements, DNS behavior, VPN endpoint requirements, LAN dependencies, container scope, and expected behavior when the tunnel is absent.
Write a test matrix with rows for normal operation, application restart, VPN restart, tunnel loss, endpoint change, host reboot, DNS failure, IPv6 availability, and container traffic. For each row, state the expected permitted and denied paths.
Draw a diagram showing the application, routing decision, VPN interface, physical uplink, resolver, VPN endpoint, and enforcement boundary.
Explain how you would collect evidence on both the tunnel and uplink without recording credentials or unrelated household traffic.
Propose a rollback plan that remains usable if a remote network-policy change disconnects management access.
Compare address binding with interface binding and document which method your selected application actually supports.

## Feynman teach-back

### prompt
Explain the design to a technically curious person who thinks selecting a VPN interface inside an application is enough.

### model_explanation
Binding tells an application which local address or interface it should try to use. Routing tells the operating system where a packet would go. A kill switch is the guard that refuses the packet if the chosen exit is not approved. If the tunnel vanishes, binding may cause an error, but software can restart, choose another address, use IPv6, ask DNS through another path, or run in a container with different rules. Therefore we verify several independent facts: the application uses the intended source, routing chooses the tunnel, enforcement rejects the uplink, DNS stays on the approved path, and IPv6 is tunneled or intentionally blocked. The strongest test deliberately removes the tunnel and confirms that traffic stops.

### self_check
Can you explain why a default route through the VPN does not prove every policy-routing table uses it?
Can you identify the narrow traffic that must usually remain allowed outside the tunnel?
Can you explain why tunnel-loss testing provides stronger evidence than a single public-address check?
Can you distinguish an inbound listener bind from outbound egress enforcement?

## Retrieval check

1. 1. Why is binding an application to a VPN address not a complete kill switch?
2. 2. What is the purpose of a VPN control-plane exception?
3. 3. What behavior demonstrates a fail-closed design when the tunnel disappears?
4. 4. Why must IPv6 be tested separately from IPv4?
5. 5. What is the difference between testing a public exit address and performing leak verification?
6. 6. Why can a container require separate verification from its host?
7. 7. What does a wildcard bind such as 0.0.0.0 mean for a listening socket?
8. 8. Why should a kill switch be tested after application restart and host reboot?
9. 9. What is wrong with allowing all traffic through the physical uplink merely so the VPN can reconnect?
10. 10. What does the classroom simulation prove about the real host's network policy?

## Guided lab

### scope
This lab is a deterministic local simulation. It creates and changes files only under /opt/lab-classroom/class51/. It does not modify host routes, interfaces, DNS settings, VPN configuration, or active packet-filter rules.

### steps
### step
1

### instruction
Create the isolated lab directory.

### command
mkdir -p /opt/lab-classroom/class51
### step
2

### instruction
Create /opt/lab-classroom/class51/policy_lab.py with the exact content supplied in the files section.
### step
3

### instruction
Run the simulation and write the deterministic report.

### command
python3 /opt/lab-classroom/class51/policy_lab.py
### step
4

### instruction
Display the generated report without contacting any external service.

### command
python3 -m json.tool /opt/lab-classroom/class51/report.json
### step
5

### instruction
Review why the healthy scenario passes all checks and why each negative scenario fails at least one specifically named control. Do not interpret this report as evidence about the host's real routes or VPN.
### step
6

### instruction
Copy the healthy scenario on paper or into notes and add separate fields for VPN endpoint, endpoint transport and port, approved LAN destinations, protected process identity, container scope, and reboot test status. This turns a simplistic model into the beginning of an operational test plan without changing the host.

### files
### path
/opt/lab-classroom/class51/policy_lab.py

### content
import json
from pathlib import Path

base = Path('/opt/lab-classroom/class51')
report_path = base / 'report.json'

scenarios = [
    {
        'name': 'healthy',
        'app_bind': '10.8.0.2',
        'vpn_address': '10.8.0.2',
        'default_path': 'vpn0',
        'allowed_egress': ['vpn0'],
        'dns_path': 'vpn0',
        'ipv6_path': 'blocked'
    },
    {
        'name': 'wildcard_binding',
        'app_bind': '0.0.0.0',
        'vpn_address': '10.8.0.2',
        'default_path': 'vpn0',
        'allowed_egress': ['vpn0'],
        'dns_path': 'vpn0',
        'ipv6_path': 'blocked'
    },
    {
        'name': 'route_leak',
        'app_bind': '10.8.0.2',
        'vpn_address': '10.8.0.2',
        'default_path': 'wan0',
        'allowed_egress': ['vpn0'],
        'dns_path': 'vpn0',
        'ipv6_path': 'blocked'
    },
    {
        'name': 'kill_switch_failure',
        'app_bind': '10.8.0.2',
        'vpn_address': '10.8.0.2',
        'default_path': 'vpn0',
        'allowed_egress': ['vpn0', 'wan0'],
        'dns_path': 'vpn0',
        'ipv6_path': 'blocked'
    },
    {
        'name': 'dns_leak',
        'app_bind': '10.8.0.2',
        'vpn_address': '10.8.0.2',
        'default_path': 'vpn0',
        'allowed_egress': ['vpn0'],
        'dns_path': 'wan0',
        'ipv6_path': 'blocked'
    },
    {
        'name': 'ipv6_leak',
        'app_bind': '10.8.0.2',
        'vpn_address': '10.8.0.2',
        'default_path': 'vpn0',
        'allowed_egress': ['vpn0'],
        'dns_path': 'vpn0',
        'ipv6_path': 'wan0'
    }
]

def evaluate(item):
    checks = {
        'application_bound_to_vpn_address': item['app_bind'] == item['vpn_address'],
        'default_path_uses_vpn': item['default_path'] == 'vpn0',
        'protected_egress_excludes_wan': 'wan0' not in item['allowed_egress'],
        'dns_uses_vpn': item['dns_path'] == 'vpn0',
        'ipv6_is_tunneled_or_blocked': item['ipv6_path'] in ('vpn0', 'blocked')
    }
    return {
        'name': item['name'],
        'checks': checks,
        'pass': all(checks.values()),
        'failed_checks': [name for name, result in checks.items() if not result]
    }

results = [evaluate(item) for item in scenarios]
report = {
    'notice': 'Simulation only; this is not evidence about the host network.',
    'scenario_count': len(results),
    'passing_scenarios': [item['name'] for item in results if item['pass']],
    'failing_scenarios': [item['name'] for item in results if not item['pass']],
    'results': results
}
base.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))


### constraints
Do not add or remove host routes.
Do not bring interfaces up or down.
Do not change system DNS configuration.
Do not apply active packet-filter rules.
Do not send requests to external IP-check or DNS-leak services from this classroom lab.
All persistent lab mutations must remain under /opt/lab-classroom/class51/.

## Expected results

- The script creates /opt/lab-classroom/class51/report.json.
- The report states that it is a simulation and not evidence about the host network.
- The report evaluates exactly six modeled scenarios.
- Only the healthy scenario has pass set to true.
- The wildcard_binding scenario fails application_bound_to_vpn_address.
- The route_leak scenario fails default_path_uses_vpn.
- The kill_switch_failure scenario fails protected_egress_excludes_wan.
- The dns_leak scenario fails dns_uses_vpn.
- The ipv6_leak scenario fails ipv6_is_tunneled_or_blocked.
- No host route, network interface, DNS configuration, VPN configuration, or active packet-filter policy is changed.

## Verification checkpoints

- [ ] Run: test -f /opt/lab-classroom/class51/report.json && echo REPORT_PRESENT
- [ ] Run: python3 -c "import json; p='/opt/lab-classroom/class51/report.json'; d=json.load(open(p)); assert d['scenario_count']==6; assert d['passing_scenarios']==['healthy']; print('SCENARIO_SUMMARY_OK')"
- [ ] Run: python3 -c "import json; p='/opt/lab-classroom/class51/report.json'; d=json.load(open(p)); m={x['name']:x for x in d['results']}; assert m['wildcard_binding']['failed_checks']==['application_bound_to_vpn_address']; print('BIND_TEST_OK')"
- [ ] Run: python3 -c "import json; p='/opt/lab-classroom/class51/report.json'; d=json.load(open(p)); m={x['name']:x for x in d['results']}; assert m['route_leak']['failed_checks']==['default_path_uses_vpn']; print('ROUTE_TEST_OK')"
- [ ] Run: python3 -c "import json; p='/opt/lab-classroom/class51/report.json'; d=json.load(open(p)); m={x['name']:x for x in d['results']}; assert m['kill_switch_failure']['failed_checks']==['protected_egress_excludes_wan']; print('KILL_SWITCH_TEST_OK')"
- [ ] Run: python3 -c "import json; p='/opt/lab-classroom/class51/report.json'; d=json.load(open(p)); m={x['name']:x for x in d['results']}; assert m['dns_leak']['failed_checks']==['dns_uses_vpn']; assert m['ipv6_leak']['failed_checks']==['ipv6_is_tunneled_or_blocked']; print('PROTOCOL_LEAK_TESTS_OK')"
- [ ] For a future controlled production test, verify the route and chosen source address for the exact destination rather than relying only on the default-route display.
- [ ] For a future controlled production test, capture both the VPN interface and physical uplink during normal operation and tunnel loss, then confirm protected payloads never appear on the uplink.
- [ ] For a future controlled production test, repeat checks for IPv4, IPv6, DNS, application restart, VPN restart, host reboot, containers, virtual machines, proxies, and browser-specific traffic.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The mkdir command reports permission denied. | The current account cannot create directories beneath /opt/lab-classroom/. | Use the classroom account or approved privilege procedure to create only /opt/lab-classroom/class51/. Do not redirect the lesson into unrelated system directories. |
| python3 is not found. | Python 3 is not installed or is not present in the current PATH. | Install Python 3 through the operating system's trusted package-management process, or run the lab on a compatible classroom host. Do not download and execute an unreviewed installer. |
| The script reports a syntax error. | The file content was copied incompletely or smart quotes replaced ordinary ASCII quotation marks. | Replace /opt/lab-classroom/class51/policy_lab.py with the exact supplied content and run it again. |
| More than one scenario passes. | The scenario data or evaluation expressions were edited. | Restore the supplied script, regenerate report.json, and rerun every verification command. |
| A real application still reaches the Internet after the VPN is disconnected. | Application binding was treated as the only control, an uplink egress allowance is too broad, or traffic is using another protocol family or namespace. | Reconnect through a safe management path, collect route and packet evidence, inspect IPv4 and IPv6 independently, inspect container or virtual-machine networking, and correct the fail-closed host policy before retesting. |
| The VPN cannot reconnect after a kill switch is enabled. | The control-plane exception does not permit the VPN endpoint, transport, port, required bootstrap name resolution, or current endpoint address. | Use console access to restore the known-good policy, validate the endpoint requirements, and add only the narrow exception required for tunnel establishment. |
| DNS fails while direct IP connectivity through the VPN works. | The approved resolver is unreachable through the tunnel, resolver routing differs from application routing, or all resolver traffic was denied without a replacement. | Inspect the active resolver configuration and route to the resolver. Authorize only the intended resolver path and test both UDP and TCP DNS behavior where applicable. |
| IPv4 tests pass but an application still exposes the uplink address. | The application is using IPv6 through the physical interface. | Provide IPv6 through the VPN or explicitly contain IPv6 for the protected scope, then test with an IPv6-capable destination. |

## Security considerations

A connected VPN indicator is not proof that all traffic uses the VPN.
Never deploy a new kill switch remotely without console or out-of-band recovery access.
Use an allowlist for the VPN control plane instead of allowing arbitrary uplink traffic.
Account for endpoint address changes when a VPN provider uses hostnames or rotating addresses.
Do not expose VPN credentials, private keys, preshared keys, cookies, or provider tokens in packet captures or lesson artifacts.
Treat IPv4 and IPv6 as separate paths requiring separate evidence.
Verify DNS over both UDP and TCP where relevant, and account for encrypted DNS configured inside individual applications.
Inspect containers, virtual machines, and separate network namespaces independently from the host.
Distinguish inbound listener exposure from outbound egress protection; a safe listener bind does not prove safe outbound behavior.
Preserve a known-good policy and rollback procedure before applying active packet-filter changes.
Review local-network exceptions carefully because broad private-network allowances can expose traffic on untrusted Wi-Fi or overlapping networks.
Use documentation address ranges in examples and never assume an example address belongs to the student's VPN provider.

## Rollback

### lab_rollback
Stop any editor or Python process using files beneath /opt/lab-classroom/class51/.
Delete /opt/lab-classroom/class51/policy_lab.py if the classroom requires individual artifact removal.
Delete /opt/lab-classroom/class51/report.json if the classroom requires individual artifact removal.
Remove /opt/lab-classroom/class51/ only after confirming it contains no files that must be retained.
No route, interface, DNS, VPN, or active packet-filter rollback is required because the lab never changes those components.

### production_rollback_principles
Obtain console or out-of-band access before changing enforcement.
Export and validate the current active policy using the platform's supported mechanism.
Schedule an automatic recovery action where operationally appropriate and cancel it only after validation.
Apply changes in a test environment before the production host.
If management connectivity is lost, restore the previously verified policy from the console rather than adding broad emergency allowances.
After rollback, verify management access, VPN establishment, DNS, IPv4, IPv6, and protected-application behavior.

## Video narration notes

Begin with the central idea: a VPN is not safe merely because its status says connected. Show the traffic path as three distinct decisions. First, the application chooses or is assigned a local source. Second, the operating system selects a route. Third, enforcement decides whether that packet is allowed to leave through the selected interface. Emphasize that application binding is useful but cannot replace fail-closed enforcement.

Walk through a healthy architecture. The physical uplink is allowed to contact only the VPN endpoint for tunnel establishment, along with narrowly approved management or bootstrap dependencies. Protected traffic is allowed through the tunnel. Direct uplink egress for the protected scope is denied. DNS uses an approved path, and IPv6 is either carried by the VPN or deliberately contained. Discuss why broad exceptions weaken the design and why endpoint hostnames introduce bootstrap DNS considerations.

Introduce negative testing. A normal test proves the intended path works, while a tunnel-loss test proves the unintended path does not work. Demonstrate the local simulation and point out each scenario: wildcard application binding, an incorrect default path, a broad uplink allowance, DNS using the uplink, and IPv6 using the uplink. Show that only the healthy scenario passes all checks. State clearly that this is a model, not a probe of the real host.

Conclude with an operational verification plan. Inspect exact-destination routing and chosen source addresses. Observe both the tunnel and physical uplink. Test DNS, IPv4, IPv6, browser behavior, proxies, containers, and virtual machines. Repeat after application restart, VPN restart, and reboot. Finally, disconnect the tunnel in a controlled maintenance window and confirm that protected traffic stops. Never apply a new enforcement policy to a remote-only machine without console access and a tested rollback path.

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

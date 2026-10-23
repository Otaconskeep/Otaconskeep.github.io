# Class 70: VLAN Design for a Homelab

**Learning objective:** Separate homelab devices into VLANs based on trust, function, and operational requirements; Create a consistent VLAN and IPv4 subnet plan with no duplicate identifiers or overlapping subnets; Distinguish access ports from trunks and document tagged VLANs, untagged VLANs, PVIDs, and administrative state consistently; Build least-privilege trunk allowlists instead of allowing every VLAN on every trunk; Explain why the worked hypervisor trunk carries the management VLAN while excluding guest and IoT VLANs; Document DHCP, DNS, NTP, internet, administrative, and explicit denied inter-zone flows; Apply a default-deny policy model without using vague destinations or actions; Recognize VLAN hopping and double-tagging risks and describe appropriate native-VLAN controls; Validate the design automatically before translating it into vendor-specific configuration
**Bloom level:** Understand / Apply
**Track:** Networking and Segmentation · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Design an auditable VLAN, subnet, switch-port, and inter-zone policy plan for a homelab without changing live network equipment. The lesson emphasizes explicit trust boundaries, least-privilege trunk allowlists, required infrastructure services, default-deny routing policy, disabled unused ports, and machine-verifiable documentation.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-27
**Compatibility:** ### operating_systems
Linux systems capable of running Python 3.9 or newer

### software_requirements
Python standard-library modules pathlib, csv, json, and ipaddress
A POSIX-compatible command environment for the displayed shell invocations

### vendor_scope
The VLAN, port, and policy artifacts are vendor-neutral. Actual switch terminology for tagged, untagged, native VLAN, access VLAN, and PVID varies by platform.

### filesystem_scope
/opt/lab-classroom/class70/

### network_scope
Offline design validation only; no packets are sent and no network device configuration is changed.

### known_limitations
The validator confirms design intent but cannot detect the capabilities or current state of physical equipment.
The policy model documents intended new-flow authorization and assumes that a future implementation handles established return traffic statefully.
IPv6 is outside this class and requires a separate addressing and policy plan before deployment.

## Learning objective

- Separate homelab devices into VLANs based on trust, function, and operational requirements
- Create a consistent VLAN and IPv4 subnet plan with no duplicate identifiers or overlapping subnets
- Distinguish access ports from trunks and document tagged VLANs, untagged VLANs, PVIDs, and administrative state consistently
- Build least-privilege trunk allowlists instead of allowing every VLAN on every trunk
- Explain why the worked hypervisor trunk carries the management VLAN while excluding guest and IoT VLANs
- Document DHCP, DNS, NTP, internet, administrative, and explicit denied inter-zone flows
- Apply a default-deny policy model without using vague destinations or actions
- Recognize VLAN hopping and double-tagging risks and describe appropriate native-VLAN controls
- Validate the design automatically before translating it into vendor-specific configuration

## Why this matters

Design an auditable VLAN, subnet, switch-port, and inter-zone policy plan for a homelab without changing live network equipment. The lesson emphasizes explicit trust boundaries, least-privilege trunk allowlists, required infrastructure services, default-deny routing policy, disabled unused ports, and machine-verifiable documentation.

## Prerequisites

- Basic understanding of Ethernet switching, IP addressing, subnets, and default gateways
- Familiarity with access ports, tagged frames, and the purpose of a router or Layer 3 gateway
- Python 3.9 or newer with the standard library
- Write permission to /opt/lab-classroom/class70/
- The parent directory /opt/lab-classroom/ must already exist
- No production switch, router, access point, or hypervisor configuration is changed in this lab

## Required reading

- IEEE 802.1Q overview: understand that VLAN tags identify logical broadcast domains across compatible links.
- RFC 1918, Address Allocation for Private Internets: review the private IPv4 address ranges.
- RFC 2131, Dynamic Host Configuration Protocol: review the client and server roles and UDP ports 67 and 68.
- RFC 1034 and RFC 1035: review the role of DNS and its use of port 53.
- RFC 5905, Network Time Protocol Version 4: review the role of NTP and UDP port 123.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| VLAN | A logical Layer 2 broadcast domain identified by a VLAN ID on equipment that supports IEEE 802.1Q. |
| Access port | A switch port intended to place ordinary untagged endpoint traffic into one configured VLAN. |
| Trunk port | A link that carries multiple VLANs, normally as explicitly allowed tagged VLANs. |
| Tagged VLAN | A VLAN transported on a frame containing an IEEE 802.1Q tag. |
| Untagged VLAN | The VLAN assigned to frames sent or received without an IEEE 802.1Q tag on a particular port. |
| PVID | The port VLAN identifier used to classify an untagged ingress frame. Vendor terminology may call this an access VLAN or native VLAN depending on port mode. |
| Native VLAN | On platforms that support the concept, the VLAN associated with untagged traffic on a trunk. This lesson assigns an unused, unrouted blackhole VLAN for that role. |
| SVI | A switched virtual interface that provides a Layer 3 gateway address for a VLAN. |
| Trust boundary | A point at which traffic crosses between systems with different security assumptions and should be evaluated by policy. |
| Default deny | A policy posture in which traffic is rejected unless a specific allow rule authorizes it. |
| VLAN hopping | A class of attacks intended to move traffic into a VLAN that the sender should not be able to reach. |
| Double-tagging | A VLAN-hopping technique that places two VLAN tags in a frame and can exploit unsafe native-VLAN behavior on some switched paths. |

## Instruction

A VLAN is a Layer 2 boundary, not a complete security control. Hosts in different VLANs require a Layer 3 device to communicate, but meaningful isolation exists only when that device enforces an explicit policy. Begin by grouping systems according to trust and function rather than placing every device in one large subnet. This design uses management, infrastructure, lab, guest, and IoT zones. Management is reserved for authorized administration clients. Infrastructure contains shared servers. Lab contains experimental workloads. Guest and IoT devices are treated as untrusted. Each routed VLAN receives a unique subnet and gateway, while VLAN 999 is an unrouted blackhole VLAN used only for unused or untagged-port handling.

An access port should have one untagged VLAN and a matching PVID. A trunk should carry only the tagged VLANs required by the attached device. Do not automatically place the management VLAN on every hypervisor trunk. In this worked design, core-02 carries tagged VLAN 10 because the hypervisor host has an explicitly documented management interface in VLAN 10. It also carries VLANs 20 and 30 for infrastructure and lab workloads. It deliberately omits VLANs 40 and 50 because this host does not run guest or IoT workloads. If host management used a separate physical access port, VLAN 10 should be removed from the workload trunk. The access-point trunk carries VLANs 40 and 50 for wireless client networks and VLAN 10 only because the access point itself has a tagged management interface there.

Policy design starts with required flows, not broad statements such as allow internal or allow selected. Every policy row must name a defined source, a defined destination, a protocol, destination ports, an action, and a purpose. Client zones need DHCP for addressing, DNS for name resolution, and NTP for time synchronization. This model represents those shared gateway-hosted services with the defined destination gateway_services. The internet destination is also explicitly defined. Management receives narrowly scoped administrative access to infrastructure and IoT HTTPS interfaces. Lab, guest, and IoT may use specified internet services but are explicitly denied access to other internal zones. A default-deny policy covers traffic not listed.

Trunk allowlists reduce accidental exposure and limit the impact of mistakes. A trunk carrying every VLAN defeats that goal even if routing rules are otherwise correct. Untagged traffic on trunks is mapped to VLAN 999, which has no gateway or SVI. This helps reduce native-VLAN ambiguity, but it does not replace other controls. Disable dynamic trunk negotiation where supported, avoid using the native VLAN for user or management traffic, and keep native-VLAN behavior consistent at both ends. These practices help mitigate VLAN hopping, including double-tagging scenarios. Unused switch ports must not merely be assigned to VLAN 999; they must also be administratively disabled. Finally, treat the generated plan as vendor-neutral intent. Validate it, review it, and only then translate it into syntax appropriate for the actual switch, router, hypervisor, and access point.

## Architecture

### design_principles
One unique IPv4 subnet per routed VLAN
VLANs are assigned by trust and function
All trunk VLANs use explicit allowlists
Management VLAN membership requires a documented management function
Guest, IoT, and lab zones cannot initiate connections to internal zones
DHCP, DNS, NTP, and approved internet flows are explicitly represented
Unlisted routed traffic is denied
Unused physical ports are assigned to VLAN 999 and administratively disabled
VLAN 999 has no gateway, SVI, or routed policy

### endpoints
### name
gateway_services

### type
service_endpoint

### meaning
Gateway-operated DHCP, DNS, and NTP services reachable by explicitly listed client VLANs
### name
internet

### type
external_endpoint

### meaning
Destinations outside the homelab reached through the upstream route

### vlans
### vlan_id
10

### name
management

### subnet
10.70.10.0/24

### gateway
10.70.10.1

### routed
True

### trust
high

### purpose
Authorized administration clients and explicitly documented device-management interfaces
### vlan_id
20

### name
infrastructure

### subnet
10.70.20.0/24

### gateway
10.70.20.1

### routed
True

### trust
controlled

### purpose
Shared internal services
### vlan_id
30

### name
lab

### subnet
10.70.30.0/24

### gateway
10.70.30.1

### routed
True

### trust
limited

### purpose
Experimental workloads
### vlan_id
40

### name
guest

### subnet
10.70.40.0/24

### gateway
10.70.40.1

### routed
True

### trust
untrusted

### purpose
Guest devices requiring internet access but no internal access
### vlan_id
50

### name
iot

### subnet
10.70.50.0/24

### gateway
10.70.50.1

### routed
True

### trust
untrusted

### purpose
Embedded and appliance devices requiring limited internet access
### vlan_id
999

### name
blackhole

### subnet


### gateway


### routed
False

### trust
none

### purpose
Unused ports and untagged trunk traffic; no SVI or gateway

### ports
### port
core-01

### connected_device
router

### mode
trunk

### tagged_vlans
10
20
30
40
50

### untagged_vlan
999

### pvid
999

### admin_state
up

### purpose
Router-on-a-stick link for all routed VLANs
### port
core-02

### connected_device
hypervisor-01

### mode
trunk

### tagged_vlans
10
20
30

### untagged_vlan
999

### pvid
999

### admin_state
up

### purpose
Tagged VLAN 10 for the host management interface and VLANs 20 and 30 for approved workloads; VLANs 40 and 50 are excluded
### port
core-03

### connected_device
ap-01

### mode
trunk

### tagged_vlans
10
40
50

### untagged_vlan
999

### pvid
999

### admin_state
up

### purpose
Tagged access-point management on VLAN 10 and guest and IoT wireless networks on VLANs 40 and 50
### port
core-04

### connected_device
nas-01

### mode
access

### tagged_vlans


### untagged_vlan
20

### pvid
20

### admin_state
up

### purpose
Infrastructure NAS
### port
core-05

### connected_device
admin-workstation

### mode
access

### tagged_vlans


### untagged_vlan
10

### pvid
10

### admin_state
up

### purpose
Authorized management workstation
### port
core-06

### connected_device
lab-node

### mode
access

### tagged_vlans


### untagged_vlan
30

### pvid
30

### admin_state
up

### purpose
Untagged lab endpoint
### port
core-07

### connected_device
unused

### mode
access

### tagged_vlans


### untagged_vlan
999

### pvid
999

### admin_state
down

### purpose
Unused port assigned to the blackhole VLAN and administratively disabled

### routing_and_policy
### routing_location
Central Layer 3 gateway

### default_action
deny

### stateful_return_traffic
Return traffic for an established allowed flow is expected to be handled by the eventual stateful policy implementation.

### policy_columns
source
destination
protocol
destination_ports
action
purpose

### restricted_sources
lab
guest
iot

### internal_zones
management
infrastructure
lab
guest
iot

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### task
Create a second design on paper for a camera VLAN using a new non-overlapping subnet.

### requirements
State whether cameras need DNS, NTP, or internet access
Name the exact management source, protocol, and destination port needed to administer cameras
Deny camera-initiated access to all internal zones
Identify which physical trunks, if any, must carry the new VLAN

### validation_goal
No trunk may receive the camera VLAN solely because it is convenient.
### task
Model removal of tagged management VLAN 10 from the hypervisor trunk.

### requirements
Add a separate physical management access port to the written architecture
Assign that port to VLAN 10 with matching untagged VLAN and PVID
Change the hypervisor workload trunk to VLANs 20 and 30 only
Describe the migration order that avoids losing host management

### validation_goal
The design must never leave the hypervisor unmanaged during the migration.
### task
Extend the validator conceptually for a voice VLAN.

### requirements
Reject duplicate VLAN IDs
Reject overlapping subnets
Require documented time and name-resolution services
Reject wildcard allow entries
Require unused ports to remain administratively down

### validation_goal
Write the proposed assertions in plain language or Python without changing live network equipment.

## Feynman teach-back

### prompt
Explain the design to a new homelab operator without using vendor-specific terms. Include why VLAN 10 is on the hypervisor trunk, why VLANs 40 and 50 are not, what VLAN 999 does, and why DHCP, DNS, NTP, and internet access must be written as separate policy flows.

### model_answer
The switch creates separate local networks for management, servers, experiments, guests, and IoT devices. A link should carry only the networks needed by the device on the other end. The hypervisor link carries management because the host itself has a tagged management interface, and it carries infrastructure and lab for approved virtual workloads. It does not carry guest or IoT because no such workloads are assigned there. VLAN 999 catches untagged trunk traffic and unused ports but has no route; unused physical ports are also shut down. When traffic must cross between networks, the gateway starts from deny and allows only named requirements. DHCP supplies addresses, DNS resolves names, NTP supplies time, and web or QUIC rules provide approved internet use. Writing each flow explicitly makes omissions and excessive permissions visible during review.

## Retrieval check

1. 1. Why is VLAN 10 present on the worked hypervisor trunk even though management VLANs should not be added to trunks automatically?
2. 2. Which VLANs must be absent from the core-02 hypervisor trunk, and why?
3. 3. What is wrong with an allow rule whose destination is merely `internal` and whose action is `allow-selected`?
4. 4. Which service flows must each client zone have to obtain addressing, resolve names, and synchronize time?
5. 5. Why must unused ports be administratively disabled even when they are assigned to VLAN 999?
6. 6. How do an unused native VLAN and explicit trunk allowlists help reduce VLAN-hopping and double-tagging risk?
7. 7. Under the stated policy, may guest, IoT, or lab initiate unrestricted traffic to another internal zone?

## Guided lab

### step
1

### name
Create the isolated lesson directory and design artifacts

### action
Run the generator. It creates only files under /opt/lab-classroom/class70/ and does not contact or configure network equipment.

### command
python3 - <<'PY'
from pathlib import Path
import csv, json
base = Path('/opt/lab-classroom/class70')
base.mkdir(exist_ok=True)
vlans = [
    {'vlan_id':'10','name':'management','subnet':'10.70.10.0/24','gateway':'10.70.10.1','routed':'true','purpose':'authorized administration'},
    {'vlan_id':'20','name':'infrastructure','subnet':'10.70.20.0/24','gateway':'10.70.20.1','routed':'true','purpose':'shared internal services'},
    {'vlan_id':'30','name':'lab','subnet':'10.70.30.0/24','gateway':'10.70.30.1','routed':'true','purpose':'experimental workloads'},
    {'vlan_id':'40','name':'guest','subnet':'10.70.40.0/24','gateway':'10.70.40.1','routed':'true','purpose':'internet-only guest clients'},
    {'vlan_id':'50','name':'iot','subnet':'10.70.50.0/24','gateway':'10.70.50.1','routed':'true','purpose':'restricted embedded devices'},
    {'vlan_id':'999','name':'blackhole','subnet':'','gateway':'','routed':'false','purpose':'disabled ports and untagged trunk traffic'}
]
ports = [
    {'port':'core-01','device':'router','mode':'trunk','tagged_vlans':'10;20;30;40;50','untagged_vlan':'999','pvid':'999','admin_state':'up','purpose':'all routed VLANs'},
    {'port':'core-02','device':'hypervisor-01','mode':'trunk','tagged_vlans':'10;20;30','untagged_vlan':'999','pvid':'999','admin_state':'up','purpose':'tagged host management plus infrastructure and lab workloads'},
    {'port':'core-03','device':'ap-01','mode':'trunk','tagged_vlans':'10;40;50','untagged_vlan':'999','pvid':'999','admin_state':'up','purpose':'tagged AP management plus guest and IoT SSIDs'},
    {'port':'core-04','device':'nas-01','mode':'access','tagged_vlans':'','untagged_vlan':'20','pvid':'20','admin_state':'up','purpose':'infrastructure NAS'},
    {'port':'core-05','device':'admin-workstation','mode':'access','tagged_vlans':'','untagged_vlan':'10','pvid':'10','admin_state':'up','purpose':'management client'},
    {'port':'core-06','device':'lab-node','mode':'access','tagged_vlans':'','untagged_vlan':'30','pvid':'30','admin_state':'up','purpose':'lab endpoint'},
    {'port':'core-07','device':'unused','mode':'access','tagged_vlans':'','untagged_vlan':'999','pvid':'999','admin_state':'down','purpose':'disabled unused port'}
]
policy = []
for zone in ('management','infrastructure','lab','guest','iot'):
    policy.extend([
        {'source':zone,'destination':'gateway_services','protocol':'udp','destination_ports':'67-68','action':'allow','purpose':'DHCP address configuration'},
        {'source':zone,'destination':'gateway_services','protocol':'udp','destination_ports':'53','action':'allow','purpose':'DNS queries'},
        {'source':zone,'destination':'gateway_services','protocol':'tcp','destination_ports':'53','action':'allow','purpose':'DNS fallback and large responses'},
        {'source':zone,'destination':'gateway_services','protocol':'udp','destination_ports':'123','action':'allow','purpose':'NTP time synchronization'}
    ])
for zone in ('management','infrastructure','lab','guest','iot'):
    policy.append({'source':zone,'destination':'internet','protocol':'tcp','destination_ports':'80,443','action':'allow','purpose':'approved web and update access'})
for zone in ('lab','guest','iot'):
    policy.append({'source':zone,'destination':'internet','protocol':'udp','destination_ports':'443','action':'allow','purpose':'approved QUIC internet access'})
policy.extend([
    {'source':'management','destination':'infrastructure','protocol':'tcp','destination_ports':'22,443','action':'allow','purpose':'authorized service administration'},
    {'source':'management','destination':'iot','protocol':'tcp','destination_ports':'443','action':'allow','purpose':'authorized IoT web administration'}
])
for source in ('lab','guest','iot'):
    for destination in ('management','infrastructure','lab','guest','iot'):
        if destination != source:
            policy.append({'source':source,'destination':destination,'protocol':'any','destination_ports':'any','action':'deny','purpose':'explicit internal isolation'})
def write_csv(name, rows, fields):
    with (base / name).open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
write_csv('vlans.csv', vlans, ['vlan_id','name','subnet','gateway','routed','purpose'])
write_csv('ports.csv', ports, ['port','device','mode','tagged_vlans','untagged_vlan','pvid','admin_state','purpose'])
write_csv('policy-matrix.csv', policy, ['source','destination','protocol','destination_ports','action','purpose'])
(base / 'policy-meta.json').write_text(json.dumps({'default_action':'deny','defined_destinations':['management','infrastructure','lab','guest','iot','gateway_services','internet']}, indent=2) + '\n', encoding='utf-8')
print('Created VLAN, port, and policy artifacts in', base)
PY

### expected
The directory contains vlans.csv, ports.csv, policy-matrix.csv, and policy-meta.json.
### step
2

### name
Install the semantic validator

### action
Create a validator that checks addressing, access and trunk consistency, hypervisor trunk restrictions, disabled unused ports, required infrastructure services, explicit internet access, explicit internal denials, and the default-deny policy.

### command
python3 - <<'PY'
from pathlib import Path
base = Path('/opt/lab-classroom/class70')
validator = r'''from pathlib import Path
import csv, ipaddress, json
base = Path('/opt/lab-classroom/class70')

def rows(name):
    with (base / name).open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))

vlans = rows('vlans.csv')
ports = rows('ports.csv')
policy = rows('policy-matrix.csv')
meta = json.loads((base / 'policy-meta.json').read_text(encoding='utf-8'))

expected_vlans = {
    '10': ('management', '10.70.10.0/24', '10.70.10.1', 'true'),
    '20': ('infrastructure', '10.70.20.0/24', '10.70.20.1', 'true'),
    '30': ('lab', '10.70.30.0/24', '10.70.30.1', 'true'),
    '40': ('guest', '10.70.40.0/24', '10.70.40.1', 'true'),
    '50': ('iot', '10.70.50.0/24', '10.70.50.1', 'true'),
    '999': ('blackhole', '', '', 'false')
}
assert len(vlans) == len(expected_vlans), 'VLAN inventory must exactly match the approved design'
seen_ids = set()
networks = []
for row in vlans:
    vid = row['vlan_id']
    assert vid not in seen_ids, f'duplicate VLAN ID {vid}'
    seen_ids.add(vid)
    assert vid in expected_vlans, f'unapproved VLAN ID {vid}'
    assert (row['name'], row['subnet'], row['gateway'], row['routed']) == expected_vlans[vid], f'VLAN {vid} differs from the approved design'
    if row['routed'] == 'true':
        network = ipaddress.ip_network(row['subnet'])
        assert ipaddress.ip_address(row['gateway']) in network, f'gateway outside subnet for VLAN {vid}'
        assert all(not network.overlaps(existing) for existing in networks), f'overlapping subnet {network}'
        networks.append(network)
assert seen_ids == set(expected_vlans), 'required VLAN missing'

port_by_name = {row['port']: row for row in ports}
assert len(port_by_name) == len(ports), 'duplicate port name'
for row in ports:
    assert row['mode'] in {'access','trunk'}, f"invalid mode on {row['port']}"
    assert row['admin_state'] in {'up','down'}, f"invalid administrative state on {row['port']}"
    tagged = {item for item in row['tagged_vlans'].split(';') if item}
    assert 'all' not in tagged and '*' not in tagged, f"wildcard trunk allowlist on {row['port']}"
    assert tagged <= set(expected_vlans), f"unknown tagged VLAN on {row['port']}"
    if row['mode'] == 'access':
        assert not tagged, f"access port {row['port']} must not have tagged VLANs"
        assert row['untagged_vlan'] == row['pvid'], f"access port {row['port']} has inconsistent untagged VLAN and PVID"
    else:
        assert row['untagged_vlan'] == '999' and row['pvid'] == '999', f"trunk {row['port']} must use blackhole VLAN 999 for untagged traffic"
assert set(port_by_name['core-01']['tagged_vlans'].split(';')) == {'10','20','30','40','50'}, 'router trunk allowlist is incorrect'
hypervisor_tags = set(port_by_name['core-02']['tagged_vlans'].split(';'))
assert hypervisor_tags == {'10','20','30'}, 'hypervisor trunk must carry only management, infrastructure, and lab VLANs'
assert '40' not in hypervisor_tags and '50' not in hypervisor_tags, 'hypervisor trunk must omit guest and IoT VLANs'
assert set(port_by_name['core-03']['tagged_vlans'].split(';')) == {'10','40','50'}, 'access-point trunk allowlist is incorrect'
for row in ports:
    if row['device'] == 'unused':
        assert row['admin_state'] == 'down', f"unused port {row['port']} must be administratively disabled"
        assert row['mode'] == 'access' and row['untagged_vlan'] == '999' and row['pvid'] == '999', f"unused port {row['port']} must be in VLAN 999"

assert meta.get('default_action') == 'deny', 'policy default must be deny'
defined_sources = {'management','infrastructure','lab','guest','iot'}
defined_destinations = set(meta.get('defined_destinations', []))
assert defined_destinations == {'management','infrastructure','lab','guest','iot','gateway_services','internet'}, 'destination definitions are incomplete or unexpected'
valid_actions = {'allow','deny'}
policy_set = set()
for row in policy:
    assert row['source'] in defined_sources, f"undefined source {row['source']}"
    assert row['destination'] in defined_destinations, f"undefined destination {row['destination']}"
    assert row['action'] in valid_actions, f"vague or invalid action {row['action']}"
    assert row['protocol'] in {'tcp','udp','any'}, f"invalid protocol {row['protocol']}"
    assert row['purpose'].strip(), 'every policy row requires a purpose'
    key = (row['source'], row['destination'], row['protocol'], row['destination_ports'], row['action'])
    assert key not in policy_set, f'duplicate policy row {key}'
    policy_set.add(key)
    if row['action'] == 'allow':
        assert row['protocol'] != 'any' and row['destination_ports'] != 'any', f'overly broad allow rule {key}'

for zone in defined_sources:
    required = {
        (zone,'gateway_services','udp','67-68','allow'),
        (zone,'gateway_services','udp','53','allow'),
        (zone,'gateway_services','tcp','53','allow'),
        (zone,'gateway_services','udp','123','allow'),
        (zone,'internet','tcp','80,443','allow')
    }
    assert required <= policy_set, f'missing DHCP, DNS, NTP, or internet flow for {zone}'
for zone in {'lab','guest','iot'}:
    assert (zone,'internet','udp','443','allow') in policy_set, f'missing approved QUIC internet flow for {zone}'

internal = {'management','infrastructure','lab','guest','iot'}
restricted = {'lab','guest','iot'}
for source in restricted:
    for destination in internal - {source}:
        denial = (source,destination,'any','any','deny')
        assert denial in policy_set, f'missing explicit denial from {source} to {destination}'
for row in policy:
    if row['source'] in restricted and row['destination'] in internal and row['destination'] != row['source']:
        assert row['action'] == 'deny', f"restricted internal allow found: {row}"
assert ('management','infrastructure','tcp','22,443','allow') in policy_set, 'management administration flow is missing'
assert ('management','iot','tcp','443','allow') in policy_set, 'IoT administration flow is missing'
print('PASS: VLANs, subnets, ports, trunk restrictions, required services, internet flows, internal denials, and default deny are valid')
'''
(base / 'validate_plan.py').write_text(validator, encoding='utf-8')
print('Created', base / 'validate_plan.py')
PY

### expected
The file /opt/lab-classroom/class70/validate_plan.py exists.
### step
3

### name
Validate the complete design

### action
Run the semantic validator. Correct the data rather than weakening validator assertions if a check fails.

### command
python3 /opt/lab-classroom/class70/validate_plan.py

### expected
The command prints a single PASS line confirming VLAN, subnet, port, trunk, service, internet, denial, and default-deny checks.
### step
4

### name
Inspect the hypervisor trunk decision

### action
Display the core-02 record and confirm that VLAN 10 is present only for the explicitly documented host management interface, while VLANs 40 and 50 are absent.

### command
python3 - <<'PY'
import csv
from pathlib import Path
path = Path('/opt/lab-classroom/class70/ports.csv')
with path.open(newline='', encoding='utf-8') as handle:
    for row in csv.DictReader(handle):
        if row['port'] == 'core-02':
            print(row)
PY

### expected
The output shows tagged_vlans as 10;20;30, describes tagged host management, and contains neither VLAN 40 nor VLAN 50.
### step
5

### name
Perform a controlled negative test

### action
Use an in-memory modification to demonstrate that an all-VLAN hypervisor trunk would violate the design. This command does not change any artifact.

### command
python3 - <<'PY'
approved = {'10','20','30'}
candidate = {'10','20','30','40','50'}
extra = candidate - approved
assert extra == {'40','50'}
print('REJECT: candidate hypervisor trunk contains unapproved VLANs', ','.join(sorted(extra)))
PY

### expected
The command rejects VLANs 40 and 50 as unapproved on the hypervisor trunk.
### step
6

### name
Review the policy matrix by intent

### action
Print all guest rules to verify required services, approved internet traffic, and explicit internal denials.

### command
python3 - <<'PY'
import csv
from pathlib import Path
path = Path('/opt/lab-classroom/class70/policy-matrix.csv')
with path.open(newline='', encoding='utf-8') as handle:
    for row in csv.DictReader(handle):
        if row['source'] == 'guest':
            print('{source} -> {destination} {protocol}/{destination_ports} {action}: {purpose}'.format(**row))
PY

### expected
Guest has DHCP, DNS, NTP, TCP web, and UDP 443 internet flows, plus explicit deny entries for management, infrastructure, lab, and IoT.

## Expected results

- Six VLAN records exist, including five routed VLANs and one unrouted blackhole VLAN.
- Every routed VLAN has a unique non-overlapping /24 subnet and a gateway inside that subnet.
- Access ports have no tagged VLANs and use matching untagged VLAN and PVID values.
- All active trunks use VLAN 999 for untagged traffic and carry explicit tagged allowlists.
- The hypervisor trunk carries VLANs 10, 20, and 30 because the host has a tagged management interface and approved infrastructure and lab workloads.
- The hypervisor trunk does not carry guest VLAN 40 or IoT VLAN 50.
- The unused port is assigned to VLAN 999 and administratively down.
- Every client zone has explicit DHCP, DNS over UDP and TCP, NTP, and TCP internet web flows.
- Lab, guest, and IoT have an explicit UDP 443 internet flow and explicit deny rules to every other internal zone.
- The policy metadata declares deny as the default action.
- The validator prints PASS without changing live network configuration.

## Verification checkpoints

- [ ] Run `python3 /opt/lab-classroom/class70/validate_plan.py`; it must print `PASS: VLANs, subnets, ports, trunk restrictions, required services, internet flows, internal denials, and default deny are valid`.
- [ ] Run `grep '^core-02,' /opt/lab-classroom/class70/ports.csv`; the tagged VLAN field must be `10;20;30` and must not contain 40 or 50.
- [ ] Run `grep '^core-07,' /opt/lab-classroom/class70/ports.csv`; the record must show access mode, untagged VLAN 999, PVID 999, and administrative state down.
- [ ] Run `grep '^guest,gateway_services' /opt/lab-classroom/class70/policy-matrix.csv`; DHCP, DNS over UDP, DNS over TCP, and NTP rows must all be present.
- [ ] Run `grep '^guest,internet' /opt/lab-classroom/class70/policy-matrix.csv`; TCP ports 80 and 443 and UDP port 443 must be explicitly allowed.
- [ ] Run `grep '^iot,internet' /opt/lab-classroom/class70/policy-matrix.csv`; TCP ports 80 and 443 and UDP port 443 must be explicitly allowed.
- [ ] Run `grep '^guest,management,any,any,deny' /opt/lab-classroom/class70/policy-matrix.csv`; an explicit guest-to-management denial must be present.
- [ ] Run `grep '^iot,infrastructure,any,any,deny' /opt/lab-classroom/class70/policy-matrix.csv`; an explicit IoT-to-infrastructure denial must be present.
- [ ] Run `grep '^lab,infrastructure,any,any,deny' /opt/lab-classroom/class70/policy-matrix.csv`; an explicit lab-to-infrastructure denial must be present.
- [ ] Run `python3 -c "import json; print(json.load(open('/opt/lab-classroom/class70/policy-meta.json'))['default_action'])"`; the output must be `deny`.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The generator reports that /opt/lab-classroom/class70 does not have a parent directory. | The required classroom parent path was not prepared before the lesson. | Have the lab administrator create /opt/lab-classroom according to the classroom platform standard, then rerun the generator. Do not redirect the lesson into an unrelated system path. |
| The validator reports that the hypervisor trunk is incorrect. | The core-02 tagged VLAN list was changed, reordered with unexpected values, or expanded to include guest or IoT. | Set the semicolon-delimited tagged_vlans value for core-02 to exactly 10;20;30. VLAN 10 is required for the documented tagged host-management interface; VLANs 40 and 50 are not required. |
| The validator reports an overly broad allow rule. | An allow entry uses protocol any or destination_ports any. | Replace the broad entry with one or more rows naming the actual protocol and destination ports needed for the service. |
| The validator reports a missing DHCP, DNS, NTP, or internet flow. | A required gateway_services or internet row was deleted or edited. | Restore the exact service row for the affected zone, including protocol, destination ports, allow action, and purpose. |
| The validator reports a restricted internal allow. | Lab, guest, or IoT was granted access to another internal zone. | Remove the allow entry and retain the explicit any/any deny for that source-destination pair. Add a narrowly scoped exception only after a documented design review and corresponding validator update. |
| The validator reports an overlapping subnet. | Two routed VLAN records use intersecting IPv4 networks. | Assign a unique non-overlapping subnet and update its gateway so the gateway remains inside the new subnet. |
| An unused port fails validation. | The port is assigned to VLAN 999 but remains administratively up, or its PVID differs from its untagged VLAN. | Set mode to access, untagged_vlan and pvid to 999, and admin_state to down. |
| A command fails with permission denied. | The current account lacks write access to the dedicated lesson directory. | Ask the lab administrator to grant appropriate ownership or write access to /opt/lab-classroom/class70. Do not broaden permissions globally. |

## Security considerations

### threats
### threat
Excessive trunk exposure

### control
Use explicit tagged VLAN allowlists. The hypervisor trunk is limited to VLANs 10, 20, and 30 and omits guest and IoT.
### threat
VLAN hopping through dynamic trunk formation

### control
Use statically defined access or trunk modes and disable dynamic trunk negotiation where the platform supports it.
### threat
Double-tagging VLAN hopping

### control
Do not use a user, server, or management VLAN as the trunk native VLAN. Map untagged trunk traffic to unrouted VLAN 999 and configure both ends consistently.
### threat
Unauthorized use of an empty switch port

### control
Assign unused ports to VLAN 999 and administratively disable them. VLAN assignment alone is not sufficient.
### threat
Untrusted lateral movement

### control
Explicitly deny lab, guest, and IoT traffic to other internal zones and use default deny for unlisted traffic.
### threat
Loss of essential client services after segmentation

### control
Explicitly document DHCP, DNS, and NTP access for every client zone before deployment.
### threat
Accidental exposure of management interfaces

### control
Carry the management VLAN only where an explicitly documented management interface requires it. Remove VLAN 10 from a trunk if management moves to a separate physical access port.

### operational_notes
VLAN separation does not authenticate users or encrypt traffic.
The Layer 3 policy implementation should log denied new connections at a sustainable rate.
Management access should originate only from controlled administration systems.
Do not create an SVI or gateway for VLAN 999.
Confirm native or untagged VLAN behavior on both ends before connecting a trunk.
Back up live device configurations before translating this design into production syntax.

## Rollback

### step
1

### action
List the exact lesson artifacts before deletion.

### command
python3 - <<'PY'
from pathlib import Path
base = Path('/opt/lab-classroom/class70')
for name in ('vlans.csv','ports.csv','policy-matrix.csv','policy-meta.json','validate_plan.py'):
    path = base / name
    print(path, 'present' if path.exists() else 'absent')
PY

### verification
Only the five documented lesson files are targeted.
### step
2

### action
Delete only the known lesson artifacts and remove the lesson directory only if it is empty.

### command
python3 - <<'PY'
from pathlib import Path
base = Path('/opt/lab-classroom/class70')
expected = Path('/opt/lab-classroom/class70')
assert base.resolve() == expected
for name in ('vlans.csv','ports.csv','policy-matrix.csv','policy-meta.json','validate_plan.py'):
    (base / name).unlink(missing_ok=True)
if base.exists() and not any(base.iterdir()):
    base.rmdir()
print('Rollback complete')
PY

### verification
The command prints `Rollback complete`. If unrelated files exist, the directory remains and those files are not removed.

## Video narration notes

Begin with the architecture rather than vendor commands. Five routed VLANs separate management, infrastructure, lab, guest, and IoT systems. VLAN 999 is different: it has no gateway and is used for disabled ports and untagged traffic on trunks. Examine the port records. Access ports have no tagged VLANs, and their untagged VLAN equals their PVID. Trunks use explicit allowlists. The router trunk carries all routed VLANs because it provides their gateways. The hypervisor trunk carries VLAN 10 only because the host has a documented tagged management interface; it also carries infrastructure and lab, but it excludes guest and IoT. The access-point trunk carries management for the access point itself and guest and IoT for its wireless networks. Next, examine policy intent. Every zone has DHCP, DNS, NTP, and approved internet flows. Guest, IoT, and lab are explicitly denied access to other internal zones, and the overall default is deny. Finally, run the validator. It checks more than file shape: it rejects wildcard trunks, verifies that the hypervisor omits VLANs 40 and 50, requires disabled unused ports, detects broad allow rules, and confirms the required service and denial relationships. This lab produces design artifacts only and does not change live equipment.

## References

- IEEE 802.1Q standard overview: https://standards.ieee.org/ieee/802.1Q/6844/
- RFC 1918, Address Allocation for Private Internets: https://www.rfc-editor.org/rfc/rfc1918
- RFC 2131, Dynamic Host Configuration Protocol: https://www.rfc-editor.org/rfc/rfc2131
- RFC 1034, Domain Names—Concepts and Facilities: https://www.rfc-editor.org/rfc/rfc1034
- RFC 1035, Domain Names—Implementation and Specification: https://www.rfc-editor.org/rfc/rfc1035
- RFC 5905, Network Time Protocol Version 4: https://www.rfc-editor.org/rfc/rfc5905
- CISA, Securing Network Infrastructure Devices: https://www.cisa.gov/news-events/news/securing-network-infrastructure-devices

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

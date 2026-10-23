# Lab: VLAN Design for a Homelab

**Module:** Segmentation, Backup & Power
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Separate homelab devices into VLANs based on trust, function, and operational requirements

## Before you start

- Basic understanding of Ethernet switching, IP addressing, subnets, and default gateways
- Familiarity with access ports, tagged frames, and the purpose of a router or Layer 3 gateway
- Python 3.9 or newer with the standard library
- Write permission to /opt/lab-classroom/class70/
- The parent directory /opt/lab-classroom/ must already exist
- No production switch, router, access point, or hypervisor configuration is changed in this lab

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

## Verification

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

## Security

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

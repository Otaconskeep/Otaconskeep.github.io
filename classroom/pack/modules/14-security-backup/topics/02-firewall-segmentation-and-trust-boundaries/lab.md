# Lab: Firewall Segmentation and Trust Boundaries

**Module:** Segmentation, Backup & Power
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Define zones as groups of systems with similar trust and policy requirements.

## Before you start

- Comfort using a Linux shell and changing directories.
- Basic understanding of IPv4 addresses, CIDR prefixes, TCP ports, and client-server traffic.
- Ability to read JSON and run Python 3 scripts.
- Completion of introductory networking and least-privilege lessons is recommended.
- Write access to /opt/lab-classroom/class71/.

## Guided lab

### workspace
/opt/lab-classroom/class71/

### constraints
Run the commands as an account that can write to the workspace.
Do not substitute a real packet-filter command for the simulator.
Every created or modified lab artifact remains below /opt/lab-classroom/class71/.
The host audit reads selected host configuration paths but writes its snapshot only inside the workspace.

### steps
### step
1

### title
Create the complete lab artifacts in a clean workspace

### explanation
These commands create every required script and data file. reset_data.py contains durable embedded originals for policy.json and flows.json, so recovery does not depend on policy.json.bak.

### commands
mkdir -p /opt/lab-classroom/class71 && cd /opt/lab-classroom/class71
cat > /opt/lab-classroom/class71/reset_data.py <<'PY'
from pathlib import Path
import json

ROOT = Path('/opt/lab-classroom/class71')
POLICY = {
    'zones': {
        'admin': {'cidr': '10.71.10.0/24', 'address_standard': 'RFC1918'},
        'servers': {'cidr': '10.71.20.0/24', 'address_standard': 'RFC1918'},
        'users': {'cidr': '10.71.30.0/24', 'address_standard': 'RFC1918'},
        'monitoring': {'cidr': '10.71.40.0/24', 'address_standard': 'RFC1918'},
        'external-test': {'cidr': '203.0.113.0/24', 'address_standard': 'RFC5737'}
    },
    'rules': [
        {'name': 'allow-admin-ssh', 'src': 'admin', 'dst': 'servers', 'protocol': 'tcp', 'port': 22, 'action': 'allow'},
        {'name': 'allow-users-https', 'src': 'users', 'dst': 'servers', 'protocol': 'tcp', 'port': 443, 'action': 'allow'},
        {'name': 'allow-server-egress-https', 'src': 'servers', 'dst': 'external-test', 'protocol': 'tcp', 'port': 443, 'action': 'allow'},
        {'name': 'default-deny', 'src': 'any', 'dst': 'any', 'protocol': 'any', 'port': 'any', 'action': 'deny'}
    ]
}
FLOWS = [
    {'name': 'admin-ssh', 'src_zone': 'admin', 'src_ip': '10.71.10.10', 'dst_zone': 'servers', 'dst_ip': '10.71.20.21', 'protocol': 'tcp', 'port': 22},
    {'name': 'users-https', 'src_zone': 'users', 'src_ip': '10.71.30.50', 'dst_zone': 'servers', 'dst_ip': '10.71.20.25', 'protocol': 'tcp', 'port': 443},
    {'name': 'users-ssh-denied', 'src_zone': 'users', 'src_ip': '10.71.30.50', 'dst_zone': 'servers', 'dst_ip': '10.71.20.21', 'protocol': 'tcp', 'port': 22},
    {'name': 'server-egress-https', 'src_zone': 'servers', 'src_ip': '10.71.20.25', 'dst_zone': 'external-test', 'dst_ip': '203.0.113.20', 'protocol': 'tcp', 'port': 443},
    {'name': 'monitoring-node-exporter', 'src_zone': 'monitoring', 'src_ip': '10.71.40.10', 'dst_zone': 'servers', 'dst_ip': '10.71.20.21', 'protocol': 'tcp', 'port': 9100},
    {'name': 'monitoring-blackbox', 'src_zone': 'monitoring', 'src_ip': '10.71.40.11', 'dst_zone': 'servers', 'dst_ip': '10.71.20.25', 'protocol': 'tcp', 'port': 9115},
    {'name': 'external-to-admin-denied', 'src_zone': 'external-test', 'src_ip': '203.0.113.30', 'dst_zone': 'admin', 'dst_ip': '10.71.10.10', 'protocol': 'tcp', 'port': 22}
]
ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / 'policy.json').write_text(json.dumps(POLICY, indent=2) + '\n')
(ROOT / 'flows.json').write_text(json.dumps(FLOWS, indent=2) + '\n')
print('Reinstalled original policy.json and flows.json')
PY
python3 /opt/lab-classroom/class71/reset_data.py
cat > /opt/lab-classroom/class71/evaluate.py <<'PY'
from pathlib import Path
import ipaddress
import json
import sys

ROOT = Path('/opt/lab-classroom/class71')
policy = json.loads((ROOT / 'policy.json').read_text())
flows = json.loads((ROOT / 'flows.json').read_text())
zones = policy['zones']


def validate_endpoint(flow, side):
    zone_name = flow[side + '_zone']
    ip_text = flow[side + '_ip']
    if zone_name not in zones:
        raise ValueError(f"{flow['name']}: unknown {side} zone {zone_name}")
    network = ipaddress.ip_network(zones[zone_name]['cidr'])
    address = ipaddress.ip_address(ip_text)
    if address not in network:
        raise ValueError(f"{flow['name']}: {side} IP {address} is outside {zone_name} {network}")


def field_matches(rule_value, flow_value):
    return rule_value == 'any' or rule_value == flow_value


def evaluate(flow):
    validate_endpoint(flow, 'src')
    validate_endpoint(flow, 'dst')
    for position, rule in enumerate(policy['rules'], start=1):
        if not field_matches(rule['src'], flow['src_zone']):
            continue
        if not field_matches(rule['dst'], flow['dst_zone']):
            continue
        if not field_matches(rule['protocol'], flow['protocol']):
            continue
        if not field_matches(rule['port'], flow['port']):
            continue
        return {
            'flow': flow['name'],
            'decision': rule['action'],
            'matched_rule': rule['name'],
            'rule_position': position,
            'src_zone': flow['src_zone'],
            'dst_zone': flow['dst_zone']
        }
    raise ValueError(f"{flow['name']}: no rule matched; policy requires an explicit terminal rule")


try:
    for item in flows:
        print(json.dumps(evaluate(item), sort_keys=True))
except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
    print(f'POLICY ERROR: {exc}', file=sys.stderr)
    sys.exit(2)
PY
cat > /opt/lab-classroom/class71/assert_results.py <<'PY'
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path('/opt/lab-classroom/class71')
EXPECTED = {
    'baseline': {
        'admin-ssh': ('allow', 'allow-admin-ssh'),
        'users-https': ('allow', 'allow-users-https'),
        'users-ssh-denied': ('deny', 'default-deny'),
        'server-egress-https': ('allow', 'allow-server-egress-https'),
        'monitoring-node-exporter': ('deny', 'default-deny'),
        'monitoring-blackbox': ('deny', 'default-deny'),
        'external-to-admin-denied': ('deny', 'default-deny')
    },
    'changed': {
        'admin-ssh': ('allow', 'allow-admin-ssh'),
        'users-https': ('allow', 'allow-users-https'),
        'users-ssh-denied': ('deny', 'default-deny'),
        'server-egress-https': ('allow', 'allow-server-egress-https'),
        'monitoring-node-exporter': ('allow', 'allow-monitoring-node-exporter'),
        'monitoring-blackbox': ('allow', 'allow-monitoring-blackbox'),
        'external-to-admin-denied': ('deny', 'default-deny')
    }
}

if len(sys.argv) != 2 or sys.argv[1] not in EXPECTED:
    print('Usage: python3 assert_results.py baseline|changed', file=sys.stderr)
    sys.exit(2)
mode = sys.argv[1]
run = subprocess.run([sys.executable, str(ROOT / 'evaluate.py')], text=True, capture_output=True)
if run.returncode != 0:
    print(run.stderr, end='', file=sys.stderr)
    sys.exit(run.returncode)
actual = {}
for line in run.stdout.splitlines():
    result = json.loads(line)
    actual[result['flow']] = (result['decision'], result['matched_rule'])
failures = []
for flow, expected in EXPECTED[mode].items():
    observed = actual.get(flow)
    if observed != expected:
        failures.append(f'{flow}: expected {expected}, observed {observed}')
extra = sorted(set(actual) - set(EXPECTED[mode]))
if extra:
    failures.append(f'unexpected flows: {extra}')
if failures:
    print('\n'.join(failures), file=sys.stderr)
    sys.exit(1)
print(f'{mode} assertions passed for {len(EXPECTED[mode])} flows')
PY
cat > /opt/lab-classroom/class71/edit_policy.py <<'PY'
from pathlib import Path
import json
import sys

ROOT = Path('/opt/lab-classroom/class71')
NEW_RULES = [
    {'name': 'allow-monitoring-node-exporter', 'src': 'monitoring', 'dst': 'servers', 'protocol': 'tcp', 'port': 9100, 'action': 'allow'},
    {'name': 'allow-monitoring-blackbox', 'src': 'monitoring', 'dst': 'servers', 'protocol': 'tcp', 'port': 9115, 'action': 'allow'}
]

if len(sys.argv) != 2 or sys.argv[1] not in ('shadow', 'correct'):
    print('Usage: python3 edit_policy.py shadow|correct', file=sys.stderr)
    sys.exit(2)
mode = sys.argv[1]
path = ROOT / 'policy.json'
policy = json.loads(path.read_text())
new_names = {rule['name'] for rule in NEW_RULES}
policy['rules'] = [rule for rule in policy['rules'] if rule['name'] not in new_names]
if mode == 'shadow':
    policy['rules'].extend(NEW_RULES)
    print('Inserted monitoring allows after default-deny; they are intentionally shadowed')
else:
    deny_positions = [index for index, rule in enumerate(policy['rules']) if rule['name'] == 'default-deny']
    if len(deny_positions) != 1:
        raise SystemExit('Expected exactly one default-deny rule')
    insertion = deny_positions[0]
    policy['rules'][insertion:insertion] = NEW_RULES
    print('Inserted monitoring allows immediately before default-deny')
path.write_text(json.dumps(policy, indent=2) + '\n')
for position, rule in enumerate(policy['rules'], start=1):
    print(f"{position}: {rule['name']} -> {rule['action']}")
PY
cat > /opt/lab-classroom/class71/check_addressing.py <<'PY'
from pathlib import Path
import ipaddress
import json
import sys

ROOT = Path('/opt/lab-classroom/class71')
policy = json.loads((ROOT / 'policy.json').read_text())
rfc1918 = [ipaddress.ip_network(value) for value in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16')]
rfc5737 = [ipaddress.ip_network(value) for value in ('192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24')]
standards = {'RFC1918': rfc1918, 'RFC5737': rfc5737}
failures = []
for name, zone in policy['zones'].items():
    network = ipaddress.ip_network(zone['cidr'])
    standard = zone['address_standard']
    valid = standard in standards and any(network.subnet_of(parent) for parent in standards[standard])
    print(f'{name}: {network} declared={standard} valid={str(valid).lower()}')
    if not valid:
        failures.append(name)
if failures:
    print(f'Address-standard failures: {failures}', file=sys.stderr)
    sys.exit(1)
if policy['zones']['monitoring']['address_standard'] != 'RFC1918':
    raise SystemExit('Monitoring must be represented as RFC1918 in this lab')
if policy['zones']['external-test']['address_standard'] != 'RFC5737':
    raise SystemExit('External test zone must be represented as RFC5737')
print('Addressing assertions passed, including monitoring and external-test')
PY
cat > /opt/lab-classroom/class71/host_audit.py <<'PY'
from pathlib import Path
import hashlib
import json
import os
import sys

ROOT = Path('/opt/lab-classroom/class71')
SNAPSHOT = ROOT / 'host-firewall-audit.json'
TARGETS = [
    Path('/etc/nftables.conf'),
    Path('/etc/ufw'),
    Path('/etc/firewalld'),
    Path('/etc/iptables'),
    Path('/etc/sysconfig/iptables'),
    Path('/etc/sysconfig/ip6tables'),
    Path('/proc/sys/net/ipv4/ip_forward')
]


def digest_file(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception as exc:
        return f'UNREADABLE:{type(exc).__name__}'


def inventory():
    result = {}
    for target in TARGETS:
        key = str(target)
        if not target.exists():
            result[key] = {'state': 'absent'}
        elif target.is_file():
            result[key] = {'state': 'file', 'sha256': digest_file(target)}
        elif target.is_dir():
            entries = {}
            for base, dirs, files in os.walk(target):
                dirs.sort()
                files.sort()
                for filename in files:
                    item = Path(base) / filename
                    entries[str(item)] = digest_file(item)
            result[key] = {'state': 'directory', 'entries': entries}
        else:
            result[key] = {'state': 'other'}
    return result


if len(sys.argv) != 2 or sys.argv[1] not in ('capture', 'check'):
    print('Usage: python3 host_audit.py capture|check', file=sys.stderr)
    sys.exit(2)
current = inventory()
if sys.argv[1] == 'capture':
    SNAPSHOT.write_text(json.dumps(current, indent=2, sort_keys=True) + '\n')
    print(f'Captured host firewall configuration fingerprints in {SNAPSHOT}')
else:
    if not SNAPSHOT.exists():
        raise SystemExit('Audit snapshot is missing; run capture first')
    original = json.loads(SNAPSHOT.read_text())
    if current != original:
        print('Host firewall configuration fingerprint changed', file=sys.stderr)
        sys.exit(1)
    for path in ROOT.rglob('*'):
        if not path.resolve().is_relative_to(ROOT.resolve()):
            raise SystemExit(f'Workspace escape detected: {path}')
    print('Host firewall fingerprints unchanged; lab artifacts remain in the class workspace')
PY
cd /opt/lab-classroom/class71 && python3 host_audit.py capture && python3 -m json.tool policy.json >/dev/null && python3 -m json.tool flows.json >/dev/null
### step
2

### title
Evaluate and assert the baseline

### explanation
The baseline assertions explicitly verify both future monitoring flows. Before the change, each must be denied by default-deny. The assertions also verify the exact matched rule for every other flow.

### commands
cd /opt/lab-classroom/class71 && python3 evaluate.py
cd /opt/lab-classroom/class71 && python3 assert_results.py baseline
cd /opt/lab-classroom/class71 && python3 check_addressing.py
### step
3

### title
Create a non-consuming backup

### explanation
The copy remains available after restoration because later restoration uses another copy operation rather than a move or replace operation.

### commands
cd /opt/lab-classroom/class71 && cp -p policy.json policy.json.bak
cd /opt/lab-classroom/class71 && test -s policy.json.bak && cmp -s policy.json policy.json.bak && echo 'Backup verified'
### step
4

### title
Intentionally create and observe shadowed rules

### explanation
The edit script prints the complete rule order. In shadow mode it appends both monitoring allows after default-deny. First-match processing therefore continues to deny both flows with the default-deny rule.

### commands
cd /opt/lab-classroom/class71 && python3 edit_policy.py shadow
cd /opt/lab-classroom/class71 && python3 -m json.tool policy.json
cd /opt/lab-classroom/class71 && python3 evaluate.py
cd /opt/lab-classroom/class71 && python3 assert_results.py baseline
### step
5

### title
Correct the rule order and verify the intended change

### explanation
Correct mode removes prior copies of the two named rules and inserts them immediately before default-deny. The changed assertions require TCP 9100 to match allow-monitoring-node-exporter and TCP 9115 to match allow-monitoring-blackbox. Existing allows and negative tests must remain unchanged.

### commands
cd /opt/lab-classroom/class71 && python3 edit_policy.py correct
cd /opt/lab-classroom/class71 && python3 evaluate.py
cd /opt/lab-classroom/class71 && python3 assert_results.py changed
cd /opt/lab-classroom/class71 && python3 check_addressing.py
### step
6

### title
Restore from the retained backup

### explanation
Copying from the backup restores the baseline while retaining policy.json.bak for another recovery attempt.

### commands
cd /opt/lab-classroom/class71 && cp -p policy.json.bak policy.json
cd /opt/lab-classroom/class71 && test -s policy.json.bak && python3 assert_results.py baseline
### step
7

### title
Remove the backup and prove embedded recovery

### explanation
After confirming ordinary restoration, remove only the scoped backup. Then change the policy again and run reset_data.py. This proves that a missing backup does not prevent scripted recovery to the embedded original policy and flow data.

### commands
cd /opt/lab-classroom/class71 && rm -f -- policy.json.bak && test ! -e policy.json.bak && echo 'Backup removal verified'
cd /opt/lab-classroom/class71 && python3 edit_policy.py correct && python3 assert_results.py changed
cd /opt/lab-classroom/class71 && python3 reset_data.py && python3 assert_results.py baseline
cd /opt/lab-classroom/class71 && test ! -e policy.json.bak && echo 'Embedded recovery succeeded without a backup'
### step
8

### title
Run the host change audit

### explanation
The audit compares selected host firewall and forwarding configuration fingerprints with the snapshot captured before policy experiments. It also rejects any discovered workspace path that resolves outside the class root.

### commands
cd /opt/lab-classroom/class71 && python3 host_audit.py check
find /opt/lab-classroom/class71 -xdev -type f -printf '%p\n' | sort

## Expected results

- The initial artifact installation succeeds in a clean workspace and creates policy.json, flows.json, evaluate.py, assert_results.py, edit_policy.py, check_addressing.py, host_audit.py, and reset_data.py.
- Baseline assertions report that seven flows passed.
- In the baseline, monitoring-node-exporter is denied by default-deny rather than by either new allow rule.
- In the baseline, monitoring-blackbox is denied by default-deny rather than by either new allow rule.
- The addressing check reports the monitoring zone as 10.71.40.0/24 with RFC1918 valid=true.
- The addressing check reports the external-test zone as 203.0.113.0/24 with RFC5737 valid=true.
- After shadow insertion, the printed order places both monitoring allow rules after default-deny and the baseline assertions still pass.
- After corrected insertion, monitoring-node-exporter is allowed by allow-monitoring-node-exporter.
- After corrected insertion, monitoring-blackbox is allowed by allow-monitoring-blackbox.
- The user SSH and external-to-admin negative tests remain denied by default-deny after the change.
- Restoration from policy.json.bak returns the policy to the baseline without consuming the backup.
- The backup-removal test confirms policy.json.bak is absent.
- Running reset_data.py after backup removal restores the embedded original policy and flows, and the baseline assertions pass.
- The host audit reports unchanged host firewall fingerprints and confirms that lab artifacts remain in the class workspace.

## Verification

- [ ] cd /opt/lab-classroom/class71 && python3 reset_data.py && python3 assert_results.py baseline
- [ ] cd /opt/lab-classroom/class71 && python3 evaluate.py | grep -F '"flow": "monitoring-node-exporter"' | grep -F '"matched_rule": "default-deny"' | grep -F '"decision": "deny"'
- [ ] cd /opt/lab-classroom/class71 && python3 evaluate.py | grep -F '"flow": "monitoring-blackbox"' | grep -F '"matched_rule": "default-deny"' | grep -F '"decision": "deny"'
- [ ] cd /opt/lab-classroom/class71 && cp -p policy.json policy.json.bak && python3 edit_policy.py correct && python3 assert_results.py changed
- [ ] cd /opt/lab-classroom/class71 && python3 evaluate.py | grep -F '"flow": "monitoring-node-exporter"' | grep -F '"matched_rule": "allow-monitoring-node-exporter"' | grep -F '"decision": "allow"'
- [ ] cd /opt/lab-classroom/class71 && python3 evaluate.py | grep -F '"flow": "monitoring-blackbox"' | grep -F '"matched_rule": "allow-monitoring-blackbox"' | grep -F '"decision": "allow"'
- [ ] cd /opt/lab-classroom/class71 && python3 check_addressing.py | grep -F 'monitoring: 10.71.40.0/24 declared=RFC1918 valid=true'
- [ ] cd /opt/lab-classroom/class71 && python3 check_addressing.py | grep -F 'external-test: 203.0.113.0/24 declared=RFC5737 valid=true'
- [ ] cd /opt/lab-classroom/class71 && cp -p policy.json.bak policy.json && test -s policy.json.bak && python3 assert_results.py baseline
- [ ] cd /opt/lab-classroom/class71 && rm -f -- policy.json.bak && test ! -e policy.json.bak
- [ ] cd /opt/lab-classroom/class71 && python3 edit_policy.py correct && python3 reset_data.py && test ! -e policy.json.bak && python3 assert_results.py baseline
- [ ] cd /opt/lab-classroom/class71 && python3 host_audit.py check
- [ ] find /opt/lab-classroom/class71 -xdev -type f -printf '%p\n' | sort

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| python3 reports that policy.json or flows.json does not exist. | The artifact installation commands were not completed, or reset_data.py was created but not executed. | Run cd /opt/lab-classroom/class71 && python3 reset_data.py, then validate both JSON files with python3 -m json.tool. |
| The monitoring rules appear in policy.json, but both monitoring flows are still denied by default-deny. | The allow rules were appended after the catch-all default-deny rule and are shadowed by first-match processing. | Run python3 edit_policy.py correct and inspect the printed order to confirm both monitoring allows precede default-deny. |
| A monitoring flow is allowed, but assert_results.py changed fails on the matched rule name. | A broader rule was added ahead of the intended named rule, or a rule name was changed. | Inspect python3 -m json.tool policy.json. Remove the unintended broad rule, preserve the required names, and rerun the changed assertions. |
| The evaluator reports that an IP is outside its declared zone. | A flow IP does not belong to the CIDR associated with its src_zone or dst_zone. | Correct the flow address or zone label. Do not bypass the CIDR validation because it protects the accuracy of the trust-boundary model. |
| check_addressing.py reports an address-standard failure. | A zone CIDR was labeled RFC1918 or RFC5737 even though it is not a subnet of the corresponding standard ranges. | Restore the originals with python3 reset_data.py or correct both the CIDR and its address_standard declaration. |
| Restoration from policy.json.bak fails because the backup is missing. | The cleanup step already removed the backup or the backup was never created. | Run python3 /opt/lab-classroom/class71/reset_data.py. It reinstalls the embedded original policy.json and flows.json without relying on the backup. |
| host_audit.py check says that the snapshot is missing. | The capture step was skipped or host-firewall-audit.json was removed. | Return the policy to baseline with reset_data.py, run host_audit.py capture, repeat only the simulator exercise, and then run host_audit.py check. |
| host_audit.py reports a changed host firewall fingerprint. | A selected host configuration changed after capture, possibly through an unrelated administrator or service. | Stop the lab, review the reported environment with the system owner, and do not claim the lab was host-neutral until the change is understood. The lab itself should use only the simulator. |
| Permission is denied when creating the workspace. | The current account lacks write permission under /opt/lab-classroom. | Have the lab administrator provision /opt/lab-classroom/class71 with appropriate ownership. Do not redirect artifacts to another path because the exercise is scoped to this workspace. |

## Security

### principles
Treat every inter-zone connection as a specific authorization decision.
Use a final default deny and place narrow allows before it.
Keep monitoring separate from administration because telemetry collection does not require general management access.
Test denied paths as carefully as allowed paths.
Verify the matched rule name, not only the resulting allow or deny decision.
Require source and destination addresses to belong to their declared zone CIDRs.
Use RFC 5737 addresses only for examples and documentation, not as private production ranges.
Keep a verified recovery path independent of an easily deleted backup.

### host_safety
The exercise does not invoke a host packet-filter utility, alter routes, enable forwarding, change interfaces, or reload services. The only intended writes are below /opt/lab-classroom/class71/. The audit script reads selected host configuration paths and stores fingerprints in the workspace.

### production_warning
A production segmentation change can interrupt administration, DNS, storage, monitoring, authentication, or application traffic. Production changes require an out-of-band recovery path, platform-specific syntax validation, staged deployment, logging, peer review, and tests from both sides of each boundary.

## Rollback

### preferred_restore
If policy.json.bak exists and has already been verified, run cd /opt/lab-classroom/class71 && cp -p policy.json.bak policy.json. This restores from the backup without consuming it.

### backup_independent_restore
If policy.json.bak is absent, run cd /opt/lab-classroom/class71 && python3 reset_data.py. This deterministically rewrites the embedded original policy.json and flows.json.

### post_restore_verification
Run cd /opt/lab-classroom/class71 && python3 assert_results.py baseline && python3 check_addressing.py.

### backup_cleanup
After successful restoration and verification, run cd /opt/lab-classroom/class71 && rm -f -- policy.json.bak && test ! -e policy.json.bak.

### scope_confirmation
Run cd /opt/lab-classroom/class71 && python3 host_audit.py check, then list workspace files with find /opt/lab-classroom/class71 -xdev -type f -printf '%p\n' | sort.

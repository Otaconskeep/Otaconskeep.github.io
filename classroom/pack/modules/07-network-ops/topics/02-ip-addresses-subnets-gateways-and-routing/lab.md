# Lab — IP Addresses, Subnets, Gateways, and Routing

**Module:** Network Operations
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Distinguish an IPv4 address from a subnet prefix, network address, broadcast address, and usable host range

## Before you start

- Basic command-line navigation
- Permission to read the host network configuration
- Python 3 installed for the offline subnet exercises
- Linux with iproute2 is preferred; equivalent read-only commands are documented for other platforms
- The directory /opt/lab-classroom/class23/ must already exist and be writable by the learner

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

## Verification

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

## Security

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

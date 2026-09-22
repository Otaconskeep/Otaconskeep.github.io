# Lab — Ports, Protocols, and Host Firewalls

**Module:** Network Operations
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Distinguish an IP address, a transport protocol, and a port number

## Before you start

- Basic command-line navigation and process management
- A Linux host or virtual machine with Python 3.9 or newer
- A writable directory already provisioned at /opt/lab-classroom/class25/
- Permission to bind unprivileged TCP and UDP ports on the loopback interface
- Basic familiarity with IPv4 addresses and client-server communication

## Guided lab

### safety_constraints
Do not change the host's real firewall configuration.
Do not bind either listener to a wildcard address or an externally reachable interface.
Create and modify files only below /opt/lab-classroom/class25/.
Use only unprivileged ports.
Run the listener as the current non-root laboratory user.
The policy evaluator is a simulator and must not be represented as active enforcement.

### workspace
/opt/lab-classroom/class25/

### files
### path
/opt/lab-classroom/class25/listener.py

### content
import socket
import sys

if len(sys.argv) != 3 or sys.argv[1] not in {"tcp", "udp"}:
    raise SystemExit("usage: python3 listener.py tcp|udp PORT")

protocol = sys.argv[1]
port = int(sys.argv[2])
if not 1024 <= port <= 65535:
    raise SystemExit("use an unprivileged port from 1024 through 65535")

kind = socket.SOCK_STREAM if protocol == "tcp" else socket.SOCK_DGRAM
with socket.socket(socket.AF_INET, kind) as server:
    server.bind(("127.0.0.1", port))
    if protocol == "tcp":
        server.listen(1)
    print(f"READY {protocol} 127.0.0.1:{port}", flush=True)
    if protocol == "tcp":
        connection, peer = server.accept()
        with connection:
            data = connection.recv(1024)
            connection.sendall(b"ACK:" + data)
            print(f"TCP_PEER {peer[0]}:{peer[1]} DATA {data.decode(errors='replace')}", flush=True)
    else:
        data, peer = server.recvfrom(1024)
        server.sendto(b"ACK:" + data, peer)
        print(f"UDP_PEER {peer[0]}:{peer[1]} DATA {data.decode(errors='replace')}", flush=True)

### path
/opt/lab-classroom/class25/probe.py

### content
import socket
import sys

if len(sys.argv) != 5 or sys.argv[1] not in {"tcp", "udp"}:
    raise SystemExit("usage: python3 probe.py tcp|udp HOST PORT MESSAGE")

protocol, host, port_text, message = sys.argv[1:]
port = int(port_text)
kind = socket.SOCK_STREAM if protocol == "tcp" else socket.SOCK_DGRAM
with socket.socket(socket.AF_INET, kind) as client:
    client.settimeout(3)
    if protocol == "tcp":
        client.connect((host, port))
        client.sendall(message.encode())
        reply = client.recv(1024)
    else:
        client.sendto(message.encode(), (host, port))
        reply, _ = client.recvfrom(1024)
print(reply.decode(errors="replace"))

### path
/opt/lab-classroom/class25/policy.json

### content
{
  "defaults": {
    "ingress": "DROP",
    "egress": "ACCEPT"
  },
  "rules": [
    {
      "name": "allow-established",
      "direction": "ingress",
      "states": ["established", "related"],
      "action": "ACCEPT"
    },
    {
      "name": "allow-local-web",
      "direction": "ingress",
      "protocol": "tcp",
      "source": "127.0.0.0/8",
      "destination_port": 18080,
      "states": ["new"],
      "action": "ACCEPT"
    },
    {
      "name": "allow-local-dns",
      "direction": "ingress",
      "protocol": "udp",
      "source": "127.0.0.0/8",
      "destination_port": 15353,
      "states": ["new"],
      "action": "ACCEPT"
    }
  ]
}

### path
/opt/lab-classroom/class25/evaluate.py

### content
import ipaddress
import json
from pathlib import Path

root = Path("/opt/lab-classroom/class25")
policy = json.loads((root / "policy.json").read_text())
packets = [
    {"name": "established-reply", "direction": "ingress", "protocol": "tcp", "source": "192.0.2.10", "destination_port": 49152, "state": "established"},
    {"name": "local-web", "direction": "ingress", "protocol": "tcp", "source": "127.0.0.1", "destination_port": 18080, "state": "new"},
    {"name": "remote-web", "direction": "ingress", "protocol": "tcp", "source": "192.0.2.10", "destination_port": 18080, "state": "new"},
    {"name": "local-dns", "direction": "ingress", "protocol": "udp", "source": "127.0.0.1", "destination_port": 15353, "state": "new"},
    {"name": "outbound-query", "direction": "egress", "protocol": "udp", "source": "192.0.2.20", "destination_port": 53, "state": "new"}
]

def matches(rule, packet):
    if rule.get("direction") != packet["direction"]:
        return False
    if "protocol" in rule and rule["protocol"] != packet["protocol"]:
        return False
    if "destination_port" in rule and rule["destination_port"] != packet["destination_port"]:
        return False
    if "states" in rule and packet["state"] not in rule["states"]:
        return False
    if "source" in rule:
        address = ipaddress.ip_address(packet["source"])
        if address not in ipaddress.ip_network(rule["source"]):
            return False
    return True

for packet in packets:
    for rule in policy["rules"]:
        if matches(rule, packet):
            print(packet["name"], rule["action"], rule["name"])
            break
    else:
        action = policy["defaults"][packet["direction"]]
        print(packet["name"], action, "default-" + packet["direction"])


### procedure
Confirm that /opt/lab-classroom/class25/ already exists, is writable by the laboratory user, and is the current working directory.
Create listener.py, probe.py, policy.json, and evaluate.py at the exact listed paths using the supplied contents. Do not create laboratory files elsewhere.
Start the TCP listener with: python3 listener.py tcp 18080 > tcp.log 2>&1 & echo $! > tcp.pid
Wait until tcp.log contains a line beginning with READY. If it does not appear within five seconds, stop and troubleshoot rather than repeatedly starting listeners.
Run the TCP client with: python3 probe.py tcp 127.0.0.1 18080 hello-tcp
Confirm that the client prints ACK:hello-tcp and that the listener exits after serving the connection.
Start the UDP listener with: python3 listener.py udp 15353 > udp.log 2>&1 & echo $! > udp.pid
Wait until udp.log contains a line beginning with READY.
Run the UDP client with: python3 probe.py udp 127.0.0.1 15353 hello-udp
Confirm that the client prints ACK:hello-udp and that the listener exits after processing the datagram.
Run the simulated policy evaluation with: python3 evaluate.py | tee evaluation.log
Compare each decision with the ordered policy. Explain why remote-web reaches the ingress default while local-web matches an explicit rule.
Edit only /opt/lab-classroom/class25/policy.json and temporarily change the allow-local-web destination_port from 18080 to 18081.
Run python3 evaluate.py again and observe that local-web is now dropped by the default ingress policy.
Restore destination_port to 18080 and rerun the evaluator to confirm the original result.

## Expected results

- The TCP listener reports that it is ready on 127.0.0.1:18080, and the TCP client prints ACK:hello-tcp.
- The UDP listener reports that it is ready on 127.0.0.1:15353, and the UDP client prints ACK:hello-udp.
- The listener logs show loopback peers and the application messages sent by the clients.
- The evaluator prints: established-reply ACCEPT allow-established.
- The evaluator prints: local-web ACCEPT allow-local-web.
- The evaluator prints: remote-web DROP default-ingress.
- The evaluator prints: local-dns ACCEPT allow-local-dns.
- The evaluator prints: outbound-query ACCEPT default-egress.
- Changing the simulated TCP rule to port 18081 causes local-web to receive DROP from the ingress default.
- No real host firewall policy is changed during the lab.

## Verification

- [ ] Run: python3 -m py_compile /opt/lab-classroom/class25/listener.py /opt/lab-classroom/class25/probe.py /opt/lab-classroom/class25/evaluate.py
- [ ] Run: python3 -m json.tool /opt/lab-classroom/class25/policy.json
- [ ] Run: grep '^READY tcp 127.0.0.1:18080' /opt/lab-classroom/class25/tcp.log
- [ ] Run: grep '^READY udp 127.0.0.1:15353' /opt/lab-classroom/class25/udp.log
- [ ] Run: grep '^local-web ACCEPT allow-local-web$' /opt/lab-classroom/class25/evaluation.log
- [ ] Run: grep '^remote-web DROP default-ingress$' /opt/lab-classroom/class25/evaluation.log
- [ ] Confirm that every newly created lesson artifact resolves beneath /opt/lab-classroom/class25/.
- [ ] Confirm that no listener process remains after each successful one-message exchange.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The listener exits with an address already in use error. | Another process is already bound to the selected address, protocol, and port, or a previous laboratory listener is still active. | Confirm whether the PID recorded in the corresponding PID file still belongs to this laboratory listener. Stop only that verified process. If the port belongs to another application, choose a different unprivileged port and update the listener command, client command, policy, and expected packet consistently. |
| The client reports connection refused for TCP. | The TCP listener is not running, failed to bind, exited before the test, or was started with a different port. | Read tcp.log, verify the READY line, and confirm that both programs use TCP, 127.0.0.1, and the same destination port. |
| The UDP client times out. | No matching UDP listener received the datagram, the listener used a different port, or TCP was selected accidentally. | Read udp.log and verify that the listener uses UDP on 127.0.0.1:15353. Restart only the laboratory UDP listener and repeat one probe. |
| The evaluator raises a JSON parsing error. | policy.json contains a missing comma, extra comma, invalid quote, or other syntax error. | Run the JSON verification command, compare the reported line with the supplied policy, and restore valid JSON before rerunning the evaluator. |
| local-web is dropped unexpectedly. | The source network, protocol, port, state, or direction in policy.json no longer matches the synthetic packet. | Compare all five fields with the local-web packet. Restore ingress, tcp, 127.0.0.0/8, destination port 18080, and state new. |
| A verification command cannot find an expected log line. | The command was run from another directory, output was not redirected to the expected file, or the listener did not complete the exchange. | Use the absolute file paths, inspect the complete log, and repeat the relevant listener-client exchange from /opt/lab-classroom/class25/. |
| Creation of lesson files fails with permission denied. | The classroom directory was not provisioned for the laboratory user. | Stop the lab and ask the administrator or instructor to provision the required directory. Do not redirect the files into unrelated system directories. |

## Security

### principles
Bind test services to loopback unless remote reachability is explicitly required.
Treat protocol and port as a pair; allowing TCP does not automatically allow UDP on the same number.
Prefer narrow source networks and specific destination ports over broad allowances.
Use a default-deny ingress posture when operational requirements and recovery procedures support it.
Allow established return traffic deliberately when using a stateful policy.
Document the owner, reason, scope, and expiration of every exception.
Validate application binding and local operation separately from firewall policy.
Maintain an independent recovery path before changing a remote system's real network policy.

### lab_boundary
The laboratory simulates decisions and creates loopback sockets. It neither installs nor applies an operating-system firewall policy.

### exposure_note
Changing 127.0.0.1 to a wildcard or externally assigned address could expose the demonstration service to other systems and is outside the authorized lab.

### data_handling
Use only non-sensitive test strings. Listener logs contain peer addresses and payload text.

## Rollback

### goal
Stop any remaining classroom listener and remove only artifacts created under the class directory.

### steps
For each tcp.pid and udp.pid file that exists, read the PID and inspect that process before taking action.
Stop a process only if its command line clearly identifies /opt/lab-classroom/class25/listener.py. Do not act on a reused PID belonging to another program.
After confirming no classroom listener remains, run: find /opt/lab-classroom/class25/ -mindepth 1 -maxdepth 1 -type f -delete
Run: find /opt/lab-classroom/class25/ -mindepth 1 -maxdepth 1 -type d -empty -delete
Leave /opt/lab-classroom/class25/ itself in place because it is the provisioned classroom workspace.

### verification
List /opt/lab-classroom/class25/ and confirm that no lesson files remain. Confirm separately that no process command line references /opt/lab-classroom/class25/listener.py.

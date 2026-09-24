# Class 25: Ports, Protocols, and Host Firewalls

**Learning objective:** Distinguish an IP address, a transport protocol, and a port number; Explain the practical differences between TCP and UDP; Identify the difference between a listening service and a firewall allowance; Describe ingress, egress, loopback, connection state, and default policy; Predict whether a packet will be accepted or dropped by an ordered rule set; Test TCP and UDP listeners without exposing services to the local network; Design a least-privilege host firewall policy before applying it to a real host
**Bloom level:** Understand / Apply
**Track:** Networking and Security Fundamentals · **Difficulty:** beginner · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Teach learners how transport protocols, port numbers, listening sockets, network interfaces, connection state, and host firewall policy work together. The lab uses loopback traffic and a policy simulator so learners can observe these concepts without changing the computer's real firewall configuration.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-24
**Compatibility:** ### operating_systems
Linux distributions capable of running Python 3.9 or newer

### python
Python 3.9 or newer using only the standard library

### network
IPv4 loopback support is required; no external network access is required for the lab

### privileges
The lab should run as a non-root user with write access to the pre-provisioned classroom directory

### ports
TCP 18080 on 127.0.0.1
UDP 15353 on 127.0.0.1

### limitations
The JSON evaluator models only selected packet attributes and first-match behavior. It is not a substitute for testing the semantics of the host's actual packet-filtering implementation.

## Learning objective

- Distinguish an IP address, a transport protocol, and a port number
- Explain the practical differences between TCP and UDP
- Identify the difference between a listening service and a firewall allowance
- Describe ingress, egress, loopback, connection state, and default policy
- Predict whether a packet will be accepted or dropped by an ordered rule set
- Test TCP and UDP listeners without exposing services to the local network
- Design a least-privilege host firewall policy before applying it to a real host

## Why this matters

Teach learners how transport protocols, port numbers, listening sockets, network interfaces, connection state, and host firewall policy work together. The lab uses loopback traffic and a policy simulator so learners can observe these concepts without changing the computer's real firewall configuration.

## Prerequisites

- Basic command-line navigation and process management
- A Linux host or virtual machine with Python 3.9 or newer
- A writable directory already provisioned at /opt/lab-classroom/class25/
- Permission to bind unprivileged TCP and UDP ports on the loopback interface
- Basic familiarity with IPv4 addresses and client-server communication

## Required reading

- Review the TCP/IP model, especially the network and transport layers.
- Read the Python socket module overview: https://docs.python.org/3/library/socket.html
- Read the IANA service name and port number registry overview: https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
- Review IPv4 loopback addressing and the special role of 127.0.0.0/8.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| port | A 16-bit transport-layer number used to identify an application endpoint. TCP and UDP each have their own port-number space. |
| socket | An operating-system communication endpoint commonly identified by an address, transport protocol, and port. |
| listening socket | A socket waiting for inbound traffic. A listener must exist before a TCP connection can be accepted or a UDP datagram can be received. |
| TCP | A connection-oriented transport protocol that provides ordered delivery, retransmission, flow control, and connection state. |
| UDP | A datagram-oriented transport protocol that does not establish a connection or guarantee delivery, ordering, or retransmission. |
| ingress | Traffic entering a host through a network path from the perspective of that host. |
| egress | Traffic leaving a host through a network path from the perspective of that host. |
| loopback | A local-only network path used for communication within the same host. IPv4 loopback commonly uses addresses in 127.0.0.0/8. |
| stateful firewall | A firewall that tracks connection state and can treat packets belonging to established traffic differently from unrelated new traffic. |
| default policy | The action taken when no explicit rule matches, commonly default deny for inbound traffic and a deliberately selected policy for outbound traffic. |
| least privilege | Allowing only the protocols, ports, sources, destinations, and directions required for a defined service. |
| attack surface | The set of reachable services and interfaces that could be probed, misconfigured, or exploited. |

## Instruction

A network service is not identified by a port number alone. A complete endpoint includes an address, a transport protocol, and a port. TCP port 443 and UDP port 443 are separate endpoints because TCP and UDP maintain separate port spaces. The address also matters: a process bound to 127.0.0.1 is reachable only through the local loopback path, while a process bound to an address assigned to a physical or virtual network interface may be reachable from other systems. A wildcard bind can cover multiple local interfaces and therefore creates a larger exposure than a loopback-only bind.

TCP is connection-oriented. Before application data is exchanged, endpoints establish a connection, and the operating system tracks its state. TCP provides ordered delivery and retransmits missing data, but those features do not make the application secure; confidentiality and authentication require higher-layer protections. UDP sends independent datagrams without a connection handshake. It has lower protocol overhead but does not guarantee that a datagram arrives, arrives once, or arrives in order. A stateful host firewall may still track a temporary flow for UDP even though UDP itself has no connection state.

A host firewall evaluates traffic at the individual machine. Its policy can consider direction, interface, source and destination addresses, protocol, ports, and observed connection state. Rules are commonly processed according to an implementation-defined order, so policy authors must understand precedence rather than merely collecting allow and deny statements. A useful baseline is to permit established return traffic, narrowly allow required new inbound services, and use an intentional default action for everything else. Outbound filtering may also be appropriate for servers, appliances, and tightly controlled environments.

A firewall allowance does not create a service. If TCP port 18080 is allowed but no process is listening, a client still cannot use the service. Conversely, a listening service is not proof that remote clients can reach it: the service may be bound only to loopback, blocked by a host policy, blocked elsewhere in the path, or hidden behind routing and address-translation boundaries. Troubleshooting should therefore separate four questions: is the application running, where is it bound, does local communication work, and does policy permit the intended path?

Rules should describe a service requirement rather than a vague desire to make an application work. For example, allowing new TCP traffic to one administration port from a dedicated management subnet is narrower than allowing every protocol and port from every address. Record the reason, owner, source scope, destination port, and expected lifetime of an exception. Test administrative access before and after any real firewall change, preferably with an independent recovery path. This class does not alter the real host firewall. Instead, it creates loopback listeners and evaluates sample packet descriptions against a deterministic policy model stored entirely under the classroom directory.

## Architecture

### scope
One Linux host using only loopback network traffic and files under /opt/lab-classroom/class25/.

### components
A TCP or UDP client implemented with the Python standard library
A loopback-only TCP or UDP listener implemented with the Python standard library
A JSON policy containing ordered rules and direction-specific defaults
A policy evaluator that compares synthetic packet descriptions with the ordered rules

### traffic_flow
The listener binds specifically to 127.0.0.1 and an unprivileged port.
The client sends a message to the matching protocol and port.
The listener returns an acknowledgment and exits after one exchange.
Separately, the evaluator reads synthetic packet metadata rather than intercepting real traffic.
The evaluator selects the first matching rule or the default for the packet direction.

### trust_boundaries
Loopback traffic remains on the local host.
A service bound to an external interface would cross into a less-trusted network boundary.
The policy simulator is educational and does not enforce operating-system traffic.

### policy_model
Established inbound traffic is accepted first. New loopback TCP traffic to port 18080 and new loopback UDP traffic to port 15353 are accepted. Other ingress traffic is dropped by default, while egress traffic is accepted by default.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### constraints
All homework files must remain under /opt/lab-classroom/class25/, and no real firewall configuration may be changed.

### tasks
Create /opt/lab-classroom/class25/policy-homework.json as a copy of the original simulated policy.
Add a synthetic inbound TCP service on port 18443 that accepts new traffic only from 192.0.2.0/24.
Add three packet cases to a copy of the evaluator: one permitted source, one source outside the subnet, and one UDP packet using the same port number.
Before running the evaluator, write down the expected decision and matching rule or default for each packet.
Explain in five sentences why the UDP packet should not match a TCP rule even though the destination port number is identical.
Write a short change plan describing validation, recovery access, testing, and rollback that would be required before implementing an equivalent policy on a real remote host.

## Feynman teach-back

### prompt
Explain the lesson to someone who knows that websites use networks but has never administered a server.

### model_explanation
An IP address identifies where a machine or interface can be reached, while a port helps deliver traffic to the correct program on that machine. TCP and UDP are different delivery systems, so the same port number can exist independently in both. A listening program is like someone waiting at a particular internal desk. A host firewall is a security checkpoint that decides which traffic may approach that desk. Opening the checkpoint does not place someone at the desk, and placing someone at the desk does not guarantee the checkpoint will admit visitors. Binding a service only to loopback is like making the desk reachable only from inside the building. A careful policy permits only the visitors, delivery method, and desk required for the service, then rejects unneeded traffic.

### self_check
Can you explain why TCP port 18080 and UDP port 18080 are not the same endpoint?
Can you explain why an allowed port can still appear unavailable?
Can you explain why a loopback-only bind reduces exposure?
Can you predict what happens when no firewall rule matches?

## Retrieval check

1. What three values are normally needed to distinguish a transport endpoint in this lesson?
2. Why are TCP port 53 and UDP port 53 considered separate endpoints?
3. Does allowing inbound traffic to a port automatically start a service on that port?
4. What is the security advantage of binding a test service to 127.0.0.1 instead of a wildcard address?
5. What does an ingress default of DROP mean when no explicit rule matches?
6. Why is an established-traffic rule useful in a stateful policy?
7. In the simulated policy, why is local-web accepted while remote-web is dropped?
8. What happens to the local-web packet when the rule's destination port is changed from 18080 to 18081?
9. Why should real remote firewall changes be made only with a tested recovery path?
10. Does successful local loopback communication prove that a service is remotely reachable?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

Begin by drawing a host with one loopback interface and one external interface. Label an application endpoint with three values: address, protocol, and port. Emphasize that TCP and UDP have independent port spaces. Demonstrate the TCP listener binding to 127.0.0.1:18080, then send one message and show the acknowledgment. Repeat with UDP on port 15353 and point out that UDP exchanges datagrams without a TCP-style connection. Next, open policy.json and read the rules from top to bottom. Explain that established traffic is accepted first, the two new loopback services are narrowly allowed, unmatched ingress is dropped, and unmatched egress is accepted. Run the evaluator and connect each output line to either a named rule or a direction-specific default. Change the TCP rule to port 18081 and show that the packet description has not changed, so it falls through to the ingress default. Restore the rule. Close by distinguishing service availability from firewall allowance and by explaining why real remote policy changes require narrow scope, testing, logging, rollback preparation, and independent recovery access.

## References

- IANA Service Name and Transport Protocol Port Number Registry: https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
- Python socket library documentation: https://docs.python.org/3/library/socket.html
- RFC 9293, Transmission Control Protocol: https://www.rfc-editor.org/rfc/rfc9293
- RFC 768, User Datagram Protocol: https://www.rfc-editor.org/rfc/rfc768
- RFC 1122, Requirements for Internet Hosts: https://www.rfc-editor.org/rfc/rfc1122
- RFC 6890, Special-Purpose IP Address Registries: https://www.rfc-editor.org/rfc/rfc6890
- NIST SP 800-41 Revision 1, Guidelines on Firewalls and Firewall Policy: https://csrc.nist.gov/pubs/sp/800/41/r1/final

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

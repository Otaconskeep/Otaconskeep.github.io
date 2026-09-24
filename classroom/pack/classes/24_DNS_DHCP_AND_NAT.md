# Class 24: DNS, DHCP, and NAT

**Learning objective:** Describe the separate responsibilities of DNS, DHCP, and NAT; Explain the DHCP discover, offer, request, and acknowledgment sequence; Distinguish recursive DNS resolution, authoritative answers, caching, and TTL behavior; Explain why transport ports are often part of a NAT translation entry; Identify common DNS, DHCP, and NAT failure domains; Verify simulated records, leases, and translation mappings; Explain why NAT is not a substitute for an explicit network security policy
**Bloom level:** Understand / Apply
**Track:** Homelab Networking · **Difficulty:** intermediate · **Duration:** ~120 minutes · **Lab risk:** low
**Build output:** Explain how DNS, DHCP, and NAT cooperate in a typical homelab, then reinforce the concepts with a deterministic simulator that creates DNS records, allocates DHCP leases, and builds NAT translation entries without modifying the host network.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux distributions capable of providing Python 3

### runtime
Python 3.8 or newer

### privileges
The user must be able to create and remove /opt/lab-classroom/class24/.

### network_impact
None; the exercise does not alter interfaces, routes, resolver settings, packet policy, or active DHCP services.

### architecture_support
x86_64
aarch64

### external_connectivity
Not required

## Learning objective

- Describe the separate responsibilities of DNS, DHCP, and NAT
- Explain the DHCP discover, offer, request, and acknowledgment sequence
- Distinguish recursive DNS resolution, authoritative answers, caching, and TTL behavior
- Explain why transport ports are often part of a NAT translation entry
- Identify common DNS, DHCP, and NAT failure domains
- Verify simulated records, leases, and translation mappings
- Explain why NAT is not a substitute for an explicit network security policy

## Why this matters

Explain how DNS, DHCP, and NAT cooperate in a typical homelab, then reinforce the concepts with a deterministic simulator that creates DNS records, allocates DHCP leases, and builds NAT translation entries without modifying the host network.

## Prerequisites

- Basic familiarity with IPv4 addresses, subnet masks, default gateways, and private address space
- Ability to run shell commands and Python 3
- Permission to create and remove files under /opt/lab-classroom/class24/
- Completion of introductory LAN, routing, and transport-protocol lessons

## Required reading

- Review IPv4 subnetting, including network, broadcast, usable host, and default gateway addresses.
- Review the roles of UDP and TCP ports in identifying application conversations.
- Review RFC 1918 private IPv4 address ranges.
- Read the overview sections of RFC 1034 and RFC 1035 for DNS concepts.
- Read the DHCP message-flow overview in RFC 2131.
- Read the traditional NAT terminology in RFC 3022.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| DNS | The Domain Name System, a distributed naming system that maps names to records such as IPv4 addresses, IPv6 addresses, mail exchangers, aliases, and service metadata. |
| Recursive resolver | A DNS service that performs or coordinates lookups on behalf of clients and normally caches the resulting answers. |
| Authoritative server | A DNS server that publishes definitive records for a DNS zone rather than merely returning cached recursive results. |
| TTL | Time to live; the duration for which a DNS answer may normally remain cached before it should be refreshed. |
| DHCP | The Dynamic Host Configuration Protocol, which supplies clients with network parameters such as an address, subnet prefix, gateway, DNS servers, and lease duration. |
| Lease | A time-bounded assignment of an IP address and related configuration to a DHCP client. |
| Reservation | A DHCP policy that consistently associates a known client identifier with a designated address. |
| DORA | A common mnemonic for DHCP Discover, Offer, Request, and Acknowledgment. |
| NAT | Network Address Translation, which rewrites address information as traffic passes between address realms. |
| PAT | Port Address Translation, a many-to-one NAT technique that distinguishes concurrent flows by translated transport ports. |
| Translation table | State that associates an internal flow with its translated external address and port. |
| Hairpin NAT | A translation path that allows an internal client to reach an internally hosted service through an address normally presented as external. |
| Split-horizon DNS | A design in which different clients receive different DNS answers for the same name, often based on whether they are inside or outside a network. |

## Instruction

DNS, DHCP, and NAT solve different problems even though a small home router may present them as one feature set. DHCP gives a client the information needed to participate on an IP network. A new client initially lacks a usable address and commonly begins with a broadcast DHCP Discover. A server responds with an Offer, the client sends a Request identifying the selected offer, and the server completes the exchange with an Acknowledgment. The resulting lease can include an address, prefix, default gateway, DNS server addresses, lease duration, and other options. A reservation is not the same thing as manually configuring an address: it remains server-managed but consistently maps a known client identifier to an intended address.

DNS answers naming questions. A client usually asks a recursive resolver for a record such as the A record for an IPv4 address or the AAAA record for an IPv6 address. If the answer is not cached, the resolver follows referrals through the DNS hierarchy until it reaches an authoritative source or another valid conclusion. Caching reduces delay and query volume, but it also means record changes are not instant. TTL values influence how long compliant caches may reuse an answer. A failed name lookup does not automatically mean that routing is broken; testing connectivity by address and then testing name resolution helps separate the two failure domains. Likewise, receiving a DNS server through DHCP does not prove that the DNS server is reachable or that it has the required records.

NAT rewrites packet addressing at a boundary. In a common IPv4 homelab, many private clients share one upstream address. Port Address Translation tracks combinations of protocol, source address, source port, destination address, and destination port, then assigns translated source ports so return traffic can be associated with the correct internal conversation. This state is normally created by outbound traffic and expires when it becomes idle or the protocol state ends. Inbound publishing requires an intentional static mapping or equivalent policy because an unsolicited packet has no existing translation entry that identifies an internal destination.

The normal dependency chain is: DHCP supplies an address, route, and resolver; DNS converts a service name into an address; routing sends packets toward the destination; and NAT may rewrite the flow at an address boundary. These services can also be deployed independently. Static clients do not require DHCP, direct address access does not require DNS, and globally routed networks may not require NAT. Troubleshooting should therefore test each layer independently rather than treating internet access as a single feature. Confirm the client configuration, test the local gateway, query the intended resolver, inspect the returned record, verify the route, and then inspect translation state where NAT is actually present. Finally, NAT must not be treated as a complete security control. Address rewriting can incidentally prevent some unsolicited traffic when no mapping exists, but access policy, service authentication, patching, segmentation, and logging remain separate responsibilities.

## Architecture

### logical_flow
Client requests network configuration from the DHCP service.
DHCP supplies an address from 192.168.24.100 through 192.168.24.105, a /24 prefix, gateway 192.168.24.1, and DNS server 192.168.24.2.
Client asks the DNS service to resolve names in the lab.home.arpa zone.
The simulated gateway creates a source translation entry when a client initiates an external flow.
Return traffic is associated with the originating client by the translation tuple.

### components
### client_segment
192.168.24.0/24

### gateway
192.168.24.1

### dns_service
192.168.24.2

### dhcp_pool
192.168.24.100-192.168.24.105

### simulated_external_address
198.51.100.24

### lab_storage
/opt/lab-classroom/class24/

### scope_note
All services in this lab are modeled in files and Python data structures. The host network configuration is not changed, no packets are transmitted, and every persistent mutation remains under /opt/lab-classroom/class24/.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### tasks
Extend the simulator with client-c and predict its address before running it.
Add an AAAA record for nas.lab.home.arpa using a documentation IPv6 prefix and preserve the existing A record.
Add a DHCP reservation data structure mapping printer-1 to 192.168.24.50, which must remain outside the dynamic pool.
Add a third NAT flow that deliberately reuses an internal source port on a different internal address, then explain why the complete flow tuple still distinguishes it.
Write a short troubleshooting decision tree that starts with client configuration and ends with application availability.

### submission_path
/opt/lab-classroom/class24/homework.json

### acceptance_criteria
All homework artifacts remain under /opt/lab-classroom/class24/.
Dynamic leases remain unique.
The reserved printer address is not allocated from the dynamic pool.
DNS records explicitly identify their record type and TTL.
Every NAT entry has enough information to associate return traffic with an internal flow.
The troubleshooting decision tree distinguishes naming failures from routing and service failures.

## Feynman teach-back

### exercise
Explain the system to a learner who knows what an IP address is but has never administered a network.

### model_explanation
DHCP is like a reception desk that temporarily gives each visitor a room number, directions to the exit, and the number for an information desk. DNS is the information desk that turns a memorable name into the numeric location needed to reach a service. NAT is like a mailroom shared by many rooms: outgoing packages use one building address, but the mailroom records a separate reference number so replies return to the correct room. The three systems often cooperate, but none performs the complete job of the others.

### self_check_prompts
Can you explain why a client may have a valid DHCP lease but still fail to resolve names?
Can you explain why a correct DNS answer does not prove that the destination service is reachable?
Can you explain how two internal clients can share one external IPv4 address at the same time?
Can you explain why a returning DHCP client may receive the same address?
Can you explain why changing a DNS record may not affect every client immediately?

## Retrieval check

1. 1. What four messages are represented by the DHCP DORA mnemonic?
2. 2. Which DHCP-supplied setting tells a client where to send traffic for destinations outside its local subnet?
3. 3. What is the difference between a recursive DNS resolver and an authoritative DNS server?
4. 4. Why can an old DNS answer remain visible after an authoritative record has changed?
5. 5. Why does PAT usually track transport ports in addition to IP addresses?
6. 6. Does a successful DNS lookup prove that the named application is reachable? Explain.
7. 7. Why should NAT not be described as a complete security policy?
8. 8. What is the practical difference between a DHCP reservation and manually assigning a static address on a client?
9. 9. What problem can occur when two interconnected sites use the same private IPv4 subnet?
10. 10. In the lab, why does the second request from client-a return 192.168.24.100 instead of consuming the next pool address?

## Guided lab

### name
Model DNS records, DHCP leases, and NAT state

### constraints
Run the commands exactly as shown.
Do not redirect output to a path outside /opt/lab-classroom/class24/.
The exercise is a deterministic simulator, not a production service deployment.
The documentation-only addresses 198.51.100.0/24 and 203.0.113.0/24 are used to avoid implying that arbitrary public systems should be contacted.

### steps
### step
1

### instruction
Create the isolated classroom directory.

### command
mkdir -p /opt/lab-classroom/class24/
### step
2

### instruction
Create a Python simulator for DNS lookup, DHCP allocation, and port-based source translation.

### command
python3 -c 'from pathlib import Path; p=Path("/opt/lab-classroom/class24/simulator.py"); p.write_text("""import ipaddress\nimport json\nfrom pathlib import Path\n\nBASE = Path(\"/opt/lab-classroom/class24\")\nNETWORK = ipaddress.ip_network(\"192.168.24.0/24\")\nPOOL = [str(ip) for ip in list(NETWORK.hosts()) if 100 <= int(str(ip).split(\".\")[-1]) <= 105]\nDNS_RECORDS = {\n    \"nas.lab.home.arpa\": {\"type\": \"A\", \"value\": \"192.168.24.10\", \"ttl\": 300},\n    \"dashboard.lab.home.arpa\": {\"type\": \"A\", \"value\": \"192.168.24.20\", \"ttl\": 300}\n}\nCLIENTS = [\"client-a\", \"client-b\", \"client-a\"]\n\ndef allocate_leases(clients):\n    leases = {}\n    available = iter(POOL)\n    events = []\n    for client in clients:\n        if client not in leases:\n            leases[client] = next(available)\n            events.append({\"client\": client, \"event\": \"new-lease\", \"address\": leases[client]})\n        else:\n            events.append({\"client\": client, \"event\": \"existing-lease\", \"address\": leases[client]})\n    return leases, events\n\ndef build_nat_table():\n    flows = [\n        {\"protocol\": \"tcp\", \"inside_ip\": \"192.168.24.100\", \"inside_port\": 51000, \"destination_ip\": \"203.0.113.10\", \"destination_port\": 443},\n        {\"protocol\": \"udp\", \"inside_ip\": \"192.168.24.101\", \"inside_port\": 53000, \"destination_ip\": \"203.0.113.53\", \"destination_port\": 53}\n    ]\n    for offset, flow in enumerate(flows):\n        flow[\"outside_ip\"] = \"198.51.100.24\"\n        flow[\"outside_port\"] = 40000 + offset\n    return flows\n\nleases, lease_events = allocate_leases(CLIENTS)\nresult = {\n    \"network\": str(NETWORK),\n    \"gateway\": \"192.168.24.1\",\n    \"dns_server\": \"192.168.24.2\",\n    \"dns_query\": {\"name\": \"nas.lab.home.arpa\", \"answer\": DNS_RECORDS[\"nas.lab.home.arpa\"]},\n    \"leases\": leases,\n    \"lease_events\": lease_events,\n    \"nat_table\": build_nat_table()\n}\n(BASE / \"results.json\").write_text(json.dumps(result, indent=2) + \"\\n\", encoding=\"utf-8\")\nprint(json.dumps(result, indent=2))\n""", encoding="utf-8")'
### step
3

### instruction
Run the simulator. Its only generated state is results.json inside the classroom directory.

### command
python3 /opt/lab-classroom/class24/simulator.py
### step
4

### instruction
Perform deterministic assertions against the generated state.

### command
python3 -c 'import json, pathlib; d=json.loads(pathlib.Path("/opt/lab-classroom/class24/results.json").read_text()); assert d["dns_query"]["answer"]["value"] == "192.168.24.10"; assert d["leases"]["client-a"] == "192.168.24.100"; assert d["leases"]["client-b"] == "192.168.24.101"; assert d["lease_events"][2]["event"] == "existing-lease"; assert len({x["outside_port"] for x in d["nat_table"]}) == 2; print("class24 verification passed")'
### step
5

### instruction
Inspect the saved result and identify which fields belong to DNS, DHCP, and NAT.

### command
python3 -m json.tool /opt/lab-classroom/class24/results.json

## Expected results

- The simulator reports the client network as 192.168.24.0/24.
- The DNS query for nas.lab.home.arpa returns an A record containing 192.168.24.10 with a TTL of 300.
- client-a receives 192.168.24.100 and client-b receives 192.168.24.101.
- The second request from client-a is labeled existing-lease and retains 192.168.24.100.
- Two NAT entries share the simulated external address 198.51.100.24 but use different translated ports.
- The assertion command prints class24 verification passed.
- The only created files are simulator.py and results.json under /opt/lab-classroom/class24/.

## Verification checkpoints

- [ ] Run `python3 /opt/lab-classroom/class24/simulator.py` again and confirm that the output is unchanged, demonstrating deterministic allocation.
- [ ] Run `python3 -m json.tool /opt/lab-classroom/class24/results.json` and confirm that the file contains dns_query, leases, lease_events, and nat_table sections.
- [ ] Run `python3 -c 'import json, pathlib; d=json.loads(pathlib.Path("/opt/lab-classroom/class24/results.json").read_text()); print(d["dns_query"]["answer"])'` and confirm that the value is 192.168.24.10.
- [ ] Run `python3 -c 'import json, pathlib; d=json.loads(pathlib.Path("/opt/lab-classroom/class24/results.json").read_text()); print(d["leases"])'` and confirm that the two distinct clients have distinct addresses.
- [ ] Run `python3 -c 'import json, pathlib; d=json.loads(pathlib.Path("/opt/lab-classroom/class24/results.json").read_text()); print([(x["inside_ip"], x["inside_port"], x["outside_ip"], x["outside_port"]) for x in d["nat_table"]])'` and confirm that each internal flow has a unique external port.
- [ ] Run `python3 -c 'from pathlib import Path; print(sorted(p.name for p in Path("/opt/lab-classroom/class24").iterdir()))'` and confirm that the lab directory contains simulator.py and results.json.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The command reports that /opt/lab-classroom/class24/ cannot be created. | The current account does not have permission to create directories under /opt. | Use an account with permission to create the required classroom directory, or have an administrator pre-create /opt/lab-classroom/class24/ and assign it to the lab user. Do not move the exercise to another path because the lesson scope requires this directory. |
| Running the simulator reports that python3 is not found. | Python 3 is not installed or is not available through the current command search path. | Install a supported Python 3 release using the operating system's normal package-management process outside this lab, then rerun the simulator. |
| The verification reports a JSON decoding error. | results.json is incomplete, was manually edited, or the simulator did not finish writing it. | Rerun `python3 /opt/lab-classroom/class24/simulator.py` to regenerate the result, then repeat the verification. |
| A client receives an unexpected simulated address. | The pool, client order, or allocation logic in simulator.py was changed. | Restore the original pool range of 192.168.24.100 through 192.168.24.105 and the client order client-a, client-b, client-a, then rerun the simulator. |
| Two NAT entries show the same translated port. | The translated-port assignment was modified so the offset is no longer applied. | Restore the expression that assigns 40000 plus the flow offset, regenerate results.json, and rerun the assertions. |
| A real client has an address but cannot resolve names. | DHCP may have supplied an incorrect resolver address, the resolver may be unreachable, or the requested DNS record may not exist. | Inspect the client's assigned DNS server, test reachability to that address, query that resolver directly, and compare the response with the authoritative zone data. |
| A real client can resolve names but cannot reach the resolved service. | DNS is functioning, but routing, packet policy, NAT state, the destination service, or return routing may be failing. | Record the returned address, test the route and gateway separately, confirm the destination service is listening, and inspect translation state at the actual address boundary. |
| A published internal service works by internal address but not by its external name from the same LAN. | The design may require hairpin translation or an internal DNS answer that points directly to the internal address. | Choose and document either a supported hairpin design or split-horizon DNS. Verify that internal and external clients receive the intended path. |

## Security considerations

Treat DHCP as a trusted infrastructure service. An unauthorized DHCP server can supply a hostile gateway or resolver and redirect client traffic.
Use network segmentation and infrastructure access controls to limit which interfaces or segments may originate server-side DHCP responses.
Protect DNS administration because altered records can redirect users even when IP routing remains healthy.
Restrict recursive DNS service to intended clients to reduce abuse and unintended resource consumption.
Use DNSSEC validation where appropriate to authenticate signed DNS data, while recognizing that it does not encrypt ordinary DNS queries.
Do not treat NAT as a complete security boundary. Translation and access policy are different functions.
Publish only required services, authenticate them, maintain updates, and retain useful logs.
Avoid overlapping private subnets across interconnected homelabs or remote-access networks because overlap creates ambiguous routing and translation requirements.
Document static assignments, DHCP reservations, exclusions, DNS records, and published translations to prevent accidental collisions.
The lab uses documentation-only external address ranges and does not send network traffic.

## Rollback

### scope
Remove only the class directory created for this lesson.

### command
python3 -c 'from pathlib import Path; import shutil; p=Path("/opt/lab-classroom/class24"); shutil.rmtree(p) if p.exists() else None'

### verification
Run `python3 -c 'from pathlib import Path; print(not Path("/opt/lab-classroom/class24").exists())'` and confirm that it prints True.

### impact
The simulator, generated results, and any homework files saved under the class directory are deleted. No host network state requires restoration because the lab does not modify it.

## Video narration notes

Begin with a diagram containing a client, a DHCP service, a DNS resolver, a gateway, and an external destination. First, show a new client without an address. Animate Discover, Offer, Request, and Acknowledgment, emphasizing that the lease includes more than an IP address: it also includes the subnet, gateway, resolver, and lifetime. Next, have the client request nas.lab.home.arpa. Follow the question to the resolver, explain cached versus authoritative answers, and point to the TTL. Then show an outbound connection whose private source address and source port are translated to the gateway's external address and a unique translated port. Trace the reply back through the translation entry to the original client. Pause to state that DNS naming, DHCP configuration, routing, and NAT translation are separate checkpoints. Move to the lab and explain that it intentionally simulates behavior rather than changing the classroom host network. Run the simulator, inspect the DNS answer, compare the first and returning DHCP events, and inspect the two NAT entries. Finish by demonstrating the assertions and summarizing the troubleshooting order: inspect client configuration, test the local gateway, query the intended resolver, confirm the returned address, verify the route, inspect translation state, and finally verify the destination application.

## References

- RFC 1034, Domain Names, Concepts and Facilities: https://www.rfc-editor.org/rfc/rfc1034
- RFC 1035, Domain Names, Implementation and Specification: https://www.rfc-editor.org/rfc/rfc1035
- RFC 2131, Dynamic Host Configuration Protocol: https://www.rfc-editor.org/rfc/rfc2131
- RFC 2132, DHCP Options and BOOTP Vendor Extensions: https://www.rfc-editor.org/rfc/rfc2132
- RFC 3022, Traditional IP Network Address Translator: https://www.rfc-editor.org/rfc/rfc3022
- RFC 1918, Address Allocation for Private Internets: https://www.rfc-editor.org/rfc/rfc1918
- RFC 5737, IPv4 Address Blocks Reserved for Documentation: https://www.rfc-editor.org/rfc/rfc5737
- RFC 8375, Special-Use Domain home.arpa: https://www.rfc-editor.org/rfc/rfc8375
- IANA Domain Name System Parameters: https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
- IANA BOOTP and DHCP Parameters: https://www.iana.org/assignments/bootp-dhcp-parameters/bootp-dhcp-parameters.xhtml

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

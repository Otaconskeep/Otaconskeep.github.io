# Class 65: Local DNS and Friendly Service Names

**Learning objective:** Explain the roles of stub resolvers, recursive resolvers, authoritative data, and DNS caches.; Create local A records that map friendly service names to private IPv4 addresses.; Use home.arpa instead of invented top-level domains or the multicast-oriented local suffix.; Query a specific DNS server and nonstandard port with dig.; Interpret NOERROR, NXDOMAIN, answer sections, record types, and time-to-live values.; Describe the operational requirements for making local names available to an entire LAN.; Identify common causes of inconsistent local name resolution.
**Bloom level:** Understand / Apply
**Track:** Networking and Core Services · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach learners how local DNS converts memorable service names into IP addresses, why home.arpa is the appropriate namespace for residential networks, and how to test a private DNS namespace safely without changing the host resolver or exposing a DNS service to the LAN.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### platforms
Linux systems capable of running dnsmasq and dig
Virtual machines
Physical homelab hosts
Linux containers with loopback networking and permission to create the specified workspace

### requirements
dnsmasq with support for host-record, local, listen-address, bind-interfaces, and configuration testing
dig with support for selecting a DNS server and port
A POSIX-compatible shell
Permission to create /opt/lab-classroom/class65/
Available loopback port 1053

### notes
Command output formatting can vary across dnsmasq and dig releases.
The lab uses IPv4 loopback and synthetic private IPv4 answers; it does not require the target service addresses to exist.
Systems with mandatory access-control policies may deny dnsmasq access to an unconventional configuration or log path. Do not weaken host policy for this exercise.
The lab does not alter resolver configuration and therefore does not make the names available to ordinary applications.

## Learning objective

- Explain the roles of stub resolvers, recursive resolvers, authoritative data, and DNS caches.
- Create local A records that map friendly service names to private IPv4 addresses.
- Use home.arpa instead of invented top-level domains or the multicast-oriented local suffix.
- Query a specific DNS server and nonstandard port with dig.
- Interpret NOERROR, NXDOMAIN, answer sections, record types, and time-to-live values.
- Describe the operational requirements for making local names available to an entire LAN.
- Identify common causes of inconsistent local name resolution.

## Why this matters

Teach learners how local DNS converts memorable service names into IP addresses, why home.arpa is the appropriate namespace for residential networks, and how to test a private DNS namespace safely without changing the host resolver or exposing a DNS service to the LAN.

## Prerequisites

- Basic understanding of IPv4 addresses, ports, and client-server communication.
- A Linux shell with permission to create /opt/lab-classroom/class65/.
- The dnsmasq and dig commands already installed. The lab intentionally does not install packages or modify system package state.
- Port 1053 on the loopback address must be available.
- No production DNS settings are changed during this class.

## Required reading

- RFC 1034, Domain Names—Concepts and Facilities: https://www.rfc-editor.org/rfc/rfc1034
- RFC 1035, Domain Names—Implementation and Specification: https://www.rfc-editor.org/rfc/rfc1035
- RFC 8375, Special-Use Domain home.arpa: https://www.rfc-editor.org/rfc/rfc8375
- dnsmasq manual page: https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html
- BIND 9 dig manual: https://bind9.readthedocs.io/en/latest/manpages.html#dig-dns-lookup-utility

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| DNS | The Domain Name System, a distributed naming system that maps names to records such as IPv4 and IPv6 addresses. |
| Stub resolver | The client-side component that sends DNS questions to a configured resolver on behalf of applications. |
| Recursive resolver | A DNS service that obtains answers for clients, commonly by consulting other DNS servers and caching the results. |
| Authoritative data | DNS data served from the source responsible for a namespace rather than learned from another resolver. |
| A record | A DNS resource record that maps a name to an IPv4 address. |
| AAAA record | A DNS resource record that maps a name to an IPv6 address. |
| CNAME record | A record that aliases one DNS name to another DNS name. |
| PTR record | A record generally used for reverse lookup from an address-oriented DNS name to a host name. |
| FQDN | A fully qualified domain name that identifies a name within the complete DNS hierarchy, such as dashboard.home.arpa. |
| TTL | Time to live, the number of seconds for which a DNS response may normally be cached. |
| NXDOMAIN | A DNS response code indicating that the requested domain name does not exist. |
| Split DNS | A design in which the answer for a name depends on which resolver or network view receives the query. |
| home.arpa | The special-use domain reserved by RFC 8375 for names within residential home networks. |

## Instruction

People remember names more reliably than addresses. A bookmark such as https://dashboard.home.arpa is easier to recognize and maintain than https://10.20.30.40. DNS supplies the translation, but it does not create application connectivity, configure a reverse proxy, or guarantee that a service is healthy. It only returns records in response to questions. A typical application asks the operating system's stub resolver for an address. The stub resolver sends the question to a configured recursive resolver, which may answer from cache, consult authoritative servers, or return an error. In a homelab, one resolver can also hold private records for internal services.

Local naming should use a deliberate namespace. RFC 8375 reserves home.arpa for residential home networks. The local suffix should generally be avoided for ordinary unicast DNS because it is conventionally associated with multicast DNS and may be handled differently by operating systems. Public domains that you do not control are also poor choices because future public records can conflict with private assumptions. Organizations that own a public domain may instead delegate or privately serve a subdomain, but that requires disciplined administration.

An A record maps a name to an IPv4 address, while an AAAA record maps a name to an IPv6 address. A CNAME points one name at another name and is useful for aliases, although clients must still resolve the target. DNS record design should represent stable service identities. For example, dashboard.home.arpa can remain constant while its address changes. Update the central record rather than editing bookmarks and application configurations across many clients.

Caching improves speed and reduces repeated work, but it also explains why DNS changes do not always appear immediately. A cached answer can remain in use until its TTL expires. Multiple clients can see different answers when they use different resolvers, retain different cache entries, or bypass the intended LAN resolver. Troubleshooting should therefore identify the exact resolver being queried, test the full name, inspect the response code, and compare direct queries with application behavior.

This lab runs dnsmasq only on 127.0.0.1:1053 and supplies an explicit configuration file. Port 1053 avoids the privileged standard DNS port and prevents the exercise from replacing the machine's configured resolver. The no-resolv and no-hosts settings make the source of the lab answers clear: only records written into the lab configuration are available. The local directive declares home.arpa as locally answered, so a missing name under that suffix should produce NXDOMAIN instead of being forwarded elsewhere. Because clients are not reconfigured, every test explicitly selects the server and port with dig.

A production design normally places a redundant or highly available resolver at stable LAN addresses, distributes those addresses to clients through network configuration, restricts who may query or administer the service, maintains both IPv4 and IPv6 records where appropriate, and monitors response health. Friendly names also belong in service documentation and certificates. If an HTTPS certificate does not contain the friendly name, DNS may resolve correctly while the browser still reports an identity error. Treat DNS as one layer in the service path, not as a substitute for routing, transport security, access control, or application monitoring.

## Architecture

### components
A client shell running dig.
A dnsmasq process bound only to 127.0.0.1 on UDP and TCP port 1053.
A lab-owned configuration file containing records for dashboard.home.arpa and nas.home.arpa.
A query log and process identifier stored beneath /opt/lab-classroom/class65/.

### query_flow
dig sends a DNS question directly to 127.0.0.1 port 1053.
dnsmasq checks the records defined in the lab configuration.
A known name receives an A-record answer.
An unknown name under home.arpa receives an NXDOMAIN response.
No upstream DNS server is consulted because the lab disables resolver-file processing and treats home.arpa as local.

### scope
The exercise is loopback-only. It does not modify the operating system resolver configuration, advertise DNS to other clients, or listen on a LAN interface.

### diagram
dig client -> 127.0.0.1:1053 -> dnsmasq -> local host-record data -> DNS response

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Design a naming plan for at least five homelab services using home.arpa. Include the service purpose, chosen name, address family, owner, and expected change frequency.
Draw the query path from an application to a stub resolver, then to a recursive resolver, cache, and authoritative source.
Explain how you would provide two resilient DNS resolver addresses to LAN clients without creating a circular dependency.
Research the difference between A, AAAA, CNAME, and PTR records and provide one appropriate homelab use case for each.
Write a change procedure for moving dashboard.home.arpa to a new address while minimizing the impact of cached answers.
Document how you would determine whether a client is bypassing the intended local resolver.

## Feynman teach-back

### prompt
Explain local DNS to someone who knows that computers have IP addresses but has never administered a network.

### model_explanation
A local DNS server is like a private address book. Instead of remembering that a dashboard lives at 10.20.30.40, a user asks for dashboard.home.arpa. The computer sends that question to a DNS resolver, and the resolver replies with the address stored for that name. The name can stay the same even if the service later moves to another address. Cached copies make repeated lookups faster, but they can temporarily preserve an old answer after a change. DNS only tells the client where to try connecting; it does not prove that the service is running or trusted.

### self_check
Can you distinguish a DNS answer from proof that an application is healthy?
Can you explain why two clients might temporarily receive different answers?
Can you explain why home.arpa is preferable to an invented suffix?
Can you describe why this lab uses 127.0.0.1:1053 instead of replacing the host resolver?

## Retrieval check

1. 1. Which special-use domain is recommended by RFC 8375 for residential home networks?
2. 2. What is the difference between an A record and an AAAA record?
3. 3. Why can a client continue using an old address after a DNS record has been changed?
4. 4. What does NXDOMAIN communicate to a DNS client?
5. 5. Why does the lab query 127.0.0.1 on port 1053 explicitly?
6. 6. Does successful DNS resolution prove that the target web application is running and trustworthy?
7. 7. Why should ordinary private unicast DNS names generally avoid the local suffix?
8. 8. What is a likely explanation when an A query succeeds but an AAAA query for the same name has no answer?

## Guided lab

### name
Build and query an isolated home.arpa namespace

### workspace
/opt/lab-classroom/class65/

### constraints
All files created or changed by the lab remain under /opt/lab-classroom/class65/.
The DNS listener is restricted to the loopback address.
The host resolver configuration is not changed.
The service uses nonstandard port 1053.
Do not continue if another process already owns 127.0.0.1:1053.

### steps
### step
1

### title
Confirm required commands

### commands
command -v dnsmasq
command -v dig

### explanation
Both commands must print an executable path. If either check fails, stop and arrange for the prerequisite to be provided outside this lab.
### step
2

### title
Create the isolated workspace

### commands
sudo install -d -m 0755 -o "$(id -un)" -g "$(id -gn)" /opt/lab-classroom/class65

### explanation
This creates only the approved class directory and assigns it to the current user so the service can write its local log and process identifier.
### step
3

### title
Check that the selected loopback port is unused

### commands
if command -v ss >/dev/null 2>&1; then ss -lntu | grep -E '127\.0\.0\.1:1053([[:space:]]|$)' || true; else echo "ss is unavailable; dnsmasq startup will perform the effective port check"; fi

### explanation
No matching listener should be displayed. If a listener is shown, do not start the lab service until the conflict has been investigated.
### step
4

### title
Write the local DNS configuration

### commands
printf '%s\n' 'port=1053' 'listen-address=127.0.0.1' 'bind-interfaces' 'no-resolv' 'no-hosts' 'domain-needed' 'bogus-priv' 'local=/home.arpa/' 'host-record=dashboard.home.arpa,10.20.30.40' 'host-record=nas.home.arpa,10.20.30.50' 'cache-size=100' 'log-queries' 'log-facility=/opt/lab-classroom/class65/dnsmasq.log' 'pid-file=/opt/lab-classroom/class65/dnsmasq.pid' > /opt/lab-classroom/class65/dnsmasq.conf
cat /opt/lab-classroom/class65/dnsmasq.conf

### explanation
The configuration provides two private A records, declares home.arpa local, disables inherited host and upstream resolver data, and keeps runtime files inside the workspace.
### step
5

### title
Validate the configuration before starting

### commands
dnsmasq --test --conf-file=/opt/lab-classroom/class65/dnsmasq.conf

### explanation
Proceed only when dnsmasq reports that the syntax check is successful.
### step
6

### title
Start the isolated DNS process

### commands
dnsmasq --no-daemon --conf-file=/opt/lab-classroom/class65/dnsmasq.conf >> /opt/lab-classroom/class65/service-output.log 2>&1 & printf '%s\n' "$!" > /opt/lab-classroom/class65/launcher.pid
sleep 1
test -s /opt/lab-classroom/class65/launcher.pid && kill -0 "$(cat /opt/lab-classroom/class65/launcher.pid)"
cat /opt/lab-classroom/class65/service-output.log

### explanation
The process runs in the background but remains bound to the loopback address and selected lab port. The process check succeeds silently when it is alive.
### step
7

### title
Resolve the dashboard name

### commands
dig @127.0.0.1 -p 1053 dashboard.home.arpa A +noall +answer

### explanation
The answer section should associate dashboard.home.arpa with 10.20.30.40.
### step
8

### title
Resolve the NAS name and inspect the full response

### commands
dig @127.0.0.1 -p 1053 nas.home.arpa A

### explanation
Inspect the header status, question section, answer section, responding server, and query time. The status should be NOERROR.
### step
9

### title
Test a missing local name

### commands
dig @127.0.0.1 -p 1053 missing.home.arpa A

### explanation
The response should report NXDOMAIN because the requested name is not among the local records.
### step
10

### title
Test a record-type mismatch

### commands
dig @127.0.0.1 -p 1053 dashboard.home.arpa AAAA

### explanation
The lab defines an A record but no AAAA record. A successful server response can therefore contain no IPv6 answer; reachability of the DNS server and existence of a requested record type are separate questions.
### step
11

### title
Review query evidence

### commands
cat /opt/lab-classroom/class65/dnsmasq.log

### explanation
The log should show the names and record types queried during the exercise.

## Expected results

- The dnsmasq configuration syntax check completes successfully.
- A dnsmasq process listens only on 127.0.0.1 port 1053 for the duration of the lab.
- A query for dashboard.home.arpa type A returns 10.20.30.40.
- A query for nas.home.arpa type A returns 10.20.30.50 with status NOERROR.
- A query for missing.home.arpa returns status NXDOMAIN.
- A query for dashboard.home.arpa type AAAA does not invent an IPv6 address.
- The dnsmasq query log records the lab questions.
- The operating system's normal DNS resolver remains unchanged.

## Verification checkpoints

- [ ] Run: dnsmasq --test --conf-file=/opt/lab-classroom/class65/dnsmasq.conf — the result must indicate valid syntax.
- [ ] Run: test -s /opt/lab-classroom/class65/launcher.pid && kill -0 "$(cat /opt/lab-classroom/class65/launcher.pid)" — a zero exit status confirms that the recorded process is alive.
- [ ] Run: dig @127.0.0.1 -p 1053 dashboard.home.arpa A +short — the output must include 10.20.30.40.
- [ ] Run: dig @127.0.0.1 -p 1053 nas.home.arpa A +short — the output must include 10.20.30.50.
- [ ] Run: dig @127.0.0.1 -p 1053 missing.home.arpa A +noall +comments — the header must contain status: NXDOMAIN.
- [ ] Run: dig @127.0.0.1 -p 1053 dashboard.home.arpa AAAA +noall +answer — no fabricated IPv6 address should appear.
- [ ] Run: grep -E 'dashboard\.home\.arpa|nas\.home\.arpa|missing\.home\.arpa' /opt/lab-classroom/class65/dnsmasq.log — the log must contain evidence of the test queries.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| dnsmasq is not found. | The prerequisite package is not installed or its executable directory is absent from PATH. | Stop the lab and arrange for dnsmasq to be installed through the normal host-management process. Do not improvise package or system changes inside this exercise. |
| dig is not found. | The system's DNS client utilities are not installed. | Stop the lab and obtain the appropriate DNS utility package through the normal host-management process before continuing. |
| The configuration test reports an error. | A directive was copied incorrectly or the installed dnsmasq release does not support the supplied syntax. | Compare /opt/lab-classroom/class65/dnsmasq.conf with the lesson, inspect the exact error line, and consult the manual for the installed release before changing anything. |
| dnsmasq reports that the address is already in use. | Another process is listening on 127.0.0.1:1053. | Do not stop an unidentified service. Inspect the existing listener, terminate only a previous instance of this class if ownership is confirmed, or select another unprivileged port consistently in both the configuration and every dig command. |
| dig times out. | The lab process exited, failed to bind, or is being queried on the wrong address or port. | Check service-output.log, confirm the recorded process with kill -0, and verify that the query explicitly uses @127.0.0.1 and -p 1053. |
| The expected A record is missing. | The queried spelling or record type does not match the configured host-record. | Use the complete name, verify that the query type is A, inspect the configuration, and rerun the syntax test before restarting the lab service. |
| A normal application cannot resolve dashboard.home.arpa even though the direct dig query works. | The lab intentionally does not configure the operating system to use 127.0.0.1:1053 as its resolver. | Use explicit dig queries for this exercise. Production resolver distribution is a separate administrative change and is intentionally outside the lab scope. |
| A changed record still appears to return an old address in another environment. | A resolver or application retained a cached answer until its TTL expired. | Query the intended resolver directly, inspect the remaining TTL, wait for expiration where practical, and confirm that all clients are using the expected resolver. |
| The query returns NOERROR but the answer section is empty. | The name can be recognized while the requested record type is not defined, such as requesting AAAA when only an A record exists. | Request the correct record type or deliberately define the missing record after confirming that the corresponding address is valid. |

## Security considerations

Bind experimental DNS services to 127.0.0.1 unless LAN access is an explicit design requirement.
Do not expose an unrestricted resolver to untrusted networks; open recursive resolvers can be abused and can contribute to amplification traffic.
Restrict configuration-file write access because anyone able to alter DNS records can redirect clients to unintended systems.
Use names from home.arpa for a residential private namespace, or use a properly controlled subdomain when operating a registered domain.
Avoid placing credentials, tokens, owner names, or other sensitive information in host names because DNS names commonly appear in logs.
DNS resolution does not authenticate an application. Use appropriate transport encryption and certificate validation for sensitive services.
Account for clients that use encrypted external resolvers or manually configured resolvers, because they may bypass local DNS policy.
Back up DNS configuration and document address ownership so stale records do not redirect users after an address is reassigned.
Where supported by the production design, operate more than one resolver so a single maintenance event does not remove naming from the entire LAN.

## Rollback

### goal
Stop only the process launched by this lab and remove only the class workspace.

### steps
Read the process identifier from /opt/lab-classroom/class65/launcher.pid.
Confirm that the identifier still belongs to a dnsmasq command using the class65 configuration.
Stop that verified process.
Delete the contents of /opt/lab-classroom/class65/ and then remove the empty class65 directory.

### commands
pid="$(cat /opt/lab-classroom/class65/launcher.pid 2>/dev/null || true)"; if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then args="$(ps -p "$pid" -o args=)"; case "$args" in *dnsmasq*'/opt/lab-classroom/class65/dnsmasq.conf'*) kill "$pid"; wait "$pid" 2>/dev/null || true ;; *) printf '%s\n' "Refusing to stop PID $pid because its command does not match this lab." >&2; exit 1 ;; esac; fi
find /opt/lab-classroom/class65 -mindepth 1 -maxdepth 1 -type f -delete
rmdir /opt/lab-classroom/class65

### validation
Confirm that /opt/lab-classroom/class65 no longer exists and that dig @127.0.0.1 -p 1053 dashboard.home.arpa A now times out or reports that no server is reachable on that port. The host's ordinary resolver settings should be exactly as they were before the lab.

## Video narration notes

Welcome to Class 65, Local DNS and Friendly Service Names. In this lesson, we replace difficult-to-remember private addresses with names such as dashboard.home.arpa. We begin by separating DNS from the applications it supports. DNS can tell a client that a name maps to an address, but it cannot guarantee that the service at that address is running, secure, or correctly configured.

The client normally uses a stub resolver, which forwards questions to a configured DNS resolver. That resolver may answer from its cache, consult another server, or use locally maintained data. The time-to-live attached to an answer controls how long it may normally remain cached. This is why a record change can be correct on the server while some clients continue to see an older address.

For a residential network, home.arpa is the standards-based private namespace. Avoid inventing a top-level suffix, and avoid using the local suffix for ordinary unicast DNS because many systems associate it with multicast DNS. A clear naming plan should identify services rather than temporary hardware details. A stable name such as nas.home.arpa can remain useful even when the underlying address changes.

Our lab is intentionally isolated. dnsmasq listens only on the loopback address and uses port 1053. We do not replace the operating system resolver, advertise the service to the LAN, or read the host's normal resolver and hosts data. Two host records are defined: dashboard.home.arpa maps to 10.20.30.40, and nas.home.arpa maps to 10.20.30.50.

After validating the configuration, we start the process and use dig to choose both the server and port explicitly. The dashboard and NAS A queries should return their configured IPv4 addresses. A query for missing.home.arpa should return NXDOMAIN. We also ask for an AAAA record that was never defined. That test demonstrates that a reachable DNS server can return no answer for a specific record type without inventing data.

Finally, we inspect the query log and perform a controlled rollback. In production, local DNS requires stable resolver addresses, configuration backups, access controls, monitoring, and a client-distribution plan. It may also need redundancy and deliberate IPv6 support. Remember the central lesson: DNS gives services durable, understandable identities, but it is only one layer of a reliable and secure homelab.

## References

- RFC 1034, Domain Names—Concepts and Facilities: https://www.rfc-editor.org/rfc/rfc1034
- RFC 1035, Domain Names—Implementation and Specification: https://www.rfc-editor.org/rfc/rfc1035
- RFC 2308, Negative Caching of DNS Queries: https://www.rfc-editor.org/rfc/rfc2308
- RFC 6762, Multicast DNS: https://www.rfc-editor.org/rfc/rfc6762
- RFC 8375, Special-Use Domain home.arpa: https://www.rfc-editor.org/rfc/rfc8375
- IANA Special-Use Domain Names registry: https://www.iana.org/assignments/special-use-domain-names/special-use-domain-names.xhtml
- dnsmasq documentation: https://thekelleys.org.uk/dnsmasq/doc.html
- BIND 9 dig documentation: https://bind9.readthedocs.io/en/latest/manpages.html#dig-dns-lookup-utility

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

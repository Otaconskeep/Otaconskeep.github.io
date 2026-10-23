# Lab: Local DNS and Friendly Service Names

**Module:** Edge Access & VPN
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain the roles of stub resolvers, recursive resolvers, authoritative data, and DNS caches.

## Before you start

- Basic understanding of IPv4 addresses, ports, and client-server communication.
- A Linux shell with permission to create /opt/lab-classroom/class65/.
- The dnsmasq and dig commands already installed. The lab intentionally does not install packages or modify system package state.
- Port 1053 on the loopback address must be available.
- No production DNS settings are changed during this class.

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

## Verification

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

## Security

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

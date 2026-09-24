# Homework: DNS, DHCP, and NAT

**Module:** Network Operations
**Activity type:** Homework / independent application
**Objective:** Describe the separate responsibilities of DNS, DHCP, and NAT

## Requirements

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

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

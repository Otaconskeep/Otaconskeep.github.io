# Homework — Ports, Protocols, and Host Firewalls

**Module:** Network Operations
**Activity type:** Homework / independent application
**Objective:** Distinguish an IP address, a transport protocol, and a port number

## Requirements

### constraints
All homework files must remain under /opt/lab-classroom/class25/, and no real firewall configuration may be changed.

### tasks
Create /opt/lab-classroom/class25/policy-homework.json as a copy of the original simulated policy.
Add a synthetic inbound TCP service on port 18443 that accepts new traffic only from 192.0.2.0/24.
Add three packet cases to a copy of the evaluator: one permitted source, one source outside the subnet, and one UDP packet using the same port number.
Before running the evaluator, write down the expected decision and matching rule or default for each packet.
Explain in five sentences why the UDP packet should not match a TCP rule even though the destination port number is identical.
Write a short change plan describing validation, recovery access, testing, and rollback that would be required before implementing an equivalent policy on a real remote host.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

# Reading: Firewall Segmentation and Trust Boundaries

**Module:** Segmentation, Backup & Power
**Activity type:** Reading (Learn)
**Objective:** Define zones as groups of systems with similar trust and policy requirements.

## Vocabulary

| Term | Meaning |
|---|---|
| zone | A named group of systems with similar trust, function, and traffic-policy requirements. |
| trust boundary | A point where traffic moves between security contexts and must be explicitly evaluated. |
| segmentation | Dividing a network into policy-controlled zones to limit reachability and reduce lateral movement. |
| least privilege | Granting only the network access required for a defined function and denying broader access. |
| first-match processing | Evaluating ordered rules from top to bottom and stopping at the first rule whose conditions match. |
| shadowed rule | A rule that cannot take effect because an earlier, broader rule matches the same traffic first. |
| default deny | A final policy position that rejects traffic unless an earlier explicit rule permits it. |
| RFC 1918 | The standard reserving 10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16 for private IPv4 networks. |
| RFC 5737 | The standard reserving 192.0.2.0/24, 198.51.100.0/24, and 203.0.113.0/24 for examples and documentation. |
| positive test | A test proving that specifically authorized traffic is allowed by the intended rule. |
| negative test | A test proving that unauthorized traffic remains denied. |

## Instruction

Segmentation is not merely the creation of subnets. A subnet becomes a meaningful security boundary only when traffic crossing that boundary is governed by an explicit, testable policy. A useful design starts with assets and required flows: who initiates a connection, where it goes, which protocol and port it uses, and why the connection exists. Systems with similar roles and trust assumptions are grouped into zones. In this lesson, administrators, users, servers, monitoring systems, and an external documentation network are separate zones. The monitoring zone is not merged with the administrator zone because collecting metrics does not justify interactive administrative access.

The policy follows least privilege. Administrator SSH and user HTTPS are separate grants because they serve different purposes. Monitoring receives only TCP 9100 and TCP 9115 access to servers. A final default-deny rule handles every flow that was not explicitly approved. Rule order is security-relevant: the simulator uses first-match processing, so a new allow placed after the catch-all deny is syntactically present but operationally useless. This is called shadowing. A change is not complete merely because a rule appears in a file; tests must prove both the decision and the exact matched rule name.

CIDRs are modeled as part of each zone rather than as decorative documentation. Every flow includes source and destination IP addresses, and the evaluator verifies that those addresses belong to the declared source and destination zone prefixes before applying policy. The internal zones use RFC 1918 private addresses. The external test zone uses 203.0.113.0/24, one of the RFC 5737 documentation prefixes. RFC 5737 space is safe for examples but is not private production address space and should not be treated as an Internet-routable target. The lab deliberately avoids changing packet filters, routes, interfaces, forwarding settings, or services on the host. All policy mutation occurs in JSON below the class workspace, allowing rule-order behavior, recovery, and auditing to be practiced without risking remote access.

## Architecture

### processing_model
### policy_engine
File-backed Python simulator

### rule_order
Top to bottom, first matching rule wins

### implicit_behavior
No implicit allow exists; the policy contains an explicit final default-deny rule

### address_validation
Before rule evaluation, each source and destination IP must belong to the CIDR declared by its stated zone

### scope
Zone labels and CIDRs are both enforced by the simulator; no host packet filter is changed

### zones
### admin
### cidr
10.71.10.0/24

### address_standard
RFC1918

### trust_role
Privileged administration clients

### boundary_notes
May initiate approved management connections but is not universally trusted.

### servers
### cidr
10.71.20.0/24

### address_standard
RFC1918

### trust_role
Application and infrastructure services

### boundary_notes
Accepts only explicitly required administration, application, and monitoring traffic.

### users
### cidr
10.71.30.0/24

### address_standard
RFC1918

### trust_role
General client systems

### boundary_notes
May consume published services but receives no administrative path.

### monitoring
### cidr
10.71.40.0/24

### address_standard
RFC1918

### trust_role
Metrics and availability collectors

### boundary_notes
Separated from administration and limited to TCP 9100 and TCP 9115 toward servers.

### external-test
### cidr
203.0.113.0/24

### address_standard
RFC5737

### trust_role
Documentation-only external traffic model

### boundary_notes
Represents an untrusted boundary in this simulation; the prefix is reserved for examples and is not presented as real Internet space.

### approved_flows
### source
admin

### destination
servers

### service
TCP 22

### purpose
Administrative SSH
### source
users

### destination
servers

### service
TCP 443

### purpose
Published HTTPS application
### source
servers

### destination
external-test

### service
TCP 443

### purpose
Simulated outbound HTTPS
### source
monitoring

### destination
servers

### service
TCP 9100

### purpose
Node metrics collection added during the change
### source
monitoring

### destination
servers

### service
TCP 9115

### purpose
Black-box metrics collection added during the change

### denied_examples
### source
users

### destination
servers

### service
TCP 22

### reason
General users do not receive administrative access.
### source
external-test

### destination
admin

### service
TCP 22

### reason
An untrusted external zone must not initiate administration access.

## Required reading

- RFC 1918, Address Allocation for Private Internets, especially the three reserved IPv4 ranges.
- RFC 5737, IPv4 Address Blocks Reserved for Documentation.
- NIST SP 800-41 Revision 1, Guidelines on Firewalls and Firewall Policy, sections covering policy design and rule ordering.
- Python documentation for the ipaddress module, focusing on IPv4Network, IPv4Address, and membership tests.

## References

- RFC 1918, Address Allocation for Private Internets: https://www.rfc-editor.org/rfc/rfc1918
- RFC 5737, IPv4 Address Blocks Reserved for Documentation: https://www.rfc-editor.org/rfc/rfc5737
- NIST SP 800-41 Revision 1, Guidelines on Firewalls and Firewall Policy: https://csrc.nist.gov/pubs/sp/800/41/r1/final
- Python 3 ipaddress module documentation: https://docs.python.org/3/library/ipaddress.html
- CIS Critical Security Controls, Network Infrastructure Management and Network Monitoring and Defense: https://www.cisecurity.org/controls

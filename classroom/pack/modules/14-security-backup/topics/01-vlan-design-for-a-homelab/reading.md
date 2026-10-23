# Reading: VLAN Design for a Homelab

**Module:** Segmentation, Backup & Power
**Activity type:** Reading (Learn)
**Objective:** Separate homelab devices into VLANs based on trust, function, and operational requirements

## Vocabulary

| Term | Meaning |
|---|---|
| VLAN | A logical Layer 2 broadcast domain identified by a VLAN ID on equipment that supports IEEE 802.1Q. |
| Access port | A switch port intended to place ordinary untagged endpoint traffic into one configured VLAN. |
| Trunk port | A link that carries multiple VLANs, normally as explicitly allowed tagged VLANs. |
| Tagged VLAN | A VLAN transported on a frame containing an IEEE 802.1Q tag. |
| Untagged VLAN | The VLAN assigned to frames sent or received without an IEEE 802.1Q tag on a particular port. |
| PVID | The port VLAN identifier used to classify an untagged ingress frame. Vendor terminology may call this an access VLAN or native VLAN depending on port mode. |
| Native VLAN | On platforms that support the concept, the VLAN associated with untagged traffic on a trunk. This lesson assigns an unused, unrouted blackhole VLAN for that role. |
| SVI | A switched virtual interface that provides a Layer 3 gateway address for a VLAN. |
| Trust boundary | A point at which traffic crosses between systems with different security assumptions and should be evaluated by policy. |
| Default deny | A policy posture in which traffic is rejected unless a specific allow rule authorizes it. |
| VLAN hopping | A class of attacks intended to move traffic into a VLAN that the sender should not be able to reach. |
| Double-tagging | A VLAN-hopping technique that places two VLAN tags in a frame and can exploit unsafe native-VLAN behavior on some switched paths. |

## Instruction

A VLAN is a Layer 2 boundary, not a complete security control. Hosts in different VLANs require a Layer 3 device to communicate, but meaningful isolation exists only when that device enforces an explicit policy. Begin by grouping systems according to trust and function rather than placing every device in one large subnet. This design uses management, infrastructure, lab, guest, and IoT zones. Management is reserved for authorized administration clients. Infrastructure contains shared servers. Lab contains experimental workloads. Guest and IoT devices are treated as untrusted. Each routed VLAN receives a unique subnet and gateway, while VLAN 999 is an unrouted blackhole VLAN used only for unused or untagged-port handling.

An access port should have one untagged VLAN and a matching PVID. A trunk should carry only the tagged VLANs required by the attached device. Do not automatically place the management VLAN on every hypervisor trunk. In this worked design, core-02 carries tagged VLAN 10 because the hypervisor host has an explicitly documented management interface in VLAN 10. It also carries VLANs 20 and 30 for infrastructure and lab workloads. It deliberately omits VLANs 40 and 50 because this host does not run guest or IoT workloads. If host management used a separate physical access port, VLAN 10 should be removed from the workload trunk. The access-point trunk carries VLANs 40 and 50 for wireless client networks and VLAN 10 only because the access point itself has a tagged management interface there.

Policy design starts with required flows, not broad statements such as allow internal or allow selected. Every policy row must name a defined source, a defined destination, a protocol, destination ports, an action, and a purpose. Client zones need DHCP for addressing, DNS for name resolution, and NTP for time synchronization. This model represents those shared gateway-hosted services with the defined destination gateway_services. The internet destination is also explicitly defined. Management receives narrowly scoped administrative access to infrastructure and IoT HTTPS interfaces. Lab, guest, and IoT may use specified internet services but are explicitly denied access to other internal zones. A default-deny policy covers traffic not listed.

Trunk allowlists reduce accidental exposure and limit the impact of mistakes. A trunk carrying every VLAN defeats that goal even if routing rules are otherwise correct. Untagged traffic on trunks is mapped to VLAN 999, which has no gateway or SVI. This helps reduce native-VLAN ambiguity, but it does not replace other controls. Disable dynamic trunk negotiation where supported, avoid using the native VLAN for user or management traffic, and keep native-VLAN behavior consistent at both ends. These practices help mitigate VLAN hopping, including double-tagging scenarios. Unused switch ports must not merely be assigned to VLAN 999; they must also be administratively disabled. Finally, treat the generated plan as vendor-neutral intent. Validate it, review it, and only then translate it into syntax appropriate for the actual switch, router, hypervisor, and access point.

## Architecture

### design_principles
One unique IPv4 subnet per routed VLAN
VLANs are assigned by trust and function
All trunk VLANs use explicit allowlists
Management VLAN membership requires a documented management function
Guest, IoT, and lab zones cannot initiate connections to internal zones
DHCP, DNS, NTP, and approved internet flows are explicitly represented
Unlisted routed traffic is denied
Unused physical ports are assigned to VLAN 999 and administratively disabled
VLAN 999 has no gateway, SVI, or routed policy

### endpoints
### name
gateway_services

### type
service_endpoint

### meaning
Gateway-operated DHCP, DNS, and NTP services reachable by explicitly listed client VLANs
### name
internet

### type
external_endpoint

### meaning
Destinations outside the homelab reached through the upstream route

### vlans
### vlan_id
10

### name
management

### subnet
10.70.10.0/24

### gateway
10.70.10.1

### routed
True

### trust
high

### purpose
Authorized administration clients and explicitly documented device-management interfaces
### vlan_id
20

### name
infrastructure

### subnet
10.70.20.0/24

### gateway
10.70.20.1

### routed
True

### trust
controlled

### purpose
Shared internal services
### vlan_id
30

### name
lab

### subnet
10.70.30.0/24

### gateway
10.70.30.1

### routed
True

### trust
limited

### purpose
Experimental workloads
### vlan_id
40

### name
guest

### subnet
10.70.40.0/24

### gateway
10.70.40.1

### routed
True

### trust
untrusted

### purpose
Guest devices requiring internet access but no internal access
### vlan_id
50

### name
iot

### subnet
10.70.50.0/24

### gateway
10.70.50.1

### routed
True

### trust
untrusted

### purpose
Embedded and appliance devices requiring limited internet access
### vlan_id
999

### name
blackhole

### subnet


### gateway


### routed
False

### trust
none

### purpose
Unused ports and untagged trunk traffic; no SVI or gateway

### ports
### port
core-01

### connected_device
router

### mode
trunk

### tagged_vlans
10
20
30
40
50

### untagged_vlan
999

### pvid
999

### admin_state
up

### purpose
Router-on-a-stick link for all routed VLANs
### port
core-02

### connected_device
hypervisor-01

### mode
trunk

### tagged_vlans
10
20
30

### untagged_vlan
999

### pvid
999

### admin_state
up

### purpose
Tagged VLAN 10 for the host management interface and VLANs 20 and 30 for approved workloads; VLANs 40 and 50 are excluded
### port
core-03

### connected_device
ap-01

### mode
trunk

### tagged_vlans
10
40
50

### untagged_vlan
999

### pvid
999

### admin_state
up

### purpose
Tagged access-point management on VLAN 10 and guest and IoT wireless networks on VLANs 40 and 50
### port
core-04

### connected_device
nas-01

### mode
access

### tagged_vlans


### untagged_vlan
20

### pvid
20

### admin_state
up

### purpose
Infrastructure NAS
### port
core-05

### connected_device
admin-workstation

### mode
access

### tagged_vlans


### untagged_vlan
10

### pvid
10

### admin_state
up

### purpose
Authorized management workstation
### port
core-06

### connected_device
lab-node

### mode
access

### tagged_vlans


### untagged_vlan
30

### pvid
30

### admin_state
up

### purpose
Untagged lab endpoint
### port
core-07

### connected_device
unused

### mode
access

### tagged_vlans


### untagged_vlan
999

### pvid
999

### admin_state
down

### purpose
Unused port assigned to the blackhole VLAN and administratively disabled

### routing_and_policy
### routing_location
Central Layer 3 gateway

### default_action
deny

### stateful_return_traffic
Return traffic for an established allowed flow is expected to be handled by the eventual stateful policy implementation.

### policy_columns
source
destination
protocol
destination_ports
action
purpose

### restricted_sources
lab
guest
iot

### internal_zones
management
infrastructure
lab
guest
iot

## Required reading

- IEEE 802.1Q overview: understand that VLAN tags identify logical broadcast domains across compatible links.
- RFC 1918, Address Allocation for Private Internets: review the private IPv4 address ranges.
- RFC 2131, Dynamic Host Configuration Protocol: review the client and server roles and UDP ports 67 and 68.
- RFC 1034 and RFC 1035: review the role of DNS and its use of port 53.
- RFC 5905, Network Time Protocol Version 4: review the role of NTP and UDP port 123.

## References

- IEEE 802.1Q standard overview: https://standards.ieee.org/ieee/802.1Q/6844/
- RFC 1918, Address Allocation for Private Internets: https://www.rfc-editor.org/rfc/rfc1918
- RFC 2131, Dynamic Host Configuration Protocol: https://www.rfc-editor.org/rfc/rfc2131
- RFC 1034, Domain Names—Concepts and Facilities: https://www.rfc-editor.org/rfc/rfc1034
- RFC 1035, Domain Names—Implementation and Specification: https://www.rfc-editor.org/rfc/rfc1035
- RFC 5905, Network Time Protocol Version 4: https://www.rfc-editor.org/rfc/rfc5905
- CISA, Securing Network Infrastructure Devices: https://www.cisa.gov/news-events/news/securing-network-infrastructure-devices

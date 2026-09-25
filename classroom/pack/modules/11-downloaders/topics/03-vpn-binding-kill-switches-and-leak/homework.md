# Homework: VPN Binding, Kill Switches, and Leak Verification

**Module:** Download Clients & Indexers
**Activity type:** Homework / independent application
**Objective:** Explain why an application bound to a VPN address is not automatically protected after that address or interface disappears.

## Requirements

Create a traffic inventory for one homelab application. Include process or service identity, IPv4 requirements, IPv6 requirements, DNS behavior, VPN endpoint requirements, LAN dependencies, container scope, and expected behavior when the tunnel is absent.
Write a test matrix with rows for normal operation, application restart, VPN restart, tunnel loss, endpoint change, host reboot, DNS failure, IPv6 availability, and container traffic. For each row, state the expected permitted and denied paths.
Draw a diagram showing the application, routing decision, VPN interface, physical uplink, resolver, VPN endpoint, and enforcement boundary.
Explain how you would collect evidence on both the tunnel and uplink without recording credentials or unrelated household traffic.
Propose a rollback plan that remains usable if a remote network-policy change disconnects management access.
Compare address binding with interface binding and document which method your selected application actually supports.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

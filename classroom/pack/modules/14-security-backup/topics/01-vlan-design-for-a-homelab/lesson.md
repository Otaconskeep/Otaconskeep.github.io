# Lesson 14.01: VLAN Design for a Homelab

**Module:** Segmentation, Backup & Power
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Separate homelab devices into VLANs based on trust, function, and operational requirements
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-27

## Learning objective

Separate homelab devices into VLANs based on trust, function, and operational requirements

## Why this matters

Design an auditable VLAN, subnet, switch-port, and inter-zone policy plan for a homelab without changing live network equipment. The lesson emphasizes explicit trust boundaries, least-privilege trunk allowlists, required infrastructure services, default-deny routing policy, disabled unused ports, and machine-verifiable documentation.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the design to a new homelab operator without using vendor-specific terms. Include why VLAN 10 is on the hypervisor trunk, why VLANs 40 and 50 are not, what VLAN 999 does, and why DHCP, DNS, NTP, and internet access must be written as separate policy flows.

### model_answer
The switch creates separate local networks for management, servers, experiments, guests, and IoT devices. A link should carry only the networks needed by the device on the other end. The hypervisor link carries management because the host itself has a tagged management interface, and it carries infrastructure and lab for approved virtual workloads. It does not carry guest or IoT because no such workloads are assigned there. VLAN 999 catches untagged trunk traffic and unused ports but has no route; unused physical ports are also shut down. When traffic must cross between networks, the gateway starts from deny and allows only named requirements. DHCP supplies addresses, DNS resolves names, NTP supplies time, and web or QUIC rules provide approved internet use. Writing each flow explicitly makes omissions and excessive permissions visible during review.

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain |
| 3 | [Lab](./lab.md) | Practice |
| 4 | [Homework](./homework.md) | Apply |
| 5 | [Quiz](./quiz.md) | Test |

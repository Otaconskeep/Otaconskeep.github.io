# Lesson 11.03: VPN Binding, Kill Switches, and Leak Verification

**Module:** Download Clients & Indexers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain why an application bound to a VPN address is not automatically protected after that address or interface disappears.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain why an application bound to a VPN address is not automatically protected after that address or interface disappears.

## Why this matters

Teach students to distinguish application binding, routing, and fail-closed packet filtering; design a layered VPN egress policy; and verify that application traffic, DNS, and IPv6 do not silently escape through a non-VPN path.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the design to a technically curious person who thinks selecting a VPN interface inside an application is enough.

### model_explanation
Binding tells an application which local address or interface it should try to use. Routing tells the operating system where a packet would go. A kill switch is the guard that refuses the packet if the chosen exit is not approved. If the tunnel vanishes, binding may cause an error, but software can restart, choose another address, use IPv6, ask DNS through another path, or run in a container with different rules. Therefore we verify several independent facts: the application uses the intended source, routing chooses the tunnel, enforcement rejects the uplink, DNS stays on the approved path, and IPv6 is tunneled or intentionally blocked. The strongest test deliberately removes the tunnel and confirms that traffic stops.

### self_check
Can you explain why a default route through the VPN does not prove every policy-routing table uses it?
Can you identify the narrow traffic that must usually remain allowed outside the tunnel?
Can you explain why tunnel-loss testing provides stronger evidence than a single public-address check?
Can you distinguish an inbound listener bind from outbound egress enforcement?

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

# Lesson 13.06: WireGuard Fundamentals and Deployment

**Module:** Edge Access & VPN
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain how WireGuard uses public keys as peer identities.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-26

## Learning objective

Explain how WireGuard uses public keys as peer identities.

## Why this matters

Teach the cryptographic identity model, routing behavior, configuration structure, deployment planning, verification methods, and operational security considerations of WireGuard. The laboratory creates and validates a staged site-to-site configuration without changing host networking or activating a tunnel.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain WireGuard to a new administrator without using the words VPN, magic, or secure by default.

### model_explanation
Each machine has a secret number and a shareable public identity derived from it. A machine keeps a list of remote public identities and the IP addresses each identity is allowed to represent. When an inner packet matches one of those address lists, the machine encrypts it for that peer and sends it inside UDP. The receiver proves which key produced the packet, decrypts it, and rejects an inner source address that the configured peer is not allowed to claim. The tunnel protects packets between the peers, while routing, service authorization, DNS, forwarding, and recovery still have to be designed separately.

### self_check
Can you explain why two peers must not exchange private keys?
Can you describe both the outbound and inbound roles of AllowedIPs?
Can you explain why a successful handshake does not prove that an application is reachable?
Can you explain when PersistentKeepalive helps and why it should not be enabled thoughtlessly?

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

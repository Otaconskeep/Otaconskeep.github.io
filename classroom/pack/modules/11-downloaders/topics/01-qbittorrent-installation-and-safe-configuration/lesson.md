# Lesson 11.01: qBittorrent Installation and Safe Configuration

**Module:** Download Clients & Indexers
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the separation between the qBittorrent process, Web UI, peer protocol, configuration, and download storage.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Explain the separation between the qBittorrent process, Web UI, peer protocol, configuration, and download storage.

## Why this matters

Deploy qBittorrent-nox as an isolated, reproducible Podman container; protect its Web UI; constrain all persistent lab state to /opt/lab-classroom/class49/; and establish responsible download, network, and rollback practices.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the deployment to a new administrator without using the words container, bind mount, or loopback.

### model_explanation
qBittorrent runs in a restricted application environment controlled by an ordinary user. Its settings and downloaded files are kept in named class directories so replacing the application wrapper does not erase them. The management page accepts connections only from the same computer, and the initial peer listener is also local-only. A password protects the management page, but downloaded files are still untrusted and peer-to-peer networking is not anonymous.

### self_check
Can you identify which directory stores settings and which stores payload data?
Can you explain why 127.0.0.1 is safer than 0.0.0.0 for the Web UI?
Can you explain why deleting a container does not have to delete its downloads?
Can you explain why transport encryption is not the same as anonymity?
Can you state what must be tested before relying on a VPN interface binding?

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

# Class 15 — IPv4 addresses, masks, and gateways

**Build output:** find your host’s IPv4, mask, and gateway; explain network vs host bits with the “255 / 0” reading hack; calculate usable addresses on a simple `/24`; prove same-LAN vs via-gateway reachability

## What you will learn

You will understand what an IPv4 address is for, how to read it on Windows and Linux, what the subnet mask and default gateway do, how DHCP usually hands out addresses at home, and how a device decides “same street / hand it over” versus “call the router.” You will practice a beginner subnet-reading hack that covers most home and small-lab `/24` networks—then you will prove it with commands, not vibes.

## Vocabulary

| Term | Meaning |
|---|---|
| IPv4 address | Four decimal numbers (0–255) separated by dots that identify a host on an IP network |
| Octet | One of the four numbers in an IPv4 address (eight bits) |
| Subnet mask / netmask | Companion value that marks which part of the address is the **network** and which is the **host** |
| Default gateway | The router IP your host uses to leave its local network (LAN) |
| DHCP | Service (usually on your router) that automatically assigns IP, mask, gateway, and DNS |
| Network address | First address of a subnet—reserved; not for normal hosts (often ends in `.0` on a `/24`) |
| Broadcast address | Last address of a subnet—reserved; talks to “everyone on this LAN” (often `.255` on a `/24`) |
| Host | A device with an IP: PC, phone, VM, AP, camera, printer… |
| Private address | Ranges used inside homes/labs (not routed on the public Internet as global uniques)—e.g. `192.168.0.0/16` |
| `/24` | Shorthand for mask `255.255.255.0` (first three octets = network on common home LANs) |

## Lesson

### What an IP address is for

Devices do not share pictures, API calls, or Netflix streams by shouting into the air. They send packets to a destination identity. On almost every LAN and on the Internet today, that identity is an **IP address**.

Think of it as a **mailing address for packets**, not a phone contact name. Without an address (or an equivalent layer-3 identity), the stack has nowhere to deliver the reply.

Your watch, phone, NAS, Proxmox node, and Docker host each need one when they participate in IP networking. That is why “everything got an IP” feels magical—and why broken addressing feels like the whole lab fell over.

### Meet the three friends on your NIC

When you inspect a typical IPv4 interface you see a trio:

| Field | Job |
|---|---|
| **IPv4 address** | “Who am I on this network?” |
| **Subnet mask** | “Which part of my address is the street name, and which is my house number?” |
| **Default gateway** | “Who do I ask when the destination is not on my street?” |

Ignore the word “IPv4” panic for now—this class is about the dotted-decimal addresses most labs still use first. IPv6 exists and matters; you will meet it later without throwing away these skills.

### How to find your address (every platform)

**Windows (CMD or PowerShell):**

```text
ipconfig
```

Look for `IPv4 Address`, `Subnet Mask`, and `Default Gateway` on the active Wi-Fi or Ethernet adapter.

**Linux / macOS:**

```bash
ip -br addr
ip route
# older alias still seen in docs:
ifconfig
```

**Phone:** Settings → Wi-Fi → tap the connected network → IP address / Router / Subnet (labels vary).

Write all three values in the workbook for the machine you use for Academy labs.

### Who handed you that number?

On most home and small-lab Wi-Fi, you did not invent `192.168.1.42`. Your **router** (or a dedicated DHCP server) offered it through **DHCP** when the interface came up: “Here is an address, here is the mask, here is the gateway, here is DNS.”

You can also set a **static** address—common for Proxmox, n8n, and NAS—so the number does not drift after a reboot. Static still must obey the same mask and stay unique on the LAN.

Bad or conflicting addresses (two hosts claiming the same IP, or a mask that lies) break “magic” fast. Diagnosis starts by reading the trio, not by reinstalling Docker.

### Why so many homes look like `192.168.1.x`

Many consumer routers ship DHCP pools in private space such as `192.168.1.0/24` or `192.168.0.0/24`. That is a convention and a private-range choice—not destiny. Your lab might use `10.0.0.0/24` or `172.16.0.0/24`. The **mask** tells the truth about what “your street” is—not the brand of the router.

### The beginner subnet-mask hack (covers most `/24` labs)

A mask has four octets too. Line them up under the IP:

```text
IP:   192.168.  1.  42
Mask: 255.255.255.   0
```

**Hack you can use today**

- Where the mask shows **255**, that octet is part of the **network** (street name)—it stays the same for every normal host on this subnet.
- Where the mask shows **0**, that octet is in the **host** portion (house number)—it changes per device.

So with `255.255.255.0`, every host on that LAN shares the first three octets (`192.168.1`) and differs in the last (`42`, `17`, `200`, …).

Deeper binary subnetting (non-`255`/`0` borders, VLSM, summarization) comes in later Academy networking work. This hack is the on-ramp that unlocks home labs and CCNA-style first chapters without drowning you on day one.

### Same street vs call the gateway

**Street analogy (sanitized):** the network portion is the street name; the host portion is the house number. Delivering coffee to a neighbor on the **same street** is a local walk. Delivering to another city needs a courier—the **default gateway**.

On the wire:

1. Host A wants Host B’s IP.
2. A applies the mask: “Is B on my network?”
3. **Yes** → deliver on the LAN (ARP/ND, switch, Wi-Fi AP—details aside).
4. **No** → send to the **default gateway**; the router forwards toward the remote network (including “the Internet”).

Netflix, public DNS, and `1.1.1.1` are almost never on your `192.168.1.0/24`. Your laptop notices and uses the gateway. Talking to your NAS on `192.168.1.50` from `192.168.1.42` with mask `255.255.255.0` stays local.

### How many usable addresses on a simple `/24`?

With mask `255.255.255.0`, the last octet can be `0`–`255` → **256** numeric values.

Two are reserved on that subnet:

| Address | Role |
|---|---|
| First (e.g. `192.168.1.0`) | **Network** address—do not assign to a host |
| Last (e.g. `192.168.1.255`) | **Broadcast**—do not assign to a host |

That leaves **254** theoretically assignable host addresses. In practice your **gateway** usually consumes one (e.g. `.1`), so a typical home pool might offer roughly **253** for phones, PCs, and IoT—exact DHCP pool size is a router setting.

If you answered “256” on the challenge, you counted reserved addresses. If you answered “254,” you remembered network + broadcast. If you answered “253,” you also subtracted a typical gateway. Write which model you used in the workbook.

### Private vs public (one careful sentence)

Addresses like `192.168.x.x`, `10.x.x.x`, and many `172.16–31.x.x` are **private**. Your router translates when you browse the public Internet. Your “what’s my IP” website shows a **public** address on the WAN side—not the `192.168` on your laptop. Both matter; do not confuse them when debugging port forwards or tunnels (Class 10).

## Guided lab

Use the machine you actually lab on. Replace example IPs with yours.

### Path A — Read the trio and classify network vs host

1. **Capture interface facts.**

:::windows
```powershell
ipconfig
ipconfig /all
Get-NetIPConfiguration | Format-List InterfaceAlias, IPv4Address, IPv4DefaultGateway
```
:::

:::linux
```bash
ip -br addr
ip route
ip -4 addr show
```
:::

2. **Workbook table:** adapter name, IPv4, mask, gateway, DHCP or static.

3. **Apply the 255/0 hack.** Circle network octets vs host octets. Write one sentence: “Every host on my LAN shares ____ and differs in ____.”

4. **List three other devices** on the same LAN (phone, AP, Proxmox, printer). Confirm their IPs share the network portion you predicted (check each device’s status page or `arp`/`ip neigh` after a ping).

:::linux
```bash
ping -c 2 GATEWAY-IP
ping -c 2 OTHER-LAN-HOST
ip neigh
```
:::

:::windows
```powershell
ping -n 2 GATEWAY-IP
ping -n 2 OTHER-LAN-HOST
arp -a
```
:::

### Path B — Same LAN vs via gateway

1. **Same-network test:** ping another LAN host; expect success (firewall permitting).

2. **Off-network test:** ping `1.1.1.1` (or another known Internet IP). Expect success only if WAN works.

:::linux
```bash
ping -c 3 1.1.1.1
traceroute -n 1.1.1.1 | head
# First hop should be your default gateway on a normal home setup
ip route | awk '/default/ {print}'
```
:::

:::windows
```powershell
ping -n 3 1.1.1.1
tracert -d 1.1.1.1
# First hop should be your Default Gateway
```
:::

3. **Workbook:** “First hop to the Internet was ____ (gateway). Local NAS ping did / did not need that hop for delivery decision.”

### Path C — Usable-address math on your `/24`

1. If your mask is `255.255.255.0`, compute:
   - network address
   - broadcast address
   - theoretical host count (254)
   - practical leftover after gateway (document your gateway IP)

2. **Optional stretch:** on the router admin UI (screenshot secrets removed), note DHCP pool start/end. Compare pool size to your math.

3. **Static caution (do not break production):** pick an unused address **inside** the subnet but **outside** the DHCP pool if you later static a lab VM. Record the choice; do not implement on a critical host until Class 1/Proxmox needs it.

## Break/fix

1. **Disconnect Wi-Fi / unplug Ethernet** → `ipconfig` / `ip addr` loses address or shows disconnected → restore → address returns (DHCP) or static returns.

2. **Wrong mental model:** pretend a host `10.0.0.5` is “local” to your `192.168.1.0/24` without a router—explain why the mask says no.

3. **Gateway down simulation (lab only):** if you can safely shut WAN on a test router, confirm LAN pings still work while `1.1.1.1` fails—proves local vs remote paths.

## Common mistakes

- Mixing up **private LAN IP** with **public WAN IP**.
- Calling every dotted number “the IP” and ignoring mask/gateway.
- Assuming all LANs are `192.168.1.0/24`.
- Assigning `.0` or `.255` to a host on a `/24`.
- Duplicating an IP already leased by DHCP.
- Debugging Docker DNS before confirming the host even has a gateway.

## Knowledge check

1. In plain words, why does a device need an IP address?
2. What three fields should you record with every IPv4 interface?
3. What does a `255` in a mask octet tell you? What does a `0` tell you?
4. When does a host use its default gateway?
5. On `192.168.1.0/24`, what are the network and broadcast addresses?
6. Why is “256 usable hosts” the wrong answer for that `/24`?
7. Who usually assigns addresses automatically at home?

## Practical gate

- [ ] Student can show IPv4, mask, and gateway from CLI or phone UI and read them aloud correctly.
- [ ] Student marks network vs host portions using the 255/0 hack for their real LAN.
- [ ] Same-LAN ping and Internet ping are both demonstrated (or failures explained with evidence).
- [ ] Usable-address calculation for their `/24` (or documented non-/24 with instructor help) is in the workbook.
- [ ] Student can explain network address, broadcast address, and why the gateway consumes an address.
- [ ] No home street address, no real public IP doxxing, and no secrets in shared screenshots.

## 2026 correction

Windows/macOS/Linux UI labels move; `ip` is preferred over `ifconfig` on modern Linux. Masks may appear as CIDR (`/24`) in some tools—same idea as `255.255.255.0`. Consumer Wi-Fi “smart” features can hide raw fields behind “Automatic.” Prefer official OS networking docs for exact clicks; the durable skills are the trio, the 255/0 reading hack, local vs gateway decision, and reserved addresses.

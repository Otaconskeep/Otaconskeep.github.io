# Class 3 — Docker Networking for the ARR Stack

**Lecture:** [NetworkChuck — Docker Networking](https://www.youtube.com/watch?v=bKFMS5C4CG0)  
**Time:** 120–150 minutes  
**Build output:** isolated application network with DNS-based calls

## Outcomes

You will understand default and user-defined bridges, embedded DNS, port publishing, host networking, `none`, MACVLAN, IPVLAN, overlay networks, and why the ARR stack normally starts with a user-defined bridge.

## Core model

Docker networking has two separate jobs:

1. Let containers communicate with each other.
2. Decide which services are reachable from the host or other networks.

```mermaid
flowchart TD
    L["LAN client"] -->|"host:8989"| H["Docker host"]
    H --> S["sonarr:8989"]
    S -->|"prowlarr:9696"| P["Prowlarr"]
    S -->|"qbittorrent:8080"| Q["qBittorrent"]
```

Inside a container, `localhost` means that container. Sonarr calling `localhost:9696` attempts to reach Sonarr, not Prowlarr. On a user-defined bridge, call `http://prowlarr:9696` using the Compose service name.

### Drivers

| Driver/mode | Purpose | Beginner position |
|---|---|---|
| Default bridge | Legacy automatic network | Understand, but do not build the stack around it |
| User-defined bridge | Single-host application networking with DNS | Default for the course |
| Host | Shares host network namespace | Use only with a documented reason |
| None | No external networking | Useful for isolation tests |
| MACVLAN | Gives containers LAN-facing MAC/IP identities | Advanced; switch/AP behavior matters |
| IPVLAN | Alternative L2/L3 attachment model | Advanced routing design |
| Overlay | Multi-host/swarm networking | Not required for one Docker host |

User-defined bridges provide predictable grouping and automatic name resolution. Port publishing is still needed for LAN users to access a service, but container-to-container calls do not need a published host port when both services share the network.

### Exposure and isolation

Do not publish every internal service simply because you can. A database used only by one application can remain reachable only on its Docker network. ARR web interfaces normally remain LAN-only or VPN-protected.

## Guided lab

**Where to run:** Docker host from Class 2 (Linux VM preferred).

### Setup — two containers on one user-defined bridge

1. **Create the network lab project.**

:::windows
```powershell
mkdir $HOME\network-lab -Force
cd $HOME\network-lab
@'
name: network-lab
services:
  responder:
    image: nginx:stable
    networks: [media_net]
  tester:
    image: curlimages/curl:latest
    command: ["sleep", "infinity"]
    networks: [media_net]
networks:
  media_net:
    name: media_net
'@ | Set-Content -Encoding utf8 compose.yaml
docker compose config
docker compose up -d
docker compose ps
```
:::

:::linux
```bash
mkdir -p ~/network-lab && cd ~/network-lab
cat > compose.yaml <<'YAML'
name: network-lab
services:
  responder:
    image: nginx:stable
    networks: [media_net]
  tester:
    image: curlimages/curl:latest
    command: ["sleep", "infinity"]
    networks: [media_net]
networks:
  media_net:
    name: media_net
YAML
docker compose config
docker compose up -d
docker compose ps
```
:::

2. **Prove DNS + HTTP by service name (no published host port required).**

:::windows
```powershell
docker compose exec tester getent hosts responder
docker compose exec tester curl -sI http://responder:80
docker network inspect media_net --format "{{json .Containers}}"
```
:::

:::linux
```bash
docker compose exec tester getent hosts responder
docker compose exec tester curl -sI http://responder:80
docker network inspect media_net
docker network inspect media_net -f '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{"\n"}}{{end}}'
```
:::

   Expected: `responder` resolves and `HTTP/1.1 200` (or similar) returns even though nothing is published to the LAN yet.

3. **Show why `localhost` inside tester is wrong for reaching responder.**

:::windows
```powershell
docker compose exec tester curl -sI http://localhost:80
# Expect failure — localhost is the tester container itself, not responder.
```
:::

:::linux
```bash
docker compose exec tester curl -sI --max-time 3 http://127.0.0.1:80 || echo "EXPECTED_FAIL localhost"
```
:::

4. **Publish a host port and compare internal vs external access.**  
   Edit responder to add:
```yaml
    ports:
      - "8081:80"
```
   Then recreate and test:

:::windows
```powershell
docker compose up -d
curl.exe -sI http://127.0.0.1:8081/
docker compose exec tester curl -sI http://responder:80
```
:::

:::linux
```bash
docker compose up -d
curl -sI http://127.0.0.1:8081/
# From another LAN machine (replace DOCKER-HOST):
# curl -sI http://DOCKER-HOST:8081/
docker compose exec tester curl -sI http://responder:80
```
:::

   Record in the workbook: **internal** `http://responder:80` vs **external** `http://DOCKER-HOST:8081`.

### Apply the model to media services

Later ARR wiring uses names like:

```text
Sonarr -> http://prowlarr:9696
Sonarr -> http://qbittorrent:8080
Radarr -> http://sabnzbd:8080
```

Exact ports go in `templates/service_contract.csv`—do not guess.

## Break/fix

1. **Disconnect tester from the network, watch DNS fail, reconnect.**

:::windows
```powershell
docker compose ps
docker network disconnect media_net $(docker compose ps -q tester)
docker compose exec tester getent hosts responder
docker network connect media_net $(docker compose ps -q tester)
docker compose exec tester getent hosts responder
docker compose exec tester curl -sI http://responder:80
```
:::

:::linux
```bash
T=$(docker compose ps -q tester)
docker network disconnect media_net "$T"
docker compose exec tester getent hosts responder || echo EXPECTED_FAIL
docker network connect media_net "$T"
docker compose exec tester getent hosts responder
docker compose exec tester curl -sI http://responder:80
```
:::

2. **Replace `responder` with `localhost` in curl** (already done above)—explain the failure in the workbook.

3. **Bind only to loopback and compare LAN access.** Change ports to `"127.0.0.1:8081:80"`, recreate, prove host-local works and another LAN device fails.

Troubleshooting order:

```text
running container -> shared network -> DNS name -> destination port -> listener -> application auth -> firewall/routing
```

## Common mistakes

- Using host LAN IPs for all internal calls and creating unnecessary hairpin paths.
- Assuming `localhost` refers to the Docker host.
- Adding `network_mode: host` as a universal fix.
- Using MACVLAN before checking parent interface, switch port, Wi-Fi limitations, and host-to-container reachability.
- Publishing database or admin ports to every interface.
- Debugging authentication before proving TCP reachability.

## Knowledge check

1. What does `localhost` mean inside Sonarr's container?
2. Why is a user-defined bridge better than the legacy default for a Compose stack?
3. Does container-to-container traffic require a published host port?
4. When is overlay networking relevant?
5. Why is host networking not a harmless troubleshooting switch?

## Practical gate

- [ ] Two containers communicate by service name.
- [ ] The student proves an unexposed service is unreachable from the LAN.
- [ ] Internal and external addresses are recorded separately.
- [ ] A deliberate network disconnect is diagnosed and repaired.
- [ ] No ARR/downloader admin interface is publicly exposed.

## 2026 correction

The lecture's driver survey is valuable, but a single-host ARR stack rarely needs MACVLAN, IPVLAN, or overlay networking. Start with a user-defined bridge and adopt advanced drivers only from an explicit requirement.


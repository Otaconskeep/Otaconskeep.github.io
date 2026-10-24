# Class 79: Docker Networking

**Learning objective:** Explain the difference between a container port and a host-published port; Describe how Docker's embedded DNS resolves Compose service names on user-defined networks; Create separate frontend and backend bridge networks; Attach a gateway service to two networks while isolating a client from a database service; Verify allowed communication with HTTP requests rather than relying on unreliable DNS-only probes; Inspect container network attachments and published-port state; Recognize that network segmentation reduces reachability but does not replace authentication or application security
**Bloom level:** Understand / Apply
**Track:** Containers and Service Infrastructure · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach how Docker Compose creates isolated bridge networks, provides service-name DNS, connects multi-homed services, and controls host exposure through explicit port publishing.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### host_platform
Linux with Docker Engine

### docker_engine
Docker Engine 24 or later recommended

### compose
Docker Compose v2 with support for the top-level name field

### container_image
alpine:3.20

### architectures
amd64
arm64

### notes
The lab uses commands provided by Alpine BusyBox.
The client keep-alive is tail -f /dev/null rather than sleep infinity.
Connectivity is verified with wget instead of relying on BusyBox nslookup behavior against Docker's embedded DNS.
Existing local copies of alpine:3.20 can be used without downloading the image again.

## Learning objective

- Explain the difference between a container port and a host-published port
- Describe how Docker's embedded DNS resolves Compose service names on user-defined networks
- Create separate frontend and backend bridge networks
- Attach a gateway service to two networks while isolating a client from a database service
- Verify allowed communication with HTTP requests rather than relying on unreliable DNS-only probes
- Inspect container network attachments and published-port state
- Recognize that network segmentation reduces reachability but does not replace authentication or application security

## Why this matters

Teach how Docker Compose creates isolated bridge networks, provides service-name DNS, connects multi-homed services, and controls host exposure through explicit port publishing.

## Prerequisites

- A Linux host or virtual machine with Docker Engine installed
- Docker Compose v2 available through the docker compose command
- Permission to communicate with the Docker daemon
- Basic familiarity with containers, YAML, TCP ports, and HTTP
- Permission to create files only under /opt/lab-classroom/class79/

## Required reading

- Docker Docs, Networking overview: https://docs.docker.com/engine/network/
- Docker Docs, Bridge network driver: https://docs.docker.com/engine/network/drivers/bridge/
- Docker Docs, Compose networking: https://docs.docker.com/compose/how-tos/networking/
- Docker Docs, Published ports: https://docs.docker.com/engine/network/#published-ports

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| bridge network | A software network created by Docker that connects containers on the same Docker host while separating them from containers on other networks. |
| user-defined network | A Docker network explicitly created by an operator or Compose project. It provides scoped connectivity and automatic name resolution between attached containers. |
| embedded DNS | Docker's built-in name-resolution service for containers on user-defined networks. It resolves service or container names only where network membership permits. |
| service name | The logical Compose name, such as gateway or database, that other containers on a shared network can use as a DNS name. |
| container port | A TCP or UDP port on which a process listens inside a container. A container port is not automatically exposed on the Docker host. |
| published port | A host address and port mapped by Docker to a container port, normally configured with the Compose ports key or docker run -p. |
| multi-homed container | A container attached to more than one network. In this lab, the gateway is attached to both frontend and backend. |
| internal network | A Docker network created with internal: true. Docker restricts external routing for that network, but members of the network can still communicate with each other. |
| network segmentation | The division of services into separate connectivity zones so that only intended communication paths exist. |

## Instruction

Docker networking separates three questions that are often confused: where a process listens, which containers can reach it, and whether the host or outside clients can reach it. A process listening on port 8080 inside a container does not automatically create a host port. Containers attached to the same user-defined bridge network can normally communicate directly using the destination container's listening port. Compose also registers service names with Docker's embedded DNS, so a client can request http://gateway:8080 without learning a changing container IP address. DNS visibility is scoped by network membership: a service that does not share a network with the requester should not be treated as directly reachable.

This lab models a segmented application. The client joins only the frontend network. The database joins only the backend network. The gateway joins both and therefore becomes the only service with a network path to each side. The gateway is multi-homed, but Docker does not automatically turn it into a general IP router. It can initiate application-level requests on both networks because it has an interface on each one. The client can resolve and contact gateway, while the gateway can resolve and contact database. The client should not directly resolve or contact database because they share no network.

The backend network is marked internal. This reduces unintended external routing for containers that exist only on that network. It is not an authentication system, an application firewall, or a guarantee that a compromised gateway cannot reach the database. The gateway is intentionally trusted with backend reachability. Production designs must still use authentication, authorization, encryption where appropriate, least-privilege credentials, and application-specific access controls.

Verification should test the complete path rather than DNS in isolation. A successful wget request demonstrates both name resolution and TCP/HTTP connectivity. A failed request is meaningful only after confirming that the client is running, wget exists, and a positive request to gateway succeeds. Otherwise, a stopped client or missing executable could be mistaken for successful isolation. Docker inspection then supplies the structural evidence: the client and database have no shared network, while the gateway appears on both networks. Finally, docker compose port confirms that no host port was published. An EXPOSE instruction or a process listening inside a container would document or create an internal listening port, but neither publishes that port to the host.

## Architecture

### overview
A three-service Compose project named class79 uses two user-defined bridge networks. HTTP is used only as a simple connectivity probe.

### networks
### name
frontend

### driver
bridge

### members
client
gateway

### purpose
Allows the client to contact the gateway.
### name
backend

### driver
bridge

### internal
True

### members
gateway
database

### purpose
Allows the gateway to contact the database without attaching the client to the database network.

### services
### name
client

### container_name_generated_by_compose
class79-client-1

### networks
frontend

### process
BusyBox-compatible tail -f /dev/null keep-alive

### role
Runs HTTP connectivity tests.
### name
gateway

### container_name_generated_by_compose
class79-gateway-1

### networks
frontend
backend

### process
BusyBox httpd listening on container port 8080

### role
Represents an application tier that can communicate with both zones.
### name
database

### container_name_generated_by_compose
class79-database-1

### networks
backend

### process
BusyBox httpd listening on container port 9090

### role
Represents a backend-only service.

### allowed_paths
client -> gateway:8080
gateway -> database:9090

### intentionally_blocked_path
client -> database:9090

### published_ports
None. The Compose file has no ports entries, so neither HTTP service is published on a host port.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Draw the two networks and label every container interface, allowed flow, blocked flow, and listening port.
Add a second frontend-only client service under /opt/lab-classroom/class79/ and prove that it can reach gateway but not database.
Temporarily attach the second client to backend, predict the result before testing, then remove that attachment and recreate the service.
Use docker network inspect on the project networks and compare the endpoint lists with each container's NetworkSettings.Networks output.
Write a short threat model explaining what happens if the dual-homed gateway is compromised and which application-level controls would still be required.

## Feynman teach-back

### prompt
Explain the lab to someone who knows basic networking but has never used Docker.

### model_explanation
Each container is like a small machine with one or more virtual network cards. The frontend network connects the client to the gateway, and the backend network connects the gateway to the database. Docker supplies a private directory service so containers on a shared network can use names such as gateway and database instead of changing IP addresses. The client cannot directly find or contact database because they do not share a network. The gateway has a virtual connection to both networks, so it can talk to each side. Port 8080 is open inside the gateway container, but it is not mapped to a port on the physical host. Therefore, other containers on frontend can use it, while host users do not receive a Docker-published endpoint.

## Retrieval check

1. 1. What is the difference between a container listening on port 8080 and Docker publishing port 8080?
2. 2. Why can the client resolve gateway by service name?
3. 3. Why should the client not be able to resolve or contact database in this lab?
4. 4. Which service is multi-homed, and why?
5. 5. Why is a generic failed wget command insufficient proof of network isolation?
6. 6. What does internal: true add to the backend network, and what security guarantees does it not provide?
7. 7. What result should docker compose port gateway 8080 produce in this lab?
8. 8. What container names should Compose v2 generate for the three services in the explicitly named class79 project?

## Guided lab

### workspace
/opt/lab-classroom/class79/

### scope_rule
All files created or edited by this lab remain under /opt/lab-classroom/class79/. Docker will also create project-scoped containers and networks managed by the Docker daemon.

### steps
### step
1

### instruction
Confirm that Docker Engine and Docker Compose v2 are available.

### command
docker version && docker compose version
### step
2

### instruction
Create the lab directories. Do not substitute another path.

### command
mkdir -p /opt/lab-classroom/class79/gateway /opt/lab-classroom/class79/database && cd /opt/lab-classroom/class79
### step
3

### instruction
Create a response file for the gateway service.

### command
cat > /opt/lab-classroom/class79/gateway/status.txt <<'EOF'
gateway reachable
EOF
### step
4

### instruction
Create a response file for the backend service.

### command
cat > /opt/lab-classroom/class79/database/db.txt <<'EOF'
database reachable through backend network
EOF
### step
5

### instruction
Create the Compose definition. The client uses tail -f /dev/null because it is supported by Alpine BusyBox and remains available for later docker compose exec commands.

### command
cat > /opt/lab-classroom/class79/compose.yaml <<'EOF'
name: class79
services:
  client:
    image: alpine:3.20
    user: "65534:65534"
    command: ["tail", "-f", "/dev/null"]
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    networks:
      - frontend

  gateway:
    image: alpine:3.20
    user: "65534:65534"
    command: ["httpd", "-f", "-p", "8080", "-h", "/srv"]
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    volumes:
      - type: bind
        source: ./gateway
        target: /srv
        read_only: true
    networks:
      - frontend
      - backend

  database:
    image: alpine:3.20
    user: "65534:65534"
    command: ["httpd", "-f", "-p", "9090", "-h", "/srv"]
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    volumes:
      - type: bind
        source: ./database
        target: /srv
        read_only: true
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
EOF
### step
6

### instruction
Validate the rendered Compose configuration, start the services, and verify that all three services remain running.

### command
cd /opt/lab-classroom/class79 && docker compose config && docker compose up -d && docker compose ps
### step
7

### instruction
From the client, request the gateway by Compose service name. Successful wget output verifies both service-name resolution and HTTP connectivity.

### command
cd /opt/lab-classroom/class79 && docker compose exec -T client sh -c 'command -v wget >/dev/null || exit 90; wget -T 5 -qO- http://gateway:8080/status.txt'
### step
8

### instruction
From the gateway, request the database by Compose service name. This verifies the permitted backend path.

### command
cd /opt/lab-classroom/class79 && docker compose exec -T gateway sh -c 'command -v wget >/dev/null || exit 90; wget -T 5 -qO- http://database:9090/db.txt'
### step
9

### instruction
Before the negative test, confirm that the client is running, wget exists, and the positive client-to-gateway control still succeeds.

### command
cd /opt/lab-classroom/class79 && docker compose ps --status running --services && docker compose exec -T client sh -c 'command -v wget >/dev/null || exit 90; wget -T 5 -qO- http://gateway:8080/status.txt'
### step
10

### instruction
Attempt the intentionally disallowed client-to-database request. A nonzero result counts as evidence of isolation only when the diagnostic reports a name-resolution or connection-path failure. An exited container or missing executable is a lab failure, not a successful negative test.

### command
cd /opt/lab-classroom/class79 && docker compose exec -T client sh -c 'command -v wget >/dev/null || exit 90; wget -T 3 -O- http://database:9090/db.txt'
### step
11

### instruction
Inspect network membership to obtain structural evidence for the permitted and denied paths.

### command
docker inspect class79-client-1 --format '{{json .NetworkSettings.Networks}}' && docker inspect class79-gateway-1 --format '{{json .NetworkSettings.Networks}}' && docker inspect class79-database-1 --format '{{json .NetworkSettings.Networks}}'
### step
12

### instruction
Verify that gateway port 8080 is not published on the host. Because there is no ports mapping, this command is expected to report an error or produce no mapping.

### command
cd /opt/lab-classroom/class79 && docker compose port gateway 8080

## Expected results

- docker compose ps lists the services client, gateway, and database as running.
- With Compose v2 and the explicit project name, the generated container names are class79-client-1, class79-gateway-1, and class79-database-1.
- The client-to-gateway request prints gateway reachable.
- The gateway-to-database request prints database reachable through backend network.
- The client-to-database request returns a nonzero status with a DNS or connection-path diagnostic because client and database do not share a network.
- Inspection shows class79-client-1 attached only to class79_frontend.
- Inspection shows class79-gateway-1 attached to both class79_frontend and class79_backend.
- Inspection shows class79-database-1 attached only to class79_backend.
- docker compose port gateway 8080 errors or prints nothing because port 8080 is not published to the host.

## Verification checkpoints

- [ ] Run cd /opt/lab-classroom/class79 && docker compose ps. The service column must show client, gateway, and database, and each service must be running.
- [ ] Run cd /opt/lab-classroom/class79 && docker compose ps --status running --services. Confirm that client appears before interpreting any client-side test.
- [ ] Run cd /opt/lab-classroom/class79 && docker compose exec -T client sh -c 'command -v wget >/dev/null || exit 90; wget -T 5 -qO- http://gateway:8080/status.txt'. It must print gateway reachable.
- [ ] Run cd /opt/lab-classroom/class79 && docker compose exec -T gateway sh -c 'command -v wget >/dev/null || exit 90; wget -T 5 -qO- http://database:9090/db.txt'. It must print database reachable through backend network.
- [ ] Run cd /opt/lab-classroom/class79 && docker compose exec -T client sh -c 'command -v wget >/dev/null || exit 90; wget -T 3 -O- http://database:9090/db.txt'. Accept the nonzero result only if the client is running, wget was found, the positive gateway control succeeded, and stderr identifies a DNS-resolution or network connection failure. Do not accept container-not-running, executable-not-found, or exit code 90 as evidence of isolation.
- [ ] Run docker inspect class79-client-1 --format '{{json .NetworkSettings.Networks}}'. Its network set must not include class79_backend.
- [ ] Run docker inspect class79-gateway-1 --format '{{json .NetworkSettings.Networks}}'. Its network set must include both class79_frontend and class79_backend.
- [ ] Run docker inspect class79-database-1 --format '{{json .NetworkSettings.Networks}}'. Its network set must not include class79_frontend.
- [ ] Run cd /opt/lab-classroom/class79 && docker compose port gateway 8080. It is expected to error or print nothing because no host port is published.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The client exits immediately after startup. | The client command was changed to an unsupported or finite command, such as sleep infinity on an Alpine BusyBox version that does not accept that operand. | Run docker compose logs client and docker inspect class79-client-1 --format '{{json .Config.Cmd}}'. Restore command: ["tail", "-f", "/dev/null"] in /opt/lab-classroom/class79/compose.yaml, then run docker compose up -d --force-recreate client. |
| One or more services repeatedly exit or are absent from docker compose ps. | The Compose file is invalid, the image is unavailable, a bind-mounted directory is missing, or the configured process failed. | Run docker compose config, then inspect docker compose ps -a and docker compose logs client gateway database from /opt/lab-classroom/class79. Correct only files in the lab workspace and recreate the affected service. |
| The client cannot retrieve the gateway response. | The gateway is not running, the frontend network attachment is missing, the service name or port is wrong, or the HTTP server has not started. | Confirm client and gateway are running, inspect both containers' network attachments, verify that both include class79_frontend, and confirm that the request uses http://gateway:8080/status.txt. |
| The gateway cannot retrieve the database response. | The gateway or database is not attached to backend, database is not running, or the request uses the wrong port or filename. | Inspect both containers and verify class79_backend membership. Check docker compose logs database and retry http://database:9090/db.txt from gateway. |
| The client can directly retrieve the database response. | The client was accidentally attached to backend, the database was attached to frontend, or an earlier container with different configuration is being tested. | Run docker compose config and inspect all three containers. Restore the intended network lists, run docker compose up -d --force-recreate, and confirm the project and container names begin with class79. |
| The client-to-database command fails with an executable-not-found message. | The image or command environment differs from the lesson, or wget is unavailable. | Do not count this as successful isolation. Confirm the service uses alpine:3.20 and run docker compose exec -T client sh -c 'command -v wget'. Recreate the client with the specified image if necessary. |
| docker compose port gateway 8080 reports that no public port exists. | No ports mapping is configured. | This is the expected result. The gateway is intended to be reachable only from containers on frontend, not from a host-published port. |
| Bind-mounted files return permission denied. | The host directories or files are not readable by container user 65534. | Inspect the ownership and read bits under /opt/lab-classroom/class79/. Ensure the directories are traversable and the two text files are readable without granting unnecessary write access. |

## Security considerations

### principles
No container port is published to the host.
The client is not attached to the backend network.
The database is not attached to the frontend network.
The backend network is marked internal.
Containers run as numeric user 65534 rather than the default root user.
All Linux capabilities are dropped.
The no-new-privileges security option is enabled.
Container root filesystems and bind mounts are read-only.

### limitations
Docker network segmentation is not a substitute for database authentication or authorization.
The gateway is intentionally able to reach the database and therefore becomes a security-sensitive trust boundary.
An internal Docker network limits external routing but does not prevent communication among its members.
Plain HTTP is used only for local connectivity demonstration and does not provide transport confidentiality or server identity.
Membership on the docker group commonly grants root-equivalent control over the Docker host; access to the Docker daemon must be tightly controlled.

## Rollback

### instruction
Stop and remove only the class79 Compose containers and project networks. The lesson files remain under the approved workspace for review or reuse.

### command
cd /opt/lab-classroom/class79 && docker compose down --volumes --remove-orphans

### verification
Run docker ps -a --filter name=class79 and docker network ls --filter name=class79. No class79 lab containers or project networks should remain.

## Video narration notes

Begin by showing the architecture as two overlapping network zones. The client belongs only to frontend, the database belongs only to backend, and gateway belongs to both. Emphasize that the overlap belongs to gateway rather than to the networks themselves. Create the workspace and the two response files, then review the Compose definition. Point out the absence of a ports key, the use of tail -f /dev/null as a BusyBox-safe client keep-alive, and the separate network lists on each service. Start the project and pause on docker compose ps to identify the service names and generated container names. From client, request gateway by service name and explain that successful output proves DNS resolution, TCP connectivity, and an HTTP response. From gateway, request database and explain the same chain on backend. Before the negative test, verify that client is running, wget exists, and client can still reach gateway. Then attempt client-to-database communication and interpret only a DNS or connection-path failure as the intended result. Inspect all three containers to connect observed behavior to network membership. Finally, run docker compose port gateway 8080 and explain why an error or empty result is correct: a listening container port is not the same as a host-published port. End by stressing that segmentation limits reachability but does not replace credentials, authorization, encryption, or gateway hardening.

## References

- Docker Docs, Networking overview: https://docs.docker.com/engine/network/
- Docker Docs, Bridge network driver: https://docs.docker.com/engine/network/drivers/bridge/
- Docker Docs, Compose networking: https://docs.docker.com/compose/how-tos/networking/
- Docker Docs, Container network settings when running containers: https://docs.docker.com/engine/containers/run/#network-settings
- Docker Docs, Compose file networks reference: https://docs.docker.com/reference/compose-file/networks/
- Docker Docs, Compose file services reference: https://docs.docker.com/reference/compose-file/services/

## Mastery gate

- [ ] Objectives demonstrated with evidence
- [ ] Feynman complete
- [ ] Quiz self-scored ≥80%
- [ ] Lab verification boxes checked
- [ ] Rollback understood

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Return to this class whenever a later service fails for identity, process, log, remote access, update, or routing reasons covered here.

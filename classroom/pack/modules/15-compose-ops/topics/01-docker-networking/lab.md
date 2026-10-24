# Lab: Docker Networking

**Module:** Compose Operations & IaC
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain the difference between a container port and a host-published port

## Before you start

- A Linux host or virtual machine with Docker Engine installed
- Docker Compose v2 available through the docker compose command
- Permission to communicate with the Docker daemon
- Basic familiarity with containers, YAML, TCP ports, and HTTP
- Permission to create files only under /opt/lab-classroom/class79/

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

## Verification

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

## Security

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

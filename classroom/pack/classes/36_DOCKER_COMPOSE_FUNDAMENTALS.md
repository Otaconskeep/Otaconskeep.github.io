# Class 36: Docker Compose Fundamentals

**Learning objective:** Explain the role of a Compose file and how it differs from an individual docker run command.; Define services, images, commands, ports, bind mounts, networks, health checks, and security options in YAML.; Use a Compose project name to create a predictable resource namespace.; Validate a Compose model before starting containers.; Start services in detached mode and inspect their state and logs.; Demonstrate service-to-service communication through Compose DNS.; Distinguish published host ports from internal container-network connectivity.; Stop and remove the lab's Compose-managed runtime resources without affecting unrelated projects.
**Bloom level:** Understand / Apply
**Track:** Containers and Application Hosting · **Difficulty:** beginner · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach students how to define, start, inspect, verify, and stop a small multi-container application with Docker Compose while keeping all directly managed host files inside /opt/lab-classroom/class36/.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-20
**Compatibility:** ### platforms
Linux hosts running Docker Engine
Linux virtual machines used as Docker hosts
Docker Desktop environments where the /opt/lab-classroom/class36/ path is available to the Docker VM or file-sharing layer

### compose_requirement
Docker Compose v2 using the docker compose command form.

### images
nginx:1.27-alpine
busybox:1.36

### notes
The lab uses standard Compose services, bridge networking, port publication, bind mounts, security options, and health checks.
Rootless Docker may use different daemon-managed storage and networking behavior, but the Compose concepts remain the same.
Mandatory access-control systems may require an approved file-labeling policy for bind-mounted content.
If port 8080 is already allocated, an administrator-approved unused loopback port may be substituted in the Compose file.
Container image tags can be updated or removed by publishers over time. Revalidate image availability and organizational approval during future lesson reviews.

## Learning objective

- Explain the role of a Compose file and how it differs from an individual docker run command.
- Define services, images, commands, ports, bind mounts, networks, health checks, and security options in YAML.
- Use a Compose project name to create a predictable resource namespace.
- Validate a Compose model before starting containers.
- Start services in detached mode and inspect their state and logs.
- Demonstrate service-to-service communication through Compose DNS.
- Distinguish published host ports from internal container-network connectivity.
- Stop and remove the lab's Compose-managed runtime resources without affecting unrelated projects.

## Why this matters

Teach students how to define, start, inspect, verify, and stop a small multi-container application with Docker Compose while keeping all directly managed host files inside /opt/lab-classroom/class36/.

## Prerequisites

- Completion of an introductory Docker lesson covering images, containers, ports, bind mounts, and container logs.
- A Linux host or virtual machine with Docker Engine installed and running.
- Docker Compose v2 available through the docker compose command.
- An account authorized to access the Docker daemon, either directly or through an approved privilege-elevation method.
- TCP port 8080 available on the loopback interface.
- Internet access for retrieving the referenced container images if they are not already present in the local image cache.

## Required reading

- Docker Docs: Compose file reference: https://docs.docker.com/reference/compose-file/
- Docker Docs: How Compose works: https://docs.docker.com/compose/intro/compose-application-model/
- Docker Docs: Networking in Compose: https://docs.docker.com/compose/how-tos/networking/
- Docker Docs: Docker Compose CLI reference: https://docs.docker.com/reference/cli/docker/compose/

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Compose file | A YAML document that declares the desired services, networks, volumes, configurations, and related settings for an application. |
| Service | A reusable container definition in a Compose model. A service can produce one or more containers with a shared configuration. |
| Project | The namespace Compose uses to group and label related containers, networks, and other resources. |
| Image | The read-only container template from which a service container is created. |
| Bind mount | A mapping that exposes a specific host file or directory at a path inside a container. |
| Published port | A mapping from a host address and port to a port inside a container. |
| Service discovery | The ability of containers on a Compose network to reach a service through its service name, such as web. |
| Health check | A command executed for a container to report whether its application is functioning, independently of whether the container process is merely running. |
| Declarative configuration | A description of the desired state rather than a sequence of manual commands used to construct that state. |
| Idempotence | The property that repeatedly applying the same desired configuration converges on the same result instead of creating unrelated duplicates. |

## Instruction

Docker Compose describes a containerized application as a model. Instead of entering a long docker run command for every container, you record the desired images, commands, networks, mounts, ports, and health checks in a YAML file. Compose then translates that model into Docker resources carrying labels that identify their project and service. This makes an application easier to review, repeat, troubleshoot, and remove as a unit.

The top-level services mapping contains the application's service definitions. In this lesson, web runs NGINX and serves a host-managed HTML file, while client runs a small BusyBox container used to test internal connectivity. Both services join labnet. Compose provides network-scoped DNS, so the client can request http://web without knowing the web container's changing IP address. Container IP addresses are implementation details and should not be placed in application configuration when a stable service name is available.

The web port declaration uses 127.0.0.1:8080:80. Port 80 is the container-side listening port, 8080 is the host-side port, and 127.0.0.1 limits the listener to the host's loopback interface. Internal traffic from client to web does not travel through port 8080; it uses the shared Docker network and the container port directly. This distinction is central to understanding Compose networking.

The HTML file is bind-mounted read-only. That demonstrates how host-managed content can be injected without rebuilding an image, while the read-only flag reduces accidental modification from inside the container. Bind mounts also create a dependency on a specific host path. Relative paths are convenient, but this lesson uses explicit paths so the mutation boundary remains clear. In a production workflow, application content is often built into a purpose-specific image rather than mounted from an administrator-managed directory.

Always validate the model before starting it. The config command resolves and checks the Compose input and can reveal YAML or schema mistakes without creating the service containers. Starting with up --detach reconciles the declared model and leaves the containers running in the background. The ps and logs commands then expose runtime state. A running process is not necessarily a functioning application, so web also has an HTTP health check. Health may briefly display as starting before becoming healthy.

Compose project names matter. This lab always supplies the project name class36 so resources are grouped predictably and do not depend on the current directory's name. The same project name and file should be used for every lifecycle command. The down command removes the project's containers and network, but it does not remove the source files or indiscriminately delete unrelated Docker resources. Compose is therefore both a documentation format and a lifecycle tool for a defined application boundary.

## Architecture

### summary
A two-service Compose project named class36 contains an NGINX web service and a BusyBox client service on an isolated bridge network.

### components
web: Runs nginx:1.27-alpine, serves a read-only HTML bind mount, publishes container port 80 to host loopback port 8080, and performs an internal HTTP health check.
client: Runs busybox:1.36 and remains available so students can execute an internal HTTP request.
labnet: A Compose-managed bridge network that provides isolation and service-name DNS.
/opt/lab-classroom/class36/site/index.html: Host-managed web content mounted into the web container.
/opt/lab-classroom/class36/compose.yaml: Declarative Compose model for the lab.

### traffic_flow
Host-local access flows from 127.0.0.1:8080 to port 80 in the web container.
Internal access flows from client to the DNS name web on port 80 through labnet.
No port is published for the client service.

### mutation_boundary
All files and directories directly created or edited by the lab are beneath /opt/lab-classroom/class36/. Docker also creates project-scoped containers and a network in its daemon-managed storage as an inherent part of running Compose.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Create a second Compose file named /opt/lab-classroom/class36/compose-homework.yaml. Keep all homework files under /opt/lab-classroom/class36/. Define a web service and two client services on one explicitly named network. Do not publish either client. Bind the web service only to host loopback, mount a homework HTML page read-only, and add a health check. Use the project name class36homework when validating or running the homework model.

### deliverables
The homework Compose file.
The homework HTML file.
The normalized output from the Compose config command.
A service status capture showing the web service healthy.
Output from each client retrieving the web page by service name.
A short explanation of why service names are preferred over container IP addresses.

### constraints
Do not edit files outside /opt/lab-classroom/class36/.
Do not use host networking, privileged mode, or Docker daemon socket mounts.
Do not publish the client services.
Use a distinct approved loopback port if the primary lab still occupies port 8080.
Stop the homework project with its exact project name after verification.

## Feynman teach-back

### prompt
Explain Docker Compose to someone who knows what a container is but has only used individual docker run commands.

### model_explanation
A Compose file is a written recipe for a group of containers. Each service describes one role, such as a web server or client. Compose gives the group a project name, creates a private network, starts the containers with the declared options, and labels the resources so they can be managed together. Containers on the network use service names instead of memorizing IP addresses. A published port allows selected host traffic to reach a container, while a bind mount makes a chosen host file visible inside it. Running up asks Docker to match the recipe; running down removes that project's runtime resources.

### self_check_questions
Why can the client use http://web/ even though no DNS record was added to the homelab's normal DNS server?
Why does the client use port 80 while a host-local user uses port 8080?
What information is preserved in compose.yaml that would otherwise be scattered across shell history?
Why is a healthy state more informative than a running state?

## Retrieval check

1. 1. What is the primary purpose of a Docker Compose file?
2. 2. In the mapping 127.0.0.1:8080:80, which port is used by another container contacting the web service through the Compose network?
3. 3. Why can the client service resolve the hostname web?
4. 4. What does docker compose config --quiet accomplish before deployment?
5. 5. What is the practical difference between a container being running and being healthy?
6. 6. Why does this lesson consistently pass -p class36?
7. 7. What protection does the read-only bind-mount suffix provide?
8. 8. Does docker compose down normally remove the Compose source file?
9. 9. Why should application configuration avoid fixed container IP addresses?
10. 10. Why is binding the published port to 127.0.0.1 safer than publishing it on all host interfaces for this local lab?

## Guided lab

### title
Build and Operate a Two-Service Compose Project

### steps
### step
1

### name
Confirm the tools

### commands
docker version
docker compose version

### notes
Both commands must succeed before continuing. If Docker access is denied, correct the approved daemon-access configuration rather than changing broad filesystem permissions.
### step
2

### name
Create the bounded lab directories

### commands
install -d /opt/lab-classroom/class36/site

### notes
This is the only host directory tree used for lab-created files.
### step
3

### name
Create the static page

### commands
printf '%s\n' '<!doctype html>' '<html lang="en">' '<head><meta charset="utf-8"><title>Class 36</title></head>' '<body><h1>Docker Compose Fundamentals</h1><p>Service discovery and bind mounts are working.</p></body>' '</html>' > /opt/lab-classroom/class36/site/index.html

### notes
The output redirection targets only the approved class directory.
### step
4

### name
Create the Compose model

### commands
printf '%s\n' 'services:' '  web:' '    image: nginx:1.27-alpine' '    ports:' '      - "127.0.0.1:8080:80"' '    volumes:' '      - "/opt/lab-classroom/class36/site/index.html:/usr/share/nginx/html/index.html:ro"' '    networks:' '      - labnet' '    security_opt:' '      - no-new-privileges:true' '    healthcheck:' '      test: ["CMD-SHELL", "wget -qO- http://127.0.0.1/ >/dev/null || exit 1"]' '      interval: 10s' '      timeout: 3s' '      retries: 5' '      start_period: 5s' '  client:' '    image: busybox:1.36' '    command: ["sh", "-c", "while true; do sleep 3600; done"]' '    networks:' '      - labnet' '    security_opt:' '      - no-new-privileges:true' 'networks:' '  labnet:' '    driver: bridge' > /opt/lab-classroom/class36/compose.yaml

### notes
Compose files do not require a legacy version key. YAML indentation is significant.
### step
5

### name
Validate the Compose model

### commands
docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml config --quiet
docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml config

### notes
The first command should produce no output on success. The second displays the normalized model for review.
### step
6

### name
Start the project

### commands
docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml up --detach

### notes
Docker may retrieve the declared images if they are not locally cached. Repeating this command reconciles the existing class36 project rather than intentionally creating an unrelated project.
### step
7

### name
Inspect service state

### commands
docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml ps
docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml logs --tail 30 web

### notes
The web health state can initially be starting. Recheck after the configured health-check interval.
### step
8

### name
Verify internal service discovery

### commands
docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml exec -T client wget -qO- http://web/

### notes
The client uses the service name web and container port 80. It does not use the published host port.
### step
9

### name
Inspect the project network

### commands
docker network inspect class36_labnet

### notes
Review the attached containers and labels. Do not build application logic around the displayed container IP addresses.
### step
10

### name
Observe declarative reconciliation

### commands
docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml up --detach
docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml ps

### notes
With an unchanged model, Compose should retain the existing desired project state instead of creating a second independently named stack.

## Expected results

- The Compose model validates without a YAML or model error.
- The class36 project contains one web container and one client container.
- The web service becomes healthy after its HTTP health check succeeds.
- The client remains running and can resolve the service name web.
- The internal HTTP request returns HTML containing Docker Compose Fundamentals.
- The web service is published only on host address 127.0.0.1 and port 8080.
- The project has a Compose-managed network named class36_labnet.
- The mounted index.html file remains stored beneath /opt/lab-classroom/class36/.

## Verification checkpoints

- [ ] Run docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml config --quiet; a zero exit status and no validation message indicate that the model is valid.
- [ ] Run docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml ps; web and client should be running, and web should eventually report healthy.
- [ ] Run docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml exec -T client wget -qO- http://web/; the response should contain the Class 36 page.
- [ ] Run docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml port web 80; the result should identify host loopback port 8080.
- [ ] Run docker network inspect class36_labnet; the output should identify the class36 project network and attached service containers.
- [ ] Run docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml logs --tail 30 web; successful requests should appear without an NGINX startup failure.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| docker compose is reported as an unknown command. | The Docker Compose v2 plugin is not installed or the active Docker CLI cannot locate it. | Install the Compose plugin using the operating system's approved package-management process, then confirm with docker compose version. |
| Docker reports permission denied while connecting to the daemon socket. | The current account is not authorized to access the Docker daemon. | Use the environment's approved administrative access method or add the account through the documented Docker access process. Remember that Docker daemon access is effectively privileged. |
| Compose reports a YAML parsing error. | Indentation, quoting, or a key in compose.yaml was changed incorrectly. | Compare the file with the lesson definition, use spaces rather than tabs, and rerun the config command before attempting to start services. |
| The web service cannot publish port 8080. | Another process or container is already listening on 127.0.0.1:8080. | Stop the conflicting lab workload through its own lifecycle procedure, or choose an approved unused loopback port by editing only /opt/lab-classroom/class36/compose.yaml and then revalidate the model. |
| The web container runs but remains unhealthy. | NGINX did not start, the mounted file is inaccessible, or the health-check command is failing. | Inspect the web logs, inspect the resolved Compose configuration, and confirm that /opt/lab-classroom/class36/site/index.html exists and is readable by the container. |
| The client cannot resolve the name web. | The services are not attached to the same Compose network or the wrong project/file combination was used. | Run the config command and verify both services list labnet. Use the exact project name class36 and Compose file path shown in the lesson. |
| The bind mount is denied on a host using mandatory access controls. | The host security policy does not permit the container to read the file with its current label or policy context. | Follow the platform's documented container-labeling procedure for content beneath the class36 directory. Do not disable the host security control globally. |
| The expected network name is not present. | A different project name was used or the project has already been stopped. | Start the model with -p class36 and inspect the output of the Compose ps command before checking class36_labnet again. |

## Security considerations

The published port is bound to 127.0.0.1, preventing direct exposure on external host interfaces. Remote access should be added only through an intentional, authenticated ingress design.
The site file is mounted read-only so the web container cannot modify the host copy through that mount.
Both services use no-new-privileges to prevent processes from gaining additional privileges through set-user-ID or set-group-ID executables.
The client has no published port and is reachable only through its attached Docker network and administrative Docker access.
The lab uses explicit image tags for repeatability at the lesson level, but tags are not immutable. Production deployments should use an image governance process and approved digest pinning without inventing or copying unverified digests.
Anyone with control of the Docker daemon can generally obtain host-level control. Treat Docker group membership and access to the daemon socket as privileged access.
Do not place passwords, API keys, or private keys directly in a Compose file. Use an appropriate secrets mechanism and restrict access according to the platform's threat model.
Review images for provenance, maintenance status, and known vulnerabilities before production use.
The lab does not grant privileged mode, host networking, host process namespace access, or unrestricted host filesystem mounts.
Application health checks establish availability signals, not application authenticity, authorization, or end-to-end security.

## Rollback

### goal
Remove the class36 runtime resources while preserving the lesson files for review or reuse.

### commands
docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml down --remove-orphans

### verification
Run docker compose -p class36 -f /opt/lab-classroom/class36/compose.yaml ps; no class36 service containers should be listed.
Run docker network inspect class36_labnet; Docker should report that the project network is absent after a successful shutdown.
Confirm that /opt/lab-classroom/class36/compose.yaml and /opt/lab-classroom/class36/site/index.html remain available as lesson artifacts.

### scope
The rollback targets only resources associated with the explicitly named class36 Compose project. It does not prune unrelated containers, networks, volumes, or images.

## Video narration notes

Welcome to Class 36, Docker Compose Fundamentals. In this class we replace a collection of one-off container commands with a declarative application model. Our model has two services. The web service runs NGINX and serves a page from a read-only bind mount. The client service gives us a controlled location from which to test container-to-container communication. Both services join a Compose-managed bridge network.

Notice that every command uses the project name class36 and the full path to the Compose file. The explicit project name creates a stable namespace, while the full path keeps the exercise independent of the current working directory. All files we create are under /opt/lab-classroom/class36/. Docker will also maintain project-scoped containers and a network in its own managed storage.

Before starting anything, we run docker compose config. This catches many YAML and model errors early and shows us the normalized configuration. After validation, docker compose up --detach asks Docker to reconcile the declared state. We then use docker compose ps rather than assuming startup means success. The health check performs an HTTP request inside the web container, so the service can report healthy only after NGINX responds.

The port mapping is intentionally bound to 127.0.0.1. A host-local connection uses port 8080, which Docker forwards to port 80 in the web container. The client does not use that published port. Because client and web share labnet, the client reaches http://web on port 80. Compose DNS translates the service name into the current network address. This is more reliable than recording a container IP that can change after recreation.

The bind mount demonstrates a simple development and homelab pattern. The HTML file exists on the host and appears at NGINX's index path. The read-only suffix prevents the container from changing the host file through that mount. For a production application, you would normally evaluate whether building content into a reviewed image provides better repeatability and supply-chain control.

Finally, we repeat the up command to see declarative reconciliation. With no model change, Compose manages the same named project rather than creating a separate stack. We finish with the down command, which removes the project's containers and network without pruning unrelated Docker resources or deleting our lesson source files.

## References

- Docker Docs: Docker Compose overview: https://docs.docker.com/compose/
- Docker Docs: Compose file reference: https://docs.docker.com/reference/compose-file/
- Docker Docs: Compose services reference: https://docs.docker.com/reference/compose-file/services/
- Docker Docs: Compose networks reference: https://docs.docker.com/reference/compose-file/networks/
- Docker Docs: Networking in Compose: https://docs.docker.com/compose/how-tos/networking/
- Docker Docs: docker compose up: https://docs.docker.com/reference/cli/docker/compose/up/
- Docker Docs: docker compose down: https://docs.docker.com/reference/cli/docker/compose/down/
- Docker Docs: docker compose config: https://docs.docker.com/reference/cli/docker/compose/config/
- Docker Docs: Bind mounts: https://docs.docker.com/engine/storage/bind-mounts/
- Docker Docs: Container security: https://docs.docker.com/engine/security/

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

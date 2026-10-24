# Reading: Docker Networking

**Module:** Compose Operations & IaC
**Activity type:** Reading (Learn)
**Objective:** Explain the difference between a container port and a host-published port

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

## Required reading

- Docker Docs, Networking overview: https://docs.docker.com/engine/network/
- Docker Docs, Bridge network driver: https://docs.docker.com/engine/network/drivers/bridge/
- Docker Docs, Compose networking: https://docs.docker.com/compose/how-tos/networking/
- Docker Docs, Published ports: https://docs.docker.com/engine/network/#published-ports

## References

- Docker Docs, Networking overview: https://docs.docker.com/engine/network/
- Docker Docs, Bridge network driver: https://docs.docker.com/engine/network/drivers/bridge/
- Docker Docs, Compose networking: https://docs.docker.com/compose/how-tos/networking/
- Docker Docs, Container network settings when running containers: https://docs.docker.com/engine/containers/run/#network-settings
- Docker Docs, Compose file networks reference: https://docs.docker.com/reference/compose-file/networks/
- Docker Docs, Compose file services reference: https://docs.docker.com/reference/compose-file/services/

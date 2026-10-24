# Reading: Reusable Docker Compose Stack Patterns

**Module:** Compose Operations & IaC
**Activity type:** Reading (Learn)
**Objective:** Create a reusable Compose stack with extension fields and YAML anchors.

## Vocabulary

| Term | Meaning |
|---|---|
| Compose model | The normalized application definition produced after Compose parses files, resolves interpolation, applies merges, and validates service structure. |
| Extension field | A reusable top-level or nested YAML element whose name begins with x-. Compose ignores it as an application resource, allowing it to hold shared configuration. |
| YAML anchor | A YAML mechanism that names a node so it can be reused through an alias. Anchors reduce repeated source text but are resolved before Compose applies its own merge rules. |
| Interpolation | Substitution of expressions such as ${WEB_PORT:-8080} before the Compose model is finalized. |
| env_file | A service setting that supplies variables to a future container. It is not, by itself, the source used to interpolate the Compose file. |
| Profile | A label that makes a service optional for normal Compose operations unless that profile is enabled or the service is explicitly targeted. |
| Override file | A later Compose file layered over an earlier file. Mapping and sequence behavior follows Compose merge rules rather than simple textual replacement. |
| Unique resource | A sequence element, such as a volume keyed by container target, that Compose can match across files and merge or replace as one logical resource. |
| !override | A Compose-specific YAML tag that replaces the earlier value completely instead of applying normal merge behavior. |
| Canonical long-form port | A normalized port object containing semantic fields such as host_ip, published, target, and protocol rather than a short string such as host:published:target. |

## Instruction

Reusable Compose design separates stable structure from deployment-specific choices. A base file should express service identity, shared policy, networks, container-facing paths, and safe defaults. Environment-specific files should contain only intentional differences. This keeps review focused: a production overlay that changes one port and one environment value is easier to audit than a copied application definition. Extension fields and YAML anchors reduce repetition inside one YAML document, but they are not templates and do not cross file boundaries. Compose still performs its own merge after YAML parsing, so learners must understand both layers.

Interpolation and env_file solve different problems. Interpolation chooses values while Compose reads the model; sources include the invoking shell, the default .env file, or an explicit --env-file. A service-level env_file supplies variables to the eventual container. Confusing these stages creates configurations that appear correct in source but render incorrectly. Rendering with docker compose config makes the effective values visible before any workload is created.

Profiles control operational selection, not whether a service exists in the application definition. In this lesson, worker is present in the full rendered model and carries the ops profile. However, docker compose config --services without an enabled profile lists only web. Enabling ops causes the service list to include both web and worker. This distinction is important when reviewing optional maintenance agents, debugging tools, or scheduled workers.

Merging also requires explicit intent. Maps commonly merge by key, while several sequence types use resource-specific uniqueness rules. A volume with the same container target represents the same logical mount, so a later definition changes that mount. A volume with a new target is appended. For values that must be replaced as a whole, such as an environment-specific published-port list, the !override tag documents replacement directly. Machine-readable JSON assertions are preferable to grepping rendered YAML because Compose may normalize short syntax into long-form objects without changing the meaning.

## Architecture

### scope
Static Compose rendering and validation only; no container is started by the lab.

### workspace
/opt/lab-classroom/class80/stack

### project_name
class80

### files
### compose.yaml
Base model containing shared defaults, web, the profile-gated worker, a network, a bind mount, and an interpolated port.

### compose.prod.yaml
Production overlay that changes APP_ENV and replaces the web port list with a port published on 127.0.0.1:8181.

### compose.mounts.yaml
Mount experiment that replaces the site source at the existing container target and appends a second mount with a new target.

### .env
Default interpolation source for the base render.

### .env.prod
Explicit interpolation source for the production render.

### .env.runtime
Service-level environment input that would be passed into containers if the stack were started.

### inspect_config.py
Assertions against normalized JSON and profile-aware service lists.

### logical_flow
The shell invokes Docker Compose in the stack directory.
Compose reads interpolation values from .env or the file selected by --env-file.
YAML anchors expand shared service policy.
Later Compose files merge over compose.yaml.
Compose emits a normalized model as JSON.
Python validates services, profiles, ports, environment values, and mount behavior.

### service_relationships
### web
Default service attached to the frontend network. It exposes a loopback-only port in the rendered model.

### worker
Optional service attached to the same network and gated by the ops profile.

### frontend
Internal application network definition present in the static model.

## Required reading

- Docker Docs, Compose file reference: https://docs.docker.com/reference/compose-file/
- Docker Docs, Merge Compose files: https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/
- Docker Docs, Use service profiles: https://docs.docker.com/compose/how-tos/profiles/
- Docker Docs, Variable interpolation: https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
- Docker Docs, Compose extension fields: https://docs.docker.com/reference/compose-file/extension/

## References

- Docker Compose file reference: https://docs.docker.com/reference/compose-file/
- Docker Compose merge rules: https://docs.docker.com/reference/compose-file/merge/
- Docker Compose multiple-file merge guide: https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/
- Docker Compose profiles: https://docs.docker.com/compose/how-tos/profiles/
- Docker Compose interpolation: https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
- Docker Compose environment variable precedence: https://docs.docker.com/compose/how-tos/environment-variables/envvars-precedence/
- Docker Compose extension fields: https://docs.docker.com/reference/compose-file/extension/
- Compose Specification: https://compose-spec.io/

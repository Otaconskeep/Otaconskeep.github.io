# Class 80: Reusable Docker Compose Stack Patterns

**Learning objective:** Create a reusable Compose stack with extension fields and YAML anchors.; Distinguish shell interpolation sources from a service-level env_file.; Use profiles to keep optional services out of the default operational selection.; Explain why a profile-gated service can remain present in the full rendered model while being absent from the default config --services result.; Apply an ordered override file and use !override when a sequence must be replaced rather than merged.; Observe volume sequence behavior when one mount has an existing target and another has a new target.; Validate canonical long-form port fields instead of relying on a particular YAML rendering style.; Use machine-readable Compose output and automated assertions to verify a stack without starting it.
**Bloom level:** Understand / Apply
**Track:** Containers and Service Orchestration · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Teach learners to structure reusable Docker Compose projects with extension fields, YAML anchors, environment interpolation, profiles, layered override files, deterministic replacement, and observable sequence-merge behavior. The lab remains static: learners render and inspect Compose models without starting containers.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_system
Linux host with access to /opt/lab-classroom/class80/

### docker_engine
A current Docker Engine release capable of using the Docker Compose v2 plugin

### docker_compose
v2.24.4 or newer; required for the !override tag and expected config behavior

### python
Python 3.8 or newer

### shell
POSIX-like shell with support for the shown here-documents

### notes
The deprecated top-level version key is intentionally omitted.
Rendered bind-mount source paths may be normalized to absolute paths.
Published values in JSON can be represented as strings; assertions normalize them before comparison.
Service ordering in --services output should not be assumed, so verification compares sets or sorted lines.
No image download is required for docker compose config.

## Learning objective

- Create a reusable Compose stack with extension fields and YAML anchors.
- Distinguish shell interpolation sources from a service-level env_file.
- Use profiles to keep optional services out of the default operational selection.
- Explain why a profile-gated service can remain present in the full rendered model while being absent from the default config --services result.
- Apply an ordered override file and use !override when a sequence must be replaced rather than merged.
- Observe volume sequence behavior when one mount has an existing target and another has a new target.
- Validate canonical long-form port fields instead of relying on a particular YAML rendering style.
- Use machine-readable Compose output and automated assertions to verify a stack without starting it.

## Why this matters

Teach learners to structure reusable Docker Compose projects with extension fields, YAML anchors, environment interpolation, profiles, layered override files, deterministic replacement, and observable sequence-merge behavior. The lab remains static: learners render and inspect Compose models without starting containers.

## Prerequisites

- Comfort using a Linux shell and editing YAML files
- Docker Engine with the Docker Compose v2 plugin installed
- Docker Compose v2.24.4 or newer for the !override YAML tag
- Python 3 for local assertions against rendered JSON
- Write access to /opt/lab-classroom/class80/
- Basic familiarity with services, images, ports, bind mounts, and environment variables

## Required reading

- Docker Docs, Compose file reference: https://docs.docker.com/reference/compose-file/
- Docker Docs, Merge Compose files: https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/
- Docker Docs, Use service profiles: https://docs.docker.com/compose/how-tos/profiles/
- Docker Docs, Variable interpolation: https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
- Docker Docs, Compose extension fields: https://docs.docker.com/reference/compose-file/extension/

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

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

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Add a profile-gated service named diagnostics using a small fixed-tag image, but continue to use config rendering only. Verify that it appears in the full model and only appears in --services when its profile is enabled.
Create compose.dev.yaml that changes LOG_LEVEL to trace without duplicating the complete web service definition. Render and assert the result.
Add a second network in an overlay and observe whether it is appended to the web service network list.
Write a Python assertion that every published port in every rendered model has host_ip set to 127.0.0.1.
Write a short design note explaining when !override communicates intent better than relying on normal uniqueness-based sequence merging.

## Feynman teach-back

### prompt
Explain the stack to another learner without using the words template, magic, or automatic.

### model_explanation
compose.yaml defines the stable application. The x-service-defaults block is reusable YAML content copied into both services through an anchor. Compose then resolves variables and applies later files in command-line order. The worker remains defined but carries the ops profile, so the full rendered model includes it while the default service selection does not. The production overlay uses !override because its port list must replace, not accumulate with, the base port. The mount overlay demonstrates two sequence outcomes: a mount with the same container target changes the existing logical mount, while a mount with a new target is added. JSON output lets us test those meanings without depending on how YAML happens to be printed.

### self_check_questions
Can you explain why env_file does not set WEB_PORT during Compose interpolation?
Can you explain why worker is in rendered.base.json but absent from services.default.txt?
Can you identify which file must appear last to change the production port?
Can you explain why /usr/share/nginx/html changes source while /srv/shared is appended?
Can you justify checking semantic port fields instead of a short port string?

## Retrieval check

1. 1. What is the practical difference between a service-level env_file and a file passed through docker compose --env-file?
2. 2. Why does the full rendered Compose model contain worker while docker compose config --services lists only web by default?
3. 3. What does the !override tag accomplish for the production ports sequence?
4. 4. In the mount experiment, why does /usr/share/nginx/html use site-blue while /srv/shared is also retained?
5. 5. Why is checking host_ip, published, target, and protocol more reliable than searching for a short port string?
6. 6. In what order should compose.yaml and compose.prod.yaml be supplied for the production overlay to take effect?
7. 7. Do Compose profiles provide an authorization boundary for sensitive services?

## Guided lab

### scope_rule
Every file created or changed by these steps is under /opt/lab-classroom/class80/. Do not run docker compose up, start, create, run, or pull during this static lesson.

### steps
### step
1

### title
Confirm tool compatibility and create the isolated workspace

### command
docker compose version
python3 --version
mkdir -p /opt/lab-classroom/class80/stack/site /opt/lab-classroom/class80/stack/site-blue /opt/lab-classroom/class80/stack/shared
cd /opt/lab-classroom/class80/stack

### explanation
Confirm that Docker Compose is v2.24.4 or newer because the production overlay uses !override. All subsequent file mutations remain inside the class workspace.
### step
2

### title
Create harmless bind-mount content

### command
cd /opt/lab-classroom/class80/stack
printf '%s\n' 'class80 base site' > site/index.html
printf '%s\n' 'class80 blue site' > site-blue/index.html
printf '%s\n' 'shared read-only content' > shared/readme.txt

### explanation
The files allow Compose to resolve real bind-mount paths. They are not served because the lab never starts a container.
### step
3

### title
Create interpolation and runtime environment files

### command
cd /opt/lab-classroom/class80/stack
cat > .env <<'EOF'
WEB_PORT=8080
APP_ENV=development
LOG_LEVEL=debug
EOF
cat > .env.prod <<'EOF'
PROD_WEB_PORT=8181
APP_ENV=production
LOG_LEVEL=info
EOF
cat > .env.runtime <<'EOF'
RUNTIME_BANNER=loaded-from-service-env-file
EOF

### explanation
.env and .env.prod participate in Compose interpolation. The service-level .env.runtime is represented in the model as container environment input and does not provide WEB_PORT or PROD_WEB_PORT to Compose interpolation.
### step
4

### title
Create the reusable base stack

### command
cd /opt/lab-classroom/class80/stack
cat > compose.yaml <<'EOF'
name: class80

x-service-defaults: &service-defaults
  restart: unless-stopped
  networks:
    - frontend
  logging:
    driver: json-file
    options:
      max-size: "10m"
      max-file: "3"

services:
  web:
    <<: *service-defaults
    image: nginx:1.27-alpine
    env_file:
      - .env.runtime
    environment:
      APP_ENV: "${APP_ENV:-development}"
      LOG_LEVEL: "${LOG_LEVEL:-info}"
    ports:
      - target: 80
        published: "${WEB_PORT:-8080}"
        host_ip: 127.0.0.1
        protocol: tcp
    volumes:
      - type: bind
        source: ./site
        target: /usr/share/nginx/html
        read_only: true
    labels:
      academy.class: "80"
      academy.role: web

  worker:
    <<: *service-defaults
    image: busybox:1.36
    profiles:
      - ops
    command:
      - sh
      - -c
      - while true; do sleep 3600; done
    environment:
      APP_ENV: "${APP_ENV:-development}"
    labels:
      academy.class: "80"
      academy.role: worker

networks:
  frontend:
    name: class80_frontend
EOF

### explanation
The x-service-defaults extension and YAML anchor centralize restart, network, and logging policy. The worker remains in the application model but is operationally gated by the ops profile.
### step
5

### title
Create an explicit production replacement overlay

### command
cd /opt/lab-classroom/class80/stack
cat > compose.prod.yaml <<'EOF'
services:
  web:
    environment:
      APP_ENV: "${APP_ENV:-production}"
    ports: !override
      - target: 80
        published: "${PROD_WEB_PORT:-8181}"
        host_ip: 127.0.0.1
        protocol: tcp
EOF

### explanation
The !override tag replaces the complete inherited port sequence. The rendered production model should contain the loopback port published as 8181 and should not retain 8080.
### step
6

### title
Create a mount merge experiment

### command
cd /opt/lab-classroom/class80/stack
cat > compose.mounts.yaml <<'EOF'
services:
  web:
    volumes:
      - type: bind
        source: ./site-blue
        target: /usr/share/nginx/html
        read_only: true
      - type: bind
        source: ./shared
        target: /srv/shared
        read_only: true
EOF

### explanation
The first mount has the same container target as the base mount, so it represents the same unique resource and changes its source to site-blue. The second mount has a new target and is appended. Rendering the merged model makes both outcomes observable.
### step
7

### title
Render normalized models without starting services

### command
cd /opt/lab-classroom/class80/stack
docker compose -f compose.yaml config --format json > rendered.base.json
docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml config --format json > rendered.prod.json
docker compose -f compose.yaml -f compose.mounts.yaml config --format json > rendered.mounts.json
docker compose -f compose.yaml config --services > services.default.txt
docker compose --profile ops -f compose.yaml config --services > services.ops.txt

### explanation
The full JSON render includes the worker definition. The default --services selection excludes worker because its profile is inactive, while the profile-enabled selection includes it.
### step
8

### title
Inspect canonical long-form port semantics

### command
cd /opt/lab-classroom/class80/stack
python3 - <<'PY'
import json
for filename in ('rendered.base.json', 'rendered.prod.json'):
    with open(filename, encoding='utf-8') as handle:
        model = json.load(handle)
    print(filename)
    for port in model['services']['web']['ports']:
        print({
            'host_ip': port.get('host_ip'),
            'published': str(port.get('published')),
            'target': int(port.get('target')),
            'protocol': port.get('protocol', 'tcp')
        })
PY

### explanation
This verifies semantic fields instead of looking for short YAML strings. Normalization is allowed to change representation while preserving port meaning.
### step
9

### title
Create automated model assertions

### command
cd /opt/lab-classroom/class80/stack
cat > inspect_config.py <<'PY'
import json
from pathlib import Path

ROOT = Path('/opt/lab-classroom/class80/stack')

def load(name):
    with (ROOT / name).open(encoding='utf-8') as handle:
        return json.load(handle)

def service_lines(name):
    return {
        line.strip()
        for line in (ROOT / name).read_text(encoding='utf-8').splitlines()
        if line.strip()
    }

def normalized_ports(model):
    result = set()
    for port in model['services']['web'].get('ports', []):
        result.add((
            str(port.get('host_ip')),
            str(port.get('published')),
            int(port.get('target')),
            str(port.get('protocol', 'tcp')),
        ))
    return result

def volume_by_target(model):
    return {
        volume['target']: volume
        for volume in model['services']['web'].get('volumes', [])
    }

base = load('rendered.base.json')
prod = load('rendered.prod.json')
mounts = load('rendered.mounts.json')

assert set(base['services']) == {'web', 'worker'}, base['services'].keys()
assert base['services']['worker']['profiles'] == ['ops']
assert service_lines('services.default.txt') == {'web'}
assert service_lines('services.ops.txt') == {'web', 'worker'}

assert normalized_ports(base) == {('127.0.0.1', '8080', 80, 'tcp')}
assert normalized_ports(prod) == {('127.0.0.1', '8181', 80, 'tcp')}
assert prod['services']['web']['environment']['APP_ENV'] == 'production'

base_volumes = volume_by_target(base)
merged_volumes = volume_by_target(mounts)
assert set(base_volumes) == {'/usr/share/nginx/html'}
assert set(merged_volumes) == {'/usr/share/nginx/html', '/srv/shared'}
assert str(base_volumes['/usr/share/nginx/html']['source']).endswith('/site')
assert str(merged_volumes['/usr/share/nginx/html']['source']).endswith('/site-blue')
assert str(merged_volumes['/srv/shared']['source']).endswith('/shared')
assert merged_volumes['/usr/share/nginx/html'].get('read_only') is True
assert merged_volumes['/srv/shared'].get('read_only') is True

print('PASS: base model contains web and profile-gated worker')
print('PASS: default service selection is web only')
print('PASS: ops service selection contains web and worker')
print('PASS: base port is 127.0.0.1:8080 -> 80/tcp')
print('PASS: production !override leaves only 127.0.0.1:8181 -> 80/tcp')
print('PASS: same-target mount changed to site-blue and new-target mount was appended')
PY
python3 inspect_config.py

### explanation
The assertions validate model inclusion separately from profile-aware service selection. They also validate long-form ports and directly demonstrate same-target replacement versus new-target append behavior for mounts.
### step
10

### title
Review the effective differences

### command
cd /opt/lab-classroom/class80/stack
python3 - <<'PY'
import json
from pathlib import Path
root = Path('/opt/lab-classroom/class80/stack')
for name in ('rendered.base.json', 'rendered.prod.json', 'rendered.mounts.json'):
    model = json.loads((root / name).read_text(encoding='utf-8'))
    web = model['services']['web']
    print(f'[{name}]')
    print('services:', ', '.join(sorted(model['services'])))
    print('ports:', web.get('ports', []))
    print('volumes:', web.get('volumes', []))
    print('environment:', web.get('environment', {}))
PY

### explanation
The final review shows that reuse and overlays produce small, explainable changes in the effective model.

## Expected results

- rendered.base.json contains both web and worker because the full Compose model retains profile-gated service definitions.
- services.default.txt contains only web because the ops profile is not enabled for the --services query.
- services.ops.txt contains web and worker because the ops profile is enabled.
- The normalized base web port has host_ip 127.0.0.1, published 8080, target 80, and protocol tcp.
- The normalized production web port has host_ip 127.0.0.1, published 8181, target 80, and protocol tcp.
- The production port list contains only the 8181 mapping because !override replaces the base sequence.
- The production web environment contains APP_ENV set to production.
- The base model mounts site at /usr/share/nginx/html.
- The mount experiment changes the source for /usr/share/nginx/html to site-blue and appends shared at /srv/shared.
- inspect_config.py prints six PASS lines and exits successfully.
- No container, network, or image pull is created by the prescribed lab steps.

## Verification checkpoints

- [ ] Run: cd /opt/lab-classroom/class80/stack && docker compose -f compose.yaml config --quiet. Expected: exit status 0 with no validation error.
- [ ] Run: cd /opt/lab-classroom/class80/stack && docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml config --quiet. Expected: exit status 0.
- [ ] Run: cd /opt/lab-classroom/class80/stack && docker compose -f compose.yaml -f compose.mounts.yaml config --quiet. Expected: exit status 0.
- [ ] Run: cd /opt/lab-classroom/class80/stack && python3 inspect_config.py. Expected: all six PASS messages and exit status 0.
- [ ] Run: cd /opt/lab-classroom/class80/stack && cat services.default.txt. Expected: web only; worker must not appear because ops is inactive.
- [ ] Run: cd /opt/lab-classroom/class80/stack && sort services.ops.txt. Expected: one line for web and one line for worker.
- [ ] Inspect rendered.base.json. Expected: services contains both web and worker even though services.default.txt contains only web.
- [ ] Inspect the ports array in rendered.base.json. Expected semantic tuple: host_ip=127.0.0.1, published=8080, target=80, protocol=tcp.
- [ ] Inspect the ports array in rendered.prod.json. Expected semantic tuple: host_ip=127.0.0.1, published=8181, target=80, protocol=tcp, with no retained 8080 entry.
- [ ] Inspect rendered.mounts.json. Expected: exactly one mount targeting /usr/share/nginx/html with a source ending in /site-blue, plus a mount targeting /srv/shared with a source ending in /shared.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Compose reports that !override is an unknown tag. | The installed Docker Compose plugin predates v2.24.4. | Upgrade the Docker Compose v2 plugin to v2.24.4 or newer, confirm with docker compose version, and rerun the production render. |
| services.default.txt contains worker. | The ops profile was enabled through a command option or the COMPOSE_PROFILES environment variable. | Run the exact default command from the lab without --profile and with COMPOSE_PROFILES unset for that invocation: env -u COMPOSE_PROFILES docker compose -f compose.yaml config --services > services.default.txt. |
| services.default.txt contains only web, but the learner expected worker too. | The learner is confusing full model inclusion with profile-aware service selection. | Treat web-only output as correct for the default --services query. Inspect rendered.base.json to confirm worker remains in the full model, then run docker compose --profile ops -f compose.yaml config --services to include it in the service selection. |
| The base port is not published as 8080. | A shell variable named WEB_PORT is overriding the value in .env. | Inspect the invoking environment with printenv WEB_PORT. Run the render from a shell where WEB_PORT is unset, or deliberately pass --env-file .env and document the intended precedence. |
| The production model still contains the 8080 port. | The production file omitted !override, was not supplied after the base file, or the learner inspected an older rendered file. | Confirm that compose.prod.yaml uses ports: !override, place it after compose.yaml in the command, regenerate rendered.prod.json, and rerun inspect_config.py. |
| A check for 127.0.0.1:8080:80 or 127.0.0.1:8181:80 fails even though the model looks correct. | The check assumes short port syntax, while Compose normalized ports into long-form objects. | Use config --format json and inspect host_ip, published, target, and protocol as separate semantic fields. |
| The mount experiment still points /usr/share/nginx/html at site. | compose.mounts.yaml was omitted, placed before compose.yaml, or the rendered file was not regenerated. | Run docker compose -f compose.yaml -f compose.mounts.yaml config --format json > rendered.mounts.json and rerun inspect_config.py. |
| The rendered source paths are absolute rather than ./site or ./site-blue. | Compose normalized relative bind paths against the first Compose file's directory. | This is expected. Compare the end of the normalized path or use pathlib rather than requiring the original relative spelling. |
| Compose reports that a bind source does not exist. | One or more of site, site-blue, or shared was not created in the stack directory. | Recreate the missing directory under /opt/lab-classroom/class80/stack and repeat the render. |
| inspect_config.py reports a service-set assertion failure. | The source files were edited, a different working copy was rendered, or stale JSON files are being inspected. | Confirm the absolute workspace path, regenerate every rendered JSON file using the lab commands, and rerun the script. |

## Security considerations

### principles
The lab performs static rendering only and does not start unreviewed images.
Published ports bind to 127.0.0.1 rather than every host interface.
Bind mounts are read-only in the Compose model.
No secrets are stored in the example environment files.
Runtime environment files should not be mistaken for secret-management systems.
Pinned image tags are clearer than floating latest tags, although production environments may additionally pin immutable digests.
Profiles reduce accidental activation of optional services but are not an authorization boundary.
Rendered configuration can expose interpolated values, so real secret-bearing output should be handled as sensitive data.

### review_checks
Review every overlay in file order because later files can materially change earlier policy.
Confirm that replacement tags are intentional and supported by the deployed Compose version.
Inspect normalized host_ip values before approving published ports.
Check bind sources and targets to ensure a later overlay does not expose an unintended host path.
Keep project names explicit to reduce the chance of operating on an unrelated Compose project.

## Rollback

### static_lab_cleanup
The lesson does not require cleanup for correctness because all generated files remain inside /opt/lab-classroom/class80/.

### idempotent_disable
cd /opt/lab-classroom/class80 && if [ -d stack ] && [ ! -e stack.disabled ]; then mv stack stack.disabled; elif [ -d stack ] && [ -e stack.disabled ]; then printf '%s\n' 'Both stack and stack.disabled exist; no rename performed.'; else printf '%s\n' 'No active stack directory to disable.'; fi

### idempotent_restore
cd /opt/lab-classroom/class80 && if [ -d stack.disabled ] && [ ! -e stack ]; then mv stack.disabled stack; elif [ -d stack.disabled ] && [ -e stack ]; then printf '%s\n' 'Both stack and stack.disabled exist; no rename performed.'; else printf '%s\n' 'No disabled stack directory to restore.'; fi

### collision_behavior
The disable and restore commands refuse to overwrite an existing destination. If both directories exist, compare them and resolve the collision manually while remaining under /opt/lab-classroom/class80/.

### optional_runtime_cleanup
The prescribed lab never starts the project. Only if a learner independently started it, change to /opt/lab-classroom/class80/stack and run docker compose --profile ops down --remove-orphans after verifying the project name is class80. This removes project runtime resources and is not part of the normal static workflow.

## Video narration notes

Begin by showing the isolated workspace and emphasize that this is a static-rendering lab: no container will be started. Introduce compose.yaml as the stable layer and point to x-service-defaults. Explain that the YAML anchor removes repeated logging, restart, and network settings, but that anchors are a YAML feature resolved before Compose performs file merging. Next, compare .env, .env.prod, and .env.runtime. Stress that interpolation happens while Compose reads the files, whereas env_file supplies values to a future container.

Render the base model as JSON. Show that both web and worker exist under services. Then display services.default.txt, which contains only web. Enable the ops profile and show that services.ops.txt contains both services. Pause to explain that model inclusion and operational selection are separate questions.

Open compose.prod.yaml and highlight ports: !override. Explain that production requires one deliberate loopback mapping, not a sequence accidentally accumulated from multiple layers. Inspect the normalized JSON fields rather than searching for a short string. The relevant facts are host_ip 127.0.0.1, published 8181, target 80, and protocol tcp.

Finally, render compose.mounts.yaml. Compare the base and merged volume arrays. The existing /usr/share/nginx/html target now uses site-blue, while /srv/shared is added as a second mount. Run inspect_config.py and connect each PASS line to a learning objective. Close by explaining that reusable stacks are trustworthy when their merge behavior is explicit, rendered output is reviewable, and assertions test meaning rather than formatting.

## References

- Docker Compose file reference: https://docs.docker.com/reference/compose-file/
- Docker Compose merge rules: https://docs.docker.com/reference/compose-file/merge/
- Docker Compose multiple-file merge guide: https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/
- Docker Compose profiles: https://docs.docker.com/compose/how-tos/profiles/
- Docker Compose interpolation: https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
- Docker Compose environment variable precedence: https://docs.docker.com/compose/how-tos/environment-variables/envvars-precedence/
- Docker Compose extension fields: https://docs.docker.com/reference/compose-file/extension/
- Compose Specification: https://compose-spec.io/

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

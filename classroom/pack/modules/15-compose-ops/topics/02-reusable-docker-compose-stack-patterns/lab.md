# Lab: Reusable Docker Compose Stack Patterns

**Module:** Compose Operations & IaC
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Create a reusable Compose stack with extension fields and YAML anchors.

## Before you start

- Comfort using a Linux shell and editing YAML files
- Docker Engine with the Docker Compose v2 plugin installed
- Docker Compose v2.24.4 or newer for the !override YAML tag
- Python 3 for local assertions against rendered JSON
- Write access to /opt/lab-classroom/class80/
- Basic familiarity with services, images, ports, bind mounts, and environment variables

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

## Verification

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

## Security

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

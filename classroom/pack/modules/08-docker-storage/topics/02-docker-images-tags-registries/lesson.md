# Lesson 08.02: Docker Images, Tags, Registries, and Provenance

**Module:** Module 8: Docker, Storage & Permissions
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** By the end, you can explain image layers, repositories, tags, manifests, registries, image IDs, and digests; inspect a local image; distinguish convenient naming from immutable identity; and record enough provenance to reproduce or investigate a deployment.

## Learning objective

By the end, you can explain image layers, repositories, tags, manifests, registries, image IDs, and digests; inspect a local image; distinguish convenient naming from immutable identity; and record enough provenance to reproduce or investigate a deployment.

## Why this matters

`app:latest` tells an operator what someone called an image, not exactly which content ran. Tags can move. Registries can be compromised. Architectures can resolve to different manifests. A homelab that records registry, repository, tag, digest, source, and update decision can roll forward deliberately and roll back to known content.

## Prior-knowledge check

1. What is the difference between an image and a running container?
2. What do you think `:latest` guarantees?
3. Where would you look to determine which image a running container uses?

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Guided practice (We do)

### Build and Inspect a Network-Free Image

### Safety and prerequisites

- Use a non-production Docker host.
- Commands create only `/opt/lab-classroom/class28/` and a local image named `academy-c28:1.0`.
- No registry login or network pull is required.
- Confirm Docker access is authorized; Docker socket access is host-administrative.

```bash
LAB=/opt/lab-classroom/class28
sudo install -d -o "$(id -u)" -g "$(id -g)" "$LAB"
printf 'Homelab Academy Class 28\n' > "$LAB/proof.txt"
printf '%s\n' \
  'FROM scratch' \
  'LABEL org.opencontainers.image.title="academy-c28"' \
  'LABEL org.opencontainers.image.source="Homelab Academy Class 28"' \
  'COPY proof.txt /proof.txt' \
  > "$LAB/Dockerfile"
docker build --pull=false -t academy-c28:1.0 "$LAB"
docker image inspect academy-c28:1.0 > "$LAB/image-inspect.json"
docker image history --no-trunc academy-c28:1.0 | tee "$LAB/image-history.txt"
docker image ls --no-trunc academy-c28:1.0
```

### Verification checkpoints

```bash
test -s "$LAB/image-inspect.json" && echo 'PASS: inspection captured'
docker image inspect academy-c28:1.0 --format '{{ index .Config.Labels "org.opencontainers.image.title" }}'
docker image inspect academy-c28:1.0 --format 'ID={{.Id}} Created={{.Created}}'
sha256sum "$LAB/Dockerfile" "$LAB/proof.txt" | tee "$LAB/source-sha256.txt"
```

Expected: the label prints `academy-c28`; the image ID begins with `sha256:`; source hashes are recorded. A locally built image normally has no registry digest until pushed/pulled through a registry.

## Feynman teach-back (required)

Explain to a beginner why a tag is like a movable label while a digest is like a fingerprint. Then explain why a fingerprint still does not tell you whether the producer or build process should be trusted.

## Reflection

What image identity information does your current homelab record, and what would you need during a supply-chain incident?

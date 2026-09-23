# Lab — Docker Images, Tags, Registries, and Provenance

**Module:** Module 8 — Docker, Storage & Permissions
**Activity type:** Lab (Practice)
**Objective:** By the end, you can explain image layers, repositories, tags, manifests, registries, image IDs, and digests; inspect a local image; distinguish convenient naming from immutable identity; and record enough provenance to reproduce or investigate a deployment.

## Guided practice

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

## Security and Rollback

- Treat registries and build pipelines as supply-chain trust boundaries.
- Never expose `/var/run/docker.sock` to an untrusted container.
- Prefer immutable digests for promoted deployments while preserving a human-readable tag in documentation.
- Keep secrets out of layers; deleting a later layer does not erase a secret from earlier history.

Rollback removes only the labeled lab image after confirming no dependent container exists:

```bash
docker ps -a --filter ancestor=academy-c28:1.0
docker image rm academy-c28:1.0
```

Preserve `/opt/lab-classroom/class28/` until evidence is graded; remove it later only with an explicitly reviewed path.

## Troubleshooting

| Symptom | Likely cause | Safe response |
|---|---|---|
| Cannot connect to Docker | Daemon stopped, wrong context, or unauthorized socket access | Check `docker context show`, service status, and approved access; do not loosen socket permissions |
| Build tries to reach a registry | Dockerfile base is not `scratch` or BuildKit behavior differs | Recheck the exact Dockerfile and retain `--pull=false` |
| `RepoDigests` is empty | Image was built locally and not associated with a registry manifest | Record image ID and source hashes; do not invent a digest |
| Architecture differs | Tag resolved through a multi-platform manifest | Record platform and platform-specific digest |

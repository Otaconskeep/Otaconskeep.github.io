# Lab — PUID, PGID, ACLs, and Container File Access

**Module:** Module 8 — Docker, Storage & Permissions
**Activity type:** Lab (Practice)
**Objective:** Explain numeric UID/GID identity across host and containers; distinguish mode bits from ACLs; diagnose bind-mount access failures; test access using an explicit container user; and design least-privilege ownership without using world-writable shortcuts.

## Guided practice

### Prove Allowed and Denied Writes

### Safety and prerequisites

- Authorized Docker host with `busybox:1.36.1` cached from earlier labs or approved for pull.
- Uses only `/opt/lab-classroom/class33/`.
- Does not create users, recursively change ownership, or use `777`.

```bash
LAB=/opt/lab-classroom/class33
sudo install -d -o "$(id -u)" -g "$(id -g)" -m 0750 "$LAB/shared"
printf 'host-created\n' > "$LAB/shared/host.txt"
chmod 0640 "$LAB/shared/host.txt"
id | tee "$LAB/host-identity.txt"
ls -ldn "$LAB" "$LAB/shared" | tee "$LAB/numeric-directories.txt"
ls -ln "$LAB/shared/host.txt" | tee "$LAB/numeric-file.txt"
docker run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$LAB/shared":/data \
  busybox:1.36.1 sh -c 'id; printf "matching-id-write\n" > /data/matching.txt; cat /data/host.txt'
if docker run --rm \
  --user 65534:65534 \
  -v "$LAB/shared":/data \
  busybox:1.36.1 sh -c 'printf "unexpected\n" > /data/denied.txt'; then
  echo 'FAIL: unrelated identity unexpectedly wrote'
  exit 1
else
  echo 'PASS: unrelated identity denied as expected'
fi
ls -ln "$LAB/shared" | tee "$LAB/after-tests.txt"
```

Optional ACL observation, without broadening access:

```bash
if command -v getfacl >/dev/null 2>&1; then getfacl -p "$LAB/shared" | tee "$LAB/shared.acl.txt"; else echo 'SKIP: getfacl unavailable'; fi
```

### Verification checkpoints

```bash
test -f "$LAB/shared/matching.txt" && echo 'PASS: matching numeric identity wrote'
test ! -e "$LAB/shared/denied.txt" && echo 'PASS: denied write left no file'
test "$(stat -c %a "$LAB/shared")" = 750 && echo 'PASS: directory not world-writable'
stat -c 'uid=%u gid=%g mode=%a path=%n' "$LAB/shared" "$LAB/shared/matching.txt"
```

## Security and Rollback

- Prefer non-root container processes and the smallest required access.
- Avoid recursive `chown` on large or shared datasets without an inventory and rollback plan.
- Do not use world-writable permissions as a diagnostic shortcut.
- Treat Docker socket access as host administration regardless of file ownership lesson goals.
- Back up ACLs with `getfacl -R` before approved ACL changes and restore with `setfacl --restore` when appropriate.

Lab rollback removes only files created inside the verified class directory:

```bash
LAB=/opt/lab-classroom/class33
test -d "$LAB/shared" && test "$LAB" = /opt/lab-classroom/class33 && rm -f -- "$LAB/shared/matching.txt" "$LAB/shared/denied.txt" "$LAB/shared/host.txt"
rmdir -- "$LAB/shared" 2>/dev/null || true
```

## Troubleshooting

| Symptom | Likely cause | Safe response |
|---|---|---|
| Correct-looking username still denied | Numeric UID/GID mismatch | Compare `id` and `ls -ln`; trust numbers |
| File mode allows group, process denied | Process lacks group or ACL mask restricts | Inspect supplementary groups and `getfacl` |
| Directory listing works but file open fails | File-specific mode/ACL or read-only mount | Inspect the exact file and mount, not just parent |
| Works as root only | Root bypass/capability masks underlying design | Restore non-root execution and correct ownership/access narrowly |
| New files differ from old files | umask, default ACL, or application creation behavior | Inspect defaults and one newly created file |
| NAS path behaves differently | NFS/CIFS identity mapping or server-side ACL | Inspect mount options and server policy before host chmod/chown |

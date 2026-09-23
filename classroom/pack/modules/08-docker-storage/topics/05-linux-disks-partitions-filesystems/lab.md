# Lab — Linux Disks, Partitions, and Filesystems

**Module:** Module 8 — Docker, Storage & Permissions
**Activity type:** Lab (Practice)
**Objective:** Trace the hierarchy from physical or virtual disk to partition table, partition, filesystem, and mountpoint; interpret `lsblk`, `blkid`, `findmnt`, and `df`; create a filesystem only inside a regular lab image file; and recognize destructive storage operations before running them.

## Guided practice

### Safe Filesystem Image

### Safety and prerequisites

- Requires `truncate`, `mkfs.ext4`, and preferably `blkid`/`dumpe2fs`.
- The target must remain exactly `/opt/lab-classroom/class31/academy-c31.img`.
- Do not substitute any `/dev/*` path.

```bash
LAB=/opt/lab-classroom/class31
sudo install -d -o "$(id -u)" -g "$(id -g)" "$LAB"
lsblk -o NAME,TYPE,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINTS | tee "$LAB/lsblk-before.txt"
findmnt --real | tee "$LAB/findmnt-before.txt"
df -hT | tee "$LAB/df-before.txt"
truncate -s 128M "$LAB/academy-c31.img"
test -f "$LAB/academy-c31.img" && test ! -b "$LAB/academy-c31.img" || { echo 'REFUSE: target boundary failed'; exit 1; }
mkfs.ext4 -F -L ACADEMY31 "$LAB/academy-c31.img"
file "$LAB/academy-c31.img" | tee "$LAB/file-signature.txt"
blkid "$LAB/academy-c31.img" | tee "$LAB/blkid.txt"
dumpe2fs -h "$LAB/academy-c31.img" 2>/dev/null | sed -n '1,35p' | tee "$LAB/ext4-header.txt"
```

### Verification checkpoints

```bash
grep -F 'ext4 filesystem data' "$LAB/file-signature.txt"
grep -F 'LABEL="ACADEMY31"' "$LAB/blkid.txt"
grep -F 'TYPE="ext4"' "$LAB/blkid.txt"
test "$(stat -c %s "$LAB/academy-c31.img")" -eq 134217728 && echo 'PASS: bounded 128 MiB image'
```

Expected: the regular file contains an ext4 filesystem with label `ACADEMY31`; no physical block device is modified or mounted.

## Security and Rollback

- Storage inventories can reveal infrastructure identifiers; redact before publishing.
- Untrusted removable media may contain hostile filesystems; mount with policy-appropriate restrictions and avoid automatic execution.
- Encryption protects data at rest only when keys and recovery materials are managed securely.

Rollback is deleting only the regular lab image after verifying the boundary:

```bash
LAB=/opt/lab-classroom/class31
test -f "$LAB/academy-c31.img" && test ! -b "$LAB/academy-c31.img" && rm -- "$LAB/academy-c31.img"
test ! -e "$LAB/academy-c31.img" && echo 'PASS: lab image removed'
```

## Troubleshooting

| Symptom | Likely cause | Safe response |
|---|---|---|
| `mkfs.ext4` missing | Filesystem utilities absent | Stop and document the prerequisite; do not install packages automatically |
| `blkid` prints nothing | Tool/permission/signature probing difference | Use `file` and `dumpe2fs -h`; preserve the image for review |
| `lsblk` shows unexpected topology | LVM, RAID, encryption, loop, or virtualization layer | Map every layer before any change |
| `df` full but `du` smaller | Deleted-open files or hidden/mounted data | Inspect mounts and open deleted files; do not delete random directories |
| Boundary test fails | Target changed or became a block device | Stop immediately; never continue with `mkfs` |

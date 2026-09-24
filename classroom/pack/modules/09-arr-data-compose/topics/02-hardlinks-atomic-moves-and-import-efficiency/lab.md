# Lab: Hardlinks, Atomic Moves, and Import Efficiency

**Module:** ARR Data Model & Compose
**Activity type:** Lab (Practice)
**Lab risk:** medium
**Objective:** Explain the relationship between a pathname, directory entry, inode, and file data.

## Before you start

- Comfort using a Linux shell and absolute paths.
- Basic familiarity with files, directories, inodes, mounts, and permissions.
- Ability to run commands with sufficient permission to create files under /opt/lab-classroom/class35/.
- Familiarity with common commands such as stat, mv, ln, find, sha256sum, and findmnt.

## Guided lab

### title
Build and Verify a Same-Filesystem Import Pipeline

### notes
Run the commands in a Bash-compatible shell on a Linux host.
The reset step deletes only descendants of the fixed classroom directory.
Do not substitute another path into the reset command.
Record output from stat and sha256sum so the relationships can be explained after the lab.

### steps
### step
1

### name
Prepare an isolated workspace

### commands
test -d /opt/lab-classroom || { printf '%s\n' 'Required classroom parent is missing.' >&2; exit 1; }
mkdir -p /opt/lab-classroom/class35
find /opt/lab-classroom/class35 -mindepth 1 -delete
mkdir -p /opt/lab-classroom/class35/incoming /opt/lab-classroom/class35/library /opt/lab-classroom/class35/work

### explanation
The fixed root prevents accidental operation on unrelated data. The incoming, library, and work directories are descendants of the same intended lab root.
### step
2

### name
Create and inspect a completed source file

### commands
ROOT=/opt/lab-classroom/class35; printf 'class35-media-payload\nsegment-two\n' > "$ROOT/incoming/episode.bin"
stat -c 'path=%n device=%d inode=%i links=%h size=%s blocks=%b' /opt/lab-classroom/class35/incoming/episode.bin
sha256sum /opt/lab-classroom/class35/incoming/episode.bin
findmnt -T /opt/lab-classroom/class35/incoming/episode.bin -o TARGET,SOURCE,FSTYPE,OPTIONS

### explanation
This establishes the source inode, integrity hash, and filesystem placement before import.
### step
3

### name
Create a hardlinked library name

### commands
ln /opt/lab-classroom/class35/incoming/episode.bin /opt/lab-classroom/class35/library/episode.bin
stat -c 'path=%n device=%d inode=%i links=%h size=%s blocks=%b' /opt/lab-classroom/class35/incoming/episode.bin /opt/lab-classroom/class35/library/episode.bin
sha256sum /opt/lab-classroom/class35/incoming/episode.bin /opt/lab-classroom/class35/library/episode.bin

### explanation
Both paths should report the same device and inode. Their hashes should match, and the shared inode's link count should reflect both names.
### step
4

### name
Prove that hardlinks share mutable content

### commands
ROOT=/opt/lab-classroom/class35; printf 'shared-update\n' >> "$ROOT/library/episode.bin"
tail -n 1 /opt/lab-classroom/class35/incoming/episode.bin
stat -c 'path=%n inode=%i links=%h size=%s' /opt/lab-classroom/class35/incoming/episode.bin /opt/lab-classroom/class35/library/episode.bin

### explanation
Appending through the library name changes the common inode, so the incoming name exposes the same appended bytes. This is why hardlinks are not independent backups.
### step
5

### name
Demonstrate atomic replacement and existing readers

### commands
ROOT=/opt/lab-classroom/class35; printf 'version-one\n' > "$ROOT/library/current.txt"; exec 3<"$ROOT/library/current.txt"; printf 'version-two\n' > "$ROOT/work/current.next"; printf 'before='; stat -c '%i' "$ROOT/library/current.txt"; mv -T "$ROOT/work/current.next" "$ROOT/library/current.txt"; printf 'after='; stat -c '%i' "$ROOT/library/current.txt"; IFS= read -r held <&3; exec 3<&-; printf 'held_reader=%s\n' "$held"; printf 'fresh_reader='; cat "$ROOT/library/current.txt"

### explanation
The open descriptor remains attached to the old inode and reads version-one, while a fresh lookup of the final pathname reads version-two. The replacement changes the directory entry rather than rewriting the old inode in place.
### step
6

### name
Publish through a temporary destination hardlink

### commands
ROOT=/opt/lab-classroom/class35; printf 'completed-movie-payload\n' > "$ROOT/incoming/movie.bin"; ln "$ROOT/incoming/movie.bin" "$ROOT/library/.movie.bin.import"; mv -T "$ROOT/library/.movie.bin.import" "$ROOT/library/movie.bin"
stat -c 'path=%n device=%d inode=%i links=%h size=%s' /opt/lab-classroom/class35/incoming/movie.bin /opt/lab-classroom/class35/library/movie.bin
sha256sum /opt/lab-classroom/class35/incoming/movie.bin /opt/lab-classroom/class35/library/movie.bin
test /opt/lab-classroom/class35/incoming/movie.bin -ef /opt/lab-classroom/class35/library/movie.bin && printf '%s\n' 'PASS: source and published path identify the same file'

### explanation
The hidden temporary name is created inside the destination directory and is then renamed to the final name. The source remains available while the destination gains an efficient second name.
### step
7

### name
Run final assertions

### commands
test "$(stat -c '%d:%i' /opt/lab-classroom/class35/incoming/episode.bin)" = "$(stat -c '%d:%i' /opt/lab-classroom/class35/library/episode.bin)" && printf '%s\n' 'PASS: episode paths share device and inode'
test "$(sha256sum /opt/lab-classroom/class35/incoming/movie.bin | awk '{print $1}')" = "$(sha256sum /opt/lab-classroom/class35/library/movie.bin | awk '{print $1}')" && printf '%s\n' 'PASS: movie hashes match'
test ! -e /opt/lab-classroom/class35/library/.movie.bin.import && printf '%s\n' 'PASS: temporary publication name is absent'
test "$(cat /opt/lab-classroom/class35/library/current.txt)" = 'version-two' && printf '%s\n' 'PASS: final pathname resolves to the replacement'

### explanation
These assertions test identity, integrity, temporary-name cleanup, and final publication state without relying on timing measurements.

## Expected results

- The incoming and library episode paths report identical device and inode values after hardlink creation.
- The episode inode reports multiple links while both directory entries exist.
- Appending through the library episode path is visible through the incoming episode path.
- The held file descriptor reads version-one after current.txt has been replaced.
- A fresh lookup of library/current.txt reads version-two after the replacement.
- The incoming and library movie paths identify the same file and produce identical SHA-256 hashes.
- The temporary .movie.bin.import pathname is absent after successful publication.
- No performance number is expected or asserted; the lab verifies filesystem identity and behavior rather than presenting a benchmark.

## Verification

- [ ] Run: stat -c 'path=%n device=%d inode=%i links=%h size=%s' /opt/lab-classroom/class35/incoming/episode.bin /opt/lab-classroom/class35/library/episode.bin
- [ ] Run: test /opt/lab-classroom/class35/incoming/episode.bin -ef /opt/lab-classroom/class35/library/episode.bin && echo PASS
- [ ] Run: test /opt/lab-classroom/class35/incoming/movie.bin -ef /opt/lab-classroom/class35/library/movie.bin && echo PASS
- [ ] Run: sha256sum /opt/lab-classroom/class35/incoming/movie.bin /opt/lab-classroom/class35/library/movie.bin and confirm that both displayed hashes are identical.
- [ ] Run: test ! -e /opt/lab-classroom/class35/library/.movie.bin.import && echo PASS
- [ ] Run: test "$(cat /opt/lab-classroom/class35/library/current.txt)" = 'version-two' && echo PASS
- [ ] Run: findmnt -T /opt/lab-classroom/class35/incoming/movie.bin and findmnt -T /opt/lab-classroom/class35/library/movie.bin; confirm that the paths resolve to the intended shared filesystem.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The ln command reports an invalid cross-device link. | The source and destination resolve to different filesystems even if their pathnames appear close together. | Compare stat device values and inspect both paths with findmnt. Place the incoming and library directories on the same filesystem for hardlink imports, or use a deliberately managed copy workflow. |
| The ln command reports that the destination already exists. | A prior run or interrupted import left the intended destination or temporary name in place. | Inspect the existing entry, compare its inode and hash, and apply an explicit collision policy. Reset only the classroom directory if its contents are disposable. |
| The source and destination hashes match but inode numbers differ. | The file was copied rather than hardlinked, or one pathname was later replaced with a new inode. | Compare device and inode values with stat. Recreate the test from a clean lab directory and use ln without symbolic-link options. |
| Editing one hardlinked path unexpectedly changes the other path. | Both names refer to the same inode, which is the defined behavior of hardlinks. | Treat imported payloads as immutable. If independent modification is required, create a deliberate copy or replace one path with a separately generated file. |
| The move appears to copy data instead of completing immediately as a metadata operation. | The source and destination are on different filesystems, so the utility cannot use one direct rename operation. | Inspect filesystem identity before moving. Create the publication temporary file inside the destination filesystem, then rename it to the final destination there. |
| Permission is denied while creating the hardlink or renaming the temporary entry. | The current account lacks directory write and search permissions, or a filesystem policy prevents hardlink creation. | Inspect directory ownership, mode bits, mount options, and applicable mandatory access controls. Grant only the minimum access required for the classroom path. |
| The reported link count is higher than expected. | Additional hardlinks to the inode exist elsewhere on the same filesystem. | Review the lab commands and search only within the controlled classroom tree using inode-aware find options. Do not assume that two visible names are the only links. |

## Security

### principles
Use a fixed, validated root directory before performing cleanup or publication operations.
Grant import services write access only to the directories where they must create or rename entries.
Treat user-supplied destination names as untrusted and reject path traversal, unexpected separators, and reserved names.
Use unique temporary names when concurrent import workers may publish into the same directory.
Define whether an existing destination must cause failure, versioning, quarantine, or intentional replacement.
Validate file type and content before publishing a source into a trusted library.
Do not treat hardlinks as backups because corruption or in-place modification is shared by every linked pathname.
Remember that deleting a pathname does not necessarily destroy data while another hardlink or open descriptor remains.
Avoid following untrusted symbolic links when an importer expects regular files.
Separate namespace atomicity from durability. Software with crash-consistency requirements should synchronize file data and relevant directory metadata appropriately.

### concurrency_notes
A predictable temporary name is acceptable only in this isolated single-user lab. Production importers should create unique temporary names safely.
A check-then-create sequence can race with another worker. Prefer kernel operations and application designs that express collision behavior directly.
Readers that opened the former destination before replacement may continue to consume the former inode.

## Rollback

### goal
Remove all artifacts created by this class while leaving every path outside the classroom directory untouched.

### commands
test -d /opt/lab-classroom/class35 && find /opt/lab-classroom/class35 -mindepth 1 -delete

### verification
Run: find /opt/lab-classroom/class35 -mindepth 1 -print
Successful rollback produces no listed descendants.
The directory /opt/lab-classroom/class35 itself remains available for future classroom use.

### limitations
Cleanup cannot reconstruct data that existed inside the classroom directory before the initial reset. Preserve any needed classroom artifacts separately before beginning the lab.

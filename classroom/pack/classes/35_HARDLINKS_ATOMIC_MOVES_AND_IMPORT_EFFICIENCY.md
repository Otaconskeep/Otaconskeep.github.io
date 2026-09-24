# Class 35: Hardlinks, Atomic Moves, and Import Efficiency

**Learning objective:** Explain the relationship between a pathname, directory entry, inode, and file data.; Create and verify hardlinks using device numbers, inode numbers, link counts, sizes, and hashes.; Distinguish hardlinking from copying, symbolic linking, and moving.; Explain why hardlinks cannot normally cross filesystem boundaries.; Demonstrate same-filesystem atomic replacement and describe what existing readers observe.; Design an efficient import sequence that publishes a completed file without duplicating its data blocks.; Identify permission, collision, mutability, durability, and filesystem-boundary risks in automated import pipelines.
**Bloom level:** Understand / Apply
**Track:** Linux Storage and Media Automation · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** medium
**Build output:** Teach learners how Linux hardlinks and same-filesystem atomic renames can support efficient, collision-resistant media and data import workflows without creating unnecessary duplicate file data.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### supported
Linux systems providing hardlinks and POSIX-style same-filesystem rename semantics.
Bash-compatible shells.
GNU Coreutils implementations of ln, mv, stat, sha256sum, and cat.
util-linux findmnt for mount inspection.

### notes
The mv -T option is specific to GNU-compatible implementations and may not exist on BSD or macOS systems.
Output fields and numeric device representations can vary between stat implementations.
Network and clustered filesystems may add cache, locking, client-visibility, or durability considerations beyond this local lab.
Copy-on-write reflinks are a separate feature and should not be confused with hardlinks; reflinked files begin with shared storage extents but have separate inodes.
Filesystem-specific protections or mandatory access-control policies may reject link or rename operations despite ordinary mode bits appearing sufficient.

## Learning objective

- Explain the relationship between a pathname, directory entry, inode, and file data.
- Create and verify hardlinks using device numbers, inode numbers, link counts, sizes, and hashes.
- Distinguish hardlinking from copying, symbolic linking, and moving.
- Explain why hardlinks cannot normally cross filesystem boundaries.
- Demonstrate same-filesystem atomic replacement and describe what existing readers observe.
- Design an efficient import sequence that publishes a completed file without duplicating its data blocks.
- Identify permission, collision, mutability, durability, and filesystem-boundary risks in automated import pipelines.

## Why this matters

Teach learners how Linux hardlinks and same-filesystem atomic renames can support efficient, collision-resistant media and data import workflows without creating unnecessary duplicate file data.

## Prerequisites

- Comfort using a Linux shell and absolute paths.
- Basic familiarity with files, directories, inodes, mounts, and permissions.
- Ability to run commands with sufficient permission to create files under /opt/lab-classroom/class35/.
- Familiarity with common commands such as stat, mv, ln, find, sha256sum, and findmnt.

## Required reading

- Linux man page: inode(7), especially inode numbers and link counts.
- Linux man page: link(2), covering hardlink creation and error conditions.
- Linux man page: rename(2), covering atomic replacement and filesystem limitations.
- GNU Coreutils documentation for ln, mv, stat, and sha256sum.
- Documentation for the storage or media application used in your homelab, focusing on hardlink and completed-download handling.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| inode | A filesystem object containing file metadata and references to file data. A regular filename is not the inode itself; it is a directory entry that refers to an inode. |
| directory entry | A mapping from a name in a directory to an inode on that filesystem. |
| hardlink | An additional directory entry referring to the same inode as another pathname. Both names are peers; neither is intrinsically the original. |
| link count | The number of hardlinks that currently refer to an inode, commonly displayed by stat as the Links field. |
| symbolic link | A distinct filesystem object that stores a path to another object. Unlike a hardlink, it has its own inode and may point across filesystems. |
| atomic rename | A same-filesystem namespace operation in which observers see either the old name mapping or the new name mapping, rather than a partially renamed state. |
| atomic replacement | Renaming a completed temporary file over an existing destination so that new path lookups resolve to the replacement as a single namespace transition. |
| filesystem boundary | The boundary between separately mounted filesystems. Hardlinks and direct rename operations cannot cross it. |
| copy fallback | Behavior in which a high-level move utility copies file data to a destination filesystem and then removes the source because a direct cross-filesystem rename is impossible. |
| publication | The step that makes a completed object visible under its intended final pathname. |
| durability | The degree to which completed data and metadata are guaranteed to survive a crash or power loss. Atomic visibility alone does not guarantee durability. |

## Instruction

A pathname is a human-readable route through one or more directories. For a regular file, the final directory entry refers to an inode, and the inode refers to the file's metadata and data blocks. Creating a hardlink adds another directory entry for the same inode. It does not copy the file's payload. Consequently, two hardlinked paths on the same filesystem normally report the same device number and inode number, while the inode's link count increases. Removing one name does not destroy the data while another hardlink or an open file descriptor still refers to the inode.

Hardlinks are valuable in import workflows where a downloader must retain a completed file for seeding while a library application needs its own organized pathname. A hardlink can provide both names without a second full data copy. This only works when the source and destination are on the same filesystem. Separate mountpoints may look like ordinary directories in a single directory tree, but if their device identifiers differ, the kernel cannot create a hardlink between them. Bind mounts can complicate visual inspection, so compare filesystem identity with stat or findmnt rather than relying only on path layout.

A hardlink is not an independent snapshot. Writing through either path changes the shared inode and is visible through the other path. By contrast, replacing one path with a newly created inode changes only that directory entry; other hardlinks continue to refer to the prior inode. This distinction is important when download clients, taggers, transcoders, or library managers may modify files after import. Applications should treat linked payloads as immutable or deliberately coordinate modifications.

A same-filesystem rename is an efficient metadata operation and provides atomic namespace visibility. If a completed temporary file is renamed over a destination, a process opening the destination afterward sees the replacement. A process that already had the old file open may continue reading the old inode. Atomicity prevents readers from observing a half-renamed pathname, but it does not prove that the file content was complete before publication. The producer must finish and close the temporary file first. Atomic rename also does not, by itself, guarantee crash durability; software requiring strong durability must use appropriate file and directory synchronization before acknowledging success.

The safest import pattern is to validate a completed source, create a uniquely named temporary hardlink inside the destination directory, and then rename that temporary name to the final name. Creating the temporary entry in the destination directory ensures the final publication rename remains on one filesystem. Collision policy must be explicit: fail, version, quarantine, or intentionally replace. Never assume that a command called move is always an atomic rename. When source and destination are on different filesystems, a utility may perform a copy followed by source removal, creating a longer window in which partial destination data must be managed. Import efficiency should therefore be evaluated by filesystem identity, inode identity, link count, integrity checks, and application behavior rather than by path names or elapsed-time claims.

## Architecture

### components
Incoming directory containing completed source files.
Work directory containing temporary files used before publication.
Library directory containing final consumer-facing names.
A single backing filesystem for the classroom directories.
Verification commands that inspect device IDs, inode numbers, link counts, content, and hashes.

### data_flow
A producer writes and closes a file under the incoming or work directory.
The importer validates the source before publication.
For retention workflows, the importer creates a temporary hardlink in the destination directory.
The temporary destination name is atomically renamed to the final library name.
The source and final library path remain separate names for one inode until one name is removed.

### constraints
All mutable lab data remains under /opt/lab-classroom/class35/.
Hardlink source and destination must be on the same filesystem.
Atomic rename guarantees apply to the namespace transition, not to application-level validation or crash durability.
Hardlinked paths share content and metadata associated with their common inode.
Directory permissions must allow the importer to create and rename entries.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Design a production import policy for a downloader and media library.

### requirements
Document how the service verifies that incoming and library paths share a filesystem.
Choose whether the source is retained as a hardlink, removed after publication, or copied across a filesystem boundary.
Define behavior for an existing destination with the same name.
Define whether imported content is immutable and identify every application allowed to modify it.
Describe how temporary names are made unique when two workers import concurrently.
List the inode, device, link-count, hash, and application-level checks recorded in logs.
Explain how interrupted copies are distinguished from fully published files when a cross-filesystem copy is unavoidable.
Keep any practical exercise and generated data strictly under /opt/lab-classroom/class35/.

### deliverable
Submit a one-page workflow description and a shell pseudocode sequence that separates validation, temporary creation, publication, verification, and cleanup.

## Feynman teach-back

### prompt
Explain the lesson to a teammate without using the words magic, duplicate, or instant.

### model_explanation
A directory stores names that point to filesystem records called inodes. A hardlink creates another name for the same inode, so both names reach the same bytes and share the inode's metadata. This is useful when a download client and a media library both need a name for one completed file. The names must be on the same filesystem because inode numbers only have meaning within that filesystem. To publish safely, an importer can create a temporary destination name after the content is complete and then rename that name to the final destination. The final rename changes what new path lookups see as one namespace operation. Programs that already opened the old file can continue reading its old inode. This publication behavior avoids a partially named result, but it does not replace content validation or crash-durability controls.

## Retrieval check

1. What two stat values should match when two pathnames are hardlinks to the same regular file?
2. Why can a hardlink not normally be created between two different filesystems?
3. How does a hardlink differ from a symbolic link?
4. What happens to the other pathname when content is modified in place through one hardlinked pathname?
5. What does a reader with an already open file descriptor observe when the destination pathname is atomically replaced?
6. Why can a command described as a move behave differently across a filesystem boundary?
7. Does atomic rename by itself guarantee that data will survive a sudden power loss? Explain.
8. Why should a temporary publication name be created inside the destination directory?
9. Why is a hardlinked library file not an independent backup of its incoming counterpart?
10. Which checks provide stronger evidence of hardlink identity than matching filenames and file sizes?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

Begin with a directory diagram showing two names pointing to one inode. Emphasize that the pathname is not the file's data and that neither hardlinked name is inherently the original. Create the classroom source, capture its device number, inode number, link count, size, and hash, and then create the library hardlink. Place both stat outputs side by side and point out the shared identity. Append through the library name and display the result through the incoming name to demonstrate shared mutability. Next, introduce atomic publication. Open version-one through a file descriptor, create version-two under a temporary work name, and rename version-two over the final path. Show that the existing descriptor still reads version-one while a fresh lookup reads version-two. Explain that atomic replacement switches the directory mapping; it does not rewrite every reader's open file. Finish with the import pattern: validate a completed source, create a temporary hardlink inside the library directory, and rename it to the final name. Stress that hardlinks and direct renames require one filesystem, that cross-filesystem moves may become copy-and-remove workflows, and that atomic visibility is not the same as crash durability. Close by verifying device IDs, inode IDs, hashes, link counts, and the absence of the temporary publication name.

## References

- Linux man-pages project, inode(7): https://man7.org/linux/man-pages/man7/inode.7.html
- Linux man-pages project, link(2): https://man7.org/linux/man-pages/man2/link.2.html
- Linux man-pages project, rename(2): https://man7.org/linux/man-pages/man2/rename.2.html
- Linux man-pages project, open(2): https://man7.org/linux/man-pages/man2/open.2.html
- GNU Coreutils manual, ln invocation: https://www.gnu.org/software/coreutils/manual/html_node/ln-invocation.html
- GNU Coreutils manual, mv invocation: https://www.gnu.org/software/coreutils/manual/html_node/mv-invocation.html
- GNU Coreutils manual, stat invocation: https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html
- The Open Group Base Specifications, rename: https://pubs.opengroup.org/onlinepubs/9699919799/functions/rename.html

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

# Class 16: Linux Filesystem and Navigation

**Learning objective:** Explain the difference between the filesystem root directory and the root user; Distinguish absolute paths from relative paths; Navigate with pwd, cd, dot, dot-dot, and the home-directory shortcut; List normal and hidden directory entries with ls; Create and organize directories and files inside the assigned lab path; Explain the difference between a filename, a pathname, an inode, and file data; Create and inspect hard links and symbolic links; Use stat, file, readlink, namei, and find to investigate filesystem objects; Recognize why quoting paths and verifying the current directory are important safety practices; Roll back the lab without modifying data outside the controlled workspace
**Bloom level:** Understand / Apply
**Track:** Linux Foundations · **Difficulty:** beginner · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Build a reliable mental model of the Linux filesystem and develop practical skill navigating directories, interpreting paths, inspecting file metadata, and safely manipulating files within a controlled lab workspace.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Debian 12 or later
Ubuntu Server 22.04 LTS or later
Rocky Linux 9 or later
AlmaLinux 9 or later
Fedora Server 40 or later

### shell
Commands are written for Bash and compatible POSIX-style command execution where noted.

### utilities
Core exercises require common Linux utilities including pwd, cd, ls, mkdir, cp, mv, ln, stat, file, readlink, find, grep, unlink, and rmdir. namei is commonly supplied by util-linux.

### implementation_notes
The find -printf option and stat -c formatting are GNU interfaces. On systems without those options, use find with -print and inspect metadata with the platform's native stat syntax. Inode behavior assumes an ordinary inode-based Linux filesystem. Hard links require source and destination to be on the same filesystem.

## Learning objective

- Explain the difference between the filesystem root directory and the root user
- Distinguish absolute paths from relative paths
- Navigate with pwd, cd, dot, dot-dot, and the home-directory shortcut
- List normal and hidden directory entries with ls
- Create and organize directories and files inside the assigned lab path
- Explain the difference between a filename, a pathname, an inode, and file data
- Create and inspect hard links and symbolic links
- Use stat, file, readlink, namei, and find to investigate filesystem objects
- Recognize why quoting paths and verifying the current directory are important safety practices
- Roll back the lab without modifying data outside the controlled workspace

## Why this matters

Build a reliable mental model of the Linux filesystem and develop practical skill navigating directories, interpreting paths, inspecting file metadata, and safely manipulating files within a controlled lab workspace.

## Prerequisites

- Access to a Linux shell using a terminal or console
- A user account that can run sudo for creation of the lab directory
- Basic familiarity with entering commands and reading command output
- Completion of earlier command-line fundamentals classes or equivalent experience

## Required reading

- Filesystem Hierarchy Standard 3.0: https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html
- GNU Coreutils manual, ls invocation: https://www.gnu.org/software/coreutils/manual/html_node/ls-invocation.html
- GNU Coreutils manual, stat invocation: https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html
- Linux man-pages, path_resolution(7): https://man7.org/linux/man-pages/man7/path_resolution.7.html
- Linux man-pages, inode(7): https://man7.org/linux/man-pages/man7/inode.7.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Filesystem | The organized structure through which an operating system stores and retrieves files, directories, links, and associated metadata. |
| Root directory | The top of the Linux directory hierarchy, written as a single forward slash. It is a location and is distinct from the root administrative account. |
| Working directory | The directory a process currently uses as the starting point for resolving relative paths. |
| Absolute path | A pathname beginning with a forward slash and resolved from the filesystem root. |
| Relative path | A pathname resolved from the current working directory rather than from the filesystem root. |
| Directory entry | A name stored in a directory that associates that name with an inode. |
| Inode | A filesystem data structure containing metadata and references to file data. A filename is not stored as the inode itself. |
| Hard link | An additional directory entry that refers to the same inode as another filename on the same filesystem. |
| Symbolic link | A special file whose content is a pathname that Linux resolves when the link is followed. |
| Hidden file | A file or directory whose name begins with a dot. It is hidden by convention from default directory listings, not by a security boundary. |
| Mount point | A directory at which another filesystem is attached to the unified Linux directory tree. |
| Canonical path | A resolved path with symbolic links and dot components interpreted to identify the resulting location. |

## Instruction

Linux presents files through one unified directory tree beginning at the root directory, written as /. Unlike systems that expose separate drive letters, Linux normally attaches additional filesystems at directories called mount points. Common top-level locations include /etc for host configuration, /home for ordinary users' home directories, /var for changing application data, /usr for installed programs and shareable data, /run for runtime state, /tmp for temporary data, and /opt for optional or locally managed software and lab content. These are conventions described by the Filesystem Hierarchy Standard, but actual layouts can vary by distribution and deployment.

Every shell process has a current working directory. The pwd command reports it, and cd changes it. An absolute path starts with / and does not depend on the current working directory. A relative path does not start with / and is interpreted from the current working directory. The component . means the current directory, while .. means the parent directory. The shell commonly expands ~ to the current user's home directory before running a command. Because relative paths depend on context, administrators should check pwd and inspect a destination before performing a mutating operation.

A path is a sequence of directory-entry names separated by forward slashes. Directories map names to inodes. An inode stores metadata such as object type, owner, permissions, timestamps, size, and references to file data. A regular filename is therefore a directory entry pointing to an inode. A hard link creates another name for the same inode, so both names initially expose the same data and share an inode number. Removing one hard-link name does not remove the inode while another link still refers to it. A symbolic link is different: it is its own filesystem object containing a pathname. It may cross filesystem boundaries and may become dangling if its target is moved or removed.

The ls command displays directory entries, while options such as -a and -l reveal hidden names and long-format metadata. Long listings are useful, but scripts should not parse their human-oriented output when a dedicated interface such as stat or find is available. stat reports detailed metadata; file examines content or identifying characteristics; readlink displays a symbolic link's stored target; namei walks through pathname components; and find recursively selects entries according to explicit conditions. Quoting variable expansions and paths prevents whitespace or wildcard characters from being interpreted unexpectedly. Tab completion, read-only inspection, and deliberate use of absolute lab paths reduce mistakes. Hidden files are not inherently protected, file extensions do not determine Linux file type, and filesystem permissions must be evaluated together with directory permissions, ownership, process identity, mount options, and access-control systems.

## Architecture

### conceptual_flow
A shell process holds a current working directory.
The shell expands syntax such as variables and the home-directory shortcut.
The kernel resolves each pathname component through directories.
Directory entries map names to inodes.
Inodes describe object metadata and reference file data.
Mount points can transition pathname resolution into another filesystem.

### lab_tree
/opt/lab-classroom/class16/
/opt/lab-classroom/class16/.lab-note
/opt/lab-classroom/class16/projects/
/opt/lab-classroom/class16/projects/app/
/opt/lab-classroom/class16/projects/app/README.txt
/opt/lab-classroom/class16/projects/app/README.hard
/opt/lab-classroom/class16/projects/app/config/
/opt/lab-classroom/class16/projects/app/config/README.link
/opt/lab-classroom/class16/projects/app/data/
/opt/lab-classroom/class16/projects/app/data/inventory.csv
/opt/lab-classroom/class16/archive/

### path_resolution_example
From /opt/lab-classroom/class16/projects/app/config, the relative path ../README.txt resolves to /opt/lab-classroom/class16/projects/app/README.txt.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### scope
Complete all practical work only beneath /opt/lab-classroom/class16/.

### tasks
Recreate the lab after rollback and draw its directory tree from memory before checking with find.
Create a new directory named docs beneath projects/app and place a short notes.txt file in it.
From projects/app/data, identify one relative path and one absolute path that both name docs/notes.txt.
Use stat to record the inode number, file type, size, ownership, and link count of notes.txt.
Create a relative symbolic link inside docs that points to ../README.txt, then explain why the target is interpreted relative to the link's containing directory.
Write five sentences comparing a copied file, a hard link, and a symbolic link.
Use the explicit rollback approach as a model to remove only the additional homework objects when finished.

### submission
Submit the directory-tree drawing, the two equivalent paths, selected stat output, the link comparison, and a brief explanation of the safety checks used.

## Feynman teach-back

### exercise
Explain pathname resolution to a new administrator without using the words obvious or simply.

### prompts
Draw a tree beginning at / and place /opt/lab-classroom/class16 beneath it.
Explain how the same relative path can resolve differently when the working directory changes.
Describe why a filename and an inode are not the same thing.
Use README.txt and README.hard to explain why editing through one name changes what is read through the other.
Use README.link to explain why moving a symbolic link's target can leave the link dangling.
Explain why checking pwd and quoting "$LAB" reduce operational risk.

### success_criteria
A successful explanation distinguishes names, paths, directory entries, inodes, and data; compares hard links with symbolic links; and traces ../README.txt from the config directory to its final target.

## Retrieval check

1. 1. What distinguishes an absolute path from a relative path?
2. 2. What does .. represent during pathname resolution?
3. 3. Why does ls normally omit .lab-note?
4. 4. What relationship should exist between the inode numbers of README.txt and README.hard?
5. 5. What pathname is stored inside README.link in this lab?
6. 6. Why can a symbolic link become dangling while a remaining hard link still accesses the file data?
7. 7. Which command reports the shell's current working directory?
8. 8. Why should "$LAB" be quoted when used as a command argument?
9. 9. Is the filesystem root directory the same thing as the root administrative user?
10. 10. Why is rmdir useful as a cautious directory rollback tool?

## Guided lab

### scope_rule
Run mutating commands only after setting LAB exactly to /opt/lab-classroom/class16. Do not substitute another path. Inspection commands may report system information, but every file or directory created, changed, moved, linked, or removed by this lab must remain beneath the lab directory.

### steps
### step
1

### title
Create and validate the controlled workspace

### commands
export LAB=/opt/lab-classroom/class16
test "$LAB" = /opt/lab-classroom/class16 || { printf '%s\n' 'Unexpected LAB value' >&2; exit 1; }
sudo install -d -o "$USER" -g "$(id -gn)" "$LAB"
cd "$LAB"
pwd

### explanation
The equality test is a guard against an accidental variable value. install creates the lab directory with ownership assigned to the invoking user. pwd must print the exact controlled path before continuing.
### step
2

### title
Build a directory hierarchy

### commands
mkdir -p "$LAB/projects/app/config" "$LAB/projects/app/data" "$LAB/archive"
printf '%s\n' 'Class 16 hidden note' > "$LAB/.lab-note"
find "$LAB" -maxdepth 4 -printf '%y %p\n' | sort

### explanation
mkdir creates the hierarchy under the absolute lab path. The dot-prefixed note demonstrates a hidden name. GNU find reports each object's type and path.
### step
3

### title
Practice absolute and relative navigation

### commands
cd "$LAB/projects/app/config"
pwd
cd ..
pwd
cd ./data
pwd
cd "$LAB"
pwd

### explanation
The first and final cd commands use absolute paths. The middle commands use parent and current-directory components relative to the shell's working directory.
### step
4

### title
Create, list, copy, and rename files

### commands
printf '%s\n' 'Homelab inventory' > "$LAB/projects/app/readme.txt"
printf '%s\n' 'hostname,role' 'lab-node,training' > "$LAB/projects/app/data/inventory.csv"
cp "$LAB/projects/app/data/inventory.csv" "$LAB/archive/inventory.csv.copy"
mv "$LAB/projects/app/readme.txt" "$LAB/projects/app/README.txt"
ls -la "$LAB"
ls -la "$LAB/projects/app" "$LAB/projects/app/data" "$LAB/archive"

### explanation
The redirections create regular files inside the workspace. cp creates an independent file, while mv changes the directory-entry name from readme.txt to README.txt.
### step
5

### title
Create and compare hard and symbolic links

### commands
ln "$LAB/projects/app/README.txt" "$LAB/projects/app/README.hard"
ln -s ../README.txt "$LAB/projects/app/config/README.link"
ls -li "$LAB/projects/app/README.txt" "$LAB/projects/app/README.hard"
ls -l "$LAB/projects/app/config/README.link"
readlink "$LAB/projects/app/config/README.link"
readlink -f "$LAB/projects/app/config/README.link"

### explanation
README.txt and README.hard should display the same inode number. The symbolic link stores the relative target ../README.txt, which resolves from the config directory.
### step
6

### title
Inspect metadata and pathname resolution

### commands
stat "$LAB/projects/app/README.txt"
stat -c 'name=%n inode=%i links=%h type=%F size=%s' "$LAB/projects/app/README.txt" "$LAB/projects/app/README.hard"
stat -c 'name=%n inode=%i links=%h type=%F size=%s' "$LAB/projects/app/config/README.link"
file "$LAB/projects/app/README.txt" "$LAB/projects/app/config/README.link"
namei -l "$LAB/projects/app/config/README.link"
find "$LAB" -type f -printf '%p\n' | sort

### explanation
stat shows inode metadata, file provides a content-oriented description, namei displays each path component, and find selects regular files recursively. Without its link-following options, find classifies the symbolic link separately from regular files.
### step
7

### title
Demonstrate shared hard-link data

### commands
printf '%s\n' 'Hard links share one inode.' >> "$LAB/projects/app/README.hard"
cat "$LAB/projects/app/README.txt"
stat -c 'name=%n inode=%i links=%h size=%s' "$LAB/projects/app/README.txt" "$LAB/projects/app/README.hard"

### explanation
Appending through README.hard changes the data observed through README.txt because both names refer to the same inode. The inode numbers and sizes should match.

## Expected results

- pwd prints /opt/lab-classroom/class16 immediately after workspace setup.
- The lab contains projects, projects/app, projects/app/config, projects/app/data, and archive directories.
- The default concept of hidden entries is demonstrated by .lab-note, which appears with ls -a or ls -la.
- README.txt and README.hard have the same inode number and a hard-link count of at least 2.
- README.link is reported as a symbolic link and stores ../README.txt as its target.
- readlink -f resolves README.link to /opt/lab-classroom/class16/projects/app/README.txt.
- Reading README.txt after appending through README.hard displays the appended sentence.
- inventory.csv.copy exists independently in the archive directory.

## Verification checkpoints

- [ ] Run test "$(pwd)" = "$LAB" after returning to the workspace; successful verification produces no output and exits with status zero.
- [ ] Run test -d "$LAB/projects/app/config" && test -d "$LAB/projects/app/data" && test -d "$LAB/archive"; all three directory tests must succeed.
- [ ] Run test -f "$LAB/projects/app/README.txt" && test -f "$LAB/projects/app/data/inventory.csv" && test -f "$LAB/archive/inventory.csv.copy"; all regular-file tests must succeed.
- [ ] Run test -L "$LAB/projects/app/config/README.link"; the symbolic-link test must succeed.
- [ ] Run test "$(readlink "$LAB/projects/app/config/README.link")" = '../README.txt'; the stored relative target must match exactly.
- [ ] Run test "$(stat -c %i "$LAB/projects/app/README.txt")" = "$(stat -c %i "$LAB/projects/app/README.hard")"; matching inode numbers confirm the hard link.
- [ ] Run test "$(stat -c %h "$LAB/projects/app/README.txt")" -ge 2; the inode must have at least two hard links.
- [ ] Run grep -Fqx 'Hard links share one inode.' "$LAB/projects/app/README.txt"; the shared content must be visible through README.txt.
- [ ] Run find "$LAB" -mindepth 1 -printf '%y %p\n' | sort and manually confirm that every reported pathname begins with /opt/lab-classroom/class16/.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Creating /opt/lab-classroom/class16 reports permission denied. | The current user cannot create directories beneath /opt, or sudo access is unavailable. | Ask the system administrator to create /opt/lab-classroom/class16 and assign it to the lab user. Do not relocate the exercise because the class scope requires the specified path. |
| cd ./data reports that the directory does not exist. | The shell is not currently in /opt/lab-classroom/class16/projects/app, or the hierarchy was not created. | Run pwd, then use cd "$LAB/projects/app" before retrying cd ./data. Re-run the directory creation step if data is absent. |
| The hidden note does not appear in an ls listing. | The default ls view omits names beginning with a dot. | Run ls -la "$LAB" and look for .lab-note. |
| Creating README.hard reports that the file already exists. | The hard link was already created during a previous attempt. | Inspect both paths with ls -li. If their inode numbers match, the required result is already present. |
| Creating the hard link reports an invalid cross-device link. | The source and destination unexpectedly reside on different filesystems, which hard links cannot cross. | Confirm both paths are exactly beneath $LAB and inspect their filesystem identifiers with stat -c '%d %n' on the parent directories. Use the prescribed paths on the same lab filesystem. |
| readlink -f produces no resolved path. | The symbolic link is dangling because README.txt is absent or the stored relative target is incorrect. | Run readlink on the link, verify that README.txt exists in projects/app, and confirm the intended target is ../README.txt from the config directory. |
| README.txt and README.hard have different inode numbers. | One path was copied or independently created instead of being made with ln. | Inspect the two files before changing anything. Roll back the lab using the explicit procedure, then repeat the link-creation step. |
| namei or GNU find formatting options are unavailable. | The host uses a minimal userland or a non-GNU implementation. | Use ls -ld on each pathname component and use find "$LAB" -print as a portable fallback. The core path and link concepts remain the same. |

## Security considerations

### principles
Treat the current working directory as security-relevant context because relative mutations depend on it.
Use an exact, validated absolute lab path for changes.
Quote all variable expansions and paths so spaces and wildcard characters are not reinterpreted by the shell.
Inspect an object with pwd, ls, stat, or readlink before modifying it.
Remember that a hidden filename is a display convention, not access control.
Directory permissions govern whether names can be created, removed, or traversed, while file permissions govern access to file content.
Symbolic links can redirect pathname resolution, so privileged automation should validate destinations and avoid trusting writable directories.
Do not assume a filename extension proves content type or safety.
Use elevated privileges only for the initial creation and ownership of the controlled workspace.

### scope_boundary
/opt/lab-classroom/class16/

### data_classification
Training data only; do not place credentials, private keys, tokens, or production configuration in the lab tree.

## Rollback

### goal
Remove only the objects created by this lesson while preserving /opt/lab-classroom/class16 as an empty classroom directory.

### commands
export LAB=/opt/lab-classroom/class16
test "$LAB" = /opt/lab-classroom/class16 || { printf '%s\n' 'Rollback refused: unexpected LAB value' >&2; exit 1; }
unlink "$LAB/projects/app/config/README.link"
unlink "$LAB/projects/app/README.hard"
unlink "$LAB/projects/app/README.txt"
unlink "$LAB/projects/app/data/inventory.csv"
unlink "$LAB/archive/inventory.csv.copy"
unlink "$LAB/.lab-note"
rmdir "$LAB/projects/app/config"
rmdir "$LAB/projects/app/data"
rmdir "$LAB/projects/app"
rmdir "$LAB/projects"
rmdir "$LAB/archive"
find "$LAB" -mindepth 1 -print

### notes
Each removal names one known lab object. rmdir refuses to remove a nonempty directory, providing a safety check. The final find command should print nothing. If an unlink command reports that a path is absent, inspect the workspace and continue only after confirming the missing path was part of this lab.

## Video narration notes

Welcome to Class 16, Linux Filesystem and Navigation. In this lesson, we will treat navigation as more than memorizing cd and ls. Linux organizes visible storage into one directory hierarchy beginning at the root directory, represented by a forward slash. That root directory is not the same as the root administrative account. Filesystems can be attached at mount points, but applications continue to access their contents through ordinary paths.

Begin by creating the controlled workspace at /opt/lab-classroom/class16. Export that exact value as LAB, validate it, enter the directory, and use pwd to confirm your location. This check matters because relative commands inherit context from the shell's current working directory. An absolute path begins at slash. A relative path begins from where the shell is currently located. A single dot represents the current directory, and two dots represent its parent.

Next, build the projects, app, config, data, and archive directories. Create a dot-prefixed note and compare ordinary ls output with ls -la. The note is called hidden only because listing tools omit dot-prefixed names by default. That convention does not protect the file from access.

Create README.txt and inventory.csv, copy the inventory into archive, and rename the readme with mv. Linux paths are case-sensitive on the filesystems commonly used in homelabs, so readme.txt and README.txt are distinct spellings. Now create README.hard with ln. When ls -li or stat displays the files, README.txt and README.hard should have the same inode number. They are two names for one inode and one set of file data.

Create README.link with a relative symbolic-link target. The link stores ../README.txt. Because the link is inside config, the parent component leads back to app, where README.txt exists. readlink shows the stored text, while readlink -f resolves it to an absolute destination. The symbolic link has its own inode and can become dangling if its pathname no longer reaches a target.

Use stat, file, namei, and find to inspect the tree from different perspectives. Then append a sentence through README.hard and read README.txt. The sentence appears through both names because both hard links reach the same inode. Finish by running every verification check. For rollback, remove only the explicitly named lab objects and use rmdir for directories. This controlled approach reinforces the central operational habit of the class: know your location, understand how a path resolves, inspect before changing, and keep every mutation inside the assigned boundary.

## References

- Filesystem Hierarchy Standard 3.0: https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html
- GNU Coreutils manual: https://www.gnu.org/software/coreutils/manual/
- Linux man-pages, path_resolution(7): https://man7.org/linux/man-pages/man7/path_resolution.7.html
- Linux man-pages, inode(7): https://man7.org/linux/man-pages/man7/inode.7.html
- Linux man-pages, symlink(7): https://man7.org/linux/man-pages/man7/symlink.7.html
- Linux man-pages, hier(7): https://man7.org/linux/man-pages/man7/hier.7.html
- Linux man-pages, find(1): https://man7.org/linux/man-pages/man1/find.1.html
- Linux man-pages, namei(1): https://man7.org/linux/man-pages/man1/namei.1.html

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

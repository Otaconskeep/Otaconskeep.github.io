# Class 18: Users, Groups, Permissions, and Least Privilege

**Learning objective:** Explain the difference between a user ID, primary group, supplementary groups, and an account name.; Interpret owner, group, and other permission classes for files and directories.; Explain the distinct meanings of read, write, and execute permissions on files and directories.; Use id, getent, stat, namei, and getfacl to investigate identity and authorization decisions.; Apply restrictive permissions and a narrowly scoped ACL inside the isolated lab directory.; Verify both successful access and expected access denial.; Describe why least privilege, group design, and periodic access review are preferable to broadly writable resources.
**Bloom level:** Understand / Apply
**Track:** Linux Systems Administration · **Difficulty:** beginner · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Teach students how Linux identifies users and groups, evaluates file permissions and access control lists, and applies least privilege without modifying system account databases. The lab builds an isolated project tree under /opt/lab-classroom/class18/ and validates permitted and denied access using the current user and an existing unprivileged audit identity.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux distributions using standard POSIX ownership and permission semantics

### shell
POSIX-style shell with the command substitutions and conditionals used in the lab; Bash is recommended.

### required_commands
id
getent
install
mkdir
printf
chmod
stat
namei
setfacl
getfacl
sudo
find
test

### filesystem
The filesystem containing /opt/lab-classroom/class18/ must support POSIX ACLs.

### notes
User and group names vary by distribution. The default auditor name must be replaced with another existing unprivileged identity if it is unavailable. Mandatory access-control systems or container restrictions may impose additional denials beyond the discretionary permissions demonstrated here.

## Learning objective

- Explain the difference between a user ID, primary group, supplementary groups, and an account name.
- Interpret owner, group, and other permission classes for files and directories.
- Explain the distinct meanings of read, write, and execute permissions on files and directories.
- Use id, getent, stat, namei, and getfacl to investigate identity and authorization decisions.
- Apply restrictive permissions and a narrowly scoped ACL inside the isolated lab directory.
- Verify both successful access and expected access denial.
- Describe why least privilege, group design, and periodic access review are preferable to broadly writable resources.

## Why this matters

Teach students how Linux identifies users and groups, evaluates file permissions and access control lists, and applies least privilege without modifying system account databases. The lab builds an isolated project tree under /opt/lab-classroom/class18/ and validates permitted and denied access using the current user and an existing unprivileged audit identity.

## Prerequisites

- A Linux host or virtual machine with a POSIX-compatible shell.
- The directory /opt/lab-classroom must already exist and permit traversal.
- The student must have sudo authorization for creating the class directory and running a command as an existing unprivileged identity.
- GNU coreutils, findutils, util-linux, getent, and the POSIX ACL utilities getfacl and setfacl must be installed.
- Basic familiarity with shell commands, paths, files, and directories.

## Required reading

- Linux man-pages: credentials(7), https://man7.org/linux/man-pages/man7/credentials.7.html
- Linux man-pages: inode(7), https://man7.org/linux/man-pages/man7/inode.7.html
- Linux man-pages: acl(5), https://man7.org/linux/man-pages/man5/acl.5.html
- Linux man-pages: id(1), https://man7.org/linux/man-pages/man1/id.1.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| UID | A numeric user identifier used by the kernel for ownership and credential checks. A login name is a human-readable mapping to a UID. |
| GID | A numeric group identifier. Files store a group owner by GID, and processes carry group credentials used during access checks. |
| Primary group | The default group associated with a user and commonly used as the group owner for newly created files. |
| Supplementary groups | Additional groups carried by a process, usually established when a login session begins. |
| Mode bits | The owner, group, and other read, write, and execute permissions stored in an inode. |
| Directory execute permission | Permission to traverse or search a directory and access named entries within it. It does not mean that the directory itself is executable software. |
| ACL | An access control list that can grant permissions to additional named users or groups beyond the traditional owner, group, and other classes. |
| ACL mask | The maximum effective permissions available to named ACL users, named ACL groups, and the owning group. |
| Least privilege | Granting an identity only the access required to perform its current task, for only as long and as narrowly as necessary. |
| Effective credentials | The UID and GIDs a process is currently using for authorization checks. |

## Instruction

Linux authorization begins with process credentials. A process has user and group identifiers, while a file has an owning UID, an owning GID, mode bits, and possibly an ACL. Names such as alice or operators are convenient labels; the kernel ultimately evaluates numeric identifiers. The id command reports the credentials associated with a user, while getent queries the system's configured identity sources without assuming that all accounts come from local files.

Traditional mode bits contain three permission classes: owner, group, and other. The kernel selects the applicable class rather than combining all three classes. If the process UID matches the file owner, the owner bits apply. Otherwise, if one of the process groups matches the file group, the group bits apply. Otherwise, the other bits apply. A POSIX ACL extends this model with named user and group entries and an ACL mask. Because the mask can reduce effective access, getfacl is often more informative than looking only at the compact mode display.

Permissions mean different things for files and directories. Reading a regular file permits reading its contents. Writing permits changing its contents. Execute permits attempting to run it as a program, subject to format, interpreter, mount, and policy constraints. On a directory, read permits listing names, write permits creating or removing directory entries, and execute permits traversal. Removing a file is therefore primarily controlled by the parent directory, not by the file's write bit. Access to a deep path also requires traversal through every parent directory. The namei command is useful when a leaf file appears readable but an ancestor blocks access.

Groups are usually the cleanest way to delegate shared access because they describe roles instead of one-off exceptions. ACLs are useful when a named user needs a narrow exception, such as read-only access to one report. Excessive ACL entries can become difficult to audit, so they should not replace thoughtful group design. Group membership changes may not appear in an already running process because credentials are normally established when the session begins.

Least privilege is both a design rule and an operational process. Begin with no access, grant the smallest required permission, test the intended action, test that prohibited actions still fail, and remove access when the task ends. Avoid treating elevated execution as a default workflow. Elevated identities can bypass ordinary discretionary controls, so successful testing as an administrator does not prove that an application identity has correct access. This class deliberately avoids creating accounts or editing system identity databases. It uses existing identities and changes only the isolated class directory.

## Architecture

### scope
/opt/lab-classroom/class18/

### identities
LAB_USER: the non-root student running the lab and owner of the class tree.
LAB_GROUP: the student's current primary group and group owner of the class tree.
AUDITOR: an existing unprivileged account, defaulting to nobody, that receives a narrow read-only ACL.

### resources
project/report.txt: a non-secret report readable by the owner and group, with an additional read-only ACL for AUDITOR.
secrets/credentials.txt: synthetic training data accessible only through the owner's permissions.
project/: traversable by AUDITOR only because of a named ACL; AUDITOR cannot create entries there.
secrets/: no AUDITOR ACL, demonstrating denial at an intermediate directory.

### access_flow
A process presents its effective UID and groups.
Every ancestor directory must permit path traversal.
The filesystem evaluates ownership, ACL entries, the ACL mask, and mode permissions.
The requested operation succeeds only if the resulting effective permission permits it.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Design a permission model for a homelab backup service, a monitoring service, and two human administrators. Do not apply the design to the host.

### deliverables
A table listing each identity, required read paths, required write paths, and explicitly prohibited paths.
A proposed group structure that favors roles over person-specific grants.
One case where a narrow ACL is justified and an explanation of why a new group would be less appropriate.
A verification plan containing both successful and denied test cases.
A short access-review procedure covering ownership, group membership, ACLs, stale access, and session refresh after membership changes.

### constraint
Homework must remain a written design exercise unless a separate disposable environment is provided.

## Feynman teach-back

### prompt
Explain the access decision to someone who knows only that files have owners. Use report.txt and credentials.txt as examples.

### model_explanation
A program tries to access a path using the identity of the process running it. Linux first needs permission to pass through every directory in that path. It then evaluates the target object's owner, group, other permissions, and any ACL. In this lab, the auditor is allowed to pass through the class and project directories and read one report, but it is not allowed to write that report. The auditor receives no route through the secrets directory, so it cannot reach the synthetic credential file. This is least privilege because the exception grants only the exact path and action needed.

### self_check
Can you explain why directory execute permission matters even when a file itself is readable?
Can you explain why file write permission does not by itself control deletion?
Can you identify where the ACL mask appears and what it limits?
Can you explain why successful administrator access is not a valid test of an unprivileged service account?

## Retrieval check

1. 1. What numeric credential does the kernel primarily use to identify a user for file ownership checks?
2. 2. What does execute permission on a directory allow?
3. 3. If a process owns a file, are the group and other mode classes added to the owner class during a traditional mode check?
4. 4. Why can a file with an apparently readable ACL entry still be inaccessible?
5. 5. Which permission on a parent directory is central to creating or removing entries in that directory?
6. 6. Why should permission testing be performed as the intended service or user identity?
7. 7. When is a group generally preferable to a named-user ACL?
8. 8. What does the POSIX ACL mask limit?
9. 9. Why might newly granted supplementary group membership not affect an existing shell?
10. 10. What two categories of test should a least-privilege verification plan contain?

## Guided lab

### name
Build and Audit a Least-Privilege Project Tree

### scope_rule
All filesystem mutations must remain within /opt/lab-classroom/class18/. The lab does not create users, create groups, edit account databases, or change any parent directory.

### steps
### step
1

### title
Record the current identity and select an auditor

### commands
export ROOT=/opt/lab-classroom/class18
export LAB_USER="$(id -un)"
export LAB_GROUP="$(id -gn)"
export AUDITOR=nobody
printf 'User=%s Group=%s Auditor=%s\n' "$LAB_USER" "$LAB_GROUP" "$AUDITOR"
id
getent passwd "$AUDITOR"
getent group "$LAB_GROUP"

### notes
Stop if getent cannot find the auditor. Choose another existing, unprivileged account and export AUDITOR to that account name. Do not use root as the auditor.
### step
2

### title
Create the isolated class tree

### commands
test -d /opt/lab-classroom
test ! -e "$ROOT" || { printf 'Refusing to overwrite existing lab tree: %s\n' "$ROOT" >&2; exit 1; }
sudo install -d -o "$LAB_USER" -g "$LAB_GROUP" -m 0750 "$ROOT"
umask 027
mkdir "$ROOT/project" "$ROOT/secrets"
printf '%s\n' 'Quarterly homelab capacity review' > "$ROOT/project/report.txt"
printf '%s\n' 'TRAINING-DATA-NOT-A-REAL-CREDENTIAL' > "$ROOT/secrets/credentials.txt"
chmod 0750 "$ROOT/project" "$ROOT/secrets"
chmod 0640 "$ROOT/project/report.txt" "$ROOT/secrets/credentials.txt"

### notes
The preflight refusal prevents the exercise from overwriting an earlier tree. The umask removes group write and all other-class permissions from newly created objects.
### step
3

### title
Inspect traditional ownership and permissions

### commands
id "$LAB_USER"
stat -c '%A %a %U %G %n' "$ROOT" "$ROOT/project" "$ROOT/project/report.txt" "$ROOT/secrets" "$ROOT/secrets/credentials.txt"
namei -l "$ROOT/project/report.txt"

### notes
Confirm that directories are mode 750 and files are mode 640 before adding an ACL.
### step
4

### title
Grant the auditor one narrow read path

### commands
setfacl -m "u:${AUDITOR}:--x" "$ROOT"
setfacl -m "u:${AUDITOR}:--x" "$ROOT/project"
setfacl -m "u:${AUDITOR}:r--" "$ROOT/project/report.txt"
getfacl -p "$ROOT" "$ROOT/project" "$ROOT/project/report.txt"

### notes
The auditor receives traversal on two directories and read access to one file. No write permission and no access to the secrets directory are granted.
### step
5

### title
Test allowed and denied operations

### commands
sudo -u "$AUDITOR" -- cat "$ROOT/project/report.txt"
if sudo -u "$AUDITOR" -- sh -c 'printf "%s\n" changed >> "$1"' sh "$ROOT/project/report.txt"; then
  printf '%s\n' 'ERROR: auditor unexpectedly wrote the report' >&2
  exit 1
else
  printf '%s\n' 'PASS: auditor write was denied'
fi
if sudo -u "$AUDITOR" -- cat "$ROOT/secrets/credentials.txt"; then
  printf '%s\n' 'ERROR: auditor unexpectedly read the secret' >&2
  exit 1
else
  printf '%s\n' 'PASS: auditor secret access was denied'
fi

### notes
An expected denial is a successful security test. The synthetic secret is not a real credential.
### step
6

### title
Review the final authorization state

### commands
stat -c '%A %a %U %G %n' "$ROOT/project/report.txt" "$ROOT/secrets/credentials.txt"
getfacl -p "$ROOT/project/report.txt" "$ROOT/secrets/credentials.txt"
namei -l "$ROOT/secrets/credentials.txt"

### notes
Look for the named auditor entry on report.txt, verify that it is bounded by the ACL mask, and verify that the secrets path has no equivalent grant.

## Expected results

- id reports the student's UID, primary GID, and supplementary groups without modifying identity data.
- The class root, project directory, and secrets directory have numeric mode 750 before considering ACL display markers.
- The two regular files have numeric mode 640.
- getfacl shows the auditor with execute-only traversal on the class root and project directory.
- getfacl shows the auditor with read-only access to project/report.txt.
- The auditor can print project/report.txt.
- The auditor cannot append to project/report.txt.
- The auditor cannot read secrets/credentials.txt.
- All created or modified filesystem objects are contained within /opt/lab-classroom/class18/.

## Verification checkpoints

- [ ] Run test -d /opt/lab-classroom/class18/project && test -d /opt/lab-classroom/class18/secrets; a zero exit status confirms that both directories exist.
- [ ] Run stat -c '%a %n' /opt/lab-classroom/class18/project /opt/lab-classroom/class18/secrets and confirm that both numeric modes are 750.
- [ ] Run stat -c '%a %n' /opt/lab-classroom/class18/project/report.txt /opt/lab-classroom/class18/secrets/credentials.txt and confirm that both numeric modes are 640.
- [ ] Run getfacl -cp /opt/lab-classroom/class18/project/report.txt and confirm that the selected auditor has a named read-only entry whose effective permissions include read.
- [ ] Run sudo -u "$AUDITOR" -- test -r /opt/lab-classroom/class18/project/report.txt and confirm a zero exit status.
- [ ] Run sudo -u "$AUDITOR" -- test ! -w /opt/lab-classroom/class18/project/report.txt and confirm a zero exit status.
- [ ] Run sudo -u "$AUDITOR" -- test ! -r /opt/lab-classroom/class18/secrets/credentials.txt and confirm a zero exit status.
- [ ] Run find /opt/lab-classroom/class18 -xdev -printf '%M %u %g %p\n' and review every object for unexpected owners, groups, or write permissions.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| getent passwd nobody returns no result. | The system does not define an account named nobody or uses a different unprivileged account name. | Select an existing non-administrative account with getent passwd, set AUDITOR to that name, and repeat the lab. Do not create an account because that would modify data outside the permitted lab scope. |
| setfacl or getfacl is not found. | The POSIX ACL user-space utilities are not installed. | Install the ACL utilities using the platform's normal package-management process before starting the lab, or ask the lab administrator to provide them. Do not alter the exercise commands to grant broad mode permissions. |
| setfacl reports that the operation is not supported. | The filesystem or mount configuration does not support the required ACL behavior. | Move the entire lab environment to an ACL-capable Linux filesystem while preserving the required /opt/lab-classroom/class18/ path, then recreate the lab tree. |
| The auditor cannot read report.txt even though the file has a named read ACL. | An ancestor directory blocks traversal, the ACL mask removes effective read access, or AUDITOR does not match the tested identity. | Use namei -l on the report path and getfacl on the class root, project directory, and report. Confirm execute-only auditor entries on both lab directories and an effective read entry on the file. |
| The auditor can unexpectedly read the synthetic secret. | A prior ACL, permissive mode, or different auditor group membership grants access. | Inspect every path component with namei -l and getfacl. Confirm directory mode 750, file mode 640, and the absence of named auditor entries on the secrets directory and file. Rebuild the isolated tree if its prior state is uncertain. |
| sudo refuses to run the test command as the auditor. | The student lacks the required sudo policy or the platform restricts target identities. | Ask the lab administrator to perform the identity-switch tests or provide a disposable VM with the required policy. Do not substitute an administrative identity because it may bypass the permissions being tested. |
| A user does not receive newly assigned group access in another environment. | The user's existing process retained the group list established when the session began. | Start a new authenticated session and verify the new process credentials with id. Avoid assuming that editing group membership retroactively changes every running process. |

## Security considerations

### principles
Use groups for stable role-based collaboration and ACLs for narrow, reviewable exceptions.
Grant traversal only on the directories required to reach an approved object.
Separate public or shareable project data from secret data so that delegation does not expose both.
Test a policy using the actual service or user identity rather than only an administrator.
Verify denied operations as well as permitted operations.
Review ACL masks because a visible ACL entry may have fewer effective permissions than its entry text suggests.
Treat account names as labels and use identity tools to confirm the actual UID and groups.
Remove temporary access after the associated task ends.

### scope_controls
The exercise never creates or deletes operating-system users or groups. All writes, ownership changes, permission changes, ACL changes, and cleanup operations are restricted to /opt/lab-classroom/class18/.

### data_classification
The credentials file contains explicitly synthetic training text. Real secrets must not be placed in the lab tree.

### audit_guidance
Record who owns each object, which groups are involved, all named ACL entries, the ACL mask, the business reason for each grant, and whether expected denials were verified.

## Rollback

### goal
Remove only the isolated class tree after confirming that no required data is stored there.

### commands
export ROOT=/opt/lab-classroom/class18
test "$ROOT" = /opt/lab-classroom/class18
sudo find "$ROOT" -xdev -depth -delete
test ! -e "$ROOT"

### notes
The deletion is irreversible for the synthetic lab files. The fixed-path equality check and filesystem boundary option reduce the risk of deleting an unintended location. Re-running the lab recreates the training data.

## Video narration notes

Begin by showing id and explaining that account names are labels for numeric credentials. Display the class root and identify its owner, group, and mode. Introduce the three permission classes, then emphasize that file permissions and directory permissions describe different operations. Use namei to walk the report path one component at a time. Explain that every directory must allow traversal before the final file can be evaluated.

Create the project and secrets directories with restrictive modes and point out the effect of the selected umask. Show stat output for both directories and files. Next, introduce the auditor as an existing unprivileged identity. Add execute-only ACL entries to the two directories on the approved path and a read-only ACL to the report. Display getfacl output, including the mask and effective permissions.

Run the report read as the auditor and show that it succeeds. Attempt an append and explain why the denial is expected. Attempt to read the synthetic secret and trace the denial to the missing directory access. Reinforce that a least-privilege test is incomplete unless prohibited actions are tested. Close by reviewing when to use role-based groups, when a narrow ACL may be appropriate, why existing sessions can retain old group credentials, and how the fixed lab boundary makes cleanup predictable.

## References

- Linux man-pages project, credentials(7): https://man7.org/linux/man-pages/man7/credentials.7.html
- Linux man-pages project, inode(7): https://man7.org/linux/man-pages/man7/inode.7.html
- Linux man-pages project, acl(5): https://man7.org/linux/man-pages/man5/acl.5.html
- Linux man-pages project, getfacl(1): https://man7.org/linux/man-pages/man1/getfacl.1.html
- Linux man-pages project, setfacl(1): https://man7.org/linux/man-pages/man1/setfacl.1.html
- Linux man-pages project, stat(1): https://man7.org/linux/man-pages/man1/stat.1.html
- Linux man-pages project, namei(1): https://man7.org/linux/man-pages/man1/namei.1.html
- GNU Coreutils manual, File permissions: https://www.gnu.org/software/coreutils/manual/html_node/File-permissions.html

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

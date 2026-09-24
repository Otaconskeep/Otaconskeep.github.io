# Reading: Users, Groups, Permissions, and Least Privilege

**Module:** Linux Foundations
**Activity type:** Reading (Learn)
**Objective:** Explain the difference between a user ID, primary group, supplementary groups, and an account name.

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

## Required reading

- Linux man-pages: credentials(7), https://man7.org/linux/man-pages/man7/credentials.7.html
- Linux man-pages: inode(7), https://man7.org/linux/man-pages/man7/inode.7.html
- Linux man-pages: acl(5), https://man7.org/linux/man-pages/man5/acl.5.html
- Linux man-pages: id(1), https://man7.org/linux/man-pages/man1/id.1.html

## References

- Linux man-pages project, credentials(7): https://man7.org/linux/man-pages/man7/credentials.7.html
- Linux man-pages project, inode(7): https://man7.org/linux/man-pages/man7/inode.7.html
- Linux man-pages project, acl(5): https://man7.org/linux/man-pages/man5/acl.5.html
- Linux man-pages project, getfacl(1): https://man7.org/linux/man-pages/man1/getfacl.1.html
- Linux man-pages project, setfacl(1): https://man7.org/linux/man-pages/man1/setfacl.1.html
- Linux man-pages project, stat(1): https://man7.org/linux/man-pages/man1/stat.1.html
- Linux man-pages project, namei(1): https://man7.org/linux/man-pages/man1/namei.1.html
- GNU Coreutils manual, File permissions: https://www.gnu.org/software/coreutils/manual/html_node/File-permissions.html

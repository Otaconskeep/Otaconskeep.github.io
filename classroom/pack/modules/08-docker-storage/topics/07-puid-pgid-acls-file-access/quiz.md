# Quiz: PUID, PGID, ACLs, and Container File Access

**Module:** Module 8: Docker, Storage & Permissions
**Activity type:** Quiz (Test)

## Knowledge check

1. Does Linux authorize a filename using usernames or numeric IDs?  
2. Does Docker universally implement PUID/PGID variables?  
3. What permission does a directory need for traversal?  
4. What does the ACL mask affect?  
5. Why is `chmod 777` usually the wrong repair?  
6. Name two non-mode-bit causes of denial.

## Answer key

1. Numeric UID/GID values, with names as user-space labels.  
2. No; individual images may implement the convention.  
3. Execute/search permission.  
4. Effective permissions for named users, named groups, and the owning-group class.  
5. It grants unnecessary access and hides the identity/design mismatch.  
6. Read-only mount, ACL mask, SELinux/AppArmor, network identity mapping, missing parent traversal, or supplementary-group mismatch.

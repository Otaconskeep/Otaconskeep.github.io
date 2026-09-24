# Quiz: Mounts, UUIDs, and fstab

**Module:** Module 8: Docker, Storage & Permissions
**Activity type:** Quiz (Test)

## Knowledge check

1. What does a mountpoint do?  
2. Why prefer a UUID over `/dev/sdX` in many persistent mounts?  
3. What are the six `fstab` fields?  
4. Does `nofail` make a mount correct or secure?  
5. What can a mount hide?  
6. Why is out-of-band or console recovery useful before testing boot mounts?

## Answer key

1. Exposes a filesystem at a directory in the unified tree.  
2. Device enumeration can change, while filesystem UUID normally persists.  
3. Source, target, type, options, dump, fsck pass.  
4. No; it changes failure handling only.  
5. Existing contents beneath the mountpoint while mounted.  
6. A bad entry can disrupt normal boot or remote access.

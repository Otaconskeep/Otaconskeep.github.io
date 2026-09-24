# Quiz: Linux Disks, Partitions, and Filesystems

**Module:** Module 8: Docker, Storage & Permissions
**Activity type:** Quiz (Test)

## Knowledge check

1. What does a partition table describe?  
2. Can a filesystem exist in a regular image file?  
3. What question does `findmnt` answer?  
4. Why can `du` and `df` disagree?  
5. Does high filesystem use prove disk failure?  
6. What must be verified before `mkfs` targets a real device?

## Answer key

1. The layout and types of partitions on a disk.  
2. Yes, as demonstrated by the bounded lab image.  
3. Which source is mounted where, with which type and options.  
4. Deleted-open files, snapshots, reserved blocks, mount boundaries, permissions, or sparse/allocation differences.  
5. No; capacity and device health are separate layers.  
6. Exact identity, topology, mounts, signatures, backups, change approval, and recovery plan.

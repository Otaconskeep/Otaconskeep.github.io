# Reading: The 3-2-1 Backup Strategy

**Module:** Segmentation, Backup & Power
**Activity type:** Reading (Learn)
**Objective:** Explain what each number in the 3-2-1 strategy represents.

## Vocabulary

| Term | Meaning |
|---|---|
| 3-2-1 backup strategy | A planning rule that calls for three copies of important data, stored across at least two independent media or failure domains, with at least one copy kept off-site. |
| Primary copy | The active data used by applications or users. It is one of the three copies, but it is not itself considered a backup. |
| Backup copy | A separately managed copy retained so data can be recovered after deletion, corruption, compromise, or infrastructure failure. |
| Failure domain | A set of components that can fail together because they share a dependency, such as one disk, host, power circuit, account, building, or administrative credential. |
| Off-site | Stored far enough from the primary location that a local disaster, theft, or facility outage is unlikely to destroy both copies. |
| Offline backup | A backup that is not continuously reachable or writable from production systems. |
| Immutable backup | A backup protected against modification or deletion for a defined retention period, including modification by compromised administrative credentials where the platform supports that guarantee. |
| Retention | The policy defining how many recovery versions are kept and how long each version remains available. |
| Recovery Point Objective | The maximum acceptable amount of data loss measured in time. It determines how frequently backups or recoverable versions should be created. |
| Recovery Time Objective | The target duration for restoring a service or data set after an interruption. |
| Restore test | A controlled recovery exercise that proves backup data can be read, reconstructed, and validated. |
| Checksum | A value calculated from data and used to detect accidental changes. This lab uses SHA-256 hashes as integrity evidence, not as proof that a file is trustworthy or malware-free. |

## Instruction

The 3-2-1 strategy begins with three copies: the active primary copy and two additional backup copies. Those copies must not merely be three directory names pointing to the same vulnerable storage. If all copies reside on one physical disk, one host, one power supply, or one administrative account, a single failure or compromise may destroy all of them. The second number therefore requires at least two independent storage media or meaningful failure domains. Examples include local server storage plus removable storage, a storage appliance plus object storage, or disk backup plus tape. The third number requires one copy to be off-site so a fire, flood, theft, electrical event, or building-wide outage does not eliminate every recovery option.

A backup is not the same thing as synchronization. Synchronization may quickly reproduce an accidental deletion or encrypted file across every replica. RAID and storage replication improve availability, but they usually preserve current state rather than a recoverable history. Snapshots can be valuable recovery points, yet snapshots stored and administered with the source may remain exposed to array failure, account compromise, or ransomware. These technologies can contribute to a backup architecture, but they do not automatically satisfy it.

A credible backup plan also includes retention, access control, encryption, monitoring, and restoration testing. The Recovery Point Objective determines how much recent work may be lost, while the Recovery Time Objective describes how quickly recovery should complete. Backup jobs must report failures, but a successful job report alone is insufficient. Operators should verify integrity, inspect expected files, and periodically restore into an isolated location. Recovery credentials and encryption keys must themselves be protected and recoverable.

This lab creates three logical copies under one classroom directory: a primary data set, a local backup copy, and a compressed archive representing an off-site transfer. Because all three remain on the same actual lab filesystem, the exercise demonstrates process and verification but does not physically satisfy the two-media or off-site requirements. A production implementation must place the backup destinations in genuinely independent failure domains. The final restore test extracts the archive into a separate restore directory and compares SHA-256 hashes with the original manifest. That test provides evidence that the selected files are present and unchanged, but it does not replace application-aware validation, malware scanning, database consistency checks, or a complete disaster-recovery exercise.

## Architecture

### production_pattern
Copy 1: active application data on primary storage.
Copy 2: versioned local backup on a separately managed storage device or system.
Copy 3: encrypted off-site backup in a separate facility, account, or provider failure domain.
At least one backup should be offline, immutable, or otherwise resistant to deletion through compromised production credentials.
Monitoring should alert on missed jobs, unexpected backup size changes, integrity failures, and approaching capacity limits.
Scheduled restore tests should validate both data and the documented recovery procedure.

### lab_topology
### primary
/opt/lab-classroom/class72/primary/

### local_backup
/opt/lab-classroom/class72/local-backup/

### simulated_offsite
/opt/lab-classroom/class72/simulated-offsite/

### restore_test
/opt/lab-classroom/class72/restore-test/

### control_data
/opt/lab-classroom/class72/control/

### important_limitation
The lab directories share one underlying filesystem and therefore represent logical roles only. They do not provide independent media, host, account, geographic, or disaster failure domains.

## Required reading

- CISA Stop Ransomware Guide, especially the recommendations for offline, encrypted, and regularly tested backups: https://www.cisa.gov/stopransomware/ransomware-guide
- NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/pubs/sp/800/34/r1/final
- Python hashlib documentation for understanding the SHA-256 integrity checks used in the lab: https://docs.python.org/3/library/hashlib.html
- Python tarfile documentation for understanding the archive and restore operations used in the lab: https://docs.python.org/3/library/tarfile.html

## References

- CISA, Stop Ransomware Guide: https://www.cisa.gov/stopransomware/ransomware-guide
- NIST Special Publication 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/pubs/sp/800/34/r1/final
- NIST Special Publication 800-209, Security Guidelines for Storage Infrastructure: https://csrc.nist.gov/pubs/sp/800/209/final
- Python 3 hashlib documentation: https://docs.python.org/3/library/hashlib.html
- Python 3 tarfile documentation: https://docs.python.org/3/library/tarfile.html
- Python 3 shutil documentation: https://docs.python.org/3/library/shutil.html

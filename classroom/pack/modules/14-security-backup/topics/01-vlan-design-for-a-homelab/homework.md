# Homework: VLAN Design for a Homelab

**Module:** Segmentation, Backup & Power
**Activity type:** Homework / independent application
**Objective:** Separate homelab devices into VLANs based on trust, function, and operational requirements

## Requirements

### task
Create a second design on paper for a camera VLAN using a new non-overlapping subnet.

### requirements
State whether cameras need DNS, NTP, or internet access
Name the exact management source, protocol, and destination port needed to administer cameras
Deny camera-initiated access to all internal zones
Identify which physical trunks, if any, must carry the new VLAN

### validation_goal
No trunk may receive the camera VLAN solely because it is convenient.
### task
Model removal of tagged management VLAN 10 from the hypervisor trunk.

### requirements
Add a separate physical management access port to the written architecture
Assign that port to VLAN 10 with matching untagged VLAN and PVID
Change the hypervisor workload trunk to VLANs 20 and 30 only
Describe the migration order that avoids losing host management

### validation_goal
The design must never leave the hypervisor unmanaged during the migration.
### task
Extend the validator conceptually for a voice VLAN.

### requirements
Reject duplicate VLAN IDs
Reject overlapping subnets
Require documented time and name-resolution services
Reject wildcard allow entries
Require unused ports to remain administratively down

### validation_goal
Write the proposed assertions in plain language or Python without changing live network equipment.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

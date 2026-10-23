# Homework: Firewall Segmentation and Trust Boundaries

**Module:** Segmentation, Backup & Power
**Activity type:** Homework / independent application
**Objective:** Define zones as groups of systems with similar trust and policy requirements.

## Requirements

### assignment
Add a backup zone using 10.71.50.0/24 and a backup-server flow to TCP 2049. Create one exact allow before default-deny and one negative flow proving users cannot reach that service.
Extend assert_results.py with expected rule names for both new flows rather than checking decisions alone.
Temporarily label the backup zone as RFC5737, run check_addressing.py, record why it fails, and then restore the correct RFC1918 label.
Temporarily change the external-test CIDR to 10.71.60.0/24 while leaving its label RFC5737, observe the failed standard check, and restore it with reset_data.py.
Draw a zone-and-arrow diagram showing all approved flows and mark each arrow with protocol, port, purpose, and initiating zone.
Write a short change plan describing how equivalent production rules would be staged without risking loss of administrative access. Do not apply it to the host.

### acceptance_criteria
The backup zone has a CIDR represented in the policy schema.
Every added flow contains source and destination addresses that validate against its zones.
The positive flow matches a specifically named allow rule.
The negative flow matches default-deny.
The learner can explain why 10.71.50.0/24 is RFC 1918 and 203.0.113.0/24 is RFC 5737.
The original class state can still be recovered by running reset_data.py.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

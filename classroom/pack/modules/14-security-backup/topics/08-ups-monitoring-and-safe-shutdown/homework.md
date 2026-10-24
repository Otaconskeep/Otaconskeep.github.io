# Homework: UPS Monitoring and Safe Shutdown

**Module:** Segmentation, Backup & Power
**Activity type:** Homework / independent application
**Objective:** Explain the roles of a UPS, UPS driver, monitoring daemon, client, and shutdown coordinator.

## Requirements

Extend the simulation with a sample containing OB but no LB and no runtime value. Document why the policy waits rather than assuming a critical battery condition.
Add an ALREADY_LATCHED test by supplying a fourth consecutive critical sample before the OL recovery sample.
Draw the shutdown dependency order for your homelab, including applications, databases, virtual machines, storage, hypervisors, monitoring, network equipment, and UPS authority.
Measure the graceful shutdown duration of each workload during a planned maintenance exercise, then explain how those observations would inform a site-specific threshold. Do not claim a universal threshold.
Write an incident checklist covering utility restoration, UPS health, battery recharge state, storage consistency, and staged service startup.
Identify which account in a proposed production architecture would have read-only monitoring access and which narrowly scoped component would have shutdown authority.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

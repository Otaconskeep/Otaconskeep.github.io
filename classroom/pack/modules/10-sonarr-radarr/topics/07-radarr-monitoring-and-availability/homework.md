# Homework: Radarr Monitoring and Availability

**Module:** Sonarr & Radarr
**Activity type:** Homework / independent application
**Objective:** Explain why a running Radarr process does not prove that movie automation is working

## Requirements

Add a fourth mock state named degraded that returns HTTP 200 with healthy set to false, then update the monitor to distinguish reachability from application health.
Extend the report with consecutive failure count logic stored in a file under /opt/lab-classroom/class46/.
Design an alert message containing the target, failure category, first observation time, latest status, and a concise operator action.
Draw a production monitoring plan that covers Radarr, its database, indexers, download clients, library storage, DNS, and reverse proxy.
Write a short policy explaining when a warning should escalate to a critical alert and when a recovery notification should be sent.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

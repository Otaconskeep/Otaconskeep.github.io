# Homework: ARR Stack Health Monitoring

**Module:** Requests & Media Servers
**Activity type:** Homework / independent application
**Objective:** Separate service reachability from application health state.

## Requirements

### workspace_rule
Make homework changes only beneath /opt/lab-classroom/class62/.

### tasks
Add a synthetic stale_data Boolean field. Define stale data as warning only when the service is reachable and no critical condition applies.
Add one positive stale-data test and one precedence test showing that declared critical remains critical even when stale_data is also true.
Keep the metric output at exactly four samples; do not introduce a high-cardinality reason label.
Add invalid-input tests for queue_depth=-1, free_space_percent=101, a missing radarr record, and an unknown declared_health value.
Write a short explanation of why an exporter execution failure should be monitored separately from arr_monitor_up.

### acceptance_criteria
All original six scenarios still pass.
The new stale-data scenarios have independent expected values.
HELP and TYPE ordering remains unchanged.
arr_monitor_up still permits only 0 and 1.
All edits and generated files remain in the class workspace.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

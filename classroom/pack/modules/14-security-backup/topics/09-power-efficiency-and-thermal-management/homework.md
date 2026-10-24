# Homework: Power Efficiency and Thermal Management

**Module:** Segmentation, Backup & Power
**Activity type:** Homework / independent application
**Objective:** Explain the difference between energy, power, temperature, utilization, and efficiency.

## Requirements

### assignment
Create a table identifying every metric present in observations.csv, its unit, its likely measurement domain, and one limitation.
Compare idle_end with the load-phase and cooldown observations without claiming that the short workload is a benchmark.
If an energy counter is available, research its max_energy_range_uj and explain how wraparound would be handled. Do not report a whole-system wattage unless the counter is documented to cover the whole system.
Write a three-stage optimization proposal: one workload-level change, one cooling or airflow inspection, and one policy change requiring a separate maintenance window.
For each proposal, define the success metric, reliability guardrail, rollback trigger, and measurement method.
Identify one service that may wake the system frequently and describe a read-only method for investigating it in a future lab.

### submission_requirements
Submit context.txt, metric-counts.txt, a concise interpretation of available data, documented limitations, and the staged proposal. Remove hostnames, serial numbers, addresses, credentials, and other sensitive infrastructure identifiers.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

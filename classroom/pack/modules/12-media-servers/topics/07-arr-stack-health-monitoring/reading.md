# Reading: ARR Stack Health Monitoring

**Module:** Requests & Media Servers
**Activity type:** Reading (Learn)
**Objective:** Separate service reachability from application health state.

## Vocabulary

| Term | Meaning |
|---|---|
| ARR stack | A collection of media-management applications such as Sonarr and Radarr, commonly operated with download clients and media servers. |
| Reachability | Whether the monitor can successfully communicate with a service. In this lesson it is represented independently by arr_monitor_up. |
| Declared health | A synthetic application-provided state of healthy, warning, or critical. |
| Queue depth | The number of pending synthetic work items. A value greater than 25 produces warning state unless a critical condition has precedence. |
| Free-space percentage | The percentage of storage capacity still available. A value below 15 produces warning state unless a critical condition has precedence. |
| Gauge | A Prometheus metric type whose value can rise or fall directly. |
| Metric family | A metric name together with its HELP and TYPE metadata and all associated labeled samples. |
| Precedence | The order in which overlapping health conditions are evaluated so that a more severe condition cannot be hidden by a less severe one. |
| Synthetic fixture | Controlled input data used to exercise monitoring behavior without contacting a production service. |

## Instruction

Health monitoring is more useful when it distinguishes transport success from application condition. A service can be reachable while reporting a critical internal state, and an unreachable service cannot provide trustworthy queue or storage information. For that reason, this lesson exposes two metric families. arr_monitor_up answers only whether the monitor could reach the service: 1 means reachable and 0 means unreachable. arr_monitor_state_number represents the classified health state: 2 means healthy, 1 means warning, and 0 means critical. These values must not be merged into a single ambiguous signal. A reachable service with declared_health set to critical therefore emits arr_monitor_up value 1 and arr_monitor_state_number value 0.

Classification follows explicit precedence. Unreachable is critical. A reachable service whose declared health is critical is also critical. Only after those checks does the exporter evaluate warning conditions: declared warning, queue depth greater than 25, or free-space percentage below 15. If none apply, the service is healthy. The comparisons are intentionally strict. Queue depth 25 is healthy when no other warning exists, while 26 is warning. Free space 15 is healthy, while 14.9 is warning. Writing these boundaries down prevents dashboards and alerts from disagreeing with the exporter.

Prometheus text exposition also has structural requirements. Each metric family should present its HELP line and TYPE line before samples from that family. The lab fixes the family order as arr_monitor_up followed by arr_monitor_state_number and fixes service order as sonarr followed by radarr. With two services and two families, every successful render must contain exactly four sample lines. Deterministic ordering is not required for Prometheus ingestion, but it makes reviews, diffs, and tests much clearer. Labels remain low-cardinality because the service label has only two permitted values.

The lab deliberately uses synthetic JSON rather than real API calls. This isolates classification logic from authentication, network failures, API-version differences, and production data. The verifier independently defines expected values for each scenario, checks the complete output text, checks metadata order, counts exactly four samples, enforces the exact sample set, and restricts arr_monitor_up to only 0 or 1. It executes both implemented warning branches rather than leaving them as untested intentions. Input validation rejects missing services, non-Boolean reachability, unsupported declared states, negative queue depths, and percentages outside zero through one hundred. A monitor should fail visibly on malformed data instead of publishing a plausible but false health result.

## Architecture

### components
### name
Synthetic JSON input

### role
Provides one record each for sonarr and radarr with reachable, declared_health, queue_depth, and free_space_percent fields.
### name
Python exporter

### role
Validates records, classifies health with deterministic precedence, and renders two Prometheus gauge families.
### name
Verification harness

### role
Executes six scenarios and checks exact output, family order, value domains, labels, sample count, and threshold behavior.
### name
Prometheus-compatible output

### role
Contains metadata and samples that could later be exposed by an HTTP collector, although this lab does not open a listener.

### data_flow
Synthetic JSON is loaded from a file or constructed in memory by the verifier.
The exporter validates both service records before rendering any metrics.
Reachability and health state are classified separately.
Metric families are emitted in a stable order with sonarr before radarr.
The verifier compares the complete rendered document with independently specified expectations.

### health_model
### reachability_metric
arr_monitor_up is 1 only when reachable is true; otherwise it is 0.

### state_metric
arr_monitor_state_number is 2 for healthy, 1 for warning, and 0 for critical.

### evaluation_order
Evaluate unreachable critical conditions first.
Evaluate reachable declared_health=critical next.
Evaluate warning conditions only when no critical condition matched.
Classify as healthy only when neither critical nor warning conditions matched.

### critical_conditions
reachable=false produces arr_monitor_up 0 and arr_monitor_state_number 0.
reachable=true with declared_health=critical produces arr_monitor_up 1 and arr_monitor_state_number 0.

### warning_conditions
reachable=true with declared_health=warning
reachable=true with queue_depth greater than 25
reachable=true with free_space_percent below 15

### healthy_conditions
reachable=true, declared_health=healthy, queue_depth at most 25, and free_space_percent at least 15

### boundary_rules
queue_depth=25 does not trigger a warning.
free_space_percent=15 does not trigger a warning.

### metric_contract
### family_order
arr_monitor_up
arr_monitor_state_number

### service_order
sonarr
radarr

### sample_count
4

### allowed_up_values
0
1

### allowed_state_values
0
1
2

## Required reading

- Prometheus exposition formats: https://prometheus.io/docs/instrumenting/exposition_formats/
- Prometheus metric and label naming practices: https://prometheus.io/docs/practices/naming/
- Prometheus instrumentation practices: https://prometheus.io/docs/practices/instrumentation/
- Python json module documentation: https://docs.python.org/3/library/json.html

## References

- Prometheus exposition formats: https://prometheus.io/docs/instrumenting/exposition_formats/
- Prometheus metric and label naming: https://prometheus.io/docs/practices/naming/
- Prometheus instrumentation practices: https://prometheus.io/docs/practices/instrumentation/
- Prometheus metric types: https://prometheus.io/docs/concepts/metric_types/
- Python json module: https://docs.python.org/3/library/json.html
- Python re module: https://docs.python.org/3/library/re.html
- Python pathlib module: https://docs.python.org/3/library/pathlib.html
- Python shutil module: https://docs.python.org/3/library/shutil.html

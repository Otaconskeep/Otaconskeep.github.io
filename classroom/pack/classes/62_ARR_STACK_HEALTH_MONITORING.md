# Class 62: ARR Stack Health Monitoring

**Learning objective:** Separate service reachability from application health state.; Apply deterministic precedence rules for critical, warning, and healthy classifications.; Represent reachability with arr_monitor_up and health with arr_monitor_state_number.; Generate valid Prometheus text exposition with HELP and TYPE metadata before samples.; Verify an exact four-sample metric set for two monitored services.; Prove the unreachable, reachable-but-critical, queue warning, low-storage warning, and threshold-boundary branches.; Reject invalid synthetic input instead of silently publishing misleading metrics.; Perform a path-guarded rollback confined to the class workspace.
**Bloom level:** Understand / Apply
**Track:** ARR Stack Operations · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Build and verify a synthetic health exporter that converts ARR-style reachability, declared health, queue depth, and storage data into deterministic Prometheus text metrics without requiring access to a live Sonarr or Radarr instance.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux distributions providing a POSIX-compatible shell and writable /opt/lab-classroom

### runtime
Python 3.8 or newer

### python_dependencies
Python standard library only

### network_required
False

### live_arr_services_required
False

### prometheus_server_required
False

### notes
The generated text follows the Prometheus text exposition conventions used by current Prometheus releases. The lab itself does not start a server or scrape endpoint.

## Learning objective

- Separate service reachability from application health state.
- Apply deterministic precedence rules for critical, warning, and healthy classifications.
- Represent reachability with arr_monitor_up and health with arr_monitor_state_number.
- Generate valid Prometheus text exposition with HELP and TYPE metadata before samples.
- Verify an exact four-sample metric set for two monitored services.
- Prove the unreachable, reachable-but-critical, queue warning, low-storage warning, and threshold-boundary branches.
- Reject invalid synthetic input instead of silently publishing misleading metrics.
- Perform a path-guarded rollback confined to the class workspace.

## Why this matters

Build and verify a synthetic health exporter that converts ARR-style reachability, declared health, queue depth, and storage data into deterministic Prometheus text metrics without requiring access to a live Sonarr or Radarr instance.

## Prerequisites

- Basic familiarity with Sonarr and Radarr as services in an ARR stack
- Ability to run shell commands and Python 3
- Basic understanding of Prometheus metrics, labels, gauges, and alert thresholds
- Write permission for /opt/lab-classroom/class62/
- No live ARR API credentials are required

## Required reading

- Prometheus exposition formats: https://prometheus.io/docs/instrumenting/exposition_formats/
- Prometheus metric and label naming practices: https://prometheus.io/docs/practices/naming/
- Prometheus instrumentation practices: https://prometheus.io/docs/practices/instrumentation/
- Python json module documentation: https://docs.python.org/3/library/json.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

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

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

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

## Feynman teach-back

### prompt
Explain the monitor to someone who knows only that Sonarr and Radarr are applications.

### model_explanation
The monitor asks two different questions. First, can it talk to the application? That answer becomes arr_monitor_up, using 1 for yes and 0 for no. Second, what condition is the application in? That becomes a state number: 2 healthy, 1 warning, or 0 critical. These questions must stay separate because an application can answer successfully while reporting a serious internal problem. Unreachable and declared critical conditions win over warnings. If neither critical condition exists, a queue over 25 or free space below 15 causes warning. Two applications multiplied by two metrics produces exactly four samples.

### self_check
Can you explain why reachable and healthy are not synonyms?
Can you state why reachable declared critical produces values 1 and 0 rather than 0 and 0?
Can you explain why queue depth 25 and free space 15 are healthy boundaries?
Can you account for all four expected samples without looking at the code?

## Retrieval check

1. 1. What does arr_monitor_up measure, and which values may it emit?
2. 2. What two metrics are emitted for a reachable service whose declared_health is critical?
3. 3. List the warning conditions evaluated after critical conditions.
4. 4. Do queue_depth=25 and free_space_percent=15 trigger warnings?
5. 5. Why must HELP and TYPE lines be checked before samples in this lab?
6. 6. How many sample lines must a successful render contain, and why?
7. 7. Why is synthetic input preferable to a live ARR API for testing the classification rules?
8. 8. What should a verifier do when reachable is the string "yes" instead of a Boolean?

## Guided lab

### workspace
/opt/lab-classroom/class62/

### mutation_scope
Every file created or modified by this lab is beneath /opt/lab-classroom/class62/.

### steps
### step
1

### title
Create the isolated class workspace

### command
mkdir -p /opt/lab-classroom/class62 && cd /opt/lab-classroom/class62 && pwd

### explanation
The printed working directory must be /opt/lab-classroom/class62. Stop if the account cannot create or write this directory.
### step
2

### title
Create the synthetic exporter

### command
cat > /opt/lab-classroom/class62/exporter.py <<'PY'
#!/usr/bin/env python3
import json
import sys

SERVICES = ("sonarr", "radarr")
STATE_NUMBER = {"critical": 0, "warning": 1, "healthy": 2}


def validate_record(service, record):
    if not isinstance(record, dict):
        raise ValueError(f"{service}: record must be an object")
    reachable = record.get("reachable")
    if not isinstance(reachable, bool):
        raise ValueError(f"{service}: reachable must be a Boolean")
    declared = record.get("declared_health")
    if declared not in STATE_NUMBER:
        raise ValueError(f"{service}: declared_health must be healthy, warning, or critical")
    queue_depth = record.get("queue_depth")
    if isinstance(queue_depth, bool) or not isinstance(queue_depth, (int, float)) or queue_depth < 0:
        raise ValueError(f"{service}: queue_depth must be a non-negative number")
    free_space = record.get("free_space_percent")
    if isinstance(free_space, bool) or not isinstance(free_space, (int, float)) or not 0 <= free_space <= 100:
        raise ValueError(f"{service}: free_space_percent must be between 0 and 100")


def classify(record):
    if not record["reachable"]:
        return "critical"
    if record["declared_health"] == "critical":
        return "critical"
    if record["declared_health"] == "warning":
        return "warning"
    if record["queue_depth"] > 25:
        return "warning"
    if record["free_space_percent"] < 15:
        return "warning"
    return "healthy"


def render(payload):
    if not isinstance(payload, dict):
        raise ValueError("top-level input must be an object")
    if set(payload) != set(SERVICES):
        raise ValueError("input must contain exactly sonarr and radarr")
    for service in SERVICES:
        validate_record(service, payload[service])

    lines = [
        "# HELP arr_monitor_up Whether the monitor can reach the service.",
        "# TYPE arr_monitor_up gauge",
    ]
    for service in SERVICES:
        value = 1 if payload[service]["reachable"] else 0
        lines.append(f'arr_monitor_up{{service="{service}"}} {value}')

    lines.extend([
        "# HELP arr_monitor_state_number Health state where critical=0, warning=1, healthy=2.",
        "# TYPE arr_monitor_state_number gauge",
    ])
    for service in SERVICES:
        state = classify(payload[service])
        lines.append(f'arr_monitor_state_number{{service="{service}"}} {STATE_NUMBER[state]}')
    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} INPUT.json")
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    print(render(payload))


if __name__ == "__main__":
    main()
PY

### explanation
The exporter has no external dependencies and does not contact live services.
### step
3

### title
Create a baseline input

### command
cat > /opt/lab-classroom/class62/sample.json <<'JSON'
{
  "sonarr": {
    "reachable": true,
    "declared_health": "healthy",
    "queue_depth": 4,
    "free_space_percent": 60
  },
  "radarr": {
    "reachable": true,
    "declared_health": "healthy",
    "queue_depth": 2,
    "free_space_percent": 55
  }
}
JSON
cd /opt/lab-classroom/class62 && python3 exporter.py sample.json

### explanation
The baseline must show two reachable samples with value 1 and two healthy state samples with value 2.
### step
4

### title
Create the exact-output verifier

### command
cat > /opt/lab-classroom/class62/verify.py <<'PY'
#!/usr/bin/env python3
import re
from exporter import render

SERVICES = ("sonarr", "radarr")
HELP_UP = "# HELP arr_monitor_up Whether the monitor can reach the service."
TYPE_UP = "# TYPE arr_monitor_up gauge"
HELP_STATE = "# HELP arr_monitor_state_number Health state where critical=0, warning=1, healthy=2."
TYPE_STATE = "# TYPE arr_monitor_state_number gauge"
UP_RE = re.compile(r'arr_monitor_up\{service="(sonarr|radarr)"\} ([01])')
STATE_RE = re.compile(r'arr_monitor_state_number\{service="(sonarr|radarr)"\} ([012])')


def service(reachable=True, declared="healthy", queue=0, free=50):
    return {
        "reachable": reachable,
        "declared_health": declared,
        "queue_depth": queue,
        "free_space_percent": free,
    }


def expected_text(up, state):
    lines = [HELP_UP, TYPE_UP]
    lines.extend(f'arr_monitor_up{{service="{name}"}} {up[name]}' for name in SERVICES)
    lines.extend([HELP_STATE, TYPE_STATE])
    lines.extend(f'arr_monitor_state_number{{service="{name}"}} {state[name]}' for name in SERVICES)
    return "\n".join(lines)


def check_case(name, payload, expected_up, expected_state):
    actual = render(payload)
    expected = expected_text(expected_up, expected_state)
    assert actual == expected, f"{name}: complete metric document differs\nEXPECTED:\n{expected}\nACTUAL:\n{actual}"

    lines = actual.splitlines()
    assert lines[0] == HELP_UP, f"{name}: arr_monitor_up HELP is not first"
    assert lines[1] == TYPE_UP, f"{name}: arr_monitor_up TYPE is not before its samples"
    assert lines[4] == HELP_STATE, f"{name}: state HELP is not before state samples"
    assert lines[5] == TYPE_STATE, f"{name}: state TYPE is not before state samples"

    samples = [line for line in lines if not line.startswith("#")]
    assert len(samples) == 4, f"{name}: expected exactly four samples, got {len(samples)}"
    expected_samples = {line for line in expected.splitlines() if not line.startswith("#")}
    assert set(samples) == expected_samples, f"{name}: sample set is not exact"

    up_matches = [UP_RE.fullmatch(line) for line in samples if line.startswith("arr_monitor_up{")]
    state_matches = [STATE_RE.fullmatch(line) for line in samples if line.startswith("arr_monitor_state_number{")]
    assert len(up_matches) == 2 and all(up_matches), f"{name}: invalid up label or value; only 0 and 1 are allowed"
    assert len(state_matches) == 2 and all(state_matches), f"{name}: invalid state label or value"
    assert {match.group(1) for match in up_matches} == set(SERVICES), f"{name}: up service set is incomplete"
    assert {match.group(1) for match in state_matches} == set(SERVICES), f"{name}: state service set is incomplete"
    print(f"PASS {name}")


CASES = [
    (
        "baseline healthy",
        {"sonarr": service(queue=4, free=60), "radarr": service(queue=2, free=55)},
        {"sonarr": 1, "radarr": 1},
        {"sonarr": 2, "radarr": 2},
    ),
    (
        "unreachable is critical",
        {"sonarr": service(reachable=False), "radarr": service()},
        {"sonarr": 0, "radarr": 1},
        {"sonarr": 0, "radarr": 2},
    ),
    (
        "reachable declared critical",
        {"sonarr": service(), "radarr": service(reachable=True, declared="critical")},
        {"sonarr": 1, "radarr": 1},
        {"sonarr": 2, "radarr": 0},
    ),
    (
        "queue depth warning",
        {"sonarr": service(queue=26), "radarr": service()},
        {"sonarr": 1, "radarr": 1},
        {"sonarr": 1, "radarr": 2},
    ),
    (
        "low free space warning",
        {"sonarr": service(), "radarr": service(free=14.9)},
        {"sonarr": 1, "radarr": 1},
        {"sonarr": 2, "radarr": 1},
    ),
    (
        "warning boundaries remain healthy",
        {"sonarr": service(queue=25), "radarr": service(free=15)},
        {"sonarr": 1, "radarr": 1},
        {"sonarr": 2, "radarr": 2},
    ),
]

for case in CASES:
    check_case(*case)

print("PASS all 6 scenarios; metadata order and exact four-sample sets verified")
PY
cd /opt/lab-classroom/class62 && python3 verify.py

### explanation
This executes the queue-depth and free-space warning branches, the reachable declared-critical branch, the unreachable branch, and both strict threshold boundaries.
### step
5

### title
Confirm malformed input is rejected

### command
cd /opt/lab-classroom/class62 && python3 - <<'PY'
from exporter import render

bad = {
    "sonarr": {
        "reachable": "yes",
        "declared_health": "healthy",
        "queue_depth": 0,
        "free_space_percent": 50
    },
    "radarr": {
        "reachable": True,
        "declared_health": "healthy",
        "queue_depth": 0,
        "free_space_percent": 50
    }
}

try:
    render(bad)
except ValueError as error:
    print(f"PASS malformed input rejected: {error}")
else:
    raise SystemExit("FAIL malformed input was accepted")
PY

### explanation
The exporter must reject a string masquerading as a Boolean rather than treating it as a truthy value.

## Expected results

- The baseline exporter output contains HELP and TYPE metadata for arr_monitor_up followed by two up samples, then HELP and TYPE metadata for arr_monitor_state_number followed by two state samples.
- Every successful scenario contains exactly four sample lines: one sample per service for each of the two metric families.
- The verifier prints PASS baseline healthy.
- The verifier prints PASS unreachable is critical.
- The verifier prints PASS reachable declared critical and confirms that the affected service has arr_monitor_up 1 with arr_monitor_state_number 0.
- The verifier prints PASS queue depth warning for queue_depth 26.
- The verifier prints PASS low free space warning for free_space_percent 14.9.
- The verifier prints PASS warning boundaries remain healthy for queue_depth 25 and free_space_percent 15.
- The verifier prints PASS all 6 scenarios; metadata order and exact four-sample sets verified.
- The malformed-input test prints PASS malformed input rejected.

## Verification checkpoints

- [ ] Run: cd /opt/lab-classroom/class62 && python3 verify.py
- [ ] Require an exit status of 0 from verify.py; any assertion failure makes verification unsuccessful.
- [ ] Require exactly six scenario lines beginning with PASS plus the final summary line.
- [ ] Run: cd /opt/lab-classroom/class62 && python3 exporter.py sample.json
- [ ] Confirm the baseline document has exactly eight lines: two metadata lines and two samples for arr_monitor_up, followed by two metadata lines and two samples for arr_monitor_state_number.
- [ ] Confirm the verifier's full-match expression for arr_monitor_up permits only values 0 and 1; value 2 must fail verification.
- [ ] Confirm the verifier compares the complete output text, so HELP and TYPE family ordering cannot change unnoticed.
- [ ] Confirm the verifier counts exactly four samples and compares their set with the four independently expected samples.
- [ ] Run: cd /opt/lab-classroom/class62 && python3 -m py_compile exporter.py verify.py
- [ ] Require an exit status of 0 from the compilation check.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| mkdir reports permission denied for /opt/lab-classroom/class62. | The current account does not have the prerequisite write access to the classroom root. | Have the lab administrator pre-create /opt/lab-classroom with ownership appropriate for the training account, then repeat the workspace step. Do not redirect the exercise into an unrelated production path. |
| The verifier reports that the complete metric document differs. | A metric name, metadata string, family order, service order, or expected numeric value was changed. | Compare the EXPECTED and ACTUAL blocks printed by the assertion. Restore the documented HELP and TYPE lines, sonarr-before-radarr ordering, and health precedence. |
| The queue depth warning scenario returns state 2. | The queue comparison was implemented as greater than or equal to a different threshold, or queue_depth was not checked. | Ensure classify uses queue_depth > 25 after the critical checks and before the healthy return. |
| The low free-space scenario returns state 2. | The storage comparison is reversed or uses the wrong boundary. | Ensure classify uses free_space_percent < 15. A value of 14.9 must warn, while exactly 15 must remain healthy when no other condition applies. |
| A reachable service with declared_health critical has arr_monitor_up 0. | Application health was incorrectly used to determine transport reachability. | Derive arr_monitor_up only from the reachable Boolean. Keep the state metric responsible for the critical application condition. |
| A grep -q spot check prints no output and is mistaken for a failed check. | grep -q is intentionally silent whether it finds a match; success is communicated through exit status 0. | Inspect the exit status, for example by running the check and then printf 'exit=%s\n' "$?". Treat only a non-zero exit status as failure; do not use lack of output as the failure signal. |
| The malformed-input test says the input was accepted. | Reachability validation was weakened to truthiness instead of requiring an actual Boolean. | Restore the isinstance(reachable, bool) validation before classification. |
| Python reports ModuleNotFoundError for exporter. | verify.py was launched from outside the class directory or exporter.py was not created. | Confirm both files exist under /opt/lab-classroom/class62 and run cd /opt/lab-classroom/class62 && python3 verify.py. |

## Security considerations

### principles
The exercise uses synthetic fixtures and requires no production ARR URL, API key, cookie, or media-library path.
Do not replace the fixtures with production responses that may contain hostnames, paths, titles, or credentials.
Metric labels are restricted to sonarr and radarr to prevent unbounded label cardinality.
The exporter opens no network listener and makes no outbound requests.
Input is validated before any metric document is returned, reducing the risk of silently publishing false health data.
All lab-created files remain under /opt/lab-classroom/class62/.

### production_guidance
A production implementation should retrieve secrets from an access-controlled secret source, use timeouts, avoid logging authentication material, expose only non-sensitive labels, and separately monitor exporter execution failures.

## Rollback

### scope
/opt/lab-classroom/class62/

### command
python3 - <<'PY'
from pathlib import Path
import shutil

p = Path("/opt/lab-classroom/class62")
expected = Path("/opt/lab-classroom/class62")
assert p == expected and p.parent == Path("/opt/lab-classroom"), f"refusing unexpected path: {p}"
shutil.rmtree(p)
PY

### behavior
The path assertion executes inside the same Python process before deletion. The operation does not suppress missing-file, permission, or partial-deletion errors.

### post_check
test ! -e /opt/lab-classroom/class62 && printf '%s\n' 'rollback verified: class62 workspace absent'

## Video narration notes

### opening
In this class we will build a small, deterministic health exporter for two representative ARR services. The goal is not to connect to production. The goal is to prove the health model before any network integration is added.

### segments
Start by separating reachability from application state. Point out that a service can answer a request and still report critical health.
Walk through the precedence rules. Unreachable and declared critical are critical. Declared warning, queue depth above 25, and free space below 15 are warnings only if no critical condition matched.
Show the baseline Prometheus document. Identify HELP, TYPE, the two arr_monitor_up samples, and the two arr_monitor_state_number samples.
Run the verifier and pause on the reachable declared-critical scenario. Emphasize the combination of up value 1 and state value 0.
Highlight the queue depth 26 and free-space 14.9 tests. Then contrast them with the healthy boundaries of 25 and 15.
Explain that the validator checks the complete output, metadata order, exactly four samples, exact labels, and strict value domains. In particular, arr_monitor_up value 2 cannot match.
Finish with malformed-input rejection and the path-guarded rollback procedure.

### closing
A useful health exporter is not just code that prints numbers. It is a documented contract whose branches, boundaries, labels, and failure behavior can be reproduced and verified.

## References

- Prometheus exposition formats: https://prometheus.io/docs/instrumenting/exposition_formats/
- Prometheus metric and label naming: https://prometheus.io/docs/practices/naming/
- Prometheus instrumentation practices: https://prometheus.io/docs/practices/instrumentation/
- Prometheus metric types: https://prometheus.io/docs/concepts/metric_types/
- Python json module: https://docs.python.org/3/library/json.html
- Python re module: https://docs.python.org/3/library/re.html
- Python pathlib module: https://docs.python.org/3/library/pathlib.html
- Python shutil module: https://docs.python.org/3/library/shutil.html

## Mastery gate

- [ ] Objectives demonstrated with evidence
- [ ] Feynman complete
- [ ] Quiz self-scored ≥80%
- [ ] Lab verification boxes checked
- [ ] Rollback understood

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Return to this class whenever a later service fails for identity, process, log, remote access, update, or routing reasons covered here.

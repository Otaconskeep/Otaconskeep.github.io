# Lab: ARR Stack Health Monitoring

**Module:** Requests & Media Servers
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Separate service reachability from application health state.

## Before you start

- Basic familiarity with Sonarr and Radarr as services in an ARR stack
- Ability to run shell commands and Python 3
- Basic understanding of Prometheus metrics, labels, gauges, and alert thresholds
- Write permission for /opt/lab-classroom/class62/
- No live ARR API credentials are required

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

## Verification

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

## Security

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

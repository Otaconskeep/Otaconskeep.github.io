# Lab: UPS Monitoring and Safe Shutdown

**Module:** Segmentation, Backup & Power
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain the roles of a UPS, UPS driver, monitoring daemon, client, and shutdown coordinator.

## Before you start

- Basic Linux command-line navigation
- Ability to read JSON and run Python 3 scripts
- A pre-created, writable /opt/lab-classroom/class77/ directory
- Basic understanding of electrical power, batteries, and graceful operating-system shutdown
- Familiarity with client-server monitoring concepts

## Guided lab

### scope
All files created or changed by this lab remain under /opt/lab-classroom/class77/. The exercise uses simulated data and must not be connected to a production shutdown hook.

### safety_boundary
Do not unplug a UPS or utility feed for this exercise.
Do not run an operating-system poweroff command.
Do not run a UPS output-removal command.
Do not install or edit system services, scheduled tasks, or production NUT configuration.
Run the commands as a user already authorized to write only to the classroom directory.

### steps
### step
1

### title
Enter and confirm the classroom workspace

### commands
cd /opt/lab-classroom/class77/
pwd

### notes
The printed path must be exactly /opt/lab-classroom/class77 before creating any artifacts.
### step
2

### title
Create deterministic simulated UPS samples

### commands
cat > samples.jsonl <<'EOF'
{"age_seconds":1,"battery_charge":100,"runtime_seconds":1800,"status":"OL"}
{"age_seconds":2,"battery_charge":78,"runtime_seconds":900,"status":"OB"}
{"age_seconds":2,"battery_charge":24,"runtime_seconds":280,"status":"OB LB"}
{"age_seconds":3,"battery_charge":22,"runtime_seconds":260,"status":"OB LB"}
{"age_seconds":4,"battery_charge":20,"runtime_seconds":240,"status":"OB LB"}
{"age_seconds":1,"battery_charge":26,"runtime_seconds":700,"status":"OL CHRG"}
{"age_seconds":2,"battery_charge":18,"runtime_seconds":220,"status":"OB LB"}
EOF

### notes
The sequence contains online operation, an on-battery event, three consecutive critical samples, recovery, and one new critical sample after recovery.
### step
3

### title
Create the simulated shutdown decision engine

### commands
cat > ups_guard.py <<'PY'
import json
import pathlib
import sys

ROOT = pathlib.Path('/opt/lab-classroom/class77').resolve()
STATE_PATH = ROOT / 'state.json'
EVENT_PATH = ROOT / 'events.jsonl'
MAX_AGE_SECONDS = 30
RUNTIME_THRESHOLD_SECONDS = 300
REQUIRED_CRITICAL_SAMPLES = 3

if pathlib.Path.cwd().resolve() != ROOT:
    raise SystemExit('Refusing to run outside the class77 workspace')

if STATE_PATH.exists():
    state = json.loads(STATE_PATH.read_text())
else:
    state = {'low_count': 0, 'latched': False}

for sequence, line in enumerate(sys.stdin, start=1):
    sample = json.loads(line)
    age = sample.get('age_seconds')
    runtime = sample.get('runtime_seconds')
    tokens = set(str(sample.get('status', '')).split())
    action = 'NO_ACTION'
    reason = 'No policy condition matched'

    if not isinstance(age, (int, float)) or age > MAX_AGE_SECONDS:
        state['low_count'] = 0
        action = 'DATA_STALE'
        reason = 'Telemetry is missing a valid age or is older than the permitted age'
    elif 'OL' in tokens:
        state = {'low_count': 0, 'latched': False}
        action = 'ONLINE'
        reason = 'Utility power is reported available; incident latch cleared'
    elif 'OB' in tokens:
        critical = 'LB' in tokens or (
            isinstance(runtime, (int, float)) and
            runtime <= RUNTIME_THRESHOLD_SECONDS
        )
        if critical:
            state['low_count'] += 1
            if state['low_count'] >= REQUIRED_CRITICAL_SAMPLES:
                if state['latched']:
                    action = 'ALREADY_LATCHED'
                    reason = 'A shutdown request was already issued for this incident'
                else:
                    state['latched'] = True
                    action = 'SHUTDOWN_REQUESTED'
                    reason = 'Critical battery state was confirmed by consecutive samples'
            else:
                action = 'LOW_BATTERY_CONFIRMING'
                reason = 'Critical state observed but confirmation count is incomplete'
        else:
            state['low_count'] = 0
            action = 'ON_BATTERY_WAIT'
            reason = 'On battery without a confirmed critical condition'
    else:
        state['low_count'] = 0
        action = 'UNKNOWN_STATUS'
        reason = 'Neither online nor on-battery status was reported'

    event = {
        'action': action,
        'latched': state['latched'],
        'low_count': state['low_count'],
        'reason': reason,
        'sequence': sequence,
        'status_tokens': sorted(tokens)
    }
    with EVENT_PATH.open('a', encoding='utf-8') as event_file:
        event_file.write(json.dumps(event, sort_keys=True) + '\n')
    STATE_PATH.write_text(json.dumps(state, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(event, sort_keys=True))
PY

### notes
The script checks its working directory before writing. Its decision output is a simulation label only; it contains no host shutdown operation.
### step
4

### title
Initialize state and run the simulation

### commands
printf '%s\n' '{"latched": false, "low_count": 0}' > state.json
printf '' > events.jsonl
python3 ups_guard.py < samples.jsonl > actual-events.jsonl
cat actual-events.jsonl

### notes
The fifth sample should produce SHUTDOWN_REQUESTED after three consecutive critical samples. Recovery clears the latch, and the final sample begins a new confirmation sequence without requesting shutdown.
### step
5

### title
Test stale telemetry handling

### commands
printf '%s\n' '{"age_seconds":90,"battery_charge":10,"runtime_seconds":120,"status":"OB LB"}' > stale-sample.jsonl
printf '%s\n' '{"latched": false, "low_count": 0}' > state.json
printf '' > events.jsonl
python3 ups_guard.py < stale-sample.jsonl > stale-result.jsonl
cat stale-result.jsonl

### notes
The action must be DATA_STALE rather than SHUTDOWN_REQUESTED because the simulated observation is older than the accepted age.

## Expected results

- The normal seven-sample run produces exactly one SHUTDOWN_REQUESTED action.
- The first OL sample produces ONLINE and leaves the latch false.
- The noncritical OB sample produces ON_BATTERY_WAIT.
- The first two critical samples produce LOW_BATTERY_CONFIRMING.
- The third consecutive critical sample produces SHUTDOWN_REQUESTED and sets the latch true.
- The recovery sample containing OL clears the counter and latch.
- The final critical sample starts a new confirmation sequence with low_count equal to 1 and does not request shutdown.
- The stale sample produces DATA_STALE and does not produce SHUTDOWN_REQUESTED.
- All generated files remain under /opt/lab-classroom/class77/.

## Verification

- [ ] Run `pwd` from the lab shell and confirm the output is exactly `/opt/lab-classroom/class77`.
- [ ] Run `grep -c '"action": "SHUTDOWN_REQUESTED"' actual-events.jsonl` after the normal simulation; the result should be `1`.
- [ ] Run `grep -c '"action": "DATA_STALE"' stale-result.jsonl` after the stale-data test; the result should be `1`.
- [ ] Run `grep -c '"action": "SHUTDOWN_REQUESTED"' stale-result.jsonl`; the result should be `0`.
- [ ] Run `wc -l < actual-events.jsonl`; the result should be `7`.
- [ ] Run `tail -n 1 actual-events.jsonl` and confirm it contains `LOW_BATTERY_CONFIRMING`, `"latched": false`, and `"low_count": 1`.
- [ ] Run `find /opt/lab-classroom/class77/ -maxdepth 1 -type f -printf '%f\n' | sort` and review that the artifacts are confined to the classroom directory.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The shell reports that /opt/lab-classroom/class77 does not exist or is not writable. | The classroom workspace was not provisioned with the required ownership before the lesson. | Stop the lab and ask the classroom administrator to provision the directory. Do not redirect the exercise into a system configuration directory. |
| The script exits with a message that it refuses to run outside the workspace. | The current working directory is not exactly /opt/lab-classroom/class77. | Change to /opt/lab-classroom/class77, verify with pwd, and rerun the script. |
| Python reports a JSON decoding error. | A JSON line in samples.jsonl, stale-sample.jsonl, or state.json is incomplete or has invalid punctuation. | Recreate the affected file from the lesson and ensure that each sample occupies one complete line. |
| More than one shutdown request appears after repeating the normal test. | events.jsonl or actual-events.jsonl contains results from an earlier run, or state was reset at an unintended point. | Reinitialize state.json and truncate events.jsonl as shown before running the complete sample sequence again. |
| The third critical sample remains in LOW_BATTERY_CONFIRMING. | A preceding sample lacked OB, was stale, or reset the consecutive critical-sample counter. | Inspect samples.jsonl and actual-events.jsonl in sequence order. Confirm that the three critical samples all contain OB and either LB or a numeric runtime at or below the demonstration threshold. |
| A stale sample causes a shutdown request. | The age check was removed, altered, or placed after the critical-state action. | Restore the supplied script so freshness is checked before OL, OB, LB, or runtime policy evaluation. |
| A real UPS reports different status tokens or lacks runtime data. | UPS models and drivers expose different capabilities and combinations of normalized variables. | Consult the driver and NUT documentation for the device. Design policy around confirmed available variables and never invent missing telemetry. |

## Security

### principles
Separate read-only telemetry access from shutdown authority.
Grant shutdown capability only to the minimum required service identity.
Restrict UPS monitoring interfaces to trusted management networks and approved clients.
Treat UPS server credentials and shutdown secrets as operational secrets.
Protect state and event logs from unauthorized modification because altered telemetry or latch state can influence availability.
Use authenticated and encrypted transport where the selected UPS monitoring stack supports it; otherwise isolate the monitoring path on a trusted network.
Ensure only one designated controller can perform final UPS output removal.
Alert on stale telemetry, repeated authentication failures, unauthorized configuration changes, and unexpected shutdown requests.

### threats
A forged low-battery state could create an availability attack.
A forged online state could suppress shutdown until battery exhaustion.
Credential theft could let an attacker request host shutdown or remove UPS output.
A duplicate controller could race with the authorized shutdown coordinator.
Unprotected logs could disclose infrastructure names, device addresses, or outage patterns.

### production_guidance
Before enabling automation, review service-account permissions, network exposure, credential storage, log ownership, shutdown ordering, and recovery behavior. Test policy with simulation and maintenance-window exercises before allowing any component to control real power.

## Rollback

### lab_reset
Remain in /opt/lab-classroom/class77/.
Reset policy state with `printf '%s\n' '{"latched": false, "low_count": 0}' > state.json`.
Reset the event log with `printf '' > events.jsonl`.
Reset captured output with `printf '' > actual-events.jsonl` and `printf '' > stale-result.jsonl`.
No service restart, package removal, host reboot, or UPS operation is required.

### production_recovery_principle
If a production automation rollout behaves unexpectedly, disable only the shutdown action path through the site's approved change process while preserving telemetry and logs. Do not clear an active incident merely to silence alerts. Confirm utility power, UPS state, workload integrity, and shutdown-authority ownership before re-enabling automation.

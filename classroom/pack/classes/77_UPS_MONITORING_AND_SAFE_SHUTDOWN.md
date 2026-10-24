# Class 77: UPS Monitoring and Safe Shutdown

**Learning objective:** Explain the roles of a UPS, UPS driver, monitoring daemon, client, and shutdown coordinator.; Interpret common Network UPS Tools status tokens such as OL, OB, and LB.; Distinguish a short utility interruption from a sustained low-battery condition.; Design a shutdown policy with confirmation, stale-data handling, and action latching.; Explain why dependent workloads should stop before storage, hypervisors, and the final shutdown authority.; Validate a shutdown policy using deterministic simulated input rather than a live power failure.; Identify security risks associated with network-accessible UPS monitoring and shutdown credentials.
**Bloom level:** Understand / Apply
**Track:** Homelab Reliability and Operations · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Teach operators how to interpret UPS state, design a conservative shutdown policy, prevent duplicate shutdown requests, and validate the policy with simulated Network UPS Tools data without changing host power settings or interacting with real UPS hardware.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### lab_platforms
Linux systems with Python 3 and a POSIX-compatible shell
Containers or virtual machines where /opt/lab-classroom/class77/ is writable

### production_context
The policy concepts apply to NUT-based physical hosts, virtualized environments, and mixed homelabs.
UPS variables and status capabilities vary by hardware model, connection type, driver, firmware, and NUT version.
The simulation does not require NUT packages, a UPS device, init-system integration, or root privileges.
Production configuration syntax must be checked against the locally installed NUT manual pages and package documentation.

### limitations
The demonstration threshold of 300 runtime seconds is an instructional value and is not a recommendation for every environment.
The lab uses a local JSON state file and is not a distributed consensus mechanism.
The lab does not test real battery capacity, UPS transfer behavior, workload shutdown duration, or electrical wiring.
The lab does not issue a real host shutdown or UPS output-removal operation.

## Learning objective

- Explain the roles of a UPS, UPS driver, monitoring daemon, client, and shutdown coordinator.
- Interpret common Network UPS Tools status tokens such as OL, OB, and LB.
- Distinguish a short utility interruption from a sustained low-battery condition.
- Design a shutdown policy with confirmation, stale-data handling, and action latching.
- Explain why dependent workloads should stop before storage, hypervisors, and the final shutdown authority.
- Validate a shutdown policy using deterministic simulated input rather than a live power failure.
- Identify security risks associated with network-accessible UPS monitoring and shutdown credentials.

## Why this matters

Teach operators how to interpret UPS state, design a conservative shutdown policy, prevent duplicate shutdown requests, and validate the policy with simulated Network UPS Tools data without changing host power settings or interacting with real UPS hardware.

## Prerequisites

- Basic Linux command-line navigation
- Ability to read JSON and run Python 3 scripts
- A pre-created, writable /opt/lab-classroom/class77/ directory
- Basic understanding of electrical power, batteries, and graceful operating-system shutdown
- Familiarity with client-server monitoring concepts

## Required reading

- Network UPS Tools documentation: https://networkupstools.org/docs/
- NUT upsc client documentation: https://networkupstools.org/docs/man/upsc.html
- NUT upsmon documentation: https://networkupstools.org/docs/man/upsmon.html
- NUT upssched documentation: https://networkupstools.org/docs/man/upssched.html
- NUT status data documentation: https://networkupstools.org/docs/developer-guide.chunked/apas01.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| UPS | An uninterruptible power supply that provides temporary battery-backed power and may expose telemetry such as line state, battery charge, load, and estimated runtime. |
| NUT | Network UPS Tools, a collection of drivers, servers, clients, and monitoring components used to expose and act on UPS information. |
| OL | A common NUT status token meaning the UPS is online and utility power is available. |
| OB | A common NUT status token meaning the UPS is operating on battery. |
| LB | A common NUT status token indicating a low-battery condition. |
| Runtime estimate | A UPS-provided estimate of remaining battery operation. It can change with load, battery condition, temperature, and device implementation, so it should not be treated as an exact countdown. |
| Debounce | Requiring a condition to remain present or be observed repeatedly before taking action, reducing reactions to transient or noisy state changes. |
| Latch | Persistent state recording that a shutdown request has already been issued, preventing repeated requests while the same incident remains active. |
| Stale telemetry | UPS data that has not been refreshed recently enough to support a safe automated decision. |
| Shutdown authority | The specifically authorized component allowed to request host shutdown or command the UPS to remove output power. |

## Instruction

A UPS does not create unlimited runtime. Its purpose is to bridge short outages, condition power where supported, and provide enough time for an orderly response when utility power does not return. Safe automation therefore begins with a policy rather than a single threshold. The policy must identify which signals are trusted, how old the data may be, how long a condition must persist, which systems shut down first, and which component has final authority.

In a typical NUT design, a hardware-specific driver communicates with the UPS. The NUT server exposes normalized variables, while monitoring clients observe status and initiate policy actions. Common status tokens include OL for online, OB for on battery, and LB for low battery. Multiple tokens may appear together. Operators should evaluate tokens as a set rather than assuming the status field contains one exact string. Runtime and charge values are useful supporting signals, but they are estimates and may vary as load or battery condition changes.

Immediate shutdown on the first OB sample is usually too aggressive because short utility interruptions may clear quickly. Waiting only for an estimated runtime to reach zero is too late because the estimate is not exact and shutdown itself requires time. A conservative policy can require several consecutive critical observations, or use a timer, before issuing a shutdown request. Thresholds must be selected from measured workload shutdown requirements, UPS behavior, and local risk tolerance; the example threshold in this class is a demonstration value, not a universal recommendation.

Automation must also fail safely when telemetry is stale. Old data cannot prove that power is healthy or that a critical condition persists. The appropriate response may be to alert and withhold a new automated action until state is confirmed. Existing incident state should be retained according to the production design, especially when loss of monitoring connectivity can occur during the same electrical event.

A latch prevents repeated shutdown requests. Once a request has been issued, subsequent low-battery samples should not launch additional shutdown workflows. The latch can be cleared after confirmed recovery, during a controlled operator reset, or according to a documented incident lifecycle. In clustered environments, latching and coordination may need shared state so two controllers do not issue conflicting actions.

Shutdown order matters. Applications should stop accepting work, transactional services should flush state, virtual machines and containers should stop, dependent storage clients should disconnect, and storage services should finish writes before the underlying hosts power down. Network equipment required for coordination must remain powered long enough for this sequence. The final UPS power-removal action, if used, belongs to one designated authority and should occur only after protected systems are down. This laboratory models decision logic only. It does not call an operating-system shutdown interface, alter NUT configuration, contact a real UPS, or remove electrical power.

## Architecture

### production_flow
UPS hardware reports electrical state and battery telemetry to a hardware-specific driver.
A NUT server normalizes and publishes UPS variables.
A monitoring client evaluates status, timers, and policy conditions.
A shutdown coordinator orders workload and host shutdown actions.
One designated authority may perform the final UPS output-removal operation after protected systems are down.

### lab_flow
samples.jsonl supplies deterministic simulated UPS observations.
ups_guard.py parses status tokens, checks data age, and applies confirmation logic.
state.json stores the low-condition counter and shutdown-request latch.
events.jsonl records each decision for audit and troubleshooting.
actual-events.jsonl captures standard output for independent verification.

### trust_boundaries
UPS telemetry crosses from a device or monitoring service into the policy engine.
The policy engine must validate freshness and expected data types before making decisions.
Shutdown privileges must be separated from ordinary read-only monitoring access.
Only one explicitly designated component should hold final power-removal authority.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Extend the simulation with a sample containing OB but no LB and no runtime value. Document why the policy waits rather than assuming a critical battery condition.
Add an ALREADY_LATCHED test by supplying a fourth consecutive critical sample before the OL recovery sample.
Draw the shutdown dependency order for your homelab, including applications, databases, virtual machines, storage, hypervisors, monitoring, network equipment, and UPS authority.
Measure the graceful shutdown duration of each workload during a planned maintenance exercise, then explain how those observations would inform a site-specific threshold. Do not claim a universal threshold.
Write an incident checklist covering utility restoration, UPS health, battery recharge state, storage consistency, and staged service startup.
Identify which account in a proposed production architecture would have read-only monitoring access and which narrowly scoped component would have shutdown authority.

## Feynman teach-back

### prompt
Explain the design to a family member using the idea of a phone battery and an unreliable battery indicator.

### model_explanation
A UPS is like a temporary battery for computers. The monitoring system should not turn everything off because one reading says the wall power flickered. It checks repeatedly to confirm that the battery is truly becoming critical. It also rejects old readings, because an old message does not describe what is happening now. Once it asks the computers to shut down, it remembers that request so it does not ask repeatedly. If wall power is confirmed to have returned, it clears that memory and waits for the next event.

## Retrieval check

1. Why is an OB status by itself usually insufficient to trigger immediate shutdown?
2. What does the LB status token commonly indicate in NUT?
3. Why should a policy validate telemetry age before evaluating battery conditions?
4. What problem does a shutdown-request latch solve?
5. Why should runtime_seconds be treated as an estimate rather than an exact countdown?
6. What action does the lab take after three consecutive critical samples?
7. What happens to the latch after a confirmed OL sample in the lab policy?
8. Why should there be only one final UPS power-removal authority?
9. Which systems should generally stop first: dependent applications or the storage and network services they require?
10. Why does this lab use simulation instead of disconnecting real utility power?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

In this class, we build and test a safe UPS shutdown decision policy without touching real power controls. A UPS provides limited time, not unlimited availability, so the goal is to use that time deliberately. We begin with the architecture: a hardware driver reads the UPS, a monitoring service publishes normalized information, a policy engine evaluates the information, and a shutdown coordinator controls the order of operations. Common NUT status tokens include OL for online, OB for on battery, and LB for low battery.

The key lesson is that one observation should not automatically become a destructive action. A brief transition to battery may clear by itself. A runtime value is also an estimate rather than a guaranteed countdown. Our demonstration policy therefore requires three consecutive critical samples. It also checks that each observation is fresh. If the data is stale, the policy emits DATA_STALE and refuses to create a new shutdown request.

The lab stores a small amount of state. A counter records consecutive critical observations, while a latch records whether a shutdown request has already been issued. On the third critical observation, the script emits SHUTDOWN_REQUESTED. This is only a label in a JSON event; no operating-system power command exists in the script. Additional critical samples would be marked as already latched instead of creating duplicate requests. A confirmed online observation clears the incident state.

In production, the shutdown sequence must follow dependencies. Applications stop accepting work, databases and storage flush data, guests shut down, and infrastructure hosts stop only after their dependents are safe. Network equipment needed for coordination must remain available during this process. If UPS output removal is used, only one designated authority should perform it after protected systems are down.

Finally, treat shutdown control as privileged access. Read-only monitoring and shutdown authority should use separate identities. Protect credentials, restrict network exposure, audit policy changes, and alert on stale data. Validate behavior with simulations and planned maintenance exercises before enabling any live power action.

## References

- Network UPS Tools project documentation: https://networkupstools.org/docs/
- Network UPS Tools upsc manual: https://networkupstools.org/docs/man/upsc.html
- Network UPS Tools upsmon manual: https://networkupstools.org/docs/man/upsmon.html
- Network UPS Tools upssched manual: https://networkupstools.org/docs/man/upssched.html
- Network UPS Tools protocol and status information: https://networkupstools.org/docs/developer-guide.chunked/apas01.html
- The Linux man-pages project shutdown documentation: https://man7.org/linux/man-pages/man8/shutdown.8.html

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

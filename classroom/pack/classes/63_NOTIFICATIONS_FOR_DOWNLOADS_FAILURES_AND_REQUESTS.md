# Class 63: Notifications for Downloads, Failures, and Requests

**Learning objective:** Explain the difference between an application event and a delivered notification.; Normalize download, failure, and request events into a consistent schema.; Route events according to operational severity and intended audience.; Prevent duplicate notifications by tracking stable event identifiers.; Redact secrets before notification content is written or transmitted.; Handle malformed events through a dead-letter record rather than silently discarding them.; Verify notification behavior through deterministic local artifacts.; Describe production controls for authentication, retry limits, timeouts, and alert fatigue.
**Bloom level:** Understand / Apply
**Track:** Media Automation and Operations · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Design and test a reliable notification pipeline for download completions, download failures, and user request events. The lesson emphasizes event normalization, severity-based routing, duplicate suppression, secret redaction, durable local queuing, dead-letter handling, and verification without contacting a real notification provider.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux systems providing Python 3 and a POSIX-compatible shell

### runtime
Python 3.8 or newer is recommended.

### external_services
No external notification provider is required or contacted.

### filesystem_scope
/opt/lab-classroom/class63/

### notes
The lab uses only Python standard-library modules.
Atomic replacement assumes the temporary state file and final state file remain on the same filesystem.
Production integrations require provider-specific authentication, timeout, retry, and rate-limit handling.
The sample timestamps and event values are deterministic training data, not performance measurements.

## Learning objective

- Explain the difference between an application event and a delivered notification.
- Normalize download, failure, and request events into a consistent schema.
- Route events according to operational severity and intended audience.
- Prevent duplicate notifications by tracking stable event identifiers.
- Redact secrets before notification content is written or transmitted.
- Handle malformed events through a dead-letter record rather than silently discarding them.
- Verify notification behavior through deterministic local artifacts.
- Describe production controls for authentication, retry limits, timeouts, and alert fatigue.

## Why this matters

Design and test a reliable notification pipeline for download completions, download failures, and user request events. The lesson emphasizes event normalization, severity-based routing, duplicate suppression, secret redaction, durable local queuing, dead-letter handling, and verification without contacting a real notification provider.

## Prerequisites

- Basic familiarity with JSON, shell commands, and Python 3.
- Understanding of download managers, media automation services, and request-management applications.
- Write access to /opt/lab-classroom/class63/.
- Ability to distinguish informational events from actionable failures.
- Completion of introductory lessons on service logs and application integration concepts is recommended.

## Required reading

- Python documentation: json — JSON encoder and decoder at https://docs.python.org/3/library/json.html
- Python documentation: pathlib — object-oriented filesystem paths at https://docs.python.org/3/library/pathlib.html
- Python documentation: hashlib — secure hashes and message digests at https://docs.python.org/3/library/hashlib.html
- OWASP Secrets Management Cheat Sheet at https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Prometheus documentation: Alerting rules at https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| event | A structured statement that something happened, such as a download completing, a download failing, or a request being approved. |
| notification | A human-facing message derived from an event and prepared for delivery to a destination such as an activity feed, request channel, or operations alert channel. |
| event identifier | A stable identifier assigned by the event producer and used to recognize repeated delivery of the same event. |
| idempotency | The property that processing the same event more than once has the same effective result as processing it once. |
| deduplication | Suppressing repeated notifications for an event that has already been accepted. |
| routing | Selecting a destination and severity based on event type, ownership, and required response. |
| redaction | Replacing sensitive values with a safe marker before data is logged, queued, or delivered. |
| outbox | A durable local queue of notifications that have been accepted for later delivery. |
| dead-letter record | A minimal record describing an event that could not be processed, retained for diagnosis without repeatedly blocking valid work. |
| alert fatigue | Reduced operator attention caused by excessive, repetitive, low-value, or poorly routed notifications. |

## Instruction

A notification pipeline should be treated as an operational system, not as a decorative feature. Download managers, media automation tools, and request applications often emit events independently. Those events may use different field names, retry policies, and authentication methods. A reliable design therefore separates event ingestion, normalization, policy, queuing, and delivery. Ingestion accepts an event but does not assume that the event is trustworthy or complete. Normalization validates a stable event identifier, an allowed event type, a timestamp, and an object-shaped payload. Policy then maps the event to a severity and audience. A successful download is usually informational and belongs in an activity destination. A failed download is actionable and belongs in an operations alert destination. Request creation may be informational, while approval or denial should normally be routed to the audience responsible for request status.

Delivery must not be confused with event acceptance. A remote notification provider can be unavailable even though the source event is valid. A durable outbox lets the system acknowledge and retain valid work before a separate delivery worker contacts the provider. Production workers should use bounded retries, increasing delays, random jitter, explicit connection and response timeouts, and a terminal failure state. Retrying forever creates hidden queues and repeated messages. Providers may also redeliver source events, so each event needs a stable identifier. Deduplication state must be written durably enough to survive process restarts. The lab demonstrates this by recording accepted identifiers in a local state file and using an atomic replacement operation when updating that state.

Notification content must be considered untrusted and potentially sensitive. Payloads can contain provider tokens, passwords, internal paths, usernames, request notes, or media names. Only fields needed by the recipient should be included. Secrets must be redacted before writing the outbox, not merely hidden in a user interface after storage. Malformed input also requires care: storing the complete rejected record can preserve a secret indefinitely. The lab records a digest, line number, and error instead of copying malformed input. Finally, a useful notification answers three questions: what happened, how important is it, and what action is expected? Severity, destination, and concise context should support those questions. Every notification rule should be tested for valid input, duplicate delivery, malformed input, and secret leakage before it is connected to a real provider.

## Architecture

### components
### name
Event producer

### role
Represents a download manager, media automation application, or request-management application that emits structured events.
### name
Normalizer and policy engine

### role
Validates required fields, redacts sensitive values, assigns severity, selects a destination, and creates a consistent notification record.
### name
Deduplication state

### role
Stores accepted event identifiers and rejected-record digests so repeated input does not create repeated output.
### name
Outbox

### role
Stores accepted notification records durably before any real provider delivery is attempted.
### name
Dead-letter file

### role
Stores minimal diagnostic information for malformed records without retaining their complete content.
### name
Delivery adapter

### role
In production, reads the outbox and communicates with an approved messaging or incident-management provider. This lab intentionally does not implement external delivery.

### event_flow
A producer writes or sends an event with a stable identifier.
The normalizer validates the event type, identifier, timestamp, and payload.
Sensitive keys are recursively replaced with a redaction marker.
Policy assigns severity and destination according to event type.
The notification is appended to the durable outbox.
The event identifier is saved in deduplication state.
A production delivery adapter would later deliver the queued notification and record delivery status.

### routing_policy
### download.completed
Severity info; destination activity.

### download.failed
Severity critical; destination alerts.

### request.created
Severity info; destination activity.

### request.approved
Severity notice; destination requests.

### request.denied
Severity notice; destination requests.

### trust_boundaries
Incoming payloads are untrusted even when they originate from an internal application.
The outbox contains recipient-visible data and must not contain reusable credentials.
A real delivery adapter crosses from the homelab into a third-party or separately administered service.
Deduplication state influences whether alerts are emitted and therefore requires integrity protection.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Add a recognized request.denied sample event and predict its destination and severity before running the processor.
Design a notification matrix listing event type, severity, audience, destination, quiet-hours behavior, and required human action.
Extend the policy design on paper to distinguish a transient provider timeout from repeated download exhaustion.
Propose a bounded retry schedule for a production delivery adapter and explain when an event should enter a terminal failure state.
Document which payload fields are necessary for each destination and exclude all fields that do not help the recipient act.
Create a test case for a secret nested inside a list of objects and verify that recursive redaction still protects it.
Describe how you would rotate a provider credential and investigate exposure if a credential were found in an old notification.

## Feynman teach-back

### prompt
Explain the pipeline to a household member who understands messaging applications but does not administer servers.

### model_explanation
An application first writes a small note saying what happened. The notification processor checks that the note has an identity and a recognized type. It removes secret values, decides who should care, and puts a safe message into an outgoing tray. It also records the note's identity so receiving the same note twice does not create two messages. If the note is malformed, the processor records only enough information to diagnose the problem. A separate delivery worker would carry messages from the outgoing tray to the messaging service. Keeping those jobs separate means a temporary messaging outage does not erase the original alert.

### self_check_questions
Why is a completed download usually routed differently from a failed download?
Why does the event need a stable identifier?
Why must redaction happen before the outbox is written?
Why is a durable outbox safer than sending directly during event processing?
Why should malformed input be represented by a digest instead of being copied without review?

## Retrieval check

1. 1. What is the primary reason to separate event acceptance from provider delivery?
2. 2. Why should download failure events normally have a different severity and destination from successful download events?
3. 3. What property allows the processor to receive the same event repeatedly without creating repeated notifications?
4. 4. Why is a stable producer-assigned event identifier preferable to hashing only the notification text?
5. 5. At what point should secret redaction occur?
6. 6. What information does this lab store for malformed input, and what does it intentionally avoid storing?
7. 7. Why should production retry behavior be bounded?
8. 8. What does the outbox delivery_status value queued mean in this lab?
9. 9. How does atomic replacement reduce the risk of corrupting deduplication state?
10. 10. What should happen if a production destination identifier is supplied directly by untrusted event content?

## Guided lab

### scope
All created or modified files remain beneath /opt/lab-classroom/class63/. The lab performs no external network requests and sends no real notifications.

### artifacts
/opt/lab-classroom/class63/notifier.py
/opt/lab-classroom/class63/events.jsonl
/opt/lab-classroom/class63/outbox.jsonl
/opt/lab-classroom/class63/deadletter.jsonl
/opt/lab-classroom/class63/state.json

### steps
### step
1

### instruction
Create the dedicated lab directory.

### command
mkdir -p /opt/lab-classroom/class63/
### step
2

### instruction
Create the local notification processor. It validates events, recursively redacts sensitive keys, routes recognized types, suppresses duplicates, and records malformed input by digest rather than raw content.

### command
cat > /opt/lab-classroom/class63/notifier.py <<'PY'
import hashlib
import json
from pathlib import Path

BASE = Path('/opt/lab-classroom/class63')
EVENTS = BASE / 'events.jsonl'
OUTBOX = BASE / 'outbox.jsonl'
DEAD = BASE / 'deadletter.jsonl'
STATE = BASE / 'state.json'

POLICY = {
    'download.completed': ('info', 'activity'),
    'download.failed': ('critical', 'alerts'),
    'request.created': ('info', 'activity'),
    'request.approved': ('notice', 'requests'),
    'request.denied': ('notice', 'requests'),
}
SENSITIVE_KEYS = {'token', 'password', 'api_key', 'authorization', 'secret'}

def redact(value):
    if isinstance(value, dict):
        return {
            key: ('[REDACTED]' if key.lower() in SENSITIVE_KEYS else redact(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value

def load_seen():
    if not STATE.exists():
        return set()
    data = json.loads(STATE.read_text(encoding='utf-8'))
    return set(data.get('seen', []))

def save_seen(seen):
    temporary = BASE / 'state.tmp'
    temporary.write_text(
        json.dumps({'seen': sorted(seen)}, indent=2) + '\n',
        encoding='utf-8'
    )
    temporary.replace(STATE)

def append_json(path, record):
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(record, sort_keys=True) + '\n')

def validate(event):
    if not isinstance(event, dict):
        raise ValueError('event must be a JSON object')
    for field in ('event_id', 'type', 'timestamp', 'payload'):
        if field not in event:
            raise ValueError('missing required field: ' + field)
    if not isinstance(event['event_id'], str) or not event['event_id'].strip():
        raise ValueError('event_id must be a non-empty string')
    if event['type'] not in POLICY:
        raise ValueError('unsupported event type')
    if not isinstance(event['timestamp'], str) or not event['timestamp'].strip():
        raise ValueError('timestamp must be a non-empty string')
    if not isinstance(event['payload'], dict):
        raise ValueError('payload must be a JSON object')

def main():
    BASE.mkdir(parents=True, exist_ok=True)
    seen = load_seen()
    queued = 0
    duplicates = 0
    rejected = 0

    with EVENTS.open('r', encoding='utf-8') as source:
        for line_number, raw in enumerate(source, start=1):
            if not raw.strip():
                continue
            digest = hashlib.sha256(raw.encode('utf-8')).hexdigest()
            dead_key = 'dead:' + digest
            try:
                event = json.loads(raw)
                validate(event)
                event_key = 'event:' + event['event_id']
                if event_key in seen:
                    duplicates += 1
                    continue
                clean_payload = redact(event['payload'])
                severity, destination = POLICY[event['type']]
                notification_id = hashlib.sha256(
                    (event['event_id'] + ':' + event['type']).encode('utf-8')
                ).hexdigest()
                notification = {
                    'notification_id': notification_id,
                    'event_id': event['event_id'],
                    'event_type': event['type'],
                    'event_timestamp': event['timestamp'],
                    'severity': severity,
                    'destination': destination,
                    'subject': event['type'].replace('.', ' ').title(),
                    'payload': clean_payload,
                    'delivery_status': 'queued'
                }
                append_json(OUTBOX, notification)
                seen.add(event_key)
                save_seen(seen)
                queued += 1
            except Exception as exc:
                if dead_key not in seen:
                    append_json(DEAD, {
                        'line_number': line_number,
                        'raw_sha256': digest,
                        'error': str(exc)
                    })
                    seen.add(dead_key)
                    save_seen(seen)
                    rejected += 1
                else:
                    duplicates += 1

    print(json.dumps({
        'queued': queued,
        'duplicates_or_known_rejections': duplicates,
        'newly_rejected': rejected
    }, sort_keys=True))

if __name__ == '__main__':
    main()
PY
### step
3

### instruction
Create four valid sample events and one malformed event. The failed-download event deliberately contains a sample secret value so redaction can be verified.

### command
cat > /opt/lab-classroom/class63/events.jsonl <<'JSONL'
{"event_id":"evt-001","type":"download.completed","timestamp":"2025-03-08T10:00:00Z","payload":{"item":"Example Documentary","quality":"1080p"}}
{"event_id":"evt-002","type":"download.failed","timestamp":"2025-03-08T10:05:00Z","payload":{"item":"Example Series S01E01","reason":"provider timeout","api_key":"LAB-SECRET-VALUE"}}
{"event_id":"evt-003","type":"request.created","timestamp":"2025-03-08T10:10:00Z","payload":{"item":"Example Film","request_id":42}}
{"event_id":"evt-004","type":"request.approved","timestamp":"2025-03-08T10:15:00Z","payload":{"item":"Example Film","request_id":42}}
{"type":"download.failed","timestamp":"2025-03-08T10:20:00Z","payload":{"reason":"missing event identifier"}}
JSONL
### step
4

### instruction
Run the processor for the first time. Four records should be queued and one malformed record should be rejected.

### command
python3 /opt/lab-classroom/class63/notifier.py
### step
5

### instruction
Run the processor again to test idempotency. No additional outbox or dead-letter records should be created.

### command
python3 /opt/lab-classroom/class63/notifier.py
### step
6

### instruction
Inspect the generated artifacts without contacting an external service.

### command
python3 - <<'PY'
import json
from pathlib import Path
base = Path('/opt/lab-classroom/class63')
for name in ('outbox.jsonl', 'deadletter.jsonl', 'state.json'):
    path = base / name
    print('\n==', name, '==')
    print(path.read_text(encoding='utf-8'))
PY
### step
7

### instruction
Perform deterministic assertions for record counts, routing, status, deduplication, and redaction.

### command
python3 - <<'PY'
import json
from pathlib import Path
base = Path('/opt/lab-classroom/class63')
outbox = [json.loads(line) for line in (base / 'outbox.jsonl').read_text(encoding='utf-8').splitlines() if line]
dead = [json.loads(line) for line in (base / 'deadletter.jsonl').read_text(encoding='utf-8').splitlines() if line]
state = json.loads((base / 'state.json').read_text(encoding='utf-8'))
assert len(outbox) == 4, outbox
assert len(dead) == 1, dead
assert len(state['seen']) == 5, state
assert all(item['delivery_status'] == 'queued' for item in outbox)
failed = next(item for item in outbox if item['event_type'] == 'download.failed')
assert failed['severity'] == 'critical'
assert failed['destination'] == 'alerts'
assert failed['payload']['api_key'] == '[REDACTED]'
serialized = json.dumps(outbox)
assert 'LAB-SECRET-VALUE' not in serialized
assert 'LAB-SECRET-VALUE' not in json.dumps(dead)
assert set(item['event_id'] for item in outbox) == {'evt-001', 'evt-002', 'evt-003', 'evt-004'}
print('PASS: routing, deduplication, dead-letter handling, and redaction verified')
PY

### production_extension
Replace the demonstration file producer with authenticated events from approved applications.
Keep normalization and policy separate from provider-specific delivery code.
Add an outbox delivery worker with explicit timeouts, bounded retries, increasing delays, and random jitter.
Record delivery attempts and terminal failures without writing provider credentials into logs.
Use provider-side identifiers or idempotency keys when supported.
Test provider failure behavior in a non-production destination before enabling household or operations channels.

## Expected results

- The first processor run reports four queued notifications and one newly rejected event.
- The second processor run reports no newly queued or newly rejected records because all five input lines are already represented in state.
- The outbox contains exactly four JSON records with unique event identifiers.
- The failed-download notification has critical severity and the alerts destination.
- The completed-download and newly created request notifications use informational routing.
- The approved request notification uses the requests destination.
- The sample API key is replaced with [REDACTED] in the outbox.
- The dead-letter file contains one digest-based diagnostic record and does not contain the malformed event's raw content.
- Every outbox record has delivery_status set to queued because this lab does not contact a real provider.

## Verification checkpoints

- [ ] Run the deterministic assertion command in lab step 7 and confirm that it prints PASS.
- [ ] Run `python3 /opt/lab-classroom/class63/notifier.py` again and confirm that queued and newly_rejected both remain zero.
- [ ] Confirm that /opt/lab-classroom/class63/outbox.jsonl contains exactly four non-empty lines.
- [ ] Confirm that /opt/lab-classroom/class63/deadletter.jsonl contains exactly one non-empty line.
- [ ] Inspect state.json and confirm that it contains four event keys and one dead-letter digest key.
- [ ] Confirm that the failed-download record is routed to alerts with critical severity.
- [ ] Confirm that the literal sample value LAB-SECRET-VALUE does not appear in outbox.jsonl, deadletter.jsonl, or state.json.
- [ ] Confirm that all generated or modified artifacts are located beneath /opt/lab-classroom/class63/.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The processor reports that events.jsonl does not exist. | The sample event creation step was skipped or the file was created under a different path. | Repeat lab step 3 and verify that the file is /opt/lab-classroom/class63/events.jsonl. |
| The first run reports zero queued events. | State from a previous run already contains the sample event identifiers. | Inspect state.json to confirm prior processing. For a clean repetition, use a new dedicated subdirectory under /opt/lab-classroom/class63/ and update the BASE value consistently, or perform the documented rollback before recreating the lab. |
| The assertion reports more than four outbox records. | The outbox was retained while state.json was reset or replaced, allowing the same events to be queued again. | Keep the outbox and deduplication state as one logical unit. Roll back all lab artifacts together, recreate them, and rerun the exercise. |
| The secret-redaction assertion fails. | The sensitive key list or recursive redaction function was changed, or the notification was built from the original payload. | Confirm that api_key is present in SENSITIVE_KEYS and that notification payloads are created from clean_payload rather than event['payload']. |
| A request event is placed in the wrong destination. | The POLICY mapping does not match the intended event type. | Review the exact event type and update the policy deliberately. Do not use broad substring matching for security-sensitive or operational routing. |
| Malformed input is added to the dead-letter file every time the processor runs. | The dead-letter digest key is not being added to persistent state. | Confirm that dead_key is added to seen and save_seen is called after the dead-letter record is appended. |
| The state file contains invalid or partial JSON after an interruption. | Atomic temporary-file replacement was removed or the storage system does not provide expected replacement semantics. | Restore the temporary-file write followed by replacement, and keep the temporary file on the same filesystem as state.json. |
| A production provider receives repeated notifications even though local deduplication works. | The delivery worker retries after an ambiguous response without a provider-side idempotency key. | Supply a stable notification identifier to providers that support idempotency and reconcile uncertain delivery outcomes before sending again. |

## Security considerations

Treat every incoming event field as untrusted data, including events from internal applications.
Authenticate production event producers and verify message integrity when the source supports signatures.
Use least-privilege provider credentials that can post only to intended destinations.
Store credentials outside event payloads, notification bodies, outbox records, and diagnostic logs.
Redact sensitive values before durable storage or transmission rather than relying only on presentation-layer masking.
Do not retain complete malformed records by default; store a digest and minimal error context unless an approved forensic process requires more.
Validate destination identifiers against an allowlist so event content cannot redirect messages.
Apply explicit connection and response timeouts in production delivery adapters.
Use bounded retries and a terminal failure state to prevent infinite retry loops.
Restrict access to the outbox because media titles, request activity, usernames, and failure details may reveal household behavior.
Avoid placing private request notes in shared channels.
Rotate any real credential immediately if it appears in an outbox, log, screenshot, support bundle, or chat message.

## Rollback

### goal
Disable the lab while preserving its artifacts for inspection. All rollback changes remain beneath /opt/lab-classroom/class63/.

### steps
### step
1

### instruction
Create an archive directory inside the lab boundary.

### command
mkdir -p /opt/lab-classroom/class63/rollback-disabled/
### step
2

### instruction
Move the executable lab script and generated data into the archive directory.

### command
for f in notifier.py events.jsonl outbox.jsonl deadletter.jsonl state.json state.tmp; do if [ -e "/opt/lab-classroom/class63/$f" ]; then mv "/opt/lab-classroom/class63/$f" /opt/lab-classroom/class63/rollback-disabled/; fi; done
### step
3

### instruction
Verify that no active processor or event file remains at the top level of the lab directory.

### command
python3 - <<'PY'
from pathlib import Path
base = Path('/opt/lab-classroom/class63')
active = [name for name in ('notifier.py', 'events.jsonl', 'outbox.jsonl', 'deadletter.jsonl', 'state.json', 'state.tmp') if (base / name).exists()]
assert not active, active
print('PASS: lab disabled; artifacts retained in rollback-disabled')
PY

### restore
To restore the lab, move the archived files from /opt/lab-classroom/class63/rollback-disabled/ back to /opt/lab-classroom/class63/ only after confirming that no same-named active files exist.

## Video narration notes

In this class, we build the control plane for useful homelab notifications. The important design decision is to treat source events and delivered messages as different objects. A download manager may report that an item completed or failed, while a request application may report that a user created, approved, or denied a request. Those events enter a normalizer that checks required fields and permits only known event types. The policy engine then assigns severity and destination. Successful activity goes to a low-noise activity destination, failures go to an operations alert destination, and request decisions go to a request-focused destination.

Before anything is queued, the processor recursively redacts keys commonly associated with credentials. This sequencing matters: masking a value only after it reaches a user interface does not remove it from files, logs, backups, or provider history. The processor then writes a normalized record to a local outbox and records the event identifier in persistent state. When the same source data is processed again, no duplicate notification is created. Malformed input follows a separate path. Instead of copying potentially sensitive raw data, the processor records a digest, line number, and validation error.

The lab deliberately stops at the queued state. It does not send data to a real provider. In production, a separate delivery adapter would read the outbox, authenticate to an approved destination, enforce timeouts, and retry temporary failures with bounded delays and jitter. Terminal failures would remain visible for operator action. As you complete the verification, focus on four properties: each valid event is routed correctly, repeated processing is idempotent, malformed input is diagnosable, and the sample secret never appears in durable notification output. Those properties are more important than the choice of any particular messaging provider.

## References

- Python json library documentation: https://docs.python.org/3/library/json.html
- Python pathlib library documentation: https://docs.python.org/3/library/pathlib.html
- Python hashlib library documentation: https://docs.python.org/3/library/hashlib.html
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- Prometheus alerting rules documentation: https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
- RFC 8259, The JavaScript Object Notation Data Interchange Format: https://www.rfc-editor.org/rfc/rfc8259
- CWE-532, Insertion of Sensitive Information into Log File: https://cwe.mitre.org/data/definitions/532.html

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

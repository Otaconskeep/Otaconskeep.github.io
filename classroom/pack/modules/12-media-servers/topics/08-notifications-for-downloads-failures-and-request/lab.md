# Lab: Notifications for Downloads, Failures, and Requests

**Module:** Requests & Media Servers
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain the difference between an application event and a delivered notification.

## Before you start

- Basic familiarity with JSON, shell commands, and Python 3.
- Understanding of download managers, media automation services, and request-management applications.
- Write access to /opt/lab-classroom/class63/.
- Ability to distinguish informational events from actionable failures.
- Completion of introductory lessons on service logs and application integration concepts is recommended.

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

## Verification

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

## Security

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

# Reading: Notifications for Downloads, Failures, and Requests

**Module:** Requests & Media Servers
**Activity type:** Reading (Learn)
**Objective:** Explain the difference between an application event and a delivered notification.

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

## Required reading

- Python documentation: json — JSON encoder and decoder at https://docs.python.org/3/library/json.html
- Python documentation: pathlib — object-oriented filesystem paths at https://docs.python.org/3/library/pathlib.html
- Python documentation: hashlib — secure hashes and message digests at https://docs.python.org/3/library/hashlib.html
- OWASP Secrets Management Cheat Sheet at https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Prometheus documentation: Alerting rules at https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/

## References

- Python json library documentation: https://docs.python.org/3/library/json.html
- Python pathlib library documentation: https://docs.python.org/3/library/pathlib.html
- Python hashlib library documentation: https://docs.python.org/3/library/hashlib.html
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- Prometheus alerting rules documentation: https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
- RFC 8259, The JavaScript Object Notation Data Interchange Format: https://www.rfc-editor.org/rfc/rfc8259
- CWE-532, Insertion of Sensitive Information into Log File: https://cwe.mitre.org/data/definitions/532.html

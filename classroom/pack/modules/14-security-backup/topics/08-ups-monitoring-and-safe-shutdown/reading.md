# Reading: UPS Monitoring and Safe Shutdown

**Module:** Segmentation, Backup & Power
**Activity type:** Reading (Learn)
**Objective:** Explain the roles of a UPS, UPS driver, monitoring daemon, client, and shutdown coordinator.

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

## Required reading

- Network UPS Tools documentation: https://networkupstools.org/docs/
- NUT upsc client documentation: https://networkupstools.org/docs/man/upsc.html
- NUT upsmon documentation: https://networkupstools.org/docs/man/upsmon.html
- NUT upssched documentation: https://networkupstools.org/docs/man/upssched.html
- NUT status data documentation: https://networkupstools.org/docs/developer-guide.chunked/apas01.html

## References

- Network UPS Tools project documentation: https://networkupstools.org/docs/
- Network UPS Tools upsc manual: https://networkupstools.org/docs/man/upsc.html
- Network UPS Tools upsmon manual: https://networkupstools.org/docs/man/upsmon.html
- Network UPS Tools upssched manual: https://networkupstools.org/docs/man/upssched.html
- Network UPS Tools protocol and status information: https://networkupstools.org/docs/developer-guide.chunked/apas01.html
- The Linux man-pages project shutdown documentation: https://man7.org/linux/man-pages/man8/shutdown.8.html

# Homework: Notifications for Downloads, Failures, and Requests

**Module:** Requests & Media Servers
**Activity type:** Homework / independent application
**Objective:** Explain the difference between an application event and a delivered notification.

## Requirements

Add a recognized request.denied sample event and predict its destination and severity before running the processor.
Design a notification matrix listing event type, severity, audience, destination, quiet-hours behavior, and required human action.
Extend the policy design on paper to distinguish a transient provider timeout from repeated download exhaustion.
Propose a bounded retry schedule for a production delivery adapter and explain when an event should enter a terminal failure state.
Document which payload fields are necessary for each destination and exclude all fields that do not help the recipient act.
Create a test case for a secret nested inside a list of objects and verify that recursive redaction still protects it.
Describe how you would rotate a provider credential and investigate exposure if a credential were found in an old notification.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

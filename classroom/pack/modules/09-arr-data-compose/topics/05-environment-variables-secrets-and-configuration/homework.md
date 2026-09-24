# Homework — Environment Variables, Secrets, and Configuration

**Module:** ARR Data Model & Compose
**Activity type:** Homework / independent application
**Objective:** Distinguish ordinary configuration values from sensitive values that require stronger handling.

## Requirements

Add an allow-listed SERVICE_REGION setting with a built-in default, JSON support, and an environment override. Keep all changes inside /opt/lab-classroom/class38/.
Modify the application so a missing optional JSON file still permits defaults, while malformed JSON remains a startup error.
Write a short configuration contract listing each setting, its type, allowed values, default, sensitivity classification, and precedence.
Design a production rotation plan that covers issuance, overlap, activation, verification, revocation, audit evidence, and emergency rollback.
Explain why logging a digest of a low-entropy sensitive value can still enable guessing and why the lab reports only a Boolean loaded status.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

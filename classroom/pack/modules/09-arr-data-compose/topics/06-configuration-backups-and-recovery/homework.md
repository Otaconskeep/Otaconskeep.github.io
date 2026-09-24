# Homework: Configuration Backups and Recovery

**Module:** ARR Data Model & Compose
**Activity type:** Homework / independent application
**Objective:** Explain why a configuration archive alone is not a complete recovery strategy.

## Requirements

### assignment
Create a second attempt under /opt/lab-classroom/class39/attempt2/. Add a third configuration file in a format Python can parse, include it in the package manifest, and extend the validator with at least two semantic rules. Create two backup generations with clearly different metadata, introduce drift, recover the older generation into a candidate directory, and document why selecting that generation is justified.

### deliverables
A short recovery runbook stored beneath the attempt2 directory.
Two versioned backup archives with separate archive checksums.
A manifest for each generation.
A validator that checks all three configuration files.
A text record of the integrity, syntax, semantic, promotion, and rollback checks performed.
A retention proposal specifying how many generations to keep and why.

### constraints
All filesystem changes must remain under /opt/lab-classroom/class39/.
Do not use real credentials or production configuration.
Do not activate a candidate until every documented validation gate passes.
Preserve the pre-recovery state until the exercise is fully verified.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

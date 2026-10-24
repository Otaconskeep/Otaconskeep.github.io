# Homework: Reusable Docker Compose Stack Patterns

**Module:** Compose Operations & IaC
**Activity type:** Homework / independent application
**Objective:** Create a reusable Compose stack with extension fields and YAML anchors.

## Requirements

Add a profile-gated service named diagnostics using a small fixed-tag image, but continue to use config rendering only. Verify that it appears in the full model and only appears in --services when its profile is enabled.
Create compose.dev.yaml that changes LOG_LEVEL to trace without duplicating the complete web service definition. Render and assert the result.
Add a second network in an overlay and observe whether it is appended to the web service network list.
Write a Python assertion that every published port in every rendered model has host_ip set to 127.0.0.1.
Write a short design note explaining when !override communicates intent better than relying on normal uniqueness-based sequence merging.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

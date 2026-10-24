# Homework: Image Version Pinning and Controlled Updates

**Module:** Compose Operations & IaC
**Activity type:** Homework / independent application
**Objective:** Explain why a mutable tag is unsuitable as the final deployment identity.

## Requirements

Add a canary channel that points to a new index while keeping stable unchanged. Require a distinct out-of-band digest and prove that a stable approval cannot authorize canary.
Add a negative test requesting linux/arm64 while supplying the linux/amd64 expected digest. Assert that deployment.json and audit.log remain byte-for-byte unchanged.
Extend update.py with an expected repository argument supplied out of band, then reject a catalog that substitutes a different repository while retaining the same manifest digest.
Design a production trust model that stores approvals outside the registry administrator's control and includes signature or attestation verification. Identify which principals may publish images, approve releases, and deploy them.
Write a test that introduces two linux/amd64 descriptors in index-v2 and confirms that the updater fails closed rather than selecting the first descriptor.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

# Quiz: Image Version Pinning and Controlled Updates

**Module:** Compose Operations & IaC
**Activity type:** Quiz / retrieval practice
**Target:** ≥80%
**Objective:** Explain why a mutable tag is unsuitable as the final deployment identity.

## Questions

1. Why is academy/demo:stable insufficient as the final identity of a controlled deployment?
2. When stable resolves to a multi-platform image index, which digest should a linux/amd64 deployment pin in this lesson?
3. Why does recomputing a catalog-provided digest not prove publisher trust or release approval?
4. What three out-of-band values does update.py require to constrain selection?
5. Why must the intentional simultaneous edit of the blob, descriptor digest, and policy still be rejected?
6. What must remain unchanged after a dry-run or rejected update?
7. Which audit fields prove linkage between the prior and promoted deployment identities?
8. Why does rollback copy deployment.backup.json instead of replacing the deployment by moving that backup?
9. When is the rollback audit event appended?
10. What important security property is not provided by the self-consistent hash check in this lab?

## After scoring

- Missed items → return to Reading → redo Feynman Retry → reattempt.

<!-- answer key is maintained in instructor materials / automation batch report; not printed for students -->

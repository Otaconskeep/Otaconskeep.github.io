# Quiz — Health Checks, Dependencies, and Restart Policies

**Module:** ARR Data Model & Compose
**Activity type:** Quiz / retrieval practice
**Target:** ≥80%
**Objective:** Explain why a running process is not necessarily a healthy or ready service

## Questions

1. What is the operational difference between liveness and readiness?
2. Why is dependency start order insufficient to guarantee that an application can use the dependency?
3. When is an on-failure restart policy generally more appropriate than an always restart policy?
4. What action should normally follow a readiness failure when the process remains live?
5. Why should health checks use explicit, short timeouts?
6. What is a restart loop, and why can it harm other services?
7. In the lab, what evidence proves that the application was restarted rather than merely recovering inside the same process?
8. Why is the lab's /crash endpoint unacceptable as an unauthenticated production endpoint?

## After scoring

- Missed items → return to Reading → redo Feynman Retry → reattempt.

<!-- answer key is maintained in instructor materials / automation batch report; not printed for students -->

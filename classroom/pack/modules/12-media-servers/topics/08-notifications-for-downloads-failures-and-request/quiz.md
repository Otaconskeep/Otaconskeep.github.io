# Quiz: Notifications for Downloads, Failures, and Requests

**Module:** Requests & Media Servers
**Activity type:** Quiz / retrieval practice
**Target:** ≥80%
**Objective:** Explain the difference between an application event and a delivered notification.

## Questions

1. 1. What is the primary reason to separate event acceptance from provider delivery?
2. 2. Why should download failure events normally have a different severity and destination from successful download events?
3. 3. What property allows the processor to receive the same event repeatedly without creating repeated notifications?
4. 4. Why is a stable producer-assigned event identifier preferable to hashing only the notification text?
5. 5. At what point should secret redaction occur?
6. 6. What information does this lab store for malformed input, and what does it intentionally avoid storing?
7. 7. Why should production retry behavior be bounded?
8. 8. What does the outbox delivery_status value queued mean in this lab?
9. 9. How does atomic replacement reduce the risk of corrupting deduplication state?
10. 10. What should happen if a production destination identifier is supplied directly by untrusted event content?

## After scoring

- Missed items → return to Reading → redo Feynman Retry → reattempt.

<!-- answer key is maintained in instructor materials / automation batch report; not printed for students -->

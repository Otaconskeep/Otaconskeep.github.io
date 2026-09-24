# Quiz: Environment Variables, Secrets, and Configuration

**Module:** ARR Data Model & Compose
**Activity type:** Quiz / retrieval practice
**Target:** ≥80%
**Objective:** Distinguish ordinary configuration values from sensitive values that require stronger handling.

## Questions

1. What is the configuration precedence used for app_mode and log_level in this lesson?
2. Why does the lesson avoid placing the generated credential directly in an environment variable?
3. What does the application verify before reading the sensitive file?
4. Why is rewriting an active sensitive file in place less safe than atomic replacement?
5. What output proves that the application loaded the sensitive value without revealing it?
6. Why should an untrusted configuration file not be loaded as executable shell text?
7. What should the application do when a required sensitive file has group-readable permissions?

## After scoring

- Missed items → return to Reading → redo Feynman Retry → reattempt.

<!-- answer key is maintained in instructor materials / automation batch report; not printed for students -->

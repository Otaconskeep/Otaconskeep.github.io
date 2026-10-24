# Lesson 15.02: Reusable Docker Compose Stack Patterns

**Module:** Compose Operations & IaC
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Create a reusable Compose stack with extension fields and YAML anchors.
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-03-08

## Learning objective

Create a reusable Compose stack with extension fields and YAML anchors.

## Why this matters

Teach learners to structure reusable Docker Compose projects with extension fields, YAML anchors, environment interpolation, profiles, layered override files, deterministic replacement, and observable sequence-merge behavior. The lab remains static: learners render and inspect Compose models without starting containers.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain the stack to another learner without using the words template, magic, or automatic.

### model_explanation
compose.yaml defines the stable application. The x-service-defaults block is reusable YAML content copied into both services through an anchor. Compose then resolves variables and applies later files in command-line order. The worker remains defined but carries the ops profile, so the full rendered model includes it while the default service selection does not. The production overlay uses !override because its port list must replace, not accumulate with, the base port. The mount overlay demonstrates two sequence outcomes: a mount with the same container target changes the existing logical mount, while a mount with a new target is added. JSON output lets us test those meanings without depending on how YAML happens to be printed.

### self_check_questions
Can you explain why env_file does not set WEB_PORT during Compose interpolation?
Can you explain why worker is in rendered.base.json but absent from services.default.txt?
Can you identify which file must appear last to change the production port?
Can you explain why /usr/share/nginx/html changes source while /srv/shared is appended?
Can you justify checking semantic port fields instead of a short port string?

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain |
| 3 | [Lab](./lab.md) | Practice |
| 4 | [Homework](./homework.md) | Apply |
| 5 | [Quiz](./quiz.md) | Test |

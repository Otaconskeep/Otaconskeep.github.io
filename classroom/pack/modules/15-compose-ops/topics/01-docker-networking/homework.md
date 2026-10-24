# Homework: Docker Networking

**Module:** Compose Operations & IaC
**Activity type:** Homework / independent application
**Objective:** Explain the difference between a container port and a host-published port

## Requirements

Draw the two networks and label every container interface, allowed flow, blocked flow, and listening port.
Add a second frontend-only client service under /opt/lab-classroom/class79/ and prove that it can reach gateway but not database.
Temporarily attach the second client to backend, predict the result before testing, then remove that attachment and recreate the service.
Use docker network inspect on the project networks and compare the endpoint lists with each container's NetworkSettings.Networks output.
Write a short threat model explaining what happens if the dual-homed gateway is compromised and which application-level controls would still be required.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

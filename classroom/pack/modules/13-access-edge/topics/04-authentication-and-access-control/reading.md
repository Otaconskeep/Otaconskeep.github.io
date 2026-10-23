# Reading: Authentication and Access Control

**Module:** Edge Access & VPN
**Activity type:** Reading (Learn)
**Objective:** Explain the difference between identification, authentication, authorization, and accounting.

## Vocabulary

| Term | Meaning |
|---|---|
| Identification | The act of claiming an identity, such as submitting a username. A claim alone does not prove that the claimant owns the identity. |
| Authentication | The process of verifying an identity claim using one or more authenticators. |
| Authorization | The decision about whether an authenticated principal may perform a particular action on a resource. |
| Accounting | Recording security-relevant activity so that administrators can investigate, review, and attribute events. |
| Principal | An authenticated user, service, device, or workload to which permissions can be assigned. |
| Authenticator | Something used to demonstrate control of an identity, such as a password, security key, certificate, or one-time-code device. |
| Authentication factor | A factor category such as something known, possessed, or inherent. Two passwords are not two independent factors because both are knowledge factors. |
| Password verifier | A derived value stored by a service and used to check a submitted password without storing the original password. |
| Salt | A unique, non-secret random value incorporated into password derivation to prevent equal passwords from producing equal stored verifiers and to frustrate precomputed attacks. |
| RBAC | Role-based access control, in which permissions are assigned to roles and roles are assigned to principals. |
| ABAC | Attribute-based access control, in which policy evaluates attributes such as user, resource, device, network, action, and time. |
| Least privilege | Granting only the permissions needed for a defined task and retaining them only as long as needed. |
| Default deny | Rejecting an operation unless a policy explicitly allows it. |
| Privilege escalation | Obtaining permissions beyond those originally assigned, either through an approved elevation process or through a vulnerability. |
| Federation | A trust arrangement in which one system accepts identity assertions issued by another system. |
| Session | A bounded period during which a service associates requests with a previously authenticated principal. |

## Instruction

Authentication and authorization answer different questions. Identification asks who a subject claims to be. Authentication evaluates evidence for that claim. Authorization begins only after the service has a trustworthy principal and asks whether that principal may perform a specific action on a specific resource. Accounting records what happened. A successful login must never be treated as permission to do everything: every protected operation needs an authorization decision, including API requests, background jobs, administrative interfaces, and object-level access.

Passwords should not be stored in plaintext or with fast general-purpose hashing alone. A service stores a verifier generated with a password-oriented derivation function, a unique random salt, and a reviewed work factor. The salt need not be secret. Its purpose is to make identical passwords produce different verifiers and to defeat useful precomputation. Verification should use a constant-time comparison primitive. Password policy should favor length, permit password managers, screen known-compromised values where practical, and avoid arbitrary composition rules that push users toward predictable patterns. Production choices should follow current platform guidance because algorithms and recommended work factors change. The PBKDF2 settings in this isolated lesson demonstrate the structure of password verification; they are not a universal production recommendation or a performance benchmark.

Multi-factor authentication combines independent factor categories. A password plus another password is still one factor category. A password plus a hardware-backed security key combines knowledge and possession. Recovery is part of the authentication system and must not be weaker than normal enrollment. Backup codes, help-desk resets, device replacement, and emergency access therefore require explicit controls, audit events, revocation procedures, and testing.

Authorization policy should be understandable, testable, and deny access when no rule explicitly permits it. RBAC is useful when job functions map cleanly to roles, but oversized roles can accumulate privilege. ABAC can express context-rich rules, yet complexity may make outcomes difficult to review. Many systems combine approaches: roles provide coarse entitlements while resource ownership, environment, device state, or time supplies additional conditions. Regardless of model, the server must enforce policy. Hiding a button in a user interface is not an authorization control.

The lab uses three roles and two permissions. A viewer may read inventory, an operator may read inventory and request a service restart, and an administrator has the permissions represented by the exercise. An account marked disabled is rejected even when its password is correct. Unknown users are checked against a dummy verifier so that the implementation does not immediately skip all expensive work. External authentication failures use the same message for an unknown username, a wrong password, and a disabled account. This reduces direct account-status disclosure, although production defenses must also consider timing, rate limits, response metadata, and behavior across recovery flows.

Audit records serve defenders and reviewers, but they can also create risk. Record event time, outcome, principal or submitted identifier, requested action, target, and relevant policy reason. Do not record passwords, session secrets, one-time codes, private keys, or complete recovery tokens. Protect logs from unauthorized reading and alteration, synchronize clocks, define retention, and monitor important events. An audit event does not replace prevention: it supports detection, investigation, and accountability after preventive policy has been applied.

## Architecture

### scope
A local, self-contained Python demonstration writes only an audit log beneath /opt/lab-classroom/class67/.

### components
An in-memory identity store containing usernames, unique salts, derived password verifiers, roles, and enabled status.
An authentication function that performs password derivation, constant-time comparison, account-status checking, and generic client-facing failure handling.
An RBAC policy mapping roles to permissions.
An authorization function that applies default deny and records its decision.
A JSON Lines audit file containing security events without passwords or password verifiers.
A test harness covering positive and negative security paths.

### decision_flow
The caller submits an identity claim and an authenticator.
The authentication layer selects the account record or a dummy record and verifies the submitted password.
A successful check for an enabled account produces a principal containing the username and role.
The authorization layer resolves the role's permissions and checks the requested permission.
The operation proceeds only when policy explicitly allows it.
Authentication and authorization outcomes are written as separate audit events.

### trust_boundaries
Submitted identity claims and passwords are untrusted input.
The identity store and policy are trusted by this demonstration but would require administrative protection in production.
An authenticated principal is trusted only as an identity statement; its requested operation still requires authorization.
Audit data is sensitive administrative data and is not intended for ordinary users.

## Required reading

- NIST SP 800-63B, Digital Identity Guidelines: Authentication and Lifecycle Management, especially the sections on authenticators, memorized secrets, and verifier requirements.
- OWASP Authentication Cheat Sheet, focusing on generic error messages, credential storage, reauthentication, and account recovery.
- OWASP Authorization Cheat Sheet, focusing on least privilege, deny by default, and permission checks on every request.
- Python documentation for hashlib.pbkdf2_hmac, secrets.token_bytes, and hmac.compare_digest.

## References

- NIST Special Publication 800-63B, Digital Identity Guidelines: Authentication and Lifecycle Management.
- NIST Special Publication 800-162, Guide to Attribute Based Access Control Definition and Considerations.
- NIST Special Publication 800-53 Revision 5, Security and Privacy Controls for Information Systems and Organizations, Access Control and Identification and Authentication control families.
- OWASP Authentication Cheat Sheet.
- OWASP Authorization Cheat Sheet.
- OWASP Password Storage Cheat Sheet.
- OWASP Session Management Cheat Sheet.
- OWASP Application Security Verification Standard, authentication, session management, and access-control requirements.
- Python Standard Library documentation for hashlib.
- Python Standard Library documentation for hmac.
- Python Standard Library documentation for secrets.

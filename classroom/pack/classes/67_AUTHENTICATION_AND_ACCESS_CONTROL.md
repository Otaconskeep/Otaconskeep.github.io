# Class 67: Authentication and Access Control

**Learning objective:** Explain the difference between identification, authentication, authorization, and accounting.; Describe passwords, security keys, one-time codes, certificates, and recovery mechanisms as authentication factors or supporting controls.; Store password verifiers using a unique salt and a deliberately expensive password-based key derivation function.; Implement role-based access control with default-deny behavior.; Return generic authentication failures while retaining useful internal audit details.; Recognize why authorization must be checked for every protected operation rather than only at login.; Verify allowed, denied, disabled-account, wrong-password, and unknown-user behavior.; Plan secure lifecycle controls for enrollment, privilege review, revocation, recovery, and audit retention.
**Bloom level:** Understand / Apply
**Track:** Identity, Security, and Systems Administration · **Difficulty:** intermediate · **Duration:** ~105 minutes · **Lab risk:** low
**Build output:** Teach homelab administrators how to distinguish authentication from authorization, design role-based permissions, apply default-deny decisions, protect stored credentials, and produce useful security audit events. The lab implements a self-contained authentication and authorization model without modifying host accounts, remote-access services, or system policy.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux distributions providing a POSIX-compatible shell and Python 3.8 or newer

### runtime
Python 3.8 or newer is required because the rollback uses Path.unlink with missing_ok.

### privileges
An authorized process may be needed to create the dedicated directory beneath /opt. The lesson should otherwise run as a non-privileged lab user that owns that directory.

### network
No network connectivity is required.

### dependencies
Only Python standard-library modules are used.

### filesystem_scope
/opt/lab-classroom/class67/

### repeatability
The main exercise may be rerun. Each run appends audit events, so verification intentionally does not depend on one exact event count.

## Learning objective

- Explain the difference between identification, authentication, authorization, and accounting.
- Describe passwords, security keys, one-time codes, certificates, and recovery mechanisms as authentication factors or supporting controls.
- Store password verifiers using a unique salt and a deliberately expensive password-based key derivation function.
- Implement role-based access control with default-deny behavior.
- Return generic authentication failures while retaining useful internal audit details.
- Recognize why authorization must be checked for every protected operation rather than only at login.
- Verify allowed, denied, disabled-account, wrong-password, and unknown-user behavior.
- Plan secure lifecycle controls for enrollment, privilege review, revocation, recovery, and audit retention.

## Why this matters

Teach homelab administrators how to distinguish authentication from authorization, design role-based permissions, apply default-deny decisions, protect stored credentials, and produce useful security audit events. The lab implements a self-contained authentication and authorization model without modifying host accounts, remote-access services, or system policy.

## Prerequisites

- Comfort using a Linux shell and running Python 3 programs.
- Basic understanding of users, groups, services, files, and permissions.
- Ability to create the dedicated directory /opt/lab-classroom/class67/.
- The lab directory must be new or reserved exclusively for this class.
- No production identity provider, host account database, or externally reachable service is required.

## Required reading

- NIST SP 800-63B, Digital Identity Guidelines: Authentication and Lifecycle Management, especially the sections on authenticators, memorized secrets, and verifier requirements.
- OWASP Authentication Cheat Sheet, focusing on generic error messages, credential storage, reauthentication, and account recovery.
- OWASP Authorization Cheat Sheet, focusing on least privilege, deny by default, and permission checks on every request.
- Python documentation for hashlib.pbkdf2_hmac, secrets.token_bytes, and hmac.compare_digest.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

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

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Draw an access-control matrix for three homelab roles, at least four resources, and at least five actions. Mark every cell as explicitly allowed or denied.
Extend the design on paper with a resource environment attribute such as development or production. State how an operator assigned to development is denied operations on production resources.
Write a session policy covering idle timeout, absolute lifetime, revocation after role changes, reauthentication for sensitive actions, and emergency invalidation.
Create an audit-event specification listing required fields, prohibited secret fields, retention expectations, and which event types should alert an administrator.
Threat-model account recovery by identifying assets, actors, entry points, likely abuse cases, preventive controls, and audit evidence.
Compare RBAC and ABAC for a homelab containing human administrators, automation services, monitoring agents, and guest users. Recommend where each model is appropriate.

## Feynman teach-back

### prompt
Explain the system to a new homelab operator without using the words authentication or authorization at first.

### model_explanation
First, the service asks, 'Can you prove you are the identity you claimed?' After accepting that proof, it separately asks, 'Is this identity allowed to perform this exact action on this exact resource?' A valid identity may still receive a denial because proof of identity is not a universal permission grant. The system records both decisions without recording the submitted secret. In formal terms, the first decision is authentication and the second is authorization.

### self_test
Can you explain why a logged-in viewer must still be denied a service restart?
Can you explain why a salt may be stored beside a password verifier?
Can you explain why hiding an administrative control in a web page does not enforce access control?
Can you explain why the recovery process belongs inside the authentication threat model?

## Retrieval check

1. 1. What is the difference between identification, authentication, and authorization?
2. 2. Why should a service use a unique salt when deriving each password verifier?
3. 3. Does combining a password with a second password provide two independent authentication factors? Explain.
4. 4. Why must a protected API perform authorization checks even after a valid login?
5. 5. What does default deny mean in an access-control policy?
6. 6. Why should unknown users, disabled accounts, and incorrect passwords generally receive similar external error messages?
7. 7. Name two categories of data that should never be written to an authentication audit log.
8. 8. Why is hiding an administrative button insufficient to protect the administrative operation?
9. 9. What security problem can occur when roles continually gain permissions but are rarely reviewed?
10. 10. Why can a successful password check still result in an authentication failure for a disabled account?

## Guided lab

### name
Build and test a default-deny RBAC decision path

### constraints
Run this exercise only on a disposable or authorized homelab system.
Every filesystem mutation made by the exercise is confined to /opt/lab-classroom/class67/.
The exercise does not create operating-system users, change host authentication, or expose a network listener.
The sample credentials exist only inside the short-lived Python process and are not production secrets.

### steps
### step
1

### instruction
Create the dedicated lab directory with restrictive default permissions.

### command
umask 077 && mkdir -p /opt/lab-classroom/class67/
### step
2

### instruction
Run the demonstration. It builds an in-memory identity store, executes six tests, and appends JSON audit events to the dedicated lab directory.

### command
umask 077 && python3 - <<'PY'
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/opt/lab-classroom/class67')
AUDIT = BASE / 'audit.jsonl'
ITERATIONS = 210_000
GENERIC_FAILURE = 'Invalid credentials or account unavailable'

PERMISSIONS = {
    'viewer': {'inventory.read'},
    'operator': {'inventory.read', 'service.restart'},
    'administrator': {'inventory.read', 'service.restart', 'identity.manage'},
}

def derive(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)

def record_for(password, role, enabled=True):
    salt = secrets.token_bytes(16)
    return {
        'salt': salt,
        'verifier': derive(password, salt),
        'role': role,
        'enabled': enabled,
    }

USERS = {
    'alice': record_for('class67-alice-demo', 'viewer'),
    'bob': record_for('class67-bob-demo', 'operator'),
    'carol': record_for('class67-carol-demo', 'administrator', enabled=False),
}
DUMMY_SALT = secrets.token_bytes(16)
DUMMY_VERIFIER = derive('dummy-value-never-used-for-login', DUMMY_SALT)

def audit(event, **fields):
    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'event': event,
        **fields,
    }
    with AUDIT.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(entry, sort_keys=True) + '\n')

def authenticate(username, password):
    account = USERS.get(username)
    salt = account['salt'] if account else DUMMY_SALT
    expected = account['verifier'] if account else DUMMY_VERIFIER
    supplied = derive(password, salt)
    password_matches = hmac.compare_digest(supplied, expected)
    if account and password_matches and account['enabled']:
        audit('authentication_success', username=username)
        return {'username': username, 'role': account['role']}, None
    reason = 'unknown_user'
    if account and not password_matches:
        reason = 'invalid_password'
    elif account and password_matches and not account['enabled']:
        reason = 'account_disabled'
    audit('authentication_failure', username=username, reason=reason)
    return None, GENERIC_FAILURE

def authorize(principal, permission, resource):
    if not principal:
        return False
    allowed = permission in PERMISSIONS.get(principal['role'], set())
    audit(
        'authorization_allowed' if allowed else 'authorization_denied',
        username=principal['username'],
        role=principal['role'],
        permission=permission,
        resource=resource,
    )
    return allowed

def check(label, condition):
    if not condition:
        raise AssertionError(label)
    print('PASS:', label)

principal, error = authenticate('alice', 'class67-alice-demo')
check('viewer authentication succeeds', principal is not None and error is None)
check('viewer may read inventory', authorize(principal, 'inventory.read', 'node-01'))
check('viewer may not restart service', not authorize(principal, 'service.restart', 'node-01'))

principal, error = authenticate('bob', 'class67-bob-demo')
check('operator authentication succeeds', principal is not None and error is None)
check('operator may restart service', authorize(principal, 'service.restart', 'node-01'))

principal, error = authenticate('carol', 'class67-carol-demo')
check('disabled account is rejected generically', principal is None and error == GENERIC_FAILURE)

principal, error = authenticate('alice', 'wrong-password')
check('wrong password is rejected generically', principal is None and error == GENERIC_FAILURE)

principal, error = authenticate('mallory', 'anything')
check('unknown user is rejected generically', principal is None and error == GENERIC_FAILURE)

print('Audit path:', AUDIT)
PY
### step
3

### instruction
Inspect the audit file without displaying or searching for any real secrets. Confirm that the file contains parseable JSON events and that denied operations are represented.

### command
python3 - <<'PY'
import json
from pathlib import Path
p = Path('/opt/lab-classroom/class67/audit.jsonl')
rows = [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
print('event_count=', len(rows))
print('event_types=', sorted({row['event'] for row in rows}))
print('denied_permissions=', [row.get('permission') for row in rows if row['event'] == 'authorization_denied'])
assert rows
assert any(row['event'] == 'authentication_success' for row in rows)
assert any(row['event'] == 'authentication_failure' for row in rows)
assert any(row['event'] == 'authorization_allowed' for row in rows)
assert any(row['event'] == 'authorization_denied' for row in rows)
assert all('password' not in row for row in rows)
print('PASS: audit verification complete')
PY

### discussion_prompts
Why is the role checked again when a permission is requested even though authentication already succeeded?
What additional resource attributes would be needed to prevent an operator from restarting services on nodes outside the operator's assigned environment?
Which audit fields would help an incident responder without unnecessarily exposing secrets or personal data?
How would session expiration, role changes, and account disablement affect an already authenticated session in a production design?

## Expected results

- The first lab command creates /opt/lab-classroom/class67/ and does not intentionally modify files outside that directory.
- The demonstration prints PASS results for successful viewer and operator authentication.
- The viewer is allowed to read inventory but denied permission to restart a service.
- The operator is allowed to request a service restart.
- The disabled account, wrong password, and unknown username all receive the same client-facing failure text.
- The audit file contains authentication successes, authentication failures, authorization allowances, and authorization denials.
- The audit file does not contain a field named password.
- Each rerun appends another set of events, so the total event count may increase while the required event types remain present.

## Verification checkpoints

- [ ] Confirm that the lab printed PASS for every test and exited without an AssertionError.
- [ ] Run: test -f /opt/lab-classroom/class67/audit.jsonl && echo PASS
- [ ] Run: python3 -c "import json,pathlib; p=pathlib.Path('/opt/lab-classroom/class67/audit.jsonl'); rows=[json.loads(x) for x in p.read_text().splitlines() if x.strip()]; assert {'authentication_success','authentication_failure','authorization_allowed','authorization_denied'} <= {r['event'] for r in rows}; print('PASS')"
- [ ] Run: python3 -c "import json,pathlib; rows=[json.loads(x) for x in pathlib.Path('/opt/lab-classroom/class67/audit.jsonl').read_text().splitlines() if x.strip()]; assert any(r.get('role')=='viewer' and r.get('permission')=='service.restart' and r['event']=='authorization_denied' for r in rows); print('PASS')"
- [ ] Run: python3 -c "import json,pathlib; rows=[json.loads(x) for x in pathlib.Path('/opt/lab-classroom/class67/audit.jsonl').read_text().splitlines() if x.strip()]; assert all('password' not in r and 'verifier' not in r and 'salt' not in r for r in rows); print('PASS')"

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Creating the lab directory reports permission denied. | The current account cannot create directories beneath /opt, or the class directory has an unexpected owner. | Use an authorized administrative workflow to create only /opt/lab-classroom/class67/ for the learner, then rerun the lab as the learner. Do not broaden unrelated filesystem permissions. |
| The shell reports that python3 cannot be found. | Python 3 is not installed or is not available through the current command search path. | Install a vendor-supported Python 3 package using the host's normal package-management process, then confirm that python3 --version works before returning to the lab. |
| The demonstration ends with an AssertionError. | The copied program was altered, truncated, or executed by a shell that did not preserve the here-document exactly. | Start a fresh terminal, copy the complete command from step 2, and verify that the closing PY marker begins at the first column with no extra characters. |
| The audit event count is larger than expected. | The lab appends events and has been run more than once. | This is expected. Evaluate the presence and contents of event types rather than requiring one fixed count, or perform the documented rollback before a clean rerun. |
| Audit verification reports invalid JSON. | The audit file was manually edited, a previous process was interrupted during a write, or unrelated content was placed in the file. | Inspect only /opt/lab-classroom/class67/audit.jsonl, preserve it if investigation is needed, then perform rollback and rerun the lab to generate a clean file. |
| Rollback reports that the directory is not empty. | Additional files were placed in the class directory after the lab ran. | List and review the directory contents. Remove or relocate only files you have positively identified as class artifacts, then rerun the narrow rollback command. Do not replace it with an unbounded recursive deletion. |

## Security considerations

### principles
Deny by default and explicitly grant narrowly defined permissions.
Separate authentication from authorization and log their outcomes independently.
Apply server-side authorization to every protected operation and object.
Use unique salts, reviewed password-derivation settings, and constant-time verifier comparison.
Use generic external authentication errors while preserving limited diagnostic reasons in protected audit data.
Treat account recovery, enrollment, factor replacement, and emergency access as security-sensitive authentication paths.
Review role assignments periodically and revoke access promptly when responsibilities change.
Protect session identifiers and require expiration, revocation, and reauthentication for sensitive actions.
Do not include passwords, private keys, session tokens, or complete recovery credentials in logs.

### lab_limitations
The in-memory identity store is educational and is not a production identity database.
The sample work factor is not presented as a benchmark or universal configuration recommendation.
The exercise does not implement throttling, persistent lockout state, session management, federation, cryptographic key management, or multi-factor enrollment.
A dummy password derivation reduces a simple user-enumeration difference but does not prove that all observable timing is identical.
The audit file is locally writable by the lab owner and is not an append-only or remotely protected logging system.

### production_guidance
Prefer mature, maintained identity platforms over custom authentication code.
Use phishing-resistant authentication for privileged administration where supported.
Rate-limit authentication attempts using controls that resist denial-of-service abuse.
Inventory service accounts and use short-lived workload identities where possible.
Test object-level authorization because permission to access one object does not imply permission to access every object of the same type.
Generate alerts for privilege changes, disabled-account attempts, suspicious recovery activity, and repeated authorization denials.
Maintain tested emergency-access procedures with strong monitoring and post-use review.

## Rollback

### goal
Remove only the audit file created by this lesson and then remove the class directory if it is empty.

### precheck
Run: python3 -c "from pathlib import Path; p=Path('/opt/lab-classroom/class67'); print([x.name for x in p.iterdir()] if p.exists() else 'already absent')"

### command
python3 -c "from pathlib import Path; p=Path('/opt/lab-classroom/class67'); (p/'audit.jsonl').unlink(missing_ok=True); p.rmdir()"

### behavior
The directory removal intentionally fails if any unexpected file remains. This prevents the rollback from recursively deleting unreviewed content.

### postcheck
Run: python3 -c "from pathlib import Path; p=Path('/opt/lab-classroom/class67'); print('PASS' if not p.exists() else 'REVIEW REQUIRED')"

## Video narration notes

Welcome to Class 67, Authentication and Access Control. This lesson separates four ideas that are often blended together: identification, authentication, authorization, and accounting. A username is an identity claim. Checking an authenticator determines whether that claim should be trusted. Once a principal has been established, a separate policy determines whether that principal may perform a requested operation. Finally, security events are recorded for review.

Our lab remains entirely inside the Class 67 directory. It does not change host accounts or expose a network service. The demonstration creates three in-memory accounts. Alice has the viewer role, Bob has the operator role, and Carol represents a disabled administrator account. Passwords are converted into verifiers using PBKDF2 with unique random salts. Submitted and stored verifier values are compared with a constant-time comparison function.

Notice the negative paths. Alice can read inventory but cannot restart a service. Bob can restart the service because that permission is assigned to the operator role. Carol cannot authenticate while disabled, even with the correct password. A wrong password and an unknown username are also rejected. The client receives the same generic failure text in all three cases, while the protected audit record retains a reason that can help an administrator investigate.

The most important design rule is that a valid login is not a universal authorization grant. Every sensitive operation must reach a server-side policy check, and the safe fallback is denial. Interfaces may hide controls for usability, but an attacker can bypass an interface and address an endpoint directly.

After running the lab, inspect the JSON Lines audit file. It should show both successful and failed authentication events, along with allowed and denied authorization decisions. It should not contain passwords, salts, or verifiers. In a production environment, these records would need stronger integrity protection, access restrictions, retention policy, monitoring, and reliable time synchronization.

Complete the lesson by explaining the flow in plain language: first prove who you are; then determine what that identity may do; finally record the security-relevant result without recording the secret. If you can explain why each stage is separate and where it must be enforced, you understand the core of authentication and access control.

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

## Mastery gate

- [ ] Objectives demonstrated with evidence
- [ ] Feynman complete
- [ ] Quiz self-scored ≥80%
- [ ] Lab verification boxes checked
- [ ] Rollback understood

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Spiral hook

Return to this class whenever a later service fails for identity, process, log, remote access, update, or routing reasons covered here.

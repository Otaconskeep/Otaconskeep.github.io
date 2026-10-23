# Lab: Authentication and Access Control

**Module:** Edge Access & VPN
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain the difference between identification, authentication, authorization, and accounting.

## Before you start

- Comfort using a Linux shell and running Python 3 programs.
- Basic understanding of users, groups, services, files, and permissions.
- Ability to create the dedicated directory /opt/lab-classroom/class67/.
- The lab directory must be new or reserved exclusively for this class.
- No production identity provider, host account database, or externally reachable service is required.

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

## Verification

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

## Security

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

# Lab: Tailscale for Homelab Remote Access

**Module:** Edge Access & VPN
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain how Tailscale separates identity and policy decisions from encrypted peer-to-peer packet transport.

## Before you start

- Basic understanding of IP addresses, CIDR notation, TCP ports, and routing.
- Familiarity with JSON and a text editor.
- Python 3 available for local validation.
- The directory /opt/lab-classroom/ already exists and is writable, or an instructor can create the class68 child directory.
- No live Tailscale account or tailnet is required for this design-only lab.

## Guided lab

### name
Author and validate a least-privilege Tailscale design

### scope
This lab does not install Tailscale, join a device, change a live policy, or alter network state. All authored files and lab-created state must remain under /opt/lab-classroom/class68/.

### scenario
Alice, alice@example.com, is the homelab administrator and requires TCP ports 22 and 443 on the legacy host.
Bob, bob@example.com, is an operator and requires only TCP port 443 on the legacy host.
Carol, carol@example.com, is a contractor and must not reach TCP port 443 on the legacy host.
The legacy host is 192.168.50.10 and cannot run Tailscale.
A dedicated device named subnet-router will advertise a route to the legacy host.
Only 192.168.50.10/32 may be advertised and approved. The wider 192.168.50.0/24 must appear exactly once across the three learner-authored JSON files, solely as the destination of a negative route-scope test.
The subnet router must use tag:homelab-router, with tag ownership assigned to group:admins.
Device approval and route approval are both required.
An exit node is not required and must be represented by the JSON boolean false.
The rollout must contain at least three phases and exactly three distinct rollback triggers.

### files
### path
/opt/lab-classroom/class68/architecture.json

### learner_authored
True

### required_shape
An object containing identities, groups, tags, devices, access_intent, and decisions. Each decisions value must explain the selected identity model, route scope, or denial model in at least 40 characters.
### path
/opt/lab-classroom/class68/test-matrix.json

### learner_authored
True

### required_shape
An array of exactly six objects. Each object contains id, source, destination, service, and expected.
### path
/opt/lab-classroom/class68/rollout.json

### learner_authored
True

### required_shape
An object containing approvals_before_enable, phases, rollback_triggers, and route_withdrawal. Every phase contains name, owner, success_criteria, and rollback_action.
### path
/opt/lab-classroom/class68/check_design.py

### learner_authored
False

### required_shape
The supplied Python checker. It reads the three learner-authored files and reports assertion failures without rewriting them.

### steps
1. Create the workspace with: mkdir /opt/lab-classroom/class68
2. Using a text editor, author architecture.json, test-matrix.json, and rollout.json from the scenario. Do not copy a prebuilt architecture. Select and document the identity mappings, narrow route, intended allows, intended denials, approval gates, rollout phases, and rollback language. Save only under /opt/lab-classroom/class68/.
3. Save the supplied checker as /opt/lab-classroom/class68/check_design.py and run: python3 /opt/lab-classroom/class68/check_design.py. The checker asserts all of the following: the three people have unique identities and required group memberships; the router tag is owned by administrators; the router requires device approval; exit_node_required is the boolean false; advertised and approved routes are exactly 192.168.50.10/32; the five host-level access intentions match the scenario; each design rationale is substantive; the matrix contains exactly six unique IDs and six unique flow assertions; all required allow and deny outcomes are present; there are exactly three denied tests; 192.168.50.0/24 occurs exactly once across the learner JSON files; both approval gates are listed; there are at least three complete rollout phases; there are exactly three unique rollback triggers; and route withdrawal is assigned to group:admins for 192.168.50.10/32.
4. Read every failure message rather than weakening the checker. Correct the learner-authored JSON documents and rerun the checker until it prints PASS.
5. Review the final files with: ls -la /opt/lab-classroom/class68/ and confirm that no lab artifact was created outside the class directory.

### checker_code
from pathlib import Path
import json
import sys

ROOT = Path('/opt/lab-classroom/class68')
errors = []

def load_json(name):
    path = ROOT / name
    try:
        with path.open('r', encoding='utf-8') as handle:
            return json.load(handle)
    except FileNotFoundError:
        errors.append(f'{name}: file is missing')
    except json.JSONDecodeError as exc:
        errors.append(f'{name}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}')
    return None

def require(condition, message):
    if not condition:
        errors.append(message)

architecture = load_json('architecture.json')
matrix = load_json('test-matrix.json')
rollout = load_json('rollout.json')

if architecture is not None:
    require(isinstance(architecture, dict), 'architecture.json must contain an object')
if matrix is not None:
    require(isinstance(matrix, list), 'test-matrix.json must contain an array')
if rollout is not None:
    require(isinstance(rollout, dict), 'rollout.json must contain an object')

if isinstance(architecture, dict):
    identities = architecture.get('identities', [])
    require(isinstance(identities, list), 'identities must be an array')
    expected_people = {
        'alice@example.com': ('Alice', 'group:admins'),
        'bob@example.com': ('Bob', 'group:operators'),
        'carol@example.com': ('Carol', 'group:contractors')
    }
    observed_people = {}
    if isinstance(identities, list):
        for item in identities:
            if isinstance(item, dict):
                observed_people[item.get('email')] = (item.get('name'), item.get('group'))
        emails = [item.get('email') for item in identities if isinstance(item, dict)]
        require(len(emails) == len(set(emails)), 'human identity email values must be unique')
    require(observed_people == expected_people, 'identities must map Alice, Bob, and Carol to the required unique email addresses and groups')

    groups = architecture.get('groups', {})
    require(isinstance(groups, dict), 'groups must be an object')
    if isinstance(groups, dict):
        require(set(groups.get('group:admins', [])) == {'alice@example.com'}, 'group:admins must contain only alice@example.com')
        require(set(groups.get('group:operators', [])) == {'bob@example.com'}, 'group:operators must contain only bob@example.com')
        require(set(groups.get('group:contractors', [])) == {'carol@example.com'}, 'group:contractors must contain only carol@example.com')

    tags = architecture.get('tags', {})
    tag_data = tags.get('tag:homelab-router', {}) if isinstance(tags, dict) else {}
    require(isinstance(tag_data, dict), 'tag:homelab-router must be an object')
    if isinstance(tag_data, dict):
        require(set(tag_data.get('owner_groups', [])) == {'group:admins'}, 'tag:homelab-router must be owned only by group:admins')

    devices = architecture.get('devices', [])
    require(isinstance(devices, list), 'devices must be an array')
    router = None
    if isinstance(devices, list):
        matches = [item for item in devices if isinstance(item, dict) and item.get('name') == 'subnet-router']
        require(len(matches) == 1, 'devices must contain exactly one device named subnet-router')
        if len(matches) == 1:
            router = matches[0]
    if router is not None:
        require(set(router.get('tags', [])) == {'tag:homelab-router'}, 'subnet-router must use only tag:homelab-router')
        require(router.get('device_approval_required') is True, 'device_approval_required must be the boolean true')
        require(router.get('exit_node_required') is False, 'exit_node_required must be the boolean false')
        require(router.get('advertised_routes') == ['192.168.50.10/32'], 'advertised_routes must be exactly [192.168.50.10/32]')
        require(router.get('approved_routes') == ['192.168.50.10/32'], 'approved_routes must be exactly [192.168.50.10/32]')

    expected_intent = {
        ('group:admins', '192.168.50.10', 'tcp/22', 'allow'),
        ('group:admins', '192.168.50.10', 'tcp/443', 'allow'),
        ('group:operators', '192.168.50.10', 'tcp/443', 'allow'),
        ('group:operators', '192.168.50.10', 'tcp/22', 'deny'),
        ('group:contractors', '192.168.50.10', 'tcp/443', 'deny')
    }
    access_intent = architecture.get('access_intent', [])
    require(isinstance(access_intent, list), 'access_intent must be an array')
    observed_intent = set()
    if isinstance(access_intent, list):
        for item in access_intent:
            if isinstance(item, dict):
                observed_intent.add((item.get('source'), item.get('destination'), item.get('service'), item.get('effect')))
    require(observed_intent == expected_intent, 'access_intent must contain exactly the five required host-level allow and deny intentions')

    decisions = architecture.get('decisions', {})
    require(isinstance(decisions, dict), 'decisions must be an object')
    for key in ('identity_model', 'route_scope', 'denial_model'):
        value = decisions.get(key, '') if isinstance(decisions, dict) else ''
        require(isinstance(value, str) and len(value.strip()) >= 40, f'decisions.{key} must contain a rationale of at least 40 characters')

if isinstance(matrix, list):
    require(len(matrix) == 6, 'test matrix must contain exactly six tests')
    ids = [item.get('id') for item in matrix if isinstance(item, dict)]
    require(len(ids) == 6 and all(isinstance(value, str) and value.strip() for value in ids), 'all six tests must have non-empty string IDs')
    require(len(ids) == len(set(ids)), 'all six test IDs must be unique')
    expected_tests = {
        ('alice@example.com', '192.168.50.10', 'tcp/22', 'allow'),
        ('alice@example.com', '192.168.50.10', 'tcp/443', 'allow'),
        ('bob@example.com', '192.168.50.10', 'tcp/443', 'allow'),
        ('bob@example.com', '192.168.50.10', 'tcp/22', 'deny'),
        ('carol@example.com', '192.168.50.10', 'tcp/443', 'deny'),
        ('alice@example.com', '192.168.50.0/24', 'route', 'deny')
    }
    observed_tests = set()
    for item in matrix:
        if isinstance(item, dict):
            observed_tests.add((item.get('source'), item.get('destination'), item.get('service'), item.get('expected')))
    require(len(observed_tests) == 6, 'the matrix must contain six unique flow assertions')
    require(observed_tests == expected_tests, 'the six matrix outcomes must exactly match the scenario, including all required denials')
    deny_count = sum(1 for item in matrix if isinstance(item, dict) and item.get('expected') == 'deny')
    require(deny_count == 3, 'the test matrix must contain exactly three expected denials')

if isinstance(rollout, dict):
    approvals = rollout.get('approvals_before_enable', [])
    require(isinstance(approvals, list), 'approvals_before_enable must be an array')
    if isinstance(approvals, list):
        normalized = {str(item).strip().lower() for item in approvals}
        require(normalized == {'device approval', 'route approval'}, 'approvals_before_enable must list exactly device approval and route approval')

    phases = rollout.get('phases', [])
    require(isinstance(phases, list) and len(phases) >= 3, 'rollout must contain at least three phases')
    if isinstance(phases, list):
        for index, phase in enumerate(phases, start=1):
            require(isinstance(phase, dict), f'rollout phase {index} must be an object')
            if isinstance(phase, dict):
                for key in ('name', 'owner', 'success_criteria', 'rollback_action'):
                    value = phase.get(key)
                    require(isinstance(value, str) and bool(value.strip()), f'rollout phase {index} requires a non-empty {key}')

    triggers = rollout.get('rollback_triggers', [])
    require(isinstance(triggers, list), 'rollback_triggers must be an array')
    if isinstance(triggers, list):
        require(len(triggers) == 3, 'rollout must contain exactly three rollback triggers')
        normalized_triggers = [str(item).strip() for item in triggers]
        require(all(len(item) >= 12 for item in normalized_triggers), 'each rollback trigger must be descriptive rather than a short label')
        require(len(set(normalized_triggers)) == 3, 'all three rollback triggers must be unique')

    withdrawal = rollout.get('route_withdrawal', {})
    require(isinstance(withdrawal, dict), 'route_withdrawal must be an object')
    if isinstance(withdrawal, dict):
        require(withdrawal.get('route') == '192.168.50.10/32', 'route_withdrawal.route must be 192.168.50.10/32')
        require(withdrawal.get('owner') == 'group:admins', 'route withdrawal must be owned by group:admins')
        procedure = withdrawal.get('procedure', '')
        require(isinstance(procedure, str) and len(procedure.strip()) >= 40, 'route withdrawal procedure must contain at least 40 characters')

if architecture is not None and matrix is not None and rollout is not None:
    serialized = json.dumps([architecture, matrix, rollout], sort_keys=True)
    require(serialized.count('192.168.50.0/24') == 1, '192.168.50.0/24 must occur exactly once across the three learner-authored JSON files')

if errors:
    print('FAIL')
    for error in errors:
        print(f'- {error}')
    sys.exit(1)

print('PASS: architecture, six tests, approvals, route scope, rollout, and rollback assertions are valid')


## Expected results

- architecture.json contains learner-selected identity mappings, human groups, a router tag, one /32 advertised route, one /32 approved route, explicit device approval, exit_node_required set to the boolean false, five access intentions, and three written design rationales.
- test-matrix.json contains exactly six uniquely identified and unique flow tests: three expected allows and three expected denials.
- The rejected prefix 192.168.50.0/24 appears exactly once across the three learner-authored JSON files and appears only as the destination of the negative route-scope test.
- rollout.json contains both approval gates, at least three complete phases, exactly three distinct rollback triggers, and an administrator-owned route-withdrawal procedure.
- The checker exits successfully and prints: PASS: architecture, six tests, approvals, route scope, rollout, and rollback assertions are valid.
- A portable directory listing shows only the intended class files under /opt/lab-classroom/class68/.

## Verification

- [ ] Run: python3 /opt/lab-classroom/class68/check_design.py. Confirm it re-runs every lab assertion and exits with status zero.
- [ ] Verify identities and groups: the checker must confirm three unique human email identities and the exact Alice-to-admins, Bob-to-operators, and Carol-to-contractors memberships.
- [ ] Verify tag ownership and enrollment: the checker must confirm that tag:homelab-router is owned only by group:admins and that device_approval_required is the boolean true.
- [ ] Verify exit-node scope: the checker must confirm that exit_node_required is the boolean false.
- [ ] Verify route scope: the checker must confirm that advertised_routes and approved_routes are each exactly [192.168.50.10/32].
- [ ] Verify access intent and rationale: the checker must confirm the five required host-level allow or deny intentions and at least 40 characters for each identity, route, and denial rationale.
- [ ] Verify the matrix: the checker must confirm exactly six non-empty unique IDs, six unique flow assertions, the complete required outcome set, and exactly three expected denials.
- [ ] Verify the broad-prefix sentinel: the checker must confirm that 192.168.50.0/24 occurs exactly once across architecture.json, test-matrix.json, and rollout.json.
- [ ] Verify rollout controls: the checker must confirm exactly the device approval and route approval gates, at least three complete phases, exactly three unique descriptive rollback triggers, and route withdrawal owned by group:admins for 192.168.50.10/32.
- [ ] Run the portable listing command: ls -la /opt/lab-classroom/class68/ and confirm the intended architecture.json, test-matrix.json, rollout.json, and check_design.py files are present.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The checker reports that a JSON file is invalid. | A comma, quote, bracket, brace, or JSON boolean is malformed. | Open the named file, inspect the reported line and column, and remember that JSON uses true and false without quotation marks. |
| The checker says exit_node_required must be the boolean false. | The value was written as the string "false", omitted, or set to true. | Set the subnet-router field to the JSON boolean false without quotation marks. |
| The checker reports more than one occurrence of 192.168.50.0/24. | The rejected broad prefix was repeated in a rationale, route list, rollout note, or more than one test. | Keep the broad prefix only in the single negative route-scope test. Refer to it generically as the broad prefix elsewhere in learner-authored files. |
| The checker reports that six tests exist but the flow assertions are not unique. | Two test IDs differ while their source, destination, service, and expected result are identical. | Compare complete test tuples and replace the duplicate with the missing scenario assertion. |
| The access intentions fail even though the test matrix passes. | The architecture document and validation matrix describe different policies, or the architecture includes an extra broad permission. | Align access_intent with the five required host-level relationships and keep the route-scope denial in the matrix. |
| The approvals assertion fails. | Device approval and route approval were treated as one control or extra approval labels were added. | List exactly two separate values under approvals_before_enable: device approval and route approval. |
| The rollback trigger assertion fails. | There are not exactly three triggers, two are duplicates, or a trigger is only a short label. | Write exactly three distinct, observable conditions describing when access or route availability must be withdrawn. |
| The class directory cannot be created. | The learner account lacks permission under /opt/lab-classroom/ or the prerequisite parent directory is missing. | Ask the instructor to provision and assign the class68 directory. Do not redirect the lab to another path because the checker intentionally fixes the allowed workspace. |

## Security

Advertise the smallest practical prefix. Because the scenario requires only one host, 192.168.50.10/32 is justified and the full private subnet is not.
Use groups for humans, tags for non-human infrastructure, device approval for enrollment, route approval for advertised reachability, and access policy for source-to-destination authorization.
Treat device approval and route approval as separate gates. Approving a router device should not silently approve every route it advertises.
Do not configure an exit node when the requirement is only access to a private host. General internet forwarding expands the role and impact of the router.
Keep tag ownership narrow. Only the administrator group may assign or own the subnet-router role in this design.
Represent denied behavior through absent permissions and negative tests. Do not create an unnecessarily broad allow with the expectation that another layer will correct it.
Review identity lifecycle, device ownership, key expiration behavior, route advertisements, and policy changes periodically.
Protect the subnet-router host as infrastructure: minimize installed services, apply operating-system updates, monitor availability, and restrict administrative ownership.
A successful design checker proves internal consistency, not live enforcement. A production rollout still requires administrative review and controlled testing against the current Tailscale policy model.

## Rollback

### lab_rollback
Delete only the four class files from /opt/lab-classroom/class68/ using an editor or file manager, then remove the empty class68 directory if the instructor permits it. Do not alter any parent directory or live Tailscale state.

### production_concept
Stop the rollout when any defined rollback trigger occurs.
Remove approval for the 192.168.50.10/32 route or stop advertising that route according to the reviewed operational procedure.
Confirm that route availability has disappeared for all test identities.
If device trust is in question, disable or remove the subnet-router device independently of route approval.
Restore the last reviewed access policy rather than improvising a broader emergency permission.
Record the trigger, affected identities, timestamps, observations, and recovery decision before retrying.

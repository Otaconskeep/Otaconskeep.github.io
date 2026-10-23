# Class 68: Tailscale for Homelab Remote Access

**Learning objective:** Explain how Tailscale separates identity and policy decisions from encrypted peer-to-peer packet transport.; Choose groups for human identities, tags for non-human devices, and device approval as an enrollment gate.; Design a subnet-router route that exposes only the required 192.168.50.10 host rather than the full 192.168.50.0/24 network.; Distinguish device approval, route approval, access policy, subnet routing, and exit-node routing.; Author positive and negative access tests for administrators, operators, and contractors.; Validate six unique tests, an explicit false exit-node requirement, three rollback triggers, and exactly one deliberate reference to the rejected broad prefix.; Plan a staged rollout and reversible route withdrawal without changing a live tailnet.
**Bloom level:** Understand / Apply
**Track:** Homelab Networking and Secure Remote Access · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Design and validate a least-privilege Tailscale remote-access architecture for a homelab without modifying a live tailnet. The lesson focuses on identity-based access, groups, device tags, device and route approval, narrowly scoped subnet routes, negative access tests, rollout gates, and rollback planning.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### lab_platform
Any environment with Python 3 and access to /opt/lab-classroom/class68/.

### operating_system_notes
The checker uses only Python standard-library features. The verification listing uses ls -la and does not depend on non-portable find formatting options.

### tailscale_notes
The lab is a design simulation and does not require a particular Tailscale client release. Before production use, compare the design with current Tailscale policy, grants, subnet-routing, route-approval, device-approval, and tag-ownership documentation.

### policy_format_note
The learner JSON files are educational design documents, not a tailnet policy file and not a substitute for validating current production policy syntax.

## Learning objective

- Explain how Tailscale separates identity and policy decisions from encrypted peer-to-peer packet transport.
- Choose groups for human identities, tags for non-human devices, and device approval as an enrollment gate.
- Design a subnet-router route that exposes only the required 192.168.50.10 host rather than the full 192.168.50.0/24 network.
- Distinguish device approval, route approval, access policy, subnet routing, and exit-node routing.
- Author positive and negative access tests for administrators, operators, and contractors.
- Validate six unique tests, an explicit false exit-node requirement, three rollback triggers, and exactly one deliberate reference to the rejected broad prefix.
- Plan a staged rollout and reversible route withdrawal without changing a live tailnet.

## Why this matters

Design and validate a least-privilege Tailscale remote-access architecture for a homelab without modifying a live tailnet. The lesson focuses on identity-based access, groups, device tags, device and route approval, narrowly scoped subnet routes, negative access tests, rollout gates, and rollback planning.

## Prerequisites

- Basic understanding of IP addresses, CIDR notation, TCP ports, and routing.
- Familiarity with JSON and a text editor.
- Python 3 available for local validation.
- The directory /opt/lab-classroom/ already exists and is writable, or an instructor can create the class68 child directory.
- No live Tailscale account or tailnet is required for this design-only lab.

## Required reading

- Tailscale, What is Tailscale?: https://tailscale.com/kb/1151/what-is-tailscale
- Tailscale, How Tailscale works: https://tailscale.com/blog/how-tailscale-works
- Tailscale, Access control lists: https://tailscale.com/kb/1018/acls
- Tailscale, Subnet routers: https://tailscale.com/kb/1019/subnets
- Tailscale, Device approval: https://tailscale.com/kb/1099/device-approval

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Tailnet | The private Tailscale network containing authorized users, devices, policy, and administrative settings. |
| Coordination plane | The service that distributes identity, key, endpoint, and policy information so nodes can discover one another. It is distinct from the encrypted data path. |
| Data plane | The encrypted path carrying packets between Tailscale nodes, directly when possible or through a relay when a direct path cannot be established. |
| Group | A named collection of human identities used in access policy. Use a group when permissions follow a person's organizational role, such as administrators or operators. |
| Tag | A policy identity assigned to a non-human or role-based device. Use a tag for infrastructure such as a subnet router, not as a substitute for a human group. |
| Device approval | An administrative enrollment gate requiring a newly joined device to be approved before it participates normally. Use it to control device admission; do not treat it as a replacement for access policy. |
| Route approval | Administrative authorization for a route advertised by a subnet router. A device may be approved while one or more of its advertised routes remain unapproved. |
| Subnet router | A Tailscale node that advertises routes to selected devices or networks that do not run Tailscale themselves. |
| Exit node | A Tailscale node selected to carry a client's general internet-bound traffic. It is not required merely to reach a private homelab host through a subnet route. |
| CIDR prefix | An address and prefix length describing a routing range. A /32 IPv4 prefix selects exactly one address, while a /24 includes 256 addresses. |
| Least privilege | Granting only the identities, destinations, protocols, and services needed for a stated task. |
| Negative test | A test that is expected to be denied. Negative tests prove that unintended paths remain unavailable. |
| DERP relay | A Tailscale relay used when peers cannot establish a direct path. Traffic remains end-to-end encrypted while relayed. |

## Instruction

Tailscale creates an identity-aware private network on top of WireGuard-based encrypted tunnels. A device joins a tailnet, receives identity and policy information through the coordination plane, and then attempts to exchange data directly with authorized peers. If direct connectivity is unavailable, a relay can carry the encrypted packets without becoming the endpoint that decrypts them. This distinction matters operationally: policy distribution and peer discovery are control functions, while application packets belong to the data plane.

Remote access should start with identities and required flows rather than with an entire private network prefix. Human permissions belong in groups because people change roles and membership can be updated centrally. Infrastructure devices should normally receive tags because a router or service should not inherit the permissions of the person who enrolled it. Device approval answers whether a new device may join; route approval answers whether an advertised route may become usable; access policy answers which source may reach which destination and service. These controls complement one another rather than replacing one another.

A subnet router is appropriate when the destination cannot run Tailscale. In this class, only 192.168.50.10 must be reached, so the router advertises 192.168.50.10/32. Advertising 192.168.50.0/24 would expose routing potential for unrelated systems and is therefore rejected. An exit node is not needed because the objective is private-host access, not forwarding general internet traffic. The design must explicitly record exit_node_required as false so the distinction is testable.

Tailscale access policy is fundamentally allow-oriented: traffic without a matching permission remains unavailable. A design document may state intended denials, but an implementation should not invent a broad allow merely to compensate with a later deny. Verification must test both sides of the boundary. Administrators need management access, operators need the web service but not remote shell access, and contractors need no access to the host. A sixth route-scope test confirms that the rejected /24 is not treated as reachable. Rollout planning then adds approvals, success criteria, rollback triggers, and a route-withdrawal owner so access can be removed predictably if the design behaves unexpectedly.

## Architecture

### component
Human identity groups

### role
Represent administrators, operators, and contractors independently of their devices.

### design_rules
Use group:admins for Alice.
Use group:operators for Bob.
Use group:contractors for Carol.
Change group membership when a person's role changes rather than tagging a personal device as a human role.

### relationships
Groups are referenced by access intent.
The administrator group owns the subnet-router tag.
### component
Tagged subnet router

### role
Provides a route from the tailnet to the one legacy homelab host that cannot run Tailscale.

### design_rules
Assign tag:homelab-router.
Require device approval.
Advertise and approve only 192.168.50.10/32.
Record exit_node_required as false.

### relationships
The tag is owned by group:admins.
The device advertises the host route.
Route approval is separate from device approval.
### component
Access policy intent

### role
Defines the required identity-to-service relationships before any live policy is written.

### design_rules
Administrators may reach TCP port 22 and TCP port 443 on 192.168.50.10.
Operators may reach TCP port 443 but not TCP port 22.
Contractors may not reach TCP port 443 on the host.
Anything not granted remains unavailable.

### relationships
Sources are human groups.
The destination is reached through the tagged subnet router.
Negative tests verify missing permissions.
### component
Approval gates

### role
Prevent an enrolled device or advertised route from becoming trusted automatically.

### design_rules
Approve the router device only after its identity and ownership are checked.
Approve the /32 route only after the advertised prefix is reviewed.
Do not infer route approval from device approval.

### relationships
Device approval controls participation.
Route approval controls route availability.
Access policy still limits which identities may use the route.
### component
Validation and rollback plan

### role
Provides deterministic positive tests, negative tests, rollout phases, and withdrawal actions.

### design_rules
Maintain exactly six uniquely identified access tests.
Include three expected denials.
Define exactly three distinct rollback triggers.
Assign route withdrawal to group:admins.

### relationships
Tests validate the architecture document.
Rollout gates depend on test results.
Rollback removes route availability without broadening another permission.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Extend the design without changing its least-privilege principle.

### tasks
Add a hypothetical second legacy service with a different single-host address and justify its prefix length.
Decide whether operators need the new service and add both a positive and a negative test.
Describe how offboarding Carol would differ from retiring the subnet router.
Explain what evidence should be collected before and after route approval.
Keep all optional homework artifacts under /opt/lab-classroom/class68/.

### submission
Submit the revised design, test rationale, and a short explanation of why group membership, tag ownership, device approval, and route approval solve different problems.

## Feynman teach-back

### prompt
Explain the design to a new homelab operator without using the words VPN, ACL, or zero trust.

### required_points
People receive permissions through role groups.
The router receives a device role through a tag.
Device approval decides whether the router may join, while route approval decides whether its host route may be used.
Only one legacy host is routed, so a /32 is used instead of the whole subnet.
Administrators receive two services, operators receive one, and contractors receive none.
An exit node is unnecessary because ordinary internet traffic is not part of the requirement.
Negative tests and rollback triggers prove the boundary and provide a safe stopping plan.

### self_check
If the explanation implies that an approved device automatically has permission to every destination, or that a subnet router must also be an exit node, revise it.

## Retrieval check

1. 1. When should a Tailscale group be used instead of a tag?
2. 2. Why does this architecture advertise 192.168.50.10/32 rather than 192.168.50.0/24?
3. 3. What is the difference between device approval and route approval?
4. 4. Why is exit_node_required false in this scenario?
5. 5. How should an intended denial normally be represented in an allow-oriented access policy?
6. 6. Why must the test matrix include negative tests as well as successful connections?
7. 7. What does the local Python checker prove, and what does it not prove?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

Begin by separating the problem into identity, device role, routing, authorization, validation, and rollback. Alice, Bob, and Carol are people, so place them in human groups. The subnet router is infrastructure, so identify it with tag:homelab-router and let only administrators own that tag. Next, examine the routing requirement. The destination is one legacy host at 192.168.50.10, not every address in its subnet. The correct advertised and approved route is therefore 192.168.50.10/32.

Now separate the approval gates. Device approval admits the router device. Route approval makes its advertised host route available. Neither decision grants Alice, Bob, or Carol application access by itself. Access intent supplies that boundary: Alice receives TCP ports 22 and 443, Bob receives only TCP port 443, and Carol receives neither. Because the policy model grants allowed paths, prohibited paths should remain unmatched and must be verified with negative tests.

The matrix has six unique tests. Three demonstrate required access, two demonstrate denied host services, and one rejects the broad subnet prefix. The broad prefix appears exactly once in learner-authored data so accidental use elsewhere is easy to detect. The design also states that no exit node is required because ordinary internet traffic is outside scope.

Finally, approvals and tests are not a rollback plan. A safe rollout needs staged phases, observable success criteria, exactly three distinct rollback triggers, and a named owner who can withdraw the /32 route. The Python checker evaluates these design assertions only. It does not contact Tailscale or claim that a live deployment works. That separation lets learners practice rigorous architecture and review without risking a production tailnet.

## References

- Tailscale, What is Tailscale?: https://tailscale.com/kb/1151/what-is-tailscale
- Tailscale, How Tailscale works: https://tailscale.com/blog/how-tailscale-works
- Tailscale, Access control lists: https://tailscale.com/kb/1018/acls
- Tailscale, Subnet routers: https://tailscale.com/kb/1019/subnets
- Tailscale, Device approval: https://tailscale.com/kb/1099/device-approval
- Tailscale, Tags: https://tailscale.com/kb/1068/acl-tags
- Tailscale, Exit nodes: https://tailscale.com/kb/1103/exit-nodes
- Python documentation, json module: https://docs.python.org/3/library/json.html
- Python documentation, pathlib module: https://docs.python.org/3/library/pathlib.html

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

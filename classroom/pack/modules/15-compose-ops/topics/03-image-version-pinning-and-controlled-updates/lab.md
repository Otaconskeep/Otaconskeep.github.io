# Lab: Image Version Pinning and Controlled Updates

**Module:** Compose Operations & IaC
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain why a mutable tag is unsuitable as the final deployment identity.

## Before you start

- Comfort using a Linux shell and Python 3.
- Basic familiarity with containers, image tags, JSON, and SHA-256 digests.
- Permission to create and modify files under /opt/lab-classroom/class81/.
- Understanding that this lab uses a local registry model and does not pull or run a real container image.

## Guided lab

### working_directory
/opt/lab-classroom/class81/

### scope_rule
Do not create, edit, move, or delete files outside /opt/lab-classroom/class81/ during this lab.

### setup_command
mkdir -p /opt/lab-classroom/class81/blobs && cd /opt/lab-classroom/class81 && python3 - <<'PY'
import json
from pathlib import Path
base = Path('/opt/lab-classroom/class81')
old = 'sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
candidate = 'sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
empty = 'sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
registry = {
  'repository': 'registry.lab/academy/demo',
  'channels': {'stable': 'index-v2', 'previous': 'index-v1'},
  'indexes': {
    'index-v1': {'manifests': [
      {'platform': {'os': 'linux', 'architecture': 'amd64'}, 'digest': old, 'blob': 'blobs/previous-amd64.manifest'}
    ]},
    'index-v2': {'manifests': [
      {'platform': {'os': 'linux', 'architecture': 'amd64'}, 'digest': candidate, 'blob': 'blobs/candidate-amd64.manifest'},
      {'platform': {'os': 'linux', 'architecture': 'arm64'}, 'digest': empty, 'blob': 'blobs/candidate-arm64.manifest'}
    ]}
  }
}
policy = {'allowed': [
  {'channel': 'stable', 'platform': 'linux/amd64', 'digest': candidate},
  {'channel': 'stable', 'platform': 'linux/amd64', 'digest': old}
]}
deployment = {
  'channel': 'stable',
  'platform': 'linux/amd64',
  'image': 'registry.lab/academy/demo@' + old
}
(base / 'blobs/previous-amd64.manifest').write_bytes(b'hello')
(base / 'blobs/candidate-amd64.manifest').write_bytes(b'abc')
(base / 'blobs/candidate-arm64.manifest').write_bytes(b'')
for name, value in [('registry.json', registry), ('policy.json', policy), ('deployment.json', deployment)]:
    (base / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
(base / 'audit.log').write_text('', encoding='utf-8')
PY

### update_program_command
cat > /opt/lab-classroom/class81/update.py <<'PY'
import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/opt/lab-classroom/class81')
DIGEST_RE = re.compile(r'^sha256:[0-9a-f]{64}$')

def load_json(name):
    with (BASE / name).open('r', encoding='utf-8') as handle:
        return json.load(handle)

def digest_bytes(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()

def image_digest(image):
    if '@' not in image:
        raise ValueError('deployment image is not digest pinned')
    value = image.rsplit('@', 1)[1]
    if not DIGEST_RE.fullmatch(value):
        raise ValueError('deployment image has an invalid digest')
    return value

def append_audit(event):
    with (BASE / 'audit.log').open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(event, sort_keys=True) + '\n')
        handle.flush()
        os.fsync(handle.fileno())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel', required=True)
    parser.add_argument('--platform', required=True)
    parser.add_argument('--expected-digest', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not DIGEST_RE.fullmatch(args.expected_digest):
        raise SystemExit('REJECT: malformed expected digest')
    if args.platform.count('/') != 1:
        raise SystemExit('REJECT: platform must be os/architecture')
    wanted_os, wanted_arch = args.platform.split('/', 1)
    registry = load_json('registry.json')
    policy = load_json('policy.json')
    deployment = load_json('deployment.json')
    index_name = registry.get('channels', {}).get(args.channel)
    if index_name is None:
        raise SystemExit('REJECT: unknown channel')
    index = registry.get('indexes', {}).get(index_name)
    if not isinstance(index, dict):
        raise SystemExit('REJECT: channel does not resolve to an index')
    matches = [d for d in index.get('manifests', []) if d.get('platform') == {'os': wanted_os, 'architecture': wanted_arch}]
    if len(matches) != 1:
        raise SystemExit('REJECT: platform selection must produce exactly one manifest')
    descriptor = matches[0]
    selected_digest = descriptor.get('digest', '')
    if not DIGEST_RE.fullmatch(selected_digest):
        raise SystemExit('REJECT: selected descriptor digest is malformed')
    blob_path = (BASE / descriptor.get('blob', '')).resolve()
    if BASE.resolve() not in blob_path.parents:
        raise SystemExit('REJECT: blob path escapes lab directory')
    actual_digest = digest_bytes(blob_path.read_bytes())
    if actual_digest != selected_digest:
        raise SystemExit('REJECT: selected manifest bytes do not match the index descriptor')
    if selected_digest != args.expected_digest:
        raise SystemExit('REJECT: selected manifest does not match the out-of-band expected digest')
    approved = any(item == {'channel': args.channel, 'platform': args.platform, 'digest': selected_digest} for item in policy.get('allowed', []))
    if not approved:
        raise SystemExit('REJECT: selected channel, platform, and digest tuple is not locally approved')
    prior_digest = image_digest(deployment.get('image', ''))
    new_deployment = {
      'channel': args.channel,
      'platform': args.platform,
      'image': registry['repository'] + '@' + selected_digest
    }
    if args.dry_run:
        print(json.dumps({'action': 'dry-run', 'index': index_name, 'selected_platform_manifest': selected_digest, 'from_digest': prior_digest, 'to_digest': selected_digest}, sort_keys=True))
        return
    target = BASE / 'deployment.json'
    backup = BASE / 'deployment.backup.json'
    temporary = BASE / 'deployment.json.tmp'
    shutil.copy2(target, backup)
    temporary.write_text(json.dumps(new_deployment, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(temporary, target)
    append_audit({
      'action': 'update',
      'channel': args.channel,
      'platform': args.platform,
      'from_digest': prior_digest,
      'to_digest': selected_digest,
      'time': datetime.now(timezone.utc).isoformat()
    })
    print('PROMOTED ' + new_deployment['image'])

if __name__ == '__main__':
    main()
PY

### rollback_program_command
cat > /opt/lab-classroom/class81/rollback.py <<'PY'
import argparse
import json
import os
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/opt/lab-classroom/class81')
DIGEST_RE = re.compile(r'^sha256:[0-9a-f]{64}$')

def load(path):
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)

def get_digest(document):
    image = document.get('image', '')
    if '@' not in image:
        raise SystemExit('REJECT: image is not digest pinned')
    digest = image.rsplit('@', 1)[1]
    if not DIGEST_RE.fullmatch(digest):
        raise SystemExit('REJECT: malformed image digest')
    return digest

def append_audit(event):
    with (BASE / 'audit.log').open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(event, sort_keys=True) + '\n')
        handle.flush()
        os.fsync(handle.fileno())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel', required=True)
    parser.add_argument('--platform', required=True)
    parser.add_argument('--expected-digest', required=True)
    args = parser.parse_args()
    if not DIGEST_RE.fullmatch(args.expected_digest):
        raise SystemExit('REJECT: malformed expected rollback digest')
    target = BASE / 'deployment.json'
    backup = BASE / 'deployment.backup.json'
    if not backup.is_file():
        raise SystemExit('REJECT: retained backup is unavailable')
    current = load(target)
    prior = load(backup)
    current_digest = get_digest(current)
    restore_digest = get_digest(prior)
    if prior.get('channel') != args.channel or prior.get('platform') != args.platform:
        raise SystemExit('REJECT: backup channel or platform does not match rollback approval')
    if restore_digest != args.expected_digest:
        raise SystemExit('REJECT: backup digest does not match the out-of-band rollback digest')
    policy = load(BASE / 'policy.json')
    approved = any(item == {'channel': args.channel, 'platform': args.platform, 'digest': restore_digest} for item in policy.get('allowed', []))
    if not approved:
        raise SystemExit('REJECT: rollback tuple is not locally approved')
    failed_copy = BASE / ('deployment.failed.' + str(time.time_ns()) + '.json')
    shutil.copy2(target, failed_copy)
    temporary = BASE / 'deployment.rollback.tmp'
    shutil.copy2(backup, temporary)
    if get_digest(load(temporary)) != args.expected_digest:
        raise SystemExit('REJECT: copied rollback candidate failed validation')
    os.replace(temporary, target)
    restored = load(target)
    if get_digest(restored) != args.expected_digest:
        raise SystemExit('REJECT: restored deployment failed post-replace validation')
    append_audit({
      'action': 'rollback',
      'channel': args.channel,
      'platform': args.platform,
      'from_digest': current_digest,
      'to_digest': restore_digest,
      'failed_state_copy': failed_copy.name,
      'time': datetime.now(timezone.utc).isoformat()
    })
    print('RESTORED ' + restored['image'])

if __name__ == '__main__':
    main()
PY

### steps
### name
Create the isolated registry model and programs

### commands
Run the setup_command.
Run the update_program_command.
Run the rollback_program_command.
cd /opt/lab-classroom/class81
### name
Inspect the index and platform descriptors

### commands
python3 -m json.tool /opt/lab-classroom/class81/registry.json
python3 -m json.tool /opt/lab-classroom/class81/deployment.json

### observation
stable resolves to index-v2. That index points separately to linux/amd64 and linux/arm64 manifests. The current deployment is pinned to the previous linux/amd64 digest rather than to stable.
### name
Verify the published golden vectors independently

### commands
cd /opt/lab-classroom/class81 && test "$(sha256sum blobs/previous-amd64.manifest | awk '{print $1}')" = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
cd /opt/lab-classroom/class81 && test "$(sha256sum blobs/candidate-amd64.manifest | awk '{print $1}')" = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
cd /opt/lab-classroom/class81 && test "$(sha256sum blobs/candidate-arm64.manifest | awk '{print $1}')" = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
### name
Prove dry-run does not mutate deployment or audit state

### commands
cd /opt/lab-classroom/class81 && cp deployment.json deployment.before-dry-run.json && cp audit.log audit.before-dry-run.log
cd /opt/lab-classroom/class81 && python3 update.py --channel stable --platform linux/amd64 --expected-digest sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad --dry-run
cd /opt/lab-classroom/class81 && cmp deployment.json deployment.before-dry-run.json && cmp audit.log audit.before-dry-run.log && test ! -e deployment.backup.json
### name
Prove a simultaneous catalog, content, and policy substitution is rejected

### commands
cd /opt/lab-classroom/class81 && cp registry.json registry.before-tamper.json && cp policy.json policy.before-tamper.json && cp blobs/candidate-amd64.manifest candidate.before-tamper.manifest && cp deployment.json deployment.before-rejection.json && cp audit.log audit.before-rejection.log
cd /opt/lab-classroom/class81 && python3 - <<'PY'
import json
from pathlib import Path
base = Path('/opt/lab-classroom/class81')
old = 'sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
new = 'sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08'
(base / 'blobs/candidate-amd64.manifest').write_bytes(b'test')
for name in ('registry.json', 'policy.json'):
    path = base / name
    path.write_text(path.read_text(encoding='utf-8').replace(old, new), encoding='utf-8')
PY
cd /opt/lab-classroom/class81 && if python3 update.py --channel stable --platform linux/amd64 --expected-digest sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad; then echo 'ERROR: substitution was accepted'; exit 1; else echo 'Expected rejection observed'; fi
cd /opt/lab-classroom/class81 && cmp deployment.json deployment.before-rejection.json && cmp audit.log audit.before-rejection.log && test ! -e deployment.backup.json
cd /opt/lab-classroom/class81 && cp registry.before-tamper.json registry.json && cp policy.before-tamper.json policy.json && cp candidate.before-tamper.manifest blobs/candidate-amd64.manifest

### observation
The substituted bytes and descriptor are internally consistent, and local policy was changed to approve them. Promotion still fails because the selected digest differs from the independently supplied expected digest.
### name
Perform the controlled update

### commands
cd /opt/lab-classroom/class81 && python3 update.py --channel stable --platform linux/amd64 --expected-digest sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
cd /opt/lab-classroom/class81 && python3 -m json.tool deployment.json
cd /opt/lab-classroom/class81 && python3 -m json.tool deployment.backup.json
cd /opt/lab-classroom/class81 && cat audit.log

## Expected results

- The stable channel resolves to index-v2, and linux/amd64 selection yields sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad rather than the linux/arm64 digest.
- The deployed image after promotion is registry.lab/academy/demo@sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad.
- The dry-run prints the selected index and digest transition but leaves deployment.json, audit.log, and backup state unchanged.
- A coordinated substitution of the candidate blob, descriptor digest, and policy approval is rejected because it differs from the out-of-band expected digest.
- The rejected update leaves deployment.json and audit.log byte-for-byte unchanged and creates no deployment.backup.json.
- A successful update retains deployment.backup.json containing the prior hello digest.
- The successful update audit event links from_digest sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824 to to_digest sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad.

## Verification

- [ ] Run: cd /opt/lab-classroom/class81 && test "$(sha256sum blobs/previous-amd64.manifest | awk '{print $1}')" = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824". This compares against the published golden digest for the exact bytes hello.
- [ ] Run: cd /opt/lab-classroom/class81 && test "$(sha256sum blobs/candidate-amd64.manifest | awk '{print $1}')" = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad". This compares against the published golden digest for the exact bytes abc.
- [ ] Run: cd /opt/lab-classroom/class81 && cmp deployment.json deployment.before-dry-run.json && cmp audit.log audit.before-dry-run.log. Both comparisons must succeed, proving dry-run left state unchanged.
- [ ] Run after the intentional rejection and before promotion: cd /opt/lab-classroom/class81 && cmp deployment.json deployment.before-rejection.json && cmp audit.log audit.before-rejection.log. Both comparisons must succeed, proving rejection left state unchanged.
- [ ] Run after promotion: cd /opt/lab-classroom/class81 && python3 - <<'PY'
import json
from pathlib import Path
base = Path('/opt/lab-classroom/class81')
old = 'sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
new = 'sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
deployment = json.loads((base / 'deployment.json').read_text())
backup = json.loads((base / 'deployment.backup.json').read_text())
events = [json.loads(line) for line in (base / 'audit.log').read_text().splitlines() if line]
assert deployment == {'channel': 'stable', 'platform': 'linux/amd64', 'image': 'registry.lab/academy/demo@' + new}
assert backup == {'channel': 'stable', 'platform': 'linux/amd64', 'image': 'registry.lab/academy/demo@' + old}
updates = [event for event in events if event.get('action') == 'update']
assert len(updates) == 1
assert updates[0]['from_digest'] == old
assert updates[0]['to_digest'] == new
assert updates[0]['channel'] == 'stable'
assert updates[0]['platform'] == 'linux/amd64'
print('deployment, retained backup, and audit linkage verified')
PY
- [ ] Run: cd /opt/lab-classroom/class81 && python3 - <<'PY'
import json
from pathlib import Path
r = json.loads(Path('registry.json').read_text())
i = r['indexes'][r['channels']['stable']]
selected = [d for d in i['manifests'] if d['platform'] == {'os': 'linux', 'architecture': 'amd64'}]
assert len(selected) == 1
assert selected[0]['digest'] == 'sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
assert r['repository'] + '@' + selected[0]['digest'] == json.loads(Path('deployment.json').read_text())['image']
print('index selection and manifest pin verified')
PY

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The golden digest test fails for candidate-amd64.manifest. | The file contains a newline, different capitalization, or bytes other than the exact three-byte sequence abc. | Run the setup command again or use Python to write b'abc' exactly to /opt/lab-classroom/class81/blobs/candidate-amd64.manifest. |
| update.py reports that the selected manifest bytes do not match the index descriptor. | A blob or its descriptor was changed without restoring the original test files. | Copy registry.before-tamper.json to registry.json and candidate.before-tamper.manifest to blobs/candidate-amd64.manifest, then rerun the golden digest checks. |
| update.py reports that the selected manifest does not match the out-of-band expected digest. | The command supplied a digest for another release or platform, or the catalog was intentionally substituted. | Do not weaken the check. Confirm the reviewed release digest and requested platform, restore the intended catalog for the lab, and rerun with the literal approved digest. |
| The platform selection does not produce exactly one manifest. | The requested platform is absent or the index contains duplicate descriptors for the same operating system and architecture. | Inspect registry.json and require one unambiguous descriptor for the requested platform. Do not silently select the first duplicate. |
| The rejection test unexpectedly creates deployment.backup.json. | The update program was modified so validation occurs after mutation, or a backup from an earlier successful update already exists. | Recreate the lab from the supplied setup and update program before the rejection test. Confirm every validation occurs before the backup and replacement operations. |
| Rollback reports that the retained backup is unavailable. | No successful update has occurred or the backup was manually moved. | Complete the controlled update first. Rollback must fail closed when the expected retained backup is absent. |
| An audit assertion reports more than one update event. | The successful update was executed multiple times without recreating the lab. | Inspect audit.log to understand the history. For the exact lesson assertion, rerun setup to begin with an empty audit log and perform one successful update. |

## Security

### controls_demonstrated
Deployment by immutable repository@sha256 reference instead of a mutable channel or tag.
Explicit index-to-platform-manifest resolution with rejection of missing or ambiguous platform matches.
Hash verification of selected manifest bytes against the selected index descriptor.
Required out-of-band expected channel, platform, and digest.
Exact local policy matching of the channel, platform, and selected manifest digest tuple.
Validation before mutation, atomic deployment replacement, retained backup state, and digest-linked audit events.
Independent golden values for known byte sequences and explicit unchanged-state assertions.

### fail_closed_behavior
The update rejects an unknown channel.
The update rejects a missing, malformed, or ambiguous platform selection.
The update rejects malformed digests and blob paths that escape the lab directory.
The update rejects when selected bytes disagree with the index descriptor.
The update rejects when the selected manifest differs from the out-of-band expected digest.
The update rejects when the exact channel, platform, and digest tuple is absent from local policy.
Rollback rejects a missing backup, an unpinned image, a tuple mismatch, an out-of-band digest mismatch, or a locally unapproved restoration.

### limitations
A self-consistent catalog digest is not publisher trust. An attacker controlling both content and its catalog digest can produce a valid hash relationship.
A self-consistent catalog hash is not a digital signature, does not identify the publisher, does not prove build provenance, and does not by itself enforce an approved digest.
The out-of-band expected digest detects substitutions that change the selected digest while the approved invocation remains trustworthy. It cannot detect malicious replacement of content with different bytes having the same SHA-256 digest, compromise of the approval source, or an operator intentionally supplying an attacker-approved digest.
The local policy check detects tuples absent from policy, but it cannot provide independent approval if policy.json and the invoking authority are both compromised.
This lab does not verify registry transport security, signatures, attestations, transparency logs, vulnerability status, image configuration, runtime behavior, or the authenticity of update.py itself.
The miniature manifest blobs are SHA-256 teaching vectors rather than runnable OCI JSON manifests. The index-selection and digest-pinning logic model the identity decisions without claiming to implement a complete registry client.
Production systems should combine digest pinning with protected change control, authenticated registries, signature or attestation verification, least privilege, monitored audit storage, and tested recovery procedures.

## Rollback

### precondition
Complete the successful controlled update so deployment.json contains the candidate digest and deployment.backup.json contains the previous approved digest.

### command
cd /opt/lab-classroom/class81 && python3 rollback.py --channel stable --platform linux/amd64 --expected-digest sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824

### verification_command
cd /opt/lab-classroom/class81 && python3 - <<'PY'
import json
from pathlib import Path
base = Path('/opt/lab-classroom/class81')
old = 'sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
new = 'sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
deployment = json.loads((base / 'deployment.json').read_text())
backup = json.loads((base / 'deployment.backup.json').read_text())
failed = list(base.glob('deployment.failed.*.json'))
events = [json.loads(line) for line in (base / 'audit.log').read_text().splitlines() if line]
rollbacks = [event for event in events if event.get('action') == 'rollback']
assert deployment['image'] == 'registry.lab/academy/demo@' + old
assert backup['image'] == 'registry.lab/academy/demo@' + old
assert failed
assert any(json.loads(path.read_text())['image'] == 'registry.lab/academy/demo@' + new for path in failed)
assert len(rollbacks) == 1
assert rollbacks[0]['from_digest'] == new
assert rollbacks[0]['to_digest'] == old
assert (base / rollbacks[0]['failed_state_copy']).is_file()
print('rollback, retained backup, failed-state evidence, and audit linkage verified')
PY

### behavior
The currently deployed candidate document is copied to a timestamped deployment.failed file before restoration.
The backup's channel, platform, pin format, out-of-band expected digest, and local approval are validated before restoration.
The backup is copied to a temporary restoration file rather than moved, so deployment.backup.json remains available.
The temporary copy is validated before atomic replacement, and deployment.json is validated again after replacement.
The rollback audit event is appended only after the restored deployment has passed post-replacement validation.
The rollback audit event links the failed candidate digest to the restored prior digest.

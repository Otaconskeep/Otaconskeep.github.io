# Class 81: Image Version Pinning and Controlled Updates

**Learning objective:** Explain why a mutable tag is unsuitable as the final deployment identity.; Distinguish an OCI image index from the platform-specific manifest selected from that index.; Resolve a channel to an index, select the exact operating-system and architecture descriptor, and deploy repository@sha256 using the selected manifest digest.; Require an out-of-band expected channel, platform, and digest in addition to catalog integrity and local policy checks.; Demonstrate that simultaneous edits to catalog content, catalog digest fields, and local policy still fail when they conflict with the out-of-band expected digest.; Verify independently published golden digests rather than trusting only a hash recomputed by the update program.; Prove that dry-run and rejected operations leave deployment and audit state unchanged.; Verify that audit records correctly link the prior deployment digest to the promoted digest.; Restore a prior deployment by copying rather than consuming the backup, preserving failed state, validating the approved rollback pin, and auditing only after restoration succeeds.
**Bloom level:** Understand / Apply
**Track:** Container Operations and Supply Chain · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Teach operators to distinguish mutable image tags, OCI image indexes, and platform-specific manifests; deploy an immutable repository@sha256 reference; require an out-of-band approved channel, platform, and digest; prove that dry runs and rejected updates do not mutate state; record auditable digest transitions; and perform a validated rollback without destroying the backup or failed deployment evidence.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_system
Linux

### required_tools
Python 3.8 or newer
POSIX-compatible shell
sha256sum
awk
cmp
cp
cat

### container_runtime
No container runtime is required; the lab models index resolution and immutable references with local files.

### python_notes
The scripts use pathlib, argparse, hashlib, shutil, json, datetime, os.replace, and time.time_ns from the Python standard library.

### filesystem_notes
The lab expects /opt/lab-classroom/class81/ to be writable. Atomic replacement assumes the temporary and target deployment files remain on the same filesystem.

### scope
All lab mutations are restricted to /opt/lab-classroom/class81/.

## Learning objective

- Explain why a mutable tag is unsuitable as the final deployment identity.
- Distinguish an OCI image index from the platform-specific manifest selected from that index.
- Resolve a channel to an index, select the exact operating-system and architecture descriptor, and deploy repository@sha256 using the selected manifest digest.
- Require an out-of-band expected channel, platform, and digest in addition to catalog integrity and local policy checks.
- Demonstrate that simultaneous edits to catalog content, catalog digest fields, and local policy still fail when they conflict with the out-of-band expected digest.
- Verify independently published golden digests rather than trusting only a hash recomputed by the update program.
- Prove that dry-run and rejected operations leave deployment and audit state unchanged.
- Verify that audit records correctly link the prior deployment digest to the promoted digest.
- Restore a prior deployment by copying rather than consuming the backup, preserving failed state, validating the approved rollback pin, and auditing only after restoration succeeds.

## Why this matters

Teach operators to distinguish mutable image tags, OCI image indexes, and platform-specific manifests; deploy an immutable repository@sha256 reference; require an out-of-band approved channel, platform, and digest; prove that dry runs and rejected updates do not mutate state; record auditable digest transitions; and perform a validated rollback without destroying the backup or failed deployment evidence.

## Prerequisites

- Comfort using a Linux shell and Python 3.
- Basic familiarity with containers, image tags, JSON, and SHA-256 digests.
- Permission to create and modify files under /opt/lab-classroom/class81/.
- Understanding that this lab uses a local registry model and does not pull or run a real container image.

## Required reading

- OCI Image Specification, Image Index: https://github.com/opencontainers/image-spec/blob/main/image-index.md
- OCI Image Specification, Manifest: https://github.com/opencontainers/image-spec/blob/main/manifest.md
- OCI Image Specification, Descriptor: https://github.com/opencontainers/image-spec/blob/main/descriptor.md
- Docker documentation, image digests: https://docs.docker.com/dhi/core-concepts/digests/
- NIST Secure Software Development Framework SP 800-218: https://csrc.nist.gov/publications/detail/sp/800-218/final

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| tag | A human-friendly and generally mutable image reference such as stable or 1.4. A registry operator can move a tag to a different object. |
| channel | An operational release stream, such as stable, that this lab maps to an image index. A channel is mutable and is not itself an immutable deployment identity. |
| image index | A multi-platform object containing descriptors for one or more platform-specific image manifests. A client selects a descriptor matching its requested operating system and architecture. |
| platform manifest | The manifest selected from an image index for one exact platform, such as linux/amd64. Its digest, rather than the channel name, becomes the deployment pin in this lab. |
| descriptor | Metadata pointing to content by digest and, when applicable, identifying the operating system and architecture for which that content was built. |
| digest pin | An immutable reference of the form repository@sha256:hexadecimal-value. The pin used here is the digest of the selected platform manifest. |
| out-of-band approval | An expected channel, platform, and digest supplied independently of the registry catalog being evaluated. In production this may come from a reviewed release record, deployment controller, or signed policy system. |
| fail closed | Refusing promotion when required input is missing, malformed, ambiguous, inconsistent, unapproved, or unverifiable. |
| audit linkage | A record that explicitly connects the digest deployed before an operation to the digest deployed after it. |

## Instruction

Container tags are convenient names, but they are usually mutable pointers. If a deployment records only academy/demo:stable, the bytes selected tomorrow may differ from the bytes selected today even though the text of the deployment reference has not changed. Digest pinning changes the final identity to a content-addressed reference such as academy/demo@sha256:ba7816bf..., making an unnoticed tag move insufficient to alter the deployed identity.

Multi-platform images add an important distinction. A channel or tag commonly resolves to an OCI image index. The index is not the same object as the image manifest used by a linux/amd64 node. The index contains descriptors for multiple platforms, and the client selects one matching the requested operating system and architecture. A policy intended to approve the runnable linux/amd64 artifact must therefore compare the digest of the selected linux/amd64 manifest, not merely a tag and not an unrelated platform descriptor. The lab registry models this explicitly: stable points to index-v2, index-v2 points to linux/amd64 and linux/arm64 manifests, and the deployment pin uses the selected linux/amd64 manifest digest.

Content hashing and authorization answer different questions. Recomputing a catalog-provided digest can detect accidental corruption when the declared digest and bytes no longer agree, but a party able to replace both the content and the digest can create a new self-consistent pair. A local policy file stored beside the catalog also does not solve that boundary if the same party can edit both files. For that reason, update.py requires an expected channel, platform, and digest supplied independently at invocation time. It checks the requested tuple, resolves the catalog index, selects exactly one matching platform descriptor, verifies the selected blob against the descriptor, compares the selected digest with the out-of-band expected digest, and then confirms local policy approval. Any mismatch is rejected before deployment, backup, or audit state is written.

The lab uses the published SHA-256 test vectors for the exact bytes abc, hello, and the empty byte string. Their literal golden values are included in the lesson and verification commands. This avoids relying solely on values generated by the setup code or by update.py. The dry-run and rejection tests also compare complete deployment and audit files before and after each attempt. A successful promotion creates a retained backup, atomically replaces deployment.json, and appends an audit event linking the previous digest to the new digest. Rollback copies the failed deployment aside, validates the retained backup against both an out-of-band rollback digest and local approval, copies rather than moves the backup into place, verifies the restored state, and only then appends the rollback event.

## Architecture

### scope
All generated and mutated files are confined to /opt/lab-classroom/class81/.

### flow
The stable channel resolves to index-v2 in registry.json.
index-v2 contains separate linux/amd64 and linux/arm64 descriptors.
The requested linux/amd64 platform selects the descriptor whose manifest blob is the exact byte sequence abc.
The selected descriptor digest is compared with the independently supplied expected digest.
The selected tuple is checked against policy.json.
The deployment is written as registry.lab/academy/demo@sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad.
A successful update retains deployment.backup.json and appends an audit record with from_digest and to_digest.

### trust_boundaries
registry.json and its blobs represent registry-controlled data and are not trusted merely because they agree with one another.
policy.json represents local authorization but is deliberately tested as mutable within the same lab boundary.
The command-line expected channel, platform, and digest model independently reviewed release approval.
The lesson's literal golden digest values are independently published expectations and are not generated by setup.py or update.py.

### golden_digests
### previous_manifest_exact_bytes
hello

### previous_manifest_sha256
sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824

### candidate_amd64_manifest_exact_bytes
abc

### candidate_amd64_manifest_sha256
sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad

### candidate_arm64_manifest_exact_bytes


### candidate_arm64_manifest_sha256
sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

### tampered_manifest_exact_bytes
test

### tampered_manifest_sha256
sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Add a canary channel that points to a new index while keeping stable unchanged. Require a distinct out-of-band digest and prove that a stable approval cannot authorize canary.
Add a negative test requesting linux/arm64 while supplying the linux/amd64 expected digest. Assert that deployment.json and audit.log remain byte-for-byte unchanged.
Extend update.py with an expected repository argument supplied out of band, then reject a catalog that substitutes a different repository while retaining the same manifest digest.
Design a production trust model that stores approvals outside the registry administrator's control and includes signature or attestation verification. Identify which principals may publish images, approve releases, and deploy them.
Write a test that introduces two linux/amd64 descriptors in index-v2 and confirms that the updater fails closed rather than selecting the first descriptor.

## Feynman teach-back

### prompt
Explain the update to a teammate without using the phrase secure because it is hashed.

### model_explanation
The stable channel points to an image index, and that index lists separate manifests for amd64 and arm64. We request linux/amd64, so only the amd64 descriptor is eligible. We verify that its bytes match its descriptor, but that alone is not approval because an attacker might replace both. We also require the digest that a reviewer supplied independently and require the same channel, platform, and digest tuple in local policy. Only after all checks agree do we write repository@sha256 for the selected amd64 manifest. The audit log records the old and new digests. A dry run or rejected update performs no write. Rollback keeps the backup, saves the failed state, verifies the approved old digest, restores it, and records the reverse digest transition.

## Retrieval check

1. Why is academy/demo:stable insufficient as the final identity of a controlled deployment?
2. When stable resolves to a multi-platform image index, which digest should a linux/amd64 deployment pin in this lesson?
3. Why does recomputing a catalog-provided digest not prove publisher trust or release approval?
4. What three out-of-band values does update.py require to constrain selection?
5. Why must the intentional simultaneous edit of the blob, descriptor digest, and policy still be rejected?
6. What must remain unchanged after a dry-run or rejected update?
7. Which audit fields prove linkage between the prior and promoted deployment identities?
8. Why does rollback copy deployment.backup.json instead of replacing the deployment by moving that backup?
9. When is the rollback audit event appended?
10. What important security property is not provided by the self-consistent hash check in this lab?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

Begin by showing deployment.json pinned to the SHA-256 digest for the exact bytes hello. Open registry.json and trace stable to index-v2. Emphasize that index-v2 is a multi-platform selection object, not the linux/amd64 manifest itself. Compare the linux/amd64 descriptor with the separate linux/arm64 descriptor, then show that the promoted reference uses the linux/amd64 manifest digest after the at-sign.

Run the literal golden-vector checks. Explain that these expected values are published in the lesson rather than generated by update.py. Next, save complete copies of deployment and audit state and perform the dry-run. Use cmp to prove that no state changed and confirm that no backup was created.

For the attack simulation, change the candidate bytes from abc to test, update the index descriptor to the correct digest for test, and change local policy to approve that same substituted digest. The catalog is now internally consistent and policy agrees with it. Invoke the updater with the independently approved abc digest. The operation must reject before any mutation because the selected digest and out-of-band digest differ. Prove deployment and audit files are unchanged, then restore the test fixtures.

Perform the real update. Inspect deployment.json to see the immutable repository@sha256 reference, inspect deployment.backup.json to see that the prior pin was retained, and inspect audit.log to verify the from_digest and to_digest linkage. Finally, run rollback with the independently supplied previous digest. Show the restored deployment, the still-retained backup, the timestamped copy of the failed candidate state, and the rollback event. Close by stating that hash consistency is useful but is not a signature, publisher identity, provenance statement, or substitute for independently protected approval.

## References

- Open Container Initiative Image Index specification: https://github.com/opencontainers/image-spec/blob/main/image-index.md
- Open Container Initiative Image Manifest specification: https://github.com/opencontainers/image-spec/blob/main/manifest.md
- Open Container Initiative Descriptor specification: https://github.com/opencontainers/image-spec/blob/main/descriptor.md
- Open Container Initiative Image Layout specification: https://github.com/opencontainers/image-spec/blob/main/image-layout.md
- Docker documentation on image digests: https://docs.docker.com/dhi/core-concepts/digests/
- NIST FIPS 180-4, Secure Hash Standard: https://csrc.nist.gov/pubs/fips/180-4/upd1/final
- NIST SP 800-218, Secure Software Development Framework: https://csrc.nist.gov/publications/detail/sp/800-218/final
- SLSA supply-chain security framework: https://slsa.dev/spec/

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

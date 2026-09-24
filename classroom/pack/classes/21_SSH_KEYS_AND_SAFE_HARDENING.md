# Class 21: SSH Keys and Safe Hardening

**Learning objective:** Explain the different roles of an SSH private key and public key.; Generate a passphrase-protected Ed25519 key pair in an isolated lab directory.; Inspect key fingerprints and verify restrictive private-key permissions.; Build a sandbox authorized_keys file with source and feature restrictions.; Identify high-value SSH daemon hardening directives and explain their operational impact.; Describe a staged production hardening process that avoids remote administrative lockout.; Recognize why host-key verification and private-key protection are separate security controls.
**Bloom level:** Understand / Apply
**Track:** Linux and Homelab Security · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach administrators how SSH key authentication works, how to generate and protect an Ed25519 key pair, how authorized-key restrictions reduce exposure, and how to plan SSH daemon hardening without risking remote lockout. The hands-on work is isolated to /opt/lab-classroom/class21/ and does not alter the active SSH service.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-22
**Compatibility:** ### operating_systems
Modern Linux distributions with GNU core utilities and OpenSSH client tools.
The optional syntax test requires an installed OpenSSH server binary and sudo permission.

### openssh_notes
Ed25519 support requires a sufficiently recent OpenSSH implementation.
The restrict authorization option requires a compatible OpenSSH version.
Directive availability, PAM interaction, include behavior, defaults, and service-management procedures vary by distribution.
FIPS-oriented environments may restrict Ed25519; follow the target platform's validated cryptographic policy.
The stat, find, grep, awk, cmp, and realpath command forms shown assume common GNU/Linux implementations.

### scope_guarantee
All lab write, permission-change, and deletion operations target only /opt/lab-classroom/class21/. Optional validation may read operating-system defaults and host-key metadata but does not apply or reload configuration.

## Learning objective

- Explain the different roles of an SSH private key and public key.
- Generate a passphrase-protected Ed25519 key pair in an isolated lab directory.
- Inspect key fingerprints and verify restrictive private-key permissions.
- Build a sandbox authorized_keys file with source and feature restrictions.
- Identify high-value SSH daemon hardening directives and explain their operational impact.
- Describe a staged production hardening process that avoids remote administrative lockout.
- Recognize why host-key verification and private-key protection are separate security controls.

## Why this matters

Teach administrators how SSH key authentication works, how to generate and protect an Ed25519 key pair, how authorized-key restrictions reduce exposure, and how to plan SSH daemon hardening without risking remote lockout. The hands-on work is isolated to /opt/lab-classroom/class21/ and does not alter the active SSH service.

## Prerequisites

- Comfort using a Linux shell and reading command output.
- Permission to create files under /opt/lab-classroom/class21/.
- The OpenSSH client tools, including ssh-keygen, must already be installed.
- Basic understanding of users, file ownership, and Unix permission modes.
- Awareness that this class creates a passphrase-protected training key that must never be reused as a production identity.

## Required reading

- OpenBSD manual page: ssh-keygen(1), especially key generation, fingerprints, and passphrase changes.
- OpenBSD manual page: ssh(1), especially IdentitiesOnly, identity files, and host-key verification.
- OpenBSD manual page: authorized_keys(5), especially the restrict and from options.
- OpenBSD manual page: sshd_config(5), especially authentication, forwarding, root login, and user-access directives.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Private key | The secret half of an asymmetric SSH identity. It remains on the client and must be protected from disclosure. |
| Public key | The shareable half of an SSH identity. A server can authorize it without learning the private key. |
| Fingerprint | A compact digest used to identify a key without comparing the complete encoded key. |
| authorized_keys | A per-account file listing public keys that may authenticate, optionally with restrictions attached to each key. |
| Host key | A server identity key used by an SSH client to determine whether it is connecting to the expected server. |
| Passphrase | A secret used to encrypt a private-key file at rest. It is not transmitted to the SSH server. |
| Public-key authentication | Authentication in which the client proves possession of a private key corresponding to a public key authorized by the server. |
| SSH agent | A process that can retain unlocked private keys in memory and answer signing requests for client applications. |
| Defense in depth | Using multiple independent controls so that failure of one control does not immediately result in compromise. |
| Remote lockout | Loss of administrative SSH access after a configuration, identity, network, or authorization error. |

## Instruction

SSH public-key authentication is based on proof of possession. The server stores a public key, while the client retains the corresponding private key. During authentication, the client signs protocol data with the private key; the server verifies the signature with the authorized public key. The private key is not uploaded to the server. A passphrase protects the private-key file if it is copied from disk, but it does not make an exposed or unlocked agent harmless. Use a distinct key for an administrative purpose or trust boundary so that one compromised identity does not silently grant access everywhere.

Ed25519 is a strong modern default for systems that support it. RSA may still be needed for specific compatibility requirements, but key type and signature compatibility must be evaluated against actual clients, servers, appliances, and compliance rules. A key comment is only a label; it is not a security boundary. Fingerprints provide a more reliable way to identify keys.

File permissions matter because another local user who can read a private key can attempt to use it. OpenSSH normally rejects private keys with overly broad permissions, but administrators should not rely solely on that safeguard. Directories holding private material should be private, and private-key files should normally be readable and writable only by their owner. Public keys are not secret, although unauthorized modification of an authorization file remains a serious integrity problem.

Server hardening must be staged. First establish and test key access for a named non-root administrative account. Keep an existing session open, verify a second independent login using the intended key, validate daemon syntax, confirm out-of-band or console recovery, and only then disable weaker authentication methods. A reload is generally safer than an abrupt restart because existing sessions can remain available, but behavior is platform-dependent. PasswordAuthentication and keyboard-interactive authentication are distinct controls on many systems. Root-login policy, forwarding, user allowlists, PAM integration, and vendor defaults must also be reviewed rather than copied blindly.

Client host-key verification protects against connecting to an impostor and is separate from user authentication. A valid user key sent through an unverified connection does not prove that the remote host is genuine. Treat unexpected host-key changes as an incident to investigate, not as an inconvenience to bypass. The lab below creates only inert fixtures and a training identity under /opt/lab-classroom/class21/. It does not install a key into a real account, change the running daemon, or reload a service.

## Architecture

### components
A client identity consisting of an Ed25519 private key and public key.
A sandbox authorized_keys file containing a restricted public-key entry.
A sandbox SSH daemon policy fixture for review and optional syntax checking.
Local inspection tools such as ssh-keygen, stat, grep, and cmp.

### trust_boundaries
The private key remains on the client side and must not be copied to the server.
The public key crosses the trust boundary and is installed only for the intended account.
The server host key authenticates the server to the client.
An SSH agent may sign on behalf of the user and therefore becomes part of the trusted computing base.

### data_flow
The client reads the private key locally, proves possession by signing SSH protocol data, and sends a signature rather than the private key. The server checks the signature against an authorized public key and applies any restrictions attached to that authorization entry.

### lab_scope
Every file created or modified by the lab is beneath /opt/lab-classroom/class21/. The active SSH service, real user home directories, system authorization files, and production daemon configuration are not changed.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Write a production change plan that includes prerequisites, a second-session test, syntax validation, log monitoring, a decision point, and console rollback. Do not execute it.
Review the authorized_keys(5) documentation for restrict, command, expiry-time, from, and permitopen. Describe one service-account use case for each relevant restriction.
Inventory the public-key fingerprints used by one non-production administrative account. Record ownership, purpose, creation date if known, and proposed retirement date without copying private material.
Compare password authentication, keyboard-interactive authentication, and public-key authentication on the OpenSSH version used in your homelab.
Explain how an SSH agent improves usability and how unrestricted agent forwarding can increase risk.

## Feynman teach-back

### prompt
Explain SSH key authentication to someone who thinks the public key is a password.

### model_explanation
The public key is more like a lock that can be copied safely. The private key is the only matching key and stays with the client. The server gives the client data to sign, and the client uses the private key to create proof. The server checks that proof with the public key. Seeing the public key does not provide the private key. A passphrase adds a locked container around the private-key file, while host-key verification answers a different question: whether the client reached the intended server.

### self_check
Can you explain why the private key must not be copied into authorized_keys?
Can you distinguish a user identity key from a server host key?
Can you explain why disabling passwords before testing a second key-based session can cause lockout?
Can you explain what a key restriction changes and what it does not change?

## Retrieval check

1. 1. Which member of an SSH key pair must remain secret?
2. 2. What security property does an SSH key fingerprint provide?
3. 3. Why should an administrator keep an existing SSH session open while applying a hardening change?
4. 4. Does a private-key passphrase get sent to the SSH server during public-key authentication?
5. 5. What does the authorized_keys restrict option generally do?
6. 6. Why is host-key verification still necessary when the user has a strong Ed25519 key?
7. 7. Is a successful daemon syntax test sufficient proof that a new administrative login will work?
8. 8. Why can disabling TCP forwarding be operationally disruptive?
9. 9. What is the purpose of testing with IdentitiesOnly when validating a specific key?
10. 10. Why is the 192.0.2.0/24 source restriction in this lab not appropriate to copy directly into production?

## Guided lab

### step
1

### title
Create the isolated workspace

### instructions
Create the class directory with restrictive access and assign it to the current user. Confirm the resolved path before continuing.

### commands
sudo install -d -m 0700 -o "$USER" -g "$(id -gn)" /opt/lab-classroom/class21
realpath /opt/lab-classroom/class21
stat -c '%A %a %U:%G %n' /opt/lab-classroom/class21
### step
2

### title
Generate a passphrase-protected training key

### instructions
Set a restrictive creation mask and generate an Ed25519 key. Enter a unique training passphrase when prompted. Do not reuse this key or passphrase in production.

### commands
umask 077; ssh-keygen -t ed25519 -a 64 -f /opt/lab-classroom/class21/class21_ed25519 -C "class21-training-key"
### step
3

### title
Inspect permissions, type, and fingerprint

### instructions
Confirm that the private key is not accessible to group or other users. Then inspect the public-key fingerprint and encoded key type.

### commands
stat -c '%A %a %U:%G %n' /opt/lab-classroom/class21/class21_ed25519 /opt/lab-classroom/class21/class21_ed25519.pub
ssh-keygen -lf /opt/lab-classroom/class21/class21_ed25519.pub
awk '{print "key_type=" $1; print "comment=" $3}' /opt/lab-classroom/class21/class21_ed25519.pub
### step
4

### title
Prove that the public key matches the private key

### instructions
Derive a public key from the private key, save it inside the lab directory, and compare it with the generated public key. The derivation command will request the key passphrase.

### commands
umask 077; ssh-keygen -y -f /opt/lab-classroom/class21/class21_ed25519 > /opt/lab-classroom/class21/derived.pub
awk '{print $1, $2}' /opt/lab-classroom/class21/class21_ed25519.pub > /opt/lab-classroom/class21/original-core.pub
awk '{print $1, $2}' /opt/lab-classroom/class21/derived.pub > /opt/lab-classroom/class21/derived-core.pub
cmp /opt/lab-classroom/class21/original-core.pub /opt/lab-classroom/class21/derived-core.pub && printf '%s\n' 'MATCH: the public key belongs to the private key'
### step
5

### title
Create a restricted authorization fixture

### instructions
Create a sandbox authorization entry. The documentation-only source network 192.0.2.0/24 intentionally prevents this fixture from being useful on a typical real network. The restrict option disables several optional SSH features unless they are explicitly re-enabled.

### commands
printf 'from="192.0.2.0/24",restrict %s\n' "$(cat /opt/lab-classroom/class21/class21_ed25519.pub)" > /opt/lab-classroom/class21/authorized_keys
chmod 600 /opt/lab-classroom/class21/authorized_keys
cat /opt/lab-classroom/class21/authorized_keys
stat -c '%A %a %U:%G %n' /opt/lab-classroom/class21/authorized_keys
### step
6

### title
Build an inert daemon-hardening fixture

### instructions
Create a policy example for review. This file is not installed, included by the operating system, or applied to a running service. The AllowUsers account is illustrative and must be replaced with a verified local administrative account during a separately approved production change.

### commands
printf '%s\n' 'PubkeyAuthentication yes' 'PasswordAuthentication no' 'KbdInteractiveAuthentication no' 'PermitRootLogin no' 'AllowUsers labadmin' 'X11Forwarding no' 'AllowTcpForwarding no' > /opt/lab-classroom/class21/sshd_config
chmod 600 /opt/lab-classroom/class21/sshd_config
nl -ba /opt/lab-classroom/class21/sshd_config
### step
7

### title
Perform static policy checks

### instructions
Check that the expected directives appear exactly once and that no line enables password authentication. These checks inspect the fixture; they do not prove that a particular operating system accepts every directive.

### commands
grep -Ec '^PubkeyAuthentication yes$' /opt/lab-classroom/class21/sshd_config
grep -Ec '^PasswordAuthentication no$' /opt/lab-classroom/class21/sshd_config
grep -Ec '^KbdInteractiveAuthentication no$' /opt/lab-classroom/class21/sshd_config
grep -Ec '^PermitRootLogin no$' /opt/lab-classroom/class21/sshd_config
! grep -Eq '^PasswordAuthentication[[:space:]]+yes$' /opt/lab-classroom/class21/sshd_config
### step
8

### title
Optionally validate syntax without applying it

### instructions
If an OpenSSH server binary is already installed, use its test mode against only the sandbox file. This reads daemon defaults and host-key information but does not reload the service. A failure may reflect missing host keys, an unavailable account, unsupported directives, or distribution-specific behavior; it must not be bypassed.

### commands
if command -v sshd >/dev/null 2>&1; then sudo sshd -t -f /opt/lab-classroom/class21/sshd_config; elif [ -x /usr/sbin/sshd ]; then sudo /usr/sbin/sshd -t -f /opt/lab-classroom/class21/sshd_config; else printf '%s\n' 'SKIP: OpenSSH server binary is not installed'; fi

## Expected results

- The workspace resolves to /opt/lab-classroom/class21 and has mode 700.
- The key-generation operation creates class21_ed25519 and class21_ed25519.pub only inside the lab workspace.
- The private key reports mode 600, while the public key may report mode 600 because it was created under a restrictive umask.
- The public key is identified as ED25519 and has a stable SHA256 fingerprint.
- The comparison prints MATCH: the public key belongs to the private key.
- The sandbox authorized_keys file begins with from="192.0.2.0/24",restrict and contains the generated public key.
- The policy fixture disables password authentication, keyboard-interactive authentication, direct root login, X11 forwarding, and TCP forwarding.
- Each static grep count prints 1, and the negative password-authentication check exits successfully.
- Optional daemon syntax validation either exits successfully, reports a diagnostic that requires investigation, or explicitly reports that the server binary is unavailable.

## Verification checkpoints

- [ ] Run test "$(realpath /opt/lab-classroom/class21)" = /opt/lab-classroom/class21 and confirm an exit status of zero.
- [ ] Run test "$(stat -c %a /opt/lab-classroom/class21)" = 700 and confirm an exit status of zero.
- [ ] Run test "$(stat -c %a /opt/lab-classroom/class21/class21_ed25519)" = 600 and confirm an exit status of zero.
- [ ] Run ssh-keygen -lf /opt/lab-classroom/class21/class21_ed25519.pub and confirm that the output identifies ED25519.
- [ ] Run cmp /opt/lab-classroom/class21/original-core.pub /opt/lab-classroom/class21/derived-core.pub and confirm an exit status of zero.
- [ ] Run grep -Eq '^from="192\.0\.2\.0/24",restrict ssh-ed25519 ' /opt/lab-classroom/class21/authorized_keys and confirm an exit status of zero.
- [ ] Run test "$(stat -c %a /opt/lab-classroom/class21/authorized_keys)" = 600 and confirm an exit status of zero.
- [ ] Run grep -Eq '^PasswordAuthentication no$' /opt/lab-classroom/class21/sshd_config and confirm an exit status of zero.
- [ ] Run grep -Eq '^PermitRootLogin no$' /opt/lab-classroom/class21/sshd_config and confirm an exit status of zero.
- [ ] Run find /opt/lab-classroom/class21 -xdev -type f -printf '%m %p\n' and review every generated file before declaring the lab complete.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| ssh-keygen is not found. | The OpenSSH client package is not installed or the executable is outside the current PATH. | Stop the lab and ask the platform administrator to install the distribution's OpenSSH client package through the approved software-management process. Do not download and execute an unreviewed installer. |
| The class directory cannot be created. | The current account lacks sudo authorization, /opt is read-only, or a parent filesystem policy blocks creation. | Verify authorization and mount policy with the system owner. Do not redirect the exercise to a production SSH directory. |
| The private-key permission is not 600. | The key was created with a permissive mask or its mode was changed afterward. | Run chmod 600 /opt/lab-classroom/class21/class21_ed25519, recheck with stat, and investigate any process that changed the mode. |
| ssh-keygen -y reports an incorrect passphrase. | The entered passphrase does not match the private key or the wrong private-key path was supplied. | Confirm the exact lab path and retry carefully. If the training passphrase is lost, delete only the individual training key files after confirming their paths and generate a new lab key. |
| The derived and original public keys do not match. | One file came from a different private key, the public-key body was modified, or the comparison included inconsistent comments. | Compare the two-field key type and encoded body as shown in the lab. Regenerate the training pair if provenance cannot be established. |
| The optional daemon test reports no host keys available. | The OpenSSH server package is incomplete, server host keys have not been provisioned, or the validator is applying system defaults. | Treat the result as a failed validation rather than ignoring it. Because the fixture is inert, continue with static review and escalate host-key provisioning to the server owner. |
| The optional daemon test reports an unsupported directive. | The installed OpenSSH version or vendor build uses different directives or lacks the feature. | Consult the manual installed on that host and adapt a copy of the sandbox fixture. Never apply a directive that the target daemon cannot validate. |
| A production SSH login fails after a separate hardening change. | The key was not authorized for the target account, account restrictions are wrong, the source restriction does not match, permissions are invalid, or all fallback methods were disabled too early. | Keep the original session open, inspect authentication logs from that session, restore the last known-good production policy through the approved console or change process, validate it, and only then retry. |

## Security considerations

### key_protection
Never share or upload the private-key file.
Use a strong, unique passphrase and an approved agent with explicit lifetime or confirmation controls where available.
Use separate identities for unrelated environments and administrative roles.
Remove obsolete public keys promptly and inventory fingerprints rather than relying on comments.
Back up private keys only through an approved encrypted secret-storage process.

### server_hardening_sequence
Confirm console or out-of-band recovery before changing remote access.
Create or verify a named non-root administrative account.
Install the intended public key with correct ownership and restrictive permissions.
Test a second independent session using that exact identity and IdentitiesOnly.
Review effective daemon configuration, includes, Match blocks, PAM behavior, and vendor defaults.
Validate syntax before activation.
Keep the existing session open during a controlled reload and test again before closing it.
Disable passwords and other fallback methods only after key-based access is proven.
Monitor authentication logs and document the recovery path.

### cautions
The 192.0.2.0/24 source restriction is from a documentation-only network and is intentionally unsuitable for normal deployment.
The restrict option can disable forwarding, agent forwarding, X11 forwarding, PTY allocation, and user startup commands depending on OpenSSH behavior. Confirm application requirements before using it.
Disabling TCP forwarding can break jump-host workflows, remote development tools, and application tunnels.
Disabling PTY allocation on an administrative key can prevent interactive shell workflows.
Changing the SSH listening port does not replace authentication, authorization, patching, monitoring, or network controls.
A successful syntax test does not prove that an account, key, network path, or recovery mechanism works.

## Rollback

### lab_effect
The lab creates only an isolated directory, a training key pair, comparison files, an authorization fixture, and a daemon-policy fixture. It does not activate any SSH setting.

### preserve_for_review
Before cleanup, record the public-key fingerprint and copy any required non-secret notes into the class record. Do not place the private key in reports or tickets.

### cleanup_commands
test "$(realpath /opt/lab-classroom/class21)" = /opt/lab-classroom/class21
find /opt/lab-classroom/class21 -xdev -mindepth 1 -maxdepth 1 -type f -print
find /opt/lab-classroom/class21 -xdev -mindepth 1 -maxdepth 1 -type f -delete

### cleanup_warning
Run the path test and review the printed file list before deletion. Cleanup permanently destroys the training private key and all class fixtures.

### production_guidance
For a real service change, restore the previously validated configuration through the approved change mechanism, validate that restored configuration, perform a controlled reload, and verify access from a second session. Use console or out-of-band recovery if no working SSH session remains.

## Video narration notes

Begin by showing the isolated path and emphasizing that the class will not touch the running SSH service. Introduce the key pair as two mathematically related objects with different handling requirements: the private key remains with the client, while the public key can be installed on a server. Generate the Ed25519 training identity and pause at the passphrase prompt to explain that the passphrase encrypts the private-key file at rest. It is not an account password and is not sent to the server.

Display the file modes and fingerprint. Point out that comments are convenient labels, while fingerprints are better identifiers. Derive the public key from the private key and compare only the key type and encoded body, because comments can differ without changing the cryptographic key.

Next, create the sandbox authorized_keys entry. Explain that the documentation-only source network makes this an inert teaching example. Discuss restrict as a convenient baseline for limiting forwarding, PTY allocation, and other optional capabilities, but warn that service and administration requirements must be understood first.

Review the daemon-policy fixture line by line. Public-key authentication remains enabled; password and keyboard-interactive methods are disabled; direct root login is denied; access is limited to a named account; and forwarding features are disabled. Emphasize that these choices can break legitimate workflows and must not be copied without testing. Demonstrate static checks and, where available, test mode against the sandbox file. Make clear that no service is reloaded.

Close with the safe production sequence: verify recovery access, authorize the key, test a second session with the intended identity, inspect effective settings and logs, validate syntax, reload in a controlled manner, test again, and only then close the original session. Reinforce that host-key verification protects the client from an impostor server and is not replaced by strong user authentication.

## References

- OpenBSD manual: ssh(1), https://man.openbsd.org/ssh
- OpenBSD manual: ssh-keygen(1), https://man.openbsd.org/ssh-keygen
- OpenBSD manual: sshd(8), https://man.openbsd.org/sshd
- OpenBSD manual: sshd_config(5), https://man.openbsd.org/sshd_config
- OpenBSD manual: authorized_keys(5), https://man.openbsd.org/authorized_keys
- IETF RFC 4252, The Secure Shell Authentication Protocol, https://www.rfc-editor.org/rfc/rfc4252
- IETF RFC 8709, Ed25519 and Ed448 Public Key Algorithms for the Secure Shell Protocol, https://www.rfc-editor.org/rfc/rfc8709
- IETF RFC 5737, IPv4 Address Blocks Reserved for Documentation, https://www.rfc-editor.org/rfc/rfc5737

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

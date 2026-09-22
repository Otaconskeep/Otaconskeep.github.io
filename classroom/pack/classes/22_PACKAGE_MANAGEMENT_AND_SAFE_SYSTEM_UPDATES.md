# Class 22 — Package Management and Safe System Updates

**Learning objective:** Explain the difference between a package repository, package metadata, dependency resolver, transaction engine, installed-package database, and running services.; Create a normalized two-column inventory of installed package names and versions.; Inspect repository and candidate-version information without performing a package transaction.; Simulate an update transaction and preserve standard output, standard error, and command status for review.; Contrast APT upgrade with APT dist-upgrade or full-upgrade resolver behavior.; Recognize removals, held packages, dependency conflicts, kernel changes, and service-impacting packages as maintenance review triggers.; Create a planning-only batch report that groups simulated package actions without applying them.; Generate and verify SHA-256 checksums for the lab evidence.; Describe rollback as a preplanned recovery process rather than an automatic package-manager feature.
**Bloom level:** Understand / Apply
**Track:** Linux Systems Administration · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Teach administrators how Linux package managers establish trust, resolve dependencies, preview transactions, identify risky changes, create a maintenance plan, and preserve auditable evidence before any real system update is approved.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-20
**Compatibility:** ### supported_families
Debian and Ubuntu systems using dpkg, APT, and apt-get
Fedora, Rocky Linux, AlmaLinux, and RHEL-compatible systems using RPM with DNF
Older RPM-family systems using YUM cache-only mode
Alpine Linux systems using APK

### shell_requirements
A POSIX-like shell for normal collection steps
Bash for the null-delimited checksum loop with process substitution
GNU or compatible find, sort, sed, awk, and sha256sum utilities

### behavior_notes
APT receives two simulations so conservative upgrade behavior can be contrasted with dist-upgrade or full-upgrade behavior.
DNF and YUM use cached metadata and --assumeno; missing cache is retained as an error rather than triggering a metadata refresh.
APK uses --simulate and does not provide the same APT upgrade-versus-dist-upgrade comparison.
Simulation behavior can vary by package-manager version and local policy.
The lab does not support language-specific package managers such as npm, pip, gem, or cargo as substitutes for the operating-system package manager.

## Learning objective

- Explain the difference between a package repository, package metadata, dependency resolver, transaction engine, installed-package database, and running services.
- Create a normalized two-column inventory of installed package names and versions.
- Inspect repository and candidate-version information without performing a package transaction.
- Simulate an update transaction and preserve standard output, standard error, and command status for review.
- Contrast APT upgrade with APT dist-upgrade or full-upgrade resolver behavior.
- Recognize removals, held packages, dependency conflicts, kernel changes, and service-impacting packages as maintenance review triggers.
- Create a planning-only batch report that groups simulated package actions without applying them.
- Generate and verify SHA-256 checksums for the lab evidence.
- Describe rollback as a preplanned recovery process rather than an automatic package-manager feature.

## Why this matters

Teach administrators how Linux package managers establish trust, resolve dependencies, preview transactions, identify risky changes, create a maintenance plan, and preserve auditable evidence before any real system update is approved.

## Prerequisites

- Comfort using a Linux shell and reading command output
- Basic understanding of files, directories, processes, services, and repositories
- A Debian, Ubuntu, Fedora, Rocky Linux, AlmaLinux, RHEL-compatible, or Alpine Linux host
- Permission to create /opt/lab-classroom/class22/
- At least one supported package manager: APT, DNF, YUM, or APK
- No real package installation, removal, or upgrade is required

## Required reading

- Debian Administrator's Handbook, Package Management: https://www.debian.org/doc/manuals/debian-handbook/apt.en.html
- APT apt-get manual page, especially --simulate, upgrade, and dist-upgrade: https://manpages.debian.org/apt-get
- DNF command reference, including --assumeno and --cacheonly: https://dnf.readthedocs.io/en/latest/command_ref.html
- Alpine Linux apk handbook: https://docs.alpinelinux.org/user-handbook/0.1a/Working/apk.html
- systemd systemctl manual page for understanding later service validation: https://www.freedesktop.org/software/systemd/man/latest/systemctl.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| package | A versioned archive containing software, metadata, dependencies, and installation instructions managed by the operating system. |
| repository | A configured source of packages and signed metadata from which a package manager discovers available versions. |
| package metadata | Information such as package names, versions, dependencies, conflicts, checksums, signatures, and repository origin. |
| dependency resolver | The component that calculates which packages must be installed, upgraded, retained, or removed to satisfy dependency rules. |
| transaction | A planned set of package operations treated as one package-manager action. |
| simulation | A package-manager mode that calculates and displays a proposed transaction without intentionally applying package changes. |
| candidate version | The package version currently preferred by repository priority, pinning, architecture, and dependency policy. |
| hold or version lock | A policy preventing a selected package from being automatically changed. |
| package database | The local authoritative record of packages and versions installed through the package manager. |
| conffile | A configuration file tracked specially by a package manager so local administrator changes can be preserved or reviewed. |
| full upgrade | A resolver mode allowed to add or remove packages when necessary to complete a system upgrade; APT also calls this dist-upgrade behavior. |
| rollback | A tested recovery procedure using snapshots, backups, known package versions, configuration restoration, or host replacement. |

## Instruction

Safe updating is a change-management exercise, not merely a command. A package manager first reads configured repositories and their trust metadata, compares available packages with the local installed-package database, resolves dependency rules, and proposes a transaction. Only after approval should a transaction engine modify package files, scripts, boot artifacts, or service state. Repository signatures authenticate metadata or packages, but they do not prove that an update is operationally compatible with a particular homelab workload.

Inventory is the first control. Record installed package names and versions in a stable format so an administrator can compare the system before and after maintenance. The lab uses two tab-separated fields: package name and installed version. Package families expose this data differently, so blindly assuming every command emits the same format produces unreliable evidence. RPM inventory avoids optional query tags that are absent on older RPM releases, while Alpine inventory is parsed from its local package database because apk info -vv is not a dependable name-and-version TSV interface.

The second control is transaction preview. On APT systems, apt-get --simulate upgrade uses a conservative resolver: installed packages are upgraded when that can be done without removing installed packages. apt-get --simulate dist-upgrade, also known conceptually as a full upgrade, allows dependency resolution that may install additional packages or remove packages. The two previews must therefore be reviewed separately. A removal appearing only in the dist-upgrade plan is not automatically wrong, but it demands an explanation. Kernel, bootloader, libc, database, container runtime, remote-access, storage, and hypervisor packages also deserve explicit maintenance planning because their effects can extend beyond the package transaction.

Simulation output is evidence only when its exit status and errors are retained. An empty-looking plan caused by a package database lock, insufficient privilege, corrupt metadata, or unavailable cache must not be reported as a successful no-op. This lab captures both output streams and records return codes. It does not advise elevating privileges merely to make a preview work; investigate the lock owner or use an approved maintenance window instead.

Batching in this lesson is planning-only. The generated batch plan classifies proposed APT actions into boot or kernel, core libraries, service-impacting packages, and applications or other packages. It does not apply any batch. On a production system, actual grouping must account for dependency constraints, supported intermediate states, redundancy, reboot requirements, snapshots, backups, console access, health checks, and application-owner approval.

Package managers are not universal rollback systems. Downgrades can fail when repositories no longer contain old versions, maintainer scripts are not reversible, databases have migrated, or configuration formats have changed. A safe update plan therefore defines recovery before execution: verify backups, identify a snapshot boundary, preserve configuration, confirm out-of-band access, record package state, establish service checks, and define stop conditions. The final artifacts are checksummed so accidental changes to the review evidence can be detected.

## Architecture

### flow
repository trust -> metadata and policy -> dependency resolver -> proposed transaction -> package database and filesystem transaction -> runtime validation -> recovery decision

### layers
### order
1

### name
Repository trust

### role
Defines which signing keys, repository URLs, release channels, and package origins are accepted.

### review_questions
Is the repository expected and supported?
Is signature validation enabled?
Has a third-party repository changed priority or release channel?
### order
2

### name
Metadata and candidate policy

### role
Describes available versions and selects candidates according to architecture, repository priority, pinning, exclusions, and version locks.

### review_questions
Which repository provides the candidate?
Is a package held, pinned, excluded, or unavailable?
Is cached metadata current enough for the intended decision?
### order
3

### name
Dependency resolver

### role
Calculates a consistent set of installs, upgrades, retained packages, and permitted removals.

### review_questions
Does the conservative plan differ from the full resolver plan?
Are removals or replacements expected?
Are dependency conflicts or broken packages reported?
### order
4

### name
Transaction engine

### role
Downloads, verifies, unpacks, configures, and runs package scripts during a real approved transaction.

### review_questions
Is adequate storage available?
Could package scripts restart services or rebuild boot files?
Is interruption recovery documented?
### order
5

### name
Installed-package database and managed files

### role
Records installed versions and tracks package-owned files, dependencies, and selected configuration state.

### review_questions
Was a pre-change inventory captured?
Are configuration-file decisions understood?
Can the database be repaired if a transaction is interrupted?
### order
6

### name
Runtime services and workloads

### role
Represents the actual processes, network listeners, containers, applications, and booted kernel that must be validated after a future update.

### review_questions
Which services may restart?
Which application checks prove health?
Is a reboot required before the new kernel or libraries are fully active?
### order
7

### name
Recovery

### role
Provides a tested path to restore service through snapshots, backups, package-version recovery, configuration restoration, failover, or rebuild.

### review_questions
What is the stop condition?
Who decides to recover?
Has restoration been tested independently of the update?

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Choose one service on the host and write five service-specific health checks that would be performed after a future approved update.
Review upgrade-simulation.txt and list every kernel, bootloader, core library, database, container, virtualization, storage, authentication, or network-service package that deserves a maintenance note.
If the host uses APT, compare the Inst, Remv, and kept-back behavior between the conservative and full resolver sections. Explain every difference without applying either transaction.
Write a one-page recovery decision tree covering continue, pause, investigate, reboot, restore snapshot, restore backup, and rebuild.
Document how repository signing keys and third-party repositories are managed on the host without changing them.
Propose maintenance batches based on workload impact and dependencies, and clearly label the proposal as planning-only.

## Feynman teach-back

### prompt
Explain safe package updating to a new homelab operator without using the words easy, just, or automatic.

### model_explanation
A package manager is like a planner and a construction crew. Repository metadata is the catalog, signatures help confirm who published the catalog, and the installed-package database records what is already in the building. The resolver creates a proposed work order. A conservative APT upgrade avoids a plan that must remove installed packages, while a full or dist-upgrade resolver may allow removals or additions to solve dependencies. A simulation lets us inspect that work order without authorizing construction. We save its errors and status because a locked door is not the same as an empty work order. Before real work, we identify affected services, prepare tests, verify recovery, and decide when to stop. A package manager can install software, but it cannot promise that an application remains healthy or that every change can be reversed.

### self_check_questions
Can you explain why a valid signature does not guarantee application compatibility?
Can you explain why a lock error must not be interpreted as zero available updates?
Can you explain why APT upgrade and dist-upgrade may produce different plans?
Can you describe a recovery method that does not depend on package downgrade?

## Retrieval check

1. 1. What is the main purpose of a package-manager simulation?
2. 2. On an APT system, what resolver behavior distinguishes upgrade from dist-upgrade or full-upgrade?
3. 3. Why must simulation standard error and exit status be preserved?
4. 4. Name four categories of package changes that should trigger additional maintenance review.
5. 5. Does a successful repository signature prove that an update is compatible with a homelab application? Explain.
6. 6. Why is package downgrade alone an insufficient rollback strategy?
7. 7. What should an operator do when a simulation cannot acquire the dpkg lock or reports that privileges are required?
8. 8. What does the batch-plan artifact do, and what does it explicitly not do?

## Guided lab

### name
Build and review a read-only package update plan

### scope_rule
Commands may read operating-system package state, but every artifact created or changed by the lab must remain under /opt/lab-classroom/class22/. No package transaction is applied.

### steps
### step
1

### title
Create the isolated workspace

### commands
ROOT=/opt/lab-classroom/class22
mkdir -p "$ROOT"
printf 'class_id=22\nworkspace=%s\ncreated_utc=%s\n' "$ROOT" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$ROOT/lab-metadata.txt"

### notes
If permission to create the directory is unavailable, stop and ask the lab administrator to provision it. Do not redirect output elsewhere.
### step
2

### title
Create a normalized package inventory

### commands
ROOT=/opt/lab-classroom/class22
if command -v dpkg-query >/dev/null 2>&1; then dpkg-query -W -f='${binary:Package}\t${Version}\n' | LC_ALL=C sort; elif command -v rpm >/dev/null 2>&1; then rpm -qa --qf '%{NAME}\t%{VERSION}-%{RELEASE}\n' | LC_ALL=C sort; elif command -v apk >/dev/null 2>&1 && test -r /lib/apk/db/installed; then awk -F: '$1=="P"{p=$2} $1=="V"{print p "\t" $2}' /lib/apk/db/installed | LC_ALL=C sort; else printf 'unsupported\tno-supported-package-database\n'; fi > "$ROOT/package-inventory.tsv"
printf 'installed_package_records\t%s\n' "$(wc -l < "$ROOT/package-inventory.tsv")" > "$ROOT/package-count.txt"

### notes
The inventory contains exactly two logical fields per record: package name and installed version. The RPM query intentionally avoids EPOCHNUM for compatibility with older RPM implementations. The Alpine parser avoids treating apk info -vv as TSV.
### step
3

### title
Capture repository and candidate policy

### commands
ROOT=/opt/lab-classroom/class22
if command -v apt-cache >/dev/null 2>&1; then { printf '%s\n' 'PACKAGE_FAMILY=apt' '=== apt-cache policy ==='; apt-cache policy; }; elif command -v dnf >/dev/null 2>&1; then { printf '%s\n' 'PACKAGE_FAMILY=dnf' '=== enabled repositories ==='; dnf --cacheonly repolist; printf '%s\n' '=== installed packages ==='; dnf --cacheonly list installed; }; elif command -v yum >/dev/null 2>&1; then { printf '%s\n' 'PACKAGE_FAMILY=yum' '=== enabled repositories ==='; yum -C repolist; printf '%s\n' '=== installed packages ==='; yum -C list installed; }; elif command -v apk >/dev/null 2>&1; then { printf '%s\n' 'PACKAGE_FAMILY=apk' '=== configured repositories ==='; cat /etc/apk/repositories 2>&1; printf '%s\n' '=== apk policy ==='; apk policy 2>&1; }; else printf '%s\n' 'PACKAGE_FAMILY=unsupported'; fi > "$ROOT/package-policy.txt" 2>&1

### notes
Cache-only options prevent DNF or YUM from refreshing metadata during this evidence collection. Existing cache age must be considered when interpreting results.
### step
4

### title
Simulate update resolver behavior and retain errors

### commands
ROOT=/opt/lab-classroom/class22
if command -v apt-get >/dev/null 2>&1; then { printf '%s\n' 'PACKAGE_FAMILY=apt' '=== conservative resolver: apt-get --simulate upgrade ==='; apt-get --simulate upgrade; conservative_rc=$?; printf 'CONSERVATIVE_EXIT_STATUS=%s\n' "$conservative_rc"; printf '%s\n' '=== full resolver: apt-get --simulate dist-upgrade ==='; apt-get --simulate dist-upgrade; full_rc=$?; printf 'FULL_UPGRADE_EXIT_STATUS=%s\n' "$full_rc"; printf '%s\n' 'REVIEW_NOTE=upgrade refuses dependency solutions that require removing installed packages; dist-upgrade may add or remove packages to complete dependency resolution.'; } > "$ROOT/upgrade-simulation.txt" 2>&1; elif command -v dnf >/dev/null 2>&1; then { printf '%s\n' 'PACKAGE_FAMILY=dnf' '=== non-applying cached upgrade proposal ==='; dnf --cacheonly --assumeno upgrade; rc=$?; printf 'SIMULATION_EXIT_STATUS=%s\n' "$rc"; printf '%s\n' 'REVIEW_NOTE=DNF does not provide the same upgrade versus dist-upgrade pair used by APT; review every proposed install, upgrade, replacement, and removal.'; } > "$ROOT/upgrade-simulation.txt" 2>&1; elif command -v yum >/dev/null 2>&1; then { printf '%s\n' 'PACKAGE_FAMILY=yum' '=== non-applying cached update proposal ==='; yum -C --assumeno update; rc=$?; printf 'SIMULATION_EXIT_STATUS=%s\n' "$rc"; } > "$ROOT/upgrade-simulation.txt" 2>&1; elif command -v apk >/dev/null 2>&1; then { printf '%s\n' 'PACKAGE_FAMILY=apk' '=== simulated upgrade ==='; apk upgrade --simulate; rc=$?; printf 'SIMULATION_EXIT_STATUS=%s\n' "$rc"; } > "$ROOT/upgrade-simulation.txt" 2>&1; else printf '%s\n' 'PACKAGE_FAMILY=unsupported' 'SIMULATION_EXIT_STATUS=127' > "$ROOT/upgrade-simulation.txt"; fi

### notes
Do not use privilege elevation to force the preview. Both standard output and standard error are captured. A nonzero status, lock error, privilege error, or metadata error means the plan was not successfully produced. On APT, compare the conservative and full resolver sections explicitly.
### step
5

### title
Create a planning-only batch report

### commands
ROOT=/opt/lab-classroom/class22
awk 'BEGIN{print "PLANNING_ONLY: no packages are changed by this report"; print "batch\tpackage\tsimulated_action"; n=0} /^Inst /{p=$2; a="upgrade-or-install"; if(p ~ /^(linux-|grub|shim|systemd-boot|kernel)/) b="1-boot-kernel"; else if(p ~ /^(libc|glibc|musl|openssl|libssl|dpkg|apt|rpm|dnf|apk|systemd)/) b="2-core-platform"; else if(p ~ /^(openssh|nginx|apache|httpd|postgresql|mysql|mariadb|docker|containerd|podman|libvirt|qemu)/) b="3-services"; else b="4-applications-other"; print b "\t" p "\t" a; n++} /^Remv /{print "REVIEW-REMOVAL\t" $2 "\tremove"; n++} END{if(n==0) print "none\tno-parsed-apt-actions\treview-raw-simulation"}' "$ROOT/upgrade-simulation.txt" > "$ROOT/update-batch-plan.tsv"

### notes
This parser recognizes common APT simulation lines. Other package families will receive a review marker and must be grouped manually from the raw simulation. The report is not an instruction to apply these groups independently; dependency constraints and supported intermediate states must be reviewed first.
### step
6

### title
Write the maintenance review checklist

### commands
ROOT=/opt/lab-classroom/class22
printf '%s\n' 'SAFE UPDATE REVIEW CHECKLIST' '[ ] Simulation completed with a reviewed zero or documented package-manager status.' '[ ] Standard error was reviewed; an empty plan was not inferred from a lock or privilege failure.' '[ ] APT upgrade and dist-upgrade outputs were compared when APT is present.' '[ ] Every proposed removal or replacement has an explanation.' '[ ] Held, pinned, excluded, or retained packages were reviewed.' '[ ] Kernel, bootloader, core library, storage, remote-access, database, virtualization, and container changes were identified.' '[ ] Configuration-file prompts and package script effects were considered.' '[ ] Sufficient disk space and package cache space will be checked before a real transaction.' '[ ] Backups or snapshots were verified by an appropriate restore test.' '[ ] Console or out-of-band access is available if network service is disrupted.' '[ ] Application health checks, service checks, and reboot validation are defined.' '[ ] Stop conditions, maintenance owner, approval, and recovery decision authority are documented.' '[ ] This lab did not apply any package changes.' > "$ROOT/maintenance-checklist.txt"

### notes
The checklist is evidence for a future maintenance decision, not proof that the host is ready to update.
### step
7

### title
Declare artifact paths and assert workspace confinement

### commands
ROOT=/opt/lab-classroom/class22
printf '%s\n' "$ROOT/lab-metadata.txt" "$ROOT/package-inventory.tsv" "$ROOT/package-count.txt" "$ROOT/package-policy.txt" "$ROOT/upgrade-simulation.txt" "$ROOT/update-batch-plan.tsv" "$ROOT/maintenance-checklist.txt" "$ROOT/artifact-paths.txt" "$ROOT/SHA256SUMS" "$ROOT/hash-verification.txt" > "$ROOT/artifact-paths.txt"
path_rc=0; while IFS= read -r p; do case "$p" in /opt/lab-classroom/class22/*) : ;; *) printf 'OUTSIDE_WORKSPACE=%s\n' "$p"; path_rc=1 ;; esac; done < "$ROOT/artifact-paths.txt"; printf 'PATH_ASSERTION_EXIT_STATUS=%s\n' "$path_rc" >> "$ROOT/lab-metadata.txt"; test "$path_rc" -eq 0

### notes
The assertion checks every declared artifact path. The supplied lab commands contain no output redirection to any other location.
### step
8

### title
Hash the evidence safely and verify it

### commands
ROOT=/opt/lab-classroom/class22
bash -c 'ROOT=/opt/lab-classroom/class22; : > "$ROOT/SHA256SUMS"; while IFS= read -r -d "" f; do sha256sum "$f" >> "$ROOT/SHA256SUMS"; done < <(find "$ROOT" -maxdepth 1 -type f ! -name SHA256SUMS ! -name hash-verification.txt -print0 | sort -z)'
sha256sum -c "$ROOT/SHA256SUMS" > "$ROOT/hash-verification.txt" 2>&1

### notes
The null-delimited loop invokes sha256sum once per discovered file and remains safe if the report set is empty or partial. SHA256SUMS and hash-verification.txt are excluded to avoid self-referential checksums.
### step
9

### title
Review rather than apply

### commands
ROOT=/opt/lab-classroom/class22
sed -n '1,240p' "$ROOT/upgrade-simulation.txt"
sed -n '1,240p' "$ROOT/update-batch-plan.tsv"
cat "$ROOT/maintenance-checklist.txt"
cat "$ROOT/hash-verification.txt"

### notes
Stop after review. Do not transform a simulated command into a real upgrade as part of this class.

## Expected results

- /opt/lab-classroom/class22/package-inventory.tsv exists, is non-empty, and contains normalized package-name and installed-version records.
- /opt/lab-classroom/class22/package-count.txt exists, is non-empty, and records the number of inventory rows.
- /opt/lab-classroom/class22/package-policy.txt exists, is non-empty, and identifies the detected package family plus repository or policy information.
- /opt/lab-classroom/class22/upgrade-simulation.txt exists, is non-empty, includes captured errors, and records one or more simulation exit statuses.
- On an APT host, upgrade-simulation.txt contains both the conservative upgrade simulation and the dist-upgrade simulation, together with an explicit explanation of their resolver difference.
- /opt/lab-classroom/class22/update-batch-plan.tsv exists and contains planning-only categories or a marker directing the administrator to review the raw simulation.
- /opt/lab-classroom/class22/maintenance-checklist.txt exists, is non-empty, and contains pre-update, validation, and recovery review items.
- /opt/lab-classroom/class22/artifact-paths.txt declares only paths beneath /opt/lab-classroom/class22/.
- /opt/lab-classroom/class22/SHA256SUMS exists and is non-empty after report generation.
- /opt/lab-classroom/class22/hash-verification.txt exists, is non-empty, and reports successful verification unless an artifact changed after hashing.
- No package is installed, upgraded, downgraded, or removed by the lab.

## Verification checkpoints

- [ ] ROOT=/opt/lab-classroom/class22; test -s "$ROOT/package-inventory.tsv" && echo 'PASS: package-inventory.tsv exists and is non-empty' || echo 'FAIL: package-inventory.tsv missing or empty'
- [ ] ROOT=/opt/lab-classroom/class22; test -s "$ROOT/package-count.txt" && grep -Eq '^installed_package_records[[:space:]]+[0-9]+$' "$ROOT/package-count.txt" && echo 'PASS: package-count.txt exists, is non-empty, and has a numeric count' || echo 'FAIL: package-count.txt is missing or malformed'
- [ ] ROOT=/opt/lab-classroom/class22; test -s "$ROOT/package-policy.txt" && grep -q '^PACKAGE_FAMILY=' "$ROOT/package-policy.txt" && echo 'PASS: package-policy.txt exists, is non-empty, and identifies a package family' || echo 'FAIL: package-policy.txt is missing or malformed'
- [ ] ROOT=/opt/lab-classroom/class22; test -s "$ROOT/upgrade-simulation.txt" && grep -Eq '(CONSERVATIVE_EXIT_STATUS|FULL_UPGRADE_EXIT_STATUS|SIMULATION_EXIT_STATUS)=' "$ROOT/upgrade-simulation.txt" && echo 'PASS: upgrade-simulation.txt exists and records command status' || echo 'FAIL: upgrade-simulation.txt is missing or lacks status evidence'
- [ ] ROOT=/opt/lab-classroom/class22; if grep -q '^PACKAGE_FAMILY=apt$' "$ROOT/upgrade-simulation.txt"; then grep -q 'conservative resolver' "$ROOT/upgrade-simulation.txt" && grep -q 'full resolver' "$ROOT/upgrade-simulation.txt" && grep -q 'dist-upgrade may add or remove packages' "$ROOT/upgrade-simulation.txt" && echo 'PASS: both APT resolver modes and their contrast are documented' || echo 'FAIL: APT resolver comparison is incomplete'; else echo 'PASS: APT-specific resolver comparison is not applicable'; fi
- [ ] ROOT=/opt/lab-classroom/class22; test -s "$ROOT/update-batch-plan.tsv" && grep -q '^PLANNING_ONLY:' "$ROOT/update-batch-plan.tsv" && echo 'PASS: planning-only batch report exists' || echo 'FAIL: update-batch-plan.tsv is missing or malformed'
- [ ] ROOT=/opt/lab-classroom/class22; test -s "$ROOT/maintenance-checklist.txt" && grep -q 'SAFE UPDATE REVIEW CHECKLIST' "$ROOT/maintenance-checklist.txt" && echo 'PASS: maintenance-checklist.txt exists and is non-empty' || echo 'FAIL: maintenance-checklist.txt is missing or malformed'
- [ ] ROOT=/opt/lab-classroom/class22; test -s "$ROOT/SHA256SUMS" && echo 'PASS: SHA256SUMS exists and is non-empty' || echo 'FAIL: SHA256SUMS missing or empty'
- [ ] ROOT=/opt/lab-classroom/class22; test -s "$ROOT/hash-verification.txt" && ! grep -q ': FAILED' "$ROOT/hash-verification.txt" && grep -q ': OK' "$ROOT/hash-verification.txt" && echo 'PASS: hash-verification.txt exists and reports successful checks' || echo 'FAIL: hash verification is missing, empty, or reports failure'
- [ ] ROOT=/opt/lab-classroom/class22; path_rc=0; test -s "$ROOT/artifact-paths.txt" || path_rc=1; while IFS= read -r p; do case "$p" in "$ROOT"/*) test -e "$p" || path_rc=1 ;; *) path_rc=1 ;; esac; done < "$ROOT/artifact-paths.txt"; test "$path_rc" -eq 0 && echo 'PASS: every declared artifact exists at the required same-path workspace' || echo 'FAIL: a declared artifact is absent or outside /opt/lab-classroom/class22/'
- [ ] ROOT=/opt/lab-classroom/class22; test -s "$ROOT/package-inventory.tsv" && test -s "$ROOT/package-count.txt" && test -s "$ROOT/package-policy.txt" && test -s "$ROOT/upgrade-simulation.txt" && test -s "$ROOT/maintenance-checklist.txt" && test -s "$ROOT/SHA256SUMS" && test -s "$ROOT/hash-verification.txt" && echo 'PASS: all required non-empty artifacts are present' || echo 'FAIL: one or more required artifacts are missing or empty'

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| mkdir reports permission denied for /opt/lab-classroom/class22/. | The student account is not allowed to create directories under /opt. | Stop the lab and ask the lab administrator to pre-create /opt/lab-classroom/class22/ with suitable ownership. Do not redirect artifacts to another directory because the mutation boundary is mandatory. |
| upgrade-simulation.txt reports that the dpkg or APT lock cannot be acquired, reports insufficient privilege, or contains no usable transaction plan. | Another package process owns the lock, the local APT configuration requires privileges even for this operation, or the simulation failed before dependency resolution. | Keep the captured error and recorded nonzero status in upgrade-simulation.txt. Do not elevate and do not treat the result as an empty successful upgrade plan. Identify the legitimate lock owner with read-only process inspection, wait for approved package activity to finish, or repeat the lab during an authorized window. |
| DNF or YUM reports that cached metadata is unavailable. | The lab uses cache-only mode to avoid changing package caches, and the host has no suitable cached repository metadata. | Retain the error and exit status as evidence. Arrange a separately approved metadata-refresh activity outside this lab, then rerun the read-only collection. Do not remove --cacheonly merely to make the output look successful. |
| The conservative APT simulation succeeds, but dist-upgrade proposes removals. | The full resolver found a dependency solution requiring replacement or removal of installed packages. | Review every Remv line, package relationship, repository origin, and replacement package. Do not apply the transaction until each removal is explained and recovery is prepared. |
| package-inventory.tsv contains an unsupported marker. | No supported local package database command or Alpine database was detected. | Confirm that the host uses APT, RPM, or APK and that its local package database is readable. Do not invent inventory data or substitute a software-language package manager. |
| update-batch-plan.tsv contains no-parsed-apt-actions. | The host is not using APT, the APT plan has no Inst or Remv lines, or the simulation failed. | Review upgrade-simulation.txt and its exit statuses first. If another package family is in use, manually classify its proposal while preserving the planning-only rule. |
| sha256sum verification reports FAILED. | A report changed, was deleted, or was replaced after SHA256SUMS was created. | Determine whether the change was expected. If evidence collection was intentionally repeated, regenerate SHA256SUMS and hash-verification.txt using Step 8; otherwise preserve the mismatch for investigation. |
| The path assertion fails. | artifact-paths.txt was edited to include an absent file or a path outside the required workspace. | Do not create the artifact elsewhere. Correct the lab workflow so every declared artifact is created under /opt/lab-classroom/class22/, regenerate the path manifest, and repeat hashing. |
| A simulation lists held-back or retained packages. | A conservative resolver cannot satisfy dependencies without additional actions, or package holds, pins, exclusions, phased deployment, or repository policy prevents selection. | Inspect package policy and package-manager-specific hold or exclusion configuration. Document the reason rather than overriding policy during this lab. |

## Security considerations

Use only repositories and signing keys approved for the host; transport encryption does not replace repository signature validation.
Do not convert a simulation command into a real transaction during the lesson.
Do not use privilege elevation simply to suppress a simulation lock or permission error.
Treat third-party repositories as part of the software supply chain and review their ownership, release channel, signing-key lifecycle, and priority.
Preserve captured errors and exit statuses so failed previews cannot be misrepresented as empty successful plans.
Review package maintainer scripts, configuration-file behavior, service restarts, kernel changes, and bootloader changes before a real update.
Ensure backups, snapshots, and restoration procedures protect application data as well as operating-system files.
Use console or out-of-band access for maintenance that could disrupt network, storage, authentication, or remote-access services.
SHA-256 checksums detect later artifact changes but do not authenticate who created the reports.
Avoid exposing package inventories publicly because they can reveal software versions useful to an attacker.

## Rollback

### lesson_artifact_cleanup
### command
ROOT=/opt/lab-classroom/class22; test "$ROOT" = /opt/lab-classroom/class22 && find "$ROOT" -mindepth 1 -maxdepth 1 -type f -delete && rmdir "$ROOT"

### effect
Deletes only regular lab artifact files immediately beneath the required class directory and then removes the empty directory.

### warning
Review ROOT and list the directory before running cleanup. The cleanup does not reverse package changes because the lab performs none.

### future_real_update_recovery_plan
Record the pre-change package inventory, repository policy, running kernel, service state, application health, and storage health.
Verify a restorable backup or snapshot before approving the transaction.
Confirm whether the filesystem, virtual machine platform, and application support crash-consistent or application-consistent snapshots.
Preserve critical configuration and application data separately from package caches.
Define stop conditions such as unexpected removals, repository changes, dependency failures, boot errors, failed service checks, or data migration errors.
Prefer restoring a tested snapshot or rebuilding from known configuration when package downgrade is unsupported.
If version downgrade is considered, first confirm that the exact old package versions remain available and that application data and maintainer scripts support reversal.
Validate networking, storage, authentication, scheduled jobs, services, application transactions, and the active kernel after recovery.

## Video narration notes

Begin by showing the package-management architecture from repository trust through recovery. Emphasize that signed metadata establishes provenance, while operational safety still requires dependency review and workload validation. Create the isolated class directory and point out that every written artifact remains below /opt/lab-classroom/class22/. Generate the package inventory, explaining why Debian, RPM, and Alpine require different extraction methods and why the final evidence uses two normalized fields. Capture repository policy without refreshing caches. Next, run the non-applying proposal. On APT, pause on the two resolver modes: upgrade is conservative about removals, while dist-upgrade or full-upgrade may add or remove packages to satisfy dependencies. Show the recorded exit statuses and explain that lock, privilege, and metadata errors remain in the same report. Never describe a failed or blank preview as no updates available. Open the planning-only batch file and discuss kernel, core platform, services, applications, and explicit removal review. Make clear that the grouping is not permission to execute separate transactions. Review the maintenance checklist, focusing on backups, console access, service checks, reboot planning, stop conditions, and recovery authority. Finally, inspect artifact-paths.txt, generate SHA-256 checksums with the empty-safe loop, and verify them. End the demonstration without applying any package transaction.

## References

- APT apt-get manual: https://manpages.debian.org/apt-get
- APT apt-cache manual: https://manpages.debian.org/apt-cache
- Debian Administrator's Handbook, APT: https://www.debian.org/doc/manuals/debian-handbook/apt.en.html
- Debian dpkg-query manual: https://manpages.debian.org/dpkg-query
- DNF command reference: https://dnf.readthedocs.io/en/latest/command_ref.html
- RPM query documentation: https://rpm.org/docs/latest/manual/queryformat.html
- Alpine Linux apk handbook: https://docs.alpinelinux.org/user-handbook/0.1a/Working/apk.html
- Fedora system upgrade documentation: https://docs.fedoraproject.org/en-US/quick-docs/upgrading-fedora-offline/
- Ubuntu package management documentation: https://ubuntu.com/server/docs/package-management
- GNU Coreutils sha256sum documentation: https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html

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

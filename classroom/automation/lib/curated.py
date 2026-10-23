#!/usr/bin/env python3
"""Explicit curated lesson corpus for Classes 16–21 (dry-run / offline backend).

This is NOT a silent model downgrade. Operators must set GENERATOR_BACKEND=curated.
Content is original Homelab Academy teaching material aligned to the existing
pack class markdown style and required quality gates.
"""
from __future__ import annotations

from typing import Any

from . import today_iso


def _base(
    class_id: int,
    title: str,
    track: str,
    difficulty: str,
    minutes: int,
    risk: str,
    purpose: str,
    prereqs: list[str],
    objectives: list[str],
    reading: list[str],
    terms: list[tuple[str, str]],
    teaching: str,
    architecture: str,
    lab: str,
    expected: list[str],
    verification: list[str],
    trouble: list[tuple[str, str, str]],
    security: str,
    rollback: str,
    feynman: str,
    homework: str,
    quiz: list[str],
    answers: list[str],
    narration: str,
    refs: list[str],
    compatibility: str,
    dangerous: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "class_id": class_id,
        "title": title,
        "track": track,
        "difficulty": difficulty,
        "estimated_minutes": minutes,
        "lab_risk": risk,
        "purpose": purpose,
        "prerequisites": prereqs,
        "learning_objectives": objectives,
        "required_reading": reading,
        "terminology": [{"term": t, "meaning": m} for t, m in terms],
        "teaching": teaching,
        "architecture": architecture,
        "lab": lab,
        "expected_results": expected,
        "verification": verification,
        "troubleshooting": [
            {"symptom": a, "likely_cause": b, "fix": c} for a, b, c in trouble
        ],
        "security": security,
        "rollback": rollback,
        "feynman": feynman,
        "homework": homework,
        "quiz": quiz,
        "answer_key": answers,
        "video_narration": narration,
        "references": refs,
        "last_reviewed": today_iso(),
        "compatibility": compatibility,
        "dangerous_commands": dangerous or [],
    }


def lesson_16() -> dict[str, Any]:
    return _base(
        16,
        "Linux Users, Groups, Permissions, and Least Privilege",
        "Linux",
        "beginner",
        75,
        "medium",
        "Homelab services fail when files are owned by the wrong user or mode. Students learn identity, groups, and least-privilege permissions so containers and host processes can share data safely without chmod 777.",
        [
            "Completed Classes 1–4 infrastructure basics (or equivalent comfort with a Linux shell)",
            "A disposable Linux lab VM or container you are allowed to break",
            "Ability to use sudo on that lab host",
        ],
        [
            "Given a path, identify owner, group, and mode bits and explain who can read/write/execute",
            "Create a dedicated service user and group and assign least-privilege ownership without using 777",
            "Explain the difference between adding a user to a group and changing a file's group",
            "Demonstrate a verification command that proves access works for the intended identity and fails for another",
        ],
        [
            "man 7 inode (ownership concepts) — local man page",
            "chmod(1), chown(1), id(1), getent(1) — local man pages",
            "Debian Wiki: Permissions — https://wiki.debian.org/Permissions (primary distribution docs)",
        ],
        [
            ("UID/GID", "Numeric identity Linux uses for ownership and process credentials"),
            ("owner", "The user identity that owns a file or directory"),
            ("group", "A named set of users sharing a GID for shared access"),
            ("mode bits", "Read/write/execute permissions for owner, group, and others"),
            ("umask", "Mask applied when creating new files to strip default permissions"),
            ("least privilege", "Grant only the access required for the job—nothing more"),
            ("sudo", "Delegated privilege escalation with an audit trail"),
            ("sticky bit", "Directory bit that restricts deletion to file owner (common on /tmp)"),
        ],
        """## Instruction

### Identity is not a username sticker

Linux authorization decisions use numbers first: UID and GID. The names in `/etc/passwd` and `/etc/group` are human labels. When a process opens a file, the kernel compares the process credentials to the inode's owner/group/mode. If your container runs as UID 1000 but the bind-mounted library is owned by UID 0 with mode `600`, the container cannot read it—no amount of “but I'm an admin in the UI” changes that.

### Read `ls -l` like a contract

Example line:

```text
-rw-r----- 1 media media 4096 Sep 22 08:00 library.db
```

- Type: `-` file, `d` directory, `l` symlink
- Owner mode `rw-`: owner may read/write
- Group mode `r--`: group may read
- Other mode `---`: everyone else denied
- Owner `media`, group `media`

### Users and groups for services

Do not run every homelab service as your login user or as root. Create a dedicated user (or reuse a documented service UID such as 1000:1000 only when you intentionally standardize PUID/PGID across containers—covered later). Prefer:

1. A group for shared libraries (example: `media`)
2. Service users that are members of that group when they must share files
3. Directories with group sticky collaboration patterns (`2775` style) only when you understand setgid directories

### Least privilege checklist

1. Prefer group-readable over world-readable
2. Prefer owning service user over root-owned config
3. Prefer `640`/`750` over `777`/`666`
4. Prefer ACL only when classic mode bits cannot express the need (later class)

### Worked example

You want Sonarr-like access to `/data/media` and a downloader to write `/data/torrents`. Wrong approach: `chmod -R 777 /data`. Right approach on a disposable lab:

1. `sudo groupadd labmedia`
2. `sudo useradd -r -g labmedia -s /usr/sbin/nologin labsvc`
3. `sudo mkdir -p /opt/lab-classroom/class16/{media,torrents}`
4. `sudo chown -R labsvc:labmedia /opt/lab-classroom/class16`
5. `sudo chmod 2770 /opt/lab-classroom/class16/media /opt/lab-classroom/class16/torrents`
6. Verify with `namei -l` and `sudo -u labsvc test -w ...`

### Guided practice

On your lab host, create `/opt/lab-classroom/class16` if missing. Create two users `alice16` and `bob16`, one group `team16`, put both users in the group, create a shared file owned by `alice16:team16` mode `640`, and prove `bob16` can read but cannot write unless you intentionally grant write.
""",
        """```text
Process (UID/GID)
    │  open(path)
    ▼
VFS permission check ──► inode owner/group/mode (+ optional ACL)
    │ allow/deny
    ▼
File bytes
```

Homelab implication: Compose `user:` / PUID/PGID must match directory ownership or the ARR import path breaks.
""",
        """## Guided lab (disposable path only)

**Scope:** only `/opt/lab-classroom/class16` on a lab VM you own.

### WARNING — privileged commands

The following use `sudo`, create users/groups, and change ownership. Do not point them at `/home`, `/`, or production media trees.

**Prerequisites:** disposable lab VM; confirm path with `realpath`.

1. Create workspace:

```bash
sudo mkdir -p /opt/lab-classroom/class16
sudo chown "$USER":"$USER" /opt/lab-classroom/class16
cd /opt/lab-classroom/class16
pwd
```

2. Create group and users (lab only):

```bash
sudo groupadd class16g || true
sudo useradd -M -N -g class16g -s /usr/sbin/nologin class16a || true
sudo useradd -M -N -g class16g -s /usr/sbin/nologin class16b || true
getent group class16g
```

3. Shared directory with setgid group inheritance:

```bash
mkdir -p share
sudo chown class16a:class16g share
sudo chmod 2770 share
sudo -u class16a bash -lc 'echo hello > /opt/lab-classroom/class16/share/note.txt'
sudo -u class16a bash -lc 'chmod 640 /opt/lab-classroom/class16/share/note.txt'
namei -l /opt/lab-classroom/class16/share/note.txt
```

4. Verify access matrix:

```bash
sudo -u class16b bash -lc 'cat /opt/lab-classroom/class16/share/note.txt'
sudo -u class16b bash -lc 'echo fail >> /opt/lab-classroom/class16/share/note.txt' ; echo "write_exit=$?"
id class16a
id class16b
```

5. **Rollback / cleanup** (lab only):

```bash
sudo rm -rf /opt/lab-classroom/class16
sudo userdel class16a || true
sudo userdel class16b || true
sudo groupdel class16g || true
```
""",
        [
            "`namei -l` shows owner/group/mode for each path element",
            "`class16b` can read `note.txt` but write fails with permission denied",
            "Cleanup removes only the lab path and lab identities",
        ],
        [
            "Confirm workspace is under `/opt/lab-classroom/class16` via `pwd` and `realpath`",
            "Show `getent passwd class16a` and `getent group class16g`",
            "Show successful read as `class16b` and failed write",
            "After cleanup, `test ! -e /opt/lab-classroom/class16` succeeds",
        ],
        [
            ("Permission denied on read", "Wrong group membership or mode lacks group read", "Check `id`, `ls -l`, and `getent group`; add user to group and re-login/new session"),
            ("New files owned by wrong group", "Parent directory missing setgid bit", "Apply `chmod 2770` on the shared directory and recreate a test file"),
            ("Cannot delete lab users", "Processes still running as that UID", "Find with `ps -u class16a` and stop them, then `userdel`"),
        ],
        """Never use `chmod -R 777` on media or config trees—world-writable paths invite accidental or malicious writes. Do not paste real passwords into labs. Prefer dedicated service accounts over sharing your admin login with containers. Record UIDs you choose so future Compose stacks can match them deliberately.""",
        """Rollback for this lab is deletion of `/opt/lab-classroom/class16` and removal of `class16a`/`class16b`/`class16g` as shown in the lab cleanup block. If you accidentally changed permissions elsewhere, restore from backup; this class intentionally avoids production paths. Snapshot the lab VM before experimenting if you are unsure.""",
        """### Explain
Describe how UID/GID and mode bits decide access, and why least privilege beats 777.

### Simplify
Explain to a 12-year-old using a locker + club membership analogy.

### Example
Give one homelab example where wrong ownership breaks a container bind mount.

### Weak spot
Note what confused you (setgid directories, umask, or sudo).

### Retry
Rewrite the explanation after re-reading the worked example.
""",
        """Independently (same disposable path): create `class16c` in `class16g`, write a file as `class16a`, prove `class16c` read-only access, then grant group write deliberately and prove write works. Capture command transcripts in your workbook. Redact hostnames if you publish screenshots.""",
        [
            "What numeric fields does the kernel use for file access decisions?",
            "What does mode `640` allow the group to do?",
            "Why is `chmod 777` usually wrong for a media library?",
            "How do you prove which groups your current shell has?",
            "What is the purpose of the setgid bit on a directory?",
            "Name one verification command that shows ownership along a path.",
            "What should you do before changing ownership on an unfamiliar tree?",
        ],
        [
            "UID and GID (process credentials vs inode owner/group)",
            "Read only (not write/execute)",
            "It grants world write, destroying confidentiality and inviting accidents",
            "`id` (and newly added groups may require a new login session)",
            "New files inherit the directory's group",
            "`namei -l` or `ls -l`",
            "Confirm the path with `realpath`, prefer backups/snapshots, stay in a disposable lab directory",
        ],
        """Open on a terminal screenshot. Narrate reading `ls -l` left to right. Demonstrate a failed access, then a least-privilege fix—never 777. Close with cleanup to emphasize reversible labs.""",
        [
            "chmod(1) Linux man page (local)",
            "chown(1) Linux man page (local)",
            "Debian Wiki Permissions: https://wiki.debian.org/Permissions",
        ],
        "Assumes a Debian/Ubuntu-like lab VM with sudo, useradd/groupadd, and bash. Paths are Linux-specific; adapt carefully on immutable OS variants.",
        [
            {
                "command": "sudo useradd ...; sudo chown -R ...; sudo rm -rf /opt/lab-classroom/class16",
                "warning": "Creates/deletes users and recursively deletes the lab directory",
                "prerequisites": "Disposable lab VM; path confirmed with realpath",
                "verification": "getent passwd/group; namei -l; test read/write matrix",
                "backup": "Prefer VM snapshot before useradd/chown experiments",
                "rollback": "rm -rf lab path; userdel/groupdel as documented",
                "failure_mode": "Pointing rm/chown at the wrong tree can destroy data",
            }
        ],
    )


def lesson_17() -> dict[str, Any]:
    return _base(
        17,
        "Processes, Signals, and systemd Service Management",
        "Linux",
        "beginner",
        80,
        "medium",
        "Homelab hosts run long-lived services under systemd. Students learn process inspection, signals, and unit control so they can start/stop/restart safely and read failure evidence instead of rebooting blindly.",
        [
            "Class 16 concepts (users/permissions) recommended",
            "Lab Linux VM with systemd (not a minimal container without systemd)",
            "Permission to use systemctl --user or a dedicated user service in lab",
        ],
        [
            "Identify a process PID, user, and command line using ps/ss",
            "Send a non-destructive signal and explain SIGTERM vs SIGKILL",
            "Create a simple user-level systemd service for a disposable script",
            "Use systemctl status/journalctl to verify start, stop, and failure",
        ],
        [
            "systemd.unit(5) and systemd.service(5) man pages",
            "signal(7) man page",
            "systemd documentation: https://www.freedesktop.org/software/systemd/man/latest/",
        ],
        [
            ("PID", "Process identifier assigned by the kernel"),
            ("signal", "Asynchronous notification to a process (e.g., TERM, KILL, HUP)"),
            ("SIGTERM", "Polite terminate request—process may clean up"),
            ("SIGKILL", "Forced kill—cannot be caught; last resort"),
            ("systemd unit", "Declarative description of a service, timer, mount, etc."),
            ("systemctl", "Controller for systemd units"),
            ("journald", "systemd journal collecting stdout/stderr and structured logs"),
            ("WantedBy", "Unit install section linking service into a target like default.target"),
        ],
        """## Instruction

### Processes are the runtime truth

Dashboards lie; `ps` and cgroup views show what is actually running. For each critical service, you should be able to answer: PID, user, parent, command, and listening ports.

### Signals

- `SIGTERM` (15): ask it to exit
- `SIGINT` (2): interrupt (Ctrl+C)
- `SIGHUP` (1): often reload config (service-dependent)
- `SIGKILL` (9): force death—skips cleanup; can corrupt state

Prefer TERM, wait, then KILL only if needed.

### systemd mental model

A `.service` unit describes ExecStart, user, restart policy, and dependencies. `systemctl start` does not magically fix permissions; it runs the command in the configured context. Failed units leave evidence in `systemctl status` and the journal.

### Worked example

A user service that writes a heartbeat file every minute teaches enable/start/status/stop without touching system-wide units.
""",
        """```text
systemctl start foo.service
   → systemd forks ExecStart
   → process PID logged
   → stdout/stderr → journald
systemctl stop
   → SIGTERM (then SIGKILL after TimeoutStopSec)
```
""",
        """## Guided lab

**Scope:** user systemd units under `~/.config/systemd/user/` and files under `/opt/lab-classroom/class17`.

1. Prepare:

```bash
mkdir -p /opt/lab-classroom/class17 ~/.config/systemd/user
cat > /opt/lab-classroom/class17/heartbeat.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "$(date -Is) heartbeat" >> /opt/lab-classroom/class17/heartbeat.log
EOF
chmod 750 /opt/lab-classroom/class17/heartbeat.sh
```

2. Unit file:

```bash
cat > ~/.config/systemd/user/class17-heartbeat.service <<'EOF'
[Unit]
Description=Class17 lab heartbeat
[Service]
Type=oneshot
ExecStart=/opt/lab-classroom/class17/heartbeat.sh
[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user start class17-heartbeat.service
systemctl --user status class17-heartbeat.service --no-pager
```

3. Signals on a foreground process (separate terminal optional):

```bash
sleep 300 &
echo $!
kill -TERM $!
wait || true
```

4. Rollback:

```bash
systemctl --user disable --now class17-heartbeat.service || true
rm -f ~/.config/systemd/user/class17-heartbeat.service
systemctl --user daemon-reload
rm -rf /opt/lab-classroom/class17
```
""",
        [
            "systemctl --user status shows the oneshot exited successfully",
            "heartbeat.log gains a timestamp line",
            "After rollback, unit file is gone and lab directory removed",
        ],
        [
            "systemctl --user status class17-heartbeat.service",
            "tail -n 1 /opt/lab-classroom/class17/heartbeat.log",
            "systemctl --user cat class17-heartbeat.service",
            "Confirm cleanup with test ! -e",
        ],
        [
            ("Unit not found", "Forgot daemon-reload or wrong --user vs system", "daemon-reload; verify path under ~/.config/systemd/user"),
            ("Permission denied ExecStart", "Script not executable or path wrong", "chmod 750; use absolute ExecStart"),
            ("Linger issues on some hosts", "User services stop at logout", "For lab, stay logged in; document loginctl enable-linger only with understanding"),
        ],
        """Do not send SIGKILL to databases as a first step. Do not enable linger or system-wide units on production without change control. Avoid editing units under /lib/systemd; use /etc overrides.""",
        """Disable/remove the user unit and delete `/opt/lab-classroom/class17` as shown. If you used kill on the wrong PID, restart that service via its proper unit—not a reboot-as-fix habit.""",
        """### Explain
Contrast SIGTERM vs SIGKILL and how systemd uses them on stop.

### Simplify
Traffic light analogy for stop requests.

### Example
Describe diagnosing a failed web service with status+journal.

### Weak spot
Note confusion about --user vs system units.

### Retry
Rewrite after reading systemd.service(5) ExecStart section.
""",
        """Write a second oneshot user service that appends `hello` to a lab file, enable it, prove it runs once via journal/status, then remove it completely.""",
        [
            "Which signal requests a graceful exit?",
            "Which signal cannot be caught?",
            "What command reloads unit files after edits?",
            "Where do user unit files normally live?",
            "Name two commands to inspect a failed service",
            "Why is reboot a poor first troubleshooting step?",
        ],
        [
            "SIGTERM",
            "SIGKILL",
            "systemctl daemon-reload (or systemctl --user daemon-reload)",
            "~/.config/systemd/user/",
            "systemctl status and journalctl -u (or --user)",
            "It destroys evidence and does not teach root cause",
        ],
        """Show ps output, then systemctl status. Emphasize TERM before KILL. Demo creating and deleting a user unit end-to-end.""",
        [
            "https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html",
            "signal(7) man page",
        ],
        "Requires a systemd-based Linux lab (Debian/Ubuntu/Fedora). Not applicable inside containers that lack systemd unless you use a full VM.",
        [
            {
                "command": "kill -TERM <pid>; systemctl --user disable --now ...",
                "warning": "Signals can stop processes; disabling units stops services",
                "prerequisites": "Know the PID/unit is the lab heartbeat",
                "verification": "systemctl --user status; journalctl --user -u ...",
                "backup": "N/A for lab oneshot; VM snapshot optional",
                "rollback": "Remove unit file; daemon-reload; restore lab dir from notes",
                "failure_mode": "Killing the wrong PID stops an unrelated service",
            }
        ],
    )


def lesson_18() -> dict[str, Any]:
    return _base(
        18,
        "Linux Logs and journalctl",
        "Linux",
        "beginner",
        70,
        "low",
        "When a homelab service fails, logs are evidence. Students learn journalctl filters and persistent journal basics so they can capture boot/service failures without guessing.",
        ["Class 17 recommended", "systemd lab host"],
        [
            "Retrieve logs for a unit since boot with journalctl",
            "Filter by time and priority",
            "Explain where traditional text logs still appear under /var/log",
            "Capture a log excerpt as workbook evidence with secrets redacted",
        ],
        [
            "journalctl(1) man page",
            "systemd-journald.service(8)",
            "https://www.freedesktop.org/software/systemd/man/latest/journalctl.html",
        ],
        [
            ("journald", "systemd component storing structured logs"),
            ("priority", "emerg..debug severity levels"),
            ("_SYSTEMD_UNIT", "journal field identifying the unit"),
            ("persistent journal", "journal stored on disk across reboots when configured"),
            ("syslog", "Traditional logging protocol/facility still seen in /var/log"),
            ("cursor", "Opaque pointer for continuing journal reads"),
            ("boot ID", "Identifier for a specific boot's log stream"),
        ],
        """## Instruction

### Logs are evidence, not vibes

When a homelab service fails after reboot, the question is not “did you try restarting again?” — it is “what did the unit say?” The systemd journal stores stdout/stderr and structured fields from units. Learning `journalctl` turns outages into timelines.

### Essential filters

- `journalctl -u service.service -b` — this boot only for one unit
- `--since "1 hour ago"` / `--until` — time windows for change correlation
- `-p err..alert` — severity band when you need failures fast
- `-o short-iso` — readable timestamps for workbook paste
- `-n 200` — cap noise while learning

Always redact tokens, session cookies, and webhook URLs before sharing excerpts.

### Journal vs classic files

Many stacks still write under `/var/log` (nginx, apt history, auth.log). Professionals can move between both worlds: journal for unit lifecycle, files for app-native formats. On appliances without persistent journals, note that reboot may wipe volatile storage — configure persistence deliberately, not accidentally.

### Worked example

Capture errors since boot, then narrow to a unit you just restarted. Save a redacted excerpt under `/opt/lab-classroom/class18/` as workbook evidence. Prefer filters over dumping the entire journal.
""",
        """```text
App stdout/stderr → journald → journalctl filters → operator evidence
App file logs → /var/log/... → tail/less
```
""",
        """## Guided lab

```bash
mkdir -p /opt/lab-classroom/class18
systemctl --user status class17-heartbeat.service --no-pager || true
journalctl --user -b -n 50 --no-pager > /opt/lab-classroom/class18/sample.txt || journalctl -b -n 50 --no-pager > /opt/lab-classroom/class18/sample.txt
journalctl -b -p err..alert --no-pager | head
ls -la /var/log | head
```

Rollback: `rm -rf /opt/lab-classroom/class18`
""",
        ["sample.txt contains journal lines", "error priority query returns without crashing", "lab dir removable"],
        ["wc -l sample.txt", "head sample.txt", "test -d /opt/lab-classroom/class18 then remove"],
        [
            ("No journal entries", "Running in environment without journal access", "Use a real VM; check permissions"),
            ("Permission denied", "Need membership in systemd-journal/adm", "Use sudo journalctl or add user carefully"),
            ("Huge output", "Missing filters", "Add -u, --since, -n"),
        ],
        """Redact tokens, IPs you consider sensitive, and usernames before sharing logs publicly. Do not disable journald persistence without understanding audit impact.""",
        """Delete `/opt/lab-classroom/class18`. Logging queries are read-only; no service changes required.""",
        """### Explain
How journalctl differs from tailing a text file.

### Simplify
Explain a 'black box recorder' analogy.

### Example
Walk through finding why a service failed after reboot.

### Weak spot
Timezones/filters confusion.

### Retry
Rewrite with one concrete -u example.
""",
        """Capture journal lines for any failed unit on your lab (or simulate by stopping a user unit), paste redacted excerpt into workbook, and list three filters you used.""",
        [
            "What flag limits logs to the current boot?",
            "Which flag filters by unit?",
            "Name a traditional log directory",
            "Why redact logs before posting online?",
            "What does -p err select?",
        ],
        [
            "The -b flag limits output to the current boot",
            "The -u flag filters by systemd unit name",
            "/var/log holds many classic text logs",
            "Secrets and personal data leak easily in unredacted logs",
            "Priority error and more severe levels depending on range syntax",
        ],
        """Show a noisy unfiltered journal, then tighten with -u and --since. Emphasize evidence hygiene and redaction before sharing.""",
        ["https://www.freedesktop.org/software/systemd/man/latest/journalctl.html"],
        "systemd hosts; containers may lack journal access.",
        [
            {
                "command": "rm -rf /opt/lab-classroom/class18",
                "warning": "Deletes lab log captures directory",
                "prerequisites": "Path confirmed under /opt/lab-classroom/class18 only",
                "verification": "test ! -e /opt/lab-classroom/class18",
                "backup": "Copy sample.txt elsewhere if you need to keep evidence",
                "rollback": "Recreate directory and re-run journalctl capture",
                "failure_mode": "Wrong path deletes unrelated files",
            }
        ],
    )


def lesson_19() -> dict[str, Any]:
    return _base(
        19,
        "SSH Keys and Safe SSH Hardening",
        "Linux",
        "intermediate",
        90,
        "high",
        "SSH is the front door to most homelabs. Students generate keys, restrict logins on a lab VM, and verify access—without locking themselves out.",
        ["Classes 16–18", "Lab VM with sshd", "Console/IPMI/hypervisor console access as break-glass"],
        [
            "Generate an Ed25519 key pair for lab use",
            "Install a public key and authenticate without a password",
            "Identify dangerous sshd settings and safer alternatives",
            "Document a break-glass rollback via console if SSH breaks",
        ],
        [
            "sshd_config(5) man page",
            "OpenSSH documentation: https://www.openssh.com/manual.html",
        ],
        [
            ("public key", "Key material you can share; placed in authorized_keys"),
            ("private key", "Secret key—never upload to git or chat"),
            ("authorized_keys", "Server file listing permitted public keys"),
            ("sshd", "SSH daemon accepting remote sessions"),
            ("PasswordAuthentication", "sshd setting allowing password logins"),
            ("PermitRootLogin", "Whether root may SSH directly"),
            ("fail2ban", "Optional intrusion prevention watching auth logs"),
        ],
        """## Instruction

### SSH is a front door

Most homelab administration still arrives over SSH. A weak front door (password auth on the public Internet, shared root passwords, unmanaged keys) eventually becomes an incident. This class builds a safe pattern: keys first, prove access, then harden — with console break-glass ready.

### Keys

Prefer Ed25519. Keep the private key private: never commit it, never paste it into Discord, never leave it unencrypted on shared storage without a passphrase unless the lab policy explicitly allows empty passphrases for disposable keys.

### Hardening order (memorize)

1. Install your public key (`authorized_keys`)
2. Open a **second** SSH session and prove login
3. Only then consider disabling password authentication
4. Run `sshd -t` before reload
5. Keep hypervisor/IPMI/console access documented

Never edit live sshd_config on a remote-only machine without a recovery path.
""",
        """```text
Client private key → SSH auth → sshd matches authorized_keys → session
```
""",
        """## Guided lab (HIGH RISK)

### WARNING
Changing sshd can lock you out. Use a disposable lab VM and keep hypervisor console open.

```bash
mkdir -p /opt/lab-classroom/class19
ssh-keygen -t ed25519 -f /opt/lab-classroom/class19/lab_ed25519 -N "" -C "class19-lab"
# Install pubkey to the LAB VM user (example):
# ssh-copy-id -i /opt/lab-classroom/class19/lab_ed25519.pub user@labvm
```

Verify with a second terminal before any sshd hardening. If you practice hardening, copy sshd_config first:

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.class19.bak
# make ONE change via /etc/ssh/sshd_config.d/99-class19.conf preferred
sudo sshd -t
sudo systemctl reload ssh || sudo systemctl reload sshd
```

Rollback:

```bash
sudo cp /etc/ssh/sshd_config.class19.bak /etc/ssh/sshd_config
sudo rm -f /etc/ssh/sshd_config.d/99-class19.conf
sudo sshd -t && sudo systemctl reload ssh || sudo systemctl reload sshd
rm -rf /opt/lab-classroom/class19
```
""",
        ["Key pair created under lab path", "sshd -t passes", "Backup config restored on rollback"],
        ["ls -l lab_ed25519*", "sudo sshd -t", "second SSH session works before disabling passwords"],
        [
            ("Locked out", "PasswordAuth disabled before key tested", "Use hypervisor console; restore backup config"),
            ("Permission denied (publickey)", "Wrong authorized_keys perms or key", "chmod 700 ~/.ssh; 600 authorized_keys"),
            ("sshd -t fails", "Syntax error", "Fix config before reload"),
        ],
        """Never commit private keys. Do not expose sshd to the public internet without keys, rate limiting, and preferably VPN. Disable root password SSH. Prefer drop-in config files.""",
        """Restore sshd_config backup and remove drop-in; reload sshd; delete lab keys directory. Confirm console login still works.""",
        """### Explain
Why test a second SSH session before disabling passwords.

### Simplify
House key vs spare key under the mat.

### Example
Describe a lockout and console recovery.

### Weak spot
authorized_keys permissions.

### Retry
Rewrite hardening order from memory.
""",
        """On lab VM only: create a drop-in that sets a banner or MaxAuthTries, validate with sshd -t, reload, prove login, then roll back completely.""",
        [
            "Which key type is recommended in this class?",
            "What must you keep private?",
            "What command validates sshd config syntax?",
            "What is break-glass access?",
            "When is it safe to disable PasswordAuthentication?",
        ],
        ["Ed25519", "Private key", "sshd -t", "Console/IPMI/hypervisor access when SSH fails", "Only after key login proven on a second session"],
        """Show keygen, ssh-copy-id, successful login, then a deliberate careful hardening with console visible.""",
        ["https://www.openssh.com/manual.html", "sshd_config(5)"],
        "OpenSSH server on Linux lab VM; Windows clients may use OpenSSH or compatible clients.",
        [
            {
                "command": "sudo editing sshd_config; systemctl reload ssh",
                "warning": "Can lock out all remote access",
                "prerequisites": "Console access; config backup; proven key auth",
                "verification": "sshd -t; second SSH login",
                "backup": "cp sshd_config to .bak; prefer drop-in files",
                "rollback": "restore backup; remove drop-in; reload",
                "failure_mode": "No console + bad sshd = full lockout",
            }
        ],
    )


def lesson_20() -> dict[str, Any]:
    return _base(
        20,
        "Package Management and Safe System Updates",
        "Linux",
        "beginner",
        75,
        "medium",
        "Unattended or careless upgrades can break homelabs. Students practice package queries, changelogs awareness, and staged updates with a rollback plan on a disposable VM.",
        ["Linux lab VM", "Classes 17–18"],
        [
            "Query installed and available packages with the distro package manager",
            "Apply updates on a lab VM with logging",
            "Explain reboot-required vs service-restart cases",
            "Document a rollback/snapshot strategy before upgrades",
        ],
        [
            "apt(8)/dnf(8) man pages for your distro",
            "Debian Securing Updates guidance via official wiki",
        ],
        [
            ("package", "Versioned software archive tracked by the OS package manager"),
            ("repository", "Signed source of packages"),
            ("pinning", "Constraining versions/origins"),
            ("changelog", "Human-readable history of package changes"),
            ("needs-restart", "Services/libs that require restart after upgrade"),
            ("snapshot", "Point-in-time VM/zfs/btrfs restore point"),
        ],
        """## Instruction

### Updates are change management

Package upgrades are not “click update.” They change libraries, kernels, and service defaults. Homelabs break when operators upgrade everything casually on Friday night with no snapshot.

### Safe rhythm (Debian/Ubuntu examples)

1. Take a VM or filesystem snapshot
2. `apt-get update` and capture the log
3. `apt list --upgradable` and skim high-risk packages (kernel, docker, openssl)
4. Apply upgrades in a maintenance window
5. `systemctl --failed` and smoke-test critical services
6. Reboot only when required — with console available

Avoid adding random third-party repositories for convenience; they expand your supply chain. Do not disable signature verification.

Keep SSH access available during remote upgrades. If a kernel ABI change requires reboot, schedule it deliberately and verify critical containers after boot using a short smoke checklist (DNS, reverse proxy, media stack health).
""",
        """```text
snapshot → apt update → review → upgrade → verify services → keep/rollback snapshot
```
""",
        """## Guided lab

```bash
mkdir -p /opt/lab-classroom/class20
sudo apt-get update | tee /opt/lab-classroom/class20/apt-update.log
apt list --upgradable 2>/dev/null | tee /opt/lab-classroom/class20/upgradable.txt || true
# Optional lab-only upgrade of a harmless package if available; otherwise stop after listing
```

If you upgrade, verify with `systemctl --failed` and reboot only if kernel requires and console is available.

Rollback: restore VM snapshot if taken; `rm -rf /opt/lab-classroom/class20`
""",
        ["update log created", "upgradable list captured", "no unexplained failed units"],
        ["test -f apt-update.log", "systemctl --failed --no-pager", "workbook notes include snapshot yes/no"],
        [
            ("apt update fails", "Network/DNS/repo mirror", "Check network; try default mirrors"),
            ("Held packages", "Pinning/holds", "apt-mark showhold"),
            ("Broken services after upgrade", "Incompatible config", "Roll back snapshot; read changelog"),
        ],
        """Do not disable signature verification. Do not add random third-party repos for convenience. Keep SSH access available during remote upgrades.""",
        """Revert VM snapshot if upgrades misbehave. Remove lab logs directory. Avoid force-downgrades unless you understand dependencies.""",
        """### Explain
Why snapshots beat wishful thinking before upgrades.

### Simplify
Save-game before a boss fight.

### Example
Kernel upgrade needing reboot with console ready.

### Weak spot
full-upgrade vs upgrade.

### Retry
Write your personal pre-upgrade checklist.
""",
        """Produce a written pre-upgrade checklist for your lab VM (snapshot, update, review, upgrade, verify, reboot policy) and attach apt list --upgradable output in your workbook.""",
        [
            "What command refreshes package metadata on Debian/Ubuntu?",
            "Why take a snapshot first?",
            "Where can apt history be found?",
            "What should you check after upgrading?",
            "Name one risk of untrusted third-party repos",
        ],
        ["apt update / apt-get update", "Fast rollback", "/var/log/apt/history.log", "systemctl --failed and critical service smoke tests", "Supply-chain / compromised packages"],
        """Show update → list → decide on camera. Stress snapshots and console availability before kernel upgrades.""",
        ["Debian apt documentation / man apt"],
        "Examples use apt; adapt to dnf/pacman on other distros.",
        [
            {
                "command": "sudo apt-get upgrade",
                "warning": "Changes many packages; can reboot-require or break services",
                "prerequisites": "VM snapshot; maintenance window; console",
                "verification": "systemctl --failed; service smoke tests",
                "backup": "Hypervisor snapshot / ZFS snapshot",
                "rollback": "Revert snapshot",
                "failure_mode": "Partial upgrade leaves system inconsistent",
            }
        ],
    )


def lesson_21() -> dict[str, Any]:
    return _base(
        21,
        "IP Addresses, Subnets, Gateways, and Routing",
        "Network",
        "beginner",
        85,
        "low",
        "Builds on Class 15 addressing literacy with routing tables and multi-subnet thinking for homelab VLANs and dual-homed hosts—without duplicating Class 15's beginner IPv4 primer.",
        ["Class 15 IPv4 addressing", "Lab Linux host"],
        [
            "Read a routing table and explain default route vs connected routes",
            "Calculate whether two addresses share a subnet given CIDR",
            "Traceroute/path explain to a gateway and beyond at a conceptual level",
            "Document the lab host's addresses and routes in a workbook table",
        ],
        [
            "ip-route(8) man page",
            "Class 15 academy material on masks/gateways",
        ],
        [
            ("routing table", "Kernel map of where to send packets"),
            ("default route", "Route used when no longer prefix matches (often 0.0.0.0/0)"),
            ("connected route", "Route for a subnet local to an interface"),
            ("CIDR", "Prefix-length notation like /24"),
            ("next hop", "Next router IP for a route"),
            ("metric", "Tie-breaker cost among routes"),
            ("asymmetric routing", "Forward and return paths differ—troubleshooting hazard"),
        ],
        """## Instruction

### From addresses to paths

Class 15 taught reading IP, mask, and gateway. This class focuses on **routing decisions**: how a host chooses an interface and next hop. When the destination is on-link, the kernel ARP/ND resolves neighbors. When it is not, the default route (or a more specific route) sends traffic to a gateway.

### Read `ip route`

Look for connected routes (your LANs) and the default route (`default` or `0.0.0.0/0`). Metrics break ties. Multi-homed labs and VLANs make wrong routes a common outage class: “ping works to the gateway but not to VLAN B” is a routing problem, not a Docker superstition.

### Practice mental model

Given `192.168.10.0/24` and `192.168.20.0/24`, two hosts need a router (or L3 switch) to talk. Document your lab’s addresses and routes before changing firewalls or reverse proxies later in the curriculum.
""",
        """```text
App → kernel route lookup → on-link delivery OR next-hop gateway → upstream
```
""",
        """## Guided lab

Create a disposable evidence directory and capture routing facts (read-only):

```bash
mkdir -p /opt/lab-classroom/class21
ip -br addr | tee /opt/lab-classroom/class21/addr.txt
ip route | tee /opt/lab-classroom/class21/route.txt
ip -4 route get 1.1.1.1 | tee /opt/lab-classroom/class21/get.txt || true
```

In your workbook, explain which interface and gateway would be used for an on-LAN neighbor versus an Internet address. Do not add experimental routes on production hosts.

Rollback (lab files only):

```bash
rm -rf /opt/lab-classroom/class21
```
""",
        ["addr and route captures exist", "student explanation of default route written", "no config changes required"],
        ["test -f route.txt", "grep -E 'default|0.0.0.0' route.txt || true", "workbook table completed"],
        [
            ("No default route", "DHCP failed or static misconfig", "Check gateway; renew DHCP"),
            ("Wrong interface chosen", "Multiple defaults/metrics", "Compare metrics; policy routing advanced"),
            ("Confusion with Class 15", "Overlapping topics", "Focus on route table literacy here"),
        ],
        """Do not change production routes casually. Avoid publishing full internal network maps if sensitive.""",
        """Read-only lab—delete captures directory. If you changed routes (not required), delete added routes and restore DHCP.""",
        """### Explain
How a host chooses between on-link and gateway delivery.

### Simplify
Neighborhood streets vs highway on-ramp.

### Example
Two VLANs and a router.

### Weak spot
CIDR math.

### Retry
Work one /24 and one /25 example.
""",
        """Draw your lab's route path to the default gateway and to another LAN host; attach `ip route` and `ip -br addr` output with any sensitive addresses redacted if you publish screenshots.""",
        [
            "What does the default route match?",
            "Which command shows the route used to reach an IP?",
            "What is a next hop?",
            "How does this class differ from Class 15?",
            "Name the command to list addresses briefly",
        ],
        ["All destinations without a longer match (typically 0.0.0.0/0)", "ip route get", "Next router IP for that route", "Emphasizes routing tables/path vs basic mask literacy", "ip -br addr"],
        """Compare Class 15 mask reading to ip route output side by side; narrate on-link versus default-route decisions.""",
        ["ip-route(8)", "Academy Class 15"],
        "Linux iproute2; concepts transfer to other OS with different commands.",
        [
            {
                "command": "rm -rf /opt/lab-classroom/class21",
                "warning": "Deletes lab capture directory only",
                "prerequisites": "Confirm path with realpath",
                "verification": "test ! -e /opt/lab-classroom/class21",
                "backup": "Copy route.txt if you need to keep evidence",
                "rollback": "Recreate directory and re-run capture commands",
                "failure_mode": "Wrong path deletes unrelated data",
            }
        ],
    )



def _shift(b: dict[str, Any], new_id: int, title: str | None = None) -> dict[str, Any]:
    old_id = int(b["class_id"])
    b = dict(b)
    b["class_id"] = new_id
    if title:
        b["title"] = title
    for k in ("lab", "teaching", "homework", "rollback", "feynman", "purpose", "security", "video_narration", "architecture"):
        if isinstance(b.get(k), str):
            b[k] = b[k].replace(f"class{old_id}", f"class{new_id}").replace(f"/class{old_id}/", f"/class{new_id}/")
    for list_key in ("verification", "expected_results", "quiz", "answer_key"):
        items = []
        for item in b.get(list_key) or []:
            if isinstance(item, str):
                items.append(item.replace(f"class{old_id}", f"class{new_id}"))
            else:
                items.append(item)
        b[list_key] = items
    dang = []
    for d in b.get("dangerous_commands") or []:
        nd = dict(d)
        for kk in nd:
            if isinstance(nd[kk], str):
                nd[kk] = nd[kk].replace(f"class{old_id}", f"class{new_id}")
        dang.append(nd)
    b["dangerous_commands"] = dang
    return b


def lesson_filesystem() -> dict[str, Any]:
    return _base(
        16,
        "Linux Filesystem and Navigation",
        "Linux",
        "beginner",
        70,
        "low",
        "Homelab operators must navigate paths confidently: absolute vs relative, home vs /opt lab trees, and where configs and logs live—without touching production media roots.",
        ["A Linux lab shell", "Classes 1–4 recommended"],
        [
            "Distinguish absolute and relative paths and resolve them with realpath/pwd",
            "List and interpret directory contents including hidden files",
            "Locate common system directories (/etc, /var/log, /home, /opt) and state their roles",
            "Create a disposable lab tree under /opt/lab-classroom/class16 and navigate it safely",
        ],
        ["hier(7) man page", "pwd(1), ls(1), find(1), realpath(1)"],
        [
            ("absolute path", "Path from filesystem root starting with /"),
            ("relative path", "Path interpreted from the current working directory"),
            ("inode", "Filesystem object metadata including ownership and mode"),
            ("cwd", "Current working directory of a process"),
            ("home directory", "Per-user starting directory, usually under /home"),
            ("symlink", "A path that points to another path"),
            ("FHS", "Filesystem Hierarchy Standard describing common Linux directories"),
            ("dotfile", "Hidden file whose name starts with a period"),
        ],
        """## Instruction

### The map of a Linux machine

Linux stores almost everything as files under a single tree rooted at `/`. Homelab work fails when you edit the wrong tree: production media under `/data`, configs under `/etc`, or a disposable lab under `/opt/lab-classroom`.

### Absolute vs relative

`/opt/lab-classroom/class16` is absolute. `../class16` is relative to cwd. Always confirm with `pwd` and `realpath` before destructive commands.

### Everyday landmarks

- `/etc` — system configuration
- `/var/log` — classic logs
- `/home` — user homes
- `/opt` — optional local software and our disposable classroom labs
- `/tmp` — temporary; may be cleared on reboot

### Worked example

Create `/opt/lab-classroom/class16/{configs,logs,bin}`, create a file, `cd` with relative paths, and prove location with `pwd` and `realpath`. Never point labs at `/data`.
""",
        """```text
/ (root)
├── etc/   configs
├── var/log/
├── home/
└── opt/lab-classroom/class16/   disposable lab only
```""",
        """## Guided lab

Only touch `/opt/lab-classroom/class16` on a disposable lab host.

```bash
sudo mkdir -p /opt/lab-classroom/class16
sudo chown "$USER":"$USER" /opt/lab-classroom/class16
cd /opt/lab-classroom/class16
mkdir -p configs logs bin
echo "lab" > configs/note.txt
touch .hidden_marker
pwd
realpath configs/note.txt
ls -la
find . -type f -o -type d
namei -l configs/note.txt
```

Rollback (lab only):

```bash
rm -rf /opt/lab-classroom/class16
```
""",
        ["pwd shows class16 path", "realpath prints absolute file path", "find lists note.txt"],
        ["pwd | grep class16", "test -f configs/note.txt", "realpath configs/note.txt"],
        [
            ("Permission denied under /opt", "Directory owned by root", "chown the lab path to your user after sudo mkdir"),
            ("Lost in relative paths", "Forgot pwd", "Run pwd; prefer absolute paths for dangerous commands"),
            ("Edited production by mistake", "Wrong tree", "Never use /data in this lab; stay under /opt/lab-classroom"),
        ],
        "Do not explore or modify other users' home directories. Keep labs under /opt/lab-classroom. Never chmod 777 system trees.",
        "Delete only /opt/lab-classroom/class16. If you changed cwd in a long-lived session, cd back to a known path.",
        """### Explain
Absolute vs relative paths and why labs use /opt/lab-classroom.

### Simplify
Street address vs 'two doors down'.

### Example
Finding a config under /etc versus a lab note under /opt.

### Weak spot
Symlinks or hidden files.

### Retry
Rewrite after reading hier(7) summary.
""",
        "Without hints, recreate the class16 tree from memory, place three files, and document each absolute path in your workbook with evidence.",
        [
            "What character starts an absolute path?",
            "Which command prints the current directory?",
            "Name two directories under / that store configs or logs",
            "Where should disposable classroom labs live in this curriculum?",
            "What does realpath do?",
            "Why avoid experimenting directly in /data?",
        ],
        [
            "A leading slash / starts an absolute path",
            "The pwd command prints the current working directory",
            "/etc and /var/log (among others) store configs or classic logs",
            "Disposable labs live under /opt/lab-classroom/...",
            "realpath resolves to a canonical absolute path",
            "It may hold production media; labs must stay disposable",
        ],
        "Open a terminal recording. Show pwd, mkdir lab tree, ls -la including hidden, and realpath. Emphasize staying out of /data.",
        ["hier(7) Linux man page (local)", "pwd(1) Linux man page (local)", "ls(1) Linux man page (local)"],
        "Linux shell with standard coreutils; examples use bash.",
        [{
            "command": "rm -rf /opt/lab-classroom/class16",
            "warning": "Deletes the disposable lab directory",
            "prerequisites": "Confirm path with realpath",
            "verification": "test ! -e /opt/lab-classroom/class16",
            "backup": "Not required for empty lab notes",
            "rollback": "Recreate directory with mkdir",
            "failure_mode": "Wrong path deletes unrelated data",
        }],
    )


def lesson_pipes() -> dict[str, Any]:
    return _base(
        17,
        "Shell Pipes and Redirection",
        "Linux",
        "beginner",
        75,
        "low",
        "Pipes and redirection turn small tools into investigation workflows for logs and configs—essential for ARR and systemd troubleshooting later.",
        ["Class 16 filesystem navigation", "Linux lab shell"],
        [
            "Redirect stdout and stderr to files safely under a lab path",
            "Build a pipeline of two or more filters (grep/sort/uniq/wc)",
            "Explain the difference between > and >> and when overwrite is dangerous",
            "Capture a filtered log excerpt without using interactive GUI tools",
        ],
        ["bash(1) REDIRECTION section", "grep(1), sort(1), uniq(1), tee(1)"],
        [
            ("stdout", "Standard output stream (file descriptor 1)"),
            ("stderr", "Standard error stream (file descriptor 2)"),
            ("pipe", "Connects stdout of one process to stdin of the next"),
            ("redirect", "Send a stream to a file or another descriptor"),
            (">", "Overwrite redirect of stdout"),
            (">>", "Append redirect of stdout"),
            ("tee", "Copy stdin to stdout and to a file"),
            ("exit status", "Numeric result of the last command; 0 usually means success"),
        ],
        """## Instruction

### Small tools, composed

Unix philosophy: each filter does one job. `grep` selects lines, `sort` orders, `uniq` collapses duplicates, `wc` counts. Pipes connect them into investigations.

### Redirection hazards

`>` overwrites. On production logs this is catastrophic. In class, only redirect into `/opt/lab-classroom/class17/`.

### stderr matters

Failures often print on stderr. Use `cmd >out 2>err` or merge deliberately with `2>&1` — and document which you used in the workbook.

### Worked example

Create a sample log, filter ERROR lines, count them, and save with tee under the disposable lab path.

Practice reading exit status with `echo $?` after a successful grep and after a failing grep so you learn to trust pipelines in scripts without ignoring failures. Prefer readable multi-line pipelines over clever one-liners when you are learning.
""",
        """```text
command → stdout → pipe → filter → tee → file + terminal
         ↘ stderr (separate unless merged)
```""",
        """## Guided lab

Scope: disposable `/opt/lab-classroom/class17` only. Confirm with `realpath` before destructive cleanup.

```bash
mkdir -p /opt/lab-classroom/class17
printf 'INFO ok\\nERROR disk\\nINFO ok\\nERROR net\\nWARN slow\\n' > /opt/lab-classroom/class17/sample.log
# Capture matches while preserving a copy for evidence
grep ERROR /opt/lab-classroom/class17/sample.log | tee /opt/lab-classroom/class17/errors.txt
wc -l < /opt/lab-classroom/class17/errors.txt
sort /opt/lab-classroom/class17/errors.txt | uniq -c
# Demonstrate append vs overwrite: append a note without destroying evidence
printf 'NOTE review complete\\n' >> /opt/lab-classroom/class17/errors.txt
# Optional stderr capture on a deliberate miss
grep MISSING /opt/lab-classroom/class17/sample.log 2> /opt/lab-classroom/class17/grep.err || true
```

Expected outcomes: `errors.txt` starts with two ERROR lines; `wc -l` reports at least 2 before the NOTE append; `uniq -c` shows counts; evidence files stay under class17.

Rollback: `rm -rf /opt/lab-classroom/class17` after `realpath` confirms the path.
""",
        ["errors.txt contains ERROR lines", "wc reports 2 before append", "uniq -c shows counts", "NOTE appended with >>"],
        ["grep -c ERROR /opt/lab-classroom/class17/sample.log", "test -f /opt/lab-classroom/class17/errors.txt", "wc -l /opt/lab-classroom/class17/errors.txt", "grep -q NOTE /opt/lab-classroom/class17/errors.txt"],
        [
            ("Empty pipe output", "Pattern mismatch", "Check sample content; use grep -n"),
            ("Overwrote a file", "Used > instead of >>", "Restore from sample; prefer >> for append labs"),
            ("Lost error messages", "stderr not captured", "Redirect 2> or merge 2>&1 deliberately"),
        ],
        "Never redirect onto production logs. Avoid `curl | sh`. Keep pipelines readable; prefer tee for evidence. Prefer >> when appending lab notes.",
        "Remove only /opt/lab-classroom/class17 with rm -rf after confirming realpath. Recreate sample.log from the printf recipe if you still need evidence.",
        """### Explain
Pipes vs redirects and why > is dangerous.

### Simplify
Assembly line for text.

### Example
Counting ERROR lines from a service log.

### Weak spot
stderr vs stdout.

### Retry
Draw the stream diagram from memory.
""",
        "Build a three-stage pipeline on a lab file that filters, sorts, and counts unique lines; save evidence with tee under /opt/lab-classroom/class17.",
        [
            "Which operator connects stdout to the next command's stdin?",
            "What is the difference between > and >>?",
            "Which stream usually carries error messages?",
            "What does tee do?",
            "Why keep redirects under /opt/lab-classroom?",
            "Name one filter used with pipes in this class",
        ],
        [
            "The pipe |",
            "> overwrites; >> appends",
            "stderr",
            "Writes stdin both to a file and to stdout",
            "To avoid destroying production files",
            "grep, sort, uniq, or wc",
        ],
        "Demo a growing pipeline live. Show a mistaken > overwrite on a lab file, then fix with recreation—never on real logs.",
        ["bash(1) REDIRECTION section (local man page)", "grep(1) Linux man page (local)", "tee(1) Linux man page (local)"],
        "bash or POSIX sh with coreutils.",
        [{
            "command": "rm -rf /opt/lab-classroom/class17",
            "warning": "Deletes lab pipeline evidence directory",
            "prerequisites": "Path confirmed",
            "verification": "test ! -e /opt/lab-classroom/class17",
            "backup": "Copy errors.txt if keeping evidence",
            "rollback": "Recreate lab files from printf sample",
            "failure_mode": "Wrong path deletes unrelated data",
        }],
    )


CURATED: dict[int, Any] = {
    16: lesson_filesystem,
    17: lesson_pipes,
    18: lambda: _shift(lesson_16(), 18, "Users, Groups, Permissions, and Least Privilege"),
    19: lambda: _shift(lesson_17(), 19, "Processes, Signals, and systemd"),
    20: lambda: _shift(lesson_18(), 20, "Logs and journalctl"),
    21: lambda: _shift(lesson_19(), 21, "SSH Keys and Safe Hardening"),
}


def get_curated(class_id: int) -> dict[str, Any]:
    if class_id not in CURATED:
        raise KeyError(f"No curated lesson for class {class_id}")
    return CURATED[class_id]()

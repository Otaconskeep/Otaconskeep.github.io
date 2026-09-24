# Class 19: Processes, Signals, and systemd

**Learning objective:** Distinguish programs, processes, threads, jobs, services, and systemd units; Inspect process identifiers, parent relationships, users, states, and command lines; Explain how Linux delivers signals and why signal handling depends on the target process; Use SIGHUP, SIGTERM, SIGSTOP, SIGCONT, and SIGKILL against a verified lab-owned process; Explain why SIGTERM is normally preferable to SIGKILL; Relate a systemd service unit to its main process and cgroup; Use read-only systemctl queries to inspect service state and selected unit properties; Recognize PID reuse and avoid signaling a process based only on a stale PID file; Clean up the laboratory without altering persistent files outside the approved directory
**Bloom level:** Understand / Apply
**Track:** Linux Systems Administration · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** medium
**Build output:** Develop a practical mental model of Linux processes, process states, signals, service supervision, and the relationship between systemd units, cgroups, and operating-system processes. The lab safely creates and controls only a purpose-built process whose persistent files remain under /opt/lab-classroom/class19/.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### supported
Linux distributions using systemd as PID 1 for the complete lesson
Bash with procps-ng and common GNU userland tools for the supplied commands
Virtual machines and physical Linux hosts where the learner may query the system manager

### limitations
Containers, chroots, compatibility layers, and minimal images may not expose systemd as PID 1.
BusyBox implementations can use different ps options and may require equivalent inspection commands.
The proc filesystem must be mounted and accessible for proc-based inspection.
Security modules, container namespaces, or restricted proc mount options may hide process details.
The selected running service and its property values are host-specific; the lesson does not assume a particular service name or result.

## Learning objective

- Distinguish programs, processes, threads, jobs, services, and systemd units
- Inspect process identifiers, parent relationships, users, states, and command lines
- Explain how Linux delivers signals and why signal handling depends on the target process
- Use SIGHUP, SIGTERM, SIGSTOP, SIGCONT, and SIGKILL against a verified lab-owned process
- Explain why SIGTERM is normally preferable to SIGKILL
- Relate a systemd service unit to its main process and cgroup
- Use read-only systemctl queries to inspect service state and selected unit properties
- Recognize PID reuse and avoid signaling a process based only on a stale PID file
- Clean up the laboratory without altering persistent files outside the approved directory

## Why this matters

Develop a practical mental model of Linux processes, process states, signals, service supervision, and the relationship between systemd units, cgroups, and operating-system processes. The lab safely creates and controls only a purpose-built process whose persistent files remain under /opt/lab-classroom/class19/.

## Prerequisites

- Comfort using a Linux shell and basic command-line utilities
- Ability to use sudo for creating the class laboratory directory
- Basic understanding of files, users, permissions, and shell scripts
- A Linux host or virtual machine using systemd as PID 1
- Completion of introductory Linux filesystem and shell classes

## Required reading

- Read the local manual pages with: man ps, man kill, man 7 signal, man systemctl, and man systemd.service
- Review the systemd documentation section describing unit states and service process tracking
- Review the proc filesystem documentation for process-specific directories such as /proc/PID/

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Program | Executable instructions stored in a file or supplied to an interpreter. A program becomes a process when it is executed. |
| Process | A running instance of a program with a process ID, credentials, address space, open file descriptors, and execution state. |
| PID | A process identifier assigned by the kernel. PIDs are finite and can be reused after a process exits. |
| PPID | The process identifier of a process's parent. |
| Thread | An execution context within a process. Threads normally share the process address space and other resources. |
| Job | A shell-managed command or pipeline associated with the current shell session and identified by a shell job number. |
| Signal | An asynchronous notification sent to a process or thread. A signal may invoke a handler, be ignored, stop execution, continue execution, or terminate the process. |
| Signal disposition | The action associated with a signal: the default action, an application-defined handler, or ignore where permitted. |
| Zombie | A process that has exited but still has a process-table entry because its parent has not collected the exit status. |
| Orphan | A process whose parent has exited. It is subsequently adopted by an appropriate subreaper, commonly the service manager or another designated process. |
| Unit | An object managed by systemd, such as a service, socket, timer, mount, path, target, or device. |
| Cgroup | A kernel control-group hierarchy used to organize processes and apply accounting, delegation, and resource controls. systemd places managed services into cgroups. |
| MainPID | The process systemd currently considers the main process of a service, when the service type and runtime state provide one. |

## Instruction

A program is passive code, while a process is a live kernel-managed execution context. Each process has a PID, a parent relationship, credentials, memory mappings, open file descriptors, and one or more threads. Shell job identifiers such as %1 are not kernel PIDs; they are conveniences maintained by a particular interactive shell. Process state letters reported by ps summarize conditions such as runnable, sleeping, stopped, or zombie, but they are observations that can change immediately after inspection.

Signals are numbered notifications with symbolic names. The kill command is named for historical reasons and can send signals that do not terminate a process. SIGTERM requests orderly termination and may be caught so an application can close files, release locks, notify peers, and remove temporary state. SIGHUP traditionally reports terminal disconnection, although many daemons interpret it as a request to reload configuration. SIGSTOP always suspends execution and cannot be caught or ignored; SIGCONT resumes a stopped process. SIGKILL causes kernel-enforced termination and cannot be caught, blocked, or ignored. SIGKILL is therefore a last resort: it prevents application cleanup and can leave incomplete transactions or stale external state even though the kernel reclaims process-local resources.

A PID file is not proof of identity. After a process exits, its PID can eventually be assigned to an unrelated process. Before signaling a PID read from a file, inspect the current owner and command line and, where practical, use a service manager that tracks the process through cgroups. Permissions also matter: an unprivileged user generally may signal only processes permitted by kernel credential checks. Elevated privileges should not be used merely to bypass uncertainty about process identity.

systemd is commonly PID 1 on modern Linux distributions. It manages units rather than treating every PID as an independent service. A service unit can have a main process, helper processes, and descendants grouped in a cgroup. This allows systemd to reason about the service as a collection instead of trusting only a PID file. Unit state and process state are related but not identical: a service may be activating while a process initializes, active with several processes, failed after an unsuccessful exit, or inactive with no remaining processes. systemctl status provides a human-oriented summary, while systemctl show exposes machine-readable properties such as ActiveState, SubState, MainPID, ControlGroup, and FragmentPath. Reading these properties is safe, but changing or restarting production units requires a separate change plan. In this class, systemd inspection is read-only; all processes created by the lab are ordinary user processes, and all persistent lab artifacts stay inside the approved class directory.

## Architecture

### components
The Linux kernel creates processes, schedules threads, enforces credentials, and delivers signals.
The proc filesystem exposes live process information used by tools such as ps.
The interactive shell starts commands, tracks shell jobs, and exposes the PID of a newly backgrounded command.
The lab worker installs signal handlers and records observable events in its own laboratory directory.
systemd, when running as PID 1, manages units and organizes service processes into cgroups.
systemctl reads unit state and properties through the systemd manager interface.

### process_flow
The shell starts worker.sh and records the resulting PID.
The kernel schedules the worker and its child sleep commands.
The administrator verifies the live PID's owner and command line.
A signal is requested with kill and delivered by the kernel subject to credential checks.
Catchable signals invoke the worker's Bash trap when the shell can process it.
Uncatchable stop, continue, and termination actions are applied by the kernel.
Read-only systemctl commands separately inspect an existing system-managed service and its cgroup.

### boundaries
The lab does not install, edit, enable, disable, start, stop, or restart any systemd unit. Persistent creation, logging, PID files, and cleanup are restricted to /opt/lab-classroom/class19/.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Under /opt/lab-classroom/class19/, create a text file that maps the common ps state letters R, S, D, T, and Z to their meanings.
Extend a copy of worker.sh under the same directory so SIGUSR1 records a one-line diagnostic message without terminating.
Run the extended worker, verify its identity, send SIGUSR1, and document the observed result under /opt/lab-classroom/class19/.
Choose one existing service and record the read-only values of Id, ActiveState, SubState, MainPID, ControlGroup, and FragmentPath in a file under the lab directory.
Write a short incident procedure under the lab directory describing identity verification, graceful termination, bounded waiting, escalation criteria, and post-action verification.

## Feynman teach-back

### prompt
Explain the lesson to someone who knows only that applications run on Linux.

### model_explanation
A program is a recipe stored on disk, and a process is a cook currently following that recipe. The kernel gives each cook a temporary number called a PID. A signal is a short instruction delivered through the kernel. SIGTERM politely asks the cook to finish safely, SIGSTOP freezes the cook, SIGCONT allows work to continue, and SIGKILL removes the cook immediately without allowing cleanup. Because PID numbers can be reused, you must check who currently owns a number before sending an instruction. systemd acts like a supervisor: it tracks services as managed units and groups their related processes together, rather than relying only on one number written in a file.

### self_check
Can you explain why a stale PID file could cause harm?
Can you explain why SIGKILL is not a stronger version of graceful shutdown?
Can you distinguish a shell job number from a kernel PID?
Can you describe how a systemd service can contain more than one process?

## Retrieval check

1. 1. What is the difference between a program and a process?
2. 2. Why is a PID read from a file insufficient proof of process identity?
3. 3. Which signal should normally be tried first when requesting an orderly process shutdown?
4. 4. Which two signals cannot be caught, blocked, or ignored?
5. 5. What does a T in the ps STAT column generally indicate?
6. 6. Why can SIGKILL create operational problems even though the kernel reclaims the terminated process's memory?
7. 7. What is the difference between a shell job identifier such as %1 and a PID?
8. 8. How does a systemd service unit relate to a cgroup?
9. 9. Which systemctl subcommand is useful for retrieving machine-readable unit properties?
10. 10. Why might a Bash signal trap run shortly after the signal rather than at the exact instant it is sent?

## Guided lab

### name
Observe and control a verified lab process

### scope
Only the lab-owned worker process may be signaled. Persistent filesystem changes are limited to /opt/lab-classroom/class19/.

### steps
### step
1

### instruction
Create the approved laboratory directory and assign it to the current user. Verify the resolved path before continuing.

### commands
export LAB=/opt/lab-classroom/class19
sudo install -d -o "$(id -u)" -g "$(id -g)" -m 0750 "$LAB"
test "$(realpath "$LAB")" = "/opt/lab-classroom/class19"
printf 'Laboratory path: %s\n' "$(realpath "$LAB")"
### step
2

### instruction
Create a worker that records its PID, reports SIGHUP, exits cleanly on SIGTERM or SIGINT, and writes a periodic heartbeat.

### commands
cat > "$LAB/worker.sh" <<'EOF'
#!/usr/bin/env bash
set -u
LAB=/opt/lab-classroom/class19
printf '%s\n' "$$" > "$LAB/worker.pid"
trap 'printf "%s received SIGHUP\n" "$(date --iso-8601=seconds)" >> "$LAB/events.log"' HUP
trap 'printf "%s received termination request\n" "$(date --iso-8601=seconds)" >> "$LAB/events.log"; exit 0' TERM INT
printf '%s started PID=%s PPID=%s\n' "$(date --iso-8601=seconds)" "$$" "$PPID" >> "$LAB/events.log"
while :; do
  printf '%s heartbeat PID=%s\n' "$(date --iso-8601=seconds)" "$$" >> "$LAB/heartbeat.log"
  sleep 2
done
EOF
chmod u=rwx,go= "$LAB/worker.sh"
: > "$LAB/events.log"
: > "$LAB/heartbeat.log"
### step
3

### instruction
Start the worker in the background, save the shell-reported PID, and confirm that it matches the PID written by the worker.

### commands
"$LAB/worker.sh" > "$LAB/stdout.log" 2> "$LAB/stderr.log" &
printf '%s\n' "$!" > "$LAB/launcher.pid"
sleep 1
test "$(cat "$LAB/launcher.pid")" = "$(cat "$LAB/worker.pid")"
PID=$(cat "$LAB/worker.pid"); ps -o pid=,ppid=,user=,stat=,etime=,args= -p "$PID"
### step
4

### instruction
Inspect the process using both ps and its proc directory. These observations are snapshots and may change immediately.

### commands
PID=$(cat "$LAB/worker.pid"); test -d "/proc/$PID"
PID=$(cat "$LAB/worker.pid"); ps -o pid,ppid,user,stat,lstart,etime,args -p "$PID"
PID=$(cat "$LAB/worker.pid"); printf 'Executable: '; readlink "/proc/$PID/exe"
PID=$(cat "$LAB/worker.pid"); printf 'Command line: '; tr '\0' ' ' < "/proc/$PID/cmdline"; printf '\n'
PID=$(cat "$LAB/worker.pid"); grep -E '^(Name|State|Pid|PPid|Uid|Gid):' "/proc/$PID/status"
### step
5

### instruction
Verify identity, send SIGHUP, and confirm that the process handled it without exiting.

### commands
PID=$(cat "$LAB/worker.pid"); ps -o pid=,user=,args= -p "$PID"
PID=$(cat "$LAB/worker.pid"); kill -HUP "$PID"
sleep 3
PID=$(cat "$LAB/worker.pid"); ps -o pid=,stat=,args= -p "$PID"
tail -n 5 "$LAB/events.log"
### step
6

### instruction
Suspend and resume the verified worker. A stopped state is normally represented by T in the ps STAT column.

### commands
PID=$(cat "$LAB/worker.pid"); ps -o pid=,user=,args= -p "$PID"
PID=$(cat "$LAB/worker.pid"); kill -STOP "$PID"
sleep 1
PID=$(cat "$LAB/worker.pid"); ps -o pid=,stat=,args= -p "$PID"
PID=$(cat "$LAB/worker.pid"); kill -CONT "$PID"
sleep 3
PID=$(cat "$LAB/worker.pid"); ps -o pid=,stat=,args= -p "$PID"
tail -n 3 "$LAB/heartbeat.log"
### step
7

### instruction
Request an orderly shutdown with SIGTERM and confirm the worker recorded its cleanup path.

### commands
PID=$(cat "$LAB/worker.pid"); ps -o pid=,user=,args= -p "$PID"
PID=$(cat "$LAB/worker.pid"); kill -TERM "$PID"
PID=$(cat "$LAB/worker.pid"); for attempt in 1 2 3 4 5; do kill -0 "$PID" 2>/dev/null || break; sleep 1; done
PID=$(cat "$LAB/worker.pid"); if kill -0 "$PID" 2>/dev/null; then printf 'Worker is still present; investigate before escalating.\n'; else printf 'Worker exited.\n'; fi
tail -n 5 "$LAB/events.log"
### step
8

### instruction
Start a fresh worker solely to compare SIGKILL with orderly termination. Verify its identity immediately before signaling it. The process cannot record a SIGKILL handler because SIGKILL is not catchable.

### commands
"$LAB/worker.sh" > "$LAB/stdout-kill.log" 2> "$LAB/stderr-kill.log" &
printf '%s\n' "$!" > "$LAB/kill-demo.pid"
sleep 1
PID=$(cat "$LAB/kill-demo.pid"); ps -o pid=,user=,args= -p "$PID"
PID=$(cat "$LAB/kill-demo.pid"); kill -KILL "$PID"
PID=$(cat "$LAB/kill-demo.pid"); wait "$PID" 2>/dev/null || true
PID=$(cat "$LAB/kill-demo.pid"); if kill -0 "$PID" 2>/dev/null; then printf 'Unexpected: process remains.\n'; else printf 'SIGKILL demonstration process is gone.\n'; fi
tail -n 5 "$LAB/events.log"
### step
9

### instruction
Inspect one currently running systemd service without changing it. Skip this step if the environment does not use systemd as PID 1.

### commands
test "$(ps -p 1 -o comm=)" = "systemd" && printf 'systemd is PID 1.\n' || printf 'This environment does not expose systemd as PID 1.\n'
UNIT=$(systemctl list-units --type=service --state=running --no-legend --no-pager | awk 'NR==1 {print $1}'); printf 'Selected unit: %s\n' "$UNIT"
UNIT=$(systemctl list-units --type=service --state=running --no-legend --no-pager | awk 'NR==1 {print $1}'); test -n "$UNIT" && systemctl show "$UNIT" --property=Id,LoadState,ActiveState,SubState,MainPID,ControlGroup,FragmentPath --no-pager
UNIT=$(systemctl list-units --type=service --state=running --no-legend --no-pager | awk 'NR==1 {print $1}'); test -n "$UNIT" && systemctl status "$UNIT" --no-pager --lines=5

## Expected results

- The laboratory directory resolves exactly to /opt/lab-classroom/class19.
- The worker's PID file and the launching shell's recorded PID contain the same value.
- ps and /proc expose the worker's PID, parent, owner, state, and command line.
- After SIGHUP, the worker remains present and events.log contains a SIGHUP entry.
- After SIGSTOP, ps reports a stopped state containing T; after SIGCONT, heartbeat entries resume.
- After SIGTERM, the first worker exits and events.log contains a termination-request entry.
- After SIGKILL, the demonstration worker exits without writing a signal-handler message for SIGKILL.
- On a systemd host, systemctl show reports properties for an existing running service without changing its state.

## Verification checkpoints

- [ ] Run: test "$(realpath /opt/lab-classroom/class19)" = "/opt/lab-classroom/class19" && echo PASS
- [ ] Run: grep -q 'received SIGHUP' /opt/lab-classroom/class19/events.log && echo PASS
- [ ] Run: grep -q 'received termination request' /opt/lab-classroom/class19/events.log && echo PASS
- [ ] Run: test -s /opt/lab-classroom/class19/heartbeat.log && echo PASS
- [ ] Run: PID=$(cat /opt/lab-classroom/class19/kill-demo.pid); ! kill -0 "$PID" 2>/dev/null && echo PASS
- [ ] On a systemd host, run: systemctl is-system-running --wait; note that degraded can be a valid existing host condition and is not caused by this read-only lab.
- [ ] Confirm that no systemd unit was started, stopped, restarted, enabled, disabled, or edited during the exercise.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Creating /opt/lab-classroom/class19 fails with permission denied. | The current account cannot create directories under /opt or does not have authorized sudo access. | Use an account authorized for the lab host and run only the provided install command with sudo. Do not redirect privileged output to another location. |
| The launcher PID and worker PID do not match. | The worker exited early, the wrong file was read, or an earlier lab instance left stale files. | Inspect stdout.log, stderr.log, and events.log. Confirm no previous lab worker remains, then recreate the files and start one worker. |
| SIGHUP does not appear in events.log immediately. | Bash may process the trap after the current external sleep command returns. | Wait at least three seconds, verify the process still has the expected command line, and inspect events.log again. |
| The process remains briefly after SIGTERM. | The shell is waiting for its current sleep child before running the trap, or the inspected PID no longer represents the intended worker. | Wait through the bounded verification loop and inspect the PID's owner and command line again. Do not escalate until identity has been revalidated. |
| ps reports no process for the PID in worker.pid. | The worker has already exited or failed during startup. | Inspect stderr.log and events.log, correct any local script error, and restart only the lab worker. |
| systemctl reports that the system was not booted with systemd. | The lesson is running in a container, subsystem, chroot, or distribution that does not expose systemd as PID 1. | Complete the process and signal sections, then perform the systemd inspection on a virtual machine or host where systemd is PID 1. |
| No running service is selected for inspection. | The system manager is unavailable or there are no visible running service units in the environment. | Verify that PID 1 is systemd and that the account may query the system manager. Do not start a service solely to satisfy this lab. |
| systemctl status returns a nonzero result even though systemctl show produced output. | The unit changed state between queries or its current state maps to a nonzero status result. | Treat the commands as separate snapshots. Re-run the read-only list and show queries and record the observed state. |

## Security considerations

### principles
Verify process identity, owner, and command line immediately before sending a signal.
Treat PID files as hints rather than durable identity because PIDs can be reused.
Signal only processes created for the lab; never experiment on authentication, storage, networking, monitoring, or orchestration services.
Prefer SIGTERM and bounded waiting so applications have an opportunity to clean up.
Reserve SIGKILL for confirmed, unresponsive processes after the consequences are understood.
Do not use elevated privileges to signal a process merely because normal permission checks denied the request.
Use systemctl show for script-friendly inspection and remember that status output is intended primarily for humans.
Consider cgroup membership when diagnosing services with multiple processes.

### systemd_notes
Production service actions can interrupt dependent applications and trigger restart policies. This class intentionally performs only read operations against systemd. Service changes should be reviewed separately with dependency analysis, maintenance planning, log monitoring, and a tested rollback procedure.

### data_boundary
All persistent lab artifacts are confined to /opt/lab-classroom/class19/. The lab reads process and unit metadata from the operating system but does not modify service definitions or other persistent host paths.

## Rollback

### process_cleanup
Check whether a recorded PID still exists and verify that its command line points to /opt/lab-classroom/class19/worker.sh.
Send SIGTERM only to a verified surviving lab worker and wait for it to exit.
If a verified lab worker remains unresponsive, review the controlled SIGKILL warning before escalation.

### artifact_cleanup
Set the exact path with: export LAB=/opt/lab-classroom/class19
Verify it with: test "$(realpath "$LAB")" = "/opt/lab-classroom/class19"
After preserving any desired notes, remove generated entries only with: find "$LAB" -mindepth 1 -maxdepth 1 -delete
Leave the class19 directory itself in place for later lessons unless the lab administrator directs otherwise.

### systemd_rollback
No systemd rollback is required because the lab performs no systemd mutation.

## Video narration notes

Begin by showing that a program on disk is different from a running process. Open ps and identify PID, PPID, user, state, elapsed time, and command line. Emphasize that every display is only a snapshot. Introduce signals as kernel-delivered notifications rather than assuming that kill always means immediate termination. Walk through the lab worker and point out its SIGHUP and SIGTERM traps. Start the worker, compare the shell-reported PID with the worker's own PID, and inspect the same process through ps and the proc filesystem. Before every signal, pause and verify the owner and command line to establish the habit of guarding against stale PID files and PID reuse.

Send SIGHUP and show that the process records the event but remains alive. Stop it with SIGSTOP, observe the T state, and resume it with SIGCONT. Then send SIGTERM and show the termination entry written by the handler. Contrast that with the second worker terminated by SIGKILL: it disappears, but no SIGKILL handler entry can exist because the signal cannot be caught. Explain that immediate termination may prevent application cleanup even though the kernel reclaims memory and file descriptors.

Finish by moving from individual processes to service supervision. Confirm whether systemd is PID 1, choose an already running service, and inspect it without changing it. Compare ActiveState and SubState with MainPID and ControlGroup. Explain that a service is a managed unit that may contain multiple related processes, and that cgroup tracking is more reliable than treating a PID file as permanent identity. Close with the operational rule: verify identity, request graceful shutdown, wait for a defined interval, investigate, and escalate only when the consequences are understood.

## References

- Linux man-pages signal(7): https://man7.org/linux/man-pages/man7/signal.7.html
- Linux man-pages kill(2): https://man7.org/linux/man-pages/man2/kill.2.html
- Linux man-pages proc_pid_status(5): https://man7.org/linux/man-pages/man5/proc_pid_status.5.html
- procps-ng ps(1): https://man7.org/linux/man-pages/man1/ps.1.html
- systemctl manual: https://www.freedesktop.org/software/systemd/man/latest/systemctl.html
- systemd.service manual: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
- systemd unit manual: https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html
- systemd control group delegation documentation: https://systemd.io/CGROUP_DELEGATION/

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

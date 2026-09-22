# Class 20 — Logs and journalctl

**Learning objective:** Explain the relationship between applications, systemd units, systemd-journald, and journalctl.; Read events from the current boot and inspect the available boot history.; Filter journal records by unit, time, priority, and field.; Recognize common journal output formats and export records for later analysis.; Distinguish volatile journal storage from persistent journal storage.; Verify conclusions by checking timestamps, boot identifiers, priorities, and unit metadata.; Handle journal access and exported log files without unnecessarily exposing sensitive data.
**Bloom level:** Understand / Apply
**Track:** Linux Systems Administration · **Difficulty:** beginner · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach learners how systemd-journald collects Linux events and how journalctl can retrieve, filter, format, export, and interpret those events without modifying system services or journal configuration.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-20
**Compatibility:** ### supported
Linux distributions using systemd and systemd-journald
Recent systemd releases that support current-boot, unit, priority, JSON, disk-usage, and boot-list queries
Python 3 for the optional structured parsing step

### limitations
Minimal containers may not run systemd or expose a host journal.
Journal retention and access policy vary by distribution and host configuration.
Older systemd releases may render timestamps or fields differently.
The find command used for the manifest expects GNU find features commonly available on Linux.
Previous boot records are unavailable when they were not retained or are not accessible.

## Learning objective

- Explain the relationship between applications, systemd units, systemd-journald, and journalctl.
- Read events from the current boot and inspect the available boot history.
- Filter journal records by unit, time, priority, and field.
- Recognize common journal output formats and export records for later analysis.
- Distinguish volatile journal storage from persistent journal storage.
- Verify conclusions by checking timestamps, boot identifiers, priorities, and unit metadata.
- Handle journal access and exported log files without unnecessarily exposing sensitive data.

## Why this matters

Teach learners how systemd-journald collects Linux events and how journalctl can retrieve, filter, format, export, and interpret those events without modifying system services or journal configuration.

## Prerequisites

- Basic Linux command-line navigation
- Familiarity with services and systemd units
- A Linux host or virtual machine using systemd and systemd-journald
- Permission to read at least the current user's journal entries
- An existing writable directory at /opt/lab-classroom/class20/

## Required reading

- Read the local journalctl manual with: man journalctl
- Read the local systemd-journald manual with: man systemd-journald
- Read the local journald configuration manual with: man journald.conf
- Review the local systemd journal fields reference with: man systemd.journal-fields

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| journal | The structured event store managed by systemd-journald. |
| systemd-journald | The system service that receives, enriches, stores, and forwards journal records. |
| journalctl | The command-line tool used to query and display records from the systemd journal. |
| unit | A systemd-managed object, such as a service, socket, mount, timer, or target, that may be associated with journal records. |
| boot ID | A unique identifier assigned to one system boot, allowing journal records to be grouped by boot. |
| priority | The syslog severity associated with a record, ranging numerically from 0 for emergency through 7 for debug. |
| field match | A journal query that selects records whose structured metadata contains a particular field and value. |
| cursor | An opaque identifier that marks a specific location in the journal and can be used to resume reading. |
| volatile journal | Journal data kept under runtime storage and normally lost when the system reboots. |
| persistent journal | Journal data stored on persistent local storage so that records can remain available across boots. |
| vacuum | A journal maintenance operation that removes archived journal data according to a size, age, or file-count limit. |

## Instruction

Linux troubleshooting depends on evidence, and the system journal is one of the most important evidence sources on a systemd-based host. systemd-journald receives records from several sources, including service standard output and standard error, native journal clients, kernel messages, and compatible logging interfaces. It stores more than a line of text: a record can also contain timestamps, process identifiers, user identifiers, executable paths, systemd unit names, boot identifiers, transport information, and priority. journalctl is the query tool for this structured data.

Running journalctl without filters may produce far more information than needed. A good investigation narrows scope deliberately. Start with the relevant boot by using -b. Restrict the source with -u followed by a unit name. Restrict time with --since and --until. Restrict severity with -p. For example, -p warning includes warning and all more severe priorities, not only records labeled warning. The standard numeric priority order is 0 emergency, 1 alert, 2 critical, 3 error, 4 warning, 5 notice, 6 informational, and 7 debug. Lower numbers represent greater severity.

Time context matters. A failure seen today may belong to the current boot, while a startup failure from yesterday may be stored under an earlier boot. journalctl --list-boots shows known boots when the required data exists. The current boot can be selected with -b 0 or simply -b. Previous boots can commonly be addressed with negative offsets such as -b -1, but previous records will not be available if the host only keeps a volatile journal or if retention has removed them.

Output format should match the task. Human-readable formats such as short-iso make chronological review convenient. Verbose output exposes all fields associated with each selected record. JSON output is useful for scripts because each record is represented as structured data rather than an ambiguous display line. Exported records can contain hostnames, usernames, process arguments, internal addresses, authentication events, application data, or secrets accidentally written by software. Treat exported files as sensitive evidence and use restrictive permissions.

The journal is not automatically proof of root cause. A warning near a failure may be unrelated, an application may omit useful details, and clocks can be inaccurate. Correlate timestamps, units, process identifiers, boot IDs, and surrounding events. Begin with a narrow hypothesis, broaden the time window if necessary, and record the exact query used. Avoid jumping directly to destructive maintenance operations. Reading, filtering, and exporting evidence should come before retention changes or journal cleanup.

Access differs among distributions. An unprivileged user may see only records associated with that user, while administrative access may expose the system journal. An empty result can therefore mean that no records matched, that old records were not retained, or that the current account cannot read them. Distinguish these possibilities before concluding that a service produced no logs.

## Architecture

### flow
The kernel, services, applications, and compatible logging interfaces emit events.
systemd-journald receives events and adds structured metadata.
Journal records are stored in volatile or persistent storage according to host configuration.
journalctl reads journal files and applies boot, unit, time, priority, and field filters.
Administrators inspect terminal output or export selected records into protected evidence files.

### key_components
### component
Event producers

### role
Kernel and user-space processes that emit messages.
### component
systemd-journald

### role
Collects records, attaches metadata, manages storage, and may forward events.
### component
Journal storage

### role
Maintains indexed binary journal records subject to access and retention policy.
### component
journalctl

### role
Queries records and renders them in human-readable or machine-readable formats.
### component
Lab evidence directory

### role
Stores only the learner's exported, read-only observations under /opt/lab-classroom/class20/.

### query_model
A useful query combines a time or boot boundary with one or more source and severity selectors. The result should then be inspected in a format appropriate to either human review or machine processing.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Choose one service visible on the lab host and export its current-boot records to /opt/lab-classroom/class20/homework-unit.log using journalctl -b -u with an ISO-like output format.
Create /opt/lab-classroom/class20/homework-notes.txt describing the selected service, the exact query, the visible time range, and any access or retention limitations.
Export records from the last 15 minutes to /opt/lab-classroom/class20/homework-last-15-minutes.log using --since and a human-readable relative time expression.
Compare short-iso, verbose, and JSON output for one recent record, then document which format is best for interactive review and which is best for scripting.
Explain in homework-notes.txt why an empty query result cannot by itself prove that an event never occurred.

## Feynman teach-back

### prompt
Explain the journal to a new administrator as if it were a searchable event notebook. Describe who writes events, who stores them, how metadata makes them searchable, and how journalctl selects a useful subset.

### model_explanation
Programs and the kernel produce events. systemd-journald collects those events and stores each one with useful labels such as time, boot, process, unit, and severity. journalctl does not create the historical event; it asks the journal to show records matching a query. A good query first selects the relevant boot or time window, then narrows by source or severity. Because retention and permissions affect what can be seen, no output does not always mean no event occurred.

### self_check
If the explanation cannot distinguish collection by systemd-journald from querying by journalctl, review the architecture before continuing.

## Retrieval check

1. 1. Which component collects and stores structured system journal records?
2. 2. What does journalctl -b select?
3. 3. What does journalctl -p warning include besides warning records?
4. 4. Why might journalctl --list-boots show only the current boot?
5. 5. What is the practical advantage of journalctl -o json for automation?
6. 6. Name three useful ways to narrow a journal query.
7. 7. Does an empty unit query prove that the service emitted no records?
8. 8. Why should exported journal records be protected with restrictive permissions?
9. 9. What is the difference between volatile and persistent journal storage?
10. 10. Why should an administrator correlate multiple fields and surrounding events before declaring a root cause?

## Guided lab

### name
Build a Read-Only Journal Evidence Set

### constraints
Run all commands from a single shell session.
Do not change journal configuration, restart services, rotate journals, or remove journal data.
All files created or changed by this lab must remain under /opt/lab-classroom/class20/.
The journal commands in this lab are read-only; shell redirection creates only the specified evidence files.

### steps
### step
1

### instruction
Confirm that the classroom directory already exists, is the expected path, and is writable. Stop if any check fails.

### command
cd /opt/lab-classroom/class20/ && test "$(pwd -P)" = "/opt/lab-classroom/class20" && test -w . && printf 'Lab directory verified: %s\n' "$(pwd -P)"
### step
2

### instruction
Set a restrictive file-creation mask for this shell so exported logs are not broadly readable.

### command
umask 077
### step
3

### instruction
Record the boots known to the local journal.

### command
journalctl --list-boots --no-pager > /opt/lab-classroom/class20/boots.txt
### step
4

### instruction
Export the latest 100 records from the current boot in an ISO-like timestamp format.

### command
journalctl -b -n 100 --no-pager -o short-iso > /opt/lab-classroom/class20/recent-current-boot.log
### step
5

### instruction
Export warning-and-higher-priority records from the current boot. An empty file is a valid result when no accessible records match.

### command
journalctl -b -p warning --no-pager -o short-iso > /opt/lab-classroom/class20/warnings-current-boot.log
### step
6

### instruction
Export records associated with the journal service during the current boot.

### command
journalctl -b -u systemd-journald.service --no-pager -o short-iso > /opt/lab-classroom/class20/journald-unit.log
### step
7

### instruction
Export up to 20 recent accessible records as newline-delimited JSON for structured inspection.

### command
journalctl -b -n 20 --no-pager -o json > /opt/lab-classroom/class20/recent.jsonl
### step
8

### instruction
Use Python to count the PRIORITY values present in the JSON export. Malformed or inaccessible input causes the command to fail instead of silently inventing data.

### command
python3 - <<'PY' > /opt/lab-classroom/class20/priority-summary.txt
import collections
import json
from pathlib import Path
source = Path('/opt/lab-classroom/class20/recent.jsonl')
counts = collections.Counter()
records = 0
with source.open('r', encoding='utf-8') as handle:
    for line_number, line in enumerate(handle, 1):
        if not line.strip():
            continue
        record = json.loads(line)
        records += 1
        counts[str(record.get('PRIORITY', 'missing'))] += 1
print(f'records={records}')
for priority in sorted(counts):
    print(f'priority_{priority}={counts[priority]}')
PY
### step
9

### instruction
Capture the journal's reported disk usage as contextual information without changing retention.

### command
journalctl --disk-usage > /opt/lab-classroom/class20/journal-disk-usage.txt
### step
10

### instruction
Record file names, sizes, and permissions for the evidence set.

### command
find /opt/lab-classroom/class20/ -maxdepth 1 -type f -printf '%f\t%s bytes\t%m\n' | sort > /opt/lab-classroom/class20/evidence-manifest.txt

### analysis_questions
How many boots are visible to the current account?
Which timestamps bound the current-boot sample?
Are any warning-or-higher records visible, and which units or processes produced them?
Which structured fields appear in the JSON records but not in the short-iso display?
Does the journald unit query return records, and could access restrictions explain an empty result?
Do the manifest permissions prevent access by group and other users?

## Expected results

- boots.txt contains the boot entries visible to the current account; the number of entries depends on retention and access.
- recent-current-boot.log contains no more than 100 accessible records from the current boot.
- warnings-current-boot.log contains only accessible current-boot records at warning priority or more severe, or it is empty when no records match.
- journald-unit.log contains accessible records associated with systemd-journald.service, or it is empty if no matching records are retained or visible.
- recent.jsonl contains at most 20 JSON objects, one journal record per nonempty line.
- priority-summary.txt reports the number of parsed records and counts only priorities actually found in recent.jsonl.
- journal-disk-usage.txt contains the usage reported by journalctl without changing journal retention.
- evidence-manifest.txt lists the evidence files created by the lab.
- Files created after the restrictive umask should not grant permissions to group or other users.

## Verification checkpoints

- [ ] Run: test -s /opt/lab-classroom/class20/boots.txt && echo 'Boot listing captured'; if this fails, inspect access and journal availability.
- [ ] Run: test -f /opt/lab-classroom/class20/recent-current-boot.log && echo 'Current-boot export exists'.
- [ ] Run: test -f /opt/lab-classroom/class20/warnings-current-boot.log && echo 'Priority-filtered export exists'; zero length is permitted.
- [ ] Run: python3 -c "import json, pathlib; [json.loads(line) for line in pathlib.Path('/opt/lab-classroom/class20/recent.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]; print('JSON records valid')".
- [ ] Run: cat /opt/lab-classroom/class20/priority-summary.txt and confirm that the records value equals the number of nonempty lines in recent.jsonl.
- [ ] Run: test "$(awk -F= '/^records=/{print $2}' /opt/lab-classroom/class20/priority-summary.txt)" = "$(grep -cve '^[[:space:]]*$' /opt/lab-classroom/class20/recent.jsonl)" && echo 'Record counts agree'.
- [ ] Run: find /opt/lab-classroom/class20/ -maxdepth 1 -type f -perm /077 -print and confirm that it prints no lab evidence files.
- [ ] Run: journalctl -b -n 1 --no-pager -o verbose and identify fields such as the boot ID, priority, transport, process identity, or unit when those fields are present.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The initial directory verification fails. | The classroom directory is absent, resolves to another path, or is not writable by the learner. | Stop the lab and have the lab administrator provision /opt/lab-classroom/class20/ with appropriate ownership. Do not redirect output to an alternate system path. |
| journalctl reports that no journal files were found. | The host does not use systemd-journald, journal storage is unavailable, or the environment exposes no journal to the learner. | Confirm that the machine is systemd-based and run systemctl status systemd-journald as a read-only check. Use a compatible lab VM if the host does not provide the journal. |
| Only a small number of records are visible. | The account has limited permissions, the host has a quiet current boot, or retention is limited. | Treat the visible subset as the authorized dataset. Ask an administrator to confirm access policy rather than weakening file permissions. |
| boots.txt lists only the current boot. | The journal may be volatile, older records may have been removed by retention policy, or previous boot data may not be accessible. | Document the limitation. Do not change storage or retention settings as part of this lab. |
| warnings-current-boot.log is empty. | No accessible current-boot records match warning or a more severe priority. | Verify that the unfiltered current-boot export contains records. An empty filtered result is valid and must not be treated as a command failure by itself. |
| The journald unit export is empty. | No matching records are retained, the local unit name differs, or the learner cannot access system-level records. | Run systemctl status systemd-journald as a read-only check and inspect accessible unit names with systemctl list-units --type=service --no-pager. |
| Python raises a JSON parsing error. | recent.jsonl is incomplete, was edited, or was not generated with JSON output. | Regenerate only recent.jsonl with the documented journalctl command, then rerun the parser. |
| Evidence files are readable by group or other users. | The restrictive umask was not set in the same shell before the files were created, or existing files retained broader modes. | Remove the affected evidence files using the scoped rollback procedure, set umask 077 in the active shell, and regenerate the files. |
| A query returns many unrelated messages. | The query lacks a boot, time, unit, priority, or field boundary. | Add the narrowest appropriate selector and confirm each selector independently before combining them. |

## Security considerations

### principles
Journal records may expose usernames, hostnames, network addresses, process arguments, authentication activity, application data, and operational details.
Use the least privilege required to inspect relevant records.
Do not broaden journal or evidence-file permissions merely to avoid an access-control error.
Keep exported evidence inside /opt/lab-classroom/class20/ and use a restrictive umask.
Review evidence before sharing it and redact sensitive values only in a separate copy so the original observation remains intact.
An exported record is a snapshot, not a trusted authorization decision or conclusive proof of causality.
Do not perform journal rotation, vacuuming, retention changes, or service restarts during evidence collection.

### access_note
Distribution policy determines which journal records an unprivileged user can read. Administrative access may reveal substantially more sensitive data, so it should be used only when required and authorized.

### integrity_note
Record the exact query, boot scope, and collection time when preserving evidence. Avoid editing the original exports.

## Rollback

### scope
Rollback removes only evidence files created by this lesson and does not alter the system journal.

### commands
find /opt/lab-classroom/class20/ -maxdepth 1 -type f \( -name 'boots.txt' -o -name 'recent-current-boot.log' -o -name 'warnings-current-boot.log' -o -name 'journald-unit.log' -o -name 'recent.jsonl' -o -name 'priority-summary.txt' -o -name 'journal-disk-usage.txt' -o -name 'evidence-manifest.txt' \) -delete
find /opt/lab-classroom/class20/ -maxdepth 1 -type f -printf '%f\n' | sort

### success_condition
None of the eight lesson-created evidence file names remain, and no files outside /opt/lab-classroom/class20/ were changed.

## Video narration notes

Welcome to Class 20: Logs and journalctl. In this lesson, we treat logs as evidence rather than as an endless wall of text. On a systemd host, systemd-journald collects messages from the kernel, services, applications, and compatible logging interfaces. Each journal record can include structured metadata such as a timestamp, boot ID, priority, process, and systemd unit. journalctl is the tool that queries those records.

Begin by reducing the search space. Use the current boot selector so that old events do not distract from a current incident. Add a unit filter when investigating a service. Add a time window when you know approximately when the problem occurred. Add a priority filter when you need to focus on warnings and failures, but remember that priority is only one signal. An informational message can still be operationally important, and a warning may be harmless in context.

The lab creates a protected evidence set under the class directory. We first verify the directory and set a restrictive umask. We then capture the boot list, recent current-boot records, warning-and-higher records, and records associated with the journal service. A second export uses JSON so Python can count priorities without parsing human-oriented columns. All journal operations are read-only; only the evidence files in the classroom directory are changed.

Results vary across hosts. A quiet machine may have few warnings. A system using volatile storage may expose only its current boot. An unprivileged account may see less than an administrator. These differences are part of the lesson: an empty result is an observation that must be interpreted alongside access and retention conditions.

Finish by inspecting file permissions and comparing output formats. Human-readable output is convenient for interactive review, while JSON is better for reliable automation. Preserve the original evidence, document the query that produced it, and avoid changing retention or restarting services until evidence collection is complete.

## References

- journalctl(1), local system manual page
- systemd-journald.service(8), local system manual page
- journald.conf(5), local system manual page
- systemd.journal-fields(7), local system manual page
- systemd journalctl documentation: https://www.freedesktop.org/software/systemd/man/latest/journalctl.html
- systemd-journald documentation: https://www.freedesktop.org/software/systemd/man/latest/systemd-journald.service.html
- Journal field documentation: https://www.freedesktop.org/software/systemd/man/latest/systemd.journal-fields.html

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

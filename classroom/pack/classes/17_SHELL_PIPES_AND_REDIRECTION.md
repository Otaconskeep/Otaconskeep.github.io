# Class 17: Shell Pipes and Redirection

**Learning objective:** Identify file descriptors 0, 1, and 2 as standard input, standard output, and standard error; Use a pipe to connect one command's standard output to another command's standard input; Redirect output with > and append output with >>; Redirect standard input with <; Capture standard error separately with 2>; Combine standard output and standard error with > file 2>&1; Explain why redirection order matters; Recognize that a pipeline normally reports the status of its final command; Use tee when output must be displayed or passed onward while also being saved; Verify generated files without changing anything outside the class laboratory directory
**Bloom level:** Understand / Apply
**Track:** Linux Foundations · **Difficulty:** beginner · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach students to connect commands with pipelines and deliberately route standard input, standard output, and standard error. The lesson emphasizes predictable data flow, safe file creation, redirection order, pipeline behavior, and verification techniques suitable for homelab administration.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Debian-family Linux distributions
Ubuntu Server
Rocky Linux
AlmaLinux
Fedora Server
Other Linux systems providing Bash, GNU coreutils, awk, and find

### shell
Commands are written for Bash. Basic pipes and redirections are broadly portable, while pipefail and some find formatting options are implementation-specific.

### required_commands
bash
install
printf
cat
awk
sort
uniq
tee
wc
find
test
grep
sed
rmdir

### notes
LC_ALL=C is applied to selected sort operations to make ordering independent of the host's locale. Diagnostic wording from cat can vary by implementation and locale, so verification checks that the error file is nonempty rather than requiring an exact message.

## Learning objective

- Identify file descriptors 0, 1, and 2 as standard input, standard output, and standard error
- Use a pipe to connect one command's standard output to another command's standard input
- Redirect output with > and append output with >>
- Redirect standard input with <
- Capture standard error separately with 2>
- Combine standard output and standard error with > file 2>&1
- Explain why redirection order matters
- Recognize that a pipeline normally reports the status of its final command
- Use tee when output must be displayed or passed onward while also being saved
- Verify generated files without changing anything outside the class laboratory directory

## Why this matters

Teach students to connect commands with pipelines and deliberately route standard input, standard output, and standard error. The lesson emphasizes predictable data flow, safe file creation, redirection order, pipeline behavior, and verification techniques suitable for homelab administration.

## Prerequisites

- Ability to open a terminal and run basic Linux commands
- Familiarity with paths, files, directories, and command arguments
- Basic use of cat, grep, sort, and wc
- Permission to create and manage /opt/lab-classroom/class17/

## Required reading

- Bash Reference Manual, Redirections: https://www.gnu.org/software/bash/manual/html_node/Redirections.html
- Bash Reference Manual, Pipelines: https://www.gnu.org/software/bash/manual/html_node/Pipelines.html
- Linux man-pages project, pipe(7): https://man7.org/linux/man-pages/man7/pipe.7.html
- GNU Coreutils manual, tee invocation: https://www.gnu.org/software/coreutils/manual/html_node/tee-invocation.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| standard input | File descriptor 0, commonly abbreviated stdin. It is the default stream from which a command reads input. |
| standard output | File descriptor 1, commonly abbreviated stdout. It is the default stream used for normal command results. |
| standard error | File descriptor 2, commonly abbreviated stderr. It is the default stream used for diagnostics and error messages. |
| pipe | A shell connection written as | that sends the standard output of the command on the left to the standard input of the command on the right. |
| redirection | A shell operation that changes where a command reads input or sends output. |
| truncate | To reduce an existing file to zero length before writing new content. The > operator normally has this effect. |
| append | To write new data after the existing contents of a file. The >> operator performs output redirection in append mode. |
| file descriptor | A small integer used by a process to refer to an open input or output resource. |
| tee | A command that copies standard input to standard output and to one or more files. |
| pipefail | A Bash option that makes a pipeline return a failure status when a command in the pipeline fails, rather than considering only the final command. |

## Instruction

A shell command normally begins with three open data streams. Standard input is file descriptor 0, standard output is file descriptor 1, and standard error is file descriptor 2. When a terminal launches a command, all three are generally connected to that terminal. This is why typed input reaches an interactive program and why both ordinary output and errors appear on the screen.

A pipeline changes that arrangement. In command_a | command_b, the shell connects command_a's standard output to command_b's standard input. The commands usually run concurrently, and the kernel buffers data between them. The pipe carries stdout only; stderr from command_a still goes to its existing destination unless it is redirected separately. Pipelines are best understood as data-flow graphs rather than as temporary files. Each stage should perform one clear transformation, such as selecting records, sorting them, counting duplicates, or formatting output.

Output redirection with > replaces a destination file's previous contents. For example, printf 'new\n' > file sends stdout into file and truncates an existing file first. Appending with >> preserves the old contents and writes at the end. Input redirection with < makes a file become a command's stdin. Thus wc -l < file prints only a count, while wc -l file commonly includes the filename because the file was supplied as an argument rather than through stdin.

Standard error is independent from standard output. The expression 2> errors.log redirects descriptor 2 while leaving descriptor 1 unchanged. The expression > combined.log 2>&1 first redirects stdout to combined.log and then makes stderr point to the same destination currently used by stdout. Redirections are processed from left to right. Reversing the order to 2>&1 > combined.log first copies the original stdout destination to stderr and only afterward moves stdout to the file; as a result, stderr may remain on the terminal. The compact Bash form &> file also combines both streams, but the longer > file 2>&1 form exposes the descriptor logic and is more portable across commonly encountered shells.

The tee command is useful when data must be preserved while continuing through a pipeline. In producer | tee saved.txt | consumer, tee writes a copy to saved.txt and passes the same data to consumer through stdout. Without an option, tee replaces the file; tee -a appends. Remember that redirection is performed by the shell before the command starts. This explains why elevating only a command does not automatically elevate the shell operation that opens a protected redirection target.

Exit status is another important distinction. By default, Bash reports a pipeline's status as the status of its final command. An earlier command can fail while a later command exits successfully. In Bash, set -o pipefail changes the pipeline status so that a failure in an earlier stage is not silently hidden. Scripts should also quote variable expansions, use explicit paths, validate output, and avoid assuming that an empty result means success. Before using >, confirm the destination because truncation occurs before the command produces output. For interactive protection, Bash's set -o noclobber can prevent ordinary > redirection from replacing an existing regular file, although scripts must not assume users have enabled it.

## Architecture

### stream_model
Keyboard or input file -> file descriptor 0 -> command
Command normal results -> file descriptor 1 -> terminal, file, or next pipeline stage
Command diagnostics -> file descriptor 2 -> terminal or explicitly selected destination

### pipeline_model
producer stdout -> pipe buffer -> consumer stdin

### lab_scope
/opt/lab-classroom/class17/

### key_rule
A pipe transports stdout by default; stderr remains separate unless the command or shell explicitly redirects it.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Within /opt/lab-classroom/class17/, create homework-services.csv containing at least eight records with name, state, and port fields.
Build a pipeline that extracts the state field, sorts it, counts repeated values, and writes the report to homework-state-counts.txt.
Build a second pipeline using tee that saves all active records to homework-active.csv while writing their count to homework-active-count.txt.
Create a command group that emits one normal message and one diagnostic message, then save the streams in separate homework files.
Write a short text file named homework-explanation.txt explaining why 2>&1 > file behaves differently from > file 2>&1.
Verify every homework result with test, grep, awk, wc, or diff without creating files outside /opt/lab-classroom/class17/.

## Feynman teach-back

### prompt
Explain pipes and redirection to someone who has never used a shell, without relying on the symbols alone.

### model_explanation
Imagine each command as a small machine with an input chute, a normal-output chute, and a separate warning chute. A pipe connects the normal-output chute of one machine to the input chute of the next machine. It does not automatically connect the warning chute. Redirection points a chute at a file instead of the terminal. A single greater-than sign starts the file over, two greater-than signs add to its end, and 2> redirects the warning chute. The expression > file 2>&1 points the normal chute at the file and then points the warning chute at the same place. The order matters because each connection is made from left to right.

## Retrieval check

1. 1. Which numeric file descriptors represent standard input, standard output, and standard error?
2. 2. In producer | consumer, which stream from producer is connected to consumer by default?
3. 3. What is the practical difference between > report.txt and >> report.txt?
4. 4. Why can an error still appear on the terminal after running command > output.txt?
5. 5. What does command > combined.txt 2>&1 do, and why does the order matter?
6. 6. What problem does tee solve in a pipeline?
7. 7. Why might a pipeline report success even if its first command failed?
8. 8. What does wc -l < services.csv commonly omit that wc -l services.csv commonly includes?

## Guided lab

### name
Build and inspect a service-report pipeline

### scope_rule
Every file created, replaced, or appended by this lab must be under /opt/lab-classroom/class17/.

### setup
Create the laboratory directory with: sudo install -d -o "$(id -un)" -g "$(id -gn)" -m 0750 /opt/lab-classroom/class17
Enter it with: cd /opt/lab-classroom/class17
Create the source data with: printf 'dns,active,53\nweb,active,443\nbackup,inactive,0\nmetrics,active,9100\nweb,active,80\n' > services.csv
Inspect the source with: cat services.csv

### steps
### step
1

### description
Redirect a file into standard input and save the resulting count.

### command
wc -l < /opt/lab-classroom/class17/services.csv > /opt/lab-classroom/class17/service-line-count.txt
### step
2

### description
Use a pipeline to extract active service names, sort them, and count duplicates.

### command
awk -F, '$2 == "active" { print $1 }' /opt/lab-classroom/class17/services.csv | LC_ALL=C sort | uniq -c > /opt/lab-classroom/class17/active-name-counts.txt
### step
3

### description
Use tee to save active service records while also passing them to wc.

### command
awk -F, '$2 == "active" { print }' /opt/lab-classroom/class17/services.csv | tee /opt/lab-classroom/class17/active-services.csv | wc -l > /opt/lab-classroom/class17/active-count.txt
### step
4

### description
Create a log and append a second event without replacing the first.

### command
printf 'pipeline-started\n' > /opt/lab-classroom/class17/events.log; printf 'pipeline-finished\n' >> /opt/lab-classroom/class17/events.log
### step
5

### description
Capture a deliberate read error separately from standard output and record the failing exit status.

### command
cat /opt/lab-classroom/class17/does-not-exist.txt > /opt/lab-classroom/class17/read-output.log 2> /opt/lab-classroom/class17/read-error.log || printf 'cat_exit=%s\n' "$?" > /opt/lab-classroom/class17/read-status.txt
### step
6

### description
Generate stdout and stderr in one command group, then save them in separate files.

### command
{ printf 'normal-message\n'; printf 'diagnostic-message\n' >&2; } > /opt/lab-classroom/class17/stdout-only.log 2> /opt/lab-classroom/class17/stderr-only.log
### step
7

### description
Generate both streams again and combine them using left-to-right redirection.

### command
{ printf 'stdout-message\n'; printf 'stderr-message\n' >&2; } > /opt/lab-classroom/class17/combined.log 2>&1
### step
8

### description
Produce a count grouped by service state.

### command
awk -F, '{ print $2 }' /opt/lab-classroom/class17/services.csv | LC_ALL=C sort | uniq -c > /opt/lab-classroom/class17/state-counts.txt
### step
9

### description
Inspect all generated regular files without modifying them.

### command
find /opt/lab-classroom/class17 -maxdepth 1 -type f -printf '%f\n' | LC_ALL=C sort

## Expected results

- services.csv contains five comma-separated service records.
- service-line-count.txt contains the number 5 without a filename.
- active-name-counts.txt reports one dns record, one metrics record, and two web records.
- active-services.csv contains four records whose state field is active.
- active-count.txt contains the number 4.
- events.log contains pipeline-started followed by pipeline-finished.
- read-output.log is empty because the deliberate cat operation produced no standard output.
- read-error.log is nonempty and contains the diagnostic from the failed cat operation.
- read-status.txt begins with cat_exit= and records a nonzero status.
- stdout-only.log contains normal-message, while stderr-only.log contains diagnostic-message.
- combined.log contains both stdout-message and stderr-message.
- state-counts.txt reports four active records and one inactive record.

## Verification checkpoints

- [ ] Run: test "$(cat /opt/lab-classroom/class17/service-line-count.txt)" = "5" && printf 'PASS: source line count\n'
- [ ] Run: test "$(cat /opt/lab-classroom/class17/active-count.txt)" = "4" && printf 'PASS: active count\n'
- [ ] Run: awk '$2 == "dns" && $1 == 1 { dns=1 } $2 == "metrics" && $1 == 1 { metrics=1 } $2 == "web" && $1 == 2 { web=1 } END { exit !(dns && metrics && web) }' /opt/lab-classroom/class17/active-name-counts.txt && printf 'PASS: active names\n'
- [ ] Run: awk -F, 'NF != 3 || $2 != "active" { bad=1 } END { exit bad }' /opt/lab-classroom/class17/active-services.csv && printf 'PASS: active records\n'
- [ ] Run: test "$(sed -n '1p' /opt/lab-classroom/class17/events.log)" = "pipeline-started" && test "$(sed -n '2p' /opt/lab-classroom/class17/events.log)" = "pipeline-finished" && printf 'PASS: append behavior\n'
- [ ] Run: test ! -s /opt/lab-classroom/class17/read-output.log && test -s /opt/lab-classroom/class17/read-error.log && grep -Eq '^cat_exit=[1-9][0-9]*$' /opt/lab-classroom/class17/read-status.txt && printf 'PASS: separated error stream\n'
- [ ] Run: grep -Fxq 'normal-message' /opt/lab-classroom/class17/stdout-only.log && grep -Fxq 'diagnostic-message' /opt/lab-classroom/class17/stderr-only.log && printf 'PASS: separate streams\n'
- [ ] Run: test "$(wc -l < /opt/lab-classroom/class17/combined.log)" = "2" && grep -Fxq 'stdout-message' /opt/lab-classroom/class17/combined.log && grep -Fxq 'stderr-message' /opt/lab-classroom/class17/combined.log && printf 'PASS: combined streams\n'
- [ ] Run: awk '$2 == "active" && $1 == 4 { active=1 } $2 == "inactive" && $1 == 1 { inactive=1 } END { exit !(active && inactive) }' /opt/lab-classroom/class17/state-counts.txt && printf 'PASS: state counts\n'

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Creating the laboratory directory reports permission denied. | The current account cannot create directories beneath /opt without elevation. | Run only the provided sudo install command for /opt/lab-classroom/class17, then confirm that the resulting directory is owned by the current user. |
| The awk command produces no active records. | The field separator was omitted, the input file was mistyped, or shell quoting changed the awk program. | Use -F, exactly as shown, keep the awk program inside single quotes, and verify the contents of services.csv with cat. |
| active-name-counts.txt contains unexpected duplicate lines. | uniq received unsorted input because the sort stage was omitted or placed after uniq. | Use the sequence producer | sort | uniq -c so identical lines are adjacent before uniq processes them. |
| An error message appears on the terminal even though stdout was redirected. | Only file descriptor 1 was redirected; file descriptor 2 still points to the terminal. | Add a separate 2> destination or combine the streams with > destination 2>&1. |
| A combined-output command still leaves diagnostics on the terminal. | The redirections were written in the reverse order, causing stderr to retain the shell's previous stdout destination. | Place the stdout redirection first and then duplicate it with 2>&1. |
| A pipeline appears successful even though an early command failed. | The shell returned the exit status of the final pipeline command. | In Bash scripts where every stage matters, enable pipefail with set -o pipefail and test the resulting status. |
| A verification command prints nothing. | The condition failed, a generated file is missing, or the shell did not reach the success-side printf after &&. | Run the tests on each file separately, inspect the file with cat, and compare its content with the expected results. |
| A file unexpectedly lost its previous contents. | The > operator truncated the file before writing. | Use >> only when appending is intended, enable noclobber during interactive work when appropriate, and verify the destination path before pressing Enter. |

## Security considerations

### principles
Treat every redirection destination as a write operation and verify its complete path before execution.
Keep untrusted data out of shell code. Pipe data as data rather than constructing commands from it.
Do not record credentials, tokens, private keys, or other secrets with tee or diagnostic redirections.
Quote variable expansions used as filenames so whitespace and wildcard characters are not reinterpreted by the shell.
Be cautious when elevated commands write through paths controlled by another user because symbolic links can redirect writes to unintended destinations.
Remember that the shell opens redirection targets before launching the command; privilege boundaries therefore depend on which process performs the open operation.
Use restrictive permissions for logs that could contain hostnames, usernames, internal addresses, or command diagnostics.
Use pipefail in Bash automation when the success of every pipeline stage is required.

### lab_boundary
All persistent writes in this lesson are confined to /opt/lab-classroom/class17/.

## Rollback

### precheck
Review the files before removal with: find /opt/lab-classroom/class17 -maxdepth 1 -type f -printf '%f\n' | LC_ALL=C sort

### remove_files
Run: find /opt/lab-classroom/class17 -maxdepth 1 -type f -delete

### remove_directory
After confirming the directory is empty, run: rmdir /opt/lab-classroom/class17

### verification
Run: test ! -e /opt/lab-classroom/class17 && printf 'Rollback complete\n'

## Video narration notes

Begin by drawing three arrows attached to every command: descriptor 0 for input, descriptor 1 for normal output, and descriptor 2 for diagnostics. Demonstrate that a command normally displays both stdout and stderr on the terminal even though they are separate streams. Next, show a simple pipeline and trace stdout from the producer into stdin of the consumer. Emphasize that stderr does not enter the pipe automatically. Introduce > as replacement output, >> as append output, and < as file-backed input. Compare wc -l with a filename argument against wc -l using input redirection. Then create an intentional error and capture descriptor 2 with 2>. Explain combined redirection by reading > combined.log 2>&1 from left to right: first stdout moves to the file, then stderr is duplicated onto stdout's current destination. Contrast this conceptually with the reversed order. Demonstrate tee as a branching point that saves records while allowing wc to continue counting them. Close by discussing exit status, Bash pipefail, quoting, verification, and the risk of truncating the wrong destination with >. Remind students that every persistent lab write remains inside /opt/lab-classroom/class17/.

## References

- GNU Bash Manual, Pipelines: https://www.gnu.org/software/bash/manual/html_node/Pipelines.html
- GNU Bash Manual, Redirections: https://www.gnu.org/software/bash/manual/html_node/Redirections.html
- GNU Bash Manual, The Set Builtin: https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html
- GNU Coreutils Manual, tee: https://www.gnu.org/software/coreutils/manual/html_node/tee-invocation.html
- GNU Coreutils Manual, wc: https://www.gnu.org/software/coreutils/manual/html_node/wc-invocation.html
- GNU Coreutils Manual, sort: https://www.gnu.org/software/coreutils/manual/html_node/sort-invocation.html
- GNU Coreutils Manual, uniq: https://www.gnu.org/software/coreutils/manual/html_node/uniq-invocation.html
- Linux man-pages project, pipe(7): https://man7.org/linux/man-pages/man7/pipe.7.html

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

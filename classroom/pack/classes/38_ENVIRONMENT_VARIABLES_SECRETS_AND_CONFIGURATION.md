# Class 38 — Environment Variables, Secrets, and Configuration

**Learning objective:** Distinguish ordinary configuration values from sensitive values that require stronger handling.; Explain how a child process inherits exported environment variables.; Describe why environment variables are convenient but are not automatically confidential.; Implement explicit configuration precedence using defaults, a configuration file, and environment overrides.; Load a sensitive value from a permission-restricted file without displaying it.; Reject a sensitive file when group or other permission bits are present.; Rotate a generated training credential with an atomic file replacement.; Verify effective configuration without logging sensitive content.
**Bloom level:** Understand / Apply
**Track:** Homelab Operations and Service Deployment · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Teach learners to separate ordinary configuration from sensitive runtime material, understand environment inheritance, validate file-based secrets, apply configuration precedence deliberately, and rotate a training credential without exposing its contents.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Debian 12
Ubuntu Server 22.04 LTS or newer
Rocky Linux 9
Other Linux distributions with equivalent POSIX utilities

### runtime
Python 3.9 or newer

### shell
POSIX-compatible shell

### filesystem
The rotation demonstration assumes the staged and active files are on the same local filesystem and that os.replace provides normal atomic replacement semantics.

### containers
The concepts apply to containers, but this lab runs directly on a Linux host and does not require a container engine.

### privilege_model
The learner must be able to create and modify only /opt/lab-classroom/class38/ beneath a pre-provisioned /opt/lab-classroom directory.

## Learning objective

- Distinguish ordinary configuration values from sensitive values that require stronger handling.
- Explain how a child process inherits exported environment variables.
- Describe why environment variables are convenient but are not automatically confidential.
- Implement explicit configuration precedence using defaults, a configuration file, and environment overrides.
- Load a sensitive value from a permission-restricted file without displaying it.
- Reject a sensitive file when group or other permission bits are present.
- Rotate a generated training credential with an atomic file replacement.
- Verify effective configuration without logging sensitive content.

## Why this matters

Teach learners to separate ordinary configuration from sensitive runtime material, understand environment inheritance, validate file-based secrets, apply configuration precedence deliberately, and rotate a training credential without exposing its contents.

## Prerequisites

- Completion of introductory Linux shell, file permissions, and process-management lessons.
- Python 3.9 or newer available as python3.
- A POSIX-compatible shell with env, stat, install, and chmod.
- The directory /opt/lab-classroom already exists and the learner has permission to create /opt/lab-classroom/class38/.
- All commands must be executed on a disposable lab host or classroom virtual machine.

## Required reading

- Python documentation: os.environ and process environment behavior.
- Python documentation: pathlib.Path file operations.
- Python documentation: os.replace atomic replacement semantics on a single filesystem.
- Linux manual pages for environ(7), stat(1), chmod(1), and umask(2).
- The Twelve-Factor App section titled Config, read critically with attention to threat models and platform limitations.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Configuration | Values that alter application behavior without changing application code, such as a log level, listening port, feature switch, or operating mode. |
| Secret | Sensitive data whose disclosure could grant access or weaken security, such as an authentication token, private key, or encryption key. |
| Environment variable | A named string value attached to a process and normally inherited by child processes. |
| Process environment | The complete set of environment variables available to a running process. |
| Configuration precedence | The documented order used to decide which source wins when several sources define the same setting. |
| Secret file | A file used to deliver sensitive data to a process, normally protected by restrictive ownership and permission controls. |
| Least privilege | Granting only the access required for a user, process, or service to perform its intended function. |
| Atomic replacement | Replacing a destination file in one filesystem operation so readers observe either the old complete file or the new complete file rather than a partially written state. |
| Redaction | Removing or obscuring sensitive values from logs, diagnostics, monitoring output, and user interfaces. |
| Fail closed | Refusing to start or operate when required security conditions cannot be verified. |

## Instruction

Applications need values that differ between environments: ports, hostnames, feature switches, log levels, credentials, and cryptographic material. These values should not all be handled in the same way. Ordinary configuration may be safe to display during diagnostics, while a secret must remain confidential at rest, in transit, in logs, and during troubleshooting. Environment variables are useful because deployment systems can supply values without rewriting application code. They also support clean process-level overrides. However, an environment variable is not a secret vault. It can be inherited by child processes, copied into diagnostic bundles, exposed by careless process inspection, retained by automation systems, or printed during debugging. For this reason, use environment variables for non-sensitive overrides unless the deployment platform provides a carefully controlled secret-injection mechanism and its limitations are understood.

Configuration precedence must be explicit and predictable. This lesson uses built-in defaults, then a JSON configuration file, then selected environment-variable overrides. The most specific runtime source wins. Unrecognized or invalid values are rejected instead of silently accepted. Sensitive material follows a separate path: an environment variable contains only the pathname of a protected file, and the application reads the file after validating that it is inside the lab directory, is a regular file, has no group or other permission bits, and is not empty. The program reports only whether the value loaded; it never prints the value itself.

A configuration file should be treated as data rather than executable shell text. Loading an untrusted file with shell sourcing can execute commands, expand variables, or alter shell behavior. Structured formats such as JSON avoid that specific execution path, although they still require schema validation and safe permissions. Sensitive files should be readable only by the service identity and should not be committed to version control, copied into container images, embedded in command arguments, or included in support archives.

Rotation is another core requirement. Rewriting a file in place can briefly expose an empty or partial value to a concurrent reader. A safer pattern is to create a new file with restrictive permissions, fully write and flush it, and then atomically replace the active file on the same filesystem. Production systems may also need coordinated overlap, revocation, audit events, and service reload behavior. The lab uses a randomly generated, disposable training credential and never reveals its content. The important operational lesson is that secure configuration includes delivery, validation, observation, rotation, and cleanup rather than merely choosing where to store a string.

## Architecture

### components
A JSON file containing non-sensitive baseline configuration.
A Python application that validates and merges configuration sources.
Selected environment variables carrying non-sensitive overrides and the pathname of a sensitive file.
A permission-restricted file containing a randomly generated, disposable training credential.
A rotation procedure that writes a new file and atomically replaces the active file.

### configuration_precedence
Built-in application defaults have the lowest precedence.
Values in config.json override built-in defaults.
APP_MODE and LOG_LEVEL environment variables override corresponding JSON values.
APP_TOKEN_FILE does not contain sensitive content; it identifies the separately protected file that the application must validate and read.

### data_flow
The application loads defaults.
The application parses /opt/lab-classroom/class38/config/config.json.
The application applies allow-listed environment overrides.
The application resolves and validates the sensitive file path.
The application reads the sensitive value into memory and reports only a Boolean loaded status.

### trust_boundaries
The process environment is outside the application configuration parser and must be validated.
The filesystem boundary requires path, file type, and permission validation.
Logs and terminal output are disclosure boundaries and must never contain the sensitive value.
The lab root is the only location in which the exercises are permitted to create, replace, or change files.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Add an allow-listed SERVICE_REGION setting with a built-in default, JSON support, and an environment override. Keep all changes inside /opt/lab-classroom/class38/.
Modify the application so a missing optional JSON file still permits defaults, while malformed JSON remains a startup error.
Write a short configuration contract listing each setting, its type, allowed values, default, sensitivity classification, and precedence.
Design a production rotation plan that covers issuance, overlap, activation, verification, revocation, audit evidence, and emergency rollback.
Explain why logging a digest of a low-entropy sensitive value can still enable guessing and why the lab reports only a Boolean loaded status.

## Feynman teach-back

### prompt
Explain the lesson to someone who knows how to run a program but has never managed application configuration.

### model_explanation
Configuration tells a program how to behave, while a secret proves identity or protects data. Environment variables are notes handed from a parent process to a child process, so they are convenient but not automatically private. This application takes ordinary settings from defaults, JSON, and approved environment overrides. For the sensitive value, the environment carries only a file location. The application checks that the file is inside the expected directory, is a normal file, has restrictive permissions, and contains data. It then uses the value without printing it. During rotation, a complete new file is prepared first and replaces the old file in one operation so a reader does not observe a partially written value.

### self_check
Can you state which source wins when the same non-sensitive setting appears in defaults, JSON, and the environment?
Can you explain why putting a value in the environment does not make it confidential?
Can you explain why writing a new file before replacement is safer than rewriting the active file in place?
Can you verify successful loading without revealing the loaded value?

## Retrieval check

1. What is the configuration precedence used for app_mode and log_level in this lesson?
2. Why does the lesson avoid placing the generated credential directly in an environment variable?
3. What does the application verify before reading the sensitive file?
4. Why is rewriting an active sensitive file in place less safe than atomic replacement?
5. What output proves that the application loaded the sensitive value without revealing it?
6. Why should an untrusted configuration file not be loaded as executable shell text?
7. What should the application do when a required sensitive file has group-readable permissions?

## Guided lab

### scope
Every filesystem mutation in this lab is confined to /opt/lab-classroom/class38/. The credential is randomly generated for the exercise, has no external privileges, and is never printed.

### steps
### step
1

### title
Create the isolated lab directories

### commands
install -d -m 0750 /opt/lab-classroom/class38
install -d -m 0750 /opt/lab-classroom/class38/config
install -d -m 0700 /opt/lab-classroom/class38/runtime

### explanation
The configuration directory will hold non-sensitive data. The runtime directory has more restrictive permissions because it will hold the generated training credential.
### step
2

### title
Create non-sensitive structured configuration

### commands
python3 - <<'PY'
import json
from pathlib import Path
path = Path('/opt/lab-classroom/class38/config/config.json')
data = {'app_mode': 'normal', 'log_level': 'info'}
path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
path.chmod(0o640)
PY

### explanation
The file contains only ordinary configuration. Python writes valid JSON directly, avoiding any need to treat configuration data as executable shell syntax.
### step
3

### title
Generate a disposable credential without displaying it

### commands
python3 - <<'PY'
import os
import secrets
from pathlib import Path
path = Path('/opt/lab-classroom/class38/runtime/app.token')
flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
fd = os.open(path, flags, 0o600)
with os.fdopen(fd, 'w', encoding='utf-8') as handle:
    handle.write(secrets.token_urlsafe(32))
    handle.write('\n')
path.chmod(0o600)
PY

### explanation
The credential is generated locally, written with restrictive permissions, and never sent to standard output. It is valid only as lab data and grants access to no service.
### step
4

### title
Create the configuration-loading application

### commands
python3 - <<'PY'
from pathlib import Path
program = '''import json
import os
import stat
from pathlib import Path

ROOT = Path("/opt/lab-classroom/class38").resolve()
CONFIG_PATH = ROOT / "config" / "config.json"
DEFAULTS = {"app_mode": "normal", "log_level": "warning"}
ALLOWED_MODES = {"normal", "maintenance"}
ALLOWED_LEVELS = {"debug", "info", "warning", "error"}

def require_choice(name, value, allowed):
    if value not in allowed:
        raise SystemExit(f"invalid {name}: {value!r}")
    return value

def load_sensitive_file():
    supplied = os.environ.get("APP_TOKEN_FILE")
    if not supplied:
        raise SystemExit("APP_TOKEN_FILE is required")
    path = Path(supplied).resolve(strict=True)
    if ROOT not in path.parents:
        raise SystemExit("sensitive file must remain inside the class38 lab root")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode):
        raise SystemExit("sensitive path is not a regular file")
    permissions = stat.S_IMODE(info.st_mode)
    if permissions & 0o077:
        raise SystemExit("sensitive file has group or other permission bits")
    value = path.read_text(encoding="utf-8").rstrip("\\n")
    if not value:
        raise SystemExit("sensitive file is empty")
    return value

def main():
    settings = dict(DEFAULTS)
    file_settings = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    unknown = set(file_settings) - {"app_mode", "log_level"}
    if unknown:
        raise SystemExit(f"unknown configuration keys: {sorted(unknown)}")
    settings.update(file_settings)
    if "APP_MODE" in os.environ:
        settings["app_mode"] = os.environ["APP_MODE"]
    if "LOG_LEVEL" in os.environ:
        settings["log_level"] = os.environ["LOG_LEVEL"]
    settings["app_mode"] = require_choice("app_mode", settings["app_mode"], ALLOWED_MODES)
    settings["log_level"] = require_choice("log_level", settings["log_level"], ALLOWED_LEVELS)
    sensitive_value = load_sensitive_file()
    safe_status = {
        "app_mode": settings["app_mode"],
        "log_level": settings["log_level"],
        "sensitive_value_loaded": bool(sensitive_value)
    }
    print(json.dumps(safe_status, sort_keys=True))

if __name__ == "__main__":
    main()
'''
path = Path('/opt/lab-classroom/class38/app.py')
path.write_text(program, encoding='utf-8')
path.chmod(0o750)
PY

### explanation
The application allow-lists configuration keys and values, constrains the sensitive path to the lab root, requires a regular file, rejects broad permissions, and emits only safe status information.
### step
5

### title
Observe environment inheritance using harmless data

### commands
env LAB_DISPLAY=child-visible python3 -c 'import os; print(os.environ["LAB_DISPLAY"])'

### explanation
The Python child process receives LAB_DISPLAY from its parent invocation. This demonstrates inheritance without placing sensitive data in the environment.
### step
6

### title
Run with file configuration and environment overrides

### commands
env APP_MODE=maintenance LOG_LEVEL=debug APP_TOKEN_FILE=/opt/lab-classroom/class38/runtime/app.token python3 /opt/lab-classroom/class38/app.py

### explanation
The environment overrides the JSON values for application mode and log level. APP_TOKEN_FILE carries only a path. The sensitive file contents are not included in the command or output.
### step
7

### title
Verify that unsafe permissions fail closed

### commands
chmod 0644 /opt/lab-classroom/class38/runtime/app.token
env APP_TOKEN_FILE=/opt/lab-classroom/class38/runtime/app.token python3 /opt/lab-classroom/class38/app.py; test $? -ne 0
chmod 0600 /opt/lab-classroom/class38/runtime/app.token

### explanation
The application must reject a sensitive file that has group or other permission bits. The final command restores the intended mode before continuing.
### step
8

### title
Rotate the credential with atomic replacement

### commands
python3 - <<'PY'
import os
import secrets
from pathlib import Path
runtime = Path('/opt/lab-classroom/class38/runtime')
active = runtime / 'app.token'
staged = runtime / 'app.token.next'
fd = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, 'w', encoding='utf-8') as handle:
    handle.write(secrets.token_urlsafe(32))
    handle.write('\n')
    handle.flush()
    os.fsync(handle.fileno())
staged.chmod(0o600)
os.replace(staged, active)
PY
env APP_TOKEN_FILE=/opt/lab-classroom/class38/runtime/app.token python3 /opt/lab-classroom/class38/app.py

### explanation
The replacement file is fully written and synchronized before os.replace makes it active. Both paths reside in the same directory and filesystem, enabling atomic replacement under normal POSIX filesystem semantics.
### step
9

### title
Inspect metadata without reading sensitive content

### commands
stat -c 'mode=%a type=%F path=%n' /opt/lab-classroom/class38/runtime/app.token
python3 -m json.tool /opt/lab-classroom/class38/config/config.json

### explanation
Metadata and non-sensitive configuration are safe to inspect. Do not display, copy, or include the credential file in diagnostic output.

## Expected results

- The harmless inheritance test prints child-visible.
- The first application run prints a JSON object showing app_mode as maintenance, log_level as debug, and sensitive_value_loaded as true.
- No command or application output displays the generated credential.
- The application exits unsuccessfully while the credential file mode is 0644 and reports that group or other permission bits are present.
- After mode 0600 is restored, the application starts successfully.
- The rotation procedure completes without producing the old or new credential on standard output.
- The post-rotation application run reports sensitive_value_loaded as true.
- The final stat command reports mode=600 and type=regular file for the active credential.

## Verification checkpoints

- [ ] Run: test -d /opt/lab-classroom/class38/config && test -d /opt/lab-classroom/class38/runtime. Success is indicated by exit status zero.
- [ ] Run: python3 -m json.tool /opt/lab-classroom/class38/config/config.json >/dev/null. Success confirms that the non-sensitive configuration is valid JSON.
- [ ] Run: test "$(stat -c '%a' /opt/lab-classroom/class38/runtime/app.token)" = 600. Success confirms the intended permission mode.
- [ ] Run: test -f /opt/lab-classroom/class38/runtime/app.token && test -s /opt/lab-classroom/class38/runtime/app.token. Success confirms that the active path is a non-empty regular file without revealing its contents.
- [ ] Run: env APP_MODE=maintenance LOG_LEVEL=debug APP_TOKEN_FILE=/opt/lab-classroom/class38/runtime/app.token python3 /opt/lab-classroom/class38/app.py. Verify that the output contains only effective non-sensitive settings and a true loaded status.
- [ ] Run: test ! -e /opt/lab-classroom/class38/runtime/app.token.next. Success confirms that the staged rotation path was replaced rather than left behind.
- [ ] Review the terminal history for the lab and confirm that no generated credential content was printed or supplied as a command argument.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Creating /opt/lab-classroom/class38 fails with permission denied. | The classroom parent directory was not provisioned as writable for the learner. | Ask the lab administrator to create /opt/lab-classroom and delegate access. Do not redirect the exercise to another path because the application intentionally enforces the assigned lab root. |
| python3 is not found. | Python 3 is not installed or is not available through the current PATH. | Use a lab image that satisfies the prerequisite or have the administrator install Python 3 through the operating system's trusted package-management process. |
| The application reports that APP_TOKEN_FILE is required. | The variable was omitted from the process invocation or was not exported to the child process. | Run the complete env command from the lab so APP_TOKEN_FILE contains the approved path to the lab credential file. |
| The application reports that the sensitive file is outside the lab root. | APP_TOKEN_FILE identifies another location or resolves through a link to another location. | Set APP_TOKEN_FILE to /opt/lab-classroom/class38/runtime/app.token and confirm that the active path is a regular file created by the lab. |
| The application reports group or other permission bits. | The sensitive file mode is broader than 0600, possibly because the deliberate failure test was not reversed. | Run chmod 0600 /opt/lab-classroom/class38/runtime/app.token and repeat the application test. |
| The application reports an invalid app_mode or log_level. | The JSON file or environment override contains a value outside the application's allow-list. | Use normal or maintenance for app_mode and debug, info, warning, or error for log_level. |
| The application reports unknown configuration keys. | An unsupported key was added to config.json. | Remove the unsupported key. The lab schema permits only app_mode and log_level. |
| Atomic replacement fails. | The staged file and active file are not on the expected filesystem, the directory is not writable, or a previous manual change altered the lab layout. | Confirm that both paths are directly under /opt/lab-classroom/class38/runtime, correct the directory permissions within the lab root, and rerun the rotation step. |

## Security considerations

### principles
Classify values before choosing a delivery mechanism. A log level is not equivalent to an authentication credential.
Do not assume that environment variables are confidential merely because they are not stored in a normal configuration file.
Use allow-lists and explicit parsing rather than accepting arbitrary keys or values.
Place only the sensitive file path in the environment for this exercise, not the sensitive value.
Run services under dedicated identities and restrict sensitive files to the intended service identity.
Never print sensitive values during startup checks, debugging, verification, or rotation.
Exclude sensitive files from source control, image build contexts, backups that lack appropriate controls, and routine support archives.
Treat access to deployment systems, service managers, and container orchestrators as sensitive because they may be able to inject or retrieve runtime configuration.
Fail closed when a required sensitive file is missing, empty, unexpectedly typed, outside the approved root, or too broadly accessible.
Document rotation, revocation, audit, and service-reload behavior before deploying a real credential.

### production_notes
A production secret-management system may provide identity-based access, encryption, short-lived credentials, audit records, automated rotation, and policy enforcement. A protected file is still useful as a delivery interface, but file permissions alone do not address host compromise, privileged users, backups, memory inspection, or accidental application logging. The lab credential is deliberately isolated and grants no external access.

## Rollback

### goal
Remove only the class-specific lab directory and all generated training data.

### prechecks
Confirm that the exact cleanup target is /opt/lab-classroom/class38.
Confirm that no production service uses any file below the class38 directory.
Confirm that the current lesson work has been assessed before deletion.

### command
python3 - <<'PY'
from pathlib import Path
import shutil
target = Path('/opt/lab-classroom/class38')
expected = Path('/opt/lab-classroom/class38')
if target != expected or target.parent != Path('/opt/lab-classroom'):
    raise SystemExit('refusing unexpected cleanup target')
if target.exists():
    shutil.rmtree(target)
PY

### verification
Run: test ! -e /opt/lab-classroom/class38. Exit status zero confirms that the class directory was removed while /opt/lab-classroom itself was preserved.

### recovery_note
Cleanup permanently removes the disposable credential and lab files. Recreate them by repeating the lesson from step 1.

## Video narration notes

Welcome to Class 38: Environment Variables, Secrets, and Configuration. In this lesson, we separate two ideas that are often mixed together. Configuration changes how an application behaves. Sensitive material grants access or protects data. A log level can usually appear in diagnostics; an authentication credential must not.

We begin with three sources for ordinary settings. The application has built-in defaults. A JSON file overrides those defaults. Selected environment variables provide the final runtime override. This precedence is deliberate and documented. The program accepts only known keys and known values, so a typo does not silently create an unexpected state.

Next, we handle sensitive material differently. The lab generates a disposable credential locally and does not print it. The environment variable APP_TOKEN_FILE contains only the location of that file. Before reading it, the program resolves the path, confirms that it remains inside the class directory, verifies that it is a regular file, checks that no group or other permission bits are set, and rejects an empty value. The status output tells us that loading succeeded without displaying the sensitive content.

The deliberate permission failure demonstrates fail-closed behavior. When the file becomes broadly readable, the program refuses to start. Restoring mode 0600 allows it to run again. This is more dependable than issuing a warning and continuing with an unsafe state.

Finally, we rotate the credential. The program creates a separate file, writes the complete new value, flushes it, and atomically replaces the active path. This avoids a window in which another process could read a partially written value. Real systems may also need overlap between old and new credentials, external revocation, audit records, and coordinated reloads. Remember the central rule: secure configuration is not merely where a value is stored. It includes classification, delivery, validation, permissions, observability, rotation, and cleanup.

## References

- Python Standard Library documentation for os: https://docs.python.org/3/library/os.html
- Python Standard Library documentation for pathlib: https://docs.python.org/3/library/pathlib.html
- Python Standard Library documentation for json: https://docs.python.org/3/library/json.html
- Python Standard Library documentation for secrets: https://docs.python.org/3/library/secrets.html
- Linux man-pages project documentation for environ(7): https://man7.org/linux/man-pages/man7/environ.7.html
- The Twelve-Factor App, Config: https://12factor.net/config
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

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

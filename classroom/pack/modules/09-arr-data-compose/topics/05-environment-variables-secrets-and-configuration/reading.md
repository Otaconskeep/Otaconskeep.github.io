# Reading: Environment Variables, Secrets, and Configuration

**Module:** ARR Data Model & Compose
**Activity type:** Reading (Learn)
**Objective:** Distinguish ordinary configuration values from sensitive values that require stronger handling.

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

## Required reading

- Python documentation: os.environ and process environment behavior.
- Python documentation: pathlib.Path file operations.
- Python documentation: os.replace atomic replacement semantics on a single filesystem.
- Linux manual pages for environ(7), stat(1), chmod(1), and umask(2).
- The Twelve-Factor App section titled Config, read critically with attention to threat models and platform limitations.

## References

- Python Standard Library documentation for os: https://docs.python.org/3/library/os.html
- Python Standard Library documentation for pathlib: https://docs.python.org/3/library/pathlib.html
- Python Standard Library documentation for json: https://docs.python.org/3/library/json.html
- Python Standard Library documentation for secrets: https://docs.python.org/3/library/secrets.html
- Linux man-pages project documentation for environ(7): https://man7.org/linux/man-pages/man7/environ.7.html
- The Twelve-Factor App, Config: https://12factor.net/config
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

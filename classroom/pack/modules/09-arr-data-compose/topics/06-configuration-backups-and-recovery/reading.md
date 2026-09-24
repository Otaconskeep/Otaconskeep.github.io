# Reading: Configuration Backups and Recovery

**Module:** ARR Data Model & Compose
**Activity type:** Reading (Learn)
**Objective:** Explain why a configuration archive alone is not a complete recovery strategy.

## Vocabulary

| Term | Meaning |
|---|---|
| configuration backup | A captured copy of configuration state, normally accompanied by version, source, integrity, and retention information. |
| recovery point objective | The maximum acceptable amount of configuration history that could be lost, usually expressed as a period of time. |
| recovery time objective | The target amount of time allowed to restore a usable configuration after a failure. |
| manifest | A list of expected files and associated metadata such as cryptographic checksums. |
| integrity check | A test that determines whether bytes have changed since a trusted checksum was created. |
| syntax validation | A check that confirms a file can be parsed according to its data format. |
| semantic validation | A check that confirms parsed values meet application-specific rules, ranges, and required relationships. |
| configuration drift | A difference between the intended configuration and the configuration currently present on a system. |
| recovery candidate | Restored content held in an isolated location while integrity and application-specific checks are performed. |
| promotion | The controlled action that makes a validated recovery candidate the active configuration. |
| rollback | The process of returning to the state that existed immediately before a change or recovery attempt. |

## Instruction

A useful configuration backup is more than a compressed copy of a directory. A recovery operator must know what was captured, which system or service it belongs to, when it was captured, whether the archive remained intact, and whether the restored files are usable. These requirements create several separate validation layers. An archive listing proves that the container can be read, but it does not prove that the files express valid settings. A cryptographic checksum detects byte changes, but a perfectly intact file can still contain an invalid port, a missing required key, or a value incompatible with the installed application version. Syntax validation confirms that a parser accepts the document. Semantic validation then checks rules meaningful to the service, such as an integer being within an allowed range.

Recovery should be staged. Extracting directly over an active configuration mixes backup extraction, validation, and activation into one difficult-to-reverse operation. Instead, restore into a candidate directory, verify the archive checksum, verify the manifest, inspect metadata, parse the files, and apply semantic checks. Only after those gates pass should the candidate be promoted. Keeping the old configuration under a distinct name provides a rapid rollback path. Renaming directories on the same filesystem also reduces the interval in which an incomplete tree could be visible, although application behavior and open file handles still determine whether a restart or reload is required.

Checksums establish integrity relative to a trusted checksum, not authenticity by themselves. If an attacker can replace both an archive and its checksum, the pair can still verify. Higher-assurance environments should protect manifests with signing, immutable storage, restricted backup credentials, or an independently controlled backup system. Configuration backups may also contain passwords, API tokens, private keys, internal addresses, or identity-provider details. They therefore require access restrictions, retention limits, secure transfer, and tested destruction procedures.

The final measure of backup quality is a successful restore test. A job reporting that it created an archive only proves that a command completed. Regular drills should recover a representative version, validate it against the target software version, and document the time and decisions required. This lab models that workflow entirely under one classroom path: establish a known configuration, create a manifest and archive, introduce legitimate-looking drift, recover to an isolated candidate, validate it, promote it, and preserve a rollback route.

## Architecture

### scope_root
/opt/lab-classroom/class39/attempt1/

### components
config/: active configuration used as the source of the backup and later as the promoted recovery target.
staging/package/: immutable-in-practice package layout assembled before archive creation.
backups/: compressed archive and its independently stored archive checksum.
restore/candidate/: isolated extraction location used for recovery validation.
rollback/: retained copy of the configuration immediately before promotion.
validate.py: read-only semantic validator for the JSON and INI examples.

### data_flow
Known configuration is written under config/.
Configuration is copied into staging/package/config/.
A deterministic file manifest is generated relative to the package root.
Package contents are archived under backups/ and the archive receives a separate checksum.
The active configuration is changed to model drift.
The archive is extracted into restore/candidate/ and validated before activation.
The drifted configuration is retained, and the candidate configuration is renamed into the active location.

### trust_boundaries
The archive checksum is useful only while its sidecar file is obtained from a trusted location.
The manifest verifies packaged configuration bytes but does not establish who created them.
The validator represents application-specific policy and must evolve when configuration schemas change.
Promotion does not automatically reload a real service; service lifecycle actions require a separate, service-specific runbook.

## Required reading

- GNU tar manual, tutorial and archive operations: https://www.gnu.org/software/tar/manual/
- GNU Coreutils manual, sha2 utilities: https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html
- Python documentation, json module: https://docs.python.org/3/library/json.html
- Python documentation, configparser module: https://docs.python.org/3/library/configparser.html
- NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/pubs/sp/800/34/r1/final

## References

- GNU tar manual: https://www.gnu.org/software/tar/manual/
- GNU Coreutils sha2 utilities: https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html
- GNU Coreutils sha2 invocation: https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html
- Python json module documentation: https://docs.python.org/3/library/json.html
- Python configparser documentation: https://docs.python.org/3/library/configparser.html
- Python pathlib documentation: https://docs.python.org/3/library/pathlib.html
- NIST SP 800-34 Rev. 1: https://csrc.nist.gov/pubs/sp/800/34/r1/final
- CISA Stop Ransomware Guide, backup and recovery guidance: https://www.cisa.gov/stopransomware/ransomware-guide

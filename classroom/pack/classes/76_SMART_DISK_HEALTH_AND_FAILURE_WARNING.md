# Class 76: SMART, Disk Health, and Failure Warning

**Learning objective:** Explain what SMART can and cannot predict.; Distinguish normalized SMART values, thresholds, and vendor-specific raw values.; Identify SATA indicators associated with media damage, transport problems, and temperature.; Interpret important NVMe health fields such as Critical Warning, Available Spare, Percentage Used, and Media and Data Integrity Errors.; Explain why an overall health result of PASSED does not prove that a drive is healthy.; Classify disk observations as informational, warning, or critical without relying on a single universal threshold.; Design monitoring that records trends and preserves enough context for incident response.; Choose a safe operational response to signs of disk failure.
**Bloom level:** Understand / Apply
**Track:** Storage Operations and Reliability · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach operators how to interpret SATA, SAS, and NVMe health information without treating a single health flag as proof that a disk is safe. Students will learn which indicators require immediate action, which may indicate a cable or controller problem, and how to turn raw health data into useful monitoring and replacement decisions.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-15
**Compatibility:** ### lab
The synthetic lab requires a POSIX-style shell, grep, and Python 3 with pathlib. It does not require access to a physical disk or privileged device nodes.

### real_devices
Concepts apply to Linux systems using ATA, SATA, SAS, and NVMe storage, but field availability depends on the drive, firmware, kernel, smartmontools version, controller, HBA, RAID mode, USB bridge, enclosure, and vendor pass-through support.

### virtualization
Virtual machines commonly see virtual disks rather than the physical device's native health data. Collect physical-drive telemetry at the hypervisor, storage appliance, controller, or enclosure layer.

### platform_note
Attribute names, raw encodings, warning thresholds, and replacement procedures are model- and platform-specific. Always consult current device and storage-platform documentation.

## Learning objective

- Explain what SMART can and cannot predict.
- Distinguish normalized SMART values, thresholds, and vendor-specific raw values.
- Identify SATA indicators associated with media damage, transport problems, and temperature.
- Interpret important NVMe health fields such as Critical Warning, Available Spare, Percentage Used, and Media and Data Integrity Errors.
- Explain why an overall health result of PASSED does not prove that a drive is healthy.
- Classify disk observations as informational, warning, or critical without relying on a single universal threshold.
- Design monitoring that records trends and preserves enough context for incident response.
- Choose a safe operational response to signs of disk failure.

## Why this matters

Teach operators how to interpret SATA, SAS, and NVMe health information without treating a single health flag as proof that a disk is safe. Students will learn which indicators require immediate action, which may indicate a cable or controller problem, and how to turn raw health data into useful monitoring and replacement decisions.

## Prerequisites

- Basic Linux command-line navigation
- Familiarity with block devices, filesystems, and storage redundancy
- Python 3 available for the synthetic-report lab
- The directory /opt/lab-classroom/class76/ must already exist and be writable by the student
- smartmontools is recommended for later host inspection but is not required for the synthetic lab

## Required reading

- smartctl manual page from the smartmontools project: https://www.smartmontools.org/browser/trunk/smartmontools/smartctl.8.in
- smartmontools documentation and device support information: https://www.smartmontools.org/wiki
- NVM Express specifications index, including the NVMe base specification: https://nvmexpress.org/specifications/
- Linux kernel documentation for NVMe: https://docs.kernel.org/nvme/index.html

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| SMART | Self-Monitoring, Analysis and Reporting Technology implemented by drive firmware to expose health, usage, error, and self-test information. |
| Normalized value | A vendor-defined SMART score, commonly displayed as VALUE, whose scale and direction must be interpreted using the drive manufacturer's rules. |
| Threshold | A vendor-defined boundary used by drive firmware when deciding whether an attribute has reached a failure condition. |
| Raw value | The underlying attribute data reported by the device. Its units and encoding may be vendor-specific and must not automatically be treated as a universal count. |
| Reallocated sector | A sector that the drive has replaced with a spare location after determining that the original location can no longer be used reliably. |
| Pending sector | A sector that could not be read reliably and is waiting for later recovery or reassessment. Pending sectors can cause read errors and deserve prompt investigation. |
| Offline uncorrectable | A sector or block that could not be corrected during an offline scan or related firmware operation. |
| UDMA CRC error | A transport-level data-integrity error commonly associated with a SATA cable, connector, backplane, power issue, or controller path rather than damaged disk media. |
| Critical Warning | An NVMe bit field indicating conditions such as low spare capacity, excessive temperature, degraded reliability, read-only mode, or volatile-memory backup failure. |
| Percentage Used | An NVMe endurance estimate reported by the controller. A value of 100 percent indicates that the estimated endurance limit has been consumed, although the device may continue operating. |
| Predictive failure | A warning that observed indicators suggest elevated failure risk. It is not a guaranteed prediction and cannot detect every sudden failure. |

## Instruction

SMART is evidence, not certainty. A drive can report an overall result of PASSED and still contain pending sectors, recorded media errors, transport faults, or rapidly worsening attributes. It can also fail suddenly without first producing a useful warning. Monitoring must therefore combine drive telemetry with filesystem errors, kernel logs, storage-controller events, redundancy state, application symptoms, and verified backups.

For ATA and SATA devices, reports often contain VALUE, WORST, THRESH, TYPE, WHEN_FAILED, and RAW_VALUE columns. VALUE and THRESH participate in the firmware's vendor-defined failure logic. RAW_VALUE is frequently operationally useful, but its encoding is not standardized across every model. Attribute names and identifiers such as Reallocated_Sector_Ct, Current_Pending_Sector, Offline_Uncorrectable, Reported_Uncorrect, Command_Timeout, Temperature_Celsius, and UDMA_CRC_Error_Count are common rather than universal. Operators should preserve the drive model, firmware revision, interface, and complete report when investigating an alert.

Pending and uncorrectable sectors are especially important because they indicate data that could not be read reliably. A growing reallocated-sector count indicates that the device is consuming spare media to replace defective locations. The urgency depends on workload, redundancy, backup quality, growth rate, and observed read errors, but valuable data should not remain dependent on a suspect device. Do not attempt to force remapping through destructive writes in a diagnostic lesson. First verify backups, collect evidence, check the array or pool, and plan replacement according to the storage platform's procedure.

UDMA CRC errors normally point toward the communication path rather than the magnetic or flash media. A nonzero historical count does not prove that errors are still occurring. Record a baseline, inspect cables, connectors, power, backplanes, and controller logs, and alert when the count increases. Temperature must also be interpreted using model-specific limits and environmental context; one isolated reading is less useful than a sustained trend.

NVMe devices use a different health model. Important fields include Critical Warning, Composite Temperature, Available Spare, Available Spare Threshold, Percentage Used, Data Units Read and Written, Unsafe Shutdowns, Media and Data Integrity Errors, and Error Information Log Entries. A zero Critical Warning field does not erase the significance of media errors. Error log entry counts may include historical or nonfatal events, so correlate them with timestamps, kernel messages, workload symptoms, firmware information, and growth over time.

Self-tests can be useful, but they consume device resources, update device-maintained logs, and may increase latency. Long tests can take substantial time. Schedule tests under an approved maintenance policy, avoid overlapping stressful operations such as rebuilds or scrubs unless the platform vendor recommends it, and never use a self-test as a substitute for a backup. A sound monitoring policy collects periodic complete reports, stores time-series changes, alerts on high-signal conditions, and documents the operator response. The safest response to suspected failure is usually to preserve evidence, verify recoverability, reduce avoidable load, confirm redundancy, and replace the device through the platform's supported workflow.

## Architecture

### flow
Drive firmware maintains health counters, error records, endurance estimates, and self-test history.
The SATA, SAS, USB, HBA, RAID, or NVMe transport determines which health fields reach the operating system.
A collection utility retrieves the available device report.
A monitoring agent records both the current report and changes from the previous baseline.
Alert rules classify media faults, transport faults, temperature conditions, endurance, and telemetry loss.
The operator correlates device health with kernel messages, filesystem or pool state, controller logs, workload symptoms, and backup status.
The incident process preserves evidence and uses the storage platform's supported replacement procedure.

### trust_boundaries
Drive firmware and vendor-specific attribute encodings
USB bridges, RAID controllers, and HBAs that may hide or transform telemetry
Privileged operating-system access to storage devices
Monitoring systems that retain serial numbers and hardware inventory

### alerting_principle
Prefer condition-specific and trend-aware alerts over a single generic healthy-or-failed result.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Design a disk-health alert policy with separate severities for pending sectors, uncorrectable sectors, increasing CRC errors, excessive temperature, NVMe Critical Warning bits, low available spare, endurance consumption, media errors, and telemetry collection failure.
For every alert, document the evidence to preserve, immediate checks, escalation condition, and replacement decision.
Explain how the policy changes for a standalone disk, a mirrored pool, and a distributed storage cluster.
Identify how your actual controller, HBA, hypervisor, or USB enclosure exposes or hides drive telemetry.
Describe how you would prove that a backup is restorable before replacing a suspect disk.

### submission
Submit a concise runbook containing alert conditions, rationale, operator actions, and rollback or stop conditions. Do not run tests against production or irreplaceable disks as part of the homework.

## Feynman teach-back

### prompt
Explain disk-health monitoring to a new homelab operator without using the phrase SMART is magic.

### model_explanation
A disk keeps a maintenance notebook containing temperatures, errors, damaged locations, lifetime usage, and test history. The notebook can show warning signs, but it cannot promise that the disk will work tomorrow. The large PASSED stamp on the cover means only that the firmware's own failure rule has not been crossed. You still need to read the individual entries. Sectors that cannot be read suggest a media problem. CRC errors often suggest a problem in the cable or controller path. NVMe media errors remain important even when its Critical Warning field is zero. Keep backups, save reports over time, watch for growth, and replace suspect drives using the storage system's documented process.

## Retrieval check

1. 1. Why is an overall SMART result of PASSED insufficient to declare a disk healthy?
2. 2. What is the operational difference between a normalized SMART value and a raw value?
3. 3. Which SATA attributes in the lab most strongly indicate unreadable media?
4. 4. What does a growing UDMA CRC error count usually cause an operator to inspect first?
5. 5. Does an NVMe Critical Warning value of 0x00 prove that the device has no media errors?
6. 6. What should be verified before increasing diagnostic load or replacing a suspect disk?
7. 7. Why should disk-health monitoring retain historical values instead of only the newest report?
8. 8. Name two infrastructure layers that can hide or transform disk-health telemetry.
9. 9. What does an NVMe Percentage Used value represent?
10. 10. Why are self-tests not a substitute for backups?

## Guided lab

### name
Classify synthetic SATA and NVMe health reports

### scope
All files created or changed by this lab are confined to /opt/lab-classroom/class76/. The reports are synthetic teaching fixtures and are not measurements from the student's hardware.

### steps
### step
1

### instruction
Confirm that the pre-provisioned lab directory exists and is writable. This check is read-only.

### command
test -d /opt/lab-classroom/class76 && test -w /opt/lab-classroom/class76 && printf '%s\n' 'class76 directory is ready'
### step
2

### instruction
Create two explicitly labeled synthetic health reports.

### command
python3 - <<'PY'
from pathlib import Path
root = Path('/opt/lab-classroom/class76')
if not root.is_dir():
    raise SystemExit('Required lab directory does not exist')
(root / 'synthetic-sata.txt').write_text('''SYNTHETIC TRAINING DATA
Device Model: Academy SATA Example
SMART overall-health self-assessment test result: PASSED
ID# ATTRIBUTE_NAME          VALUE WORST THRESH RAW_VALUE
  5 Reallocated_Sector_Ct   100   100   010    0
194 Temperature_Celsius     066   055   000    34
197 Current_Pending_Sector  100   100   000    12
198 Offline_Uncorrectable   100   100   000    3
199 UDMA_CRC_Error_Count    200   199   000    41
''', encoding='utf-8')
(root / 'synthetic-nvme.txt').write_text('''SYNTHETIC TRAINING DATA
Model Number: Academy NVMe Example
Critical Warning:                   0x00
Temperature:                        39 Celsius
Available Spare:                    100%
Available Spare Threshold:          10%
Percentage Used:                    7%
Unsafe Shutdowns:                   2
Media and Data Integrity Errors:    4
Error Information Log Entries:      4
''', encoding='utf-8')
print('Synthetic fixtures created')
PY
### step
3

### instruction
Create a small classifier that demonstrates why overall health and Critical Warning fields must not be evaluated alone.

### command
python3 - <<'PY'
from pathlib import Path
root = Path('/opt/lab-classroom/class76')
program = '''from pathlib import Path
import re

ROOT = Path("/opt/lab-classroom/class76")

def sata_value(text, name):
    match = re.search(r"^\\s*\\d+\\s+" + re.escape(name) + r"\\s+\\d+\\s+\\d+\\s+\\d+\\s+(\\d+)", text, re.MULTILINE)
    return int(match.group(1)) if match else None

def named_number(text, label):
    match = re.search(r"^" + re.escape(label) + r":\\s+(\\d+)", text, re.MULTILINE)
    return int(match.group(1)) if match else None

sata = (ROOT / "synthetic-sata.txt").read_text(encoding="utf-8")
nvme = (ROOT / "synthetic-nvme.txt").read_text(encoding="utf-8")

pending = sata_value(sata, "Current_Pending_Sector")
uncorrectable = sata_value(sata, "Offline_Uncorrectable")
crc = sata_value(sata, "UDMA_CRC_Error_Count")
media_errors = named_number(nvme, "Media and Data Integrity Errors")
critical_warning = re.search(r"^Critical Warning:\\s+(0x[0-9a-fA-F]+)", nvme, re.MULTILINE)
critical_warning = critical_warning.group(1) if critical_warning else "missing"

print("SATA overall field: PASSED")
print(f"CRITICAL: SATA pending sectors={pending}; preserve evidence, verify recovery, and plan replacement.")
print(f"CRITICAL: SATA offline uncorrectable sectors={uncorrectable}; data could not be corrected.")
print(f"WARNING: SATA CRC error count={crc}; establish a baseline and inspect the transport path if it grows.")
print(f"NVMe Critical Warning field: {critical_warning}")
print(f"CRITICAL: NVMe media and data integrity errors={media_errors}; a zero Critical Warning field does not cancel this evidence.")
'''
(root / 'classify_health.py').write_text(program, encoding='utf-8')
print('Classifier created')
PY
### step
4

### instruction
Run the classifier without creating bytecode files.

### command
PYTHONDONTWRITEBYTECODE=1 python3 /opt/lab-classroom/class76/classify_health.py
### step
5

### instruction
Review the synthetic evidence manually and compare it with the classifier output.

### command
grep -E 'PASSED|Pending|Uncorrectable|CRC|Critical Warning|Percentage Used|Media and Data' /opt/lab-classroom/class76/synthetic-sata.txt /opt/lab-classroom/class76/synthetic-nvme.txt
### step
6

### instruction
Write a response note that stays inside the lab directory and records an appropriate operational decision.

### command
python3 - <<'PY'
from pathlib import Path
path = Path('/opt/lab-classroom/class76/operator-response.txt')
path.write_text('''Synthetic incident response
1. Preserve the complete health reports and relevant system logs.
2. Verify that backups are current and restorable.
3. Confirm array, pool, replica, or redundancy status before changing hardware.
4. Treat pending, uncorrectable, and NVMe media errors as high-signal evidence.
5. Check whether the SATA CRC count is increasing and inspect the transport path.
6. Schedule replacement through the platform-specific storage procedure.
7. Do not treat PASSED or a zero Critical Warning field as a guarantee.
''', encoding='utf-8')
print(path)
PY

### operational_extension
After the lab, an administrator may inspect real devices using approved read-only collection procedures. Device access, controller pass-through options, self-tests, and replacement operations must follow the host or storage-platform runbook and are intentionally excluded from this low-risk lab.

## Expected results

- The readiness check prints that the class76 directory is ready.
- The lab directory contains synthetic-sata.txt, synthetic-nvme.txt, classify_health.py, and operator-response.txt.
- The classifier reports critical SATA findings for 12 pending sectors and 3 offline uncorrectable sectors.
- The classifier reports the SATA CRC count as a transport-path warning that requires a baseline and trend analysis.
- The classifier reports four NVMe media and data integrity errors as critical evidence even though Critical Warning is 0x00.
- The student can explain why the synthetic SATA PASSED result does not override the detailed attributes.

## Verification checkpoints

- [ ] Run: test -s /opt/lab-classroom/class76/synthetic-sata.txt && test -s /opt/lab-classroom/class76/synthetic-nvme.txt && test -s /opt/lab-classroom/class76/classify_health.py && test -s /opt/lab-classroom/class76/operator-response.txt
- [ ] Run: PYTHONDONTWRITEBYTECODE=1 python3 /opt/lab-classroom/class76/classify_health.py | grep -F 'SATA pending sectors=12'
- [ ] Run: PYTHONDONTWRITEBYTECODE=1 python3 /opt/lab-classroom/class76/classify_health.py | grep -F 'SATA offline uncorrectable sectors=3'
- [ ] Run: PYTHONDONTWRITEBYTECODE=1 python3 /opt/lab-classroom/class76/classify_health.py | grep -F 'NVMe media and data integrity errors=4'
- [ ] Run: grep -F 'Do not treat PASSED or a zero Critical Warning field as a guarantee.' /opt/lab-classroom/class76/operator-response.txt
- [ ] Confirm verbally or in written notes that a growing CRC count normally directs initial investigation toward the cable, connector, backplane, power, controller, or transport path.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The readiness check produces no output or returns a nonzero status. | The pre-provisioned lab directory is missing or the current user cannot write to it. | Ask the lab administrator to provision /opt/lab-classroom/class76/ with appropriate ownership. Do not redirect the exercise to another path because the lab mutation boundary is mandatory. |
| Python reports PermissionError while creating a fixture. | The lab directory exists but is not writable by the current account. | Correct the lab directory ownership through the classroom provisioning process, then repeat the fixture-creation step. |
| The classifier reports a missing or None value. | A synthetic report was edited, truncated, or reformatted so that the teaching parser no longer matches it. | Re-run the fixture-creation step to restore the exact synthetic input and then execute the classifier again. |
| The synthetic SATA report says PASSED, causing the student to classify the device as healthy. | The student relied on the summary field and ignored pending and uncorrectable sectors. | Review the detailed attributes and classify Current_Pending_Sector and Offline_Uncorrectable as high-signal evidence requiring backup verification and replacement planning. |
| A nonzero CRC count is interpreted as definite media damage. | Transport errors and media errors were not separated. | Record the current CRC count, determine whether it is increasing, and investigate cables, connectors, backplanes, power, controllers, and related logs. |
| Real hardware exposes little or no useful health information. | A USB bridge, hardware RAID controller, HBA mode, virtual disk layer, or unsupported device path is hiding telemetry. | Consult the enclosure or controller documentation for supported pass-through methods and collect controller-native health information. Do not assume that absent telemetry means a healthy disk. |

## Security considerations

### principles
Treat direct block-device access as privileged. Grant it only to trusted administrators and narrowly scoped monitoring services.
Do not expose storage-health collection interfaces directly to untrusted networks.
Health reports may contain serial numbers, model numbers, firmware versions, topology, workload counters, and other inventory data useful to an attacker.
Store reports with access controls appropriate for infrastructure inventory and operational logs.
Do not run destructive write tests against disks that contain valuable data.
Verify backups and redundancy before attempting remediation on a suspect device.
Use stable device identity, such as a platform-approved persistent identifier, so an alert is not attached to the wrong disk after device enumeration changes.
Restrict monitoring automation to collection and alerting unless a separately reviewed runbook authorizes remediation.

### data_handling
The lab uses synthetic reports and does not collect identifiers from real hardware. If real reports are later attached to tickets, redact sensitive inventory fields according to organizational policy while preserving enough context for diagnosis.

## Rollback

### impact
The lab does not alter block devices, initiate self-tests, change services, or modify system configuration. It creates only four files in the designated class directory.

### procedure
Remove only the known lab-generated files with the following controlled command: python3 - <<'PY'
from pathlib import Path
root = Path('/opt/lab-classroom/class76')
for name in ('synthetic-sata.txt', 'synthetic-nvme.txt', 'classify_health.py', 'operator-response.txt'):
    path = root / name
    if path.is_file() or path.is_symlink():
        path.unlink()
print('Class 76 generated files removed')
PY

### verification
Run: test ! -e /opt/lab-classroom/class76/synthetic-sata.txt && test ! -e /opt/lab-classroom/class76/synthetic-nvme.txt && test ! -e /opt/lab-classroom/class76/classify_health.py && test ! -e /opt/lab-classroom/class76/operator-response.txt

## Video narration notes

Welcome to Class 76: SMART, Disk Health, and Failure Warning. The central rule for this class is simple: disk telemetry is evidence, not a guarantee. A drive that reports PASSED may still contain pending sectors or uncorrectable data. An NVMe device with a zero Critical Warning field may still report media and data integrity errors. Conversely, a historical counter may describe an old event rather than an active failure. Good operations require context and trends.

On SATA devices, pay special attention to pending sectors, offline uncorrectable sectors, reallocated sectors, reported uncorrectable errors, command timeouts, temperatures, and interface CRC errors. Do not assume that every raw value has universal units. Manufacturers define many of these encodings. Pending and uncorrectable sectors point toward data that could not be read reliably. CRC errors more often point toward the transport path, so inspect cables, connectors, backplanes, power, and controllers and determine whether the counter is increasing.

NVMe uses a different health structure. Review Critical Warning, temperature, available spare, spare threshold, Percentage Used, unsafe shutdowns, media and data integrity errors, and error log entries. Percentage Used estimates endurance consumption, not filesystem capacity. Critical Warning is a bit field rather than a complete statement about every historical error.

In the lab, we deliberately use synthetic reports. This keeps the exercise low risk and avoids changing a real drive's state. The SATA fixture says PASSED but contains twelve pending sectors and three offline uncorrectable sectors. It also contains a CRC count that should trigger transport-path investigation and trend monitoring. The NVMe fixture reports no critical-warning bits but records four media errors. The classifier demonstrates why operators must inspect specific conditions rather than trust one summary field.

When a real disk appears suspect, preserve the complete report and relevant system logs. Verify that backups are current and restorable. Confirm redundancy and identify the correct physical device. Avoid unnecessary load. Then use the storage platform's supported replacement process. Monitoring should retain historical reports, because a growing count is often more meaningful than a nonzero count by itself. Finally, remember that health telemetry complements backups, redundancy, filesystem checks, kernel logs, and application monitoring. It replaces none of them.

## References

- smartmontools project home: https://www.smartmontools.org/
- smartctl manual source: https://www.smartmontools.org/browser/trunk/smartmontools/smartctl.8.in
- smartd manual source: https://www.smartmontools.org/browser/trunk/smartmontools/smartd.8.in
- NVM Express specifications: https://nvmexpress.org/specifications/
- Linux kernel NVMe documentation: https://docs.kernel.org/nvme/index.html
- Linux kernel block subsystem documentation: https://docs.kernel.org/block/index.html

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

# Lab: SMART, Disk Health, and Failure Warning

**Module:** Segmentation, Backup & Power
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain what SMART can and cannot predict.

## Before you start

- Basic Linux command-line navigation
- Familiarity with block devices, filesystems, and storage redundancy
- Python 3 available for the synthetic-report lab
- The directory /opt/lab-classroom/class76/ must already exist and be writable by the student
- smartmontools is recommended for later host inspection but is not required for the synthetic lab

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

## Verification

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

## Security

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

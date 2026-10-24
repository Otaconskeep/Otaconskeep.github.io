# Reading: SMART, Disk Health, and Failure Warning

**Module:** Segmentation, Backup & Power
**Activity type:** Reading (Learn)
**Objective:** Explain what SMART can and cannot predict.

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

## Required reading

- smartctl manual page from the smartmontools project: https://www.smartmontools.org/browser/trunk/smartmontools/smartctl.8.in
- smartmontools documentation and device support information: https://www.smartmontools.org/wiki
- NVM Express specifications index, including the NVMe base specification: https://nvmexpress.org/specifications/
- Linux kernel documentation for NVMe: https://docs.kernel.org/nvme/index.html

## References

- smartmontools project home: https://www.smartmontools.org/
- smartctl manual source: https://www.smartmontools.org/browser/trunk/smartmontools/smartctl.8.in
- smartd manual source: https://www.smartmontools.org/browser/trunk/smartmontools/smartd.8.in
- NVM Express specifications: https://nvmexpress.org/specifications/
- Linux kernel NVMe documentation: https://docs.kernel.org/nvme/index.html
- Linux kernel block subsystem documentation: https://docs.kernel.org/block/index.html

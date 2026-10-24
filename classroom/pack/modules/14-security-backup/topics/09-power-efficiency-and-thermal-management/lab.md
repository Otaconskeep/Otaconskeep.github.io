# Lab: Power Efficiency and Thermal Management

**Module:** Segmentation, Backup & Power
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain the difference between energy, power, temperature, utilization, and efficiency.

## Before you start

- Comfort using a Linux shell and reading files under /proc and /sys.
- Basic understanding of CPU load, processes, storage devices, and system services.
- Python 3, awk, find, and standard GNU or compatible shell utilities.
- Permission to create and modify files only under /opt/lab-classroom/class78/.
- Physical or remote access sufficient to stop the lab if the host reports overheating, instability, fan failure, or an unexpected shutdown.

## Guided lab

### name
Observe idle, controlled load, and cooldown behavior

### scope
The lab reads Linux telemetry from /proc and /sys, creates a script and observation files under /opt/lab-classroom/class78/, and runs a short single-process CPU workload. It does not write to sysfs, alter a governor, modify a fan curve, install software, or make a persistent system configuration change.

### safety_notes
Do not perform the load phase on hardware with a failed fan, failed pump, known cooling fault, active thermal alarm, unstable power supply, or an unknown vendor temperature limit.
Keep an interactive session available. Press Ctrl-C if temperature rises unexpectedly, fans do not respond, the system becomes unstable, or monitoring reports throttling or an alarm.
The workload uses one Python process for a short interval. It is an observation stimulus, not a benchmark and not a cooling-system qualification test.
Virtual machines and containers may expose incomplete, virtualized, or host-controlled telemetry. Do not infer physical package temperature or wall power from unavailable sensors.
Record ambient conditions separately if a trustworthy room sensor is available. Do not substitute an internal motherboard sensor and label it as room ambient.

### steps
### step
1

### instruction
Create the class workspace with ownership assigned to the current user. This is the only persistent location modified by the lab.

### command
sudo install -d -o "$(id -un)" -g "$(id -gn)" -m 0750 /opt/lab-classroom/class78/
### step
2

### instruction
Inventory the read-only telemetry interfaces. Missing paths are acceptable and indicate that the platform, kernel, permissions, or virtualization layer does not expose that source.

### command
printf '%s\n' 'Thermal zones:'; ls -1 /sys/class/thermal/thermal_zone*/temp 2>/dev/null || true; printf '%s\n' 'CPU frequency files:'; ls -1 /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq 2>/dev/null || true; printf '%s\n' 'Energy counters:'; find /sys/class/powercap -type f -name energy_uj -print 2>/dev/null || true
### step
3

### instruction
Create the observation script. The CSV uses a long format so that systems with different sensor counts can be compared without inventing absent data.

### command
cat > /opt/lab-classroom/class78/run_lab.sh <<'EOF'
#!/bin/sh
set -eu
BASE=/opt/lab-classroom/class78
OUT="$BASE/observations.csv"
PID=""
cleanup() {
  if [ -n "$PID" ]; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM
printf 'timestamp,phase,metric,source,value,unit\n' > "$OUT"
record() {
  phase="$1"
  ts=$(date --iso-8601=seconds)
  load1=$(awk '{print $1}' /proc/loadavg)
  printf '%s,%s,load1,/proc/loadavg,%s,runnable_average\n' "$ts" "$phase" "$load1" >> "$OUT"
  for z in /sys/class/thermal/thermal_zone*; do
    [ -r "$z/temp" ] || continue
    raw=$(cat "$z/temp")
    type=$(cat "$z/type" 2>/dev/null | tr -d '\n' || printf unknown)
    value=$(awk -v r="$raw" 'BEGIN { printf "%.3f", r / 1000 }')
    printf '%s,%s,thermal_c,%s:%s,%s,C\n' "$ts" "$phase" "$z" "$type" "$value" >> "$OUT"
  done
  for f in /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq; do
    [ -r "$f" ] || continue
    value=$(cat "$f")
    printf '%s,%s,cpu_frequency,%s,%s,kHz\n' "$ts" "$phase" "$f" "$value" >> "$OUT"
  done
  find /sys/class/powercap -type f -name energy_uj -print 2>/dev/null | while IFS= read -r f; do
    [ -r "$f" ] || continue
    value=$(cat "$f")
    printf '%s,%s,energy_counter,%s,%s,uJ\n' "$ts" "$phase" "$f" "$value" >> "$OUT"
  done
}
record idle_start
sleep 10
record idle_end
python3 -c 'import hashlib,time
end=time.monotonic()+10
value=b"class78"
while time.monotonic()<end:
    value=hashlib.sha256(value).digest()' &
PID=$!
i=1
while [ "$i" -le 10 ]; do
  record "load_$i"
  sleep 1
  i=$((i + 1))
done
wait "$PID" || true
PID=""
sleep 15
record cooldown
printf 'Completed. Review %s\n' "$OUT"
EOF
chmod 0750 /opt/lab-classroom/class78/run_lab.sh
### step
4

### instruction
Record context needed to interpret the observations. Add only factual details known for the current system.

### command
{ date --iso-8601=seconds; uname -a; printf 'Virtualization: '; systemd-detect-virt 2>/dev/null || printf 'unknown\n'; printf 'Online CPUs: '; cat /sys/devices/system/cpu/online; printf 'Operator notes: workload state, room conditions, chassis condition, and active power profile should be documented before comparison.\n'; } > /opt/lab-classroom/class78/context.txt
### step
5

### instruction
Run the observation sequence while watching the host, its fans, and any available out-of-band thermal console.

### command
/opt/lab-classroom/class78/run_lab.sh
### step
6

### instruction
Inspect the collected rows without modifying system policy.

### command
sed -n '1,240p' /opt/lab-classroom/class78/observations.csv
### step
7

### instruction
Summarize which metrics were actually available. A zero count is a valid finding and must not be replaced with an assumed value.

### command
awk -F, 'NR>1 {count[$3]++} END {for (m in count) print m, count[m]}' /opt/lab-classroom/class78/observations.csv | sort > /opt/lab-classroom/class78/metric-counts.txt && cat /opt/lab-classroom/class78/metric-counts.txt

### analysis_questions
Which thermal zones changed during the load phase, and are their names specific enough to identify a component?
Did frequency observations vary by CPU, and could the samples represent momentary values rather than state residency?
Did the cooldown observation move toward the idle observations, remain elevated, or become unavailable?
If energy counters exist, which power domain does each counter represent, and can counter wraparound occur?
What environmental or workload variables could prevent a fair comparison with a later run?
Would a proposed optimization reduce total energy, merely reduce peak power, or only move heat and work to another device?

## Expected results

- The directory /opt/lab-classroom/class78/ contains run_lab.sh, context.txt, observations.csv, and metric-counts.txt after successful completion.
- The CSV contains time-stamped idle, load, and cooldown phases, with only the metrics exposed and readable on the current host.
- The controlled load may increase a reported CPU-related temperature or frequency, but the size and timing of any change are hardware-, policy-, workload-, and environment-specific.
- A virtual machine, container, or unsupported platform may show no thermal, frequency, or energy-counter rows; this is a valid result rather than evidence of zero temperature or zero energy use.
- Energy-counter values, when available, are cumulative values for named power domains and are not automatically whole-system wall-energy measurements.
- No CPU governor, firmware profile, power cap, thermal trip point, fan curve, service definition, or persistent operating-system configuration is changed.

## Verification

- [ ] Run `find /opt/lab-classroom/class78 -maxdepth 1 -type f -printf '%f\n' | sort` and confirm that the expected four files are present.
- [ ] Run `awk -F, 'NR==1 {ok=($1=="timestamp" && $2=="phase" && $3=="metric")} END {exit !ok}' /opt/lab-classroom/class78/observations.csv` and confirm that it exits successfully.
- [ ] Run `awk -F, 'NR>1 {phase[$2]=1} END {print ("idle_start" in phase), ("idle_end" in phase), ("load_1" in phase), ("cooldown" in phase)}' /opt/lab-classroom/class78/observations.csv` and confirm that all four printed indicators are 1.
- [ ] Run `find /opt/lab-classroom/class78 -xdev -type f -printf '%p %s bytes\n'` and review that all generated persistent files remain inside the permitted class directory.
- [ ] Review shell history and confirm that no command wrote to /sys, changed a CPU governor, changed a fan controller, modified firmware, or installed a package.
- [ ] If energy data is analyzed, verify the documented power domain and handle counter wraparound before calculating a delta.
- [ ] Repeat the lab only under comparable workload and environmental conditions if the results will be used to support an optimization decision.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Permission is denied while creating the class directory. | The current account cannot create directories under /opt or sudo is unavailable. | Ask the system owner to create /opt/lab-classroom/class78/ with ownership assigned to the lab user. Do not redirect persistent lab output to another location because the lab's mutation boundary is fixed. |
| No thermal-zone files are listed. | The kernel, hardware driver, container, or hypervisor does not expose thermal sensors through the generic thermal sysfs interface. | Record the absence in context.txt and use a vendor-supported read-only BMC, platform, or hypervisor interface outside this lab. Do not invent a temperature or treat absence as zero. |
| No CPU frequency files are listed. | The CPU frequency driver is unavailable, the platform uses another interface, permissions restrict access, or the environment is virtualized. | Continue with available metrics and document the limitation. Do not load new drivers or change firmware as part of this lab. |
| No energy_uj files are found. | The platform does not support the Linux powercap framework, the relevant driver is absent, or the interface is hidden from the guest. | Use the remaining observations. For future whole-system studies, use an appropriately rated and independently validated meter while following electrical safety requirements. |
| The Python workload does not start. | Python 3 is missing, execution is restricted, or process creation is limited. | Stop the lab and record that the load phase was not performed. Do not install software because package installation would violate the lab mutation boundary. |
| Temperature rises unexpectedly, a thermal alarm appears, or the system becomes unstable. | Cooling may be impaired, the environment may be too warm, telemetry may be delayed, or the platform may already be near a protective limit. | Press Ctrl-C, allow the host to cool, preserve the observations, and inspect cooling hardware according to vendor procedures. Do not disable throttling or thermal protection. |
| Energy-counter values decrease between samples. | The counter wrapped, reset, the system resumed from a power transition, or samples came from different power-domain instances. | Check the domain's max_energy_range_uj file when available, calculate wraparound correctly, and discard incomparable samples rather than reporting a negative energy use. |
| Temperature remains elevated at the cooldown sample. | Thermal mass, slow fan policy, another workload, high ambient temperature, or hot-air recirculation may delay cooling. | Do not assume failure from one sample. Stop additional load, inspect active processes and airflow, and collect a longer read-only cooldown series if the hardware remains within vendor limits. |

## Security

Treat BMC, UPS, smart-plug, and power-distribution telemetry as administrative data because it can reveal occupancy, workload timing, hardware inventory, and operational patterns.
Use least-privilege read access for monitoring. This lab deliberately avoids writable sysfs controls and persistent power-management changes.
Do not place BMC or metering credentials in scripts, CSV files, shell history, screenshots, or homework submissions.
Preserve an out-of-band recovery method before experimenting with production power policies. An aggressive policy can impair remote access, storage availability, or network links.
Do not disable thermal throttling, thermal shutdown, fan-failure alarms, or power-supply protection mechanisms.
Consider availability and fault domains before consolidating services. Powering down a redundant node may save energy while removing resilience.
Keep collected files at mode 0750 or stricter when they include hardware identifiers or operational schedules.

## Rollback

### impact
The observation workload ends automatically and makes no persistent system-policy changes. Rollback consists only of removing the four files created in the class workspace.

### command
rm -f /opt/lab-classroom/class78/run_lab.sh /opt/lab-classroom/class78/context.txt /opt/lab-classroom/class78/observations.csv /opt/lab-classroom/class78/metric-counts.txt

### verification
Run `find /opt/lab-classroom/class78 -maxdepth 1 -type f -print` and confirm that it prints no files. The class directory may remain in place.

### recovery
If the files were removed unintentionally, recreate and rerun the lab. The measurements cannot be reconstructed exactly because workload and environmental conditions change over time.

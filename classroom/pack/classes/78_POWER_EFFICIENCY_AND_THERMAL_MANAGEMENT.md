# Class 78: Power Efficiency and Thermal Management

**Learning objective:** Explain the difference between energy, power, temperature, utilization, and efficiency.; Describe how dynamic voltage and frequency scaling, idle states, workload placement, airflow, and ambient temperature interact.; Collect repeatable thermal, load, frequency, and optional energy-counter observations without changing system power policy.; Compare idle, controlled-load, and cooldown phases while accounting for sensor availability and measurement limitations.; Recognize thermal throttling, inadequate cooling, obstructed airflow, and inefficient always-on workloads.; Develop a staged optimization plan that preserves reliability, storage integrity, service availability, and remote recoverability.; Verify that an efficiency change improves the intended metric rather than merely shifting heat, latency, or energy use elsewhere.
**Bloom level:** Understand / Apply
**Track:** Homelab Operations and Reliability · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** low
**Build output:** Teach homelab operators how to observe power and thermal behavior, distinguish useful measurements from misleading snapshots, identify common sources of wasted energy and heat, and make evidence-based optimization decisions without changing firmware, kernel, fan, or power-management settings during the lab.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### operating_systems
Linux systems exposing standard /proc interfaces
Linux systems that may optionally expose thermal sysfs, CPU frequency sysfs, or powercap energy counters

### shell
POSIX-compatible /bin/sh with common Linux userland utilities

### runtime
Python 3 is required only for the short controlled workload.

### virtualization
The lab can run in a virtual machine or container, but physical thermal, frequency, and energy telemetry may be hidden, virtualized, or controlled by the host.

### hardware_notes
Sensor names, domains, units, update rates, power-policy interfaces, protective limits, and counter ranges are platform-specific. Consult the exact vendor documentation before making production changes.

### mutation_boundary
/opt/lab-classroom/class78/

## Learning objective

- Explain the difference between energy, power, temperature, utilization, and efficiency.
- Describe how dynamic voltage and frequency scaling, idle states, workload placement, airflow, and ambient temperature interact.
- Collect repeatable thermal, load, frequency, and optional energy-counter observations without changing system power policy.
- Compare idle, controlled-load, and cooldown phases while accounting for sensor availability and measurement limitations.
- Recognize thermal throttling, inadequate cooling, obstructed airflow, and inefficient always-on workloads.
- Develop a staged optimization plan that preserves reliability, storage integrity, service availability, and remote recoverability.
- Verify that an efficiency change improves the intended metric rather than merely shifting heat, latency, or energy use elsewhere.

## Why this matters

Teach homelab operators how to observe power and thermal behavior, distinguish useful measurements from misleading snapshots, identify common sources of wasted energy and heat, and make evidence-based optimization decisions without changing firmware, kernel, fan, or power-management settings during the lab.

## Prerequisites

- Comfort using a Linux shell and reading files under /proc and /sys.
- Basic understanding of CPU load, processes, storage devices, and system services.
- Python 3, awk, find, and standard GNU or compatible shell utilities.
- Permission to create and modify files only under /opt/lab-classroom/class78/.
- Physical or remote access sufficient to stop the lab if the host reports overheating, instability, fan failure, or an unexpected shutdown.

## Required reading

- Linux kernel documentation: CPU frequency and voltage scaling, https://docs.kernel.org/admin-guide/pm/cpufreq.html
- Linux kernel documentation: CPU idle time management, https://docs.kernel.org/admin-guide/pm/cpuidle.html
- Linux kernel documentation: Generic thermal sysfs driver interface, https://docs.kernel.org/driver-api/thermal/sysfs-api.html
- Linux kernel documentation: Power capping framework, https://docs.kernel.org/power/powercap/powercap.html
- Review the processor, motherboard, storage, chassis, fan, and power-supply thermal limits published by the actual hardware vendors before changing any production setting.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Power | The instantaneous rate of energy use, commonly measured in watts. A power reading describes what is happening at a particular moment or over a short averaging interval. |
| Energy | Power accumulated over time, commonly expressed as watt-hours or joules. Electricity cost is based primarily on energy, not a single instantaneous power reading. |
| Thermal headroom | The margin between current operating temperature and a hardware-defined temperature at which throttling, protection, or shutdown behavior may occur. |
| DVFS | Dynamic voltage and frequency scaling, which adjusts processor operating frequency and voltage in response to policy, demand, and platform constraints. |
| C-state | A processor idle state. Deeper idle states can reduce power but may introduce additional wake latency and depend on firmware, kernel, drivers, and workload behavior. |
| P-state | A processor performance state or performance request associated with operating frequency and voltage behavior. Exact implementation differs among platforms. |
| Thermal throttling | Automatic reduction of performance or activity to keep a component within its protective operating limits. |
| TDP | A vendor-specific thermal design figure used for platform and cooling design. It is not necessarily the processor's fixed power consumption or maximum electrical draw. |
| Power cap | A hardware or software-enforced constraint on energy or power consumption, such as an interface exposed through the Linux powercap framework. |
| Workload consolidation | Placing compatible services on fewer active systems so other systems can enter deeper idle states or be powered off, while still preserving capacity and fault-domain requirements. |
| Thermal soak | The gradual rise toward a steady temperature after a workload begins. A brief sample may end before the chassis, heatsink, or coolant reaches equilibrium. |
| Fan curve | A controller policy mapping temperature or other sensor input to fan speed. Poorly chosen curves can cause excess noise, temperature oscillation, or inadequate cooling. |

## Instruction

Power efficiency is not the same as low utilization, low temperature, or low instantaneous wattage. Power is a rate, while energy is power integrated over time. A server drawing modest power continuously may consume more energy than a faster server that completes work promptly and returns to an effective idle state. Temperature is also not a direct measurement of electrical power. It reflects heat generation, heat transfer, sensor location, ambient conditions, airflow, thermal mass, and controller behavior. Two systems consuming similar power can report different temperatures because their cooling paths and sensor placements differ.

Modern processors coordinate frequency selection, voltage, boost behavior, idle states, package limits, firmware policy, and operating-system policy. A high frequency reading does not by itself prove waste, because some interfaces report requested, nominal, or momentary frequency rather than residency over time. Likewise, a low load average does not prove that the package can enter deep idle states. Frequent timers, polling applications, high interrupt rates, busy storage, chatty virtual machines, network broadcasts, and poorly behaving device drivers can repeatedly wake the system. Efficient operation therefore requires correlated observations rather than one number.

Cooling should be treated as a complete path: room air enters the chassis, passes through filters and component heatsinks, and exits without being immediately recirculated. Dust, blocked intake space, reversed fans, loose heatsinks, dried thermal-interface material, failed pumps, cable obstructions, and mixed airflow directions can all reduce thermal headroom. Increasing fan speed may lower component temperature while increasing acoustic noise and fan power; reducing fan speed may save little energy while shortening component life. Vendor limits and platform telemetry must govern these decisions.

Measurement quality matters. Record ambient conditions, firmware mode, kernel version, active services, fan policy, and workload state. Compare equivalent time windows, allow for thermal soak, and repeat observations. On-host energy counters may cover only a CPU package or another limited power domain; they are not automatically equivalent to whole-system wall power. UPS and smart-plug readings may include conversion loss or multiple attached devices. BMC sensor update intervals may be slower than workload changes. The correct conclusion is often a range or trend rather than a universal wattage claim.

Optimization should proceed from reversible and well-observed changes. Remove genuinely unnecessary work, schedule batch jobs intelligently, enable application sleep or backoff behavior, right-size virtual machines, and consider consolidating compatible services. Then evaluate operating-system and firmware power policies with an out-of-band recovery path. Undervolting, custom fan control, disabling thermal protection, or forcing unsupported power limits can create silent computation errors, storage failures, abrupt shutdowns, or loss of remote access and are outside this lab. Reliability is part of efficiency: a small energy reduction is not a success if it causes retries, data corruption, premature hardware replacement, or service outages.

## Architecture

### model
Observe, correlate, decide, change, and verify

### layers
### layer
Facility and room

### concerns
Ambient temperature and humidity
Rack or shelf spacing
Hot-air recirculation
UPS conversion losses
Shared circuit capacity
### layer
Chassis and cooling

### concerns
Intake and exhaust direction
Dust and filter restriction
Fan and pump health
Heatsink mounting
Cable obstruction
### layer
Platform

### concerns
Firmware power profile
CPU and device idle support
Thermal trip behavior
BMC sensor visibility
Power-supply efficiency and redundancy mode
### layer
Operating system

### concerns
CPU frequency policy
Idle-state availability
Interrupt and timer activity
Storage power policy
Driver support
### layer
Workload

### concerns
Useful work per unit of energy
Polling and wakeups
Batch scheduling
Virtual-machine right-sizing
Service consolidation and availability constraints

### measurement_flow
Sensors and counters feed a time-stamped observation set. Observations are correlated with workload phases and environmental notes. A hypothesis is then tested with one reversible change at a time, followed by the same observation procedure.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### assignment
Create a table identifying every metric present in observations.csv, its unit, its likely measurement domain, and one limitation.
Compare idle_end with the load-phase and cooldown observations without claiming that the short workload is a benchmark.
If an energy counter is available, research its max_energy_range_uj and explain how wraparound would be handled. Do not report a whole-system wattage unless the counter is documented to cover the whole system.
Write a three-stage optimization proposal: one workload-level change, one cooling or airflow inspection, and one policy change requiring a separate maintenance window.
For each proposal, define the success metric, reliability guardrail, rollback trigger, and measurement method.
Identify one service that may wake the system frequently and describe a read-only method for investigating it in a future lab.

### submission_requirements
Submit context.txt, metric-counts.txt, a concise interpretation of available data, documented limitations, and the staged proposal. Remove hostnames, serial numbers, addresses, credentials, and other sensitive infrastructure identifiers.

## Feynman teach-back

### plain_language_explanation
A server turns electrical energy into useful computation and heat. Power tells us how quickly it is using energy right now; energy tells us how much it used over a period. Temperature tells us how successfully heat is moving from a component to the surrounding air, not exactly how much electricity the entire server consumes. To improve efficiency, first observe an idle period, a known piece of work, and a cooldown period. Then change only one thing and repeat the same observation. A change is useful only if it reduces the intended energy cost while preserving correct results, acceptable response time, safe temperatures, and required reliability.

### teach_back_prompts
Explain why a cooler CPU is not automatically a more energy-efficient CPU.
Explain why a short wall-power reading cannot establish monthly energy use.
Describe how a polling service can waste energy even when average CPU utilization appears low.
Explain why consolidating services can improve idle efficiency but reduce fault tolerance.
Describe why a CPU package energy counter cannot automatically be presented as whole-server energy.

### misconception_check
If your explanation relies on one temperature, one frequency, or one instantaneous power value, add time, workload context, measurement scope, and environmental conditions before drawing a conclusion.

## Retrieval check

1. What is the difference between power and energy?
2. Why does a lower component temperature not necessarily prove lower electrical power consumption?
3. What can prevent an apparently idle Linux system from entering deep CPU idle states?
4. Why should a CPU package energy counter not automatically be treated as whole-system energy?
5. What is thermal throttling, and why should it not be disabled to improve benchmark performance?
6. Why can workload consolidation improve energy efficiency while also increasing operational risk?
7. What information should be held constant or recorded when comparing two power-management configurations?
8. Why is a brief load-and-cooldown lab not sufficient to certify a cooling design?
9. What should an operator do if a thermal alarm appears during the controlled load?
10. What constitutes a successful efficiency change?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

Welcome to Class 78, Power Efficiency and Thermal Management. Our goal is not to chase the lowest temperature or force the lowest CPU frequency. Our goal is to understand how useful work, energy, heat, cooling, and reliability interact.

Begin with the measurement vocabulary. Power is a rate, usually expressed in watts. Energy is accumulated power over time. Temperature is the result of heat generation and heat transfer. A temperature sensor does not directly tell us whole-system power, and a CPU energy counter does not necessarily include memory, disks, fans, network devices, or power-supply losses.

The architecture spans several layers. Room temperature and air recirculation affect the chassis. Chassis airflow and cooling hardware affect component temperature. Firmware controls protective behavior and may select a power profile. Linux coordinates frequency and idle policies where the platform permits it. Applications determine whether the machine can remain idle or is repeatedly awakened by timers, polling, interrupts, storage, and network activity.

In the lab, we make no policy changes. We create files only under the class directory, inventory available telemetry, and collect a long-format CSV. The sequence records an idle period, runs one short Python process, samples during that controlled load, and records a cooldown observation. This is not a benchmark. It provides a repeatable stimulus for learning how the available sensors respond.

Some systems will expose thermal zones, per-CPU frequency files, and powercap energy counters. Others will expose only part of that information. A guest virtual machine may expose none of it. Missing telemetry is a limitation to document, not a value of zero. If an energy counter is present, determine the domain it measures and account for counter wraparound before calculating a delta.

Watch the host during the load. Stop immediately if a thermal alarm appears, cooling hardware behaves abnormally, or the system becomes unstable. Never disable thermal protection to complete a lab. After collection, compare the phases while considering sensor update intervals, thermal mass, background workloads, and room conditions.

A sound optimization process changes one variable at a time and repeats the same measurement. Start by removing unnecessary work and reducing excessive polling. Consider workload scheduling and right-sizing. Inspect airflow and cooling before changing fan controls. Evaluate firmware or operating-system policies only in a separate maintenance window with rollback and remote recovery. The winning configuration is not simply the one with the lowest instantaneous reading. It is the one that reduces the intended energy cost while preserving correct work, acceptable performance, safe operation, and the resilience your homelab requires.

## References

- Linux kernel CPU frequency and voltage scaling documentation: https://docs.kernel.org/admin-guide/pm/cpufreq.html
- Linux kernel CPU idle time management documentation: https://docs.kernel.org/admin-guide/pm/cpuidle.html
- Linux kernel generic thermal sysfs driver interface: https://docs.kernel.org/driver-api/thermal/sysfs-api.html
- Linux kernel power capping framework documentation: https://docs.kernel.org/power/powercap/powercap.html
- Linux kernel hwmon subsystem documentation: https://docs.kernel.org/hwmon/hwmon-kernel-api.html
- The Green Grid, Data Center Power Efficiency Metrics: PUE and DCiE, https://www.thegreengrid.org/
- ASHRAE Technical Committee 9.9, Data Center Resources: https://tc0909.ashraetcs.org/
- ENERGY STAR computer server resources: https://www.energystar.gov/products/data_center_equipment/computer_servers
- Vendor documentation for the exact processor, motherboard, chassis, cooling system, storage devices, power supply, UPS, and BMC deployed in the lab.

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

# Class 41 — Sonarr Series Monitoring and Availability

**Learning objective:** Differentiate monitored state from missing, available, downloaded, and cutoff-unmet states; Explain how series-, season-, and episode-level monitoring decisions affect release eligibility; Predict whether an episode is waiting for an air date, waiting for availability, missing, cutoff unmet, satisfied, or intentionally unmonitored; Explain the difference between RSS-style release processing, automatic search, and interactive search; Select monitoring policies appropriate for continuing series, completed archives, pilots, and newly added series; Audit monitoring choices without initiating downloads or changing a production Sonarr instance
**Bloom level:** Understand / Apply
**Track:** Media Automation · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach administrators how Sonarr monitoring, episode state, release availability, quality cutoffs, and search behavior interact. The lesson emphasizes predicting Sonarr's decisions before changing a production library.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### target
Sonarr v4 concepts and contemporary Servarr terminology

### notes
Exact labels, icons, monitoring shortcuts, and menu locations can vary between Sonarr releases.
The core distinctions among monitored, missing, future, cutoff unmet, and satisfied remain applicable.
The lab requires Python 3 and standard Linux command-line utilities but does not require Sonarr to be installed.
The fixture uses fixed dates so its output remains deterministic regardless of the current date.
Administrators should verify version-specific availability options and search controls in the installed release before applying production changes.

## Learning objective

- Differentiate monitored state from missing, available, downloaded, and cutoff-unmet states
- Explain how series-, season-, and episode-level monitoring decisions affect release eligibility
- Predict whether an episode is waiting for an air date, waiting for availability, missing, cutoff unmet, satisfied, or intentionally unmonitored
- Explain the difference between RSS-style release processing, automatic search, and interactive search
- Select monitoring policies appropriate for continuing series, completed archives, pilots, and newly added series
- Audit monitoring choices without initiating downloads or changing a production Sonarr instance

## Why this matters

Teach administrators how Sonarr monitoring, episode state, release availability, quality cutoffs, and search behavior interact. The lesson emphasizes predicting Sonarr's decisions before changing a production library.

## Prerequisites

- Basic familiarity with Sonarr series, seasons, episodes, and quality profiles
- Ability to read JSON and run Python 3 from a terminal
- Permission to create files under /opt/lab-classroom/class41/
- A conceptual understanding of download clients and indexers; neither is required for this lab
- Completion of earlier Sonarr installation and library organization lessons, or equivalent experience

## Required reading

- Sonarr documentation home: https://wiki.servarr.com/sonarr
- Sonarr Quick Start Guide: https://wiki.servarr.com/sonarr/quick-start-guide
- Sonarr Library documentation: https://wiki.servarr.com/sonarr/library
- Sonarr FAQ: https://wiki.servarr.com/sonarr/faq

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Monitored | A policy flag indicating that Sonarr may consider a series, season, or episode for acquisition or upgrade. Monitoring creates eligibility; it does not guarantee that a release will be found, accepted, or downloaded. |
| Missing | An episode that is expected to be available, has no associated media file, and is monitored. An unmonitored episode without a file is intentionally ignored rather than actionable missing content. |
| Minimum availability | The configured point at which Sonarr may treat content as eligible for acquisition. Labels and date behavior can vary by Sonarr version and metadata, so the effective date should be verified in the episode or series details. |
| Air date | Metadata describing when an episode is scheduled to air. Time zones, delayed releases, streaming schedules, and incorrect metadata can affect the apparent state. |
| Quality profile | An ordered set of allowed qualities and an upgrade cutoff used to decide whether a release is acceptable and whether an existing file should be upgraded. |
| Cutoff unmet | A monitored episode already has a file, but the file's quality has not reached the quality profile cutoff. Sonarr may continue seeking an acceptable upgrade. |
| RSS sync | Periodic processing of newly published indexer releases. It is not a historical search of every missing episode. |
| Automatic search | A search initiated by Sonarr to locate a suitable release for one or more monitored episodes. |
| Interactive search | A user-requested search that displays candidate releases and rejection reasons so the administrator can inspect or select a result. |
| Series type | A Sonarr setting, such as standard, daily, or anime, that influences release parsing and episode identification. |
| Release eligibility | The combined result of monitoring, dates, quality policy, release restrictions, indexer results, and download-client readiness. It is broader than the monitored flag alone. |

## Instruction

Sonarr monitoring is an expression of intent, not a promise that a file will appear. A monitored episode becomes a candidate for acquisition only when its scheduling and availability conditions are met. It must then have an acceptable release from a working indexer, pass the quality profile and any release restrictions, and be sent successfully to a download client. If any part of that chain fails, the episode can remain missing even though monitoring is enabled. Monitoring is hierarchical: choices made while adding a series commonly establish episode-level states across seasons, but later season or episode changes can create intentional exceptions. Always inspect the effective episode state rather than assuming the top-level series icon tells the whole story.

A useful mental model is to classify each episode in order. First ask whether it is monitored. If not, Sonarr should generally ignore it. Next ask whether the episode has reached its relevant air or availability date. If not, it is waiting rather than missing. If it is monitored and available but has no file, it is missing and can be a search target. If it has a file, compare that file with the assigned quality profile. A file below the cutoff can be cutoff unmet, while a file at or above the cutoff is normally satisfied. Custom formats, language policy, release exclusions, and profile scoring can further affect whether a candidate is accepted.

Monitoring options are shortcuts for establishing intent. All episodes is suitable when a complete collection is desired. Future episodes is useful when existing history should be left alone but upcoming episodes should be acquired. Missing episodes targets known gaps without necessarily replacing files that already exist. Existing episodes preserves focus on already imported content, while none disables automated acquisition. Version-specific interfaces may also offer first-season, latest-season, or pilot-oriented choices. Confirm the resulting episode flags after using any shortcut.

RSS processing and backlog searching must also be distinguished. RSS sync examines newly posted releases from configured indexers and compares them with current needs. It does not continuously search an indexer's entire history. A newly monitored old episode may therefore remain missing until an automatic or interactive search is performed, or until a matching release is reposted. Interactive search is the best diagnostic tool because it exposes rejected candidates and their reasons. Before launching a broad search, review the number of monitored episodes, profile assignment, free storage, download-client limits, and indexer limits. This prevents a monitoring correction from unexpectedly creating a large acquisition queue.

## Architecture

### decision_flow
Series, season, and episode monitoring choices establish acquisition intent.
Episode metadata supplies air dates, availability dates, numbering, and series type.
The assigned quality profile defines allowed qualities and an upgrade cutoff.
RSS sync or a deliberate search obtains candidate releases from configured indexers.
Sonarr evaluates candidates against monitoring state, dates, quality, custom formats, language, and release restrictions.
An accepted release is sent to a download client.
After completion, Sonarr imports the file and updates episode-file state.

### state_model
For this lesson, an episode is classified in this order: unmonitored; waiting for its air date; waiting for a later availability date; missing; cutoff unmet; or satisfied. Production Sonarr evaluates additional policy and integration details, but this ordering is a reliable troubleshooting foundation.

### boundaries
Sonarr decides what it wants and coordinates acquisition. Indexers report releases, download clients transfer data, and the filesystem provides storage. A failure in one component must not be diagnosed solely from the monitored icon.

### lab_design
The lab uses an offline JSON inventory and a local Python classifier. It does not connect to Sonarr, indexers, download clients, or media storage.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Design monitoring policies for three cases: a currently airing favorite, a completed archival series with intentional gaps, and a new series for which only the pilot is desired.
For each case, state whether historical searches should be run and what checks must occur before searching.
Add a new episode to a copy of the lab inventory that is monitored, available, has a Bluray-1080p file, and should classify as satisfied.
Add another episode with an unknown quality label and explain why manual review is safer than silently assigning a rank.
Create a one-page operational checklist for reviewing monitored counts, missing counts, cutoff-unmet counts, storage capacity, indexer health, and download-client readiness before a bulk search.

## Feynman teach-back

### prompt
Explain monitoring to a family member who thinks selecting a show means every episode will immediately download.

### model_explanation
Monitoring tells Sonarr which episodes it is allowed to care about. Sonarr still waits until an episode is considered available, looks for releases through an indexer, rejects releases that do not meet the rules, and asks a download client to transfer an accepted one. An old missing episode may also need a deliberate historical search because the normal feed mainly evaluates newly posted releases. A file can already exist and still be monitored for an upgrade if it has not reached the quality cutoff.

### self_check
Your explanation should separately mention intent, availability, searching, acceptance rules, downloading, and quality upgrades. If monitored and downloaded are used as synonyms, revise the explanation.

## Retrieval check

1. 1. Does enabling monitoring guarantee that Sonarr will download an episode immediately?
2. 2. What is the practical difference between a monitored missing episode and an unmonitored episode with no file?
3. 3. Why can an old episode remain missing after monitoring is enabled?
4. 4. What does cutoff unmet mean?
5. 5. Why should air date and minimum availability be checked separately?
6. 6. What is the safest Sonarr search mode for diagnosing why candidate releases are rejected?
7. 7. If an existing below-cutoff file is unmonitored, should the basic state model classify it as an upgrade candidate?
8. 8. Name four systems or policies, in addition to monitoring, that can prevent acquisition.

## Guided lab

### name
Model Monitoring and Availability Decisions Safely

### safety_scope
Every file created or changed by this lab is under /opt/lab-classroom/class41/. The exercise does not alter a real Sonarr database, library, container, service, or download queue.

### steps
### step
1

### title
Create the isolated fixture directory

### instructions
Create the class directory. If it already contains work, inspect it before proceeding and use a separate child directory if preservation is required.

### command
sudo install -d -m 0755 /opt/lab-classroom/class41
### step
2

### title
Create the baseline episode inventory

### instructions
Write a deterministic inventory using 2025-03-01 as the evaluation date. Monitoring is represented explicitly at episode level so each decision can be audited.

### command
sudo tee /opt/lab-classroom/class41/baseline.json >/dev/null <<'EOF'
{
  "as_of": "2025-03-01",
  "quality_profile": {
    "cutoff": "WEB-1080p",
    "ranking": {
      "SDTV": 1,
      "HDTV-720p": 2,
      "WEB-1080p": 3,
      "Bluray-1080p": 4
    }
  },
  "episodes": [
    {
      "series": "Harbor Signal",
      "episode": "S01E01",
      "air_date": "2025-01-10",
      "availability_date": "2025-01-10",
      "monitored": false,
      "has_file": true,
      "quality": "WEB-1080p"
    },
    {
      "series": "Harbor Signal",
      "episode": "S01E02",
      "air_date": "2025-02-14",
      "availability_date": "2025-02-14",
      "monitored": true,
      "has_file": false,
      "quality": null
    },
    {
      "series": "Harbor Signal",
      "episode": "S01E03",
      "air_date": "2025-03-15",
      "availability_date": "2025-03-16",
      "monitored": true,
      "has_file": false,
      "quality": null
    },
    {
      "series": "Archive Lane",
      "episode": "S02E01",
      "air_date": "2024-10-01",
      "availability_date": "2024-10-01",
      "monitored": true,
      "has_file": false,
      "quality": null
    },
    {
      "series": "Archive Lane",
      "episode": "S02E02",
      "air_date": "2024-10-08",
      "availability_date": "2024-10-08",
      "monitored": false,
      "has_file": true,
      "quality": "HDTV-720p"
    },
    {
      "series": "Current Affairs",
      "episode": "2025-02-21",
      "air_date": "2025-02-21",
      "availability_date": "2025-02-21",
      "monitored": true,
      "has_file": true,
      "quality": "HDTV-720p"
    },
    {
      "series": "Current Affairs",
      "episode": "2025-02-28",
      "air_date": "2025-02-28",
      "availability_date": "2025-03-03",
      "monitored": true,
      "has_file": false,
      "quality": null
    }
  ]
}
EOF
sudo cp /opt/lab-classroom/class41/baseline.json /opt/lab-classroom/class41/inventory.json
### step
3

### title
Create the offline classifier

### instructions
The classifier applies the lesson's ordered state model and prints one auditable decision for every episode.

### command
sudo tee /opt/lab-classroom/class41/audit.py >/dev/null <<'PY'
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

root = Path('/opt/lab-classroom/class41')
source = root / (sys.argv[1] if len(sys.argv) > 1 else 'inventory.json')
source = source.resolve()
if root.resolve() not in source.parents:
    raise SystemExit('Input must remain inside the class41 directory')

with source.open(encoding='utf-8') as handle:
    data = json.load(handle)

as_of = date.fromisoformat(data['as_of'])
ranking = data['quality_profile']['ranking']
cutoff = data['quality_profile']['cutoff']
cutoff_rank = ranking[cutoff]
counts = Counter()

for item in data['episodes']:
    air_date = date.fromisoformat(item['air_date'])
    availability_date = date.fromisoformat(item['availability_date'])
    if not item['monitored']:
        state = 'unmonitored'
    elif as_of < air_date:
        state = 'waiting_future_air_date'
    elif as_of < availability_date:
        state = 'waiting_minimum_availability'
    elif not item['has_file']:
        state = 'missing_search_candidate'
    elif item['quality'] not in ranking:
        state = 'manual_review_unknown_quality'
    elif ranking[item['quality']] < cutoff_rank:
        state = 'cutoff_unmet_upgrade_candidate'
    else:
        state = 'satisfied'
    counts[state] += 1
    print(f"{item['series']} {item['episode']}: {state}")

print('SUMMARY')
for state in sorted(counts):
    print(f'{state}={counts[state]}')
PY
sudo python3 /opt/lab-classroom/class41/audit.py inventory.json
### step
4

### title
Explain every baseline decision

### instructions
For each output line, identify the first test that determined the state. Notice that Archive Lane S02E02 remains unmonitored even though its file is below the configured cutoff. Monitoring must be enabled before it becomes an upgrade candidate.
### step
5

### title
Model a monitoring-policy change

### instructions
Create a separate scenario that stops monitoring Archive Lane S02E01 and starts monitoring Archive Lane S02E02. This represents changing intent without altering the baseline.

### command
sudo python3 - <<'PY'
import json
from pathlib import Path
root = Path('/opt/lab-classroom/class41')
with (root / 'baseline.json').open(encoding='utf-8') as handle:
    data = json.load(handle)
for item in data['episodes']:
    key = (item['series'], item['episode'])
    if key == ('Archive Lane', 'S02E01'):
        item['monitored'] = False
    if key == ('Archive Lane', 'S02E02'):
        item['monitored'] = True
with (root / 'monitoring-scenario.json').open('w', encoding='utf-8') as handle:
    json.dump(data, handle, indent=2)
    handle.write('\n')
PY
sudo python3 /opt/lab-classroom/class41/audit.py monitoring-scenario.json
### step
6

### title
Model an availability correction

### instructions
Create another scenario in which metadata says Current Affairs 2025-02-28 became available on its air date. Compare this with the baseline, where the episode waits until 2025-03-03.

### command
sudo python3 - <<'PY'
import json
from pathlib import Path
root = Path('/opt/lab-classroom/class41')
with (root / 'baseline.json').open(encoding='utf-8') as handle:
    data = json.load(handle)
for item in data['episodes']:
    if item['series'] == 'Current Affairs' and item['episode'] == '2025-02-28':
        item['availability_date'] = '2025-02-28'
with (root / 'availability-scenario.json').open('w', encoding='utf-8') as handle:
    json.dump(data, handle, indent=2)
    handle.write('\n')
PY
sudo python3 /opt/lab-classroom/class41/audit.py availability-scenario.json
### step
7

### title
Relate the model to a real Sonarr interface without changing it

### instructions
If a Sonarr instance is available, use read-only observation to find one monitored episode, one unmonitored episode, one missing episode, and one episode with a file. Record the visible status, air date, profile, and any rejection reasons shown by an interactive-search view. Do not initiate a grab, edit monitoring, trigger a search, or enter credentials into the lab files.

## Expected results

- The baseline classifies Harbor Signal S01E01 as unmonitored.
- The baseline classifies Harbor Signal S01E02 and Archive Lane S02E01 as missing search candidates.
- The baseline classifies Harbor Signal S01E03 as waiting for a future air date.
- The baseline classifies Archive Lane S02E02 as unmonitored even though its file is below the quality cutoff.
- The baseline classifies Current Affairs 2025-02-21 as a cutoff-unmet upgrade candidate.
- The baseline classifies Current Affairs 2025-02-28 as waiting for minimum availability.
- The monitoring scenario changes Archive Lane S02E01 to unmonitored and Archive Lane S02E02 to a cutoff-unmet upgrade candidate.
- The availability scenario changes Current Affairs 2025-02-28 from waiting for availability to a missing search candidate.

## Verification checkpoints

- [ ] Run `sudo python3 /opt/lab-classroom/class41/audit.py inventory.json` and confirm that the summary includes unmonitored=2, missing_search_candidate=2, waiting_future_air_date=1, waiting_minimum_availability=1, and cutoff_unmet_upgrade_candidate=1.
- [ ] Run `sudo python3 /opt/lab-classroom/class41/audit.py monitoring-scenario.json` and confirm that Archive Lane S02E01 is unmonitored while Archive Lane S02E02 is cutoff unmet.
- [ ] Run `sudo python3 /opt/lab-classroom/class41/audit.py availability-scenario.json` and confirm that Current Affairs 2025-02-28 is a missing search candidate.
- [ ] Run `sudo cmp /opt/lab-classroom/class41/baseline.json /opt/lab-classroom/class41/inventory.json` immediately after setup; no output and a zero exit status confirm the working inventory initially matches the baseline.
- [ ] Run `sudo find /opt/lab-classroom/class41 -maxdepth 1 -type f -printf '%f\n' | sort` and confirm that all lab artifacts remain inside the designated class directory.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Python reports that an input must remain inside the class41 directory. | The argument supplied to audit.py resolves outside the permitted lab directory. | Place the JSON scenario in /opt/lab-classroom/class41/ and pass only its local filename, such as inventory.json. |
| The classifier reports a JSON decoding error. | A scenario file contains a missing comma, unmatched quote, or other invalid JSON. | Compare the scenario with baseline.json or recreate it by rerunning the scenario-generation step. |
| A monitored old episode in Sonarr remains missing after monitoring is enabled. | Monitoring changed eligibility, but RSS processing did not search historical indexer results. | Review profile and integration health, then use interactive search for a small diagnostic sample before considering a controlled automatic search. |
| Interactive search shows releases, but every release is rejected. | The candidates conflict with the quality profile, custom-format score, language policy, release restrictions, series type, age limits, or another acceptance rule. | Read the displayed rejection reasons and correct the specific policy or parsing issue rather than broadly weakening all restrictions. |
| An aired episode is shown as future or not yet available. | Metadata, time-zone handling, streaming release timing, or minimum-availability policy differs from the expected schedule. | Check Sonarr's effective episode dates, host time, container time, series metadata, and configured availability behavior before forcing a search. |
| An episode has a file but Sonarr continues looking for releases. | The existing file is below the assigned quality cutoff or does not satisfy format-scoring policy. | Inspect the episode file quality, assigned profile, cutoff, custom-format scores, and upgrade permissions. |
| A season appears monitored, but selected episodes are ignored. | Episode-level monitoring exceptions exist or a previous bulk operation changed only part of the hierarchy. | Open the season details and verify the effective monitoring flag for each affected episode. |
| A broad search creates more activity than expected. | Many historical episodes or upgrade candidates were monitored at once. | Pause further search activity in the appropriate application controls, inspect the monitored count and queue, and apply changes to a small series or season before expanding scope. |

## Security considerations

### principles
Treat the Sonarr API key as a secret because it can authorize library and application changes.
Use a dedicated administrative account or protected access path for Sonarr management.
Do not expose Sonarr directly to an untrusted network without appropriate authentication and a maintained access-control layer.
Review monitoring changes before initiating searches because they can cause downloads, storage consumption, and third-party service requests.
Apply least privilege to media, download, and configuration paths.

### lab_controls
The lab is offline and stores only fabricated series metadata under /opt/lab-classroom/class41/. No production URLs, API keys, indexer credentials, download-client credentials, or real library paths are required.

### operational_warning
Bulk monitoring and search operations can generate significant indexer requests and download activity. Validate one series or a small season first, then review the queue and rejection reasons before widening scope.

## Rollback

### goal
Return the exercise to its original baseline without affecting any path outside the class directory.

### steps
Restore the working inventory with `sudo cp /opt/lab-classroom/class41/baseline.json /opt/lab-classroom/class41/inventory.json`.
Ignore or retain monitoring-scenario.json and availability-scenario.json as audit evidence; they have no connection to a Sonarr instance.
Rerun `sudo python3 /opt/lab-classroom/class41/audit.py inventory.json` and verify the original summary.
If a real Sonarr interface was observed, no rollback is required because the lab instructed read-only observation.

## Video narration notes

Welcome to Class 41, Sonarr Series Monitoring and Availability. The central idea is that monitored does not mean downloaded. Monitoring records intent: Sonarr is allowed to care about an episode. The episode must also be available, discoverable, acceptable under its profile, and transferable through a functioning download client. Start troubleshooting by looking at the effective episode state. If it is unmonitored, Sonarr should ignore it. If its air date is still in the future, it is waiting. If it has aired but has not reached the relevant availability point, it is still waiting. If it is monitored and available with no file, it is missing. If it has a file below the profile cutoff, it is an upgrade candidate. If the file meets the cutoff, it is satisfied under our simplified model.

The lab uses a local JSON inventory instead of a production Sonarr server. Run the classifier and explain why each episode enters its category. Then change only the monitoring flags for two Archive Lane episodes. The missing episode becomes intentionally ignored, while the existing low-quality file becomes an upgrade candidate. This demonstrates that monitoring changes the meaning of existing facts; it does not create or delete a file. Next, adjust an availability date. The affected episode changes from waiting to missing because it has crossed the eligibility boundary.

In a real Sonarr instance, remember that RSS sync is not a continuous historical search. A newly monitored old episode may need an explicit search. Prefer interactive search while troubleshooting because it exposes rejection reasons. Before any broad automatic search, check the number of monitored episodes, the quality profile, available storage, indexer health, and download-client capacity. Apply policy changes to a small sample first, observe the queue, and only then expand the operation.

## References

- Sonarr documentation: https://wiki.servarr.com/sonarr
- Sonarr Quick Start Guide: https://wiki.servarr.com/sonarr/quick-start-guide
- Sonarr Library documentation: https://wiki.servarr.com/sonarr/library
- Sonarr Settings documentation: https://wiki.servarr.com/sonarr/settings
- Sonarr FAQ: https://wiki.servarr.com/sonarr/faq
- Official Sonarr source repository and release notes: https://github.com/Sonarr/Sonarr

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

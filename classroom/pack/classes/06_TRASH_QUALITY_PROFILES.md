# Class 6 — TRaSH Guides, Quality Profiles, and Custom Formats

**Lecture:** [IBRACORP — TRaSH Guides + Notifiarr](https://www.youtube.com/watch?v=DCxU3Vzaz6k)  
**Time:** 180 minutes  
**Build output:** documented quality policy with controlled scoring tests

## Why this class matters

Installing Sonarr or Radarr is easy. Designing what they should prefer, reject, upgrade, and stop upgrading is the difficult part. TRaSH Guides supplies maintained recommendations; your profile still represents a local policy constrained by display, audio system, storage, bandwidth, and tolerance for upgrades.

## Vocabulary

| Term | Meaning |
|---|---|
| Quality | Technical source/encode class recognized by the ARR application |
| Quality definition | Size limits associated with quality classes |
| Quality profile | Allowed qualities, ordering, upgrade, and cutoff policy |
| Custom Format (CF) | Rule that matches release characteristics |
| CF score | Positive or negative preference applied to a match |
| Minimum CF score | Threshold a candidate must meet |
| Upgrade-until score | Score target that can trigger further upgrades |
| Cutoff | Quality condition after which quality upgrades stop |
| REMUX | Near-direct disc media remuxed into a container |
| WEB-DL | File sourced from a streaming distributor download |
| Blu-ray encode | Compressed encode sourced from Blu-ray |
| DV/HDR | Dynamic-range formats with compatibility considerations |

## The decision model

Candidate selection is not one universal score. The application evaluates availability, monitored state, language, quality, Custom Formats, rejection rules, existing-file state, upgrade settings, and other constraints.

```mermaid
flowchart TD
    C["Candidate release"] --> E["Eligibility checks"]
    E --> Q["Quality/profile"]
    Q --> F["Custom Formats + scores"]
    F --> U["Upgrade/cutoff logic"]
    U --> A["Accept or reject"]
```

The correct question is not “What is the highest number?” It is “Does the selected result match the intended policy, and will future upgrades stop where we expect?”

## Requirements before profiles

Write the policy in plain language:

- Target resolution: 1080p, 2160p, or separate libraries/profiles.
- Maximum practical file size or storage budget.
- Accepted source classes.
- HDR/Dolby Vision compatibility.
- Preferred audio codecs and channel layouts.
- Language requirements.
- Whether release-group preferences matter.
- Whether remux quality is desired or wasteful for the environment.
- When upgrades should stop.

Example requirement:

> Prefer 1080p WEB-DL or strong Blu-ray encodes, reject unwanted low-quality sources, prefer compatible surround audio, avoid DV-only releases on displays lacking DV, and stop upgrading after the target quality and score are reached.

## Quality definitions versus profiles

Quality definitions bound expected sizes. Profiles decide allowed/ordered qualities and cutoff behavior. Custom Formats express characteristics that the built-in quality class does not fully capture.

Changing a size limit can make releases unavailable even if their quality name is allowed. Changing a cutoff can prevent or cause future upgrades. Changing CF scores can reorder candidates and trigger replacement activity. Treat each as a controlled configuration change.

## Custom Formats

A CF might recognize HDR type, audio codec, streaming service, release group, unwanted edition, or another release-name/media characteristic. A score expresses preference, not certainty. Overlapping CFs can stack, so test sample names rather than assuming one rule wins.

Design principles:

- Use negative scores or explicit rejection for truly unwanted traits.
- Use modest positive scores for preferences.
- Reserve very large weights for hard policy distinctions.
- Document why each score exists.
- Avoid importing every available CF “just in case.”

## Upgrade logic

Four questions must have explicit answers:

1. Are upgrades enabled?
2. What quality cutoff applies?
3. What minimum CF score makes a candidate eligible?
4. What upgrade-until CF score ends score-driven replacement?

A profile can accept a current file yet continue searching forever if upgrade targets are unreachable. It can also stop too early if cutoff or score targets are accidentally satisfied.

## Guided lab

Work in **one** app first (Sonarr *or* Radarr). Export/backup before edits. TRaSH Guides are a reference for intent—not a blind paste.

1. **Export / back up current quality profiles.**

:::windows
```powershell
cd COMPOSE_DIR
# UI: Settings → General → Backup, download zip to a private folder
# Also copy config bind mount:
Copy-Item -Recurse .\sonarr\config $HOME\backups\sonarr-profiles-$(Get-Date -Format yyyyMMdd) -ErrorAction SilentlyContinue
```
:::

:::linux
```bash
cd COMPOSE_DIR
# UI backup zip AND:
mkdir -p ~/backups/profiles-$(date +%Y%m%d)
cp -a ./sonarr/config ~/backups/profiles-$(date +%Y%m%d)/sonarr 2>/dev/null || true
cp -a ./radarr/config ~/backups/profiles-$(date +%Y%m%d)/radarr 2>/dev/null || true
```
:::

2. **Record current state (workbook table).**  
   For the profile you will change: allowed qualities, order, cutoff, upgrade allowed?, minimum Custom Format score, upgrade-until score, list of Custom Formats + scores.

3. **Optional API dump of profiles** (redact; replace KEY/PORT):

:::linux
```bash
curl -s "http://127.0.0.1:8989/api/v3/qualityprofile?apikey=YOUR_KEY" | head -c 400; echo
curl -s "http://127.0.0.1:8989/api/v3/customformat?apikey=YOUR_KEY" | head -c 400; echo
```
:::

:::windows
```powershell
curl.exe -s "http://127.0.0.1:8989/api/v3/qualityprofile?apikey=YOUR_KEY"
curl.exe -s "http://127.0.0.1:8989/api/v3/customformat?apikey=YOUR_KEY"
```
:::

4. **Write the local requirement in one sentence** (example: “Prefer 1080p WEB, reject incompatible HDR for this TV, allow upgrades until score ≥ X”).

5. **Import or create only the Custom Formats that match that sentence.** Assign scores and write *why* each score exists.

6. **Set qualities, cutoff, min CF score, upgrade-until.** Save the profile.

7. **Interactive search a controlled monitored title.** For ≥5 release candidates, record in the workbook:

```text
release name | quality | CF score | preferred? | reason accepted/rejected
```

8. **If ranking violates the written policy, change only one rule**, save, repeat the five-candidate table.

9. **Prove rollback:** restore from the backup zip or copied config (app stopped if required), reopen profile UI, confirm original scores return.

:::linux
```bash
docker compose stop sonarr
# restore config from ~/backups/... then:
docker compose start sonarr
docker compose logs --tail=50 sonarr
```
:::

## Example scoring exercise

Keep the in-class scoring table from the lesson. Practice explaining each total out loud.

## Break/fix

1. Set an unreachable upgrade-until score; observe endless “not done” behavior; restore.

2. Give a minor preference a higher score than a hard compatibility CF; observe bad ranking; restore.

3. Temporarily remove an incompatible-HDR (or similar) CF; inspect newly eligible junk; restore.

4. Restore backup and prove the five-candidate ranking matches the pre-change table.


## Common mistakes

- Mixing 1080p and 2160p goals without understanding quality ordering.
- Copying scores from a guide without checking hardware compatibility.
- Confusing minimum score with upgrade-until score.
- Allowing DV profiles that produce bad playback on the household display chain.
- Setting file-size limits that exclude every reasonable release.
- Changing global profiles on a live library without a sample evaluation and backup.

## Knowledge check

1. What is the difference between a quality and a Custom Format?
2. Why can multiple CF scores apply to one release?
3. What does cutoff control?
4. What is the risk of an unreachable upgrade-until score?
5. Why should hardware compatibility be written before importing profiles?
6. Does the highest-resolution candidate automatically represent the best local choice?

## Practical gate

- [ ] A plain-language quality requirement exists.
- [ ] Every imported CF has an owner and reason.
- [ ] Five controlled candidates produce expected rankings/rejections.
- [ ] Cutoff and score-upgrade behavior are explained.
- [ ] A backup and rollback path are proven.
- [ ] Storage and playback constraints are represented.

## 2026 correction

TRaSH recommendations and supported sync tooling change. Always use the current guide for profile identifiers and semantics, then verify behavior in the current Sonarr/Radarr release before applying changes broadly.


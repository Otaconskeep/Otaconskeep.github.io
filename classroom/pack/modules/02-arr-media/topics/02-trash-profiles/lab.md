# Lab — TRaSH quality profiles

**Module:** Module 2 — ARR Media Automation  
**Activity type:** Lab (Practice)  
**Objective:** Given playback and storage constraints, the learner can write a plain-language quality policy, configure Custom Formats and cutoff/upgrade settings, and prove ranking on five controlled candidates.

## Before you start

- Reading complete
- Lesson Feynman teach-back drafted (you may refine after the lab)

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

## Break / fix

### Break/fix

1. Set an unreachable upgrade-until score; observe endless “not done” behavior; restore.

2. Give a minor preference a higher score than a hard compatibility CF; observe bad ranking; restore.

3. Temporarily remove an incompatible-HDR (or similar) CF; inspect newly eligible junk; restore.

4. Restore backup and prove the five-candidate ranking matches the pre-change table.

## Feedback / common mistakes

- Mixing 1080p and 2160p goals without understanding quality ordering.
- Copying scores from a guide without checking hardware compatibility.
- Confusing minimum score with upgrade-until score.
- Allowing DV profiles that produce bad playback on the household display chain.
- Setting file-size limits that exclude every reasonable release.
- Changing global profiles on a live library without a sample evaluation and backup.

## Lab gate

All boxes must be true before the next class unlocks. If you fail: feedback → targeted review → new practice → reassess.

- [ ] A plain-language quality requirement exists.
- [ ] Every imported CF has an owner and reason.
- [ ] Five controlled candidates produce expected rankings/rejections.
- [ ] Cutoff and score-upgrade behavior are explained.
- [ ] A backup and rollback path are proven.
- [ ] Storage and playback constraints are represented.
- [ ] Prior-knowledge check answered
- [ ] Feynman teach-back completed (Explain, Simplify, Example, Weak spot, Retry)
- [ ] Independent practice completed
- [ ] Retrieval check attempted (target ≥80% when scored)
- [ ] Evidence recorded in workbook / verification matrix

# Lab — Container operations

**Module:** Module 1 — Infrastructure & Addressing  
**Activity type:** Lab (Practice)  
**Objective:** Given a running Compose service, the learner can inspect health and logs, perform a controlled image update, and roll back to a known-good state with evidence.

## Before you start

- Reading complete
- Lesson Feynman teach-back drafted (you may refine after the lab)

## Guided lab

Use the Class 2 `compose-lab` web service (or recreate it). Goal: prove you can update an explicit image tag and roll back with commands—not vibes.

1. **Record the current image identity (last-known-good).**

:::windows
```powershell
cd $HOME\compose-lab
docker compose ps
docker compose images
docker image inspect nginx:stable --format "Id={{.Id}} RepoTags={{.RepoTags}}"
Copy-Item compose.yaml compose.yaml.bak
curl.exe -s http://127.0.0.1:8080/ | findstr UNIQUE
```
:::

:::linux
```bash
cd ~/compose-lab
docker compose ps
docker compose images
docker image inspect nginx:stable --format 'Id={{.Id}} RepoTags={{.RepoTags}}'
cp compose.yaml compose.yaml.bak
curl -s http://127.0.0.1:8080/ | grep UNIQUE
```
:::

   Write the image ID and tag in the workbook. That is your rollback target.

2. **Run the acceptance test (before change).**  
   Browser or curl must show your unique phrase. Record “PASS” + timestamp.

3. **Change to another explicit tag, validate, pull, recreate.**  
   Edit `image:` from `nginx:stable` to a newer explicit tag you choose from Docker Hub (example pattern `nginx:1.27`—pick one that exists today). Then:

:::windows
```powershell
docker compose config
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=80 web
docker compose images
```
:::

:::linux
```bash
docker compose config
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=80 web
docker image inspect $(docker compose images -q web) --format '{{.RepoTags}} {{.Id}}'
```
:::

4. **Re-run the acceptance test.**  
   `curl` the unique phrase again. If it fails, do not continue—roll back now.

5. **Simulate a bad update (nonexistent tag), then restore.**

:::windows
```powershell
# Temporarily set image: nginx:this-tag-does-not-exist-otacon
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=40 web
Copy-Item compose.yaml.bak compose.yaml -Force
docker compose pull
docker compose up -d
curl.exe -s http://127.0.0.1:8080/ | findstr UNIQUE
```
:::

:::linux
```bash
# edit image to nginx:this-tag-does-not-exist-otacon, then:
docker compose pull || true
docker compose up -d || true
docker compose ps
docker compose logs --tail=40 web
cp compose.yaml.bak compose.yaml
docker compose pull
docker compose up -d
curl -s http://127.0.0.1:8080/ | grep UNIQUE
```
:::

6. **Fill a mini service contract** (also use `templates/service_contract.csv`):

```text
purpose: compose-lab nginx demo
image/version: (tag + image id)
configuration path: ./compose.yaml , ./site
media/download paths: n/a
internal address/port: web:80
published address/port: DOCKER-HOST:8080
dependencies: none
health test: curl unique phrase
backup method: copy compose.yaml + site/
update procedure: change tag -> config -> pull -> up -d -> test
rollback procedure: restore compose.yaml.bak -> pull -> up -d -> test
```

## Break / fix

### Break/fix scenarios

Run with commands; change only one variable at a time.

- **Restart loop:** `docker compose ps` + `docker inspect --format '{{.State.ExitCode}} {{.State.Error}}' CID` + first error in `logs`.
- **Port conflict:**

:::windows
```powershell
netstat -ano | findstr :8080
```
:::

:::linux
```bash
ss -lntp | grep 8080 || sudo lsof -i :8080
```
:::

- **Disk pressure:** `docker system df` and host `df -h` / PowerShell `Get-PSDrive`. Do **not** run `docker system prune --volumes` casually.
- **Permission denied:** inspect mount UID/GID and mode.
- **Update regression:** restore last-known-good tag from step 1.

## Feedback / common mistakes

- Skipping evidence and calling it done.
- Changing multiple variables before retesting.
- Moving on without completing Feynman teach-back.

## Lab gate

All boxes must be true before the next class unlocks. If you fail: feedback → targeted review → new practice → reassess.

- [ ] A service contract is complete.
- [ ] Health is verified above the container-process layer.
- [ ] Configuration is backed up.
- [ ] An update and rollback are demonstrated.
- [ ] The runbook identifies last-known-good version and acceptance test.
- [ ] Logs shared as evidence contain no secrets.
- [ ] Prior-knowledge check answered
- [ ] Feynman teach-back completed (Explain, Simplify, Example, Weak spot, Retry)
- [ ] Independent practice completed
- [ ] Retrieval check attempted (target ≥80% when scored)
- [ ] Evidence recorded in workbook / verification matrix

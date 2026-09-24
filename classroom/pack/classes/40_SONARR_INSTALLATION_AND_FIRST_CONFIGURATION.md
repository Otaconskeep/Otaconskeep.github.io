# Class 40: Sonarr Installation and First Configuration

**Learning objective:** Explain Sonarr's role in a media automation architecture.; Install the current Sonarr v4 Linux x64 release into a self-contained laboratory directory.; Configure Sonarr to listen only on the loopback interface for the initial lab.; Start and stop Sonarr without creating a system-wide service.; Complete the first-run authentication and media root configuration.; Distinguish a root folder from a download-client destination.; Verify the process, listening socket, web interface, logs, and application data.; Describe how permissions and path consistency affect imports.
**Bloom level:** Understand / Apply
**Track:** Media Automation · **Difficulty:** beginner · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Install Sonarr as a self-contained laboratory application, start it with data stored entirely under the class workspace, complete its initial web configuration, and understand the boundaries between Sonarr, download clients, media storage, and media servers.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** The executable installation commands target 64-bit x86 Linux systems reporting x86_64 from uname -m and use the Sonarr v4 main-channel Linux x64 archive. ARM64 systems require the corresponding official ARM64 build and are not covered by the executable commands in this lesson. The web workflow may vary slightly between Sonarr v4 maintenance releases. Port 8989 must be available. The portable process model is suitable for this controlled lab; production systems should use an appropriately supervised and supported deployment model.

## Learning objective

- Explain Sonarr's role in a media automation architecture.
- Install the current Sonarr v4 Linux x64 release into a self-contained laboratory directory.
- Configure Sonarr to listen only on the loopback interface for the initial lab.
- Start and stop Sonarr without creating a system-wide service.
- Complete the first-run authentication and media root configuration.
- Distinguish a root folder from a download-client destination.
- Verify the process, listening socket, web interface, logs, and application data.
- Describe how permissions and path consistency affect imports.

## Why this matters

Install Sonarr as a self-contained laboratory application, start it with data stored entirely under the class workspace, complete its initial web configuration, and understand the boundaries between Sonarr, download clients, media storage, and media servers.

## Prerequisites

- A Linux x86_64 host with Python 3, tar, gzip, and standard process-management utilities installed.
- Permission to create and modify files under /opt/lab-classroom/class40/.
- TCP port 8989 must be unused on the laboratory host.
- Outbound HTTPS access to the official Sonarr download service.
- A web browser capable of reaching http://127.0.0.1:8989 from the laboratory host.
- Basic familiarity with Linux paths, processes, and file permissions.

## Required reading

- Sonarr documentation home: https://wiki.servarr.com/sonarr
- Sonarr installation documentation: https://wiki.servarr.com/sonarr/installation
- Sonarr quick-start guide: https://wiki.servarr.com/sonarr/quick-start-guide
- Servarr Docker guide for comparison with this portable laboratory installation: https://wiki.servarr.com/docker-guide

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| Sonarr | An application that monitors television series, evaluates releases, sends selected releases to a download client, and imports completed files into an organized library. |
| Root folder | The top-level library directory under which Sonarr creates and manages series folders. |
| Download client | A separate application that performs the actual transfer of content after Sonarr submits a release. |
| Indexer | A release-search source queried by Sonarr directly or through an indexer-management application. |
| Import | The operation in which Sonarr recognizes a completed file and copies, moves, or hard-links it into the organized library. |
| Quality profile | A policy defining acceptable qualities, upgrade behavior, and the quality at which Sonarr should stop searching for improvements. |
| Application data directory | The directory containing Sonarr's database, configuration, logs, backup data, and other persistent state. |
| Bind address | The local network address on which an application accepts connections. |
| Loopback | A host-local network interface, normally represented by 127.0.0.1, that is not directly reachable from another machine. |

## Instruction

Sonarr is an automation coordinator rather than a downloader or media player. It tracks desired television series, searches configured indexers, applies quality and release rules, submits an approved release to a separate download client, observes completion, and then imports the resulting file into a structured library. A media server such as Jellyfin, Plex, or Emby may scan that final library, but it is not part of Sonarr itself. Keeping these responsibilities separate makes troubleshooting much easier: search failures involve indexers, transfer failures involve the download client, import failures commonly involve paths or permissions, and playback failures generally belong to the media server.

This class uses a portable installation instead of a package manager, container engine, or system service. The application binary, persistent data, temporary extraction data, logs, sample library, and process identifier all remain under /opt/lab-classroom/class40/. This design satisfies the class mutation boundary and makes rollback straightforward. It is not a recommendation that every production installation use a manually started process. A production deployment should use a supervised service or container, a dedicated identity, durable storage, regular backups, and a deliberate upgrade policy.

The initial configuration binds Sonarr to 127.0.0.1 on TCP port 8989. Loopback binding is an important safety control because an unconfigured administrative interface should not be exposed to the local network. During onboarding, create authentication values known only to the administrator and store them using an appropriate private credential-management workflow. Do not place them in shell history, lesson notes, screenshots, or source control. After onboarding, the laboratory adds /opt/lab-classroom/class40/media/tv as a root folder. That root is the organized destination library; it is not where an external download client should place incomplete transfers.

Path consistency is essential when Sonarr and a download client run in different environments. A completed file path reported by the client must be meaningful to Sonarr. Containers often require matching volume mappings or a carefully designed remote path mapping. Permissions must also permit Sonarr to traverse source directories and create, rename, or link files in the destination. Grant only the access needed rather than making the entire filesystem broadly writable. This lab does not configure a real indexer or download client, so related health notices may remain until those integrations are intentionally added.

## Architecture

The laboratory flow is: browser on the local host -> Sonarr web interface at 127.0.0.1:8989 -> Sonarr application process -> persistent application data under /opt/lab-classroom/class40/data and television library under /opt/lab-classroom/class40/media/tv. In a complete deployment, Sonarr also communicates outbound with indexers and a download client. The download client writes completed data to a path Sonarr can access, Sonarr imports that data into the root folder, and a separate media server scans the organized library. This lab intentionally omits those external integrations.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Draw a data-flow diagram containing Sonarr, one indexer, one download client, a completed-download directory, the television root folder, and a media server.
Write a permissions plan for a dedicated Sonarr identity and a separate download-client identity without granting universal write access.
Compare portable, native-service, and container-based Sonarr installations. Identify one operational advantage and one operational cost of each.
Design a backup plan for /opt/lab-classroom/class40/data that states backup frequency, retention, restore testing, and protection of sensitive configuration.
Explain how mismatched container paths can prevent completed-download imports and provide a conceptual corrected mapping without changing this lab.
Document the checks you would perform before allowing Sonarr access from another host.

## Feynman teach-back

Explain Sonarr to a new administrator without using product jargon: Sonarr maintains a list of television episodes you want, asks search sources what releases exist, applies rules to select an acceptable release, instructs another program to transfer it, and organizes the completed file into a library. Then explain why the download location and library location are different, why Sonarr must be able to see both paths, and why binding the initial interface to 127.0.0.1 reduces risk. If you cannot clearly identify which component searches, downloads, imports, and plays the media, revisit the architecture section.

## Retrieval check

1. What job does Sonarr perform, and what job does it delegate to a download client?
2. Why does this lab bind Sonarr to 127.0.0.1 instead of a wildcard address?
3. What is the difference between a Sonarr root folder and a completed-download directory?
4. Why can two applications using different path names for the same storage cause an import failure?
5. Which directory contains the persistent Sonarr state in this lab?
6. Why may Sonarr display health notices after this lab even when the installation is working?
7. What should be checked before exposing Sonarr beyond the local host?

## Guided lab

### scope
Every filesystem mutation performed by these steps remains below /opt/lab-classroom/class40/. The lab does not install packages, create operating-system users, alter host startup configuration, or create a system-wide service.

### steps
Confirm the host architecture with: uname -m. Continue only when the result is x86_64.
Confirm that port 8989 is not already listening with: ss -ltn | grep ':8989'. No output is the desired pre-lab result.
Create the laboratory directories with: mkdir -p /opt/lab-classroom/class40/{app,artifacts,data,data-baseline,home,tmp,dotnet-bundle,xdg-config,xdg-cache,logs,media/tv}
Restrict the workspace so it is accessible only to its current owner with: chmod 700 /opt/lab-classroom/class40
Download the current Sonarr v4 Linux x64 archive over HTTPS with: python3 -c "import urllib.request; urllib.request.urlretrieve('https://services.sonarr.tv/v1/download/main/latest?version=4&os=linux&arch=x64', '/opt/lab-classroom/class40/artifacts/sonarr-linux-x64.tar.gz')"
Check that the downloaded object is a readable gzip-compressed tar archive with: tar -tzf /opt/lab-classroom/class40/artifacts/sonarr-linux-x64.tar.gz | head
Extract the archive into the application directory with: tar -xzf /opt/lab-classroom/class40/artifacts/sonarr-linux-x64.tar.gz -C /opt/lab-classroom/class40/app --strip-components=1
Confirm that the executable exists with: test -x /opt/lab-classroom/class40/app/Sonarr && echo 'Sonarr executable is present'
Create a loopback-only initial configuration with: python3 -c "from pathlib import Path; Path('/opt/lab-classroom/class40/data/config.xml').write_text('<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Config>\n  <BindAddress>127.0.0.1</BindAddress>\n  <Port>8989</Port>\n  <SslPort>9898</SslPort>\n  <EnableSsl>False</EnableSsl>\n  <LaunchBrowser>False</LaunchBrowser>\n  <Branch>main</Branch>\n  <LogLevel>info</LogLevel>\n  <UrlBase></UrlBase>\n  <UpdateMechanism>BuiltIn</UpdateMechanism>\n</Config>\n', encoding='utf-8')"
Save the pre-start configuration as a rollback baseline with: cp -a /opt/lab-classroom/class40/data/. /opt/lab-classroom/class40/data-baseline/
Start Sonarr with all configurable runtime paths inside the class workspace by running: cd /opt/lab-classroom/class40; HOME=/opt/lab-classroom/class40/home TMPDIR=/opt/lab-classroom/class40/tmp XDG_CONFIG_HOME=/opt/lab-classroom/class40/xdg-config XDG_CACHE_HOME=/opt/lab-classroom/class40/xdg-cache DOTNET_BUNDLE_EXTRACT_BASE_DIR=/opt/lab-classroom/class40/dotnet-bundle nohup ./app/Sonarr -nobrowser -data=/opt/lab-classroom/class40/data > /opt/lab-classroom/class40/logs/console.log 2>&1 & printf '%s\n' "$!" > /opt/lab-classroom/class40/sonarr.pid
Wait for startup, then verify that the recorded process exists with: kill -0 "$(cat /opt/lab-classroom/class40/sonarr.pid)" && echo 'Sonarr process is running'
Verify loopback listening with: ss -ltn | grep '127.0.0.1:8989'
Open http://127.0.0.1:8989 in a browser on the same host. Complete the first-run authentication prompt using administrator-created values that are not copied into lesson notes or shell commands.
In Sonarr, open Settings, then Media Management. Enable advanced settings if required, select Add Root Folder, and add /opt/lab-classroom/class40/media/tv.
Review the default episode naming and quality-profile behavior without adding indexers or a download client. Preserve defaults unless you can explain the effect of a proposed change.
Open System, then Status, and record the displayed Sonarr version and application-data path in your private lab notes. Do not record authentication material or sensitive application access values.
Review System, then Logs. The absence of a configured download client or indexer is acceptable in this introductory lab.
Stop Sonarr at the end of the lab with: kill "$(cat /opt/lab-classroom/class40/sonarr.pid)"
Confirm shutdown with: while kill -0 "$(cat /opt/lab-classroom/class40/sonarr.pid)" 2>/dev/null; do sleep 1; done; echo 'Sonarr has stopped'

## Expected results

- The Sonarr application files exist under /opt/lab-classroom/class40/app/.
- Persistent configuration, database, and log data are created under /opt/lab-classroom/class40/data/.
- The Sonarr process starts successfully and listens only on 127.0.0.1:8989.
- The local browser displays the Sonarr onboarding or main application interface.
- Initial authentication is enabled using administrator-created values that are not embedded in the lesson.
- The path /opt/lab-classroom/class40/media/tv is accepted as a television root folder.
- Sonarr reports its application-data path as /opt/lab-classroom/class40/data.
- Indexer or download-client health notices may remain because those integrations are intentionally outside this lab.
- The recorded process stops cleanly when the lab shutdown command is run.

## Verification checkpoints

- [ ] Run test -x /opt/lab-classroom/class40/app/Sonarr && echo PASS to confirm that the application executable is present.
- [ ] Run kill -0 "$(cat /opt/lab-classroom/class40/sonarr.pid)" && echo PASS while Sonarr is expected to be running.
- [ ] Run ss -ltn | grep '127.0.0.1:8989' and confirm that the listening address is loopback rather than a wildcard address.
- [ ] Visit http://127.0.0.1:8989 and confirm that the authenticated Sonarr interface loads.
- [ ] In System Status, confirm that the application-data directory is /opt/lab-classroom/class40/data.
- [ ] In Settings and Media Management, confirm that /opt/lab-classroom/class40/media/tv appears as a root folder.
- [ ] Run test -f /opt/lab-classroom/class40/data/sonarr.db && echo PASS after first startup to confirm creation of the application database.
- [ ] Inspect /opt/lab-classroom/class40/logs/console.log and the Sonarr Logs page for startup failures without publishing the complete configuration or sensitive application access values.
- [ ] After shutdown, run kill -0 "$(cat /opt/lab-classroom/class40/sonarr.pid)" 2>/dev/null || echo PASS and confirm that PASS is displayed.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The archive download fails. | The host lacks outbound HTTPS connectivity, name resolution is failing, or the official download service is temporarily unavailable. | Confirm general network and DNS operation, verify that the official URL is reachable, and retry the Python download command. Do not substitute an untrusted mirror. |
| The tar integrity check reports that the file is not a gzip archive. | The download is incomplete or the service returned an error document instead of the archive. | Inspect the file type with file /opt/lab-classroom/class40/artifacts/sonarr-linux-x64.tar.gz, download it again from the official service, and repeat the tar listing before extraction. |
| The Sonarr executable does not start. | The host architecture is not x86_64, the archive was not extracted correctly, required runtime support is unavailable, or execution is prohibited on the mounted filesystem. | Recheck uname -m, confirm the executable bit, review /opt/lab-classroom/class40/logs/console.log, and use the official build matching the host architecture. This lesson's command is specifically for x86_64. |
| Sonarr reports that port 8989 is already in use. | Another service or another Sonarr process already owns the port. | Use ss -ltnp to identify the existing listener. Stop only a process you own and understand, or conduct the class on an isolated host where port 8989 is free. |
| The browser cannot open the Sonarr interface. | Sonarr is still starting, the process exited, the browser is running on a different machine, or the listener was not created. | Check the PID with kill -0, inspect console.log, and confirm the socket with ss. Because Sonarr is bound to 127.0.0.1, the browser must run on the same host unless a separately secured access method is deliberately configured. |
| The root folder cannot be added. | The directory does not exist or the Sonarr process lacks traversal or write permission. | Confirm that /opt/lab-classroom/class40/media/tv exists and that the account running Sonarr owns or can write to the class workspace. |
| Sonarr displays health notices about missing indexers or download clients. | Those integrations were intentionally not configured in this introductory lab. | Treat the notices as expected for this class. Configure real integrations only after reviewing their authentication, path, and network requirements. |
| A later download completes but Sonarr cannot import it. | The path reported by the download client is not visible to Sonarr, or Sonarr lacks permission to read the source and write the library. | Compare the exact completed-download path seen by both applications, align container mounts if applicable, and grant the minimum required ownership and group access. |
| The shutdown command says that the process does not exist. | Sonarr already stopped or the PID file is stale. | Check console.log for an earlier exit and use ps to confirm whether a Sonarr process owned by the lab user remains. Do not signal an unrelated process. |

## Security considerations

The initial interface is bound to 127.0.0.1 so it is not directly exposed to other hosts.
Enable Sonarr authentication during onboarding even when access is currently limited to loopback.
Use unique administrator-created authentication values and keep them out of shell history, screenshots, lesson submissions, and source control.
Treat Sonarr's configuration directory and application-generated access material as sensitive.
Do not publish the complete contents of config.xml or unrestricted diagnostic bundles.
Keep the class workspace restricted to its owner unless a deliberate group-access design is required.
Download application archives only from the official Sonarr service. For production, pin an approved release and validate it using officially published integrity information when available.
Do not expose Sonarr directly to the public internet. Use a deliberately secured access architecture with authentication, encryption, updates, and access controls.
Run Sonarr as a non-privileged dedicated identity in production rather than as the system administrator.
Give Sonarr only the filesystem permissions needed to access its application data, completed downloads, and organized media library.
Review third-party indexers and download clients separately because each integration introduces its own trust boundary.
Back up the Sonarr application-data directory before upgrades or major configuration changes.

## Rollback

Stop the process with: kill "$(cat /opt/lab-classroom/class40/sonarr.pid)"
Wait for shutdown with: while kill -0 "$(cat /opt/lab-classroom/class40/sonarr.pid)" 2>/dev/null; do sleep 1; done
Preserve the post-lab application state with: mv /opt/lab-classroom/class40/data /opt/lab-classroom/class40/data-after-lab
Re-create the data directory from the baseline with: mkdir -p /opt/lab-classroom/class40/data && cp -a /opt/lab-classroom/class40/data-baseline/. /opt/lab-classroom/class40/data/
The portable application, downloaded archive, logs, baseline, and preserved post-lab state remain inside /opt/lab-classroom/class40/ for review.
To resume the completed configuration instead of the baseline, stop Sonarr, preserve the current data directory under another name within the class workspace, and rename data-after-lab back to data.

## Video narration notes

Welcome to Class 40, Sonarr Installation and First Configuration. In this lab, we will install Sonarr without changing system package state or creating a permanent host service. Everything we write stays under /opt/lab-classroom/class40/. We begin by confirming that the machine uses the x86_64 architecture and that TCP port 8989 is free. We then create isolated directories for the application, persistent data, temporary files, logs, and the sample television library.

The current Sonarr v4 Linux x64 archive is downloaded directly from the official service and checked as a readable gzip-compressed tar archive before extraction. We create a small initial configuration that binds the web interface to 127.0.0.1. This is an important safety measure: the first-run administrative interface should not be available to other machines before authentication is configured.

When Sonarr starts, its application data is directed to the class data directory. Runtime environment paths are also redirected into the class workspace. We verify three separate things: the process exists, the socket listens on 127.0.0.1 port 8989, and the browser can load the application. These checks separate process problems, network-listener problems, and browser-access problems.

During onboarding, create private authentication values and do not copy them into commands or submitted notes. Next, add /opt/lab-classroom/class40/media/tv as the root folder. Remember that this is the organized library destination, not an incomplete-download directory. Sonarr will eventually receive completed files from a separate download client and import them into this root.

The lab does not configure an indexer or download client, so related health messages are expected. Before finishing, review System Status, confirm the application-data path, and inspect logs for startup errors. Finally, stop the process using the recorded PID and verify that it has exited. The resulting directory contains the portable installation, persistent data, logs, and a pre-start baseline that can be used for rollback.

## References

- Sonarr documentation: https://wiki.servarr.com/sonarr
- Sonarr installation guide: https://wiki.servarr.com/sonarr/installation
- Sonarr quick-start guide: https://wiki.servarr.com/sonarr/quick-start-guide
- Sonarr settings documentation: https://wiki.servarr.com/sonarr/settings
- Servarr Docker guide: https://wiki.servarr.com/docker-guide
- Sonarr official website: https://sonarr.tv/

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

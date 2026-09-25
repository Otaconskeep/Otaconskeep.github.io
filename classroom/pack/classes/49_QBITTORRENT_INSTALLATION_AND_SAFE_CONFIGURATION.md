# Class 49: qBittorrent Installation and Safe Configuration

**Learning objective:** Explain the separation between the qBittorrent process, Web UI, peer protocol, configuration, and download storage.; Deploy qBittorrent-nox without installing a desktop environment or modifying host package state.; Keep Podman image, runtime, configuration, and download data beneath /opt/lab-classroom/class49/.; Restrict the Web UI and initial peer listener to the host loopback interface.; Retrieve the generated temporary Web UI credential and replace it with a unique password.; Disable unnecessary discovery and automation features and preserve Web UI security checks.; Verify port bindings, persistent storage, container state, and authentication behavior.; Remove and recreate the container without deleting its persistent configuration or downloads.
**Bloom level:** Understand / Apply
**Track:** Self-Hosted Applications · **Difficulty:** intermediate · **Duration:** ~90 minutes · **Lab risk:** medium
**Build output:** Deploy qBittorrent-nox as an isolated, reproducible Podman container; protect its Web UI; constrain all persistent lab state to /opt/lab-classroom/class49/; and establish responsible download, network, and rollback practices.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-03-08
**Compatibility:** ### host
Linux with functional rootless Podman and user-namespace support.

### podman
Designed for current Podman releases that support --root, --runroot, --tmpdir, --events-backend, rootless port publication, and --userns=keep-id.

### application
Designed for qBittorrent versions that generate a temporary Web UI administrator password on startup. Authentication details can differ on older releases.

### image
Uses lscr.io/linuxserver/qbittorrent:latest for the exercise and records the retrieved repository digest. Image entrypoint paths or bundled versions may change and must be reviewed before production use.

### network
Uses IPv4 host-loopback publications on ports 8080 and 6881. The exercise does not create router mappings or intentionally expose the service to a LAN.

### storage_constraint
All lab-created persistent state is redirected to /opt/lab-classroom/class49/. Host prerequisites must be installed before the lab.

## Learning objective

- Explain the separation between the qBittorrent process, Web UI, peer protocol, configuration, and download storage.
- Deploy qBittorrent-nox without installing a desktop environment or modifying host package state.
- Keep Podman image, runtime, configuration, and download data beneath /opt/lab-classroom/class49/.
- Restrict the Web UI and initial peer listener to the host loopback interface.
- Retrieve the generated temporary Web UI credential and replace it with a unique password.
- Disable unnecessary discovery and automation features and preserve Web UI security checks.
- Verify port bindings, persistent storage, container state, and authentication behavior.
- Remove and recreate the container without deleting its persistent configuration or downloads.

## Why this matters

Deploy qBittorrent-nox as an isolated, reproducible Podman container; protect its Web UI; constrain all persistent lab state to /opt/lab-classroom/class49/; and establish responsible download, network, and rollback practices.

## Prerequisites

- A Linux host with rootless Podman already installed and working.
- A user account permitted to run Podman without elevated privileges.
- At least 2 GB of free space under /opt/lab-classroom/class49/ for container storage, configuration, and test data.
- Basic familiarity with Linux paths, TCP ports, containers, and browser-based administration.
- Permission to download the selected container image and to use BitTorrent only for lawful, authorized content.
- Ports 8080 and 6881 must not already be occupied on the host loopback interface.

## Required reading

- qBittorrent Wiki: Web UI documentation and authentication behavior — https://github.com/qbittorrent/qBittorrent/wiki/Web-UI
- qBittorrent Wiki: Explanation of options in qBittorrent — https://github.com/qbittorrent/qBittorrent/wiki/Explanation-of-Options-in-qBittorrent
- Podman documentation for rootless operation — https://docs.podman.io/en/latest/markdown/podman.1.html#rootless-mode
- LinuxServer.io qBittorrent image documentation — https://docs.linuxserver.io/images/docker-qbittorrent/
- Review your network's acceptable-use policy and the copyright rules applicable to your location before transferring content.

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| qBittorrent-nox | The headless qBittorrent executable intended for systems that do not run the graphical desktop client. |
| Web UI | The browser-based administrative interface used to manage qBittorrent. |
| Peer port | The TCP and UDP port on which a BitTorrent client can accept inbound peer connections. |
| Loopback | A host-local network interface, normally represented by 127.0.0.1 for IPv4, that is not directly reachable from another machine. |
| Bind mount | A host directory presented at a specific path inside a container so application data persists independently of the container. |
| Rootless container | A container launched by an unprivileged host user using a user namespace rather than a privileged system-wide container daemon. |
| Image digest | A content-derived identifier that can be recorded to identify the exact container image retrieved at a point in time. |
| Seeding | Uploading pieces of content to other peers after or while obtaining that content. |
| DHT | A distributed hash table used to discover peers without relying exclusively on a central tracker. |
| UPnP/NAT-PMP | Protocols that may automatically request port mappings from a gateway; they should not be enabled without an explicit network design. |

## Instruction

qBittorrent is not merely a download page. It is a network-facing application with an administrative Web UI, a peer-to-peer protocol engine, persistent state, and the ability to write large quantities of data. Safe installation therefore begins with boundaries. The Web UI is a control plane: anyone who can authenticate to it may add transfers, inspect activity, alter paths, or change network behavior. It must not be casually exposed to a LAN or the Internet. This lab publishes the Web UI only on 127.0.0.1, which means a browser on the same host can reach it while remote systems cannot connect directly. The peer port is also initially loopback-only. This conservative starting point sacrifices inbound peer connectivity in exchange for a clearly bounded first deployment. Any later decision to expose a peer port should be deliberate and based on the local network design.

Persistent data is separated from the disposable container. Configuration is stored under /opt/lab-classroom/class49/config/ and transfer data is stored under /opt/lab-classroom/class49/downloads/. Podman image and container metadata are also redirected beneath the class directory. Replacing a container should therefore not remove the configuration or downloaded files. Rootless Podman, a non-root qBittorrent process, dropped Linux capabilities, and the no-new-privileges setting reduce impact if the application is compromised, but they do not make untrusted content safe. Downloaded programs, documents, archives, and media must still be treated according to their origin and scanned or inspected before use.

A BitTorrent client does not provide anonymity. Peer participants can generally observe peer IP addresses, and transport encryption is not an anonymity system. A VPN can alter the visible network path, but qBittorrent must be intentionally bound to the correct interface if a fail-closed design is required. That design is outside this isolated installation lab and must be tested rather than assumed. Legal and policy controls matter as much as technical controls: only transfer content you are authorized to obtain and distribute. Safe defaults also include changing the generated Web UI password, leaving cross-site request forgery and host-header protections enabled, disabling automatic execution of external programs, avoiding unreviewed search plugins, and setting download and seeding limits appropriate to the host's capacity.

## Architecture

### components
A rootless Podman process controlled by the current host user.
A qBittorrent-nox container created from the LinuxServer.io qBittorrent image.
A Web UI published as 127.0.0.1:8080 on the host.
A peer listener initially published as 127.0.0.1:6881 over TCP and UDP.
Persistent configuration at /opt/lab-classroom/class49/config/.
Persistent completed and incomplete data directories beneath /opt/lab-classroom/class49/downloads/.
Podman image, container, event, temporary, and runtime state beneath /opt/lab-classroom/class49/.

### data_flow
The local browser connects to 127.0.0.1:8080, which Podman forwards to qBittorrent's container port 8080.
qBittorrent writes preferences and session metadata through the /config bind mount.
qBittorrent writes payload data through the /downloads bind mount.
Outbound peer and tracker traffic originates from the rootless container network.
Inbound peer connections are not available from the LAN while the host peer-port publication remains bound to 127.0.0.1.

### trust_boundaries
The Web UI credential separates an authorized local administrator from unauthenticated callers.
The container boundary reduces direct access to the host but is not equivalent to a separate virtual machine.
Bind-mounted configuration and downloads are intentionally writable by qBittorrent and must be backed up separately.
Container images and plugins are software supply-chain inputs and must come from reviewed sources.
Downloaded content remains untrusted even when the transfer itself completed successfully.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

Create a one-page deployment record containing the image repository digest, host port mappings, persistent paths, update policy, backup policy, and responsible owner. Store it beneath /opt/lab-classroom/class49/.
Draft a capacity plan that defines maximum download space, incomplete-transfer space, upload bandwidth, download bandwidth, and a response to a full filesystem. Do not invent benchmark data; use values appropriate to your own host.
Research a Linux distribution that officially publishes torrent files. Document how you would verify that a torrent or downloaded image came from that distribution before using it.
Design, but do not implement, a secure remote-access approach for the Web UI. Explain authentication, encryption, exposure boundaries, and logging.
Describe a VPN fail-closed test plan that proves qBittorrent cannot continue using an unintended interface when the VPN disappears.

## Feynman teach-back

### prompt
Explain the deployment to a new administrator without using the words container, bind mount, or loopback.

### model_explanation
qBittorrent runs in a restricted application environment controlled by an ordinary user. Its settings and downloaded files are kept in named class directories so replacing the application wrapper does not erase them. The management page accepts connections only from the same computer, and the initial peer listener is also local-only. A password protects the management page, but downloaded files are still untrusted and peer-to-peer networking is not anonymous.

### self_check
Can you identify which directory stores settings and which stores payload data?
Can you explain why 127.0.0.1 is safer than 0.0.0.0 for the Web UI?
Can you explain why deleting a container does not have to delete its downloads?
Can you explain why transport encryption is not the same as anonymity?
Can you state what must be tested before relying on a VPN interface binding?

## Retrieval check

1. 1. Why is the qBittorrent Web UI bound to 127.0.0.1 in the initial deployment?
2. 2. What is the operational benefit of storing /config and /downloads outside the disposable container object?
3. 3. Does enabling BitTorrent protocol encryption make a user anonymous? Explain briefly.
4. 4. Which qBittorrent credential should be changed immediately after first startup?
5. 5. Why are UPnP and NAT-PMP disabled unless specifically required?
6. 6. What should happen to cross-site request forgery, clickjacking, and host-header protections?
7. 7. What does the recorded image repository digest provide that the latest tag does not?
8. 8. Why might inbound peer connectivity be limited in this lab?
9. 9. Is a completed download automatically trustworthy because qBittorrent reports it as complete?
10. 10. What must be verified before assuming a VPN prevents traffic from leaving through another interface?

## Guided lab

### scope_rule
Every persistent file created by this lab must remain beneath /opt/lab-classroom/class49/. Run the commands as the same unprivileged user in one shell. Do not substitute a system-wide Podman storage location.

### steps
### step
1

### title
Create private lab directories

### commands
umask 077
LAB=/opt/lab-classroom/class49
install -d -m 700 "$LAB" "$LAB/home" "$LAB/runtime" "$LAB/tmp" "$LAB/storage" "$LAB/runroot" "$LAB/config" "$LAB/downloads" "$LAB/downloads/complete" "$LAB/downloads/incomplete"

### notes
The parent /opt/lab-classroom directory must already permit the current user to create class49. Do not change permissions outside the class49 directory as part of this lab.
### step
2

### title
Create a lab-scoped Podman environment

### commands
cat > "$LAB/env.sh" <<'EOF'
LAB=/opt/lab-classroom/class49
export LAB
export HOME="$LAB/home"
export XDG_CONFIG_HOME="$LAB/home/.config"
export XDG_DATA_HOME="$LAB/home/.local/share"
export XDG_CACHE_HOME="$LAB/home/.cache"
export XDG_RUNTIME_DIR="$LAB/runtime"
export TMPDIR="$LAB/tmp"
p49podman() {
  command podman --root "$LAB/storage" --runroot "$LAB/runroot" --tmpdir "$LAB/tmp" --events-backend=file "$@"
}
EOF
. "$LAB/env.sh"
install -d -m 700 "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" "$XDG_CACHE_HOME"

### notes
Source env.sh before every later p49podman command if a new shell is opened. The wrapper redirects Podman's persistent and temporary state into the class directory.
### step
3

### title
Pull and identify the container image

### commands
. /opt/lab-classroom/class49/env.sh
p49podman pull lscr.io/linuxserver/qbittorrent:latest
p49podman image inspect lscr.io/linuxserver/qbittorrent:latest --format '{{json .RepoDigests}}' | tee "$LAB/image-digests.json"

### notes
The latest tag can change. The recorded repository digest identifies what was retrieved for this exercise. For a long-lived deployment, review updates and pin an approved digest rather than silently following a moving tag.
### step
4

### title
Start qBittorrent with constrained host bindings

### commands
. /opt/lab-classroom/class49/env.sh
p49podman run --detach --name class49-qbittorrent --userns=keep-id --user "$(id -u):$(id -g)" --cap-drop=ALL --security-opt=no-new-privileges --env HOME=/config --env XDG_CONFIG_HOME=/config --publish 127.0.0.1:8080:8080/tcp --publish 127.0.0.1:6881:6881/tcp --publish 127.0.0.1:6881:6881/udp --volume "$LAB/config:/config:rw" --volume "$LAB/downloads:/downloads:rw" --entrypoint /usr/bin/qbittorrent-nox lscr.io/linuxserver/qbittorrent:latest --webui-port=8080
p49podman ps --filter name=class49-qbittorrent
p49podman logs class49-qbittorrent | tee "$LAB/initial-container.log"

### notes
Read the startup log for the temporary Web UI password. Treat the log as sensitive because it may contain that credential. The application runs as the current host user's numeric identity rather than through the image's normal service supervisor.
### step
5

### title
Complete the initial Web UI configuration

### commands


### notes
Open http://127.0.0.1:8080 in a browser on the Podman host. Sign in with username admin and the temporary password shown in the container log. Immediately set a unique password in Tools, Options, Web UI. Keep authentication enabled. Keep host-header validation, cross-site request forgery protection, and clickjacking protection enabled. Do not configure an alternate unauthenticated subnet. Set the default save path to /downloads/complete and the incomplete path to /downloads/incomplete.
### step
6

### title
Apply conservative application settings

### commands


### notes
In qBittorrent options, disable UPnP/NAT-PMP port forwarding unless it is explicitly required and reviewed. Ensure no external program is configured to run when a torrent is added or completed. Disable the search feature and RSS feature if they are not needed. Configure sensible global upload and download limits for the host and network. Configure a seeding ratio or time limit that matches the authorization and policy for the content. Do not interpret protocol encryption or anonymous mode as an anonymity guarantee.
### step
7

### title
Restart and verify persistence

### commands
. /opt/lab-classroom/class49/env.sh
p49podman restart class49-qbittorrent
p49podman ps --filter name=class49-qbittorrent
p49podman logs --tail 50 class49-qbittorrent
find "$LAB/config" -maxdepth 4 -type f -print
find "$LAB/downloads" -maxdepth 2 -type d -print

### notes
Confirm that the changed password still works after restart and that the selected download paths remain configured.
### step
8

### title
Perform an authorized functional test

### commands


### notes
Optionally add only a clearly authorized torrent, such as a torrent published by a Linux distribution for its own installation image. Confirm that incomplete and completed files appear only beneath the mapped /downloads paths. Remove the test task through the Web UI when finished. Do not delete its payload unless deletion is intentional.

## Expected results

- Podman image, runtime, event, configuration, and download state created by the lab resides beneath /opt/lab-classroom/class49/.
- The class49-qbittorrent container remains in a running state after initial startup and restart.
- The Web UI responds at http://127.0.0.1:8080 and requires authentication.
- The initial temporary password is replaced by a unique administrator-selected password.
- Host port 8080 is bound to 127.0.0.1 rather than to every host interface.
- Host TCP and UDP port 6881 are initially bound to 127.0.0.1, preventing direct LAN-originated inbound peer connections.
- qBittorrent configuration persists beneath /opt/lab-classroom/class49/config/ after the container is restarted or recreated.
- Completed and incomplete download locations map to separate directories beneath /opt/lab-classroom/class49/downloads/.
- Automatic external program execution and unnecessary automatic gateway port mapping are disabled.
- The exact repository digest returned during the image pull is recorded in /opt/lab-classroom/class49/image-digests.json.

## Verification checkpoints

- [ ] Run `. /opt/lab-classroom/class49/env.sh; p49podman ps --filter name=class49-qbittorrent` and confirm the container status is Up.
- [ ] Run `. /opt/lab-classroom/class49/env.sh; p49podman port class49-qbittorrent` and confirm the host-side addresses begin with 127.0.0.1.
- [ ] Run `ss -lnt | grep ':8080 '` and verify the listening address is 127.0.0.1 rather than 0.0.0.0 or an externally reachable host address.
- [ ] Run `ss -lntu | grep ':6881 '` and verify the initial TCP and UDP peer publications are limited to 127.0.0.1.
- [ ] Open http://127.0.0.1:8080 and verify that the old temporary password no longer authenticates after the password change.
- [ ] Restart the container, sign in using the new password, and verify that the download directories and security settings persisted.
- [ ] Run `find /opt/lab-classroom/class49/config -maxdepth 4 -type f -print` and confirm qBittorrent created configuration files under the designated configuration directory.
- [ ] Run `. /opt/lab-classroom/class49/env.sh; p49podman inspect class49-qbittorrent --format '{{json .Mounts}}'` and confirm only the intended config and downloads bind mounts are present.
- [ ] Run `. /opt/lab-classroom/class49/env.sh; p49podman inspect class49-qbittorrent --format '{{.HostConfig.Privileged}}'` and confirm the result is false.
- [ ] Inspect /opt/lab-classroom/class49/image-digests.json and confirm it contains the retrieved image's repository digest.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The class49 directory cannot be created. | The current user does not have permission to create directories beneath /opt/lab-classroom. | Have the lab administrator pre-create /opt/lab-classroom/class49 with ownership assigned to the lab user. Do not broaden permissions on unrelated directories. |
| The p49podman command is not found. | The lab environment file was not sourced in the current shell. | Run `. /opt/lab-classroom/class49/env.sh` and then retry the p49podman command. |
| Rootless Podman reports a user-namespace or subordinate-ID error. | Rootless Podman was not fully configured for the account, or the installed Podman version does not support the requested user-namespace behavior. | Stop the lab and have the host administrator correct the account's rootless Podman configuration. Do not switch the exercise to an unrestricted privileged container. |
| The container exits immediately and the log says /usr/bin/qbittorrent-nox does not exist. | The image layout changed after the lesson was reviewed. | Inspect the image documentation and image metadata, confirm the reviewed qBittorrent executable path, and update the entrypoint only after validating the image source and version. |
| The container reports that /config or /downloads is not writable. | The directories are not owned or writable by the user running rootless Podman, or files were previously created under a different identity. | Stop the container, inspect ownership beneath the class49 directory, and have the lab administrator restore ownership only within /opt/lab-classroom/class49/. Do not grant universal write access. |
| Port publication fails with an address-already-in-use message. | Another process is already listening on host port 8080 or 6881. | Identify the existing listener with `ss -lntu`, then either stop the conflicting lab service or choose an unused host port while retaining the 127.0.0.1 binding. |
| The Web UI does not load even though the container is running. | qBittorrent is still starting, the application exited after container creation, or the browser is not running on the same host. | Review `p49podman logs class49-qbittorrent`, verify the port mapping, and access 127.0.0.1 from the Podman host. Use a separately designed authenticated tunnel if remote administration is required. |
| No temporary password is visible in the current terminal. | The startup message scrolled out of view, the log was not queried, or the installed qBittorrent version uses different first-run behavior. | Run `. /opt/lab-classroom/class49/env.sh; p49podman logs class49-qbittorrent` and consult the qBittorrent Web UI documentation for the installed version. Do not guess or publish credentials. |
| A torrent can connect outbound but receives few or no inbound connections. | The peer port is intentionally bound to host loopback for the initial safe deployment. | Treat this as expected lab behavior. Design and review an explicit inbound peer-port exposure separately before changing the host binding. |
| Settings disappear after the container is recreated. | The configuration path was changed, the /config bind mount was omitted, or the container ran with a different application home. | Recreate the container with HOME and XDG_CONFIG_HOME set to /config and with /opt/lab-classroom/class49/config mounted at /config. |

## Security considerations

### controls
Run Podman rootlessly and run qBittorrent as the invoking user's numeric identity.
Drop all container capabilities and apply the no-new-privileges security option.
Publish the Web UI only on 127.0.0.1.
Publish the initial peer listener only on 127.0.0.1.
Replace the temporary Web UI password immediately with a unique password.
Retain Web UI authentication, host-header validation, cross-site request forgery protection, and clickjacking protection.
Disable automatic gateway port mapping unless a documented network requirement exists.
Do not enable external completion commands or add unreviewed search plugins.
Record and review the retrieved image digest before treating the installation as reproducible.
Back up configuration independently and treat downloaded content as untrusted.

### warnings
BitTorrent participation can reveal a peer's network address to trackers and other peers.
Protocol encryption does not provide anonymity.
A container is an isolation boundary, not a guarantee that malicious content cannot affect the host or user.
Exposing the Web UI beyond loopback without transport protection and carefully designed authentication can reveal credentials and administrative traffic.
Binding qBittorrent to a VPN interface is only useful when the binding and loss-of-VPN behavior have been tested.
Only download or distribute content for which you have authorization.

### credential_handling
The initial container log may contain a temporary administrator password. Keep /opt/lab-classroom/class49/initial-container.log private, change the password immediately, and remove or securely archive the log according to local policy after it is no longer needed.

### remote_access_guidance
Do not change the Web UI publication to 0.0.0.0 merely for convenience. A remote-management design should use an authenticated, encrypted access path and should preserve qBittorrent's Web UI security checks.

## Rollback

### preserve_data_procedure
Source the environment with `. /opt/lab-classroom/class49/env.sh`.
Stop the application with `p49podman stop class49-qbittorrent`.
If recreation is required, remove only the container object with `p49podman rm --force class49-qbittorrent`.
Leave /opt/lab-classroom/class49/config/ and /opt/lab-classroom/class49/downloads/ intact.
Re-run the reviewed container creation command to restore service using the retained bind-mounted data.

### configuration_rollback
Before making later configuration changes, stop the container and copy the relevant configuration file to a timestamped backup beneath /opt/lab-classroom/class49/config-backups/. Restore only while qBittorrent is stopped so the application does not overwrite the restored file.

### full_cleanup_policy
This lesson does not perform irreversible recursive deletion. After the container is stopped and removed, an administrator may archive or remove /opt/lab-classroom/class49/ under the site's data-retention procedure after verifying that no required downloads, configuration, credentials, or image records remain.

## Video narration notes

In this class, we install qBittorrent as a headless service while keeping every persistent lab artifact beneath the class49 directory. We begin by creating private directories for Podman storage, temporary state, qBittorrent configuration, and downloads. A small environment file ensures that rootless Podman does not silently use its normal storage locations. We then pull the reviewed qBittorrent image and record its repository digest. Remember that a tag such as latest can move; the digest is the stronger record of what was actually retrieved.

The container launches qBittorrent-nox directly as the current user's identity. It receives no Linux capabilities and cannot gain additional privileges. The Web UI is published only on 127.0.0.1 port 8080. The peer TCP and UDP ports are also initially limited to 127.0.0.1. This is intentionally conservative: it lets us configure and study the service before deciding whether any inbound peer access belongs in the network design.

After startup, we inspect the container log for the temporary Web UI password, sign in locally, and replace that password immediately. We preserve the protections for host-header validation, cross-site request forgery, and clickjacking. We configure completed and incomplete paths under the mounted downloads directory, disable automatic gateway port mapping unless it is specifically required, and make sure qBittorrent cannot automatically execute a program after a transfer. Search plugins and RSS automation should remain disabled when they are not needed.

Finally, we restart the service and verify persistence. We inspect the published addresses, container mounts, privilege state, and files created beneath the class directory. A legal test torrent may be used if its publisher clearly authorizes distribution. Throughout the exercise, remember that peer-to-peer protocol encryption is not anonymity, downloaded content is not automatically safe, and remote Web UI exposure requires a separate security design. The rollback procedure removes only the disposable container object while preserving configuration and downloads.

## References

- qBittorrent official website — https://www.qbittorrent.org/
- qBittorrent Wiki: Web UI — https://github.com/qbittorrent/qBittorrent/wiki/Web-UI
- qBittorrent Wiki: Explanation of Options — https://github.com/qbittorrent/qBittorrent/wiki/Explanation-of-Options-in-qBittorrent
- qBittorrent GitHub repository — https://github.com/qbittorrent/qBittorrent
- LinuxServer.io qBittorrent image documentation — https://docs.linuxserver.io/images/docker-qbittorrent/
- Podman command documentation — https://docs.podman.io/en/latest/markdown/podman.1.html
- Podman run documentation — https://docs.podman.io/en/latest/markdown/podman-run.1.html
- Podman rootless-mode documentation — https://docs.podman.io/en/latest/markdown/podman.1.html#rootless-mode

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

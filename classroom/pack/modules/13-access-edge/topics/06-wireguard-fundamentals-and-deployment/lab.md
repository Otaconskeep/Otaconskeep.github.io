# Lab: WireGuard Fundamentals and Deployment

**Module:** Edge Access & VPN
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain how WireGuard uses public keys as peer identities.

## Before you start

- Comfort using a Linux shell and reading INI-style configuration files.
- Basic understanding of IPv4 addressing, CIDR notation, routing tables, UDP, and network address translation.
- A Linux lab host with Python 3 and the WireGuard command-line utility installed before class.
- Write access to /opt/lab-classroom/class69/.
- Understanding that the documentation-only endpoint vpn.example.invalid is intentionally nonfunctional.

## Guided lab

### scope
All persistent changes are confined to /opt/lab-classroom/class69/. The exercise does not create an interface, alter routing, contact the example endpoint, or modify host services.

### steps
### name
Confirm required tools

### commands
command -v wg
python3 --version

### notes
These commands are read-only. Stop if either required program is unavailable; do not install packages as part of this constrained laboratory.
### name
Create protected laboratory directories

### commands
install -d -m 700 /opt/lab-classroom/class69/keys /opt/lab-classroom/class69/configs

### notes
The directories are inside the only permitted mutation path.
### name
Generate peer keys and a preshared key

### commands
set -eu; umask 077; LAB=/opt/lab-classroom/class69; wg genkey > "$LAB/keys/gateway.private"; wg pubkey < "$LAB/keys/gateway.private" > "$LAB/keys/gateway.public"; wg genkey > "$LAB/keys/client.private"; wg pubkey < "$LAB/keys/client.private" > "$LAB/keys/client.public"; wg genpsk > "$LAB/keys/peer.psk"

### notes
Private values are redirected directly into protected files. Do not display private-key or preshared-key files in shared terminals, transcripts, tickets, or screenshots.
### name
Create the staged gateway configuration

### commands
set -eu; umask 077; LAB=/opt/lab-classroom/class69; GATEWAY_PRIVATE=$(cat "$LAB/keys/gateway.private"); CLIENT_PUBLIC=$(cat "$LAB/keys/client.public"); PEER_PSK=$(cat "$LAB/keys/peer.psk"); printf '%s\n' '[Interface]' "PrivateKey = $GATEWAY_PRIVATE" 'Address = 10.69.0.1/24' 'ListenPort = 51820' '' '[Peer]' "PublicKey = $CLIENT_PUBLIC" "PresharedKey = $PEER_PSK" 'AllowedIPs = 10.69.0.2/32' > "$LAB/configs/gateway.conf"; unset GATEWAY_PRIVATE CLIENT_PUBLIC PEER_PSK

### notes
The peer receives a unique /32 authorization on the gateway.
### name
Create the staged client configuration

### commands
set -eu; umask 077; LAB=/opt/lab-classroom/class69; CLIENT_PRIVATE=$(cat "$LAB/keys/client.private"); GATEWAY_PUBLIC=$(cat "$LAB/keys/gateway.public"); PEER_PSK=$(cat "$LAB/keys/peer.psk"); printf '%s\n' '[Interface]' "PrivateKey = $CLIENT_PRIVATE" 'Address = 10.69.0.2/24' '' '[Peer]' "PublicKey = $GATEWAY_PUBLIC" "PresharedKey = $PEER_PSK" 'Endpoint = vpn.example.invalid:51820' 'AllowedIPs = 10.69.0.0/24' 'PersistentKeepalive = 25' > "$LAB/configs/client.conf"; unset CLIENT_PRIVATE GATEWAY_PUBLIC PEER_PSK

### notes
The reserved .invalid name prevents accidental use as a real service endpoint. The selected prefix demonstrates split tunneling.
### name
Verify permissions and cryptographic relationships

### commands
stat -c '%a %n' /opt/lab-classroom/class69/keys /opt/lab-classroom/class69/configs /opt/lab-classroom/class69/keys/gateway.private /opt/lab-classroom/class69/keys/client.private /opt/lab-classroom/class69/keys/peer.psk /opt/lab-classroom/class69/configs/gateway.conf /opt/lab-classroom/class69/configs/client.conf
set -eu; LAB=/opt/lab-classroom/class69; test "$(wg pubkey < "$LAB/keys/gateway.private")" = "$(cat "$LAB/keys/gateway.public")"; test "$(wg pubkey < "$LAB/keys/client.private")" = "$(cat "$LAB/keys/client.public")"; echo 'Key derivation checks passed.'
set -eu; LAB=/opt/lab-classroom/class69; grep -Fqx 'AllowedIPs = 10.69.0.2/32' "$LAB/configs/gateway.conf"; grep -Fqx 'AllowedIPs = 10.69.0.0/24' "$LAB/configs/client.conf"; grep -Fqx 'Endpoint = vpn.example.invalid:51820' "$LAB/configs/client.conf"; echo 'Configuration policy checks passed.'

### notes
The checks avoid printing secret values. Directories should report mode 700, while generated files should report mode 600.

### deployment_plan
Replace documentation addresses and names with approved production values.
Generate each production private key on the peer that will own it.
Exchange and independently verify only public keys.
Confirm that tunnel and routed prefixes do not overlap existing networks.
Confirm outer UDP reachability, forwarding policy, return routing, DNS behavior, and IPv6 scope.
Capture a known-good out-of-band access method before activation.
Activate one peer during a change window and inspect handshake age, byte counters, routes, and application reachability.
Stop and revert if administrative access, expected routing, or policy enforcement changes unexpectedly.

## Expected results

- The directories /opt/lab-classroom/class69/keys and /opt/lab-classroom/class69/configs exist with mode 700.
- The key directory contains gateway.private, gateway.public, client.private, client.public, and peer.psk.
- The configuration directory contains gateway.conf and client.conf with mode 600.
- Deriving a public key from each private key reproduces the corresponding saved public key.
- The gateway configuration authorizes the client as 10.69.0.2/32.
- The client configuration routes only 10.69.0.0/24 through the staged peer.
- The client endpoint is vpn.example.invalid:51820 and is intentionally unsuitable for live use.
- No WireGuard interface, route, service, or host network policy is changed by the lab.

## Verification

- [ ] Run: stat -c '%a %n' /opt/lab-classroom/class69/keys /opt/lab-classroom/class69/configs. Both directories should report 700.
- [ ] Run: stat -c '%a %n' /opt/lab-classroom/class69/keys/gateway.private /opt/lab-classroom/class69/keys/client.private /opt/lab-classroom/class69/keys/peer.psk /opt/lab-classroom/class69/configs/gateway.conf /opt/lab-classroom/class69/configs/client.conf. Each file should report 600.
- [ ] Run: test "$(wg pubkey < /opt/lab-classroom/class69/keys/gateway.private)" = "$(cat /opt/lab-classroom/class69/keys/gateway.public)" && echo PASS. The output should be PASS.
- [ ] Run: test "$(wg pubkey < /opt/lab-classroom/class69/keys/client.private)" = "$(cat /opt/lab-classroom/class69/keys/client.public)" && echo PASS. The output should be PASS.
- [ ] Run: grep -Fqx 'AllowedIPs = 10.69.0.2/32' /opt/lab-classroom/class69/configs/gateway.conf && echo PASS. The output should be PASS.
- [ ] Run: grep -Fqx 'AllowedIPs = 10.69.0.0/24' /opt/lab-classroom/class69/configs/client.conf && echo PASS. The output should be PASS.
- [ ] Run: grep -Fqx 'Endpoint = vpn.example.invalid:51820' /opt/lab-classroom/class69/configs/client.conf && echo PASS. The output should be PASS.
- [ ] Confirm through the host's normal read-only network inspection process that no interface or route was added for this staged exercise.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| The wg command is not found. | The WireGuard command-line utilities were not installed before the constrained lab. | Stop the lab and ask the lab administrator to prepare the required package outside the exercise. Do not modify the host package set during this lab. |
| Key generation reports permission denied. | The learner cannot write to /opt/lab-classroom/class69/ or an existing directory has incompatible ownership. | Have the lab administrator correct ownership only within /opt/lab-classroom/class69/, then repeat the affected generation step. |
| A key derivation comparison fails. | A public-key file was copied from the wrong peer, a key file was altered, or an earlier command only partially completed. | Do not mix individual files from different attempts. Remove the staged artifacts using the documented rollback procedure, regenerate the complete key set, and rebuild both configurations. |
| A configuration policy check fails. | The configuration was manually edited, whitespace or capitalization changed, or gateway and client prefixes were reversed. | Review the intended roles, recreate the affected file from the lab command, and repeat the exact-match checks. |
| A future live deployment has no handshake. | Possible causes include mismatched public keys, mismatched preshared keys, an incorrect endpoint, blocked UDP traffic, an inactive listener, or incorrect system time. | Compare public-key fingerprints through a trusted channel, confirm both peers use the same preshared key, verify endpoint resolution and UDP reachability, and inspect listener and handshake state without exposing private material. |
| A future live deployment shows a handshake but cannot pass application traffic. | AllowedIPs, local routes, forwarding policy, destination-side return routes, address translation, MTU, or service authorization may be incorrect. | Trace the inner source and destination in both directions, inspect route selection on every hop, verify that each peer owns the claimed source prefix, test smaller packets for an MTU problem, and confirm the destination service permits the tunnel source. |
| A roaming client works briefly and then becomes unreachable while idle. | An intervening NAT mapping expires when no authenticated traffic is sent. | Apply PersistentKeepalive only to the NATed peer that needs inbound reachability and validate an interval appropriate for the environment. |
| Internet access unexpectedly follows the tunnel in a future deployment. | A default prefix was placed in the client's AllowedIPs, creating a full-tunnel route. | Restore the intended split-tunnel prefixes and verify both IPv4 and IPv6 route scope before reactivation. |

## Security

### key_handling
Generate production private keys locally on the systems that will own them.
Never transmit, paste, log, or ticket private keys.
Treat a preshared key as secret on both peers and rotate it if either copy may be exposed.
Protect configurations because they commonly embed private and preshared keys.
Use an authenticated secondary channel to verify public-key fingerprints.

### least_privilege
Assign each client only the individual tunnel address and destination prefixes it needs.
Avoid broad AllowedIPs when a smaller set accurately represents the peer.
Apply service-level and network-level authorization in addition to tunnel authentication.
Separate administrative access from general user or application tunnels where practical.

### operational_guidance
WireGuard encrypts traffic between peers but does not make activity anonymous.
Outer IP addresses, UDP ports, packet sizes, and timing remain observable.
A recent handshake proves cryptographic peer contact, not successful application authorization.
Plan both IPv4 and IPv6 explicitly to avoid bypasses or accidental loss of connectivity.
Maintain an out-of-band recovery path before changing remote access or default routing.
Record peer ownership, assigned prefixes, key creation date, intended endpoint, and rotation history without recording private keys.

### rotation
Introduce a newly generated peer identity through a controlled configuration change, verify it, remove the old public-key authorization, and securely retire old secret material according to organizational policy. WireGuard peer identity changes are configuration changes rather than certificate renewals.

### incident_response
If a private or preshared key is suspected of exposure, treat the associated identity as compromised. Remove or replace its authorization, generate fresh secret material, verify the new public key through a trusted channel, review reachable services, and inspect available connection metadata for unexpected use.

## Rollback

### scope
Rollback deletes only artifacts created under /opt/lab-classroom/class69/. It cannot recover deleted keys; regeneration creates new identities.

### commands
find /opt/lab-classroom/class69 -type f -delete
find /opt/lab-classroom/class69 -depth -type d -empty -delete

### verification
Run: test ! -e /opt/lab-classroom/class69 && echo 'Rollback complete.'
If the top directory intentionally remains, run: find /opt/lab-classroom/class69 -mindepth 1 -print. Successful content cleanup produces no output.

### production_note
For a live deployment, rollback must also restore the previously approved peer configuration, route behavior, forwarding policy, name resolution, and service state through the environment's change-management system. The constrained lab performs none of those live changes.

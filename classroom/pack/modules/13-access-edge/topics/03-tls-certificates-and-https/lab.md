# Lab: TLS Certificates and HTTPS

**Module:** Edge Access & VPN
**Activity type:** Lab (Practice)
**Lab risk:** low
**Objective:** Explain the distinct roles of a private key, public key, certificate signing request, certificate, and certificate authority

## Before you start

- Basic familiarity with TCP/IP, DNS names, ports, and client-server communication
- Basic shell navigation and command execution
- OpenSSL command-line tools
- curl with HTTPS support
- Permission to create files under /opt/lab-classroom/class66/
- An unused local TCP port 8443

## Guided lab

### goal
Create a local CA, issue a localhost server certificate, observe failure without explicit trust, verify success with explicit trust, inspect the peer certificate, and stop the server safely.

### steps
### step
1

### title
Create and secure the lab directory

### command
LAB=/opt/lab-classroom/class66; mkdir -p "$LAB" && chmod 700 "$LAB" && printf 'Lab directory: %s\n' "$LAB"

### explanation
The directory is the only location mutated by this lab. Restrictive directory permissions reduce accidental exposure of generated private keys.
### step
2

### title
Generate the lab CA private key and self-signed CA certificate

### command
LAB=/opt/lab-classroom/class66; openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$LAB/ca.key" && chmod 600 "$LAB/ca.key" && openssl req -x509 -new -sha256 -key "$LAB/ca.key" -days 365 -subj "/CN=Class 66 Lab Root CA/O=OtaconsKeep Homelab Academy" -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign" -addext "subjectKeyIdentifier=hash" -out "$LAB/ca.crt"

### explanation
The CA certificate is self-signed and suitable only as a lab trust anchor. The CA private key never leaves the class directory.
### step
3

### title
Generate the server key and certificate signing request

### command
LAB=/opt/lab-classroom/class66; openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$LAB/server.key" && chmod 600 "$LAB/server.key" && openssl req -new -sha256 -key "$LAB/server.key" -subj "/CN=localhost/O=OtaconsKeep Homelab Academy" -out "$LAB/server.csr" && openssl req -in "$LAB/server.csr" -noout -verify

### explanation
The CSR proves possession of the server private key and carries the requested subject. Identity authorization will be encoded through certificate extensions during issuance.
### step
4

### title
Define server certificate extensions

### command
LAB=/opt/lab-classroom/class66; cat > "$LAB/server.ext" <<'EOF'
[server_cert]
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
subjectAltName=@alt_names

[alt_names]
DNS.1=localhost
IP.1=127.0.0.1
EOF

### explanation
The extension profile prevents the leaf certificate from acting as a CA, enables server authentication, and supplies both DNS and IPv4 loopback identities.
### step
5

### title
Issue the server certificate

### command
LAB=/opt/lab-classroom/class66; openssl x509 -req -sha256 -in "$LAB/server.csr" -CA "$LAB/ca.crt" -CAkey "$LAB/ca.key" -CAserial "$LAB/ca.srl" -CAcreateserial -days 30 -extfile "$LAB/server.ext" -extensions server_cert -out "$LAB/server.crt" && openssl verify -CAfile "$LAB/ca.crt" "$LAB/server.crt"

### explanation
The CA signs the CSR and applies the controlled extension profile. openssl verify confirms that the issued certificate chains to the supplied lab CA.
### step
6

### title
Inspect certificate identity and usage

### command
LAB=/opt/lab-classroom/class66; openssl x509 -in "$LAB/server.crt" -noout -subject -issuer -dates -serial -ext basicConstraints -ext extendedKeyUsage -ext subjectAltName && openssl x509 -in "$LAB/server.crt" -noout -checkhost localhost && openssl x509 -in "$LAB/server.crt" -noout -checkip 127.0.0.1

### explanation
This confirms the issuer, validity window, server-auth usage, non-CA status, and both intended identities before the certificate is placed into service.
### step
7

### title
Start the loopback-only OpenSSL TLS server and record its actual PID

### command
LAB=/opt/lab-classroom/class66; cd "$LAB" || exit 1; nohup openssl s_server -accept 127.0.0.1:8443 -cert "$LAB/server.crt" -key "$LAB/server.key" -www </dev/null >"$LAB/server.log" 2>&1 & pid=$!; printf '%s\n' "$pid" > "$LAB/server.pid"; sleep 1; args=$(ps -p "$pid" -o args= 2>/dev/null || true); case "$args" in *"openssl s_server"*"$LAB/server.crt"*) printf 'TLS server PID %s is running on 127.0.0.1:8443\n' "$pid" ;; *) printf 'TLS server did not start as expected. Log follows:\n' >&2; cat "$LAB/server.log" >&2; exit 1 ;; esac

### explanation
The shell changes directory first and then backgrounds the simple nohup command. nohup executes OpenSSL in the same recorded process, so $! identifies the OpenSSL server rather than a background subshell. The command line is checked before continuing.
### step
8

### title
Demonstrate failure when the lab CA is not trusted

### command
set +e; output=$(curl --noproxy '*' --resolve localhost:8443:127.0.0.1 --silent --show-error https://localhost:8443/ 2>&1); rc=$?; set -e; printf '%s\n' "$output"; if [ "$rc" -eq 0 ]; then printf 'Unexpected success without the lab CA\n' >&2; exit 1; fi; printf 'Expected certificate verification failure occurred; curl exit status was %s\n' "$rc"

### explanation
The server certificate is signed correctly, but the client does not yet trust the private lab CA. --resolve preserves the requested DNS name while forcing the connection to the IPv4 address on which the server listens.
### step
9

### title
Trust only the lab CA for this request

### command
LAB=/opt/lab-classroom/class66; curl --noproxy '*' --resolve localhost:8443:127.0.0.1 --fail --silent --show-error --cacert "$LAB/ca.crt" https://localhost:8443/

### explanation
Supplying --cacert allows curl to build a trusted chain while still validating the DNS identity localhost against the certificate Subject Alternative Name.
### step
10

### title
Verify the live TLS peer with OpenSSL

### command
LAB=/opt/lab-classroom/class66; openssl s_client -connect 127.0.0.1:8443 -servername localhost -CAfile "$LAB/ca.crt" -verify_return_error -showcerts </dev/null >"$LAB/s_client.out" 2>"$LAB/s_client.err" && openssl x509 -in "$LAB/s_client.out" -noout -subject -issuer -fingerprint -sha256 && openssl x509 -in "$LAB/s_client.out" -noout -checkhost localhost

### explanation
The client sends localhost through Server Name Indication, requires successful chain verification, saves diagnostic output inside the lab directory, and performs a separate identity check on the presented certificate.
### step
11

### title
Stop the exact OpenSSL server process

### command
LAB=/opt/lab-classroom/class66; pid=$(cat "$LAB/server.pid") || exit 1; args=$(ps -p "$pid" -o args= 2>/dev/null || true); case "$args" in *"openssl s_server"*"$LAB/server.crt"*) kill "$pid" || exit 1 ;; *) printf 'Refusing to signal PID %s because it is not the expected lab OpenSSL server\n' "$pid" >&2; exit 1 ;; esac; i=0; while kill -0 "$pid" 2>/dev/null && [ "$i" -lt 50 ]; do sleep 0.1; i=$((i + 1)); done; if kill -0 "$pid" 2>/dev/null; then printf 'Server PID %s did not exit; preserve artifacts and investigate\n' "$pid" >&2; exit 1; fi; find "$LAB" -maxdepth 1 -type f -name 'server.pid' -delete; printf 'TLS server PID %s has exited\n' "$pid"

### explanation
The PID is matched to both openssl s_server and the lab certificate path before signaling. The process must disappear before its PID record is removed.

## Expected results

- The lab directory exists with restrictive permissions and all generated artifacts remain under /opt/lab-classroom/class66/.
- openssl verify reports /opt/lab-classroom/class66/server.crt: OK.
- Certificate inspection shows CA:FALSE, TLS Web Server Authentication, DNS:localhost, and IP Address:127.0.0.1.
- The first curl request fails because the private lab CA is not trusted by default.
- The curl request using --cacert succeeds and returns the OpenSSL s_server status page.
- The live peer certificate is issued by the Class 66 lab CA and passes the localhost identity check.
- The shutdown step reports that the recorded TLS server PID exited.

## Verification

- [ ] Run `openssl verify -CAfile /opt/lab-classroom/class66/ca.crt /opt/lab-classroom/class66/server.crt`; the result must end with `server.crt: OK`.
- [ ] Run `openssl x509 -in /opt/lab-classroom/class66/server.crt -noout -checkhost localhost`; it must report that the certificate matches the host.
- [ ] Run `openssl x509 -in /opt/lab-classroom/class66/server.crt -noout -checkip 127.0.0.1`; it must report that the certificate matches the IP address.
- [ ] While the server is running, run `curl --noproxy '*' --resolve localhost:8443:127.0.0.1 --fail --cacert /opt/lab-classroom/class66/ca.crt https://localhost:8443/`; it must complete without a certificate error.
- [ ] After the stop step, the PID recorded before shutdown must no longer appear in `ps`, and a connection to 127.0.0.1:8443 should fail unless another service independently uses that port.
- [ ] Confirm that the exercise did not install ca.crt into a system or browser trust store.

## Break/fix

| Symptom | Likely cause | Fix |
|---|---|---|
| OpenSSL reports that -addext is unknown. | The installed OpenSSL version predates support for the option or uses a vendor-specific command implementation. | Use OpenSSL 1.1.1 or newer for this lesson. Do not silently omit CA constraints or key-usage extensions. |
| The server startup check fails and server.log says the address is already in use. | Another process is listening on 127.0.0.1:8443. | Identify and stop only the conflicting service if it is safe to do so, or schedule the lab when the required port is free. Do not change the certificate identity merely to bypass the conflict. |
| The first curl request succeeds even though --cacert was not supplied. | The lab CA or an equivalent signing certificate was previously added to a client trust store, or curl is being affected by CA-related environment variables. | Inspect curl's TLS backend and CA environment settings, remove unintended lab trust through the mechanism that added it, and repeat using a clean client configuration. |
| curl reports a hostname or subject name mismatch. | The requested URL identity is not present in the certificate Subject Alternative Name extension. | Use the URL https://localhost:8443/ with the supplied --resolve option, then inspect the certificate with `openssl x509 -ext subjectAltName`. |
| curl reports connection refused instead of a certificate verification error. | The OpenSSL server failed to start, exited, or is not listening on 127.0.0.1:8443. | Read /opt/lab-classroom/class66/server.log and validate the saved PID with ps. Restart only after resolving the logged error. |
| The shutdown step refuses to signal the recorded PID. | The PID file is stale, the server exited, or the operating system reused the PID for a different process. | Inspect the PID and command line manually. Never signal a mismatched process. If the expected OpenSSL server is already absent, remove the stale PID record inside the lab directory. |
| OpenSSL chain verification succeeds but an HTTPS client still rejects the endpoint. | Chain validation and service identity validation are separate checks; the URL name may not match the certificate SAN, or the client may impose additional policy. | Check the requested hostname, Subject Alternative Name entries, validity dates, extended key usage, and the specific client error. |

## Security

### controls
The server binds only to 127.0.0.1, preventing direct access from other hosts.
The exercise supplies the lab CA per command rather than installing it into a machine-wide trust store.
CA and server private keys are stored only under the class directory with owner-only file permissions.
The server PID is validated against its command line and certificate path before any signal is sent.
The generated CA is for education only and must not issue certificates for production or externally reachable services.

### key_management
Anyone who obtains ca.key can issue certificates accepted wherever ca.crt is trusted. Anyone who obtains server.key can impersonate this lab server while the certificate is valid. Do not copy these keys to shared storage or source-control repositories.

### trust_warning
Installing a private lab CA as a global trust anchor grants it broad authority to authenticate services. This lab deliberately avoids that change.

### exposure_warning
OpenSSL s_server is a diagnostic tool, not a production web server. It is loopback-bound and should be stopped after testing.

## Rollback

### objective
Stop the expected OpenSSL server, confirm that it has exited, and then remove only the class directory and its artifacts.

### command
LAB=/opt/lab-classroom/class66; if [ -d "$LAB" ]; then if [ -f "$LAB/server.pid" ]; then pid=$(cat "$LAB/server.pid"); args=$(ps -p "$pid" -o args= 2>/dev/null || true); case "$args" in *"openssl s_server"*"$LAB/server.crt"*) kill "$pid" || exit 1; i=0; while kill -0 "$pid" 2>/dev/null && [ "$i" -lt 50 ]; do sleep 0.1; i=$((i + 1)); done; if kill -0 "$pid" 2>/dev/null; then kill -KILL "$pid" || exit 1; i=0; while kill -0 "$pid" 2>/dev/null && [ "$i" -lt 20 ]; do sleep 0.1; i=$((i + 1)); done; fi; if kill -0 "$pid" 2>/dev/null; then printf 'Unable to confirm exit of PID %s; rollback aborted before deleting artifacts\n' "$pid" >&2; exit 1; fi ;; "") printf 'Recorded PID %s is not running; continuing with artifact cleanup\n' "$pid" ;; *) printf 'PID %s belongs to another process; rollback aborted without signaling or deleting artifacts\n' "$pid" >&2; exit 1 ;; esac; fi; find "$LAB" -mindepth 1 -maxdepth 1 -type f -delete && rmdir "$LAB"; fi

### verification
Confirm that no process matching the recorded PID remains before deletion, that /opt/lab-classroom/class66/ no longer exists, and that no system trust store was changed.

### scope
The rollback neither signals an unverified PID nor deletes anything outside /opt/lab-classroom/class66/.

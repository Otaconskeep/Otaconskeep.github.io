# Class 66: TLS Certificates and HTTPS

**Learning objective:** Explain the distinct roles of a private key, public key, certificate signing request, certificate, and certificate authority; Create a private lab certificate authority without modifying the operating system trust store; Issue a server certificate containing DNS and IP Subject Alternative Names; Run a loopback-only TLS service and record the PID of the actual OpenSSL server process; Distinguish trust-chain validation from hostname validation; Use curl and OpenSSL to verify a certificate chain and HTTPS endpoint; Stop the TLS service safely and remove only class-specific artifacts
**Bloom level:** Understand / Apply
**Track:** Networking and Security · **Difficulty:** intermediate · **Duration:** ~75 minutes · **Lab risk:** low
**Build output:** Teach how TLS certificates establish server identity, how certificate authorities and trust stores participate in verification, how hostname validation uses Subject Alternative Names, and how to operate and verify a small HTTPS service using OpenSSL and curl.
**Mastery unlock:** ≥80% quiz + completed Feynman teach-back + lab verification + homework evidence.
**Last reviewed:** 2025-02-20
**Compatibility:** ### operating_systems
Linux distributions with a POSIX-like shell and procps-compatible ps
Linux hosts where /opt/lab-classroom/class66/ can be created by the learner

### required_tools
OpenSSL 1.1.1 or newer
curl with TLS support
Standard shell utilities including mkdir, chmod, cat, ps, find, grep, and sleep

### network_requirements
No external network access is required after tools are installed. TCP port 8443 must be free on 127.0.0.1.

### notes
Commands use RSA keys for broad instructional compatibility. The TLS protocol and cipher suite are negotiated by the installed OpenSSL build. The lesson does not depend on a specific negotiated cipher or performance result.

## Learning objective

- Explain the distinct roles of a private key, public key, certificate signing request, certificate, and certificate authority
- Create a private lab certificate authority without modifying the operating system trust store
- Issue a server certificate containing DNS and IP Subject Alternative Names
- Run a loopback-only TLS service and record the PID of the actual OpenSSL server process
- Distinguish trust-chain validation from hostname validation
- Use curl and OpenSSL to verify a certificate chain and HTTPS endpoint
- Stop the TLS service safely and remove only class-specific artifacts

## Why this matters

Teach how TLS certificates establish server identity, how certificate authorities and trust stores participate in verification, how hostname validation uses Subject Alternative Names, and how to operate and verify a small HTTPS service using OpenSSL and curl.

## Prerequisites

- Basic familiarity with TCP/IP, DNS names, ports, and client-server communication
- Basic shell navigation and command execution
- OpenSSL command-line tools
- curl with HTTPS support
- Permission to create files under /opt/lab-classroom/class66/
- An unused local TCP port 8443

## Required reading

- OpenSSL documentation: https://docs.openssl.org/3.0/man1/openssl-req/
- OpenSSL certificate command documentation: https://docs.openssl.org/3.0/man1/openssl-x509/
- OpenSSL TLS server documentation: https://docs.openssl.org/3.0/man1/openssl-s_server/
- RFC 5280, Internet X.509 Public Key Infrastructure Certificate and CRL Profile: https://www.rfc-editor.org/rfc/rfc5280
- RFC 6125, Service Identity in TLS: https://www.rfc-editor.org/rfc/rfc6125

## Prior-knowledge check

Answer briefly before reading Instruction.

1. What problem does this class prevent in a homelab?
2. What disposable lab boundary will you use?
3. What evidence will prove you succeeded?

## Vocabulary

| Term | Meaning |
|---|---|
| TLS | Transport Layer Security, the protocol that provides encryption, integrity protection, and authenticated identities for connections such as HTTPS. |
| HTTPS | HTTP carried through a TLS connection. The TLS layer is established and verified before normal HTTP messages are exchanged. |
| Private key | Secret cryptographic material used to prove possession of an identity and perform operations such as signing. It must not be distributed with the certificate. |
| Public key | The non-secret portion of a key pair. A certificate binds a public key to an asserted identity. |
| Certificate authority | An entity whose certificate and private key are used to sign other certificates. Clients must trust an appropriate CA before accepting certificates issued by it. |
| Certificate signing request | A signed request containing a public key and requested identity information. A CA validates the request according to policy before issuing a certificate. |
| Certificate chain | A sequence from a leaf certificate through one or more issuing CA certificates to a trust anchor recognized by the client. |
| Trust anchor | A CA certificate explicitly trusted by a client or operating system. Trust anchors are commonly stored in a system or application-specific trust store. |
| Subject Alternative Name | The certificate extension containing DNS names, IP addresses, or other identities for which a certificate is valid. |
| Hostname validation | The client-side comparison of the requested service name with identities in the server certificate, normally its Subject Alternative Name extension. |
| PEM | A text encoding that wraps base64-encoded cryptographic data between BEGIN and END labels. |
| TLS handshake | The exchange in which peers negotiate protocol parameters, establish session keys, and authenticate the server certificate before application data is transferred. |

## Instruction

TLS addresses three major properties of a network connection: confidentiality, integrity, and authentication. Encryption prevents an observer from directly reading application traffic. Integrity checks detect unauthorized changes in transit. Authentication lets a client determine whether the peer presenting a certificate is authorized for the requested identity. These properties are related but not interchangeable. A connection may be encrypted while still being vulnerable to impersonation if the client does not verify the certificate.

A server certificate contains a public key, identity information, validity dates, usage restrictions, and a digital signature from an issuer. The matching private key remains on the server. During the TLS handshake, the server proves possession of that private key. The client then evaluates the certificate chain against its trusted CA certificates. A valid issuer signature alone is insufficient: the chain must lead to a trust anchor accepted by the client, the certificate must be within its validity period, its extensions must allow server authentication, and the requested hostname or IP address must match a Subject Alternative Name.

A self-created CA is not automatically trusted. This is why an initial curl request to the lab server should fail even though the certificate is correctly signed by the lab CA. Supplying the CA certificate explicitly with --cacert creates narrow, command-specific trust without altering the machine-wide trust store. This is safer for a classroom exercise and demonstrates that trust is a client policy decision rather than a property a server can declare for itself.

Modern clients use the Subject Alternative Name extension for identity checks. The certificate Common Name should not be treated as a substitute. This lab includes both DNS:localhost and IP:127.0.0.1 so students can examine both identity forms. curl is instructed to resolve localhost directly to 127.0.0.1. That preserves the DNS name used for certificate validation while avoiding an IPv6 localhost connection to a server intentionally bound only to IPv4 loopback.

Operationally, private-key handling is as important as certificate issuance. The lab directory is restricted, private keys receive owner-only permissions, and the server listens only on loopback. The OpenSSL server is started as the direct background command after changing directories; its actual PID is recorded and validated against its command line. Shutdown checks that the PID still belongs to the expected OpenSSL process before signaling it, waits for process termination, and only then removes the PID record or lab artifacts.

## Architecture

### components
### name
Lab root CA

### role
Signs the server certificate and acts as an explicitly supplied trust anchor for lab clients.

### location
/opt/lab-classroom/class66/ca.crt
### name
HTTPS test server

### role
Uses the issued certificate and private key to provide a local TLS endpoint.

### location
127.0.0.1:8443
### name
TLS client

### role
Uses curl or openssl s_client to validate the chain, service identity, and handshake.

### location
The same host as the test server

### trust_flow
The client connects using the service identity localhost. The server presents server.crt and proves possession of server.key. The client validates the issuer signature using ca.crt, checks certificate validity and usage, and compares localhost with the DNS Subject Alternative Name.

### scope
All generated keys, certificates, logs, serial files, extension files, and PID records remain under /opt/lab-classroom/class66/. No system trust store or production service configuration is changed.

## Worked example

See the worked example embedded in Instruction; reproduce it on your disposable lab path.

## Guided practice

Complete the guided lab steps with hints allowed, then restate results in your own words.

## Independent practice

### tasks
Draw the lab trust chain and label the trust anchor, issuer, leaf certificate, public keys, and private keys.
Inspect server.crt and list every condition a client should check before accepting it for https://localhost:8443/.
Explain what error should occur if a client connects using a DNS name not present in the Subject Alternative Name extension.
Compare the security consequences of losing server.key with those of losing ca.key.
Write a certificate-renewal plan that replaces a leaf certificate before expiration without changing the trusted CA or exposing private keys.
Explain why placing the lab CA into a global trust store would expand risk beyond this single endpoint.

### submission
Provide a short trust-chain diagram, certificate inspection notes, and written answers. Do not submit private-key contents.

## Feynman teach-back

### prompt
Explain HTTPS to a new administrator without using the phrase 'it is secure because it has a lock icon.'

### model_explanation
The server owns a private key and presents a certificate containing the matching public key and approved service names. A certificate authority signs that certificate. The client trusts selected CA certificates, verifies the issuer chain and validity rules, and confirms that the requested hostname appears in the certificate. The server proves possession of its private key during the handshake, and both sides derive temporary session keys used to encrypt and authenticate application traffic. If the CA is not trusted or the name does not match, encryption alone does not establish that the client reached the intended server.

### self_check
Can you explain why the server certificate may be public but the server private key must remain secret?
Can you distinguish chain trust from hostname validation?
Can you explain why explicitly supplying ca.crt changes the result without changing the server certificate?
Can you explain why localhost was forced to 127.0.0.1 while still remaining the URL hostname?

## Retrieval check

1. 1. What does a server prove by successfully completing a TLS handshake with a certificate's matching private key?
2. 2. Why does a correctly signed certificate from the lab CA fail in curl before --cacert is supplied?
3. 3. Which certificate field should contain localhost for modern hostname validation?
4. 4. What is the difference between certificate-chain validation and hostname validation?
5. 5. Why does the lab use --resolve localhost:8443:127.0.0.1 instead of requesting https://127.0.0.1:8443/ for the primary DNS-name test?
6. 6. Why must a shutdown procedure verify a recorded PID's command line before signaling it?
7. 7. Which private key creates the greater trust impact if compromised: server.key or ca.key, and why?

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

## Verification checkpoints

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

## Security considerations

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

## Video narration notes

Begin by showing the empty class directory and describing TLS as a combination of encryption, integrity, and authenticated identity. Generate the lab CA and emphasize that ca.key is the authority's critical secret while ca.crt is the public trust anchor. Generate the server key and CSR, then display the extension file and point out CA:FALSE, serverAuth, DNS:localhost, and IP:127.0.0.1. Sign the CSR and verify the chain before starting any service. Start OpenSSL s_server only on IPv4 loopback, showing that the command backgrounds OpenSSL itself and records the actual server PID. Demonstrate the first curl failure without the lab CA and explain that a valid signature is not enough when the issuer is untrusted. Repeat with --cacert and --resolve, noting that localhost remains the validated service name while the connection is forced to 127.0.0.1. Use openssl s_client to inspect the live peer and verify its chain. Finish by validating the recorded process command, stopping that exact OpenSSL server, confirming its exit, and discussing why cleanup must not delete PID evidence before termination is confirmed.

## References

- OpenSSL req documentation: https://docs.openssl.org/3.0/man1/openssl-req/
- OpenSSL x509 documentation: https://docs.openssl.org/3.0/man1/openssl-x509/
- OpenSSL verify documentation: https://docs.openssl.org/3.0/man1/openssl-verify/
- OpenSSL s_client documentation: https://docs.openssl.org/3.0/man1/openssl-s_client/
- OpenSSL s_server documentation: https://docs.openssl.org/3.0/man1/openssl-s_server/
- curl HTTPS certificate documentation: https://curl.se/docs/sslcerts.html
- RFC 5280: https://www.rfc-editor.org/rfc/rfc5280
- RFC 6125: https://www.rfc-editor.org/rfc/rfc6125
- RFC 8446, The Transport Layer Security Protocol Version 1.3: https://www.rfc-editor.org/rfc/rfc8446

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

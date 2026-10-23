# Reading: TLS Certificates and HTTPS

**Module:** Edge Access & VPN
**Activity type:** Reading (Learn)
**Objective:** Explain the distinct roles of a private key, public key, certificate signing request, certificate, and certificate authority

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

## Required reading

- OpenSSL documentation: https://docs.openssl.org/3.0/man1/openssl-req/
- OpenSSL certificate command documentation: https://docs.openssl.org/3.0/man1/openssl-x509/
- OpenSSL TLS server documentation: https://docs.openssl.org/3.0/man1/openssl-s_server/
- RFC 5280, Internet X.509 Public Key Infrastructure Certificate and CRL Profile: https://www.rfc-editor.org/rfc/rfc5280
- RFC 6125, Service Identity in TLS: https://www.rfc-editor.org/rfc/rfc6125

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

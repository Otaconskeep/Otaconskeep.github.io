# Homework: TLS Certificates and HTTPS

**Module:** Edge Access & VPN
**Activity type:** Homework / independent application
**Objective:** Explain the distinct roles of a private key, public key, certificate signing request, certificate, and certificate authority

## Requirements

### tasks
Draw the lab trust chain and label the trust anchor, issuer, leaf certificate, public keys, and private keys.
Inspect server.crt and list every condition a client should check before accepting it for https://localhost:8443/.
Explain what error should occur if a client connects using a DNS name not present in the Subject Alternative Name extension.
Compare the security consequences of losing server.key with those of losing ca.key.
Write a certificate-renewal plan that replaces a leaf certificate before expiration without changing the trusted CA or exposing private keys.
Explain why placing the lab CA into a global trust store would expand risk beyond this single endpoint.

### submission
Provide a short trust-chain diagram, certificate inspection notes, and written answers. Do not submit private-key contents.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

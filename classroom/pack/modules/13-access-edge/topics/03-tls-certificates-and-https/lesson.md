# Lesson 13.03: TLS Certificates and HTTPS

**Module:** Edge Access & VPN
**Activity type:** Lesson (Orient → Recall → Learn → Explain → Reflect)
**Learning objective:** Explain the distinct roles of a private key, public key, certificate signing request, certificate, and certificate authority
**Bloom level:** Understand / Apply
**Last reviewed:** 2025-02-20

## Learning objective

Explain the distinct roles of a private key, public key, certificate signing request, certificate, and certificate authority

## Why this matters

Teach how TLS certificates establish server identity, how certificate authorities and trust stores participate in verification, how hostname validation uses Subject Alternative Names, and how to operate and verify a small HTTPS service using OpenSSL and curl.

## Learn

Complete the module reading first:

- [Reading](./reading.md)

## Feynman teach-back (required)

### prompt
Explain HTTPS to a new administrator without using the phrase 'it is secure because it has a lock icon.'

### model_explanation
The server owns a private key and presents a certificate containing the matching public key and approved service names. A certificate authority signs that certificate. The client trusts selected CA certificates, verifies the issuer chain and validity rules, and confirms that the requested hostname appears in the certificate. The server proves possession of its private key during the handshake, and both sides derive temporary session keys used to encrypt and authenticate application traffic. If the CA is not trusted or the name does not match, encryption alone does not establish that the client reached the intended server.

### self_check
Can you explain why the server certificate may be public but the server private key must remain secret?
Can you distinguish chain trust from hostname validation?
Can you explain why explicitly supplying ca.crt changes the result without changing the server certificate?
Can you explain why localhost was forced to 127.0.0.1 while still remaining the URL hostname?

## Reflection

1. What did I learn?
2. What did I struggle with?
3. How does this connect to earlier classes?

## Topic path (do in order)

| Step | Activity | Purpose |
|---|---|---|
| 1 | [Reading](./reading.md) | Learn |
| 2 | This lesson (Feynman) | Explain |
| 3 | [Lab](./lab.md) | Practice |
| 4 | [Homework](./homework.md) | Apply |
| 5 | [Quiz](./quiz.md) | Test |

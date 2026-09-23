# Quiz — Docker Images, Tags, Registries, and Provenance

**Module:** Module 8 — Docker, Storage & Permissions
**Activity type:** Quiz (Test)

## Knowledge check

1. Can a tag be reassigned?  
2. What does a digest identify?  
3. Why might one tag resolve differently on amd64 and arm64?  
4. What is the difference between an image ID and a registry digest?  
5. Name three useful provenance artifacts.  
6. Why is `latest` a poor production change-control policy?

## Answer key

1. Yes; tags are mutable registry references.  
2. Content referenced by a cryptographic manifest hash.  
3. A multi-platform index can select different platform manifests.  
4. The local image ID identifies local image configuration/content; RepoDigest records registry manifest identity.  
5. Examples: source URL, SBOM, signature, attestation, build record, scan report, OCI labels, approved digest.  
6. It hides which version/content will resolve and makes rollback ambiguous.

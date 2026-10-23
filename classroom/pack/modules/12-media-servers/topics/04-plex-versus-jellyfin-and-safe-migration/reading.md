# Reading: Plex versus Jellyfin and Safe Migration

**Module:** Requests & Media Servers
**Activity type:** Reading (Learn)
**Objective:** Compare Plex and Jellyfin across licensing, account dependencies, remote access, plug-ins, client coverage, administration, and migration implications.

## Vocabulary

| Term | Meaning |
|---|---|
| Media library | The video, audio, image, subtitle, and related content files consumed by a media server. These files should normally be separated from application configuration and databases. |
| Application state | Mutable server data such as configuration, database files, metadata, users, watch history, artwork caches, and plug-in state. |
| Control plane | The configuration and state that determine how a service behaves, as distinct from the media files being served. |
| Cutover | The controlled point at which clients or routing begin using the replacement service. |
| Rollback | A planned restoration of the previous service and its validated state after a failed or rejected cutover. |
| Checksum manifest | A file containing cryptographic hashes and paths used to detect missing or changed files. |
| Restore test | Extraction of a backup into an isolated location followed by structural and checksum verification. |
| Least privilege | Granting a process only the access required for its task, such as permitting media reads while denying media modification. |
| Service identity | The operating-system account under which a service runs and whose permissions constrain that service. |
| Candidate state | Prepared replacement-service state that has passed validation but has not necessarily become authoritative. |

## Instruction

1. Begin with requirements, not brand loyalty. Plex and Jellyfin both index media, retrieve metadata, track playback, and serve clients, but their operating models differ.

2. Licensing: Plex is proprietary software with a mixture of free functions and optional Plex Pass features. Jellyfin is free and open-source software. A license difference does not automatically determine reliability or suitability; it affects auditability, feature access, support expectations, and long-term governance.

3. Accounts: Plex commonly integrates server ownership, user access, and discovery through Plex-hosted accounts. Some local-network behavior can continue under configured exceptions, but administrators must understand which workflows depend on Plex infrastructure. Jellyfin normally uses server-local users and authentication. That reduces reliance on a vendor account service but makes the homelab operator responsible for identity lifecycle, password policy, and safe exposure.

4. Remote access: Plex provides an integrated remote-access workflow and may use vendor-assisted discovery or relay behavior when direct connectivity is unavailable. Jellyfin operators generally design their own secure publication path, name resolution, TLS termination, and access policy. Direct exposure is not required for this lesson, and migration must not silently copy old trust assumptions into a new service.

5. Plug-ins and extensions: Plex retains a more restricted modern plug-in model than its historical ecosystem. Jellyfin supports server plug-ins, but each extension expands update, compatibility, and supply-chain risk. Inventory functionality instead of assuming that a plug-in with the same name or purpose will migrate.

6. Client coverage: Plex has broad official client availability across televisions, mobile devices, browsers, streaming appliances, and consoles. Jellyfin has clients for many common platforms, but availability and feature parity vary by device and application. Test every client type actually used in the household, including subtitle handling, codec negotiation, profiles, and accessibility needs.

7. Migration reality: media files are generally reusable, but Plex and Jellyfin configuration databases are not drop-in replacements for one another. Users, passwords, sharing rules, metadata choices, playlists, watch history, and plug-in behavior may require recreation, supported tooling, or documented mappings. Never point two applications at each other's mutable database directories.

8. Safe sequence: inventory the source, stop or quiesce writes in a real deployment, record versions, checksum state, create a backup, extract it into an isolated directory, verify checksums, prepare the candidate, validate clients, cut over, observe, and retain a rollback window. A backup is only a recovery hypothesis until extraction and verification succeed.

9. Lab command details: install -d creates directories rather than copying a file; its -m option sets the requested mode at creation time. find with -type f selects regular files, while -print0 emits NUL-delimited paths so spaces and unusual characters are handled safely. sort -z preserves those NUL delimiters. xargs -0 passes the paths safely to sha256sum. sha256sum -c reads a manifest, recalculates each listed hash, and returns a nonzero status if a file is absent or changed. tar -C changes archive context without changing the shell's working directory; -c creates, -x extracts, -t lists, -z enables gzip, and -f names the archive.

10. The lab uses a simulated service marker instead of starting real Plex or Jellyfin daemons. The files, archive, extraction, permissions, checksums, state translation, cutover, corruption, and recovery are real, but all writes remain beneath /opt/lab-classroom/class59/.

## Architecture

### source_service
A fixture Plex control plane stored at /opt/lab-classroom/class59/state/plex.

### candidate_service
A fixture Jellyfin control plane stored at /opt/lab-classroom/class59/state/jellyfin.

### shared_media
A separate media fixture at /opt/lab-classroom/class59/media/library. It is readable by the unprivileged nobody identity and not writable by that identity.

### backup_path
/opt/lab-classroom/class59/backups/plex-pre-migration.tgz

### restore_test_path
/opt/lab-classroom/class59/restore-check

### post_rollback_extract_path
/opt/lab-classroom/class59/verification-extract

### manifests
SHA-256 manifests are stored under /opt/lab-classroom/class59/manifests.

### cutover_model
The file cutover/active-service represents the selected service. cutover/active-service.before is an immutable migration record of the original Plex selection.

### data_flow
Clients conceptually select the service named by cutover/active-service.
Plex and Jellyfin have separate mutable control-plane directories.
Both services reference the same media path rather than copying media into application state.
The Plex archive is extracted and verified before cutover.
Rollback replaces damaged Plex fixture state with the previously verified extraction while retaining the damaged directory.

## Required reading

- Plex Support: Back Up Plex Media Server Data.
- Plex Support: Move an Install to Another System.
- Jellyfin Documentation: Backup and Restore.
- Jellyfin Documentation: Migrating.
- GNU Coreutils manual sections for install, sha256sum, stat, and mv.
- GNU tar manual sections covering archive listing, extraction, and directory selection.

## References

- Plex Support, Back Up Plex Media Server Data: https://support.plex.tv/articles/201539237-backing-up-plex-media-server-data/
- Plex Support, Move an Install to Another System: https://support.plex.tv/articles/201370363-move-an-install-to-another-system/
- Plex Support, Remote Access: https://support.plex.tv/articles/200289506-remote-access/
- Plex Legal, Terms of Service: https://www.plex.tv/about/privacy-legal/plex-terms-of-service/
- Jellyfin Documentation, Backup and Restore: https://jellyfin.org/docs/general/administration/backup-and-restore/
- Jellyfin Documentation, Migrating: https://jellyfin.org/docs/general/administration/migrate/
- Jellyfin Documentation, Networking: https://jellyfin.org/docs/general/networking/
- Jellyfin Documentation, Clients: https://jellyfin.org/downloads/clients/
- Jellyfin Project, Software Freedom: https://jellyfin.org/
- GNU Coreutils Manual, sha2 utilities: https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html
- GNU Coreutils Manual, install invocation: https://www.gnu.org/software/coreutils/manual/html_node/install-invocation.html
- GNU Findutils Manual: https://www.gnu.org/software/findutils/manual/html_mono/find.html
- GNU tar Manual: https://www.gnu.org/software/tar/manual/

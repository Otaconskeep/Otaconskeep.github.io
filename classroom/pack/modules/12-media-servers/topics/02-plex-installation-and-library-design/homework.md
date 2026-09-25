# Homework: Plex Installation and Library Design

**Module:** Requests & Media Servers
**Activity type:** Homework / independent application
**Objective:** Explain the roles of Plex configuration, transcode, and media storage.

## Requirements

### assignment
Extend the staged design without starting Plex.

### tasks
Add a read-only /media/home-videos bind mount rooted at /opt/lab-classroom/class57/media/home-videos.
Create three empty sample files demonstrating a consistent personal-video naming convention.
Write /opt/lab-classroom/class57/docs/backup-plan.txt describing configuration backup timing, retention, restore testing, and why transcode data is excluded.
Write /opt/lab-classroom/class57/docs/identity-plan.txt documenting the intended numeric UID, numeric GID, and required access for each mounted directory.
Update the validator so it confirms that all four media mounts are read-only and that no credential-like key appears in compose.yaml.

### submission_criteria
All submitted files remain under /opt/lab-classroom/class57/.
The design keeps media mounts read-only.
The backup plan distinguishes persistent application state from disposable cache data.
The identity plan uses numeric identities rather than relying only on account names.
No real credential, token, private media, or personally identifying filename is included.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

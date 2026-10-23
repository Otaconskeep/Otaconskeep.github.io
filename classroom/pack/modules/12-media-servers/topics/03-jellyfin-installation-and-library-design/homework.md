# Homework: Jellyfin Installation and Library Design

**Module:** Requests & Media Servers
**Activity type:** Homework / independent application
**Objective:** Describe the roles of Jellyfin configuration, cache, metadata, and media storage

## Requirements

### assignment
Create a library design document at /opt/lab-classroom/class58/library-plan.txt for a hypothetical household with movies, episodic shows, music, family videos, and children's content.

### requirements
List the proposed directory tree beneath the class58 media directory.
Provide two correctly formatted movie examples and two episodic-show examples.
State which libraries may use public metadata providers and which should not.
Describe read-only versus writable storage requirements.
Classify config, cache, metadata, and source media by backup priority.
Describe how administrator and playback accounts should be separated.
Document how future storage expansion could preserve stable container paths.

### success_criteria
The plan separates content types, uses predictable names, protects source media, distinguishes backups from cache regeneration, and does not require moving any lab artifact outside /opt/lab-classroom/class58/.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

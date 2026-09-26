# Homework: Jellyseerr or Overseerr Request Management

**Module:** Requests & Media Servers
**Activity type:** Homework / independent application
**Objective:** Explain the role of Jellyseerr or Overseerr between users, a media server, and download automation

## Requirements

### submission_location
/opt/lab-classroom/class56/homework.json

### instructions
Create a JSON document at the submission location. Do not include real hostnames, public addresses, usernames, API keys, tokens, webhook URLs, or other credentials. The document must parse as JSON and contain every required key shown in the schema.

### schema
### type
object

### required
class_id
chosen_platform
default_role
approval_mode
weekly_request_limit
tmdb_secret_source
user_sync_review
availability_explanation
compose_exposure
incident_response

### properties
### class_id
Integer equal to 56

### chosen_platform
String equal to jellyseerr or overseerr

### default_role
String equal to requester

### approval_mode
String equal to manual

### weekly_request_limit
Integer from 1 through 10

### tmdb_secret_source
String describing a supported environment or secret-manager source without including a credential

### user_sync_review
Array of at least three strings describing post-sync account checks

### availability_explanation
String explaining why availability synchronization is not a library scan

### compose_exposure
String describing the loopback binding and intended secure access path

### incident_response
Array of at least three ordered strings describing response to a leaked request-manager credential

### example_document
### class_id
56

### chosen_platform
jellyseerr

### default_role
requester

### approval_mode
manual

### weekly_request_limit
5

### tmdb_secret_source
An environment variable injected by the deployment secret mechanism

### user_sync_review
Confirm each imported identity belongs to a current media-server user
Confirm requester is the default role
Remove administrative or approval rights that lack an operational justification

### availability_explanation
Availability synchronization reads what the media server already knows; a library scan makes the media server inspect its configured storage paths.

### compose_exposure
The application listens through a host port bound to 127.0.0.1 and remote access is provided only through an authenticated TLS endpoint.

### incident_response
Revoke or rotate the exposed credential at its issuing service
Update the protected deployment secret and restart only the affected integration as required
Review access and application logs for unauthorized use

### grading_criteria
The file is valid JSON and contains all required keys.
class_id is 56 and chosen_platform is jellyseerr or overseerr.
The default role is requester and approval mode is manual.
The weekly limit is an integer from 1 through 10.
The TMDB secret source describes protected injection without disclosing a credential.
The user synchronization review contains at least three meaningful checks.
The availability explanation clearly separates synchronization from scanning.
The exposure statement includes loopback binding and a secure remote-access path.
The incident response includes revocation or rotation, protected redeployment, and log review.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

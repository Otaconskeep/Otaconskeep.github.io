# Reading: Bazarr and Subtitle Automation

**Module:** Requests & Media Servers
**Activity type:** Reading (Learn)
**Objective:** Describe Bazarr's role in a media automation architecture

## Vocabulary

| Term | Meaning |
|---|---|
| Bazarr | A companion application for Sonarr and Radarr that searches for, downloads, upgrades, and manages subtitle files. |
| Language profile | A policy describing which subtitle languages and variants are wanted for a movie or series. |
| Forced subtitle | A subtitle track intended mainly for foreign-language or otherwise untranslated dialogue within predominantly different-language content. |
| Hearing-impaired subtitle | A subtitle variant that can include speaker labels, sound descriptions, and other accessibility cues. |
| Provider | An external subtitle source queried by Bazarr, often requiring credentials, rate-limit awareness, or account-specific configuration. |
| Subtitle score | Bazarr's assessment of how well a candidate subtitle matches the requested title, release, language, episode, and other preferences. |
| Path mapping | A translation used when Bazarr and a media manager refer to the same files through different filesystem paths. |
| Embedded subtitle | A subtitle stream stored inside a media container rather than as a separate sidecar file. |
| Sidecar subtitle | A separate subtitle file, such as an SRT file, stored alongside its corresponding media file. |
| API key | A secret token used by Bazarr to authenticate requests to Sonarr or Radarr. |

## Instruction

Bazarr does not replace Sonarr or Radarr. Sonarr remains responsible for series and episode records, while Radarr remains responsible for movie records. Bazarr connects to their APIs, learns what titles are monitored, receives the file paths those applications know about, and then evaluates subtitle requirements against configured language profiles. It also needs filesystem access to the same media files. These are two separate dependencies: an API connection supplies metadata and monitoring state, while a media mount supplies access to inspect media and write sidecar subtitles.

Path consistency is one of the most important design concerns. If Radarr reports a movie at /movies/Example/Example.mkv, Bazarr must be able to find that file at the reported path or translate it with an intentional path mapping. Using matching container paths across the media stack is generally easier to reason about than adding translations. A mapping can solve a legitimate difference, but it can also hide a poor storage design and make troubleshooting harder.

Bazarr normally writes subtitle files next to media, so a read-only media mount supports inspection but prevents complete automation. Production write access should therefore be narrow rather than broad: run Bazarr as a dedicated unprivileged identity and grant that identity only the permissions required for relevant movie and series directories. Do not grant access to unrelated storage. Existing media ownership and group strategy should be understood before enabling writes.

Language profiles express intent. A household may require one language for all titles, prefer another language when available, request forced subtitles, or choose hearing-impaired variants. Profiles should be tested on a small library subset before broad assignment. Provider limits and authentication also matter. Aggressive searches can cause throttling or account restrictions, and a poorly matched result may have incorrect timing or release characteristics. Bazarr's scoring, minimum score, upgrade behavior, and provider selection should be treated as quality controls rather than bypassed merely to obtain any result.

The safest rollout is staged. First validate networking, paths, ownership, and API reachability. Next connect Sonarr and Radarr and confirm that their libraries appear without launching a broad search. Then configure one provider and one language profile. Test a small number of known titles, inspect the resulting filenames and timing, and only then enable scheduled searches or upgrades. Back up Bazarr's configuration before major profile, provider, or path changes. This class stages and validates a deployment definition but deliberately does not start a container, pull an image, contact subtitle providers, or modify an existing media library.

## Architecture

### components
### name
Bazarr

### role
Evaluates subtitle requirements, queries configured providers, and manages sidecar subtitle files.
### name
Sonarr

### role
Supplies series, episode, monitoring, and media-file metadata through its API.
### name
Radarr

### role
Supplies movie, monitoring, and media-file metadata through its API.
### name
Media storage

### role
Contains movie and series files and, when authorized, the subtitle sidecar files written by Bazarr.
### name
Subtitle providers

### role
Supply subtitle candidates subject to provider credentials, policies, availability, and rate limits.
### name
Administrator browser

### role
Accesses the Bazarr web interface through a trusted local path or an authenticated reverse proxy.

### data_flows
Bazarr uses a Sonarr API key to retrieve monitored series, episodes, and file paths.
Bazarr uses a Radarr API key to retrieve monitored movies and file paths.
Bazarr reads media metadata and writes approved sidecar subtitles through mounted media paths.
Bazarr queries explicitly enabled subtitle providers and records search and download outcomes.
The administrator configures providers, language profiles, scoring, and media-manager connections through the web interface.

### lab_boundary
All files created or modified by this lab remain under /opt/lab-classroom/class61/. The lab does not start Bazarr, create containers, pull images, alter an existing media library, or contact external subtitle services.

## Required reading

- Bazarr documentation: https://wiki.bazarr.media/
- Bazarr setup documentation: https://wiki.bazarr.media/Getting-Started/Setup-Guide/
- Docker Compose file reference: https://docs.docker.com/reference/compose-file/
- Sonarr FAQ and documentation: https://wiki.servarr.com/sonarr
- Radarr FAQ and documentation: https://wiki.servarr.com/radarr

## References

- Bazarr documentation: https://wiki.bazarr.media/
- Bazarr setup guide: https://wiki.bazarr.media/Getting-Started/Setup-Guide/
- Bazarr troubleshooting documentation: https://wiki.bazarr.media/Troubleshooting/
- LinuxServer.io Bazarr image documentation: https://docs.linuxserver.io/images/docker-bazarr/
- Docker Compose file reference: https://docs.docker.com/reference/compose-file/
- Docker bind mount documentation: https://docs.docker.com/engine/storage/bind-mounts/
- Sonarr documentation: https://wiki.servarr.com/sonarr
- Radarr documentation: https://wiki.servarr.com/radarr

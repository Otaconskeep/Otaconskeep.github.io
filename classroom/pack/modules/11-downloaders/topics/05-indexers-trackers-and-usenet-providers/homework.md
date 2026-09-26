# Homework: Indexers, Trackers, and Usenet Providers

**Module:** Download Clients & Indexers
**Activity type:** Homework / independent application
**Objective:** Differentiate a Usenet indexer, Usenet provider, torrent indexer, BitTorrent tracker, download client, and automation application.

## Requirements

### assignment
Design two architecture plans on paper or in a local text file under /opt/lab-classroom/class53/: one for an authorized Usenet workflow and one for an authorized BitTorrent workflow.

### requirements
Label discovery, metadata, transfer, staging, and import boundaries.
Identify which components require credentials.
State which links require encrypted transport.
Describe how secrets are withheld from logs and source control.
Provide one failure test for every boundary.
Explain why a successful indexer query does not prove that a transfer can complete.
Include a policy statement limiting use to authorized content.

### challenge
Extend evaluate.py with a client role for each protocol and require each indexer record to identify a compatible client. Keep every generated file inside /opt/lab-classroom/class53/ and use only synthetic values.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

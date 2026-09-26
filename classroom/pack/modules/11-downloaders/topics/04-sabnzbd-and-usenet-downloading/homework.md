# Homework: SABnzbd and Usenet Downloading

**Module:** Download Clients & Indexers
**Activity type:** Homework / independent application
**Objective:** Describe the roles of a Usenet provider, an indexer, an NZB file, and SABnzbd.

## Requirements

### assignment
Design a live deployment plan without entering real secrets or starting services. Extend the policy beneath /opt/lab-classroom/class52 with a fourth category, document the intended owner and shared group for each directory, specify a primary and lower-priority backup provider strategy, and describe how an authorized automation client would submit an NZB while receiving only the minimum API capability it needs.

### deliverables
A revised policy file stored beneath /opt/lab-classroom/class52/config.
A diagram or text flow showing indexer, automation client, SABnzbd, providers, incomplete storage, completed categories, and downstream import.
A permissions matrix listing the SABnzbd account, automation account, and downstream application account.
A threat analysis covering exposed management access, stolen API keys, malicious archives, path traversal, and post-processing scripts.
A short explanation of how the design respects legal access and provider terms.

### success_criteria
All paths remain beneath /opt/lab-classroom/class52 for the classroom exercise.
Incomplete and completed paths are distinct.
The management interface is not designed for direct exposure to an untrusted network.
No actual credential, API key, or provider account identifier appears in the deliverables.
The provider strategy explains TLS, connection limits, priorities, and the difference between retention and completion.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

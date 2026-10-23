# Homework: Local DNS and Friendly Service Names

**Module:** Edge Access & VPN
**Activity type:** Homework / independent application
**Objective:** Explain the roles of stub resolvers, recursive resolvers, authoritative data, and DNS caches.

## Requirements

Design a naming plan for at least five homelab services using home.arpa. Include the service purpose, chosen name, address family, owner, and expected change frequency.
Draw the query path from an application to a stub resolver, then to a recursive resolver, cache, and authoritative source.
Explain how you would provide two resilient DNS resolver addresses to LAN clients without creating a circular dependency.
Research the difference between A, AAAA, CNAME, and PTR records and provide one appropriate homelab use case for each.
Write a change procedure for moving dashboard.home.arpa to a new address while minimizing the impact of cached answers.
Document how you would determine whether a client is bypassing the intended local resolver.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz

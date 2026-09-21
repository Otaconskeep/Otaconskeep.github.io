# KeepRoute / OmniRoute Public Page Audit

**Product page:** KEEPROUTE 1.0, OtaconsKeep Stateful AI Orchestration 
**Public path:** `/keeproute/` 
**Audit time (UTC):** 2026-09-19T23:55:57Z 
**Publication recommendation:** **GO** (security/privacy leak scan PASS; installer claims honest)

## Files changed

| Path | Change |
|---|---|
| `keeproute/index.html` | New public product page |
| `keeproute/keeproute.css` | Page styles (diagrams, charts, beginner modal) |
| `keeproute/keeproute.js` | Subnav, charts, beginner mode, handoff pulse |
| `keeproute/OMNIROUTE_PUBLIC_PAGE_AUDIT.md` | This report |
| `index.html` | Top nav + home quickpick card |
| `assets/style.css` | Quickpick grid supports 4 cards |
| `otacon/index.html`, `ai9/index.html`, `faq/index.html`, `expansion/index.html`, `premium/index.html` | Top-level **KeepRoute** nav tab |
| `downloads/index.html` | Link to KeepRoute page |

No private evidence trees, mission JSON, or private lab filesystem paths were copied into the public site.

## Page URL / path

- Local preview: `http://127.0.0.1:8000/keeproute/` (from repo root via `python -m http.server`)
- Production: `https://otaconskeep-site.otaconskeep.workers.dev/keeproute/`

Top-level tab label: **KeepRoute**

## Content sections

1. Overview / hero (KEEPROUTE 1.0 identity, powered by OmniRoute)
2. Ten-second OmniRoute vs KeepRoute distinction
3. Where KeepRoute fits (OtaconsKeep → KeepRoute → OmniRoute → providers)
4. What it actually does (examples + handoff visual)
5. Why this design exists
6. What KeepRoute improved
7. Before/after + architecture SVG (conceptual)
8. KeepRoute vs stock OmniRoute capability table
9. Why it helps long-running agent work
10. Benchmarks (sanitized release results + methodology)
11. Security / privacy (verified vs NOT VERIFIED)
12. Pros & cons
13. Limitations (visible, including public-safe residuals)
14. Install (Easy path + **pending** KeepRoute packager honesty)
15. Release card
16. FAQ
17. “I don’t understand” beginner mode

## Benchmark sources (sanitized)

Published numbers are release-test observations only (sample sizes shown):

| Claim on page | Source class |
|---|---|
| 58 soak missions, 100% completion, 0 interventions | 1.0 promotion soak sample |
| 0 hard-invariant violations | Release soak + final sweep counters |
| 200/200 trivial→local (100/100 ×2), paid leak 0 | Final MOE-2 verification runs |
| 100/100 after large local model loaded | Post-load local-route verification |
| 2/2 host-reboot recovery | KeepRoute reboot tests |
| Final sweep 0 fails; post-release smoke PASS | Final regression + smoke |

**Not published:** raw evidence paths, mission IDs, LAN addresses, container names, filesystem locations, unredacted logs.

**Not claimed:** apples-to-apples performance % vs unmodified stock OmniRoute.

## Stock comparison sources

Upstream (public):

- https://github.com/diegosouzapw/OmniRoute
- OmniRoute `docs/ARCHITECTURE.md` (gateway, combos, fallback, usage/health)
- OmniRoute Resilience Guide (circuit breaker, cooldowns, model lockout)

KeepRoute column reflects OtaconsKeep orchestration capabilities verified in the 1.0 release campaign. Stock is described neutrally as the routing data plane.

## Security scan result

**PASS**

Primary scan: no matches for private RFC1918 ranges, private absolute filesystem roots, `.env`, private keys, bearer headers, high-entropy token patterns, or source maps under `keeproute/`.

Secondary review: educational mentions of “API keys / secrets” appear only as warnings (do not paste keys into the browser). No actual secrets shipped.

Pre-existing note (outside KeepRoute page): `downloads/index.html` historically mentions a local UI port in soft-update guidance, not introduced by this page.

### Security claims honesty

| Control | Public claim |
|---|---|
| No secrets in frontend | Claimed (verified for this page) |
| Server-side provider credentials (design) | Claimed as design intent |
| Private data-plane binding (design) | Claimed as design intent |
| Encryption of all mission state at rest | **NOT VERIFIED, not claimed** |
| Encrypted backups of all sensitive state | **NOT VERIFIED, not claimed** |
| TLS everywhere | Deployment-dependent, not overclaimed |

## Installation test result

| Item | Result |
|---|---|
| Dedicated KeepRoute one-click installer (OmniRoute + Mission Controller + Auto Guard + providers + smoke) | **NOT SHIPPED**, page marks **pending** |
| OtaconsKeep Lite Setup.bat (existing public installer) | Linked as today’s foundation path |
| Provider credential examples with real secrets | None (forbidden) |
| Advanced setup exposing lab topology | Not published |

Acceptance: installer honesty requirement met (no fabricated KeepRoute packager).

## Screenshots / assets created

- Inline SVG architecture diagram (conceptual)
- CSS before/after flows
- CSS bar charts (no external chart CDN)
- Animated handoff chip sequence (CSS/JS)
- Provider status “READY” mock (sanitized, fictional statuses)
- No live-lab screenshots (avoids IP/path/user leakage)

## Limitations disclosed

Full limitations section includes non-guarantees, handoff package boundaries, cost/outage reality, checkpoint≠backup, and public-safe residual operational notes (warm-up delay, cosmetic gateway health noise, intentional private data-plane binding).

## Remaining gaps

1. **KeepRoute one-click installer** not yet available, must ship before “Easy Install KeepRoute” can be unmarked pending.
2. **Encryption-at-rest / encrypted backups** not verified as product features, left NOT VERIFIED.
3. **Home quickpick** now has four cards; layout updated to 2×2 / 4-col responsive.
4. Site deploy/push not performed by this audit (working tree ready for operator commit/push).

## Acceptance checklist

| ID | Check | Status |
|---|---|---|
| A | Own top-level tab; mobile/desktop CSS | PASS |
| B | Beginner can learn what/why/install/Auto/failure | PASS |
| C | Stock comparison sourced; sample sizes shown; limitations visible | PASS |
| D | Install steps honest; pending features labeled | PASS |
| E | Leak scan PASS; no secrets; security claims match reality | PASS |
| F | Charts/diagrams/mobile readable | PASS |
| G | Links: OtaconsKeep download, Otacon guide, public OmniRoute GitHub; no admin/private links | PASS |

## Publication recommendation

**GO to publish** the `/keeproute/` page after normal site deploy.

Do **not** market a finished KeepRoute installer until it exists and is re-audited.

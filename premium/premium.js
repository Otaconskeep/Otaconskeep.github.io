/* Otaconskeep Premium, gate, licenses, member portal, unlock telemetry */
(function () {
 'use strict';

 var GATE_BUILD = '20260919d';

 // Discord webhook: every unlock posts license + fingerprint so Antonio can
 // see payment-linked codes being reused across machines/locations.
 // Paste a channel webhook URL here, commit, redeploy. Unlock works either way.
 var NOTIFY_WEBHOOK_URL = '';

 // License registry, source of truth for who paid / who is active.
 // Operator console (/premium/ops/) reads the same table.
 var LICENSES = {
 RAM36: {
 licenseId: 'OK-PREM-RAM36-001',
 displayName: 'Ram36',
 tier: 'early-access',
 status: 'active',
 seats: 1,
 issued: '2026-09-12',
 paymentRef: 'BMC, issued by hand',
 notes: 'Early supporter'
 },
 JOSHBLOCK: {
 licenseId: 'OK-PREM-BLOCK-001',
 displayName: 'Josh Block',
 tier: 'early-access',
 status: 'active',
 seats: 1,
 issued: '2026-09-16',
 paymentRef: 'BMC, issued by hand (friend)',
 notes: 'Rotated 2026-09-19; BLOCK alias kept for old bookmarks'
 },
 // Alias, old access name still unlocks the same seat
 BLOCK: {
 licenseId: 'OK-PREM-BLOCK-001',
 displayName: 'Josh Block',
 tier: 'early-access',
 status: 'active',
 seats: 1,
 issued: '2026-09-16',
 paymentRef: 'BMC, issued by hand (friend)',
 notes: 'Alias of JOSHBLOCK'
 },
 CRISTO: {
 licenseId: 'OK-PREM-CRISTO-001',
 displayName: 'Cristo',
 tier: 'early-access',
 status: 'active',
 seats: 1,
 issued: '2026-09-12',
 paymentRef: 'BMC, issued by hand',
 notes: 'Early supporter'
 }
 };

 // Credential hashes (SHA-256). Password hashed alone; PIN as "NAME:PIN".
 // JOSHBLOCK pw = IloveJohnnynXof2026; pin = 1776 (NAME:PIN)
 // BLOCK also accepts legacy usmc + new password; pin 1776 under BLOCK:1776
 var USERS = {
 RAM36: {
 pwHashes: ['2428a5260348e9ed5340ca09471e085f5415f5dbe1d106408b5d300fec28cd3a'],
 pinHash: 'cc65ec6dbf2e389a5bb42f42a78d546040af789a9b875d202ea4d4ff295bf5f2'
 },
 JOSHBLOCK: {
 pwHashes: [
 'd76a0868c089cd1a7133644b39d3282354ddf17ad34015049a22fc5949231060', // IloveJohnnynXof2026
 '91dbdd4a1c1bbe3af464f2618161e115977d02a5d49cc0e23313937c31580143' // legacy usmc
 ],
 pinHash: 'b1a7667b9aff621ec1f48d05c4ae19266282a384468e5b1c41ae98707a95eeff' // JOSHBLOCK:1776
 },
 BLOCK: {
 pwHashes: [
 'd76a0868c089cd1a7133644b39d3282354ddf17ad34015049a22fc5949231060', // IloveJohnnynXof2026
 '91dbdd4a1c1bbe3af464f2618161e115977d02a5d49cc0e23313937c31580143', // usmc
 '1366b2c27302a5ecbc7176daf875dee60e5cd8d1cf779231c9d48796c2677696' // prior issued
 ],
 pinHash: '4aa28222afbc5df797bc645cc4e5ed71d733c34676a0f2a24dfc768a905fa391' // BLOCK:1776
 },
 CRISTO: {
 pwHashes: ['101ea620e95097064943b518e9456392523a063e3fee1a87fab3679c17017e30'],
 pinHash: 'e888e0ff427cc49d4facf2182f713e523b5092c01e34e63a2e1c7e328daf90df'
 }
 };

 // Active projects / member news (edit this list when shipping updates).
 var MEMBER_NEWS = [
 {
 date: '2026-09-17',
 tag: 'Portal',
 title: 'Premium Member HQ is live',
 body: 'License cards, install placeholders, member news, and a written sharing protocol. Operator desk at /premium/ops/ for Antonio to check seats and payment refs.'
 },
 {
 date: '2026-09-16',
 tag: 'Expansion',
 title: 'Foundation layer installable today',
 body: 'Schema, relationship formulas, motion manifests, and the five-agent default roster install with one command after Lite. Dashboard / Codec / War Room still in build.'
 },
 {
 date: '2026-09-16',
 tag: 'RC1',
 {
 title: 'Otacon v1.1 — Keep-parity Aria behavior',
 body: 'Public roster ships work-first delivery, anti-greeting scrub, and layered learning. Soft-update with OtaconsKeep-Setup.bat. GitHub: otacons-ai-ecosystem releases/tag/v1.1.',
 date: '2026-09-22'
},
 title: 'Keep Expansion RC1 frozen for qualification',
 body: 'Protected artifact path under test. Backup/purge and Windows UAT still block a public 1.0 GO, early access stays foundation + Discord priority.'
 },
 {
 date: '2026-09-15',
 tag: 'Core',
 title: 'Otaconskeep Lite one-click Setup',
 body: 'Windows Setup BAT + Linux curl path remain the free foundation Premium installs on top of.'
 }
 ];

 window.OtaconsPremium = {
 GATE_BUILD: GATE_BUILD,
 NOTIFY_WEBHOOK_URL: NOTIFY_WEBHOOK_URL,
 LICENSES: LICENSES,
 USERS: USERS,
 MEMBER_NEWS: MEMBER_NEWS
 };
})();

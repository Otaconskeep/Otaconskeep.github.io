/**
 * OtaconsKeep product explainers, dual-mode "What is it?" system.
 * Data: /data/products/explainers.json
 */
(function () {
 'use strict';

 var DATA_URL = '/data/products/explainers.json';
 var MODE_KEY = 'ok_explainer_mode';
 var catalog = null;
 var openProductId = null;
 var lastFocus = null;
 var focusablesSel = 'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])';

 function $(sel, root) { return (root || document).querySelector(sel); }
 function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

 function esc(s) {
 return String(s == null ? '' : s)
 .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
 .replace(/"/g, '&quot;');
 }

 function getMode() {
 try {
 var m = sessionStorage.getItem(MODE_KEY);
 if (m === 'technical' || m === 'quick') return m;
 } catch (e) {}
 return 'quick';
 }

 function setMode(mode) {
 try { sessionStorage.setItem(MODE_KEY, mode); } catch (e) {}
 }

 /* ---- SVG icons ---- */
 var ICONS = {
 core: '<svg class="qp-icon px-icon" viewBox="0 0 48 48" aria-hidden="true"><rect x="8" y="8" width="32" height="32" rx="3" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="24" cy="24" r="6" fill="none" stroke="currentColor" stroke-width="2"/><path d="M24 8v6M24 34v6M8 24h6M34 24h6" stroke="currentColor" stroke-width="2"/></svg>',
 colorizer: '<svg class="qp-icon px-icon" viewBox="0 0 48 48" aria-hidden="true"><rect x="6" y="10" width="22" height="28" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M28 18h12v20H18" fill="none" stroke="currentColor" stroke-width="2" opacity=".55"/><path d="M10 20h10M10 26h14M10 32h8" stroke="currentColor" stroke-width="2"/><circle cx="36" cy="14" r="5" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
 constellation: '<svg class="qp-icon px-icon" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="10" cy="34" r="3.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="24" cy="36" r="3.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="38" cy="34" r="3.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="38" cy="20" r="3.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M24 16v16M24 12l14 8M24 12L10 34M24 36l14-2" stroke="currentColor" stroke-width="1.5" opacity=".7"/></svg>',
 desk: '<svg class="qp-icon px-icon" viewBox="0 0 48 48" aria-hidden="true"><rect x="6" y="12" width="36" height="22" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M14 34v6M34 34v6M10 40h28" stroke="currentColor" stroke-width="2"/><path d="M12 18h10M12 23h16M12 28h8" stroke="currentColor" stroke-width="1.8"/></svg>',
 route: '<svg class="qp-icon px-icon" viewBox="0 0 48 48" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="36" cy="36" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M16 12h8c6 0 6 12 0 12h-4c-6 0-6 12 0 12h12" fill="none" stroke="currentColor" stroke-width="2"/><path d="M32 36h4" stroke="currentColor" stroke-width="2"/></svg>'
 };

 /* ---- Diagram builders ---- */
 function node(x, y, w, h, label, sub) {
 var t = '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="3" fill="#121926" stroke="#39e6c8" stroke-width="1.2"/>';
 t += '<text x="' + (x + w / 2) + '" y="' + (y + (sub ? h / 2 - 2 : h / 2 + 4)) + '" text-anchor="middle" fill="#e4edf5" font-size="11" font-family="Figtree,sans-serif">' + esc(label) + '</text>';
 if (sub) t += '<text x="' + (x + w / 2) + '" y="' + (y + h / 2 + 12) + '" text-anchor="middle" fill="#8ea0b6" font-size="9" font-family="JetBrains Mono,monospace">' + esc(sub) + '</text>';
 return t;
 }

 function arrow(x1, y1, x2, y2) {
 return '<path d="M' + x1 + ' ' + y1 + ' L' + x2 + ' ' + y2 + '" stroke="#2d3e56" stroke-width="1.5" marker-end="url(#pxArrow)"/>';
 }

 function svgWrap(inner, vb, caption) {
 return '<div class="px-diagram" role="img" aria-label="' + esc(caption) + '">' +
 '<svg viewBox="' + vb + '" xmlns="http://www.w3.org/2000/svg">' +
 '<defs><marker id="pxArrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#39e6c8"/></marker></defs>' +
 inner + '</svg><p class="caption">' + esc(caption) + '</p></div>';
 }

 var DIAGRAMS = {
 'flow-lite': function () {
 return svgWrap(
 node(170, 8, 100, 36, 'You') + arrow(220, 44, 220, 58) +
 node(140, 58, 160, 36, 'OtaconsKeep') + arrow(220, 94, 220, 108) +
 node(130, 108, 180, 40, 'AI agent', 'memory + tools') + arrow(220, 148, 220, 162) +
 node(140, 162, 160, 36, 'Result to you') + arrow(220, 198, 220, 212) +
 node(120, 212, 200, 36, 'Useful state kept'),
 '0 0 440 260',
 'You talk to OtaconsKeep; an agent uses memory and tools; useful state can persist.'
 );
 },
 'arch-lite': function () {
 return svgWrap(
 node(160, 4, 120, 32, 'User') + arrow(220, 36, 220, 48) +
 node(140, 48, 160, 32, 'OtaconsKeep UI') + arrow(220, 80, 220, 92) +
 node(110, 92, 220, 36, 'Core API / Agent Runtime') + arrow(220, 128, 220, 140) +
 node(100, 140, 240, 36, 'Model Runtime / Router') +
 arrow(140, 176, 80, 198) + arrow(220, 176, 220, 198) + arrow(300, 176, 360, 198) +
 node(20, 198, 100, 40, 'Memory') + node(170, 198, 100, 40, 'Tools') + node(320, 198, 110, 40, 'Integrations') +
 arrow(220, 238, 220, 250) + node(130, 250, 180, 32, 'Persistent State'),
 '0 0 440 292',
 'Lite architecture: UI → runtime → router → memory/tools/integrations → local state.'
 );
 },
 'flow-ai9': function () {
 return svgWrap(
 node(20, 40, 90, 48, 'B&W manga') + arrow(110, 64, 130, 64) +
 node(130, 40, 90, 48, 'Firefox') + arrow(220, 64, 240, 64) +
 node(240, 40, 90, 48, 'Your GPU') + arrow(330, 64, 350, 64) +
 node(350, 40, 90, 48, 'Color out'),
 '0 0 460 130',
 'Black-and-white page → Firefox → local GPU colorization → color image.'
 );
 },
 'arch-ai9': function () {
 return svgWrap(
 node(160, 8, 120, 32, 'Firefox') + arrow(220, 40, 220, 52) +
 node(140, 52, 160, 32, 'AI9 Local API') + arrow(220, 84, 220, 96) +
 node(130, 96, 180, 32, 'Preprocess') + arrow(220, 128, 220, 140) +
 node(130, 140, 180, 36, 'GPU inference') + arrow(220, 176, 220, 188) +
 node(130, 188, 180, 32, 'Postprocess') + arrow(220, 220, 220, 232) +
 node(140, 232, 160, 32, 'Firefox'),
 '0 0 440 276',
 'AI9 request lifecycle stays on your machine.'
 );
 },
 'flow-expansion': function () {
 return svgWrap(
 node(170, 4, 100, 30, 'You') + arrow(220, 34, 220, 46) +
 node(140, 46, 160, 30, 'OtaconsKeep') + arrow(220, 76, 220, 88) +
 node(130, 88, 180, 30, 'Agent team') +
 node(10, 140, 78, 50, 'Aria', 'coord') +
 node(96, 140, 78, 50, 'Vector', 'systems') +
 node(182, 140, 78, 50, 'Ledger', 'data') +
 node(268, 140, 78, 50, 'Muse', 'creative') +
 node(354, 140, 78, 50, 'Sentry', 'security') +
 arrow(160, 118, 50, 140) + arrow(190, 118, 135, 140) + arrow(220, 118, 220, 140) +
 arrow(250, 118, 305, 140) + arrow(280, 118, 390, 140),
 '0 0 440 210',
 'You → OtaconsKeep → specialized agents with different jobs.'
 );
 },
 'arch-expansion': function () {
 return svgWrap(
 node(140, 4, 160, 30, 'Deck / Codec UI') + arrow(220, 34, 220, 46) +
 node(110, 46, 220, 36, 'Multi-agent runtime') + arrow(220, 82, 220, 94) +
 node(40, 94, 150, 44, 'Identity + personality') + node(230, 94, 170, 44, 'Relationships + emotion') +
 arrow(220, 138, 220, 150) +
 node(100, 150, 240, 36, 'Model router / tools') + arrow(220, 186, 220, 198) +
 node(110, 198, 220, 36, 'Dossiers / journals / memory'),
 '0 0 440 246',
 'Expansion stacks roster identity and behavioral state on Core.'
 );
 },
 'flow-keepdesk': function () {
 return svgWrap(
 node(170, 4, 100, 30, 'You') + arrow(220, 34, 220, 46) +
 node(140, 46, 160, 32, 'Keep Desk') +
 node(40, 100, 90, 36, 'Agent A') + node(140, 100, 90, 36, 'Agent B') +
 node(240, 100, 90, 36, 'Agent C') + node(340, 100, 90, 36, 'Agent D') +
 arrow(180, 78, 85, 100) + arrow(210, 78, 185, 100) + arrow(230, 78, 285, 100) + arrow(260, 78, 385, 100) +
 node(80, 160, 280, 40, 'Shared: memory · tasks · tools · local models'),
 '0 0 450 220',
 'One desk interface for named teammates sharing local resources.'
 );
 },
 'arch-keepdesk': function () {
 return svgWrap(
 node(160, 4, 120, 28, 'User') + arrow(220, 32, 220, 44) +
 node(140, 44, 160, 28, 'Keep Desk UI') + arrow(220, 72, 220, 84) +
 node(100, 84, 240, 32, 'Command / conversation') + arrow(220, 116, 220, 128) +
 node(130, 128, 180, 32, 'Agent runtime') + arrow(220, 160, 220, 172) +
 node(130, 172, 180, 32, 'Local model') + arrow(300, 188, 360, 210) +
 node(320, 210, 110, 40, 'Tools / tasks'),
 '0 0 440 262',
 'Keep Desk UI sits above agent runtime and local models.'
 );
 },
 'flow-keeproute': function () {
 return svgWrap(
 node(20, 20, 80, 36, 'Task') + arrow(100, 38, 120, 38) +
 node(120, 20, 90, 36, 'Model A') + arrow(210, 38, 230, 38) +
 node(230, 20, 100, 36, 'Limit / fail') +
 node(230, 80, 100, 36, 'Checkpoint') + arrow(280, 56, 280, 80) +
 arrow(330, 98, 350, 98) +
 node(350, 80, 90, 36, 'KeepRoute') + arrow(440, 98, 460, 98) +
 node(460, 80, 90, 36, 'Model B') + arrow(505, 116, 505, 140) +
 node(450, 140, 110, 36, 'Continue'),
 '0 0 580 190',
 'Instead of stopping, checkpoint → KeepRoute → continue on Model B.'
 );
 },
 'arch-keeproute': function () {
 return svgWrap(
 node(130, 4, 180, 30, 'Coding tool / agent') + arrow(220, 34, 220, 46) +
 node(100, 46, 240, 36, 'KeepRoute') +
 node(20, 100, 90, 40, 'Mission') + node(120, 100, 90, 40, 'Checkpoints') +
 node(220, 100, 90, 40, 'Recovery') + node(320, 100, 100, 40, 'Handoff') +
 arrow(220, 140, 220, 152) +
 node(120, 152, 200, 32, 'OmniRoute') + arrow(220, 184, 220, 196) +
 node(90, 196, 260, 36, 'Models / providers'),
 '0 0 440 244',
 'KeepRoute owns mission state; OmniRoute routes to providers.'
 );
 },
 'family': function () {
 var caption = 'Lite is the foundation; Expansion, Keep Desk, and KeepRoute build around it. AI9 is family-adjacent and does not require Lite Core.';
 var svg =
 '<svg viewBox="0 0 440 190" xmlns="http://www.w3.org/2000/svg">' +
 '<defs><marker id="pxArrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#39e6c8"/></marker></defs>' +
 node(130, 8, 180, 40, 'OtaconsKeep Lite', 'Core foundation') +
 arrow(160, 48, 75, 78) + arrow(220, 48, 220, 78) + arrow(280, 48, 365, 78) +
 node(20, 78, 110, 44, 'Expansion', 'multi-agent') +
 node(165, 78, 110, 44, 'Keep Desk', 'workspace') +
 node(310, 78, 110, 44, 'KeepRoute', 'orchestration') +
 arrow(365, 122, 365, 140) +
 node(300, 140, 130, 36, 'OmniRoute') +
 '</svg>';
 return '<div class="px-diagram" role="img" aria-label="' + esc(caption) + '">' + svg +
 '<div class="px-family-ai9"><strong>AI9 GPU colorizer</strong>' +
 '<span>Family-adjacent · does not require Lite Core</span></div>' +
 '<p class="caption">' + esc(caption) + '</p></div>';
 }
 };

 function renderDiagram(id) {
 var fn = DIAGRAMS[id];
 return fn ? fn() : '';
 }

 function metaBox(k, v) {
 return '<div class="px-meta"><div class="k">' + esc(k) + '</div><div class="v">' + esc(v) + '</div></div>';
 }

 function renderQuick(p) {
 var q = p.quick;
 var html = '<h3>' + esc(q.headline) + '</h3>';
 html += '<p>' + esc(q.opening) + '</p>';
 html += renderDiagram(q.visual);
 html += '<h3>In simple terms</h3><ul>';
 (q.points || []).forEach(function (pt) { html += '<li>' + esc(pt) + '</li>'; });
 html += '</ul>';
 html += '<div class="px-meta-grid">';
 html += metaBox('Best for', q.bestFor);
 html += metaBox('Runs on', q.runsOn);
 if (q.requires) html += metaBox('Requires', q.requires);
 html += metaBox('Cost', q.cost);
 html += '</div>';
 if (q.important) html += '<div class="px-callout"><strong>Important:</strong> ' + esc(q.important) + '</div>';
 if (q.relationship) html += '<p><strong>In the OtaconsKeep family:</strong> ' + esc(q.relationship) + '</p>';
 return html;
 }

 function renderTechnical(p) {
 var t = p.technical;
 var html = '<h3>System role</h3><p>' + esc(t.systemRole) + '</p>';
 html += renderDiagram(t.visual);
 if (t.omniVsKeep) {
 html += '<h3>OmniRoute vs KeepRoute</h3>';
 html += '<div class="px-meta-grid">';
 html += metaBox('OmniRoute', t.omniVsKeep.omniroute);
 html += metaBox('KeepRoute', t.omniVsKeep.keeproute);
 html += '</div>';
 }
 html += '<h3>Major components</h3><ul>';
 (t.components || []).forEach(function (c) { html += '<li>' + esc(c) + '</li>'; });
 html += '</ul>';
 html += '<h3>Data / request flow</h3><ul>';
 (t.dataFlow || []).forEach(function (c) { html += '<li>' + esc(c) + '</li>'; });
 html += '</ul>';
 html += '<h3>Dependencies</h3><ul>';
 (t.dependencies || []).forEach(function (c) { html += '<li>' + esc(c) + '</li>'; });
 html += '</ul>';
 html += '<h3>Persistence</h3><p>' + esc(t.persistence) + '</p>';
 html += '<h3>Networking / interfaces</h3><p>' + esc(t.networking) + '</p>';
 html += '<h3>Hardware</h3><p>' + esc(t.hardware) + '</p>';
 html += '<h3>Installation</h3><p>' + esc(t.installation) + '</p>';
 if (t.capabilityStatus && t.capabilityStatus.length) {
 html += '<h3>Capability status</h3><table class="px-status-table"><thead><tr><th>Item</th><th>Status</th></tr></thead><tbody>';
 t.capabilityStatus.forEach(function (row) {
 html += '<tr><td>' + esc(row.item) + '</td><td>' + esc(row.status) + '</td></tr>';
 });
 html += '</tbody></table>';
 }
 html += '<h3>Limitations</h3><ul>';
 (t.limitations || []).forEach(function (c) { html += '<li>' + esc(c) + '</li>'; });
 html += '</ul>';
 if (t.statusNotes) html += '<div class="px-callout">' + esc(t.statusNotes) + '</div>';
 if (t.engineeringLinks && t.engineeringLinks.length) {
 html += '<h3>Engineering</h3><div class="px-eng-links">';
 t.engineeringLinks.forEach(function (l) {
 html += '<a href="' + esc(l.href) + '">' + esc(l.label) + '</a>';
 });
 html += '</div>';
 }
 return html;
 }

 function ensureShell() {
 var root = $('#px-root');
 if (root) return root;
 root = document.createElement('div');
 root.id = 'px-root';
 root.className = 'px-root';
 root.hidden = true;
 root.innerHTML =
 '<div class="px-backdrop" data-px-close="1"></div>' +
 '<div class="px-dialog" role="dialog" aria-modal="true" aria-labelledby="px-title" tabindex="-1">' +
 '<div class="px-header">' +
 '<div id="px-icon-slot"></div>' +
 '<div style="min-width:0;flex:1">' +
 '<div id="px-badges" class="qp-badges"></div>' +
 '<h2 id="px-title"></h2>' +
 '<p class="px-tagline" id="px-tagline"></p>' +
 '</div>' +
 '<button type="button" class="px-close" data-px-close="1" aria-label="Close explainer">×</button>' +
 '</div>' +
 '<div class="px-modes" role="tablist" aria-label="Explanation mode">' +
 '<button type="button" role="tab" id="px-tab-quick" aria-controls="px-panel" data-mode="quick">Quick Explanation</button>' +
 '<button type="button" role="tab" id="px-tab-tech" aria-controls="px-panel" data-mode="technical">Technical Deep Dive</button>' +
 '</div>' +
 '<div class="px-body" id="px-panel" role="tabpanel"></div>' +
 '</div>';
 document.body.appendChild(root);
 root.addEventListener('click', function (e) {
 if (e.target && e.target.getAttribute('data-px-close')) closeExplainer();
 });
 $('#px-tab-quick', root).addEventListener('click', function () { switchMode('quick'); });
 $('#px-tab-tech', root).addEventListener('click', function () { switchMode('technical'); });
 return root;
 }

 function productById(id) {
 if (!catalog) return null;
 for (var i = 0; i < catalog.products.length; i++) {
 if (catalog.products[i].id === id) return catalog.products[i];
 }
 return null;
 }

 function renderBadges(list, kind) {
 return (list || []).map(function (b) {
 return '<span class="qp-badge" data-kind="' + esc(kind) + '">' + esc(b) + '</span>';
 }).join('');
 }

 function fillDialog(p) {
 var root = ensureShell();
 $('#px-icon-slot', root).innerHTML = ICONS[p.icon] || ICONS.core;
 $('#px-badges', root).innerHTML =
 renderBadges(p.access, 'access') +
 renderBadges(p.maturity, 'maturity') +
 renderBadges(p.runtime, 'runtime');
 $('#px-title', root).textContent = p.name;
 $('#px-tagline', root).textContent = p.tagline;
 switchMode(getMode(), p);
 }

 function switchMode(mode, p) {
 p = p || productById(openProductId);
 if (!p) return;
 setMode(mode);
 var root = ensureShell();
 var quickTab = $('#px-tab-quick', root);
 var techTab = $('#px-tab-tech', root);
 quickTab.setAttribute('aria-selected', mode === 'quick' ? 'true' : 'false');
 techTab.setAttribute('aria-selected', mode === 'technical' ? 'true' : 'false');
 var panel = $('#px-panel', root);
 panel.innerHTML = (mode === 'technical' ? renderTechnical(p) : renderQuick(p));
 panel.innerHTML += footerActions(p);
 }

 function footerActions(p) {
 var html = '<div class="px-footer-actions">';
 (p.actions || []).forEach(function (a) {
 if (a.explainer) return;
 var cls = a.primary ? 'btn btn-primary' : 'btn btn-ghost';
 var extra = a.external ? ' target="_blank" rel="noopener"' : '';
 html += '<a class="' + cls + '" href="' + esc(a.href) + '"' + extra + '>' + esc(a.label) + '</a>';
 });
 html += '</div>';
 return html;
 }

 function openExplainer(id) {
 var p = productById(id);
 if (!p) return;
 lastFocus = document.activeElement;
 openProductId = id;
 fillDialog(p);
 var root = ensureShell();
 root.hidden = false;
 document.body.style.overflow = 'hidden';
 var dialog = $('.px-dialog', root);
 dialog.focus();
 if (location.hash !== '#' + p.hash) {
 history.replaceState(null, '', '#' + p.hash);
 }
 }

 function closeExplainer() {
 var root = $('#px-root');
 if (!root || root.hidden) return;
 root.hidden = true;
 document.body.style.overflow = '';
 openProductId = null;
 var hashes = (catalog && catalog.products || []).map(function (p) { return p.hash; });
 if (hashes.indexOf((location.hash || '').replace('#', '')) >= 0) {
 history.replaceState(null, '', location.pathname + location.search);
 }
 if (lastFocus && lastFocus.focus) lastFocus.focus();
 }

 function trapFocus(e) {
 var root = $('#px-root');
 if (!root || root.hidden || e.key !== 'Tab') return;
 var dialog = $('.px-dialog', root);
 var list = $all(focusablesSel, dialog).filter(function (el) {
 return el.offsetParent !== null || el === dialog;
 });
 if (!list.length) return;
 var first = list[0];
 var last = list[list.length - 1];
 if (e.shiftKey && document.activeElement === first) {
 e.preventDefault();
 last.focus();
 } else if (!e.shiftKey && document.activeElement === last) {
 e.preventDefault();
 first.focus();
 }
 }

 function wireCard(card, p) {
 card.setAttribute('data-product-id', p.id);
 var btn = card.querySelector('[data-explainer="' + p.id + '"]');
 if (btn) {
 btn.addEventListener('click', function (e) {
 e.preventDefault();
 openExplainer(p.id);
 });
 }
 }

 function renderFamilyAndCompare(mount) {
 if (!mount || !catalog) return;
 var familyHtml =
 '<div class="product-family" id="product-family">' +
 '<h2>How the products fit together</h2>' +
 renderDiagram('family') +
 '<p class="intro" style="margin:10px 0 0;font-size:0.9rem;">' + esc(catalog.family_note) + '</p></div>';

 var videoHtml =
 '<div class="product-family-video" id="product-family-video" aria-label="OtaconsKeep video">' +
 '<div class="install-demo-video">' +
 '<div class="install-demo-video-frame">' +
 '<iframe src="https://www.youtube-nocookie.com/embed/vYXsi4ZRStw" ' +
 'title="OtaconsKeep" ' +
 'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" ' +
 'allowfullscreen loading="lazy" referrerpolicy="strict-origin-when-cross-origin"></iframe>' +
 '</div></div>' +
 '<p class="intro" style="margin:10px 0 0;font-size:0.85rem;">' +
 '<a href="https://youtu.be/vYXsi4ZRStw" target="_blank" rel="noopener">Watch on YouTube →</a></p></div>';

 var rows = (catalog.comparison || []).map(function (r) {
 return '<tr><td><strong>' + esc(r.product) + '</strong></td><td>' + esc(r.what) +
 '</td><td>' + esc(r.best_if) + '</td></tr>';
 }).join('');

 var compareHtml =
 '<section class="product-compare" id="which-one" aria-label="Which product do I need">' +
 '<h2>Which one do I need?</h2>' +
 '<div class="eng-table-wrap" style="overflow-x:auto;border:1px solid var(--line);border-radius:4px;">' +
 '<table class="eng-table" style="width:100%;border-collapse:collapse;font-size:0.9rem;min-width:480px;">' +
 '<thead><tr>' +
 '<th style="text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);color:var(--cream-faint);font:600 0.7rem JetBrains Mono,monospace;text-transform:uppercase;">Product</th>' +
 '<th style="text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);color:var(--cream-faint);font:600 0.7rem JetBrains Mono,monospace;text-transform:uppercase;">What it is</th>' +
 '<th style="text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);color:var(--cream-faint);font:600 0.7rem JetBrains Mono,monospace;text-transform:uppercase;">Best if you want</th>' +
 '</tr></thead><tbody>' + rows + '</tbody></table></div></section>';

 mount.insertAdjacentHTML('afterend', familyHtml + videoHtml + compareHtml);
 }

 function checkHash() {
 if (!catalog) return;
 var h = (location.hash || '').replace('#', '');
 for (var i = 0; i < catalog.products.length; i++) {
 if (catalog.products[i].hash === h) {
 openExplainer(catalog.products[i].id);
 return;
 }
 }
 }

 function boot() {
 fetch(DATA_URL, { credentials: 'same-origin' })
 .then(function (r) {
 if (!r.ok) throw new Error('products ' + r.status);
 return r.json();
 })
 .then(function (data) {
 catalog = data;
 MODE_KEY; // storage key from data optional
 if (data.mode_storage_key) {
 /* keep local MODE_KEY constant for simplicity */
 }
 $all('.quickpick[data-product-id]').forEach(function (card) {
 var id = card.getAttribute('data-product-id');
 var p = productById(id);
 if (p) wireCard(card, p);
 });
 var grid = $('.quickpick-grid');
 if (grid) renderFamilyAndCompare(grid.parentElement || grid);
 document.addEventListener('keydown', function (e) {
 if (e.key === 'Escape') closeExplainer();
 trapFocus(e);
 });
 window.addEventListener('hashchange', checkHash);
 checkHash();
 })
 .catch(function (err) {
 console.warn('[product-explainers]', err);
 });
 }

 if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
 else boot();
})();

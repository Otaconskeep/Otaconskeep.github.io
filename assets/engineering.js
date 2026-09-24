/**
 * OtaconsKeep Engineering Portal runtime
 * Loads structured JSON under /data/engineering/ and renders interactive views.
 * Accuracy: never invent PASS / benchmark numbers, compute only from published records.
 */
(function () {
 'use strict';

 var DATA_BASE = '/data/engineering/';
 var FILES = [
 'meta', 'overview', 'requirements', 'architecture', 'interfaces', 'risks',
 'tests', 'evidence', 'benchmarks', 'releases', 'issues', 'models',
 'baselines', 'hardware', 'behavioral_models', 'diagrams', 'math', 'analysis'
 ];

 var state = {
 data: {},
 index: {},
 filters: { q: '', status: '', category: '', subsystem: '' },
 activeSection: 'overview'
 };

 var LIFECYCLE = [
 { id: 'concept', label: 'Concept', section: 'overview' },
 { id: 'requirements', label: 'Requirements', section: 'requirements' },
 { id: 'architecture', label: 'Architecture', section: 'architecture' },
 { id: 'design', label: 'Design', section: 'models-sysml' },
 { id: 'implementation', label: 'Implementation', section: 'interfaces' },
 { id: 'integration', label: 'Integration', section: 'traceability' },
 { id: 'verification', label: 'Verification', section: 'vv' },
 { id: 'validation', label: 'Validation', section: 'vcrm' },
 { id: 'operations', label: 'Operations', section: 'releases' }
 ];

 // Math is also a lifecycle-adjacent destination from verification
 LIFECYCLE.splice(6, 0, { id: 'math', label: 'Math', section: 'math' });

 function $(sel, root) { return (root || document).querySelector(sel); }
 function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

 function escapeHtml(s) {
 return String(s == null ? '' : s)
 .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
 .replace(/"/g, '&quot;');
 }

 function toneForStatus(st) {
 var s = String(st || '').toLowerCase();
 if (/verified|pass|closed|released|qualified|ok/.test(s)) return 'ok';
 if (/fail|open|danger|critical/.test(s)) return 'bad';
 if (/pending|draft|design|mitigating|monitoring|development|blocked|implemented/.test(s)) return 'warn';
 return 'muted';
 }

 function statusHtml(st) {
 var label = st == null || st === '' ? 'No data' : st;
 return '<span class="eng-status" data-tone="' + toneForStatus(label) + '">' + escapeHtml(label) + '</span>';
 }

 function idBtn(id) {
 if (!id) return '-';
 return '<button type="button" class="eng-id" data-eng-id="' + escapeHtml(id) + '">' + escapeHtml(id) + '</button>';
 }

 function badgeLabel(label) {
 var l = String(label || '');
 var cls = 'eng-badge-mock';
 if (/MEASURED/i.test(l)) cls = 'eng-badge-measured';
 else if (/ANALYSIS|INSPECTION/i.test(l)) cls = 'eng-badge-analysis';
 else if (/REFERENCE|MIXED/i.test(l)) cls = 'eng-badge-ref';
 return '<span class="' + cls + '">' + escapeHtml(l) + '</span>';
 }

 function orderedKeys(rec, type) {
 var pref = {
 requirement: ['id', 'title', 'text', 'level', 'category', 'priority', 'satisfied_by', 'allocated_to',
 'verified_by', 'verification_method', 'verification_approach', 'verification_level', 'verified',
 'verification_planned', 'verification_executed', 'evidence', 'result', 'risk', 'risk_level',
 'risk_rationale', 'verification_rationale', 'status'],
 test: ['id', 'title', 'class', 'verification_method', 'verification_level', 'requirements', 'result',
 'evidence', 'procedure', 'expected_result', 'actual_result', 'execution_date', 'source_module', 'source_function'],
 risk: ['id', 'title', 'scenario', 'probability', 'severity', 'initial_risk', 'residual_probability',
 'residual_severity', 'residual_risk', 'residual_rationale', 'status', 'mitigation', 'linked_requirements', 'linked_tests'],
 architecture: ['id', 'name', 'kind', 'sysml_stereotype', 'ports', 'parts', 'description', 'linked_requirements', 'status']
 };
 var keys = pref[type] || Object.keys(rec || {});
 var seen = {};
 var out = [];
 keys.forEach(function (k) {
 if (Object.prototype.hasOwnProperty.call(rec, k)) { out.push(k); seen[k] = true; }
 });
 Object.keys(rec || {}).forEach(function (k) {
 if (!seen[k] && k !== 'mermaid') out.push(k);
 });
 return out;
 }

 function empty(msg) {
 return '<div class="eng-empty" role="status">' + escapeHtml(msg || 'No engineering record has been published for this category.') + '</div>';
 }

 function pubVal(v) {
 if (v == null || v === '' || v === 'No data' || v === 'Not yet published') {
 return '<span class="value muted">Not yet published</span>';
 }
 return '<span class="value">' + escapeHtml(String(v)) + '</span>';
 }

 function fetchJson(name) {
 return fetch(DATA_BASE + name + '.json', { credentials: 'same-origin' })
 .then(function (r) {
 if (!r.ok) throw new Error(name + ' ' + r.status);
 return r.json();
 });
 }

 function buildIndex() {
 var idx = {};
 function put(id, type, obj) {
 if (!id) return;
 idx[id] = { type: type, record: obj };
 }
 (state.data.requirements.requirements || []).forEach(function (r) { put(r.id, 'requirement', r); });
 (state.data.architecture.elements || []).forEach(function (r) { put(r.id, 'architecture', r); });
 (state.data.interfaces.interfaces || []).forEach(function (r) { put(r.id, 'interface', r); });
 (state.data.risks.risks || []).forEach(function (r) { put(r.id, 'risk', r); });
 (state.data.tests.tests || []).forEach(function (r) { put(r.id, 'test', r); });
 (state.data.evidence.evidence || []).forEach(function (r) { put(r.id, 'evidence', r); });
 (state.data.issues.issues || []).forEach(function (r) { put(r.id, 'issue', r); });
 (state.data.models.models || []).forEach(function (r) { put(r.id, 'model', r); });
 (state.data.baselines.baselines || []).forEach(function (r) { put(r.id, 'baseline', r); });
 (state.data.releases.releases || []).forEach(function (r) { put(r.id, 'release', r); });
 (state.data.behavioral_models.models || []).forEach(function (r) { put(r.id, 'behavioral_model', r); });
 (state.data.diagrams.diagrams || []).forEach(function (r) { put(r.id, 'diagram', r); });
 if (state.data.math) {
 (state.data.math.worked_examples || []).forEach(function (r) { put(r.id, 'math_trace', r); });
 }
 if (state.data.analysis) {
 (state.data.analysis.datasets || []).forEach(function (r) { put(r.id, 'dataset', r); });
 }
 state.index = idx;
 }

 function computeMetrics() {
 var reqs = state.data.requirements.requirements || [];
 var tests = state.data.tests.tests || [];
 var risks = state.data.risks.risks || [];
 var verified = reqs.filter(function (r) { return String(r.status).toLowerCase() === 'verified'; }).length;
 var pending = reqs.filter(function (r) {
 return /pending|draft|design|implemented/i.test(String(r.status || ''));
 }).length;
 var passed = tests.filter(function (t) { return /^pass$/i.test(String(t.result || '')); }).length;
 var failed = tests.filter(function (t) { return /fail/i.test(String(t.result || '')); }).length;
 var blocked = tests.filter(function (t) { return /block/i.test(String(t.result || '')); }).length;
 var openRisks = risks.filter(function (r) { return /open|mitigating|monitoring/i.test(String(r.status || '')); }).length;
 var highRisks = risks.filter(function (r) { return (r.residual_risk || r.initial_risk || 0) >= 9; }).length;
 var issues = (state.data.issues.issues || []).filter(function (i) { return /open|monitoring/i.test(i.status || ''); }).length;
 var rel = (state.data.releases.releases || [])[0];

 return [
 { label: 'Current Release', value: rel ? rel.version : null },
 { label: 'Requirements', value: reqs.length },
 { label: 'Requirements Verified', value: verified },
 { label: 'Requirements Pending', value: pending },
 { label: 'System Tests (register)', value: tests.length },
 { label: 'Tests Passed', value: passed },
 { label: 'Tests Failed', value: failed },
 { label: 'Tests Blocked', value: blocked },
 { label: 'Open Risks', value: openRisks },
 { label: 'High Risks (≥9)', value: highRisks },
 { label: 'Known Issues', value: issues },
 { label: 'Architecture Baseline', value: (state.data.architecture.baseline_id || 'Not yet published') },
 { label: 'Last Qualification Run', value: (rel && rel.qualification_date) || 'Not yet published' }
 ];
 }

 function coverageStats() {
 var reqs = state.data.requirements.requirements || [];
 var n = reqs.length || 1;
 function pct(pred) {
 var c = reqs.filter(pred).length;
 return { count: c, pct: Math.round(100 * c / n) };
 }
 return {
 arch: pct(function (r) { return (r.linked_architecture || []).length > 0; }),
 method: pct(function (r) { return !!r.verification_method; }),
 tests: pct(function (r) { return (r.linked_tests || []).length > 0; }),
 verified: pct(function (r) { return String(r.status).toLowerCase() === 'verified'; }),
 riskMit: (function () {
 var risks = state.data.risks.risks || [];
 var withMit = risks.filter(function (r) { return !!r.mitigation; }).length;
 return { count: withMit, pct: risks.length ? Math.round(100 * withMit / risks.length) : 0 };
 })(),
 riskVer: (function () {
 var risks = state.data.risks.risks || [];
 var withT = risks.filter(function (r) { return (r.linked_tests || []).length > 0; }).length;
 return { count: withT, pct: risks.length ? Math.round(100 * withT / risks.length) : 0 };
 })(),
 evid: (function () {
 var tests = state.data.tests.tests || [];
 var withE = tests.filter(function (t) { return (t.evidence || []).length > 0; }).length;
 return { count: withE, pct: tests.length ? Math.round(100 * withE / tests.length) : 0 };
 })()
 };
 }

 function matchFilters(text, record) {
 var q = (state.filters.q || '').trim().toLowerCase();
 if (q) {
 var blob = JSON.stringify(record).toLowerCase();
 if (blob.indexOf(q) === -1 && String(text || '').toLowerCase().indexOf(q) === -1) return false;
 }
 if (state.filters.status && String(record.status || record.result || '') !== state.filters.status) return false;
 if (state.filters.category && String(record.category || record.class || '') !== state.filters.category) return false;
 if (state.filters.subsystem && String(record.allocated_subsystem || record.affected_subsystem || '') !== state.filters.subsystem) return false;
 return true;
 }

 function renderMetrics(el) {
 var metrics = computeMetrics();
 el.innerHTML = metrics.map(function (m) {
 var isMuted = m.value === 'Not yet published' || m.value == null;
 return '<div class="eng-metric"><div class="label">' + escapeHtml(m.label) + '</div>' +
 (isMuted ? '<div class="value muted">' + escapeHtml(m.value == null ? 'Not yet published' : m.value) + '</div>'
 : '<div class="value">' + escapeHtml(String(m.value)) + '</div>') + '</div>';
 }).join('');
 }

 function renderLifecycle(el) {
 el.innerHTML = LIFECYCLE.map(function (s, i) {
 var arrow = i < LIFECYCLE.length - 1 ? '<span class="arrow" aria-hidden="true">→</span>' : '';
 return '<button type="button" data-lifecycle="' + s.id + '" data-section="' + s.section + '" aria-pressed="false">' +
 escapeHtml(s.label) + '</button>' + arrow;
 }).join('');
 }

 function ragTone(rag) {
 var r = String(rag || '').toLowerCase();
 if (r === 'green' || r === 'ok') return 'ok';
 if (r === 'yellow' || r === 'warn' || r === 'amber' || r === 'partial') return 'warn';
 if (r === 'red' || r === 'bad') return 'bad';
 return 'muted';
 }

 function ragCell(rag) {
 var tone = ragTone(rag);
 var label = tone === 'ok' ? 'GO' : tone === 'warn' ? 'PARTIAL' : tone === 'bad' ? 'NO' : ', ';
 return '<span class="eng-rag" data-tone="' + tone + '" title="' + escapeHtml(String(rag || '')) + '">' + label + '</span>';
 }

 function evidencePackageStrip() {
 var reqs = state.data.requirements.requirements || [];
 var tests = state.data.tests.tests || [];
 var risks = state.data.risks.risks || [];
 var verified = reqs.filter(function (r) { return String(r.status).toLowerCase() === 'verified'; }).length;
 var openRisks = risks.filter(function (r) { return /open|mitigating|monitoring/i.test(r.status || ''); }).length;
 var high = risks.filter(function (r) { return (r.residual_risk || 0) >= 9; }).length;
 var blocked = tests.filter(function (t) { return /block/i.test(String(t.result || '')); }).length;
 var cm = ((state.data.math && state.data.math.chapters) || []).length;
 var models = ((state.data.behavioral_models && state.data.behavioral_models.models) || []).length;
 var measured = ((state.data.benchmarks && state.data.benchmarks.benchmarks) || []).filter(function (b) {
 return b.label === 'MEASURED';
 }).length;
 var chips = [
 { label: 'Requirements', value: reqs.length, tone: reqs.length ? 'ok' : 'muted', href: '#requirements' },
 { label: 'Verified', value: verified, tone: verified ? 'ok' : 'warn', href: '#vcrm' },
 { label: 'Tests on register', value: tests.length, tone: tests.length ? 'ok' : 'muted', href: '#tests' },
 { label: 'Blocked tests', value: blocked, tone: blocked ? 'bad' : 'ok', href: '#tests' },
 { label: 'Open risks', value: openRisks, tone: openRisks ? 'warn' : 'ok', href: '#risk' },
 { label: 'High residual (≥9)', value: high, tone: high ? 'bad' : 'ok', href: '#risk' },
 { label: 'Continuity eqns', value: cm, tone: cm >= 20 ? 'ok' : 'warn', href: '#math' },
 { label: 'Behavior models', value: models, tone: models >= 20 ? 'ok' : 'warn', href: '#behavioral' },
 { label: 'GPU MEASURED', value: measured, tone: measured >= 3 ? 'ok' : 'warn', href: '#benchmarks' }
 ];
 return '<div class="eng-ov-strip" aria-label="Evidence package health">' +
 chips.map(function (c) {
 return '<a class="eng-ov-chip" data-tone="' + c.tone + '" href="' + c.href + '">' +
 '<span class="eng-ov-chip-val">' + escapeHtml(String(c.value)) + '</span>' +
 '<span class="eng-ov-chip-lab">' + escapeHtml(c.label) + '</span></a>';
 }).join('') + '</div>';
 }

 function renderOverview(root) {
 var o = state.data.overview;
 var html = '';
 html += '<p class="eng-ov-tagline">' + escapeHtml(o.tagline || 'Digital engineering evidence board') + '</p>';
 html += '<p class="intro">' + escapeHtml(o.purpose) + '</p>';
 html += evidencePackageStrip();

 html += '<div class="eng-ov-jump">';
 (o.jump_links || []).forEach(function (j) {
 html += '<a class="eng-ov-jump-btn" data-tone="' + escapeHtml(j.tone || 'cyan') + '" href="' + escapeHtml(j.href) + '">' +
 escapeHtml(j.label) + '</a>';
 });
 html += '</div>';

 html += '<div class="eng-ov-grid-3">';
 html += '<article class="eng-ov-panel"><h3>Mission</h3><p>' + escapeHtml(o.mission) + '</p></article>';
 html += '<article class="eng-ov-panel"><h3>Operational concept</h3><p>' + escapeHtml(o.operational_concept) + '</p></article>';
 html += '<article class="eng-ov-panel eng-ov-panel-boundaries"><h3>Product lanes</h3>';
 html += '<p><span class="eng-lane cyan">Lite</span> ' + escapeHtml(o.lite_premium_boundaries.Lite) + '</p>';
 if (o.lite_premium_boundaries.AI9) {
 html += '<p><span class="eng-lane cyan">AI9</span> ' + escapeHtml(o.lite_premium_boundaries.AI9) + '</p>';
 }
 html += '<p><span class="eng-lane amber">Expansion</span> ' + escapeHtml(o.lite_premium_boundaries.Expansion) + '</p>';
 html += '<p><span class="eng-lane slate">Reference</span> ' + escapeHtml(o.lite_premium_boundaries['Reference Keep']) + '</p>';
 html += '</article></div>';

 // Product portfolio
 html += '<h3 class="eng-ov-h">Product portfolio</h3>';
 html += '<div class="eng-ov-products">';
 (o.products || []).forEach(function (p) {
 html += '<article class="eng-ov-product" data-color="' + escapeHtml(p.color || 'cyan') + '">' +
 '<header><span class="eng-ov-prod-name">' + escapeHtml(p.name) + '</span>' +
 statusHtml(p.maturity) + '</header>' +
 '<div class="eng-ov-prod-meta">' +
 '<span class="eng-lane ' + escapeHtml(p.color || 'cyan') + '">' + escapeHtml(p.access) + '</span> ' +
 '<span class="eng-ov-evid" data-tone="' + ragTone(p.evidence === 'Partial' ? 'yellow' : p.evidence === 'Not public clone' ? 'muted' : 'green') + '">' +
 escapeHtml(p.evidence) + '</span></div>' +
 '<p>' + escapeHtml(p.claim) + '</p>' +
 (p.relationship || p.requires_lite_core === false || p.dependency_note ?
 '<p class="eng-ov-sub">' +
 (p.relationship ? escapeHtml(p.relationship) + '. ' : '') +
 (p.requires_lite_core === false ? 'Does not require Lite Core. ' : (p.requires_lite_core === true ? 'Requires Lite Core. ' : '')) +
 escapeHtml(p.dependency_note || '') +
 '</p>' : '') +
 (p.link ? '<a href="' + escapeHtml(p.link) + '">Open →</a>' : '') +
 '</article>';
 });
 html += '</div>';

 // Capability matrix
 if (o.capability_matrix) {
 var cm = o.capability_matrix;
 html += '<h3 class="eng-ov-h">Capability matrix <span class="eng-ov-sub">(RAG vs product lane)</span></h3>';
 if (cm.notes) html += '<p class="intro">' + escapeHtml(cm.notes) + '</p>';
 html += '<div class="eng-ov-legend">';
 Object.keys(cm.legend || {}).forEach(function (k) {
 html += '<span>' + ragCell(k) + ' ' + escapeHtml(cm.legend[k]) + '</span>';
 });
 html += '</div>';
 html += '<div class="eng-table-wrap"><table class="eng-table eng-ov-matrix" aria-label="Capability matrix"><thead><tr><th>Capability</th>';
 (cm.columns || []).forEach(function (c) { html += '<th>' + escapeHtml(c) + '</th>'; });
 html += '</tr></thead><tbody>';
 (cm.rows || []).forEach(function (row) {
 html += '<tr><td>' + escapeHtml(row.capability) + '</td>';
 (cm.columns || []).forEach(function (c) { html += '<td class="eng-ov-matrix-cell">' + ragCell(row[c]) + '</td>'; });
 html += '</tr>';
 });
 html += '</tbody></table></div>';
 }

 // Deployments + capabilities
 html += '<div class="eng-ov-grid-2">';
 html += '<section><h3 class="eng-ov-h">Deployment readiness</h3>';
 html += '<div class="eng-table-wrap"><table class="eng-table"><thead><tr><th>ID</th><th>Name</th><th>RAG</th><th>Status</th><th>Notes</th></tr></thead><tbody>';
 (o.deployment_models || []).forEach(function (d) {
 html += '<tr><td class="mono">' + escapeHtml(d.id) + '</td><td>' + escapeHtml(d.name) +
 '</td><td>' + ragCell(d.rag || 'yellow') + '</td><td>' + statusHtml(d.status) +
 '</td><td>' + escapeHtml(d.notes || '') + '</td></tr>';
 });
 html += '</tbody></table></div></section>';

 html += '<section><h3 class="eng-ov-h">Major capabilities</h3><ul class="eng-ov-caplist">';
 (o.major_capabilities || []).forEach(function (c) {
 if (typeof c === 'string') {
 html += '<li>' + escapeHtml(c) + '</li>';
 } else {
 html += '<li>' + ragCell(c.rag) + ' <strong>' + escapeHtml(c.name) + '</strong> ' +
 '<span class="eng-ov-sub">' + escapeHtml(c.lane || '') + '</span></li>';
 }
 });
 html += '</ul></section></div>';

 // Scope lanes
 html += '<h3 class="eng-ov-h">System boundaries</h3>';
 html += '<div class="eng-ov-scope">';
 html += '<div class="eng-ov-scope-col in"><h4>In scope (public)</h4><ul>';
 (o.system_boundaries.in_scope_public || []).forEach(function (x) {
 html += '<li>' + escapeHtml(x) + '</li>';
 });
 html += '</ul></div>';
 html += '<div class="eng-ov-scope-col out"><h4>Out of scope / reference</h4><ul>';
 (o.system_boundaries.out_of_scope_or_reference_only || []).forEach(function (x) {
 html += '<li>' + escapeHtml(x) + '</li>';
 });
 html += '</ul></div></div>';

 // Externals + context
 html += '<h3 class="eng-ov-h">External systems</h3><div class="eng-ov-ext">';
 (o.external_systems || []).forEach(function (e) {
 html += '<div class="eng-ov-ext-chip" data-tier="' + escapeHtml(e.tier || 'optional') + '">' +
 '<strong>' + escapeHtml(e.name) + '</strong>' +
 '<span>' + escapeHtml(e.role) + '</span>' +
 '<span class="mono">' + escapeHtml(e.id) + '</span></div>';
 });
 html += '</div>';

 html += '<h3 class="eng-ov-h">Context map</h3><div class="eng-ov-context">';
 (o.context_nodes || []).forEach(function (n) {
 html += '<span class="eng-ov-node" data-kind="' + escapeHtml(n.kind) + '">' +
 escapeHtml(n.label) + '</span>';
 });
 html += '</div>';

 html += '<div class="eng-ov-grid-2" style="margin-top:18px">';
 html += '<section class="eng-ov-panel assume"><h3>Assumptions</h3><ul>';
 (o.assumptions || []).forEach(function (a) { html += '<li>' + escapeHtml(a) + '</li>'; });
 html += '</ul></section>';
 html += '<section class="eng-ov-panel constrain"><h3>Constraints</h3><ul>';
 (o.constraints || []).forEach(function (a) { html += '<li>' + escapeHtml(a) + '</li>'; });
 html += '</ul></section></div>';

 html += '<p class="intro" style="margin-top:16px">Actors: ' + escapeHtml((o.major_actors || []).join(' · ')) + '</p>';
 root.innerHTML = html;
 }

 function card(title, body) {
 return '<div class="eng-card" tabindex="0"><h3>' + escapeHtml(title) + '</h3><p>' + escapeHtml(body) + '</p></div>';
 }

  function renderReqTable(root) {
    var pack = state.data.requirements;
    var rows = (pack.requirements || []).filter(function (r) {
      return matchFilters(r.id + ' ' + r.title + ' ' + r.text, r);
    });
    if (!rows.length) { root.innerHTML = empty('No requirements match filters.'); return; }
    var legend =
      '<div class="eng-req-legend">' +
      '<span class="eng-req-level" data-level="1">L1 System</span>' +
      '<span class="eng-req-level" data-level="2">L2 Subsystem</span>' +
      '<span class="eng-req-level" data-level="3">L3 Component</span>' +
      '<span class="intro" style="margin:0">MBSE / SysML shall-statements. Verified=Yes only with evidence.</span></div>';
    root.innerHTML =
      '<p class="intro"><strong>' + escapeHtml(pack.baseline_id || '') + '</strong> · ' +
      escapeHtml(pack.methodology || 'MBSE / SysML requirements') + '</p>' +
      '<p class="intro">' + escapeHtml(pack.notes || '') + ' Click an ID for full record (acceptance G/W/T, rationales).</p>' +
      legend +
      '<div class="eng-toolbar"><button type="button" class="eng-export" data-export="rtm">Export CSV</button></div>' +
      '<div class="eng-table-wrap"><table class="eng-table eng-req-table" aria-label="System requirements">' +
      '<thead><tr>' +
      '<th>Level</th><th>ID</th><th>Title</th><th>Text (shall)</th><th>Category</th><th>Priority</th>' +
      '<th>Verification method</th><th>Verification approach</th><th>Verified</th>' +
      '<th>Planned</th><th>Executed</th><th>Risk</th><th>Risk level</th><th>Risk rationale</th>' +
      '<th>Verification rationale</th>' +
      '</tr></thead><tbody>' +
      rows.map(function (r) {
        var lvl = r.level || 2;
        return '<tr data-level="' + lvl + '">' +
          '<td><span class="eng-req-level" data-level="' + lvl + '">L' + lvl + '</span></td>' +
          '<td>' + idBtn(r.id) + '</td>' +
          '<td>' + escapeHtml(r.title) + '</td>' +
          '<td class="eng-req-shall">' + escapeHtml(r.text) + '</td>' +
          '<td>' + escapeHtml(r.category) + '</td>' +
          '<td>' + escapeHtml(r.priority) + '</td>' +
          '<td>' + escapeHtml(r.verification_method || '-') + '</td>' +
          '<td class="eng-req-approach">' + escapeHtml(r.verification_approach || '-') + '</td>' +
          '<td>' + (r.verified === 'Yes'
            ? '<span class="eng-status" data-tone="ok">Yes</span>'
            : '<span class="eng-status" data-tone="warn">No</span>') + '</td>' +
          '<td>' + escapeHtml(r.verification_planned || '-') + '</td>' +
          '<td>' + escapeHtml(r.verification_executed || '-') + '</td>' +
          '<td>' + (r.risk && r.risk !== 'None' ? idBtn(r.risk) : 'None') + '</td>' +
          '<td><span class="eng-risk-lvl" data-lvl="' + escapeHtml(String(r.risk_level || 'None')) + '">' +
            escapeHtml(r.risk_level || 'None') + '</span></td>' +
          '<td class="eng-req-rationale">' + escapeHtml(r.risk_rationale || '-') + '</td>' +
          '<td class="eng-req-rationale">' + escapeHtml(r.verification_rationale || '-') + '</td>' +
          '</tr>';
      }).join('') + '</tbody></table></div>';
  }

  function mathVarIcon(kind) {
    var icons = {
      weight: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3l2.5 6.5H22l-5.5 4 2.1 6.5L12 16.8 5.4 20l2.1-6.5L2 9.5h7.5z"/></svg>',
      trigger: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13 2L4 14h7l-1 8 10-14h-7l1-6z"/></svg>',
      state: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="3" fill="currentColor"/></svg>',
      event: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 100 20 10 10 0 000-20zm1 5v5.2l3.5 2.1-.8 1.3L11 13V7h2z"/></svg>',
      relation: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 10a3 3 0 110-6 3 3 0 010 6zm8 0a3 3 0 110-6 3 3 0 010 6zM4 20v-1a5 5 0 015-5h1.2a6.5 6.5 0 000 2H9a3 3 0 00-3 3v1H4zm16 0v-1a3 3 0 00-3-3h-1.2a6.5 6.5 0 000-2H17a5 5 0 015 5v1h-2z"/></svg>',
      memory: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6 4h12a2 2 0 012 2v14l-8-3.5L4 20V6a2 2 0 012-2z"/></svg>',
      goal: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 3a7 7 0 110 14 7 7 0 010-14zm0 3a4 4 0 100 8 4 4 0 000-8zm0 2.5a1.5 1.5 0 110 3 1.5 1.5 0 010-3z"/></svg>',
      clamp: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 7h16v2H4V7zm0 8h16v2H4v-2zm3-4h10v2H7v-2z"/></svg>',
      score: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 19h2V9H4v10zm4 0h2V5H8v14zm4 0h2v-7h-2v7zm4 0h2V8h-2v11zm4 0h2v-4h-2v4z"/></svg>',
      default: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2L2 7l10 5 10-5-10-5zm0 9L2 6v2l10 5 10-5V6l-10 5zm0 4L2 10v2l10 5 10-5v-2l-10 5z"/></svg>'
    };
    return icons[kind] || icons.default;
  }

  function mathVarKind(sym, def) {
    var blob = String(sym || '') + ' ' + String(def || '');
    blob = blob.toLowerCase();
    if (/weight|w_t|b_d|confidence factor|modifier/.test(blob)) return 'weight';
    if (/trigger|g_t|match|active/.test(blob)) return 'trigger';
    if (/state|x_t|mood|baseline|x\^|x★|x\*/.test(blob)) return 'state';
    if (/event|delta|δ|impact|ω/.test(blob)) return 'event';
    if (/relation|trust|target|y_j|bond|person/.test(blob)) return 'relation';
    if (/memory|γ|recency|retrieval|m_/.test(blob)) return 'memory';
    if (/goal|utilit|u_k|g_t/.test(blob)) return 'goal';
    if (/clip|clamp|cap|bound|δ_/.test(blob)) return 'clamp';
    if (/score|quality|q_t|argmax|valence/.test(blob)) return 'score';
    return 'default';
  }

  function parseVarCard(v, lineFallback) {
    if (v && (v.sym || v.def)) {
      return { sym: v.sym || '', def: v.def || '', kind: mathVarKind(v.sym, v.def) };
    }
    var line = String(lineFallback || '');
    var m = line.match(/^(.+?)\s+is\s+(.+?)\.?$/i);
    if (m) return { sym: m[1].trim(), def: m[2].trim(), kind: mathVarKind(m[1], m[2]) };
    return { sym: '', def: line, kind: 'default' };
  }

  function renderMathVarCards(sec, s) {
    var cards = [];
    if (sec.variables_plain && sec.variables_plain.length) {
      cards = sec.variables_plain.map(function (v) {
        return { plain: v.plain || '', tip: v.tip || '', kind: v.kind || mathVarKind(v.plain, v.tip) };
      });
    } else if (sec.variables && sec.variables.length) {
      cards = sec.variables.map(function (v) {
        return {
          plain: v.def || v.sym || '',
          tip: v.sym ? ('Symbol: ' + v.sym) : '',
          kind: mathVarKind(v.sym, v.def)
        };
      });
    } else if (s.variables_explained && s.variables_explained.length) {
      cards = s.variables_explained.map(function (line) {
        var c = parseVarCard(null, line);
        return { plain: c.def || c.sym, tip: c.sym, kind: c.kind };
      });
    }
    if (!cards.length) return '';
    var html = '<div class="eng-math-block" data-tone="vars">';
    html += '<h5 class="eng-math-h">Variables (picture cards)</h5>';
    html += '<div class="eng-math-vargrid">';
    cards.forEach(function (c, i) {
      var tone = ['cyan', 'amber', 'violet', 'green', 'rose'][i % 5];
      html += '<div class="eng-math-varcard eng-math-varcard-graphic" data-tone="' + tone + '">';
      html += '<div class="eng-math-varicon eng-math-varicon-lg" data-kind="' + escapeHtml(c.kind) + '">' + mathVarIcon(c.kind) + '</div>';
      html += '<div class="eng-math-varbody">';
      html += '<div class="eng-math-varplain">' + escapeHtml(c.plain) + '</div>';
      if (c.tip) html += '<div class="eng-math-defvar">' + escapeHtml(c.tip) + '</div>';
      html += '</div></div>';
    });
    html += '</div></div>';
    return html;
  }

  function mathBlock(tone, title, bodyHtml) {
    if (!bodyHtml) return '';
    return '<div class="eng-math-block" data-tone="' + tone + '">' +
      '<h5 class="eng-math-h">' + escapeHtml(title) + '</h5>' +
      bodyHtml + '</div>';
  }

  function renderMathChapter(sec) {
    var s = sec.simplified || {};
    var html = '<article class="eng-math-chapter" id="' + escapeHtml(sec.id) + '">';
    html += '<h3>' + escapeHtml(String(sec.number) + ') ' + sec.title) + '</h3>';
    if (s.headline || sec.simple_explanation) {
      html += '<p class="eng-math-q"><span class="eng-math-q-kicker">Answers</span> ' +
        escapeHtml(s.headline || sec.simple_explanation) + '</p>';
    }

    html += '<h4 class="eng-math-eq-label">Equation</h4>';
    (sec.katex || []).forEach(function (eq) {
      html += '<div class="eng-katex" data-katex="' + escapeHtml(eq) + '"></div>';
    });

    html += '<div class="eng-math-easy">';
    html += '<div class="eng-math-easy-banner">In plain terms</div>';

    var lead = s.plain_equation || (sec.meaning ? sec.meaning : '');
    if (lead) {
      html += '<p class="eng-math-easy-lead"><strong>' + escapeHtml(lead) + '</strong></p>';
    }

    html += renderMathVarCards(sec, s);

    if (s.how_it_touches_agents) {
      html += mathBlock('agent', 'How this touches an agent',
        '<p class="eng-math-body">' + escapeHtml(s.how_it_touches_agents) + '</p>');
    }
    if (s.how_it_works || sec.why_this_logic) {
      html += mathBlock('logic', 'Why this logic / how it works',
        '<p class="eng-math-body">' + escapeHtml(s.how_it_works || sec.why_this_logic) + '</p>');
    }
    if (s.why_it_works) {
      html += mathBlock('why', 'Why these choices',
        '<p class="eng-math-body">' + escapeHtml(s.why_it_works) + '</p>');
    } else if (sec.psychology_theory_basis && sec.psychology_theory_basis.length) {
      html += mathBlock('why', 'Theory basis',
        '<ul class="eng-math-chiprow">' + sec.psychology_theory_basis.map(function (p) {
          return '<li>' + escapeHtml(p) + '</li>';
        }).join('') + '</ul>');
    }
    if (s.how_put_together || sec.why_these_variables) {
      html += mathBlock('stack', 'Why these variables / how it fits the stack',
        '<p class="eng-math-body">' + escapeHtml(s.how_put_together || sec.why_these_variables) + '</p>');
    }
    if (s.connects_to) {
      html += mathBlock('link', 'Connection',
        '<p class="eng-math-body">' + escapeHtml(s.connects_to) + '</p>');
    }
    html += '</div>';

    if (sec.summary_equation) {
      html += '<h4 class="eng-math-eq-label">Short summary</h4>';
      (sec.summary_equation.katex || []).forEach(function (eq) {
        html += '<div class="eng-katex" data-katex="' + escapeHtml(eq) + '"></div>';
      });
      if (sec.summary_equation.meaning) html += '<p class="intro">' + escapeHtml(sec.summary_equation.meaning) + '</p>';
      if (sec.summary_equation.simple) html += '<p class="intro">' + escapeHtml(sec.summary_equation.simple) + '</p>';
    }
    html += '</article>';
    return html;
  }

  function renderMath(root) {
    var m = state.data.math;
    if (!m) { root.innerHTML = empty(); return; }
    var html = '';
    html += '<p class="intro"><strong>' + escapeHtml(m.title || 'Continuity Model') + '</strong>';
    if (m.created_by) html += ' · Created by ' + escapeHtml(m.created_by);
    html += '</p>';
    html += '<p class="intro">' + escapeHtml(m.honesty) + '</p>';

    if (m.simplified_intro) {
      html += '<h3>' + escapeHtml(m.simplified_intro.title) + '</h3>';
      (m.simplified_intro.body || []).forEach(function (p) {
        html += '<p class="intro">' + escapeHtml(p) + '</p>';
      });
    }

    if (m.rationale) {
      html += '<h3>' + escapeHtml(m.rationale.title) + '</h3><ul style="color:var(--cream-dim)">';
      (m.rationale.body || []).forEach(function (b) { html += '<li>' + escapeHtml(b) + '</li>'; });
      html += '</ul>';
      var j = m.rationale.core_logic_justification || {};
      html += '<div class="eng-math-justify"><p><strong>Why multiplication:</strong> ' + escapeHtml(j.multiplication || '') + '</p>';
      html += '<p><strong>Why summation:</strong> ' + escapeHtml(j.summation || '') + '</p>';
      html += '<p><strong>Why decay:</strong> ' + escapeHtml(j.decay || '') + '</p>';
      html += '<p><strong>Why bounded noise:</strong> ' + escapeHtml(j.bounded_noise || '') + '</p></div>';
    }

    if (m.manual_note) {
      html += '<blockquote class="eng-math-note">' + escapeHtml(m.manual_note) + '</blockquote>';
    }

    html += '<h3>Table of contents</h3><ol class="eng-math-toc">';
    (m.toc || m.chapters || []).forEach(function (t) {
      var id = t.id || ('CM-' + String(t.number).padStart(2, '0'));
      html += '<li><a href="#' + escapeHtml(id) + '">' + escapeHtml(String(t.number || '') + '. ' + (t.title || '')) + '</a></li>';
    });
    html += '</ol>';

    html += '<p class="intro">Each section shows the generalized equation first, then the plain-language explanation immediately under it.</p>';

    (m.chapters || []).forEach(function (sec) {
      html += renderMathChapter(sec);
    });

    html += '<h3>How the equations interact during a Codec turn</h3>';
    html += '<ol class="eng-math-flow" style="color:var(--cream-dim)">';
    html += '<li><strong>Identity and traits load</strong> (CM-01, CM-15). Dossier lines become weights; identity keeps a floor.</li>';
    html += '<li><strong>Event arrives</strong> (CM-03, CM-12, CM-13). Inputs are normalized and capped, then turned into state deltas.</li>';
    html += '<li><strong>State and relationships update</strong> (CM-04, CM-05, CM-07). Mood moves, bonds shift, residue carries forward, then decay pulls toward baseline.</li>';
    html += '<li><strong>Memory and goals compete</strong> (CM-09, CM-18, CM-19, CM-22). Relevant memories score; goals get utilities; conflict resolution picks a dominant driver (CM-20).</li>';
    html += '<li><strong>Reply assembles</strong> (CM-11, CM-16). Output mixes identity with adaptive continuity; quality can feed learning (CM-21).</li>';
    html += '</ol>';
    html += '<p class="intro">Social and device equations (CM-06, CM-10, CM-17) only join when those adapters are configured. Markov and OR views (CM-24, CM-25) are analysis and planning layers, not a replacement for the continuous state.</p>';

    if (m.runtime_mapping) {
      html += '<h3 id="runtime-mapping">' + escapeHtml(m.runtime_mapping.title) + '</h3>';
      html += '<p class="intro">' + escapeHtml(m.runtime_mapping.note || '') + '</p>';
      (m.runtime_mapping.sections || []).forEach(function (sec) {
        html += '<h4 id="' + escapeHtml(sec.id) + '">' + escapeHtml(sec.title) + '</h4>';
        (sec.katex || []).forEach(function (eq) {
          html += '<div class="eng-katex" data-katex="' + escapeHtml(eq) + '"></div>';
        });
        if (sec.notes) html += '<p class="intro">' + escapeHtml(sec.notes) + '</p>';
      });
    }

    if (m.markov_or_notes) {
      html += '<h3>' + escapeHtml(m.markov_or_notes.title) + '</h3>';
      html += '<p class="intro">' + escapeHtml(m.markov_or_notes.body) + '</p>';
    }

    html += '<h3>Worked numerical examples</h3>';
    (m.worked_examples || []).forEach(function (ex) {
      html += '<div class="eng-mock-card"><span class="eng-badge-mock">' + escapeHtml(ex.label || 'MOCK') + '</span> ' +
        '<strong>' + escapeHtml(ex.id) + '</strong>: ' + escapeHtml(ex.title) +
        '<pre class="eng-eq">' + escapeHtml(JSON.stringify({ initial: ex.initial, event: ex.event, steps: ex.steps, final: ex.final }, null, 2)) +
        '</pre><p class="intro">' + escapeHtml(ex.disclaimer || '') + '</p></div>';
    });
    if (m.pipeline) {
      html += '<h3>' + escapeHtml(m.pipeline.title) + '</h3><ol style="color:var(--cream-dim)">';
      (m.pipeline.steps || []).forEach(function (s) { html += '<li>' + escapeHtml(s) + '</li>'; });
      html += '</ol><p class="intro">Linked: ' + (m.pipeline.linked_models || []).map(idBtn).join(' ') +
        ' ' + idBtn(m.pipeline.linked_diagram) + '</p>';
    }
    html += '<h3>Measurable metrics and tests</h3><div class="eng-table-wrap"><table class="eng-table"><thead><tr><th>Metric</th><th>Test</th></tr></thead><tbody>';
    (m.measurable_metrics || []).forEach(function (row) {
      html += '<tr><td>' + escapeHtml(row.metric) + '</td><td>' + idBtn(row.test) + '</td></tr>';
    });
    html += '</tbody></table></div>';
    html += '<p class="intro"><a href="/about/#feeling">About: measurable emotion</a> · <a href="#behavioral">Behavioral Models</a></p>';
    root.innerHTML = html;
    typesetKatex(root);
  }

 function typesetKatex(root) {
 if (!window.katex) return;
 $all('[data-katex]', root).forEach(function (el) {
 try {
 window.katex.render(el.getAttribute('data-katex'), el, { throwOnError: false, displayMode: true });
 } catch (e) { el.textContent = el.getAttribute('data-katex'); }
 });
 }

 function renderHeatmap(corr) {
 var vars = corr.variables || [];
 var mat = corr.matrix || [];
 var html = '<div class="eng-heat" role="img" aria-label="' + escapeHtml(corr.title) + '">';
 html += '<div class="eng-heat-row"><span class="eng-heat-lab"></span>' + vars.map(function (v) {
 return '<span class="eng-heat-lab">' + escapeHtml(v) + '</span>';
 }).join('') + '</div>';
 mat.forEach(function (row, i) {
 html += '<div class="eng-heat-row"><span class="eng-heat-lab">' + escapeHtml(vars[i] || '') + '</span>';
 row.forEach(function (v) {
 var t = (v + 1) / 2;
 var bg = 'rgba(57,230,200,' + (0.15 + 0.75 * Math.abs(v)).toFixed(2) + ')';
 if (v < 0) bg = 'rgba(239,95,107,' + (0.15 + 0.75 * Math.abs(v)).toFixed(2) + ')';
 html += '<span class="eng-heat-cell" style="background:' + bg + '" title="' + v + '">' + Number(v).toFixed(2) + '</span>';
 });
 html += '</div>';
 });
 html += '</div>';
 return html;
 }

 function renderAnalysis(root) {
 var a = state.data.analysis;
 if (!a) { root.innerHTML = empty('No dataset available'); return; }
 var html = '<p class="intro">' + escapeHtml(a.honesty) + '</p>';
 html += '<div class="eng-callout-ok">Status: ' + escapeHtml(a.status) +
 ' · sample_total ≈ ' + escapeHtml(String(a.sample_total || '-')) +
 '. ANALYSIS = equation-derived public samples (no private Keep logs).</div>';
 html += '<h3>Datasets</h3><ul style="color:var(--cream-dim)">';
 (a.datasets || []).forEach(function (d) {
 html += '<li>' + badgeLabel(d.label) + ' ' + idBtn(d.id) +
 ' · ' + escapeHtml(d.title) +
 (d.n != null ? ' <span class="mono">(n=' + escapeHtml(String(d.n)) + ')</span>' : '') +
 ' · <a href="' + escapeHtml(d.path) + '">CSV</a><br>' + escapeHtml(d.description) + '</li>';
 });
 html += '</ul>';
 (a.correlations || []).forEach(function (c) {
 html += '<h3>' + badgeLabel(c.label) + ' ' + escapeHtml(c.title) + '</h3>';
 html += renderHeatmap(c);
 html += '<p class="intro">' + escapeHtml(c.note || '') + '</p>';
 });
 if (a.sensitivity) {
 var s = a.sensitivity;
 html += '<h3>' + badgeLabel(s.label) + ' ' + escapeHtml(s.title) + '</h3>';
 html += '<p class="intro">Baseline ΔJ ≈ ' + escapeHtml(String(s.baseline_delta_j)) + '</p>';
 html += '<div class="eng-tornado">';
 (s.bars || []).forEach(function (b) {
 var lo = Number(b.low), hi = Number(b.high), base = Number(s.baseline_delta_j) || 1;
 var span = Math.max(Math.abs(hi - base), Math.abs(lo - base), 0.001);
 html += '<div class="eng-tornado-row"><span class="lab">' + escapeHtml(b.param) + '</span>' +
 '<span class="bar"><i style="left:50%;width:' + Math.min(48, 48 * Math.abs(hi - lo) / (2 * span)).toFixed(1) +
 '%"></i></span><span class="nums">' + lo + ' → ' + hi + '</span></div>';
 });
 html += '</div><p class="intro">' + escapeHtml(s.note || '') + '</p>';
 }
 root.innerHTML = html;
 }

 function renderBenchmarks(root) {
 var b = state.data.benchmarks;
 var html = '';
 if (b.disclaimer) {
 html += '<div class="eng-callout-amber">' + escapeHtml(b.disclaimer) + '</div>';
 }
 if (b.plan) {
 html += '<h3>' + escapeHtml(b.plan.title) + ' (' + escapeHtml(b.plan.id) + ')</h3>';
 html += '<p class="intro">' + escapeHtml(b.plan.method) + ' Rule: ' + escapeHtml(b.plan.rule) + '</p>';
 html += '<ul style="color:var(--cream-dim)">' + (b.plan.classes || []).map(function (c) {
 return '<li>' + escapeHtml(c) + '</li>';
 }).join('') + '</ul>';
 }
 if (b.gpu_tier_csv) {
 html += '<p class="intro">GPU tier CSV: <a href="' + escapeHtml(b.gpu_tier_csv) + '">' + escapeHtml(b.gpu_tier_csv) + '</a></p>';
 }
 var rows = b.benchmarks || [];
 if (!rows.length) {
 html += empty(b.status || 'No engineering record has been published for this category.');
 } else {
 html += '<div class="eng-table-wrap"><table class="eng-table" aria-label="Benchmarks"><thead><tr>' +
 '<th>ID</th><th>Label</th><th>Series</th><th>GPU</th><th>VRAM</th><th>tok/s mean</th><th>p95</th><th>TTFT ms</th><th>N</th><th>Date</th></tr></thead><tbody>';
 rows.forEach(function (r) {
 var badge = r.label === 'MEASURED' ? 'eng-badge-measured' : 'eng-badge-mock';
 html += '<tr><td>' + idBtn(r.id) + '</td><td><span class="' + badge + '">' + escapeHtml(r.label || '') +
 '</span></td><td>' + escapeHtml(r.series || r.class || '-') + '</td><td>' + escapeHtml(r.gpu || r.hardware || '-') +
 '</td><td>' + escapeHtml(r.vram || '-') + '</td><td>' + escapeHtml(r.mean == null ? '-' : String(r.mean)) +
 '</td><td>' + escapeHtml(r.p95 == null ? '-' : String(r.p95)) +
 '</td><td>' + escapeHtml(r.ttft_ms_mean == null ? '-' : String(r.ttft_ms_mean)) +
 '</td><td>' + escapeHtml(String(r.n == null ? '-' : r.n)) +
 '</td><td>' + escapeHtml(r.date || '-') + '</td></tr>';
 });
 html += '</tbody></table></div>';
 html += '<p class="intro">' + escapeHtml(b.status || '') + '</p>';
 }
 root.innerHTML = html;
 }

 function renderHardware(root) {
 var h = state.data.hardware;
 var tiers = (h.capability_tiers || []).map(function (t) {
 return '<tr><td>' + escapeHtml(t.name) + '</td><td>' + escapeHtml(t.vram) + '</td><td>' +
 escapeHtml(t.capability) + '</td><td>' + statusHtml(t.status) + '</td></tr>';
 }).join('');
 var tested = h.tested_hardware || [];
 root.innerHTML =
 '<p class="intro">Hardware capability based on published installer/FAQ guidance. No unsupported performance claims.</p>' +
 '<div class="eng-table-wrap"><table class="eng-table" aria-label="Capability tiers"><thead><tr><th>Tier</th><th>VRAM</th><th>Capability</th><th>Status</th></tr></thead><tbody>' +
 tiers + '</tbody></table></div>' +
 '<h3 style="margin:16px 0 8px;font-size:1rem;">Minimum / environment</h3>' +
 '<ul style="color:var(--cream-dim);font-size:0.9rem;">' +
 Object.keys(h.minimum_requirements || {}).map(function (k) {
 var v = h.minimum_requirements[k];
 return '<li><strong>' + escapeHtml(k) + ':</strong> ' + escapeHtml(Array.isArray(v) ? v.join(', ') : String(v)) + '</li>';
 }).join('') + '</ul>' +
 '<h3 style="margin:16px 0 8px;font-size:1rem;">Tested hardware</h3>' +
 (tested.length ? tested.map(function (t) {
 return '<div class="eng-empty">' + escapeHtml(t.status || t.known_limitations && t.known_limitations[0] || 'No data') + '</div>';
 }).join('') : empty());
 }

 function renderArch(root) {
 var arch = state.data.architecture;
 var els = arch.elements || [];
 root.innerHTML =
 '<p class="intro">Architecture baseline <strong class="mono">' + escapeHtml(arch.baseline_id) +
 '</strong> · ' + escapeHtml(arch.baseline_status) + '. Elements are SysML <span class="mono">«block»</span> classifiers. ' +
 escapeHtml(arch.mbse_note || '') + '</p>' +
 '<div class="eng-table-wrap"><table class="eng-table" aria-label="Architecture elements"><thead><tr>' +
 '<th>ID</th><th>Name</th><th>«block»</th><th>Parts</th><th>Ports</th><th>Status</th><th>Requirements</th></tr></thead><tbody>' +
 els.map(function (e) {
 return '<tr><td>' + idBtn(e.id) + '</td><td>' + escapeHtml(e.name) + '</td><td>' +
 escapeHtml(e.sysml_stereotype || 'block') + '</td><td>' + ((e.parts || []).map(idBtn).join(' ') || '-') +
 '</td><td class="mono">' + escapeHtml((e.ports || []).join(', ') || '-') +
 '</td><td>' + statusHtml(e.status) + '</td><td>' + (e.linked_requirements || []).map(idBtn).join(' ') + '</td></tr>';
 }).join('') + '</tbody></table></div>' +
 '<div id="eng-diagrams-arch"></div>';
 renderDiagrams($('#eng-diagrams-arch'), ['CTX-001', 'BDD-001', 'IBD-001', 'UML-COMP-001']);
 }

 function renderDiagrams(root, ids) {
 if (!root) return;
 var diagrams = state.data.diagrams.diagrams || [];
 var list = ids ? diagrams.filter(function (d) { return ids.indexOf(d.id) >= 0; }) : diagrams;
 root.innerHTML = list.map(function (d) {
 return '<div class="eng-diagram eng-diagram-' + escapeHtml(d.type || '') + '" data-diagram="' + escapeHtml(d.id) + '">' +
 '<div class="eng-diagram-toolbar"><strong class="mono" style="flex:1;color:var(--cream-dim);font-size:0.8rem;">' +
 idBtn(d.id) + ' · ' + escapeHtml(d.notation || d.type || '') + ' · ' + escapeHtml(d.title) + '</strong>' +
 '<button type="button" data-fs="' + escapeHtml(d.id) + '">Fullscreen</button></div>' +
 '<pre class="mermaid">' + escapeHtml(d.mermaid) + '</pre>' +
 '<p class="eng-diagram-caption">' + escapeHtml(d.notes || d.title) + '</p></div>';
 }).join('');
 runMermaid(root);
 }

 function runMermaid(root) {
 if (!window.mermaid) return;
 try {
 window.mermaid.run({ nodes: $all('.mermaid', root || document) });
 } catch (e) { /* ignore render races */ }
 }

 function renderSysML(root) {
 root.innerHTML =
 '<p class="intro">SysML / UML model views. <strong>BDD</strong> = Block Definition Diagram (blocks, parts, values, ports). ' +
 '<strong>IBD</strong> = Internal Block Diagram (part usages, ports, connectors, item flows). UML sequence/component views included where useful. ' +
 'MBSE-001 shows the Need → Requirement → «satisfy» → «verify» → Evidence chain.</p>' +
 '<div id="eng-sysml-diagrams"></div>';
 renderDiagrams($('#eng-sysml-diagrams'), [
 'BDD-001', 'IBD-001', 'UML-COMP-001', 'MBSE-001', 'PAR-001',
 'SEQ-001', 'SEQ-002', 'ACT-001', 'ACT-002', 'ACT-003', 'STM-001', 'STM-002', 'CTX-001'
 ]);
 }

 function renderInterfaces(root) {
 var rows = state.data.interfaces.interfaces || [];
 root.innerHTML = '<div class="eng-table-wrap"><table class="eng-table" aria-label="Interfaces"><thead><tr><th>ID</th><th>Source</th><th>Destination</th><th>Protocol</th><th>Purpose</th><th>Reqs</th></tr></thead><tbody>' +
 rows.map(function (i) {
 return '<tr><td>' + idBtn(i.id) + '</td><td>' + escapeHtml(i.source) + '</td><td>' + escapeHtml(i.destination) +
 '</td><td>' + escapeHtml(i.protocol) + '</td><td>' + escapeHtml(i.purpose) + '</td><td>' +
 (i.associated_requirements || []).map(idBtn).join(' ') + '</td></tr>';
 }).join('') + '</tbody></table></div>';
 }

 function renderTraceability(root) {
 var reqs = state.data.requirements.requirements || [];
 root.innerHTML =
 '<p class="intro">MBSE chain: Need → Requirement → Architecture («satisfy») → Implementation → Verification Case («verify») → Evidence → Result. Verified requires evidence.</p>' +
 '<div class="eng-toolbar"><button type="button" class="eng-export" data-export="rtm">Export CSV</button>' +
 '<button type="button" class="eng-export" data-export="rtm-json">Export JSON</button></div>' +
 '<div class="eng-table-wrap"><table class="eng-table" id="eng-rtm" aria-label="Requirements traceability matrix"><thead><tr>' +
 '<th>Requirement</th><th>Title</th><th>Satisfied by</th><th>Allocated to</th><th>Method</th><th>Verified by</th><th>Evidence</th><th>Result</th></tr></thead><tbody>' +
 reqs.map(function (r) {
 var evid = r.evidence || [];
 if (!evid.length) {
 (r.verified_by || r.linked_tests || []).forEach(function (tid) {
 var t = state.index[tid] && state.index[tid].record;
 if (t && t.evidence) evid = evid.concat(t.evidence);
 });
 }
 return '<tr><td>' + idBtn(r.id) + '</td><td>' + escapeHtml(r.title) + '</td><td>' +
 (r.satisfied_by || r.linked_architecture || []).map(idBtn).join(' ') + '</td><td>' +
 idBtn(r.allocated_to || r.allocated_subsystem) +
 '</td><td>' + escapeHtml(r.verification_method) + '</td><td>' +
 (r.verified_by || r.linked_tests || []).map(idBtn).join(' ') +
 '</td><td>' + (evid.length ? evid.map(idBtn).join(' ') : '-') + '</td><td>' +
 statusHtml(r.result || r.status) + '</td></tr>';
 }).join('') + '</tbody></table></div>' +
 '<h3 style="margin:18px 0 8px;font-size:1rem;">Traceability graph</h3>' +
 '<div class="eng-toolbar"><label class="mono" style="font-size:0.75rem;color:var(--cream-faint);">Select ID </label>' +
 '<select id="eng-trace-select">' + reqs.map(function (r) {
 return '<option value="' + escapeHtml(r.id) + '">' + escapeHtml(r.id) + '</option>';
 }).join('') + '</select></div><div class="eng-trace-graph" id="eng-trace-graph"></div>';
 updateTraceGraph();
 }

 function updateTraceGraph() {
 var sel = $('#eng-trace-select');
 var out = $('#eng-trace-graph');
 if (!sel || !out) return;
 var id = sel.value;
 var r = state.index[id] && state.index[id].record;
 if (!r) { out.textContent = 'No data'; return; }
 var lines = ['<span class="node">' + escapeHtml(id) + '</span> <span style="color:var(--cream-faint)">(«requirement»)</span>'];
 (r.satisfied_by || r.linked_architecture || []).forEach(function (a) {
 lines.push('↓ «satisfy»');
 lines.push('<span class="node">' + escapeHtml(a) + '</span> <span style="color:var(--cream-faint)">(«block»)</span>');
 });
 if (r.allocated_to || r.allocated_subsystem) {
 lines.push('↓ allocatedTo');
 lines.push('<span class="node">' + escapeHtml(r.allocated_to || r.allocated_subsystem) + '</span>');
 }
 (r.verified_by || r.linked_tests || []).forEach(function (a) {
 lines.push('↓ «verify»');
 lines.push('<span class="node">' + escapeHtml(a) + '</span>');
 var t = state.index[a] && state.index[a].record;
 if (t) {
 lines.push('↓ method / level');
 lines.push(escapeHtml(t.verification_method || r.verification_method || '-') + ' · ' +
 escapeHtml(t.verification_level || r.verification_level || '-'));
 lines.push('↓ result');
 lines.push(statusHtml(t.result));
 (t.evidence || []).forEach(function (e) {
 lines.push('↓ evidence');
 lines.push('<span class="node">' + escapeHtml(e) + '</span>');
 });
 }
 });
 out.innerHTML = lines.join('<br>');
 }

 function renderVCRM(root) {
 var reqs = state.data.requirements.requirements || [];
 var chain = state.data.requirements.mbse_chain ||
 'Need → Requirement → Architecture → Mathematical Model → Implementation → Verification Case → Evidence → Result';
 root.innerHTML =
 '<p class="intro">The <strong>Verification Cross-Reference Matrix (VCRM)</strong> is a generated view of relationships already stored in the engineering model. ' +
 'It shows how every requirement is proven: verification method (TAID: Test / Analysis / Inspection / Demonstration), verification case, level, evidence, release, and result. ' +
 'Relationships: «satisfy» (design element), «verify» (verification case). Model chain: <span class="mono">' + escapeHtml(chain) + '</span>. ' +
 'ST-003 remains Blocked with EVID-001 (honesty).</p>' +
 '<div class="eng-toolbar"><button type="button" class="eng-export" data-export="vcrm">Export CSV</button></div>' +
 '<div class="eng-table-wrap"><table class="eng-table" aria-label="VCRM"><thead><tr>' +
 '<th>Requirement</th><th>Verification Method</th><th>Verification Case</th><th>Level</th>' +
 '<th>Satisfied by</th><th>Evidence</th><th>Result</th><th>Status</th></tr></thead><tbody>' +
 reqs.map(function (r) {
 var cases = r.verified_by || r.linked_tests || [];
 if (!cases.length) {
 return '<tr><td>' + idBtn(r.id) + '</td><td>' + escapeHtml(r.verification_method) +
 '</td><td>-</td><td>' + escapeHtml(r.verification_level || '-') +
 '</td><td>' + ((r.satisfied_by || []).map(idBtn).join(' ') || '-') +
 '</td><td>-</td><td>' + statusHtml('Verification Pending') +
 '</td><td>' + statusHtml(r.status) + '</td></tr>';
 }
 return cases.map(function (tid) {
 var t = state.index[tid] && state.index[tid].record || {};
 var evid = (t.evidence && t.evidence.length) ? t.evidence : (r.evidence || []);
 return '<tr><td>' + idBtn(r.id) + '</td><td>' +
 escapeHtml(t.verification_method || r.verification_method) + '</td><td>' +
 idBtn(tid) + '</td><td>' +
 escapeHtml(t.verification_level || r.verification_level || '-') + '</td><td>' +
 ((r.satisfied_by || r.linked_architecture || []).map(idBtn).join(' ') || idBtn(r.allocated_to) || '-') +
 '</td><td>' + (evid.length ? evid.map(idBtn).join(' ') : '-') +
 '</td><td>' + statusHtml(t.result || r.result) +
 '</td><td>' + statusHtml(r.status) + '</td></tr>';
 }).join('');
 }).join('') + '</tbody></table></div>';
 }

 function renderVV(root) {
 var c = coverageStats();
 var reqs = state.data.requirements.requirements || [];
 var verified = reqs.filter(function (r) { return String(r.status).toLowerCase() === 'verified'; }).length;
 root.innerHTML =
 '<div class="eng-card-grid">' +
 '<div class="eng-card"><h3>Verification</h3><p>Did we build the system right? Covers requirement, integration, system, and regression checks against published procedures.</p></div>' +
 '<div class="eng-card"><h3>Validation</h3><p>Did we build the right system? Operational validation and release qualification, not inferred from code existence alone.</p></div>' +
 '</div>' +
 '<p class="intro" style="margin-top:14px;">Verified requirements / total: <strong>' + verified + ' / ' + reqs.length +
 '</strong> (Verified count increases only when status is Verified with evidence, currently none claimed without evidence).</p>' +
 '<div class="eng-coverage">' +
 cov('Req → architecture', c.arch) + cov('Req → verify method', c.method) +
 cov('Req → tests', c.tests) + cov('Req verified', c.verified) +
 cov('Risks mitigated', c.riskMit) + cov('Risks with tests', c.riskVer) +
 cov('Tests with evidence', c.evid) +
 '</div>' +
 '<div id="eng-vmodel"></div>';
 renderDiagrams($('#eng-vmodel'), ['VMOD-001']);
 }

 function cov(label, s) {
 return '<div class="eng-metric"><div class="label">' + escapeHtml(label) + '</div>' +
 '<div class="value">' + s.count + ' (' + s.pct + '%)</div><div class="bar"><span style="width:' + s.pct + '%"></span></div></div>';
 }

 function renderTests(root) {
 var tests = (state.data.tests.tests || []).filter(function (t) { return matchFilters(t.id + ' ' + t.title, t); });
 var sum = state.data.tests.suite_summary || {};
 var rex = state.data.tests.rex_metrics || {};
 root.innerHTML =
 '<p class="intro">' + escapeHtml(state.data.tests.inventory_note || '') + '</p>' +
 '<div class="eng-suite-strip">' +
 '<div><span class="k">Total</span><span class="v">' + escapeHtml(String(sum.total || tests.length)) + '</span></div>' +
 '<div><span class="k">Pass</span><span class="v ok">' + escapeHtml(String(sum.pass != null ? sum.pass : '-')) + '</span></div>' +
 '<div><span class="k">Blocked</span><span class="v warn">' + escapeHtml(String(sum.blocked != null ? sum.blocked : '-')) + '</span></div>' +
 '<div><span class="k">Fail</span><span class="v bad">' + escapeHtml(String(sum.fail != null ? sum.fail : 0)) + '</span></div>' +
 '<div><span class="k">Modules audited</span><span class="v">' + escapeHtml(String(sum.executor_modules_audited || '-')) + '</span></div>' +
 '</div>' +
 '<p class="intro">REX metrics: ' + escapeHtml(rex.status || 'No data') + ': ' + escapeHtml(rex.note || '') + '</p>' +
 '<div class="eng-table-wrap" style="margin-top:12px;"><table class="eng-table" aria-label="Test register"><thead><tr>' +
 '<th>ID</th><th>Title</th><th>Class</th><th>Method</th><th>Level</th><th>Requirements</th><th>Result</th><th>Evidence</th></tr></thead><tbody>' +
 tests.map(function (t) {
 return '<tr><td>' + idBtn(t.id) + '</td><td>' + escapeHtml(t.title) + '</td><td>' + escapeHtml(t.class) +
 '</td><td>' + escapeHtml(t.verification_method || '-') + '</td><td>' + escapeHtml(t.verification_level || '-') +
 '</td><td>' + (t.requirements || []).map(idBtn).join(' ') + '</td><td>' + statusHtml(t.result) +
 '</td><td>' + ((t.evidence || []).map(idBtn).join(' ') || '-') + '</td></tr>';
 }).join('') + '</tbody></table></div>';
 }

 function riskBand(score) {
 var bands = (state.data.risks.matrix && state.data.risks.matrix.bands) || [
 { name: 'Low', min: 1, max: 4, color: '#2f6f4e' },
 { name: 'Medium', min: 5, max: 9, color: '#c4a035' },
 { name: 'High', min: 10, max: 15, color: '#c45c26' },
 { name: 'Critical', min: 16, max: 25, color: '#a33b3b' }
 ];
 for (var i = 0; i < bands.length; i++) {
 if (score >= bands[i].min && score <= bands[i].max) return bands[i];
 }
 return bands[0];
 }

 function renderRisks(root) {
 var risks = state.data.risks.risks || [];
 var matrixMeta = state.data.risks.matrix || {};
 var cells = {};
 risks.forEach(function (r) {
 var p = r.probability || 0, s = r.severity || 0;
 var k = p + ',' + s;
 (cells[k] = cells[k] || []).push(r);
 });
 var matrix = '<div class="eng-risk-matrix-wrap"><div class="eng-risk-axis-y">Probability →</div>' +
 '<div class="eng-risk-matrix" role="grid" aria-label="SE risk matrix P×S">';
 matrix += '<div class="hdr corner"></div>';
 for (var sev = 1; sev <= 5; sev++) matrix += '<div class="hdr">S' + sev + '</div>';
 for (var p = 5; p >= 1; p--) {
 matrix += '<div class="hdr">P' + p + '</div>';
 for (var s = 1; s <= 5; s++) {
 var score = p * s;
 var band = riskBand(score);
 var items = cells[p + ',' + s] || [];
 var ids = items.map(function (r) { return r.id; });
 matrix += '<button type="button" class="cell' + (items.length ? ' has' : '') +
 '" style="background:' + band.color + (items.length ? 'ee' : '55') +
 '" data-risk-cell="' + escapeHtml(ids.join(',')) +
 '" title="' + escapeHtml((ids.join(', ') || 'empty') + ' · score ' + score + ' (' + band.name + ')') + '">' +
 (items.length ? '<span class="n">' + items.length + '</span><span class="ids">' +
 ids.map(function (id) { return id.replace('RSK-', ''); }).join(' ') + '</span>' : '') +
 '</button>';
 }
 }
 matrix += '</div><div class="eng-risk-axis-x">Severity →</div></div>';
 var legend = '<div class="eng-risk-legend">' +
 (matrixMeta.bands || []).map(function (b) {
 return '<span><i style="background:' + escapeHtml(b.color) + '"></i>' +
 escapeHtml(b.name) + ' (' + b.min + '–' + b.max + ')</span>';
 }).join('') + '</div>';
 var cards = risks.map(function (r) {
 var steps = r.mitigation_steps || {};
 var road = (r.roadmap || []).map(function (x) {
 return '<li>' + escapeHtml(x.step) + ': <em>' + escapeHtml(x.status) + '</em></li>';
 }).join('');
 var ib = riskBand(r.initial_risk || 0);
 var rb = riskBand(r.residual_risk || 0);
 return '<article class="eng-risk-card">' +
 '<h3>' + idBtn(r.id) + ' ' + escapeHtml(r.title) + ' ' + statusHtml(r.status) + '</h3>' +
 '<div class="eng-risk-scores">' +
 '<span class="score" style="border-color:' + ib.color + '">Initial P' + r.probability + '×S' + r.severity +
 '=' + r.initial_risk + ' <em>' + escapeHtml(ib.name) + '</em></span>' +
 '<span class="score" style="border-color:' + rb.color + '">Residual P' + r.residual_probability +
 '×S' + r.residual_severity + '=' + r.residual_risk + ' <em>' + escapeHtml(rb.name) + '</em></span></div>' +
 '<p><strong>Scenario:</strong> ' + escapeHtml(r.scenario || r.description) + '</p>' +
 '<p><strong>Cause chain:</strong> ' + escapeHtml((r.cause_chain || [r.cause]).join(' → ')) + '</p>' +
 '<p><strong>Detection:</strong> ' + escapeHtml((r.detection || []).join('; ') || '-') + '</p>' +
 '<p><strong>Mitigation strategy</strong></p><ul style="color:var(--cream-dim);font-size:0.88rem">' +
 '<li>Prevent: ' + escapeHtml((steps.prevent || []).join('; ') || '-') + '</li>' +
 '<li>Detect: ' + escapeHtml((steps.detect || []).join('; ') || '-') + '</li>' +
 '<li>Respond: ' + escapeHtml((steps.respond || []).join('; ') || '-') + '</li>' +
 '<li>Recover: ' + escapeHtml((steps.recover || []).join('; ') || '-') + '</li></ul>' +
 '<p><strong>Residual rationale:</strong> ' + escapeHtml(r.residual_rationale || '') + '</p>' +
 '<p><strong>Owner / review:</strong> ' + escapeHtml(r.owner || '-') + ' / ' + escapeHtml(r.review_date || '-') + '</p>' +
 (road ? '<p><strong>Roadmap</strong></p><ul style="color:var(--cream-dim);font-size:0.88rem">' + road + '</ul>' : '') +
 '<p>Links: ' + (r.linked_requirements || []).map(idBtn).join(' ') + ' ' +
 (r.linked_tests || []).map(idBtn).join(' ') + '</p></article>';
 }).join('');
 root.innerHTML =
 '<p class="intro">Systems engineering 5×5 risk matrix (Probability × Severity). Cell color = score band. ' +
 'Click a cell to open the first risk ID. RSK-005 remains Open (residual High) until the WSL e2e gate is green.</p>' +
 legend + matrix +
 '<div class="eng-toolbar" style="margin-top:14px;"><button type="button" class="eng-export" data-export="risks">Export CSV</button></div>' +
 cards;
 }

 function renderBehavioral(root) {
 var bm = state.data.behavioral_models;
 var models = bm.models || [];
 var cm = models.filter(function (m) { return String(m.id).indexOf('MOD-CM-') === 0; });
 var other = models.filter(function (m) { return String(m.id).indexOf('MOD-CM-') !== 0; });
 root.innerHTML =
 '<p class="intro">Registry of behavioral / Continuity Model modules. Full equation write-ups: <a href="#math">Math</a>.</p>' +
 (bm.continuity_model ? '<div class="eng-callout-amber">' + escapeHtml(bm.continuity_model.title) +
 ', ' + escapeHtml(String(bm.continuity_model.count)) + ' design equations by ' +
 escapeHtml(bm.continuity_model.author || '') + '. ' + escapeHtml(bm.continuity_model.note || '') + '</div>' : '') +
 '<p class="intro">Behavior Model <strong class="mono">' + escapeHtml(bm.behavior_model_version) +
 '</strong> · Personality Schema <strong class="mono">' + escapeHtml(bm.personality_schema_version) +
 '</strong> · Relationship <strong class="mono">' + escapeHtml((bm.relationship_model_versions || []).join(' / ')) + '</strong></p>' +
 '<h3>Continuity Model registry (' + cm.length + ')</h3>' +
 '<div class="eng-card-grid" style="margin-bottom:16px;">' +
 cm.map(function (m) {
 return '<button type="button" class="eng-card" data-eng-id="' + escapeHtml(m.id) + '"><h3>' +
 escapeHtml(m.id) + '</h3><p>' + escapeHtml(m.name) + ', ' + escapeHtml(m.purpose) +
 (m.continuity_model_ref ? ' · <span class="mono">' + escapeHtml(m.continuity_model_ref) + '</span>' : '') +
 '</p></button>';
 }).join('') + '</div>' +
 '<h3>Runtime emotion / relationship modules</h3>' +
 '<div class="eng-card-grid" style="margin-bottom:16px;">' +
 other.map(function (m) {
 return '<button type="button" class="eng-card" data-eng-id="' + escapeHtml(m.id) + '"><h3>' +
 escapeHtml(m.id) + '</h3><p>' + escapeHtml(m.name) + ', ' + escapeHtml(m.purpose) + '</p></button>';
 }).join('') + '</div>' +
 renderEmotionTables(bm) +
 renderPersonalityCompare(bm) +
 '<h3 style="margin:18px 0 8px;font-size:1rem;">State traces</h3>' +
 '<p class="intro">Live Keep traces are not exported. Public ANALYSIS samples: <a href="#analysis">Analysis</a>. Equation write-ups: <a href="#math">Math</a>.</p>';
 }

 function renderModels(root) {
 var models = state.data.models.models || [];
 root.innerHTML =
 '<p class="intro">Separates third-party foundation models from anything OtaconsKeep trains or fine-tunes. ' +
 escapeHtml(state.data.models.notes || '') + '</p>' +
 '<div class="eng-table-wrap"><table class="eng-table" aria-label="Model provenance"><thead><tr>' +
 '<th>ID</th><th>Component</th><th>Model</th><th>Hosting</th><th>OK fine-tuned?</th><th>Statement</th></tr></thead><tbody>' +
 models.map(function (m) {
 return '<tr><td>' + idBtn(m.id) + '</td><td>' + escapeHtml(m.component) + '</td><td>' + escapeHtml(m.model) +
 '</td><td>' + escapeHtml(m.hosting) + '</td><td>' + (m.fine_tuned_by_otaconskeep ? 'Yes' : 'No') +
 '</td><td>' + escapeHtml(m.statement || '') + '</td></tr>';
 }).join('') + '</tbody></table></div>';
 }

 function renderEmotionTables(bm) {
 var emo = (bm.models || []).find(function (m) { return m.id === 'MOD-EMO-001'; });
 if (!emo) return '';
 var rows = (emo.state_variables || []).map(function (v) {
 return '<tr><td class="mono">' + escapeHtml(String(v.symbol)) + '</td><td>' + escapeHtml(v.name) +
 '</td><td>' + escapeHtml(JSON.stringify(v.range)) + '</td><td>' + escapeHtml(String(v.default)) +
 '</td><td>' + escapeHtml(v.timescale) + '</td></tr>';
 }).join('');
 return '<h3 style="margin:8px 0;font-size:1rem;">MOD-EMO-001 state vector</h3>' +
 '<div class="eng-table-wrap"><table class="eng-table" aria-label="Emotion state"><thead><tr><th>Symbol</th><th>State</th><th>Range</th><th>Default</th><th>Timescale</th></tr></thead><tbody>' +
 rows + '</tbody></table></div>' +
 '<h3 style="margin:14px 0 8px;font-size:1rem;">Update / blend rule</h3>' +
 '<div class="eng-eq">' + escapeHtml(JSON.stringify(emo.blend_rule, null, 2)) + '</div>' +
 '<h3 style="margin:14px 0 8px;font-size:1rem;">Time decay</h3>' +
 '<div class="eng-eq">' + escapeHtml(JSON.stringify(emo.time_decay, null, 2)) + '</div>' +
 '<h3 style="margin:14px 0 8px;font-size:1rem;">Comparison event</h3>' +
 '<div class="eng-eq">' + escapeHtml(JSON.stringify(emo.comparison_event, null, 2)) + '</div>';
 }

 function renderPersonalityCompare(bm) {
 var per = (bm.models || []).find(function (m) { return m.id === 'MOD-PER-001'; });
 if (!per || !per.profiles) return '';
 var dims = Object.keys(per.profiles._default || {});
 var agents = Object.keys(per.profiles).filter(function (k) { return k !== '_default'; });
 var head = '<th>Parameter</th>' + agents.map(function (a) { return '<th>' + escapeHtml(a) + '</th>'; }).join('');
 var body = dims.map(function (d) {
 return '<tr><td class="mono">' + escapeHtml(d) + '</td>' + agents.map(function (a) {
 return '<td>' + escapeHtml(String(per.profiles[a][d])) + '</td>';
 }).join('') + '</tr>';
 }).join('');
 return '<h3 style="margin:18px 0 8px;font-size:1rem;">Personality parameter comparison (source profiles)</h3>' +
 '<div class="eng-table-wrap"><table class="eng-table" aria-label="Personality comparison"><thead><tr>' + head +
 '</tr></thead><tbody>' + body + '</tbody></table></div>' +
 '<p class="intro">Radar charts omitted until a visualization dependency is standardized; table values are authoritative.</p>';
 }

 function renderReleases(root) {
 var rels = state.data.releases.releases || [];
 var bases = state.data.baselines.baselines || [];
 root.innerHTML =
 '<div class="eng-table-wrap"><table class="eng-table" aria-label="Release qualification"><thead><tr>' +
 '<th>ID</th><th>Version</th><th>Qualification</th><th>Status</th><th>Blocked tests</th><th>Notes</th></tr></thead><tbody>' +
 rels.map(function (r) {
 return '<tr><td>' + idBtn(r.id) + '</td><td>' + escapeHtml(r.version) + '</td><td>' +
 escapeHtml(r.qualification_date || 'Not yet published') + '</td><td>' + statusHtml(r.qualification_status) +
 '</td><td>' + (r.blocked_tests || []).map(idBtn).join(' ') + '</td><td>' + escapeHtml(r.notes || '') + '</td></tr>';
 }).join('') + '</tbody></table></div>' +
 '<h3 style="margin:18px 0 8px;font-size:1rem;">Configuration baselines</h3>' +
 '<div class="eng-table-wrap"><table class="eng-table"><thead><tr><th>ID</th><th>Type</th><th>Name</th><th>Release</th><th>Status</th></tr></thead><tbody>' +
 bases.map(function (b) {
 return '<tr><td>' + idBtn(b.id) + '</td><td>' + escapeHtml(b.type) + '</td><td>' + escapeHtml(b.name) +
 '</td><td>' + escapeHtml(b.release) + '</td><td>' + statusHtml(b.status) + '</td></tr>';
 }).join('') + '</tbody></table></div>' +
 '<p class="intro">Schema versions: ' + escapeHtml(JSON.stringify(state.data.baselines.schema_versions || {})) + '</p>';
 }

 function renderIssues(root) {
 var issues = state.data.issues.issues || [];
 root.innerHTML = '<div class="eng-table-wrap"><table class="eng-table" aria-label="Known issues"><thead><tr>' +
 '<th>ID</th><th>Description</th><th>Severity</th><th>Subsystem</th><th>Status</th><th>Workaround</th></tr></thead><tbody>' +
 issues.map(function (i) {
 return '<tr><td>' + idBtn(i.id) + '</td><td>' + escapeHtml(i.description) + '</td><td>' +
 escapeHtml(i.severity) + '</td><td>' + idBtn(i.affected_subsystem) + '</td><td>' +
 statusHtml(i.status) + '</td><td>' + escapeHtml(i.workaround) + '</td></tr>';
 }).join('') + '</tbody></table></div>';
 }

 function renderSearchResults(root, q) {
 q = (q || '').trim().toLowerCase();
 if (!q) { root.innerHTML = ''; return; }
 var hits = [];
 Object.keys(state.index).forEach(function (id) {
 var entry = state.index[id];
 var blob = (id + ' ' + JSON.stringify(entry.record)).toLowerCase();
 if (blob.indexOf(q) >= 0) hits.push({ id: id, type: entry.type });
 });
 root.innerHTML = hits.length
 ? '<div class="eng-table-wrap"><table class="eng-table"><thead><tr><th>ID</th><th>Type</th></tr></thead><tbody>' +
 hits.slice(0, 80).map(function (h) {
 return '<tr><td>' + idBtn(h.id) + '</td><td>' + escapeHtml(h.type) + '</td></tr>';
 }).join('') + '</tbody></table></div>'
 : empty('No matches.');
 }

 var SECTION_RENDERERS = {
 overview: renderOverview,
 requirements: renderReqTable,
 hardware: renderHardware,
 architecture: renderArch,
 'models-sysml': renderSysML,
 interfaces: renderInterfaces,
 traceability: renderTraceability,
 vv: renderVV,
 vcrm: renderVCRM,
 tests: renderTests,
 risk: renderRisks,
 analysis: renderAnalysis,
 benchmarks: renderBenchmarks,
 models: renderModels,
 math: renderMath,
 behavioral: renderBehavioral,
 releases: renderReleases,
 issues: renderIssues,
 search: function (root) { renderSearchResults(root, state.filters.q); }
 };

 function showSection(id) {
 state.activeSection = id;
 $all('.eng-sidebar a').forEach(function (a) {
 a.setAttribute('aria-current', a.getAttribute('href') === '#' + id ? 'true' : 'false');
 });
 $all('.eng-section').forEach(function (sec) {
 var match = sec.id === 'sec-' + id;
 sec.hidden = !match;
 });
 var panel = $('#panel-' + id);
 if (panel && SECTION_RENDERERS[id]) {
 SECTION_RENDERERS[id](panel);
 bindDynamic(panel);
 }
 if (location.hash !== '#' + id) {
 history.replaceState(null, '', '#' + id);
 }
 }

 function openDetail(id) {
 var entry = state.index[id];
 var drawer = $('#eng-drawer');
 var back = $('#eng-backdrop');
 if (!entry || !drawer) return;
 var r = entry.record;
 drawer.innerHTML =
 '<button type="button" class="close" id="eng-drawer-close" aria-label="Close">Close</button>' +
 '<h2>' + escapeHtml(id) + '</h2>' +
 '<p style="color:var(--cream-dim);margin:0 0 8px;">Type: ' + escapeHtml(entry.type) + '</p>' +
 '<dl>' + orderedKeys(r, entry.type).map(function (k) {
 var v = r[k];
 var display;
 if (Array.isArray(v)) display = v.map(function (x) {
 return typeof x === 'string' && state.index[x] ? idBtn(x) : escapeHtml(String(x));
 }).join(' ');
 else if (v && typeof v === 'object') display = '<pre class="eng-eq" style="margin:0">' + escapeHtml(JSON.stringify(v, null, 2)) + '</pre>';
 else if (typeof v === 'string' && state.index[v]) display = idBtn(v);
 else display = escapeHtml(String(v));
 return '<dt>' + escapeHtml(k) + '</dt><dd>' + display + '</dd>';
 }).join('') + '</dl>';
 drawer.classList.add('open');
 back.classList.add('open');
 $('#eng-drawer-close').onclick = closeDetail;
 bindDynamic(drawer);
 }

 function closeDetail() {
 $('#eng-drawer').classList.remove('open');
 $('#eng-backdrop').classList.remove('open');
 }

  function exportCsv(kind) {
    var rows = [];
    if (kind === 'vcrm') {
      rows.push(['Requirement', 'Verification Method', 'Verification Case', 'Level', 'Satisfied by', 'Evidence', 'Result', 'Status']);
      (state.data.requirements.requirements || []).forEach(function (r) {
        var cases = r.verified_by || r.linked_tests || ['-'];
        cases.forEach(function (tid) {
          var t = state.index[tid] && state.index[tid].record || {};
          rows.push([
            r.id,
            t.verification_method || r.verification_method,
            tid,
            t.verification_level || r.verification_level,
            (r.satisfied_by || []).join(' '),
            ((t.evidence || r.evidence || []).join(' ')),
            t.result || r.result,
            r.status
          ]);
        });
      });
    } else if (kind === 'rtm') {
      rows.push(['Level', 'ID', 'Title', 'Text', 'Category', 'Priority', 'Method', 'Approach', 'Verified', 'Planned', 'Executed', 'Risk', 'Risk level', 'Risk rationale', 'Verification rationale', 'Status']);
      (state.data.requirements.requirements || []).forEach(function (r) {
        rows.push([
          r.level, r.id, r.title, r.text, r.category, r.priority,
          r.verification_method, r.verification_approach, r.verified,
          r.verification_planned, r.verification_executed,
          r.risk, r.risk_level, r.risk_rationale, r.verification_rationale, r.status
        ]);
      });
    } else if (kind === 'risks') {
      rows.push(['ID', 'Title', 'P', 'S', 'Initial', 'Residual', 'Status', 'Mitigation']);
      (state.data.risks.risks || []).forEach(function (r) {
        rows.push([r.id, r.title, r.probability, r.severity, r.initial_risk, r.residual_risk, r.status, r.mitigation]);
      });
    } else if (kind === 'rtm-json') {
      downloadBlob(JSON.stringify(state.data.requirements, null, 2), 'requirements.json', 'application/json');
      return;
    }
    var csv = rows.map(function (r) {
      return r.map(function (c) {
        var s = String(c == null ? '' : c);
        return '"' + s.replace(/"/g, '""') + '"';
      }).join(',');
    }).join('\n');
    downloadBlob(csv, kind + '.csv', 'text/csv');
  }

 function downloadBlob(text, name, type) {
 var a = document.createElement('a');
 a.href = URL.createObjectURL(new Blob([text], { type: type }));
 a.download = name;
 a.click();
 URL.revokeObjectURL(a.href);
 }

 function bindDynamic(root) {
 $all('[data-eng-id]', root).forEach(function (btn) {
 btn.addEventListener('click', function (e) {
 e.preventDefault();
 openDetail(btn.getAttribute('data-eng-id'));
 });
 });
 $all('[data-export]', root).forEach(function (btn) {
 btn.addEventListener('click', function () { exportCsv(btn.getAttribute('data-export')); });
 });
 $all('[data-risk-cell]', root).forEach(function (btn) {
 btn.addEventListener('click', function () {
 var ids = (btn.getAttribute('data-risk-cell') || '').split(',').filter(Boolean);
 if (ids[0]) openDetail(ids[0]);
 });
 });
 var ts = $('#eng-trace-select', root);
 if (ts) ts.addEventListener('change', updateTraceGraph);
 $all('[data-fs]', root).forEach(function (btn) {
 btn.addEventListener('click', function () {
 var box = btn.closest('.eng-diagram');
 if (!box) return;
 if (!document.fullscreenElement) box.requestFullscreen && box.requestFullscreen();
 else document.exitFullscreen && document.exitFullscreen();
 });
 });
 }

 function bindChrome() {
 renderLifecycle($('#eng-lifecycle'));
 renderMetrics($('#eng-metrics'));

 $all('#eng-lifecycle button').forEach(function (btn) {
 btn.addEventListener('click', function () {
 $all('#eng-lifecycle button').forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
 btn.setAttribute('aria-pressed', 'true');
 showSection(btn.getAttribute('data-section'));
 var target = $('#sec-' + btn.getAttribute('data-section')) || $('#panel-' + btn.getAttribute('data-section'));
 if (target && target.scrollIntoView) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
 });
 });

 $all('.eng-sidebar a').forEach(function (a) {
 a.addEventListener('click', function (e) {
 e.preventDefault();
 showSection(a.getAttribute('href').replace('#', ''));
 });
 });

 var search = $('#eng-search');
 if (search) {
 search.addEventListener('input', function () {
 state.filters.q = search.value;
 if (search.value.trim()) showSection('search');
 });
 }
 ['eng-filter-status', 'eng-filter-category'].forEach(function (id) {
 var el = $('#' + id);
 if (!el) return;
 el.addEventListener('change', function () {
 if (id.indexOf('status') >= 0) state.filters.status = el.value;
 if (id.indexOf('category') >= 0) state.filters.category = el.value;
 showSection(state.activeSection === 'search' ? 'requirements' : state.activeSection);
 });
 });

 $('#eng-backdrop').addEventListener('click', closeDetail);
 document.addEventListener('keydown', function (e) {
 if (e.key === 'Escape') closeDetail();
 });
 }

 function sectionForType(type) {
 var map = {
 requirement: 'requirements',
 architecture: 'architecture',
 interface: 'interfaces',
 risk: 'risk',
 test: 'tests',
 evidence: 'vv',
 issue: 'issues',
 model: 'models',
 baseline: 'architecture',
 release: 'releases',
 behavioral_model: 'behavioral',
 diagram: 'models-sysml',
 math_trace: 'math',
 dataset: 'analysis'
 };
 return map[type] || 'overview';
 }

 function resolveHash(hash) {
 if (SECTION_RENDERERS[hash]) {
 showSection(hash);
 return;
 }
 if (/^CM-\d{2}$/i.test(hash) || hash === 'runtime-mapping' || hash === 'state-vector' || hash === 'blend' || hash === 'decay' || hash === 'comparison' || hash === 'formula5') {
 showSection('math');
 setTimeout(function () {
 var el = document.getElementById(hash);
 if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
 }, 80);
 return;
 }
 var entry = state.index[hash];
 if (entry) {
 showSection(sectionForType(entry.type));
 openDetail(hash);
 return;
 }
 showSection('overview');
 }

 function boot() {
 var status = $('#eng-load-status');
 Promise.all(FILES.map(function (f) {
 return fetchJson(f).then(function (j) { state.data[f] = j; });
 })).then(function () {
 buildIndex();
 if (status) status.textContent = 'Engineering data loaded · schema ' +
 (state.data.meta.schema_version || '') + ' · audited ' + (state.data.meta.last_audited || '');
 bindChrome();
 resolveHash((location.hash || '#overview').replace('#', ''));
 window.addEventListener('hashchange', function () {
 resolveHash((location.hash || '#overview').replace('#', ''));
 });
 }).catch(function (err) {
 if (status) status.textContent = 'Failed to load engineering data: ' + err.message;
 });
 }

 if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
 else boot();
})();

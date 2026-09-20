/**
 * OtaconsKeep Engineering Portal runtime
 * Loads structured JSON under /data/engineering/ and renders interactive views.
 * Accuracy: never invent PASS / benchmark numbers — compute only from published records.
 */
(function () {
  'use strict';

  var DATA_BASE = '/data/engineering/';
  var FILES = [
    'meta', 'overview', 'requirements', 'architecture', 'interfaces', 'risks',
    'tests', 'evidence', 'benchmarks', 'releases', 'issues', 'models',
    'baselines', 'hardware', 'behavioral_models', 'diagrams'
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
    if (/pending|draft|design|mitigating|monitoring|development|blocked|implemented/.test(s)) return 'warn';
    if (/fail|open|danger|high/.test(s)) return 'bad';
    return 'muted';
  }

  function statusHtml(st) {
    var label = st == null || st === '' ? 'No data' : st;
    return '<span class="eng-status" data-tone="' + toneForStatus(label) + '">' + escapeHtml(label) + '</span>';
  }

  function idBtn(id) {
    if (!id) return '—';
    return '<button type="button" class="eng-id" data-eng-id="' + escapeHtml(id) + '">' + escapeHtml(id) + '</button>';
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
      { label: 'Requirements Verified', value: verified === 0 ? 'Not yet published' : verified },
      { label: 'Requirements Pending', value: pending },
      { label: 'System Tests (register)', value: tests.length },
      { label: 'Tests Passed', value: passed === 0 ? 'Not yet published' : passed },
      { label: 'Tests Failed', value: failed === 0 ? 'Not yet published' : failed },
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

  function renderOverview(root) {
    var o = state.data.overview;
    var nodes = (o.context_nodes || []).map(function (n) {
      return '<li><strong>' + escapeHtml(n.label) + '</strong> <span class="mono" style="color:var(--cream-faint)">(' + escapeHtml(n.kind) + ')</span></li>';
    }).join('');
    root.innerHTML =
      '<p class="intro">' + escapeHtml(o.purpose) + '</p>' +
      '<div class="eng-card-grid">' +
      card('System mission', o.mission) +
      card('Operational concept', o.operational_concept) +
      card('Lite / Premium boundaries', o.lite_premium_boundaries.Lite + ' ' + o.lite_premium_boundaries.Expansion) +
      '</div>' +
      '<h3 style="margin:18px 0 8px;font-size:1rem;">System boundaries</h3>' +
      '<p class="intro"><strong>In scope (public):</strong> ' + escapeHtml((o.system_boundaries.in_scope_public || []).join('; ')) + '</p>' +
      '<p class="intro"><strong>Out of scope / reference:</strong> ' + escapeHtml((o.system_boundaries.out_of_scope_or_reference_only || []).join('; ')) + '</p>' +
      '<h3 style="margin:18px 0 8px;font-size:1rem;">Context actors &amp; externals</h3>' +
      '<ul style="color:var(--cream-dim);font-size:0.92rem;">' + nodes + '</ul>' +
      '<h3 style="margin:18px 0 8px;font-size:1rem;">Assumptions</h3><ul style="color:var(--cream-dim);font-size:0.92rem;">' +
      (o.assumptions || []).map(function (a) { return '<li>' + escapeHtml(a) + '</li>'; }).join('') + '</ul>' +
      '<h3 style="margin:18px 0 8px;font-size:1rem;">Constraints</h3><ul style="color:var(--cream-dim);font-size:0.92rem;">' +
      (o.constraints || []).map(function (a) { return '<li>' + escapeHtml(a) + '</li>'; }).join('') + '</ul>';
  }

  function card(title, body) {
    return '<div class="eng-card" tabindex="0"><h3>' + escapeHtml(title) + '</h3><p>' + escapeHtml(body) + '</p></div>';
  }

  function renderReqTable(root) {
    var rows = (state.data.requirements.requirements || []).filter(function (r) { return matchFilters(r.id + ' ' + r.title, r); });
    if (!rows.length) { root.innerHTML = empty('No requirements match filters.'); return; }
    root.innerHTML = '<div class="eng-table-wrap"><table class="eng-table" aria-label="System requirements">' +
      '<thead><tr><th>ID</th><th>Title</th><th>Category</th><th>Priority</th><th>Status</th><th>Verify</th><th>Subsystem</th></tr></thead><tbody>' +
      rows.map(function (r) {
        return '<tr><td>' + idBtn(r.id) + '</td><td>' + escapeHtml(r.title) + '</td><td>' + escapeHtml(r.category) +
          '</td><td>' + escapeHtml(r.priority) + '</td><td>' + statusHtml(r.status) + '</td><td>' +
          escapeHtml(r.verification_method) + '</td><td>' + idBtn(r.allocated_subsystem) + '</td></tr>';
      }).join('') + '</tbody></table></div>';
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
    var els = state.data.architecture.elements || [];
    root.innerHTML =
      '<p class="intro">Architecture baseline ' + escapeHtml(state.data.architecture.baseline_id) +
      ' — status ' + escapeHtml(state.data.architecture.baseline_status) + '.</p>' +
      '<div class="eng-table-wrap"><table class="eng-table" aria-label="Architecture elements"><thead><tr><th>ID</th><th>Name</th><th>Kind</th><th>Status</th><th>Requirements</th></tr></thead><tbody>' +
      els.map(function (e) {
        return '<tr><td>' + idBtn(e.id) + '</td><td>' + escapeHtml(e.name) + '</td><td>' + escapeHtml(e.kind) +
          '</td><td>' + statusHtml(e.status) + '</td><td>' + (e.linked_requirements || []).map(idBtn).join(' ') + '</td></tr>';
      }).join('') + '</tbody></table></div>' +
      '<div id="eng-diagrams-arch"></div>';
    renderDiagrams($('#eng-diagrams-arch'), ['CTX-001', 'BDD-001', 'IBD-001']);
  }

  function renderDiagrams(root, ids) {
    if (!root) return;
    var diagrams = state.data.diagrams.diagrams || [];
    var list = ids ? diagrams.filter(function (d) { return ids.indexOf(d.id) >= 0; }) : diagrams;
    root.innerHTML = list.map(function (d) {
      return '<div class="eng-diagram" data-diagram="' + escapeHtml(d.id) + '">' +
        '<div class="eng-diagram-toolbar"><strong class="mono" style="flex:1;color:var(--cream-dim);font-size:0.8rem;">' +
        idBtn(d.id) + ' · ' + escapeHtml(d.title) + '</strong>' +
        '<button type="button" data-fs="' + escapeHtml(d.id) + '">Fullscreen</button></div>' +
        '<pre class="mermaid">' + escapeHtml(d.mermaid) + '</pre></div>';
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
    root.innerHTML = '<p class="intro">SysML-style views derived from real subsystems. Steps shown only where implementation exists.</p><div id="eng-sysml-diagrams"></div>';
    renderDiagrams($('#eng-sysml-diagrams'), ['BDD-001', 'IBD-001', 'SEQ-001', 'SEQ-002', 'ACT-001', 'ACT-002', 'ACT-003', 'STM-001', 'STM-002']);
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
      '<p class="intro">Requirements Traceability Matrix — structural links only; Verified status requires evidence.</p>' +
      '<div class="eng-toolbar"><button type="button" class="eng-export" data-export="rtm">Export CSV</button>' +
      '<button type="button" class="eng-export" data-export="rtm-json">Export JSON</button></div>' +
      '<div class="eng-table-wrap"><table class="eng-table" id="eng-rtm" aria-label="Requirements traceability matrix"><thead><tr>' +
      '<th>Requirement ID</th><th>Requirement</th><th>Architecture</th><th>Implementation</th><th>Method</th><th>Test</th><th>Evidence</th><th>Status</th></tr></thead><tbody>' +
      reqs.map(function (r) {
        var tests = r.linked_tests || [];
        var evid = [];
        tests.forEach(function (tid) {
          var t = state.index[tid] && state.index[tid].record;
          if (t && t.evidence) evid = evid.concat(t.evidence);
        });
        return '<tr><td>' + idBtn(r.id) + '</td><td>' + escapeHtml(r.title) + '</td><td>' +
          (r.linked_architecture || []).map(idBtn).join(' ') + '</td><td>' + idBtn(r.allocated_subsystem) +
          '</td><td>' + escapeHtml(r.verification_method) + '</td><td>' + tests.map(idBtn).join(' ') +
          '</td><td>' + (evid.length ? evid.map(idBtn).join(' ') : '—') + '</td><td>' + statusHtml(r.status) + '</td></tr>';
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
    var lines = ['<span class="node">' + escapeHtml(id) + '</span>'];
    (r.linked_architecture || []).forEach(function (a) { lines.push('↓'); lines.push('<span class="node">' + escapeHtml(a) + '</span>'); });
    if (r.allocated_subsystem) { lines.push('↓'); lines.push('<span class="node">' + escapeHtml(r.allocated_subsystem) + '</span> <span style="color:var(--cream-faint)">(component)</span>'); }
    (r.linked_risks || []).forEach(function (a) { lines.push('↓'); lines.push('<span class="node">' + escapeHtml(a) + '</span> <span style="color:var(--cream-faint)">(risk)</span>'); });
    (r.linked_tests || []).forEach(function (a) {
      lines.push('↓');
      lines.push('<span class="node">' + escapeHtml(a) + '</span>');
      var t = state.index[a] && state.index[a].record;
      if (t) {
        lines.push('↓');
        lines.push(statusHtml(t.result));
        (t.evidence || []).forEach(function (e) { lines.push('↓'); lines.push('<span class="node">' + escapeHtml(e) + '</span>'); });
      }
    });
    out.innerHTML = lines.join('<br>');
  }

  function renderVCRM(root) {
    var reqs = state.data.requirements.requirements || [];
    root.innerHTML =
      '<p class="intro">Verification Cross-Reference Matrix. Results reflect published test records only.</p>' +
      '<div class="eng-toolbar"><button type="button" class="eng-export" data-export="vcrm">Export CSV</button></div>' +
      '<div class="eng-table-wrap"><table class="eng-table" aria-label="VCRM"><thead><tr>' +
      '<th>Requirement</th><th>Method</th><th>Level</th><th>Test</th><th>Procedure</th><th>Evidence</th><th>Result</th><th>Build</th><th>Date</th><th>Status</th></tr></thead><tbody>' +
      reqs.map(function (r) {
        var tests = r.linked_tests || [];
        if (!tests.length) {
          return '<tr><td>' + idBtn(r.id) + '</td><td>' + escapeHtml(r.verification_method) +
            '</td><td>—</td><td>—</td><td>—</td><td>—</td><td>' + statusHtml('Verification Pending') +
            '</td><td>—</td><td>—</td><td>' + statusHtml(r.status) + '</td></tr>';
        }
        return tests.map(function (tid) {
          var t = state.index[tid] && state.index[tid].record || {};
          return '<tr><td>' + idBtn(r.id) + '</td><td>' + escapeHtml(r.verification_method) + '</td><td>' +
            escapeHtml(t.class || '—') + '</td><td>' + idBtn(tid) + '</td><td>' + escapeHtml(t.procedure || 'Not yet published') +
            '</td><td>' + ((t.evidence || []).map(idBtn).join(' ') || '—') + '</td><td>' + statusHtml(t.result) +
            '</td><td>' + escapeHtml(t.software_version || '—') + '</td><td>' + escapeHtml(t.execution_date || '—') +
            '</td><td>' + statusHtml(t.result) + '</td></tr>';
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
      '<div class="eng-card"><h3>Validation</h3><p>Did we build the right system? Operational validation and release qualification — not inferred from code existence alone.</p></div>' +
      '</div>' +
      '<p class="intro" style="margin-top:14px;">Verified requirements / total: <strong>' + verified + ' / ' + reqs.length +
      '</strong> (Verified count increases only when status is Verified with evidence — currently none claimed without evidence).</p>' +
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
    var rex = state.data.tests.rex_metrics || {};
    root.innerHTML =
      '<p class="intro">' + escapeHtml(state.data.tests.inventory_note || '') + '</p>' +
      '<div class="eng-empty">REX metrics: ' + escapeHtml(rex.status || 'No data') + ' — ' + escapeHtml(rex.note || '') + '</div>' +
      '<div class="eng-table-wrap" style="margin-top:12px;"><table class="eng-table" aria-label="Test register"><thead><tr>' +
      '<th>ID</th><th>Title</th><th>Class</th><th>Requirements</th><th>Result</th><th>Evidence</th></tr></thead><tbody>' +
      tests.map(function (t) {
        return '<tr><td>' + idBtn(t.id) + '</td><td>' + escapeHtml(t.title) + '</td><td>' + escapeHtml(t.class) +
          '</td><td>' + (t.requirements || []).map(idBtn).join(' ') + '</td><td>' + statusHtml(t.result) +
          '</td><td>' + ((t.evidence || []).map(idBtn).join(' ') || '—') + '</td></tr>';
      }).join('') + '</tbody></table></div>';
  }

  function renderRisks(root) {
    var risks = state.data.risks.risks || [];
    var matrix = '';
    var cells = {};
    risks.forEach(function (r) {
      var p = r.probability || 0, s = r.severity || 0;
      var k = p + ',' + s;
      (cells[k] = cells[k] || []).push(r.id);
    });
    matrix += '<div class="hdr"></div>';
    for (var sev = 1; sev <= 5; sev++) matrix += '<div class="hdr">S' + sev + '</div>';
    for (var p = 5; p >= 1; p--) {
      matrix += '<div class="hdr">P' + p + '</div>';
      for (var s = 1; s <= 5; s++) {
        var ids = cells[p + ',' + s] || [];
        matrix += '<button type="button" class="cell' + (ids.length ? ' has' : '') + '" data-risk-cell="' +
          escapeHtml(ids.join(',')) + '" title="' + escapeHtml(ids.join(', ') || 'empty') + '">' +
          (ids.length || '') + '</button>';
      }
    }
    root.innerHTML =
      '<p class="intro">Probability × severity matrix (1–5). Click a cell to open listed risks.</p>' +
      '<div class="eng-risk-matrix" role="grid" aria-label="Risk matrix">' + matrix + '</div>' +
      '<div class="eng-toolbar" style="margin-top:14px;"><button type="button" class="eng-export" data-export="risks">Export CSV</button></div>' +
      '<div class="eng-table-wrap"><table class="eng-table" aria-label="Risk register"><thead><tr>' +
      '<th>ID</th><th>Title</th><th>P</th><th>S</th><th>Initial</th><th>Residual</th><th>Status</th><th>Mitigation</th></tr></thead><tbody>' +
      risks.map(function (r) {
        return '<tr><td>' + idBtn(r.id) + '</td><td>' + escapeHtml(r.title) + '</td><td>' + r.probability +
          '</td><td>' + r.severity + '</td><td>' + r.initial_risk + '</td><td>' + r.residual_risk +
          '</td><td>' + statusHtml(r.status) + '</td><td>' + escapeHtml(r.mitigation) + '</td></tr>';
      }).join('') + '</tbody></table></div>' +
      '<h3 style="margin:18px 0 8px;font-size:1rem;">Risk mitigation traceability</h3>' +
      '<div class="eng-table-wrap"><table class="eng-table"><thead><tr><th>Risk</th><th>Mitigation</th><th>Requirements</th><th>Tests</th></tr></thead><tbody>' +
      risks.map(function (r) {
        return '<tr><td>' + idBtn(r.id) + '</td><td>' + escapeHtml(r.mitigation) + '</td><td>' +
          (r.linked_requirements || []).map(idBtn).join(' ') + '</td><td>' +
          (r.linked_tests || []).map(idBtn).join(' ') + '</td></tr>';
      }).join('') + '</tbody></table></div>';
  }

  function renderAnalysis(root) {
    root.innerHTML = empty('No dataset available') +
      '<p class="intro" style="margin-top:12px;">Correlation matrices (hardware vs performance, VRAM vs capability, REX closure, etc.) will render here when CSV/JSON ingest lands under data/engineering/ingest/.</p>';
  }

  function renderBenchmarks(root) {
    var b = state.data.benchmarks;
    if (!b.benchmarks || !b.benchmarks.length) {
      root.innerHTML = empty(b.status) +
        '<p class="intro" style="margin-top:10px;">Supported classes (awaiting measured runs): ' +
        escapeHtml((b.classes_supported || []).join(', ')) + '</p>';
      return;
    }
    /* real rows would render here */
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

  function renderBehavioral(root) {
    var bm = state.data.behavioral_models;
    var models = bm.models || [];
    root.innerHTML =
      '<p class="intro">Mathematical behavioral models extracted from runtime source. Equations are implementation-derived — not decorative.</p>' +
      '<p class="intro">Behavior Model <strong class="mono">' + escapeHtml(bm.behavior_model_version) +
      '</strong> · Personality Schema <strong class="mono">' + escapeHtml(bm.personality_schema_version) +
      '</strong> · Relationship <strong class="mono">' + escapeHtml((bm.relationship_model_versions || []).join(' / ')) + '</strong></p>' +
      '<div class="eng-card-grid" style="margin-bottom:16px;">' +
      models.map(function (m) {
        return '<button type="button" class="eng-card" data-eng-id="' + escapeHtml(m.id) + '"><h3>' +
          escapeHtml(m.id) + '</h3><p>' + escapeHtml(m.name) + ' — ' + escapeHtml(m.purpose) + '</p></button>';
      }).join('') + '</div>' +
      renderEmotionTables(bm) +
      renderPersonalityCompare(bm) +
      '<h3 style="margin:18px 0 8px;font-size:1rem;">State traces / sensitivity</h3>' +
      empty((bm.simulation_hooks && bm.simulation_hooks.state_traces) || 'No fabricated traces.');
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
      '<dl>' + Object.keys(r).map(function (k) {
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
    if (kind === 'rtm' || kind === 'vcrm') {
      (state.data.requirements.requirements || []).forEach(function (r) {
        rows.push([r.id, r.title, (r.linked_architecture || []).join('|'), r.allocated_subsystem,
          r.verification_method, (r.linked_tests || []).join('|'), r.status]);
      });
    } else if (kind === 'risks') {
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

  function boot() {
    var status = $('#eng-load-status');
    Promise.all(FILES.map(function (f) {
      return fetchJson(f).then(function (j) { state.data[f] = j; });
    })).then(function () {
      buildIndex();
      if (status) status.textContent = 'Engineering data loaded · schema ' +
        (state.data.meta.schema_version || '') + ' · audited ' + (state.data.meta.last_audited || '');
      bindChrome();
      var hash = (location.hash || '#overview').replace('#', '');
      showSection(SECTION_RENDERERS[hash] ? hash : 'overview');
    }).catch(function (err) {
      if (status) status.textContent = 'Failed to load engineering data: ' + err.message;
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();

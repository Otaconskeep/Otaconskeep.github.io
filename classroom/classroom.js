(function () {
  'use strict';

  var OS_KEY = 'otaconskeep-classroom-os';
  var CHECK_KEY = 'otaconskeep-classroom-checks';

  function getOS() {
    try { return localStorage.getItem(OS_KEY) || 'linux'; } catch (e) { return 'linux'; }
  }
  function setOS(os) {
    try { localStorage.setItem(OS_KEY, os); } catch (e) {}
    applyOS(os);
  }
  function applyOS(os) {
    document.querySelectorAll('.cr-osbar button').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-os') === os ? 'true' : 'false');
    });
    document.querySelectorAll('.cr-os-block').forEach(function (el) {
      var show = el.getAttribute('data-os') === os || el.getAttribute('data-os') === 'both';
      el.classList.toggle('active', show);
    });
    document.documentElement.setAttribute('data-classroom-os', os);
  }

  function loadChecks() {
    try { return JSON.parse(localStorage.getItem(CHECK_KEY) || '{}'); } catch (e) { return {}; }
  }
  function saveChecks(map) {
    try { localStorage.setItem(CHECK_KEY, JSON.stringify(map)); } catch (e) {}
  }

  function initCheckpoints() {
    var map = loadChecks();
    document.querySelectorAll('.cr-check').forEach(function (box) {
      var id = box.getAttribute('data-check-id');
      if (!id) return;
      var gate = box.querySelector('.cr-gate');
      var inputs = box.querySelectorAll('input[type="checkbox"]');
      function refresh() {
        var all = true;
        var state = map[id] || {};
        inputs.forEach(function (inp, i) {
          var key = inp.getAttribute('data-k') || String(i);
          if (state[key]) inp.checked = true;
          if (!inp.checked) all = false;
        });
        if (gate) gate.classList.toggle('ready', all);
      }
      inputs.forEach(function (inp, i) {
        inp.addEventListener('change', function () {
          var key = inp.getAttribute('data-k') || String(i);
          map[id] = map[id] || {};
          map[id][key] = inp.checked;
          saveChecks(map);
          refresh();
        });
      });
      refresh();
    });
  }

  function closestHelp(el) {
    while (el && el !== document) {
      if (el.classList && el.classList.contains('cr-help')) return el;
      el = el.parentNode;
    }
    return null;
  }

  document.addEventListener('click', function (e) {
    var osBtn = e.target.closest && e.target.closest('.cr-osbar button[data-os]');
    if (osBtn) {
      setOS(osBtn.getAttribute('data-os'));
      return;
    }
    var pathCard = e.target.closest && e.target.closest('[data-set-os]');
    if (pathCard) {
      setOS(pathCard.getAttribute('data-set-os'));
    }
    var btn = e.target.closest && e.target.closest('.cr-btn[data-cr]');
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    var help = closestHelp(btn);
    if (!help) return;
    var kind = btn.getAttribute('data-cr');
    var panel = help.querySelector('.cr-panel.' + (kind === 'mean' ? 'mean' : 'more'));
    if (!panel) return;
    var open = btn.getAttribute('aria-expanded') === 'true';
    help.querySelectorAll('.cr-btn[data-cr]').forEach(function (b) {
      if (b !== btn) b.setAttribute('aria-expanded', 'false');
    });
    help.querySelectorAll('.cr-panel').forEach(function (p) {
      if (p !== panel) p.hidden = true;
    });
    btn.setAttribute('aria-expanded', open ? 'false' : 'true');
    panel.hidden = open;
  });

  var toggle = document.querySelector('.navtoggle');
  var links = document.querySelector('.navlinks');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }


  var FEYN_KEY = 'otaconskeep-classroom-feynman';

  function loadFeynman() {
    try { return JSON.parse(localStorage.getItem(FEYN_KEY) || '{}'); } catch (e) { return {}; }
  }
  function saveFeynman(map) {
    try { localStorage.setItem(FEYN_KEY, JSON.stringify(map)); } catch (e) {}
  }

  function initFeynman() {
    var map = loadFeynman();
    document.querySelectorAll('textarea[data-feynman-id]').forEach(function (ta) {
      var id = ta.getAttribute('data-feynman-id');
      var field = ta.getAttribute('data-feynman-field');
      if (!id || !field) return;
      if (map[id] && map[id][field]) ta.value = map[id][field];
      ta.addEventListener('input', function () {
        map[id] = map[id] || {};
        map[id][field] = ta.value;
        saveFeynman(map);
        refreshFeynmanGate(id, map);
      });
      refreshFeynmanGate(id, map);
    });
  }

  function refreshFeynmanGate(id, map) {
    var fields = ['explain', 'simplify', 'example', 'weak', 'retry'];
    var done = fields.every(function (f) {
      return map[id] && String(map[id][f] || '').trim().length >= 12;
    });
    document.querySelectorAll('.cr-box-feynman').forEach(function (box) {
      box.classList.toggle('ready', done);
    });
    var note = document.querySelector('.cr-feynman-note');
    if (note) {
      note.textContent = done
        ? 'Feynman teach-back complete in this browser. Finish the practical gate checkboxes next.'
        : 'Answers save in this browser (localStorage). Completing all five fields is part of the mastery unlock.';
    }
  }

  applyOS(getOS());
  initCheckpoints();
  initFeynman();
})();

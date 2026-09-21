(function () {
  'use strict';

  function closestStep(el) {
    while (el && el !== document) {
      if (el.classList && el.classList.contains('cr-step')) return el;
      el = el.parentNode;
    }
    return null;
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('.cr-btn[data-cr]');
    if (!btn) return;
    var step = closestStep(btn);
    if (!step) return;
    var kind = btn.getAttribute('data-cr');
    var panel = step.querySelector('.cr-panel.' + (kind === 'mean' ? 'mean' : 'more'));
    if (!panel) return;
    var open = btn.getAttribute('aria-expanded') === 'true';
    // close sibling panel of other kind in same step
    step.querySelectorAll('.cr-btn[data-cr]').forEach(function (b) {
      if (b === btn) return;
      b.setAttribute('aria-expanded', 'false');
    });
    step.querySelectorAll('.cr-panel').forEach(function (p) {
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
})();

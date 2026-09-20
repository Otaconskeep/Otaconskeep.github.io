/* Keep Desk Install Vault — reuses OtaconsPremium seat table (BMC licenses) */
(function () {
  'use strict';

  var STORAGE_UNLOCK = 'otaconskeep_keepdesk_unlocked';
  var STORAGE_USER = 'otaconskeep_keepdesk_user';
  // Also honor premium unlock on same browser
  var PREMIUM_UNLOCK = 'otaconskeep_premium_unlocked';
  var PREMIUM_USER = 'otaconskeep_premium_user';

  function $(id) { return document.getElementById(id); }

  function sha256(text) {
    var data = new TextEncoder().encode(text);
    return crypto.subtle.digest('SHA-256', data).then(function (buf) {
      return Array.from(new Uint8Array(buf)).map(function (b) {
        return b.toString(16).padStart(2, '0');
      }).join('');
    });
  }

  function registry() {
    var P = window.OtaconsPremium || {};
    return {
      build: P.GATE_BUILD || 'dev',
      users: P.USERS || {},
      licenses: P.LICENSES || {}
    };
  }

  function reveal(username, opts) {
    opts = opts || {};
    var locked = $('kd-locked');
    var unlocked = $('kd-unlocked');
    if (locked) locked.hidden = true;
    if (unlocked) unlocked.hidden = false;

    var reg = registry();
    var lic = reg.licenses[username] || reg.licenses[(username || '').toUpperCase()] || {};
    var name = lic.displayName || username || 'Operator';

    var welcome = $('kd-welcome');
    var thanks = $('kd-thanks');
    if (welcome) welcome.textContent = 'Welcome, ' + name + '.';
    if (thanks) thanks.textContent = 'Seat active. Install dossier unlocked. Thank you for funding the Keep.';

    if ($('kd-lic-name')) $('kd-lic-name').textContent = username || '—';
    if ($('kd-lic-id')) $('kd-lic-id').textContent = lic.licenseId || '—';
    if ($('kd-lic-tier')) $('kd-lic-tier').textContent = lic.tier || 'supporter';
    if ($('kd-lic-pay')) $('kd-lic-pay').textContent = lic.paymentRef || 'BMC';
    if ($('kd-lic-status')) $('kd-lic-status').textContent = (lic.status || 'active').toUpperCase();

    try {
      sessionStorage.setItem(STORAGE_UNLOCK, '1');
      sessionStorage.setItem(STORAGE_USER, username || '');
    } catch (e) {}

    if (opts.scroll !== false) {
      var vault = $('vault');
      if (vault) vault.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function lockVault() {
    var locked = $('kd-locked');
    var unlocked = $('kd-unlocked');
    if (locked) locked.hidden = false;
    if (unlocked) unlocked.hidden = true;
    try {
      sessionStorage.removeItem(STORAGE_UNLOCK);
      sessionStorage.removeItem(STORAGE_USER);
    } catch (e) {}
  }

  function tryUnlock(name, password, pin) {
    var reg = registry();
    var key = (name || '').trim().toUpperCase();
    var user = reg.users[key];
    if (!user) {
      return Promise.resolve({ ok: false, error: 'Unknown access name (build ' + reg.build + ').' });
    }

    var checks = [];
    if (password) {
      checks.push(sha256(password).then(function (h) {
        return (user.pwHashes || []).indexOf(h) !== -1;
      }));
    }
    if (pin) {
      checks.push(sha256(key + ':' + pin).then(function (h) {
        return h === user.pinHash;
      }));
    }
    if (!checks.length) {
      return Promise.resolve({ ok: false, error: 'Enter password and/or PIN.' });
    }

    return Promise.all(checks).then(function (results) {
      if (results.some(Boolean)) return { ok: true, user: key };
      return { ok: false, error: 'Incorrect credentials (build ' + reg.build + ').' };
    });
  }

  function boot() {
    var reg = registry();
    var buildEl = $('kd-gate-build');
    if (buildEl) buildEl.textContent = reg.build;

    var form = $('kd-gate-form');
    var err = $('kd-gate-error');
    var lockBtn = $('kd-lock-btn');

    if (lockBtn) lockBtn.addEventListener('click', lockVault);

    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (err) err.textContent = '';
        var name = ($('kd-gate-name') || {}).value || '';
        var pw = ($('kd-gate-pw') || {}).value || '';
        var pin = ($('kd-gate-pin') || {}).value || '';
        tryUnlock(name, pw, pin).then(function (res) {
          if (!res.ok) {
            if (err) err.textContent = res.error || 'Denied.';
            return;
          }
          reveal(res.user, { scroll: true });
        }).catch(function () {
          if (err) err.textContent = 'Gate error — try again.';
        });
      });
    }

    try {
      if (sessionStorage.getItem(STORAGE_UNLOCK) === '1') {
        reveal(sessionStorage.getItem(STORAGE_USER) || '', { scroll: false });
        return;
      }
      // Premium unlock on same device also opens Keep Desk vault
      if (sessionStorage.getItem(PREMIUM_UNLOCK) === '1') {
        reveal(sessionStorage.getItem(PREMIUM_USER) || '', { scroll: false });
      }
    } catch (e) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

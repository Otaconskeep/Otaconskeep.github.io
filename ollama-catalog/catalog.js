(function () {
  var HEADROOM = 0.75;
  var state = {
    view: "tags",
    query: "",
    capabilities: [],
    budget: 16,
    contextMin: 0,
    localOnly: true,
    sort: "sizeGB",
    asc: true,
    page: 1,
    family: ""
  };
  var pageSize = 60;
  var snapshot = null;
  var evidence = null;

  function $(id) { return document.getElementById(id); }
  function num(value) { return Number(value).toLocaleString(); }

  function fits(variant, budget) {
    if (!budget) return true;
    if (variant.cloud) return false;
    if (variant.sizeGB == null || !isFinite(variant.sizeGB)) return false;
    return variant.sizeGB <= budget * HEADROOM;
  }

  function allVariants() {
    var rows = [];
    (snapshot.models || []).forEach(function (model) {
      (model.variants || []).forEach(function (variant) {
        rows.push(Object.assign({}, variant, {
          family: model.name,
          description: model.description,
          capabilities: model.capabilities || [],
          pulls: model.pulls,
          updatedAt: model.updatedAt
        }));
      });
    });
    return rows;
  }

  function capabilityOptions() {
    var set = {};
    (snapshot.models || []).forEach(function (model) {
      (model.capabilities || []).forEach(function (cap) { set[cap] = true; });
    });
    return Object.keys(set).sort();
  }

  function wordsOk(text) {
    var words = state.query.toLowerCase().trim().split(/\s+/).filter(Boolean);
    var hay = text.toLowerCase();
    return words.every(function (word) { return hay.indexOf(word) !== -1; });
  }

  function filtered() {
    if (state.view === "families") {
      return (snapshot.models || []).filter(function (model) {
        if (state.capabilities.length && !state.capabilities.some(function (cap) {
          return (model.capabilities || []).indexOf(cap) !== -1;
        })) return false;
        if (state.budget) {
          var any = (model.variants || []).some(function (variant) { return fits(variant, state.budget); });
          if (!any) return false;
        }
        if (state.localOnly && (model.variants || []).length && !(model.variants || []).some(function (variant) { return !variant.cloud; })) {
          return false;
        }
        return wordsOk([model.name, model.description].concat(model.capabilities || [], model.sizes || []).join(" "));
      });
    }
    return allVariants().filter(function (row) {
      if (state.family && row.family !== state.family) return false;
      if (state.localOnly && row.cloud) return false;
      if (state.capabilities.length && !state.capabilities.some(function (cap) {
        return row.capabilities.indexOf(cap) !== -1;
      })) return false;
      if (!fits(row, state.budget)) return false;
      if (state.contextMin && !(row.contextTokens != null && row.contextTokens >= state.contextMin)) return false;
      return wordsOk([row.name, row.family, row.description, row.quantHint, row.inputLabel].concat(row.capabilities).join(" "));
    });
  }

  function sortRows(rows) {
    var key = state.sort;
    var dir = state.asc ? 1 : -1;
    return rows.slice().sort(function (a, b) {
      var x = a[key];
      var y = b[key];
      if (x == null && y == null) return String(a.name).localeCompare(String(b.name));
      if (x == null) return 1;
      if (y == null) return -1;
      var result = typeof x === "number" ? x - y : String(x).localeCompare(String(y), undefined, { numeric: true });
      return result * dir || String(a.name).localeCompare(String(b.name));
    });
  }

  function badge(cap) {
    return '<span class="oc-badge oc-' + cap.replace(/[^a-z0-9_-]/gi, "") + '">' + cap + "</span>";
  }

  function renderTable(rows) {
    var pageCount = Math.max(1, Math.ceil(rows.length / pageSize));
    if (state.page > pageCount) state.page = pageCount;
    var start = (state.page - 1) * pageSize;
    var pageRows = rows.slice(start, start + pageSize);
    var html = "";
    if (state.view === "families") {
      html += "<table><thead><tr>" +
        sortHead("name", "Model") +
        "<th>Description</th><th>Capabilities</th><th>Listed sizes</th>" +
        sortHead("pulls", "Pulls") +
        sortHead("tagCountListed", "Tags") +
        sortHead("updatedAt", "Updated") +
        "</tr></thead><tbody>";
      pageRows.forEach(function (model) {
        var caps = (model.capabilities || []).map(badge).join("") || '<span class="oc-muted">—</span>';
        html += "<tr><td><a href=\"" + model.url + "\" target=\"_blank\" rel=\"noopener\">" + model.name + "</a></td>" +
          "<td class=\"oc-desc\">" + escapeHtml(model.description || "") + "</td>" +
          "<td>" + caps + "</td>" +
          "<td>" + escapeHtml((model.sizes || []).join(" · ") || "—") + "</td>" +
          "<td class=\"oc-num\">" + escapeHtml(model.pullsLabel) + "</td>" +
          "<td><button type=\"button\" class=\"oc-link\" data-family=\"" + escapeHtml(model.name) + "\">" + (model.variants || []).length + "</button></td>" +
          "<td class=\"oc-num\">" + (model.updatedAt || "").slice(0, 10) + "</td></tr>";
      });
    } else {
      html += "<table><thead><tr>" +
        sortHead("name", "Model : tag") +
        "<th>Capabilities</th>" +
        sortHead("sizeGB", "Download") +
        sortHead("contextTokens", "Context") +
        "<th>Input</th>" +
        sortHead("quantHint", "Quant hint") +
        "<th>Pull</th></tr></thead><tbody>";
      pageRows.forEach(function (row) {
        var caps = row.capabilities.map(badge).join("") || '<span class="oc-muted">—</span>';
        html += "<tr><td><a href=\"" + row.url + "\" target=\"_blank\" rel=\"noopener\">" + escapeHtml(row.name) + "</a></td>" +
          "<td>" + caps + "</td>" +
          "<td class=\"oc-num\">" + escapeHtml(row.sizeLabel || "—") + "</td>" +
          "<td class=\"oc-num\">" + escapeHtml(row.contextLabel || "—") + "</td>" +
          "<td>" + escapeHtml(row.inputLabel || "—") + "</td>" +
          "<td>" + escapeHtml(row.quantHint || "—") + "</td>" +
          "<td><button type=\"button\" class=\"oc-link\" data-copy=\"" + escapeHtml(row.pullCommand) + "\">Copy</button></td></tr>";
      });
    }
    html += "</tbody></table>";
    if (!rows.length) html += '<p class="oc-empty">Nothing matches. Clear a filter or raise the VRAM budget.</p>';
    $("oc-table").innerHTML = html;
    var from = rows.length ? start + 1 : 0;
    var to = Math.min(start + pageSize, rows.length);
    $("oc-count").textContent = num(rows.length) + " shown · " + from + "–" + to;
    $("oc-page").textContent = "Page " + state.page + " of " + pageCount;
    $("oc-prev").disabled = state.page <= 1;
    $("oc-next").disabled = state.page >= pageCount;
  }

  function sortHead(key, label) {
    var mark = state.sort === key ? (state.asc ? " ↑" : " ↓") : "";
    return '<th><button type="button" class="oc-sort" data-sort="' + key + '">' + label + mark + "</button></th>";
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderEvidence() {
    var failures = (evidence.tagPageFailures || []).length;
    var checks = [];
    ["8", "12", "16", "24", "32"].forEach(function (budget) {
      var expected = evidence.vramFit && evidence.vramFit[budget] && evidence.vramFit[budget].matchingTags;
      var actual = 0;
      (snapshot.models || []).forEach(function (model) {
        (model.variants || []).forEach(function (variant) {
          if (fits(variant, Number(budget))) actual += 1;
        });
      });
      checks.push({ budget: budget, expected: expected, actual: actual, ok: expected === actual });
    });
    var ok = checks.every(function (row) { return row.ok; }) && failures === 0 && evidence.libraryHttp === 200;
    $("oc-evidence").className = "oc-evidence" + (ok ? " is-ok" : " is-bad");
    var fitLine = checks.map(function (row) {
      return row.budget + "GB " + num(row.actual) + (row.ok ? "" : " (evidence " + row.expected + ")");
    }).join(" · ");
    $("oc-evidence").innerHTML =
      "<p><strong>" + (ok ? "Evidence checks match this snapshot." : "Evidence check failed. Do not trust the filters until this is re-scraped.") + "</strong></p>" +
      "<p>Source <a href=\"" + evidence.source + "\" target=\"_blank\" rel=\"noopener\">" + evidence.source + "</a>" +
      " · HTTP " + evidence.libraryHttp +
      " · " + num(evidence.libraryBytes) + " bytes" +
      " · sha256 " + String(evidence.librarySha256 || "").slice(0, 16) + "…" +
      " · fetched " + evidence.fetchedAt + "</p>" +
      "<p>" + num(evidence.familyCount) + " families · " + num(evidence.variantCount) + " tags · " +
      evidence.tagPagesOk + " tag pages OK · " + failures + " failures · parser " + evidence.parser + "</p>" +
      "<p>VRAM shortlist (listed download ≤ 75% of budget, cloud excluded): " + fitLine + "</p>" +
      "<p class=\"oc-muted\">" + escapeHtml(evidence.rules.vramFit) + "</p>";
  }

  function renderChips() {
    var host = $("oc-caps");
    host.innerHTML = "";
    capabilityOptions().forEach(function (cap) {
      var button = document.createElement("button");
      button.type = "button";
      button.className = "oc-chip" + (state.capabilities.indexOf(cap) !== -1 ? " is-on" : "");
      button.textContent = cap;
      button.addEventListener("click", function () {
        var index = state.capabilities.indexOf(cap);
        if (index === -1) state.capabilities.push(cap);
        else state.capabilities.splice(index, 1);
        state.page = 1;
        draw();
      });
      host.appendChild(button);
    });
  }

  function draw() {
    renderChips();
    document.querySelectorAll("[data-budget]").forEach(function (button) {
      button.classList.toggle("is-on", Number(button.getAttribute("data-budget")) === state.budget);
    });
    document.querySelectorAll("[data-view]").forEach(function (button) {
      button.classList.toggle("is-on", button.getAttribute("data-view") === state.view);
    });
    $("oc-local").checked = state.localOnly;
    renderTable(sortRows(filtered()));
  }

  function bind() {
    $("oc-search").addEventListener("input", function (event) {
      state.query = event.target.value;
      state.family = "";
      state.page = 1;
      draw();
    });
    document.querySelectorAll("[data-view]").forEach(function (button) {
      button.addEventListener("click", function () {
        state.view = button.getAttribute("data-view");
        state.sort = state.view === "families" ? "pulls" : "sizeGB";
        state.asc = state.view !== "families";
        state.page = 1;
        draw();
      });
    });
    document.querySelectorAll("[data-budget]").forEach(function (button) {
      button.addEventListener("click", function () {
        var next = Number(button.getAttribute("data-budget"));
        state.budget = state.budget === next ? 0 : next;
        state.page = 1;
        draw();
      });
    });
    $("oc-context").addEventListener("change", function (event) {
      state.contextMin = Number(event.target.value) || 0;
      state.page = 1;
      draw();
    });
    $("oc-local").addEventListener("change", function (event) {
      state.localOnly = event.target.checked;
      state.page = 1;
      draw();
    });
    $("oc-reset").addEventListener("click", function () {
      state.query = "";
      state.capabilities = [];
      state.budget = 16;
      state.contextMin = 0;
      state.localOnly = true;
      state.family = "";
      state.page = 1;
      state.view = "tags";
      state.sort = "sizeGB";
      state.asc = true;
      $("oc-search").value = "";
      $("oc-context").value = "0";
      draw();
    });
    $("oc-prev").addEventListener("click", function () { state.page -= 1; draw(); });
    $("oc-next").addEventListener("click", function () { state.page += 1; draw(); });
    $("oc-table").addEventListener("click", function (event) {
      var sort = event.target.closest("[data-sort]");
      if (sort) {
        var key = sort.getAttribute("data-sort");
        state.asc = state.sort === key ? !state.asc : key === "name";
        state.sort = key;
        draw();
        return;
      }
      var family = event.target.closest("[data-family]");
      if (family) {
        state.family = family.getAttribute("data-family");
        state.view = "tags";
        state.sort = "sizeGB";
        state.asc = true;
        state.page = 1;
        $("oc-search").value = state.family;
        state.query = state.family;
        draw();
        return;
      }
      var copy = event.target.closest("[data-copy]");
      if (copy && navigator.clipboard) {
        navigator.clipboard.writeText(copy.getAttribute("data-copy"));
        copy.textContent = "Copied";
      }
    });
  }

  Promise.all([
    fetch("data/models.json").then(function (response) { if (!response.ok) throw new Error("models HTTP " + response.status); return response.json(); }),
    fetch("data/evidence.json").then(function (response) { if (!response.ok) throw new Error("evidence HTTP " + response.status); return response.json(); })
  ]).then(function (pair) {
    snapshot = pair[0];
    evidence = pair[1];
    if (snapshot.fetchedAt !== evidence.fetchedAt) {
      throw new Error("models.json and evidence.json timestamps differ");
    }
    $("oc-status").textContent = num(snapshot.count) + " families · " + num(snapshot.variantCount) + " tags";
    renderEvidence();
    bind();
    draw();
  }).catch(function (error) {
    $("oc-status").textContent = "Catalog failed to load";
    $("oc-evidence").className = "oc-evidence is-bad";
    $("oc-evidence").textContent = error.message;
  });
})();

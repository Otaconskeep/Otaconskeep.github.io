(() => {
  const $ = (s) => document.querySelector(s);
  let meta = null;
  let guides = null;
  let selected = "auto";
  let currentMission = null;
  let abortCtrl = null;
  let streamEl = null;
  let lastRouted = null;

  const termOut = $("#termOut");
  const agentList = $("#agentList");
  const authForm = $("#authForm");
  const runBtn = $("#runBtn");
  const abortBtn = $("#abortBtn");
  const authMsg = $("#authMsg");
  const linkBadge = $("#linkBadge");
  const activeName = $("#activeName");
  const missionStatus = $("#missionStatus");
  const termAgent = $("#termAgent");
  const emptyProviders = $("#emptyProviders");

  function bootLine(text, kind = "sys") {
    streamEl = null;
    const line = document.createElement("div");
    line.className = kind;
    line.textContent = text;
    termOut.appendChild(line);
    termOut.scrollTop = termOut.scrollHeight;
  }

  function appendStream(text) {
    if (!streamEl) {
      streamEl = document.createElement("div");
      streamEl.className = "stream";
      termOut.appendChild(streamEl);
    }
    streamEl.textContent += text;
    termOut.scrollTop = termOut.scrollHeight;
  }

  function clearTerm() {
    termOut.innerHTML = "";
    streamEl = null;
  }

  function setBusy(on) {
    runBtn.disabled = on;
    const spin = runBtn.querySelector(".btn-spin");
    if (spin) spin.hidden = !on;
    abortBtn.disabled = !on;
  }

  function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.hidden = false;
  }
  function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.hidden = true;
  }

  document.querySelectorAll("[data-close]").forEach((btn) => {
    btn.addEventListener("click", () => closeModal(btn.dataset.close));
  });
  document.querySelectorAll(".modal").forEach((m) => {
    m.addEventListener("click", (e) => {
      if (e.target === m) m.hidden = true;
    });
  });

  /* Matrix rain — slowed down */
  (function rain() {
    const canvas = $("#rain");
    const ctx = canvas.getContext("2d");
    let w, h, cols, drops;
    const chars = "ｱｲｳｴｵｶｷｸｹｺ0123456789KEEPROUTE".split("");
    let last = 0;
    const FRAME_MS = 70; // slower than ~16ms

    function resize() {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
      cols = Math.floor(w / 18);
      drops = Array.from({ length: cols }, () => Math.random() * -40);
    }
    resize();
    window.addEventListener("resize", resize);

    function frame(ts) {
      requestAnimationFrame(frame);
      if (ts - last < FRAME_MS) return;
      last = ts;
      ctx.fillStyle = "rgba(2, 8, 6, 0.12)";
      ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = "#00ff88";
      ctx.font = "13px Share Tech Mono, monospace";
      for (let i = 0; i < drops.length; i++) {
        if (Math.random() > 0.65) continue; // fewer glyphs per frame
        ctx.globalAlpha = 0.55;
        ctx.fillText(chars[(Math.random() * chars.length) | 0], i * 18, drops[i] * 18);
        ctx.globalAlpha = 1;
        if (drops[i] * 18 > h && Math.random() > 0.985) drops[i] = 0;
        drops[i] += 0.45; // slower fall
      }
    }
    requestAnimationFrame(frame);
  })();

  function tick() {
    $("#clock").textContent = new Date().toISOString().slice(11, 19) + "Z";
  }
  tick();
  setInterval(tick, 1000);

  function renderAgents() {
    agentList.innerHTML = "";
    const agents = meta?.agents || {};
    const keys = Object.keys(agents);
    emptyProviders.hidden = keys.length > 0;

    // Prefer Auto first, then alphabetical by label
    keys.sort((a, b) => {
      if (a === "auto") return -1;
      if (b === "auto") return 1;
      return (agents[a].label || a).localeCompare(agents[b].label || b);
    });

    if (selected && !agents[selected]) {
      selected = agents.auto ? "auto" : keys[0] || "auto";
    }

    for (const key of keys) {
      const a = agents[key];
      const routed = lastRouted === key || a.routed;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className =
        "provider-row" +
        (key === selected ? " is-on" : "") +
        (a.default ? " is-default" : "");
      btn.innerHTML = `
        <span class="pname">${a.label}</span>
        <span class="lights">
          <span title="Connected or not"><i class="light ${a.connected ? "on" : ""}"></i> Status</span>
          <span title="Used for the last job"><i class="light route ${routed ? "on" : ""}"></i> Routed</span>
        </span>
        <span class="pblurb">${a.blurb || a.hint || ""}</span>`;
      btn.addEventListener("click", () => {
        selected = key;
        activeName.textContent = a.label;
        termAgent.textContent = a.label;
        missionStatus.textContent = a.default ? "AUTO READY" : "SELECTED";
        renderAgents();
        bootLine(`> Selected: ${a.label}`, "sys");
      });
      agentList.appendChild(btn);
    }

    if (agents[selected]) {
      activeName.textContent = agents[selected].label;
      termAgent.textContent = agents[selected].label;
    }
  }

  function renderHow() {
    const h = guides?.how_it_works;
    if (!h) return;
    $("#howTitle").textContent = h.title;
    const body = $("#howBody");
    body.innerHTML = "";
    if (h.intro) {
      const intro = document.createElement("p");
      intro.className = "how-intro";
      intro.textContent = h.intro;
      body.appendChild(intro);
    }
    if (h.emphasis) {
      const em = document.createElement("p");
      em.className = "how-emphasis";
      em.textContent = h.emphasis;
      body.appendChild(em);
    }
    for (const s of h.steps || []) {
      const el = document.createElement("div");
      el.className = "how-step";
      el.innerHTML = `<div class="how-n">${s.n}</div><div><h3>${s.title}</h3><p>${s.body}</p></div>`;
      body.appendChild(el);
    }
  }

  function renderFaq() {
    const body = $("#faqBody");
    body.innerHTML = "";
    for (const item of guides?.faq || []) {
      const el = document.createElement("div");
      el.className = "faq-item";
      el.innerHTML = `<h3>${item.q}</h3><p>${item.a}</p>`;
      body.appendChild(el);
    }
  }

  function showProvider(id) {
    const list = guides?.providers || [];
    const p = list.find((x) => x.id === id) || list[0];
    if (!p) return;
    document.querySelectorAll("#providerTabs button").forEach((b) => {
      b.classList.toggle("is-on", b.dataset.id === p.id);
    });
    $("#providerBody").innerHTML = `
      <div class="provider-guide">
        <h3>${p.title}</h3>
        <p class="summary">${p.summary}</p>
        <ol>${p.steps.map((s) => `<li>${s}</li>`).join("")}</ol>
      </div>`;
  }

  function renderProviderTabs() {
    const tabs = $("#providerTabs");
    tabs.innerHTML = "";
    for (const p of guides?.providers || []) {
      const b = document.createElement("button");
      b.type = "button";
      b.dataset.id = p.id;
      b.textContent = p.title.split("(")[0].trim();
      b.addEventListener("click", () => showProvider(p.id));
      tabs.appendChild(b);
    }
    if (guides?.providers?.[0]) showProvider(guides.providers[0].id);
  }

  $("#howBtn").addEventListener("click", () => {
    renderHow();
    openModal("howModal");
  });
  $("#confusedBtn").addEventListener("click", () => {
    closeModal("howModal");
    renderFaq();
    openModal("faqModal");
  });
  $("#faqToHow").addEventListener("click", () => {
    closeModal("faqModal");
    renderHow();
    openModal("howModal");
  });
  $("#providersBtn").addEventListener("click", async () => {
    renderProviderTabs();
    await loadAuth();
    openModal("providersModal");
  });

  async function loadAuth() {
    const r = await fetch("/api/auth");
    const d = await r.json();
    authForm.innerHTML = "";
    for (const f of d.fields || []) {
      const wrap = document.createElement("div");
      wrap.className = "field";
      const ph =
        f.configured && f.secret ? `saved: ${f.masked}` : f.placeholder || "";
      wrap.innerHTML = `
        <label for="f-${f.id}">${f.label}</label>
        <input id="f-${f.id}" name="${f.id}" type="${f.secret ? "password" : "text"}"
          placeholder="${ph}" autocomplete="off" spellcheck="false"
          ${!f.secret && f.value ? `value="${String(f.value).replace(/"/g, "&quot;")}"` : ""} />
        <p class="help">${f.help || ""}</p>
        ${f.configured ? `<p class="configured">● SAVED</p>` : ""}`;
      authForm.appendChild(wrap);
    }
  }

  async function refreshStatus() {
    try {
      const r = await fetch("/api/status");
      const d = await r.json();
      if (d.health?.ok) {
        linkBadge.textContent = "OMNIROUTE ONLINE";
        linkBadge.className = "badge ok";
      } else {
        linkBadge.textContent = "OMNIROUTE OFFLINE";
        linkBadge.className = "badge bad";
      }
      if (d.last_routed?.agent) lastRouted = d.last_routed.agent;
      if (d.agents) {
        // merge live connected/routed into meta if present
        if (meta?.agents) {
          for (const [k, v] of Object.entries(d.agents)) {
            if (meta.agents[k]) {
              meta.agents[k].connected = v.connected;
              meta.agents[k].routed = v.routed;
            }
          }
          renderAgents();
        }
      }
    } catch {
      linkBadge.textContent = "KEEPROUTE LOCAL";
      linkBadge.className = "badge dim";
    }
  }

  $("#saveAuth").addEventListener("click", async () => {
    const body = {};
    authForm.querySelectorAll("input").forEach((inp) => {
      if (inp.value.trim()) body[inp.name] = inp.value.trim();
    });
    if (!Object.keys(body).length) {
      authMsg.hidden = false;
      authMsg.textContent = "Paste a key first, then save.";
      return;
    }
    const r = await fetch("/api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const d = await r.json();
    authMsg.hidden = false;
    authMsg.textContent = d.ok ? `Saved: ${d.saved.join(", ")}` : d.error || "Save failed";
    authForm.querySelectorAll('input[type="password"]').forEach((i) => {
      i.value = "";
    });
    await loadAuth();
    meta = await (await fetch("/api/meta")).json();
    renderAgents();
    bootLine("> Keys saved. Providers list refreshed.", "sys");
  });

  async function runMission() {
    const prompt = $("#promptInput").value.trim();
    if (!prompt) {
      bootLine("> Type what you want in the box first.", "err");
      return;
    }
    setBusy(true);
    missionStatus.textContent = "WORKING…";
    clearTerm();
    bootLine("Sending to OmniRoute…", "sys");
    if (selected === "auto") {
      bootLine("Auto is on — OmniRoute will pick the best provider for this job.", "sys");
    }

    try {
      const r = await fetch("/api/mission", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent: selected, prompt }),
      });
      const d = await r.json();
      if (!d.ok) {
        bootLine(d.error || "Something went wrong", "err");
        missionStatus.textContent = "FAILED";
        setBusy(false);
        return;
      }
      currentMission = d.mission_id;
      const label = meta?.agents?.[d.agent]?.label || d.agent;
      missionStatus.textContent = "LIVE";
      activeName.textContent = label;
      termAgent.textContent = label;

      abortCtrl = new AbortController();
      const es = await fetch(d.stream, { signal: abortCtrl.signal });
      const reader = es.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const parts = buf.split("\n\n");
        buf = parts.pop() || "";
        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith("data:")) continue;
          let payload;
          try {
            payload = JSON.parse(line.slice(5).trim());
          } catch {
            continue;
          }
          if (payload.kind === "done") {
            missionStatus.textContent =
              payload.status === "ok" ? "DONE" : "STOPPED";
            streamEl = null;
            meta = await (await fetch("/api/meta")).json();
            if (meta.last_routed?.agent) lastRouted = meta.last_routed.agent;
            renderAgents();
            continue;
          }
          if (payload.kind === "route") {
            try {
              const info = JSON.parse(payload.text);
              if (info.agent) lastRouted = info.agent;
              renderAgents();
            } catch {}
            continue;
          }
          if (payload.kind === "out") appendStream(payload.text || "");
          else bootLine(payload.text || "", payload.kind === "err" ? "err" : "sys");
        }
      }
    } catch (e) {
      if (e.name !== "AbortError") {
        bootLine(String(e.message || e), "err");
        missionStatus.textContent = "LOST";
      }
    } finally {
      setBusy(false);
      currentMission = null;
      abortCtrl = null;
    }
  }

  runBtn.addEventListener("click", runMission);
  abortBtn.addEventListener("click", async () => {
    if (currentMission) {
      await fetch(`/api/mission/${currentMission}/abort`, { method: "POST" });
    }
    if (abortCtrl) abortCtrl.abort();
    missionStatus.textContent = "STOPPED";
    bootLine("> Stopped.", "err");
    setBusy(false);
  });

  $("#promptInput").addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") runMission();
  });

  (async function init() {
    clearTerm();
    bootLine("KeepRoute is ready.", "sys");
    bootLine("Leave Auto on. OmniRoute picks the best provider for each job.", "sys");
    meta = await (await fetch("/api/meta")).json();
    guides = await (await fetch("/api/guides")).json();
    selected = meta.default_agent || "auto";
    if (meta.last_routed?.agent) lastRouted = meta.last_routed.agent;
    renderAgents();
    await refreshStatus();
    setInterval(refreshStatus, 10000);
  })();
})();

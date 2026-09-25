/**
 * Ask Otaconskeep — floating site chat widget.
 * Talks to the Worker's /api/chat (Cloudflare Workers AI, grounded in real
 * site facts, see otaconskeep-site worker.js). Self-injecting: include this
 * one script tag on a page and it builds its own DOM.
 */
(function () {
 var API_URL = 'https://otaconskeep-site.otaconskeep.workers.dev/api/chat';
 var history = [];

 function escapeHtml(s) {
 return String(s)
 .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
 .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
 }

 // Escape first, then turn [text](https://...) into a real link -- safe
 // because it only runs after escaping, and only accepts http(s) URLs.
 function renderAssistantText(s) {
 var escaped = escapeHtml(s);
 return escaped.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, function (_, text, url) {
 return '<a href="' + url + '" target="_blank" rel="noopener">' + text + '</a>';
 });
 }

 function build() {
 var launcher = document.createElement('button');
 launcher.className = 'keep-chat-launcher';
 launcher.type = 'button';
 launcher.setAttribute('aria-label', 'Ask about Otaconskeep');
 launcher.textContent = 'Ask Otaconskeep';

 var panel = document.createElement('div');
 panel.className = 'keep-chat-panel';
 panel.hidden = true;
 panel.innerHTML =
 '<div class="keep-chat-head">' +
 '<span class="keep-chat-head-title">Ask Otaconskeep</span>' +
 '<button type="button" class="keep-chat-close" aria-label="Close chat">✕</button>' +
 '</div>' +
 '<div class="keep-chat-log" role="log" aria-live="polite"></div>' +
 '<form class="keep-chat-form">' +
 '<input class="keep-chat-input" type="text" placeholder="Ask about Otacon, KeepRoute, install steps..." maxlength="800" autocomplete="off">' +
 '<button class="keep-chat-send" type="submit">Send</button>' +
 '</form>';

 document.body.appendChild(launcher);
 document.body.appendChild(panel);

 var log = panel.querySelector('.keep-chat-log');
 var form = panel.querySelector('.keep-chat-form');
 var input = panel.querySelector('.keep-chat-input');
 var sendBtn = panel.querySelector('.keep-chat-send');
 var closeBtn = panel.querySelector('.keep-chat-close');

 function addMsg(role, text, extraClass) {
 var el = document.createElement('div');
 el.className = 'keep-chat-msg ' + role + (extraClass ? ' ' + extraClass : '');
 if (role === 'assistant') {
 el.innerHTML = renderAssistantText(text);
 } else {
 el.textContent = text;
 }
 log.appendChild(el);
 log.scrollTop = log.scrollHeight;
 return el;
 }

 function addThinking() {
 var el = document.createElement('div');
 el.className = 'keep-chat-thinking';
 el.innerHTML =
 '<span>OTACON // ANALYZING</span>' +
 '<span class="keep-chat-thinking-dots"><span></span><span></span><span></span></span>';
 log.appendChild(el);
 log.scrollTop = log.scrollHeight;
 return el;
 }

 function openPanel() {
 panel.hidden = false;
 launcher.hidden = true;
 input.focus();
 if (!log.children.length) {
 addMsg('assistant', "Hi, I'm the site assistant. Ask me anything about Otacon, KeepRoute, Keep Desk, AI9, Expansion, Classroom, or how to install.");
 }
 }
 function closePanel() {
 panel.hidden = true;
 launcher.hidden = false;
 }

 launcher.addEventListener('click', openPanel);
 closeBtn.addEventListener('click', closePanel);

 form.addEventListener('submit', function (e) {
 e.preventDefault();
 var message = input.value.trim();
 if (!message) return;

 addMsg('user', message);
 history.push({ role: 'user', content: message });
 input.value = '';
 input.disabled = true;
 sendBtn.disabled = true;
 var pending = addThinking();

 fetch(API_URL, {
 method: 'POST',
 headers: { 'Content-Type': 'application/json' },
 body: JSON.stringify({ message: message, history: history.slice(-6) }),
 })
 .then(function (res) {
 if (!res.ok) throw new Error('HTTP ' + res.status);
 if (!res.body || !res.body.getReader) {
 // No streaming support (very old browser) -- fall back to a full read.
 return res.text().then(function (raw) { return streamFallback(raw); });
 }
 return streamReply(res.body.getReader());
 })
 .then(function (fullText) {
 if (fullText != null) history.push({ role: 'assistant', content: fullText });
 })
 .catch(function () {
 pending.remove();
 var live = doc_lastBubble();
 if (live) live.remove();
 addMsg('assistant', "Couldn't reach the assistant just now — try again in a moment, or check /faq/.", 'error');
 })
 .finally(function () {
 input.disabled = false;
 sendBtn.disabled = false;
 input.focus();
 });

 function doc_lastBubble() { return log.querySelector('.keep-chat-msg.assistant.streaming'); }

 // Reads the SSE stream from the worker ("data: {...}\n\n", ending
 // "data: [DONE]\n\n") and grows the reply bubble token by token --
 // this is the actual "Otacon thinking, then transmitting" feel instead
 // of a pause-then-dump.
 function streamReply(reader) {
 var decoder = new TextDecoder();
 var buffer = '';
 var full = '';
 var bubble = null;

 function pump() {
 return reader.read().then(function (chunk) {
 if (chunk.done) return full;
 buffer += decoder.decode(chunk.value, { stream: true });
 var events = buffer.split('\n\n');
 buffer = events.pop(); // last piece may be incomplete, keep for next read
 for (var i = 0; i < events.length; i++) {
 var line = events[i].trim();
 if (!line.startsWith('data:')) continue;
 var payload = line.slice(5).trim();
 if (payload === '[DONE]') continue;
 var parsed;
 try { parsed = JSON.parse(payload); } catch (e) { continue; }
 var token = parsed && parsed.response;
 if (!token) continue;
 if (!bubble) {
 pending.remove();
 bubble = addMsg('assistant', '', 'streaming');
 }
 full += token;
 bubble.innerHTML = renderAssistantText(full);
 log.scrollTop = log.scrollHeight;
 }
 return pump();
 });
 }

 return pump().then(function () {
 if (bubble) bubble.classList.remove('streaming');
 if (!bubble) { pending.remove(); addMsg('assistant', full || "Sorry, I didn't get a response — try again in a moment."); }
 return full;
 });
 }

 function streamFallback(raw) {
 pending.remove();
 var full = '';
 raw.split('\n\n').forEach(function (block) {
 var line = block.trim();
 if (!line.startsWith('data:')) return;
 var payload = line.slice(5).trim();
 if (payload === '[DONE]') return;
 try { full += (JSON.parse(payload).response || ''); } catch (e) {}
 });
 addMsg('assistant', full || "Sorry, I didn't get a response — try again in a moment.");
 return full;
 }
 });
 }

 if (document.readyState === 'loading') {
 document.addEventListener('DOMContentLoaded', build);
 } else {
 build();
 }
})();

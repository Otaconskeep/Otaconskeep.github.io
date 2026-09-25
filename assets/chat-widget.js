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
 var pending = addMsg('assistant', 'Thinking...', 'pending');

 fetch(API_URL, {
 method: 'POST',
 headers: { 'Content-Type': 'application/json' },
 body: JSON.stringify({ message: message, history: history.slice(-6) }),
 })
 .then(function (res) {
 if (!res.ok) throw new Error('HTTP ' + res.status);
 return res.json();
 })
 .then(function (data) {
 pending.remove();
 if (data.error) throw new Error(data.error);
 addMsg('assistant', data.reply);
 history.push({ role: 'assistant', content: data.reply });
 })
 .catch(function () {
 pending.remove();
 addMsg('assistant', "Couldn't reach the assistant just now — try again in a moment, or check /faq/.", 'error');
 })
 .finally(function () {
 input.disabled = false;
 sendBtn.disabled = false;
 input.focus();
 });
 });
 }

 if (document.readyState === 'loading') {
 document.addEventListener('DOMContentLoaded', build);
 } else {
 build();
 }
})();

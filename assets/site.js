(function () {
 'use strict';

 // Canonical public site is GitHub Pages. Workers is a mirror, nudge if someone lands there.
 try {
 if (/\.workers\.dev$/i.test(location.hostname)) {
 var bar = document.createElement('div');
 bar.setAttribute('role', 'note');
 bar.style.cssText = 'position:sticky;top:0;z-index:60;background:#0e5f52;color:#e4edf5;font:600 0.85rem/1.4 Figtree,sans-serif;padding:10px 16px;text-align:center;border-bottom:1px solid #39e6c8;';
 var path = location.pathname + location.search + location.hash;
 bar.innerHTML = 'Canonical site: <a href="https://otaconskeep.github.io' + path + '" style="color:#fff;text-decoration:underline">otaconskeep.github.io</a> (this Workers URL is a deploy mirror).';
 document.addEventListener('DOMContentLoaded', function () {
 document.body.insertBefore(bar, document.body.firstChild);
 });
 }
 } catch (e) {}


 // Copy-to-clipboard for every [data-copy-target] button.
 function initCopyButtons() {
 var buttons = document.querySelectorAll('[data-copy-target]');
 buttons.forEach(function (btn) {
 var targetId = btn.getAttribute('data-copy-target');
 var target = document.getElementById(targetId);
 if (!target) return;

 btn.addEventListener('click', function () {
 var text = target.textContent.replace(/\s+\\\s*\n\s*/g, ' \\\n').trim();
 var original = btn.textContent;

 function settle(ok) {
 btn.textContent = ok ? 'Copied' : 'Select & copy manually';
 btn.classList.toggle('copy-fail', !ok);
 setTimeout(function () {
 btn.textContent = original;
 btn.classList.remove('copy-fail');
 }, 1800);
 }

 try {
 if (navigator.clipboard && navigator.clipboard.writeText) {
 navigator.clipboard.writeText(target.textContent.trim()).then(
 function () { settle(true); },
 function () { settle(false); }
 );
 } else {
 settle(false);
 }
 } catch (err) {
 settle(false);
 }
 });
 });
 }

 // Mobile nav toggle.
 function initNavToggle() {
 var toggle = document.querySelector('.navtoggle');
 var links = document.querySelector('.navlinks');
 if (!toggle || !links) return;

 toggle.addEventListener('click', function () {
 var isOpen = links.classList.toggle('open');
 toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
 });

 links.querySelectorAll('a').forEach(function (a) {
 a.addEventListener('click', function () {
 links.classList.remove('open');
 toggle.setAttribute('aria-expanded', 'false');
 });
 });
 }

 // Inside the Keep: gallery + lightbox + tour

 var GALLERY_DATA = [
 { slug: 'loading-room', title: 'Entering the Keep', caption: 'A boot sequence with real continuity and atmosphere, not just a spinner.' },
 { slug: 'war-room-1', title: 'War Room: Situation View', caption: 'Commander-level awareness of active operations, decisions and outcomes.' },
 { slug: 'war-room-2', title: 'War Room: Operational Detail', caption: 'Live operational picture: discoveries, active work, and outcomes in one surface.' },
 { slug: 'project-rex-board', title: 'Project REX', caption: 'From proposal to approval, execution, verification and tracked outcome.' },
 { slug: 'video-studio', title: 'Production Studio', caption: 'Local AI production, GPU jobs, media generation and workflow control.' },
 { slug: 'module-entry-video-studio', title: 'Production Studio: Module Entry', caption: 'Where an AI media-production job begins.' },
 { slug: 'module-tuning-video-studio', title: 'Production Studio: Model Tuning', caption: 'Real controls over module and model parameters, not just a generate button.' },
 { slug: 'albedo-room', title: 'Albedo’s Lair', caption: 'A themed governance and media-curation room built around one agent’s personality.' },
 { slug: 'albedo-dossier-1', title: 'Albedo: Personnel Dossier', caption: 'Persistent identity and role record for an individual agent.' },
 { slug: 'albedo-dossier-2', title: 'Albedo: Detailed Dossier', caption: 'A deeper look at how the Keep tracks agent state over time.' },
 { slug: 'codec-1', title: 'Codec: Ecosystem Cockpit', caption: 'Voice, TTS and agent routing in one communications cockpit.' },
 { slug: 'codec-2', title: 'Codec: Live Conversation', caption: 'The actual interaction experience behind a Codec call.' },
 { slug: 'foxdie', title: 'FOXDIE: Media Integrity', caption: 'Autonomous duplicate detection and quarantine across the media library.' },
 { slug: 'greyfox', title: 'Gray Fox: Systems Health', caption: 'CPU, RAM, storage pressure and bottlenecks as an agent’s domain.' },
 { slug: 'mantis-automation-builder', title: 'Home Automation: Visual Builder', caption: 'Drag-and-drop automation authoring across hundreds of real devices.' },
 { slug: 'mantis-automation', title: 'Home Automation: Control', caption: 'The broader automation interface behind a single agent’s domain.' },
 { slug: 'mantis-room', title: 'Psycho Mantis: Automation Room', caption: 'Character identity paired with a functional automation domain.' },
 { slug: 'relationships-1', title: 'Agent Relationships', caption: 'Persistent relationship state between agents and the operator.' },
 { slug: 'relationships-2', title: 'Relationship Dynamics', caption: 'How agents’ regard for each other evolves instead of resetting.' },
 { slug: 'more-agent-rooms', title: 'A Keep Full of Agents', caption: 'Many persistent personas, each with its own room and responsibility.' },
 { slug: 'sniperwolf-room', title: 'Sniper Wolf: Agent Room', caption: 'An immersive, persistent persona with its own presentation.' },
 { slug: 'meiling-room', title: 'Mei Ling: Operations Room', caption: 'Tied directly to file integrity, backups and schedules, not decorative.' },
 { slug: 'nastasha-room', title: 'Nastasha Romanenko: Agent Room', caption: 'Another persistent character occupying its own visual space.' },
 { slug: 'johnny-quickhands', title: 'Johnny Quickhands: Agent Room', caption: 'An independently styled agent space with its own identity.' },
 { slug: 'johnny-2', title: 'Johnny Quickhands: Live Interaction', caption: 'Proof these rooms are functioning interfaces, not static cards.' },
 { slug: 'agent-room-halister', title: 'Halister Blackcloak: Agent Room', caption: 'A dedicated visual environment for an individual persona.' },
 { slug: 'snake-security', title: 'Solid Snake: Security Operations', caption: 'Vulnerabilities, CVEs, patching and firewall posture as a named domain.' },
 { slug: 'agent-report', title: 'Agent Operational Report', caption: 'What an agent owns, is doing, and the state of its responsibilities.' },
 { slug: 'agent-reporting', title: 'Agent Reporting System', caption: 'Structured status and activity across Keep personnel.' },
 { slug: 'dossier-2', title: 'Personnel Dossier System', caption: 'Structured agent records that live outside the chat session.' },
 { slug: 'dossier-3', title: 'Agent Identity & Role Records', caption: 'Agents modeled as members of an organization, not a dropdown list.' },
 { slug: 'dossier-4', title: 'Keep Roster Intelligence', caption: 'The scale of structured information the Keep maintains per agent.' },
 { slug: 'cli-runner', title: 'Keep CLI Runner', caption: 'Real operator tooling for controlled technical execution.' },
 { slug: 'monolith-editor', title: 'Monolith Editor', caption: 'Built-in tooling for evolving the environment itself.' },
 { slug: 'otacons-myspace', title: 'Otacon MySpace: Social Layer', caption: 'A persistent, retro social world the agents participate in.' },
 { slug: 'otacons-myspace-posts', title: 'Agent Social Posts', caption: 'Persistent agent voice and output outside direct prompts.' },
 { slug: 'fitness-ai', title: 'AI Fitness Control Room', caption: 'Workout tracking, progression and AI coaching in one panel.' },
 { slug: 'albedo-operational-update', title: 'Albedo: Operational Update', caption: 'Albedo reports live FOXDIE and Project REX activity, including review queues, approved work, and items requiring escalation.', folder: 'discord', tag: 'Discord Relay' },
 { slug: 'naomi-appointment-digest', title: 'Naomi Hunter: Appointment Digest', caption: 'Naomi turns upcoming household and personal events into a concise reminder digest so important appointments don’t disappear into a calendar.', folder: 'discord', tag: 'Discord Relay' },
 { slug: 'otacon-weekly-lab-intelligence', title: 'Otacon: Weekly Lab Intelligence', caption: 'A scheduled intelligence report combining system observations, research progress, and agent development into one readable update.', folder: 'discord', tag: 'Discord Relay' },
 { slug: 'otacon-voice-training-completion', title: 'Otacon: Voice Training Completion', caption: 'AI jobs don’t silently finish in the background. Otacon reports successful model export and deployment when a trained voice becomes available to the Keep.', folder: 'discord', tag: 'Discord Relay' },
 { slug: 'otacon-morning-briefing', title: 'Otacon: Morning Briefing', caption: 'A daily briefing combining useful personal and system context into a message delivered automatically.', folder: 'discord', tag: 'Discord Relay' }
 ];

 var DISCORD_SLUGS = [
 'albedo-operational-update',
 'naomi-appointment-digest',
 'otacon-weekly-lab-intelligence',
 'otacon-voice-training-completion',
 'otacon-morning-briefing'
 ];

 var FEATURED_SLUGS = [
 'loading-room', 'war-room-1', 'project-rex-board', 'video-studio',
 'albedo-room', 'codec-1', 'foxdie', 'mantis-automation-builder',
 'relationships-1', 'more-agent-rooms'
 ];

 var TOUR_STEPS = [
 { slug: 'loading-room', label: '01 ENTERING' },
 { slug: 'war-room-1', label: '02 WAR ROOM' },
 { slug: 'project-rex-board', label: '03 REX' },
 { slug: 'video-studio', label: '04 PRODUCTION' },
 { slug: 'more-agent-rooms', label: '05 AGENT ROOMS' },
 { slug: 'mantis-automation-builder', label: '06 AUTOMATION' },
 { slug: 'codec-1', label: '07 CODEC' }
 ];

 function imgPath(item) {
 var folder = (item && item.folder) ? item.folder : 'keep';
 var slug = typeof item === 'string' ? item : item.slug;
 if (typeof item === 'string') return '/assets/img/keep/' + slug + '.webp';
 return '/assets/img/' + folder + '/' + slug + '.webp';
 }
 function findItem(slug) {
 for (var i = 0; i < GALLERY_DATA.length; i++) if (GALLERY_DATA[i].slug === slug) return i;
 return -1;
 }

 function galleryCardHTML(item, idx, opts) {
 opts = opts || {};
 var cls = opts.cardClass || 'gallery-item';
 var tag = item.tag || 'Reference Keep';
 return (
 '<button type="button" class="' + cls + '" data-idx="' + idx + '">' +
 '<span class="thumb-wrap">' +
 '<img src="' + imgPath(item) + '" alt="' + item.title + ': Discord / Keep screenshot from the Otaconskeep reference Keep" loading="lazy">' +
 '<span class="gtag">' + tag + '</span>' +
 '</span>' +
 '<span class="gbody">' +
 '<h4>' + item.title + '</h4>' +
 '<p>' + item.caption + '</p>' +
 '</span>' +
 '</button>'
 );
 }

 function initGalleries() {
 var featuredEl = document.getElementById('gallery-featured');
 var fullEl = document.getElementById('gallery-full');
 var discordEl = document.getElementById('discord-feed');

 if (featuredEl) {
 featuredEl.innerHTML = FEATURED_SLUGS.map(function (slug) {
 var idx = findItem(slug);
 return galleryCardHTML(GALLERY_DATA[idx], idx);
 }).join('');
 }

 if (fullEl) {
 fullEl.innerHTML = GALLERY_DATA.map(function (item, idx) {
 return galleryCardHTML(item, idx, item.folder === 'discord' ? { cardClass: 'gallery-item discord-in-gallery' } : {});
 }).join('');
 }

 if (discordEl) {
 discordEl.innerHTML = DISCORD_SLUGS.map(function (slug) {
 var idx = findItem(slug);
 return galleryCardHTML(GALLERY_DATA[idx], idx, { cardClass: 'discord-card' });
 }).join('');
 }

 if (featuredEl || fullEl || discordEl) initLightbox();
 }

 function initLightbox() {
 var lb = document.getElementById('lightbox');
 if (!lb) return;
 var imgEl = lb.querySelector('.lightbox-inner img');
 var titleEl = lb.querySelector('.lightbox-caption h4');
 var capEl = lb.querySelector('.lightbox-caption p');
 var current = 0;

 function show(idx) {
 current = (idx + GALLERY_DATA.length) % GALLERY_DATA.length;
 var item = GALLERY_DATA[current];
 imgEl.src = imgPath(item);
 imgEl.alt = item.title;
 titleEl.textContent = item.title;
 capEl.textContent = item.caption;
 }

 document.querySelectorAll('.gallery-item, .discord-card').forEach(function (btn) {
 btn.addEventListener('click', function () {
 show(parseInt(btn.getAttribute('data-idx'), 10));
 lb.classList.add('open');
 });
 });

 lb.querySelector('.lightbox-close').addEventListener('click', function () {
 lb.classList.remove('open');
 });
 lb.addEventListener('click', function (e) {
 if (e.target === lb) lb.classList.remove('open');
 });
 lb.querySelector('.lightbox-prev').addEventListener('click', function () { show(current - 1); });
 lb.querySelector('.lightbox-next').addEventListener('click', function () { show(current + 1); });

 document.addEventListener('keydown', function (e) {
 if (!lb.classList.contains('open')) return;
 if (e.key === 'Escape') lb.classList.remove('open');
 if (e.key === 'ArrowLeft') show(current - 1);
 if (e.key === 'ArrowRight') show(current + 1);
 });
 }

 function initTour() {
 var stepsEl = document.getElementById('tour-steps');
 var stageImg = document.getElementById('tour-stage-img');
 var stageNum = document.getElementById('tour-step-num');
 var stageTitle = document.getElementById('tour-step-title');
 var stageCaption = document.getElementById('tour-step-caption');
 if (!stepsEl || !stageImg) return;

 stepsEl.innerHTML = TOUR_STEPS.map(function (step, i) {
 return '<button type="button" class="tour-step' + (i === 0 ? ' active' : '') + '" data-i="' + i + '">' + step.label + '</button>';
 }).join('');

 function activate(i) {
 var step = TOUR_STEPS[i];
 var item = GALLERY_DATA[findItem(step.slug)];
 stageImg.src = imgPath(step.slug);
 stageImg.alt = item.title;
 stageNum.textContent = step.label;
 stageTitle.textContent = item.title;
 stageCaption.textContent = item.caption;
 stepsEl.querySelectorAll('.tour-step').forEach(function (btn, idx) {
 btn.classList.toggle('active', idx === i);
 });
 }

 stepsEl.querySelectorAll('.tour-step').forEach(function (btn) {
 btn.addEventListener('click', function () {
 activate(parseInt(btn.getAttribute('data-i'), 10));
 });
 });

 activate(0);
 }

 // Hear the Keep: codec voice archive player

 var CODEC_SPEAKERS = [
 { name: 'Otacon', role: 'Systems / Engineering', start: 0, end: 17.3 },
 { name: 'Mei Ling', role: 'Operations / Records', start: 17.3, end: 31.7 },
 { name: 'Naomi Hunter', role: 'Research / Continuity', start: 31.7, end: 38.0 },
 { name: 'Halister Black Cloak', role: 'Project REX / Governance', start: 38.0, end: 9999 }
 ];

 function fmtTime(sec) {
 if (!isFinite(sec) || sec < 0) sec = 0;
 var m = Math.floor(sec / 60);
 var s = Math.floor(sec % 60);
 return m + ':' + (s < 10 ? '0' : '') + s;
 }

 function initCodecPlayer() {
 var audio = document.getElementById('codec-audio');
 var playBtn = document.getElementById('codec-play-btn');
 var restartBtn = document.getElementById('codec-restart-btn');
 var progressTrack = document.getElementById('codec-progress-track');
 var progressFill = document.getElementById('codec-progress-fill');
 var timeElapsed = document.getElementById('codec-time-elapsed');
 var timeTotal = document.getElementById('codec-time-total');
 var liveTag = document.getElementById('codec-live-tag');
 var transmitLabel = document.getElementById('codec-transmit-label');
 var speakerNameEl = document.getElementById('codec-speaker-name');
 var speakerRoleEl = document.getElementById('codec-speaker-role');
 var frames = document.querySelectorAll('#codec-screen .frame');
 var agentCards = document.querySelectorAll('#codec-agents .codec-agent');
 if (!audio || !playBtn) return;

 var currentSlot = -1;

 function setSlot(i) {
 if (i === currentSlot) return;
 currentSlot = i;
 frames.forEach(function (f, idx) { f.classList.toggle('active', idx === i); });
 agentCards.forEach(function (c, idx) { c.classList.toggle('active', idx === i); });
 var sp = CODEC_SPEAKERS[i];
 speakerNameEl.textContent = sp.name;
 speakerRoleEl.textContent = sp.role;
 transmitLabel.textContent = 'Transmitting // ' + sp.name.toUpperCase();
 transmitLabel.classList.remove('idle');
 }

 function resetSlot() {
 currentSlot = -1;
 frames.forEach(function (f, idx) { f.classList.toggle('active', idx === 0); });
 agentCards.forEach(function (c) { c.classList.remove('active'); });
 speakerNameEl.textContent = 'Otaconskeep';
 speakerRoleEl.textContent = 'Press play to begin';
 transmitLabel.textContent = 'Voice Link Standby';
 transmitLabel.classList.add('idle');
 }

 function speakerAt(t) {
 for (var i = 0; i < CODEC_SPEAKERS.length; i++) {
 if (t >= CODEC_SPEAKERS[i].start && t < CODEC_SPEAKERS[i].end) return i;
 }
 return CODEC_SPEAKERS.length - 1;
 }

 audio.addEventListener('loadedmetadata', function () {
 timeTotal.textContent = fmtTime(audio.duration);
 });

 audio.addEventListener('timeupdate', function () {
 var dur = audio.duration || 1;
 var pct = (audio.currentTime / dur) * 100;
 progressFill.style.width = pct + '%';
 timeElapsed.textContent = fmtTime(audio.currentTime);
 if (isFinite(audio.duration)) timeTotal.textContent = fmtTime(audio.duration);
 setSlot(speakerAt(audio.currentTime));
 });

 audio.addEventListener('play', function () {
 playBtn.innerHTML = '&#10074;&#10074; Pause';
 liveTag.textContent = 'Voice Link Active';
 liveTag.classList.add('status-live');
 });

 audio.addEventListener('pause', function () {
 playBtn.innerHTML = '&#9654; Play Keep Welcome';
 liveTag.textContent = 'Standing By';
 liveTag.classList.remove('status-live');
 });

 audio.addEventListener('ended', function () {
 playBtn.innerHTML = '&#9654; Play Keep Welcome';
 liveTag.textContent = 'Standing By';
 liveTag.classList.remove('status-live');
 progressFill.style.width = '0%';
 timeElapsed.textContent = '0:00';
 resetSlot();
 });

 playBtn.addEventListener('click', function () {
 if (audio.paused) {
 audio.play().catch(function () {});
 } else {
 audio.pause();
 }
 });

 restartBtn.addEventListener('click', function () {
 audio.currentTime = 0;
 resetSlot();
 audio.play().catch(function () {});
 });

 progressTrack.addEventListener('click', function (e) {
 var rect = progressTrack.getBoundingClientRect();
 var ratio = (e.clientX - rect.left) / rect.width;
 if (isFinite(audio.duration)) audio.currentTime = ratio * audio.duration;
 });

 resetSlot();
 }

 // Manual install column: clickable steps; Next opens the following step.
 function initManualSteps() {
 document.querySelectorAll('.manual-steps').forEach(function (group) {
 var steps = Array.prototype.slice.call(group.querySelectorAll(':scope > .manual-step'));
 if (!steps.length) return;

 steps.forEach(function (step, index) {
 step.addEventListener('toggle', function () {
 if (!step.open) return;
 steps.forEach(function (other) {
 if (other !== step) other.open = false;
 });
 });

 var nextBtn = step.querySelector('.manual-next');
 if (!nextBtn) return;
 nextBtn.addEventListener('click', function (e) {
 e.preventDefault();
 var next = steps[index + 1];
 if (!next) return;
 steps.forEach(function (other) { other.open = false; });
 next.open = true;
 try {
 next.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
 } catch (err) {}
 });
 });
 });
 }

 // Manual path OS chooser: Windows / Linux / Advanced WSL.
 function initOsChoosers() {
 document.querySelectorAll('[data-os-chooser]').forEach(function (chooser) {
 var root = chooser.closest('.os-card-manual') || chooser.parentElement;
 if (!root) return;
 var buttons = Array.prototype.slice.call(chooser.querySelectorAll('[data-os-target]'));
 var paths = Array.prototype.slice.call(root.querySelectorAll('[data-os-path]'));

 function activate(key) {
 buttons.forEach(function (btn) {
 var on = btn.getAttribute('data-os-target') === key;
 btn.classList.toggle('is-active', on);
 btn.setAttribute('aria-selected', on ? 'true' : 'false');
 });
 paths.forEach(function (path) {
 var on = path.getAttribute('data-os-path') === key;
 path.classList.toggle('is-active', on);
 if (on) {
 var steps = path.querySelectorAll(':scope > .manual-steps > .manual-step');
 steps.forEach(function (step, i) { step.open = i === 0; });
 }
 });
 }

 buttons.forEach(function (btn) {
 btn.addEventListener('click', function () {
 activate(btn.getAttribute('data-os-target'));
 });
 });
 });
 }

 document.addEventListener('DOMContentLoaded', function () {
 initCopyButtons();
 initManualSteps();
 initOsChoosers();
 initNavToggle();
 initGalleries();
 initTour();
 initCodecPlayer();
 });
})();

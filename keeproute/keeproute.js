(function () {
 'use strict';

 function initSubnav() {
 var links = document.querySelectorAll('.kr-subnav a[href^="#"]');
 if (!links.length) return;
 var sections = [];
 links.forEach(function (a) {
 var id = a.getAttribute('href').slice(1);
 var el = document.getElementById(id);
 if (el) sections.push({ id: id, el: el, a: a });
 });
 function setActive() {
 var y = window.scrollY + 120;
 var current = sections[0];
 sections.forEach(function (s) {
 if (s.el.offsetTop <= y) current = s;
 });
 links.forEach(function (a) { a.classList.remove('is-active'); });
 if (current) current.a.classList.add('is-active');
 }
 window.addEventListener('scroll', setActive, { passive: true });
 setActive();
 }

 function initBars() {
 var fills = document.querySelectorAll('.kr-bar-fill[data-pct]');
 if (!fills.length) return;
 function paint() {
 fills.forEach(function (el) {
 var pct = Number(el.getAttribute('data-pct') || 0);
 el.style.width = Math.max(0, Math.min(100, pct)) + '%';
 });
 }
 if ('IntersectionObserver' in window) {
 var io = new IntersectionObserver(function (entries) {
 entries.forEach(function (e) {
 if (e.isIntersecting) {
 paint();
 io.disconnect();
 }
 });
 }, { threshold: 0.2 });
 var host = document.querySelector('.kr-charts');
 if (host) io.observe(host);
 else paint();
 } else {
 paint();
 }
 }

 function initBeginner() {
 var btn = document.getElementById('kr-beginner-open');
 var modal = document.getElementById('kr-beginner-modal');
 var close = document.getElementById('kr-beginner-close');
 if (!btn || !modal) return;

 function open() {
 modal.hidden = false;
 document.body.style.overflow = 'hidden';
 close && close.focus();
 }
 function shut() {
 modal.hidden = true;
 document.body.style.overflow = '';
 btn.focus();
 }

 btn.addEventListener('click', open);
 close && close.addEventListener('click', shut);
 modal.addEventListener('click', function (e) {
 if (e.target === modal) shut();
 });
 document.addEventListener('keydown', function (e) {
 if (e.key === 'Escape' && !modal.hidden) shut();
 });

 modal.querySelectorAll('.kr-q').forEach(function (q) {
 var b = q.querySelector('button.q');
 if (!b) return;
 b.addEventListener('click', function () {
 q.classList.toggle('open');
 });
 });
 }

 function initHandoffPulse() {
 var nodes = document.querySelectorAll('.kr-anim-handoff .node[data-pulse]');
 if (!nodes.length) return;
 var i = 0;
 function tick() {
 nodes.forEach(function (n) { n.classList.remove('pulse'); });
 nodes[i % nodes.length].classList.add('pulse');
 i += 1;
 }
 tick();
 setInterval(tick, 900);
 }

 document.addEventListener('DOMContentLoaded', function () {
 initSubnav();
 initBars();
 initBeginner();
 initHandoffPulse();
 });
})();

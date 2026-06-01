/**
 * frontend/js/app.js
 * Main entry point — wires socket events → Table + Stats modules.
 */

// ── Socket events → modules ──
document.addEventListener('pp:connected',    () => Stats.setConnected(true));
document.addEventListener('pp:disconnected', () => Stats.setConnected(false));
document.addEventListener('pp:history',  e => Table.loadHistory(e.detail));
document.addEventListener('pp:packet',   e => Table.addPacket(e.detail));
document.addEventListener('pp:stats',    e => Stats.update(e.detail));

// ── Filter buttons ──
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => Table.setFilter(btn.dataset.filter));
});

// ── Search ──
document.getElementById('search-input').addEventListener('input', e => {
  Table.setSearch(e.target.value);
});

// ── Pause button ──
document.getElementById('btn-pause').addEventListener('click', () => {
  Table.togglePause();
});

// ── Clear button ──
document.getElementById('btn-clear').addEventListener('click', () => {
  location.reload();
});

// ── Toast helper (global) ──
window.showToast = function(msg, type = '') {
  const wrap = document.getElementById('toast-wrap');
  const div  = document.createElement('div');
  div.className = `toast ${type}`;
  div.textContent = msg;
  wrap.appendChild(div);
  setTimeout(() => div.remove(), 3500);
};
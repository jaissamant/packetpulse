/**
 * frontend/js/app.js
 * Main entry point — wires socket events → Table + Stats + Charts.
 */

// ── Socket events → modules ──
document.addEventListener('pp:connected',    () => Stats.setConnected(true));
document.addEventListener('pp:disconnected', () => Stats.setConnected(false));
document.addEventListener('pp:history',  e => Table.loadHistory(e.detail));
document.addEventListener('pp:packet',   e => Table.addPacket(e.detail));
document.addEventListener('pp:stats',    e => Stats.update(e.detail));

// ── Protocol filter buttons ──
document.querySelectorAll('.proto-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.proto-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    Table.setFilter(btn.dataset.proto);
  });
});

// ── Search ──
const searchInput = document.getElementById('searchInput');
if (searchInput) {
  searchInput.addEventListener('input', e => {
    Table.setSearch(e.target.value);
  });
}

// ── Init charts on load ──
document.addEventListener('DOMContentLoaded', () => {
  if (typeof initAllCharts === 'function') initAllCharts();
});
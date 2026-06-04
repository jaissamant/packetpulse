/**
 * frontend/js/app.js  —  Day 6
 * Wires all socket events → Table, Stats, Charts, Alerts.
 */

// ── Socket → modules ──
document.addEventListener('pp:connected', () => {
  Stats.setConnected(true);
});

document.addEventListener('pp:disconnected', () => {
  Stats.setConnected(false);
});

document.addEventListener('pp:history', e => {
  Table.loadHistory(e.detail);
});

document.addEventListener('pp:packet', e => {
  Table.addPacket(e.detail);
  Charts.addPacket(e.detail);
});

document.addEventListener('pp:stats', e => {
  Stats.update(e.detail);
  Charts.updateStats(e.detail);
});

document.addEventListener('pp:alert', e => {
  Alerts.receive(e.detail);
});

// ── Filter buttons ──
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

// ── Init charts ──
Charts.init()
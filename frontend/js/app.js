/**
 * frontend/js/app.js
 * Main entry point — wires socket events → Table + Stats + Charts.
 */

// ── Socket events → modules ──
document.addEventListener('pp:connected',    () => Stats.setConnected(true));
document.addEventListener('pp:disconnected', () => Stats.setConnected(false));
document.addEventListener('pp:history',  e => Table.loadHistory(e.detail));
document.addEventListener('pp:packet',   e => {
    // Only add to table if NOT paused
    if (!window.isPaused) {
        Table.addPacket(e.detail);
    }
});
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

// ── Pause and Clear Logic ──
window.isPaused = false; // Global state for pause

const pauseBtn = document.getElementById('pauseBtn');
const clearBtn = document.getElementById('clearBtn');

if (pauseBtn) {
    pauseBtn.addEventListener('click', () => {
        window.isPaused = !window.isPaused;
        pauseBtn.textContent = window.isPaused ? 'Resume' : 'Pause';
        pauseBtn.classList.toggle('active', window.isPaused);
    });
}

if (clearBtn) {
    clearBtn.addEventListener('click', () => {
        // Assuming your Table module has a clear method
        if (typeof Table.clear === 'function') {
            Table.clear();
        } else {
            // Fallback if no Table.clear method exists
            document.getElementById('packetTableBody').innerHTML = '';
        }
    });
}

// ── Init charts on load ──
document.addEventListener('DOMContentLoaded', () => {
  if (typeof initAllCharts === 'function') initAllCharts();
});
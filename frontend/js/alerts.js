/**
 * frontend/js/alerts.js  —  Day 6
 * Alert panel UI — receives alerts via WebSocket,
 * shows toast notifications, manages the alert panel.
 */

const Alerts = (() => {
  let alertList   = [];
  let panelOpen   = false;
  let critCount   = 0;
  let warnCount   = 0;

  const MAX_ALERTS  = 50;
  const TOAST_DURATION = 5000;

  // ── Init ──
  function init() {
    // Close panel
    document.getElementById('alertPanelClose').addEventListener('click', closePanel);
    // Clear alerts
    document.getElementById('alertClearBtn').addEventListener('click', clearAlerts);
    // Toggle panel
    document.getElementById('alertToggleBtn').addEventListener('click', togglePanel);
  }

  // ── Receive alert from socket ──
  function receive(alert) {
    alertList.unshift(alert); // newest first
    if (alertList.length > MAX_ALERTS) alertList.pop();

    if (alert.severity === 'critical') critCount++;
    else if (alert.severity === 'warning') warnCount++;

    renderList();
    updateBadge();
    showToast(alert);
  }

  // ── Panel ──
  function togglePanel() {
    panelOpen = !panelOpen;
    document.getElementById('alert-panel').classList.toggle('open', panelOpen);
  }

  function closePanel() {
    panelOpen = false;
    document.getElementById('alert-panel').classList.remove('open');
  }

  function clearAlerts() {
    alertList  = [];
    critCount  = 0;
    warnCount  = 0;
    renderList();
    updateBadge();
    // Also clear on server
    fetch('/api/alerts/clear', { method: 'POST' });
  }

  // ── Render alert list ──
  function renderList() {
    const el = document.getElementById('alertListBody');
    if (!el) return;

    if (alertList.length === 0) {
      el.innerHTML = `
        <div class="alert-empty">
          <div class="alert-empty-icon">✅</div>
          <div class="alert-empty-text">No alerts — network looks clean</div>
        </div>`;
      return;
    }

    el.innerHTML = alertList.map(a => alertHTML(a)).join('');
  }

  function alertHTML(a) {
    const time = a.timestamp
      ? a.timestamp.substring(11, 19)
      : '—';
    return `
      <div class="alert-item ${a.severity}">
        <div class="alert-item-top">
          <span class="alert-sev-badge ${a.severity}">${a.severity}</span>
          <span class="alert-title">${a.title}</span>
          <span class="alert-time">${time}</span>
        </div>
        <div class="alert-message">${a.message}</div>
      </div>`;
  }

  // ── Badge on toggle button ──
  function updateBadge() {
    const badge = document.getElementById('alertCountBadge');
    if (!badge) return;

    const total = alertList.length;
    badge.textContent = total;

    badge.className = 'alert-count-badge';
    if (critCount > 0)     badge.classList.add('crit');
    else if (warnCount > 0) badge.classList.add('warn');
  }

  // ── Toast notification ──
  function showToast(alert) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    // Only toast warnings and criticals
    if (alert.severity === 'info') return;

    const div = document.createElement('div');
    div.className = `toast-notif ${alert.severity}`;
    div.innerHTML = `
      <div class="t-title">⚠ ${alert.title}</div>
      <div class="t-msg">${alert.message}</div>
    `;
    container.appendChild(div);

    // Auto-dismiss
    setTimeout(() => {
      div.style.opacity = '0';
      div.style.transition = 'opacity 0.3s';
      setTimeout(() => div.remove(), 300);
    }, TOAST_DURATION);
  }

  // Init on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', init);

  return { receive, togglePanel, clearAlerts };
})();
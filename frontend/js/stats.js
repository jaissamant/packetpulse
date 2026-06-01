/**
 * frontend/js/stats.js
 * Updates the stat cards and connection status
 * whenever a stats_update event arrives.
 */

const Stats = (() => {
  const els = {
    total:    document.getElementById('stat-total'),
    bytes:    document.getElementById('stat-bytes'),
    pps:      document.getElementById('stat-pps'),
    proto:    document.getElementById('stat-proto'),
    conns:    document.getElementById('stat-conns'),
    statusDot:document.getElementById('status-dot'),
    statusTxt:document.getElementById('status-text'),
  };

  function update(data) {
    els.total.textContent = (data.total_packets || 0).toLocaleString();
    els.bytes.textContent = formatBytes(data.total_bytes || 0);
    els.pps.textContent   = (data.packets_per_sec || 0).toFixed(1);

    // Top protocol
    const proto = data.by_protocol || {};
    const top = Object.entries(proto).sort((a, b) => b[1] - a[1])[0];
    els.proto.textContent = top ? top[0] : '—';

    // Active connections (unique src IPs)
    els.conns.textContent = Object.keys(proto).length;
  }

  function setConnected(yes) {
    if (yes) {
      els.statusDot.className = 'status-dot live';
      els.statusTxt.textContent = 'Live';
    } else {
      els.statusDot.className = 'status-dot dead';
      els.statusTxt.textContent = 'Disconnected';
    }
  }

  function formatBytes(b) {
    if (b < 1024)        return b + ' B';
    if (b < 1048576)     return (b / 1024).toFixed(1) + ' KB';
    if (b < 1073741824)  return (b / 1048576).toFixed(1) + ' MB';
    return (b / 1073741824).toFixed(2) + ' GB';
  }

  return { update, setConnected };
})();
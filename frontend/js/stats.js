/**
 * frontend/js/stats.js  —  Day 6
 * Updates stat cards and connection status.
 */

const Stats = (() => {

  function update(s) {
    const total = document.getElementById('statPackets');
    const bytes = document.getElementById('statBytes');
    const pps   = document.getElementById('statPPS');
    const bps   = document.getElementById('statBPS');
    const proto = document.getElementById('statTopProto');
    const pcount= document.getElementById('statProtoCount');
    const hosts = document.getElementById('statHosts');

    if (total) total.textContent = (s.total_packets || 0).toLocaleString();
    if (bytes) bytes.textContent = formatBytes(s.total_bytes || 0);
    if (pps)   pps.textContent   = `${(s.packets_per_sec || 0).toFixed(1)} pkt/s`;
    if (bps)   bps.textContent   = `${formatBytes(s.bytes_per_sec || 0)}/s`;

    // Top protocol
    const byProto = s.by_protocol || {};
    const topEntry = Object.entries(byProto).sort((a, b) => b[1] - a[1])[0];
    if (proto)  proto.textContent  = topEntry ? topEntry[0] : '—';
    if (pcount) pcount.textContent = topEntry ? `${topEntry[1]} packets` : '0 packets';

    // Host count (unique protocols as proxy, or use window._hostCounts)
    if (hosts) {
      const hostCount = Object.keys(window._hostCounts || {}).length;
      hosts.textContent = hostCount;
    }
  }

  function setConnected(ok) {
    const dot  = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    if (dot) {
      dot.className = 'status-dot ' + (ok ? 'connected' : 'error');
    }
    if (text) text.textContent = ok ? 'Connected' : 'Disconnected';
  }

  function formatBytes(b) {
    if (!b || b < 1024)      return `${b || 0} B`;
    if (b < 1024 * 1024)    return `${(b / 1024).toFixed(1)} KB`;
    if (b < 1024 ** 3)      return `${(b / 1024 / 1024).toFixed(2)} MB`;
    return `${(b / 1024 ** 3).toFixed(2)} GB`;
  }

  return { update, setConnected };
})();
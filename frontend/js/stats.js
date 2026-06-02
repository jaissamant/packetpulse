/**
 * frontend/js/stats.js
 * Updates the stat cards and connection status
 * whenever a stats_update event arrives.
 */

const Stats = (() => {
  const els = {
    packets:   document.getElementById('statPackets'),
    bytes:     document.getElementById('statBytes'),
    pps:       document.getElementById('statPPS'),
    bps:       document.getElementById('statBPS'),
    topProto:  document.getElementById('statTopProto'),
    protoCount:document.getElementById('statProtoCount'),
    hosts:     document.getElementById('statHosts'),
    statusDot: document.getElementById('statusDot'),
    statusTxt: document.getElementById('statusText'),
  };

  function update(data) {
    // Total packets
    if (els.packets) els.packets.textContent = (data.total_packets || 0).toLocaleString();

    // Total bytes
    if (els.bytes) els.bytes.textContent = formatBytes(data.total_bytes || 0);

    // Packets per second
    if (els.pps) els.pps.textContent = (data.pps_current || 0) + ' pkt/s';

    // Bytes per second
    if (els.bps) els.bps.textContent = formatBytes(data.bandwidth_bps || 0) + '/s';

    // Top protocol
    const proto = data.by_protocol || {};
    const top = Object.entries(proto).sort((a, b) => b[1] - a[1])[0];
    if (els.topProto)   els.topProto.textContent   = top ? top[0] : '—';
    if (els.protoCount) els.protoCount.textContent = top ? top[1] + ' packets' : '0 packets';

    // Active hosts (unique src IPs)
    const hostCount = Object.keys(data.top_src_ips || {}).length;
    if (els.hosts) els.hosts.textContent = hostCount;

    // Update charts
    if (typeof updateAllCharts === 'function') updateAllCharts(data);
  }

  function setConnected(yes) {
    if (!els.statusDot || !els.statusTxt) return;
    if (yes) {
      els.statusDot.className = 'status-dot connected';
      els.statusTxt.textContent = 'Live';
    } else {
      els.statusDot.className = 'status-dot error';
      els.statusTxt.textContent = 'Disconnected';
    }
  }

  function formatBytes(b) {
    if (b < 1024)       return b + ' B';
    if (b < 1048576)    return (b / 1024).toFixed(1) + ' KB';
    if (b < 1073741824) return (b / 1048576).toFixed(1) + ' MB';
    return (b / 1073741824).toFixed(2) + ' GB';
  }

  return { update, setConnected };
})();
// charts.js — Day 4/5/6: Live Chart.js analytics for PacketPulse

const CHART_COLORS = {
  TCP:   '#00f5c4',
  UDP:   '#7b61ff',
  ICMP:  '#ff6b6b',
  ARP:   '#ffd93d',
  OTHER: '#4a9eff',
};

const SPARKLINE_MAX = 30;

// ─────────────────────────────────────────────
// 1. Protocol Distribution — Donut
// ─────────────────────────────────────────────
let protocolChart = null;

function initProtocolChart() {
  const ctx = document.getElementById('protocolChart');
  if (!ctx) return;

  protocolChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['TCP', 'UDP', 'ICMP', 'ARP', 'OTHER'],
      datasets: [{
        data: [0, 0, 0, 0, 0],
        backgroundColor: Object.values(CHART_COLORS),
        borderColor: '#0a0e1a',
        borderWidth: 3,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      animation: { duration: 400, easing: 'easeOutQuart' },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#8892a4',
            font: { family: 'JetBrains Mono, monospace', size: 11 },
            padding: 14,
            usePointStyle: true,
            pointStyleWidth: 8,
          }
        },
        tooltip: {
          backgroundColor: '#0d1117',
          borderColor: '#1e2d3d',
          borderWidth: 1,
          titleColor: '#00f5c4',
          bodyColor: '#c9d1d9',
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.parsed} pkts (${
              Math.round(ctx.parsed / Math.max(ctx.dataset.data.reduce((a,b)=>a+b,0),1)*100)
            }%)`
          }
        }
      }
    }
  });
}

function updateProtocolChart(byProtocol) {
  if (!protocolChart) return;
  const keys = ['TCP', 'UDP', 'ICMP', 'ARP', 'OTHER'];
  protocolChart.data.datasets[0].data = keys.map(k => byProtocol[k] || 0);
  protocolChart.update('none');
}

// ─────────────────────────────────────────────
// 2. Traffic Sparkline — packets/sec over time
// ─────────────────────────────────────────────
let sparklineChart  = null;
const sparklineData = new Array(SPARKLINE_MAX).fill(0);
const sparklineLabels = new Array(SPARKLINE_MAX).fill('');
let lastPacketCount = 0;

function initSparklineChart() {
  const ctx = document.getElementById('sparklineChart');
  if (!ctx) return;

  sparklineChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: sparklineLabels,
      datasets: [{
        label: 'Packets/sec',
        data: sparklineData,
        borderColor: '#00f5c4',
        backgroundColor: 'rgba(0,245,196,0.08)',
        borderWidth: 2,
        pointRadius: 0,
        fill: true,
        tension: 0.4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: {
        x: { display: false },
        y: {
          min: 0,
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            color: '#8892a4',
            font: { family: 'JetBrains Mono, monospace', size: 10 },
            maxTicksLimit: 4,
          }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0d1117',
          borderColor: '#1e2d3d',
          borderWidth: 1,
          titleColor: '#00f5c4',
          bodyColor: '#c9d1d9',
        }
      }
    }
  });
}

function pushSparklinePoint(pps) {
  sparklineData.push(pps);
  sparklineData.shift();
  sparklineLabels.push(new Date().toLocaleTimeString());
  sparklineLabels.shift();
  if (sparklineChart) sparklineChart.update('none');
}

// ─────────────────────────────────────────────
// 3. Top Hosts — Horizontal Bar
// ─────────────────────────────────────────────
let hostsChart = null;

function initHostsChart() {
  const ctx = document.getElementById('hostsChart');
  if (!ctx) return;

  hostsChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: [],
      datasets: [{
        label: 'Packets',
        data: [],
        backgroundColor: 'rgba(123,97,255,0.7)',
        borderColor: '#7b61ff',
        borderWidth: 1,
        borderRadius: 4,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            color: '#8892a4',
            font: { family: 'JetBrains Mono, monospace', size: 10 },
          }
        },
        y: {
          grid: { display: false },
          ticks: {
            color: '#c9d1d9',
            font: { family: 'JetBrains Mono, monospace', size: 10 },
          }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0d1117',
          borderColor: '#1e2d3d',
          borderWidth: 1,
          titleColor: '#7b61ff',
          bodyColor: '#c9d1d9',
        }
      }
    }
  });
}

function updateHostsChart(byProtocol) {
  if (!hostsChart) return;
  // Build top hosts from packet buffer tracked in window._hostCounts
  const hostCounts = window._hostCounts || {};
  const sorted = Object.entries(hostCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);
  hostsChart.data.labels   = sorted.map(([ip]) => ip);
  hostsChart.data.datasets[0].data = sorted.map(([, count]) => count);
  hostsChart.update('none');
}

// ─────────────────────────────────────────────
// 4. Bytes Gauge — doughnut as gauge
// ─────────────────────────────────────────────
let bytesGauge = null;
let peakBytes  = 1;

function initBytesGauge() {
  const ctx = document.getElementById('bytesGauge');
  if (!ctx) return;

  bytesGauge = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [0, 100],
        backgroundColor: ['#4a9eff', 'rgba(255,255,255,0.05)'],
        borderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      circumference: 180,
      rotation: -90,
      cutout: '78%',
      animation: { duration: 600, easing: 'easeOutCubic' },
      plugins: { legend: { display: false }, tooltip: { enabled: false } }
    }
  });
}

function updateBytesGauge(totalBytes) {
  if (!bytesGauge) return;
  if (totalBytes > peakBytes) peakBytes = totalBytes;
  const pct = Math.min((totalBytes / peakBytes) * 100, 100);
  bytesGauge.data.datasets[0].data = [pct, 100 - pct];
  bytesGauge.update('none');

  const label = document.getElementById('bytesGaugeLabel');
  if (label) label.textContent = formatBytes(totalBytes);
}

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────
function formatBytes(b) {
  if (b < 1024)            return `${b} B`;
  if (b < 1024 * 1024)    return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / 1024 / 1024).toFixed(2)} MB`;
}

// ─────────────────────────────────────────────
// Init all charts + sparkline ticker
// ─────────────────────────────────────────────
function initAllCharts() {
  initProtocolChart();
  initSparklineChart();
  initHostsChart();
  initBytesGauge();

  // Tick sparkline every second
  setInterval(() => {
    const currentCount = window._totalPackets || 0;
    const pps = Math.max(0, currentCount - lastPacketCount);
    lastPacketCount = currentCount;
    pushSparklinePoint(pps);
  }, 1000);
}

// ─────────────────────────────────────────────
// Public Charts object — called from app.js
// ─────────────────────────────────────────────
const Charts = {

  // Called once on startup
  init() {
    initAllCharts();
  },

  // Called for every new packet (to track host counts)
  addPacket(pkt) {
    if (!pkt || !pkt.src_ip) return;
    if (!window._hostCounts) window._hostCounts = {};
    window._hostCounts[pkt.src_ip] = (window._hostCounts[pkt.src_ip] || 0) + 1;
  },

  // Called every 2s with stats from server
  updateStats(stats) {
    if (!stats) return;
    window._totalPackets = stats.total_packets || 0;
    updateProtocolChart(stats.by_protocol || {});
    updateHostsChart(stats.by_protocol || {});
    updateBytesGauge(stats.total_bytes || 0);
  }
};

// Auto-init when DOM is ready
document.addEventListener('DOMContentLoaded', () => Charts.init());
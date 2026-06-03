/**
 * frontend/js/inspector.js  —  Day 5
 * Packet inspector panel with geo IP lookup.
 * Works alongside the existing Day 4 JS files.
 */

const KNOWN_PORTS = new Set([
  20, 21, 22, 23, 25, 53, 67, 68, 80, 110, 143,
  194, 443, 465, 587, 993, 995, 3306, 3389, 5432, 8080, 8443
]);

// ── Open / Close ──
function hideInspector() {
  document.getElementById('ins-overlay').classList.remove('show');
  document.getElementById('inspector').classList.remove('open');
}

// Called from table.js when a row is clicked
window.showInspector = function(p) {
  document.getElementById('ins-overlay').classList.add('show');
  document.getElementById('inspector').classList.add('open');
  renderInspector(p);
};

// ── Close handlers ──
document.getElementById('insClose').addEventListener('click', hideInspector);
document.getElementById('ins-overlay').addEventListener('click', hideInspector);

// ── Render ──
function renderInspector(p) {
  const body  = document.getElementById('ins-body');
  const src   = p.src_port ? `${p.src_ip}:${p.src_port}` : (p.src_ip || '—');
  const dst   = p.dst_port ? `${p.dst_ip}:${p.dst_port}` : (p.dst_ip || '—');
  const flags = (p.flags || [])
    .map(f => `<span class="iflag iflag-${f}">${f}</span>`).join(' ')
    || '<span class="inone">none</span>';
  const warn  = p.dst_port && p.dst_port > 1024 && !KNOWN_PORTS.has(p.dst_port)
    ? `<div class="ins-warn">⚠ Unusual destination port <strong>${p.dst_port}</strong> — not a well-known service</div>`
    : '';

  body.innerHTML = `

    <!-- Traffic Flow -->
    <div class="ins-sec">
      <div class="ins-sec-label">Traffic Flow</div>
      <div class="flow-row">
        <div class="flow-ip flow-src">${src}</div>
        <div class="flow-arrow">→</div>
        <div class="flow-ip flow-dst">${dst}</div>
      </div>
    </div>

    <!-- Packet Details -->
    <div class="ins-sec">
      <div class="ins-sec-label">Packet Details</div>
      <div class="kv-grid">
        ${kv('Protocol',  insBadge(p.protocol))}
        ${kv('Service',   p.service || 'Unknown')}
        ${kv('Size',      (p.size || 0) + ' bytes')}
        ${kv('TTL',       p.ttl || '—')}
        ${kv('Timestamp', (p.timestamp || '—').replace('T', ' ').replace('Z', ''))}
        ${kv('TCP Flags', flags)}
      </div>
    </div>

    <!-- Geo IP -->
    <div class="ins-sec" id="ins-geo">
      <div class="ins-sec-label">Geo IP Lookup</div>
      <div class="geo-loading">
        <span class="geo-spin">⟳</span> Looking up locations...
      </div>
    </div>

    <!-- Payload hex -->
    ${p.payload_preview ? `
    <div class="ins-sec">
      <div class="ins-sec-label">Payload Preview (hex)</div>
      <div class="hex-block">${fmtHex(p.payload_preview)}</div>
    </div>` : ''}

    ${warn}
  `;

  // Fetch geo async
  fetchGeo(p.src_ip, p.dst_ip);
}

// ── Geo fetch ──
async function fetchGeo(src, dst) {
  try {
    const res  = await fetch(`/api/geo/both/${src}/${dst}`);
    const data = await res.json();
    const el   = document.getElementById('ins-geo');
    if (!el) return;

    const sg = data.src || {};
    const dg = data.dst || {};

    el.innerHTML = `
      <div class="ins-sec-label">Geo IP Lookup</div>
      <div class="geo-grid">
        <div class="geo-card">
          <div class="geo-role">Source</div>
          <div class="geo-ip src-c">${src}</div>
          <div class="geo-flag">${sg.flag || '🌐'}</div>
          <div class="geo-loc">${sg.city ? sg.city + ', ' : ''}${sg.country || 'Unknown'}</div>
          <div class="geo-org">${sg.org || sg.isp || ''}</div>
        </div>
        <div class="geo-divider">↔</div>
        <div class="geo-card">
          <div class="geo-role">Destination</div>
          <div class="geo-ip dst-c">${dst}</div>
          <div class="geo-flag">${dg.flag || '🌐'}</div>
          <div class="geo-loc">${dg.city ? dg.city + ', ' : ''}${dg.country || 'Unknown'}</div>
          <div class="geo-org">${dg.org || dg.isp || ''}</div>
        </div>
      </div>
    `;
  } catch (e) {
    const el = document.getElementById('ins-geo');
    if (el) el.innerHTML += '<div class="inone" style="margin-top:8px">Could not fetch geo data</div>';
  }
}

// ── Helpers ──
function kv(label, value) {
  return `<div class="kv-row">
    <div class="kv-label">${label}</div>
    <div class="kv-value">${value}</div>
  </div>`;
}

function insBadge(proto) {
  const map = {
    TCP:  'color:#60a5fa;background:#1e3a5f;border:1px solid #1d4ed855',
    UDP:  'color:#4ade80;background:#052e16;border:1px solid #16a34a55',
    ICMP: 'color:#fbbf24;background:#1c1004;border:1px solid #d9770655',
    DNS:  'color:#c084fc;background:#1e1033;border:1px solid #7c3aed55',
    ARP:  'color:#f472b6;background:#2d0a1e;border:1px solid #be185d55',
  };
  const s = map[proto] || 'color:#94a3b8;background:#1e2130;border:1px solid #2a2d3a';
  return `<span style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;${s}">${proto}</span>`;
}

function fmtHex(hex) {
  return (hex.match(/.{1,2}/g) || [])
    .map((b, i) => `<span class="hbyte">${b}</span>${(i + 1) % 16 === 0 ? '<br>' : ' '}`)
    .join('');
}
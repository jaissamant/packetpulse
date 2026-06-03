/**
 * frontend/js/table.js  (Day 5 update)
 * Same as Day 4 but rows now open the inspector on click.
 */

const Table = (() => {
  const MAX_ROWS   = 200;
  let allPackets   = [];
  let activeFilter = 'ALL';
  let searchTerm   = '';
  let autoScroll   = true;
  let isPaused     = false;

  const tbody    = document.getElementById('packetTableBody');
  const tableWrap= document.querySelector('.table-scroll');

  // ── Filter ──
  function setFilter(f) {
    activeFilter = f;
    document.querySelectorAll('.proto-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.proto === f);
    });
    renderFull();
  }

  // ── Search ──
  function setSearch(term) {
    searchTerm = term.toLowerCase();
    renderFull();
  }

  // ── Add packet ──
  function addPacket(pkt) {
    allPackets.push(pkt);
    if (allPackets.length > MAX_ROWS) allPackets.shift();
    if (isPaused || !matchesFilter(pkt)) return;
    clearEmpty();
    const tr = buildRow(pkt);
    tbody.appendChild(tr);
    while (tbody.rows.length > MAX_ROWS) tbody.deleteRow(0);
    if (autoScroll) scrollBottom();
  }

  // ── Load history ──
  function loadHistory(packets) {
    allPackets = packets.slice(-MAX_ROWS);
    renderFull();
  }

  // ── Full re-render ──
  function renderFull() {
    const filtered = allPackets.filter(matchesFilter);
    if (filtered.length === 0) { showEmpty(); return; }
    tbody.innerHTML = '';
    filtered.forEach(p => tbody.appendChild(buildRow(p)));
    scrollBottom();
  }

  // ── Build row ──
  function buildRow(p) {
    const tr   = document.createElement('tr');
    const time = p.timestamp ? p.timestamp.substring(11, 19) : '—';
    const src  = p.src_port  ? `${p.src_ip}:${p.src_port}` : (p.src_ip || '—');
    const dst  = p.dst_port  ? `${p.dst_ip}:${p.dst_port}` : (p.dst_ip || '—');
    const svc  = (p.service && p.service !== 'Unknown') ? p.service : '';

    tr.innerHTML = `
      <td>${time}</td>
      <td>${protoBadge(p.protocol)}</td>
      <td title="${src}">${src}</td>
      <td title="${dst}">${dst}</td>
      <td>${p.size}B</td>
      <td>${svc}</td>
    `;

    // Day 5: open inspector on click
    tr.addEventListener('click', () => {
      if (window.showInspector) window.showInspector(p);
    });

    return tr;
  }

  // ── Protocol badge ──
  function protoBadge(proto) {
    const map = {
      TCP:  'proto-tcp',
      UDP:  'proto-udp',
      ICMP: 'proto-icmp',
      ARP:  'proto-arp',
      DNS:  'proto-dns',
    };
    const cls = map[proto] || 'proto-other';
    return `<span class="proto-badge ${cls}">${proto}</span>`;
  }

  // ── Filter match ──
  function matchesFilter(p) {
    if (activeFilter !== 'ALL' && p.protocol !== activeFilter) return false;
    if (searchTerm) {
      const hay = `${p.src_ip||''} ${p.dst_ip||''} ${p.protocol||''} ${p.service||''}`.toLowerCase();
      if (!hay.includes(searchTerm)) return false;
    }
    return true;
  }

  // ── Helpers ──
  function showEmpty() {
    tbody.innerHTML = `<tr class="empty-row">
      <td colspan="6" style="text-align:center;padding:40px;color:#4a5568;">
        📡 Waiting for packets…
      </td></tr>`;
  }

  function clearEmpty() {
    const empty = tbody.querySelector('.empty-row');
    if (empty) empty.remove();
  }

  function scrollBottom() {
    if (tableWrap) tableWrap.scrollTop = tableWrap.scrollHeight;
  }

  // Pause auto-scroll when user scrolls up
  if (tableWrap) {
    tableWrap.addEventListener('scroll', () => {
      autoScroll = tableWrap.scrollHeight - tableWrap.scrollTop
        - tableWrap.clientHeight < 60;
    });
  }

  showEmpty();

  return { setFilter, setSearch, addPacket, loadHistory };
})();
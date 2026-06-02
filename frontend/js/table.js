/**
 * frontend/js/table.js
 * Manages the live packet feed table — rendering, filtering,
 * auto-scroll, and search.
 */

const Table = (() => {
  const MAX_ROWS   = 200;
  let allPackets   = [];
  let activeFilter = 'ALL';
  let searchTerm   = '';
  let autoScroll   = true;

  const tbody    = document.getElementById('packetTableBody');
  const tableWrap = document.querySelector('.table-scroll');

  // ── Filter ──
  function setFilter(f) {
    activeFilter = f;
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

    if (!matchesFilter(pkt)) return;

    clearEmpty();
    const tr = document.createElement('tr');
    tr.innerHTML = rowHTML(pkt);
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

    if (filtered.length === 0) {
      showEmpty();
      return;
    }

    tbody.innerHTML = filtered.map(p =>
      `<tr>${rowHTML(p)}</tr>`
    ).join('');

    scrollBottom();
  }

  // ── Row HTML ──
  function rowHTML(p) {
    const time = p.timestamp ? p.timestamp.substring(11, 19) : '—';
    const src  = p.src_port  ? `${p.src_ip}:${p.src_port}` : (p.src_ip || '—');
    const dst  = p.dst_port  ? `${p.dst_ip}:${p.dst_port}` : (p.dst_ip || '—');
    const svc  = (p.service && p.service !== 'Unknown') ? p.service : '';

    return `
      <td>${time}</td>
      <td>${badgeHTML(p.protocol)}</td>
      <td title="${src}">${src}</td>
      <td title="${dst}">${dst}</td>
      <td class="size-cell">${p.size}B</td>
      <td class="svc-cell">${svc}</td>
    `;
  }

  // ── Protocol badge ──
  function badgeHTML(proto) {
    const known = ['TCP','UDP','ICMP','ARP'];
    const cls = known.includes(proto) ? proto : 'OTHER';
    return `<span class="proto-badge ${cls}">${proto}</span>`;
  }

  // ── Filter match ──
  function matchesFilter(p) {
    if (activeFilter !== 'ALL' && p.protocol !== activeFilter) return false;
    if (searchTerm) {
      const hay = `${p.src_ip} ${p.dst_ip} ${p.protocol} ${p.service}`.toLowerCase();
      if (!hay.includes(searchTerm)) return false;
    }
    return true;
  }

  // ── Helpers ──
  function showEmpty() {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--text-dim)">
      Waiting for packets…
    </td></tr>`;
  }

  function clearEmpty() {
    const empty = tbody.querySelector('td[colspan]');
    if (empty) tbody.innerHTML = '';
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
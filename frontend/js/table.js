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
  let isPaused     = false;

  const tbody      = document.getElementById('packet-table');
  const countEl    = document.getElementById('packet-count');
  const pauseBanner= document.getElementById('pause-banner');
  const tableWrap  = document.getElementById('table-wrap');

  // ── Filter ──
  function setFilter(f) {
    activeFilter = f;
    document.querySelectorAll('.filter-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.filter === f);
    });
    renderFull();
  }

  // ── Search ──
  function setSearch(term) {
    searchTerm = term.toLowerCase();
    renderFull();
  }

  // ── Pause / Resume ──
  function togglePause() {
    isPaused = !isPaused;
    pauseBanner.classList.toggle('show', isPaused);
    document.getElementById('btn-pause').textContent =
      isPaused ? '▶ Resume' : '⏸ Pause';
  }

  // ── Add packet ──
  function addPacket(pkt) {
    allPackets.push(pkt);
    if (allPackets.length > MAX_ROWS) allPackets.shift();

    if (isPaused) return;
    if (!matchesFilter(pkt)) return;

    clearEmpty();
    const tr = document.createElement('tr');
    tr.className = 'new-row';
    tr.innerHTML = rowHTML(pkt);
    tr.addEventListener('click', () => window.Inspector && Inspector.show(pkt));
    tbody.appendChild(tr);

    // Trim
    while (tbody.rows.length > MAX_ROWS) tbody.deleteRow(0);

    updateCount();
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
      updateCount();
      return;
    }

    tbody.innerHTML = filtered.map(p => {
      return `<tr class="new-row">${rowHTML(p)}</tr>`;
    }).join('');

    // Attach click handlers
    tbody.querySelectorAll('tr').forEach((tr, i) => {
      tr.addEventListener('click', () =>
        window.Inspector && Inspector.show(filtered[i])
      );
    });

    updateCount();
    scrollBottom();
  }

  // ── Row HTML ──
  function rowHTML(p) {
    const time  = p.timestamp ? p.timestamp.substring(11, 19) : '—';
    const src   = p.src_port  ? `${p.src_ip}:${p.src_port}` : p.src_ip;
    const dst   = p.dst_port  ? `${p.dst_ip}:${p.dst_port}` : p.dst_ip;
    const flags = (p.flags || []).map(f =>
      `<span class="flag-pill flag-${f}">${f}</span>`
    ).join('');
    const svc   = (p.service && p.service !== 'Unknown') ? p.service : '';

    return `
      <td>${time}</td>
      <td>${badgeHTML(p.protocol)}</td>
      <td class="td-src" title="${src}">${src}</td>
      <td class="td-arrow">→</td>
      <td class="td-dst" title="${dst}">${dst}</td>
      <td class="td-size">${p.size}B</td>
      <td>${flags}</td>
      <td class="td-svc">${svc}</td>
    `;
  }

  // ── Badge ──
  function badgeHTML(proto) {
    const cls = ['TCP','UDP','ICMP','DNS','ARP'].includes(proto)
      ? `b-${proto}` : 'b-def';
    return `<span class="badge ${cls}">${proto}</span>`;
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
    tbody.innerHTML = `<tr><td colspan="8">
      <div class="empty-state">
        <div class="empty-icon">📡</div>
        <div class="empty-title">Waiting for packets...</div>
        <div class="empty-sub">Open a browser tab or browse the web</div>
      </div></td></tr>`;
  }

  function clearEmpty() {
    if (tbody.querySelector('.empty-state')) tbody.innerHTML = '';
  }

  function scrollBottom() {
    tableWrap.scrollTop = tableWrap.scrollHeight;
  }

  function updateCount() {
    const n = allPackets.filter(matchesFilter).length;
    countEl.textContent = `${n.toLocaleString()} packets`;
  }

  // Pause auto-scroll when user scrolls up
  tableWrap.addEventListener('scroll', () => {
    autoScroll = tableWrap.scrollHeight - tableWrap.scrollTop
      - tableWrap.clientHeight < 60;
  });

  // Init empty state
  showEmpty();

  return { setFilter, setSearch, addPacket, loadHistory, togglePause };
})();
# analytics.py — Day 4: Server-side analytics engine for PacketPulse

from collections import defaultdict, deque
from threading import Lock
import time


class Analytics:
    """
    Tracks rolling analytics over a sliding time window.
    Thread-safe — updated from the capture thread, read from Flask routes.
    """

    WINDOW_SECONDS = 60  # rolling window for rate calculations

    def __init__(self):
        self._lock = Lock()

        # Cumulative counters
        self.total_packets = 0
        self.total_bytes = 0

        # Protocol breakdown
        self.by_protocol: dict[str, int] = defaultdict(int)

        # Top talkers
        self.top_src_ips: dict[str, int] = defaultdict(int)
        self.top_dst_ips: dict[str, int] = defaultdict(int)

        # Rolling window: deque of (timestamp, bytes) tuples
        self._window: deque[tuple[float, int]] = deque()

        # Packets/sec ring buffer (last 60 readings, one per second)
        self._pps_ring: deque[int] = deque(maxlen=60)
        self._last_tick = time.time()
        self._packets_since_tick = 0

        # Service distribution
        self.by_service: dict[str, int] = defaultdict(int)

    # ──────────────────────────────────────────────
    # Feed a packet dict in from the capture engine
    # ──────────────────────────────────────────────
    def ingest(self, pkt: dict) -> None:
        size = pkt.get("size", 0)
        proto = pkt.get("protocol", "OTHER")
        src = pkt.get("src_ip", "")
        dst = pkt.get("dst_ip", "")
        svc = pkt.get("service", "OTHER")
        now = time.time()

        with self._lock:
            self.total_packets += 1
            self.total_bytes += size
            self.by_protocol[proto] += 1
            self.by_service[svc] += 1

            if src:
                self.top_src_ips[src] += 1
            if dst:
                self.top_dst_ips[dst] += 1

            # Rolling window for bandwidth
            self._window.append((now, size))
            self._trim_window(now)

            # pps tick
            self._packets_since_tick += 1
            elapsed = now - self._last_tick
            if elapsed >= 1.0:
                self._pps_ring.append(
                    int(self._packets_since_tick / elapsed)
                )
                self._packets_since_tick = 0
                self._last_tick = now

    # ──────────────────────────────────────────────
    # Snapshot for the /api/stats endpoint
    # ──────────────────────────────────────────────
    def snapshot(self) -> dict:
        now = time.time()
        with self._lock:
            self._trim_window(now)

            window_bytes = sum(b for _, b in self._window)
            window_pkts = len(self._window)
            elapsed = min(self.WINDOW_SECONDS, max(1, now - (
                self._window[0][0] if self._window else now
            )))

            bps = window_bytes / elapsed if elapsed > 0 else 0
            pps_now = self._pps_ring[-1] if self._pps_ring else 0
            pps_avg = (
                int(sum(self._pps_ring) / len(self._pps_ring))
                if self._pps_ring else 0
            )

            top_src = dict(
                sorted(self.top_src_ips.items(), key=lambda x: -x[1])[:10]
            )
            top_dst = dict(
                sorted(self.top_dst_ips.items(), key=lambda x: -x[1])[:10]
            )

            return {
                "total_packets": self.total_packets,
                "total_bytes": self.total_bytes,
                "by_protocol": dict(self.by_protocol),
                "by_service": dict(self.by_service),
                "top_src_ips": top_src,
                "top_dst_ips": top_dst,
                "bandwidth_bps": round(bps, 1),
                "pps_current": pps_now,
                "pps_average": pps_avg,
                "window_packets": window_pkts,
                "window_bytes": window_bytes,
            }

    # ──────────────────────────────────────────────
    # Reset (useful for testing / clear button)
    # ──────────────────────────────────────────────
    def reset(self) -> None:
        with self._lock:
            self.total_packets = 0
            self.total_bytes = 0
            self.by_protocol.clear()
            self.by_service.clear()
            self.top_src_ips.clear()
            self.top_dst_ips.clear()
            self._window.clear()
            self._pps_ring.clear()
            self._packets_since_tick = 0
            self._last_tick = time.time()

    # ──────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────
    def _trim_window(self, now: float) -> None:
        cutoff = now - self.WINDOW_SECONDS
        while self._window and self._window[0][0] < cutoff:
            self._window.popleft()
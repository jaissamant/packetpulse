"""
api/alerts.py  —  Day 6
-----------------------
Rule-based alert engine for PacketPulse.
Detects: high traffic rate, port scans, suspicious ports, unknown protocols.
"""

import time
import threading
from collections import defaultdict, deque
from datetime import datetime

# ── Alert severity levels ──
INFO     = "info"
WARNING  = "warning"
CRITICAL = "critical"

# ── Well-known safe ports ──
SAFE_PORTS = {
    20, 21, 22, 23, 25, 53, 67, 68, 80, 110,
    143, 194, 443, 465, 587, 993, 995, 1080,
    3306, 3389, 5432, 8080, 8443, 27017
}

# ── Suspicious ports (common attack vectors) ──
SUSPICIOUS_PORTS = {
    23: "Telnet (unencrypted)",
    135: "MS RPC",
    137: "NetBIOS",
    138: "NetBIOS",
    139: "NetBIOS",
    445: "SMB (ransomware vector)",
    1433: "MSSQL",
    3389: "RDP (brute-force target)",
    4444: "Metasploit default",
    5900: "VNC",
    6667: "IRC (botnet C2)",
    31337: "Back Orifice",
}


class AlertEngine:
    """
    Monitors packet stream and fires alerts based on rules.
    Thread-safe.
    """

    def __init__(self, max_alerts: int = 100):
        self.max_alerts  = max_alerts
        self.alerts      = deque(maxlen=max_alerts)
        self._lock       = threading.Lock()
        self._callbacks  = []

        # State for port scan detection
        # src_ip → set of dst_ports seen in last 10s
        self._port_scan_tracker: dict[str, dict] = defaultdict(
            lambda: {"ports": set(), "last_reset": time.time()}
        )

        # State for traffic rate alerts
        self._pkt_timestamps: deque = deque(maxlen=500)
        self._last_high_traffic_alert = 0

        # Thresholds (tunable)
        self.thresholds = {
            "high_traffic_pps":  50,    # packets/sec
            "port_scan_ports":   10,    # unique ports in 10s = port scan
            "port_scan_window":  10,    # seconds
        }

    # ── Public API ──

    def on_alert(self, callback):
        """Register a callback fired on every new alert."""
        self._callbacks.append(callback)

    def process_packet(self, pkt: dict):
        """Feed a packet into the alert engine. Call for every packet."""
        self._pkt_timestamps.append(time.time())
        self._check_high_traffic()
        self._check_suspicious_port(pkt)
        self._check_port_scan(pkt)
        self._check_suspicious_protocol(pkt)

    def get_alerts(self, limit: int = 50) -> list:
        with self._lock:
            return list(self.alerts)[-limit:]

    def get_alert_counts(self) -> dict:
        with self._lock:
            counts = {INFO: 0, WARNING: 0, CRITICAL: 0}
            for a in self.alerts:
                counts[a["severity"]] = counts.get(a["severity"], 0) + 1
            return counts

    def update_thresholds(self, new_thresholds: dict):
        self.thresholds.update(new_thresholds)

    def clear_alerts(self):
        with self._lock:
            self.alerts.clear()

    # ── Rules ──

    def _check_high_traffic(self):
        now = time.time()
        one_sec_ago = now - 1.0
        recent = sum(1 for t in self._pkt_timestamps if t >= one_sec_ago)

        if recent >= self.thresholds["high_traffic_pps"]:
            # Throttle: max one alert per 5 seconds
            if now - self._last_high_traffic_alert > 5:
                self._last_high_traffic_alert = now
                self._fire(
                    severity=WARNING,
                    title="High Traffic Rate",
                    message=f"{recent} packets/sec — above threshold of {self.thresholds['high_traffic_pps']}",
                    category="traffic",
                )

    def _check_suspicious_port(self, pkt: dict):
        dst_port = pkt.get("dst_port")
        if not dst_port:
            return
        if dst_port in SUSPICIOUS_PORTS:
            desc = SUSPICIOUS_PORTS[dst_port]
            self._fire(
                severity=WARNING,
                title="Suspicious Port Detected",
                message=f"Traffic to port {dst_port} ({desc}) from {pkt.get('src_ip','?')}",
                category="port",
                packet=pkt,
            )

    def _check_port_scan(self, pkt: dict):
        src_ip   = pkt.get("src_ip")
        dst_port = pkt.get("dst_port")
        if not src_ip or not dst_port:
            return

        tracker = self._port_scan_tracker[src_ip]
        now     = time.time()

        # Reset window if expired
        if now - tracker["last_reset"] > self.thresholds["port_scan_window"]:
            tracker["ports"]      = set()
            tracker["last_reset"] = now

        tracker["ports"].add(dst_port)

        if len(tracker["ports"]) >= self.thresholds["port_scan_ports"]:
            self._fire(
                severity=CRITICAL,
                title="Port Scan Detected",
                message=f"{src_ip} scanned {len(tracker['ports'])} ports in {self.thresholds['port_scan_window']}s",
                category="scan",
                packet=pkt,
            )
            # Reset to avoid spam
            tracker["ports"]      = set()
            tracker["last_reset"] = now

    def _check_suspicious_protocol(self, pkt: dict):
        proto = pkt.get("protocol", "")
        known = {"TCP", "UDP", "ICMP", "ARP", "DNS", "IPv6",
                 "GRE", "ESP", "ICMPv6"}
        if proto and proto not in known and not proto.startswith("PROTO"):
            self._fire(
                severity=INFO,
                title="Unknown Protocol",
                message=f"Unusual protocol detected: {proto} from {pkt.get('src_ip','?')}",
                category="protocol",
                packet=pkt,
            )

    # ── Internal ──

    def _fire(self, severity: str, title: str, message: str,
              category: str, packet: dict = None):
        alert = {
            "id":        id(object()),
            "severity":  severity,
            "title":     title,
            "message":   message,
            "category":  category,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "packet":    packet,
        }
        with self._lock:
            self.alerts.append(alert)

        for cb in self._callbacks:
            try:
                cb(alert)
            except Exception as e:
                print(f"[AlertEngine] Callback error: {e}")
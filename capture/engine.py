"""
capture/engine.py
-----------------
Core packet capture engine using Scapy.
Captures live packets, parses them into clean dicts,
and pushes them to registered callbacks.
"""
 
import threading
import time
from datetime import datetime
from collections import deque
 
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, DNS, Raw
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
 
 
# Protocol number → name mapping
PROTOCOL_MAP = {
    1:  "ICMP",
    6:  "TCP",
    17: "UDP",
    41: "IPv6",
    47: "GRE",
    50: "ESP",
    58: "ICMPv6",
}
 
# Well-known port → service name
SERVICE_MAP = {
    20:  "FTP-data",
    21:  "FTP",
    22:  "SSH",
    23:  "Telnet",
    25:  "SMTP",
    53:  "DNS",
    67:  "DHCP",
    68:  "DHCP",
    80:  "HTTP",
    110: "POP3",
    143: "IMAP",
    194: "IRC",
    443: "HTTPS",
    465: "SMTPS",
    587: "SMTP",
    993: "IMAPS",
    995: "POP3S",
    1433: "MSSQL",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    27017: "MongoDB",
}
 
 
def parse_packet(pkt) -> dict | None:
    """
    Parse a raw Scapy packet into a clean, JSON-serialisable dict.
    Returns None if the packet has no IP layer (e.g. pure L2 broadcast).
    """
    if not pkt.haslayer(IP):
        return None
 
    ip_layer = pkt[IP]
    proto_num = ip_layer.proto
    proto_name = PROTOCOL_MAP.get(proto_num, f"PROTO-{proto_num}")
 
    # Ports (only TCP/UDP carry them)
    src_port = dst_port = None
    flags = []
 
    if pkt.haslayer(TCP):
        tcp = pkt[TCP]
        src_port = tcp.sport
        dst_port = tcp.dport
        # Decode TCP flags into readable list
        flag_map = {
            "F": "FIN", "S": "SYN", "R": "RST",
            "P": "PSH", "A": "ACK", "U": "URG",
        }
        flags = [flag_map[f] for f in flag_map if f in str(tcp.flags)]
 
    elif pkt.haslayer(UDP):
        udp = pkt[UDP]
        src_port = udp.sport
        dst_port = udp.dport
 
    # Service name from either port
    service = (
        SERVICE_MAP.get(dst_port)
        or SERVICE_MAP.get(src_port)
        or "Unknown"
    )
 
    # Payload preview (first 64 bytes, hex-encoded)
    payload_hex = ""
    if pkt.haslayer(Raw):
        raw_data = bytes(pkt[Raw])[:64]
        payload_hex = raw_data.hex()
 
    # Packet size
    pkt_size = len(pkt)
 
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "src_ip":    ip_layer.src,
        "dst_ip":    ip_layer.dst,
        "protocol":  proto_name,
        "proto_num": proto_num,
        "src_port":  src_port,
        "dst_port":  dst_port,
        "service":   service,
        "size":      pkt_size,
        "ttl":       ip_layer.ttl,
        "flags":     flags,
        "payload_preview": payload_hex,
    }
 
 
class PacketCapture:
    """
    Thread-safe packet capture engine.
 
    Usage:
        cap = PacketCapture(interface="eth0", buffer_size=500)
        cap.on_packet(my_callback)   # register a callback
        cap.start()
        ...
        cap.stop()
    """
 
    def __init__(self, interface: str = None, buffer_size: int = 500):
        self.interface   = interface          # None = sniff all interfaces
        self.buffer_size = buffer_size
        self._callbacks  = []
        self._running    = False
        self._thread     = None
        self._lock       = threading.Lock()
 
        # Circular buffer holding last N parsed packets
        self.packet_buffer: deque[dict] = deque(maxlen=buffer_size)
 
        # Simple live stats
        self.stats = {
            "total_packets": 0,
            "total_bytes":   0,
            "by_protocol":   {},   # proto_name → count
            "start_time":    None,
            "packets_per_sec": 0.0,
        }
        self._pps_window: deque[float] = deque(maxlen=60)  # timestamps for pps calc
 
    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #
 
    def on_packet(self, callback):
        """Register a function to be called with each parsed packet dict."""
        self._callbacks.append(callback)
 
    def start(self):
        """Start capturing packets in a background thread."""
        if self._running:
            return
        if not SCAPY_AVAILABLE:
            raise RuntimeError(
                "Scapy is not installed. Run: pip install scapy"
            )
        self._running = True
        self.stats["start_time"] = datetime.utcnow().isoformat() + "Z"
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        print(f"[PacketCapture] Started on interface: {self.interface or 'all'}")
 
    def stop(self):
        """Stop the capture thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        print("[PacketCapture] Stopped.")
 
    def get_buffer(self) -> list[dict]:
        """Return a snapshot of the current packet buffer (thread-safe)."""
        with self._lock:
            return list(self.packet_buffer)
 
    def get_stats(self) -> dict:
        """Return a copy of the current stats dict."""
        with self._lock:
            stats_copy = dict(self.stats)
            stats_copy["by_protocol"] = dict(self.stats["by_protocol"])
            return stats_copy
 
    def is_running(self) -> bool:
        return self._running
 
    # ------------------------------------------------------------------ #
    #  Internal                                                            #
    # ------------------------------------------------------------------ #
 
    def _capture_loop(self):
        """Main capture loop — runs in a daemon thread."""
        sniff(
            iface=self.interface,
            prn=self._handle_packet,
            store=False,              # don't accumulate in memory
            stop_filter=lambda _: not self._running,
        )
 
    def _handle_packet(self, pkt):
        """Scapy callback — parse, store, and broadcast the packet."""
        parsed = parse_packet(pkt)
        if parsed is None:
            return
 
        with self._lock:
            # Update buffer
            self.packet_buffer.append(parsed)
 
            # Update stats
            self.stats["total_packets"] += 1
            self.stats["total_bytes"]   += parsed["size"]
 
            proto = parsed["protocol"]
            self.stats["by_protocol"][proto] = (
                self.stats["by_protocol"].get(proto, 0) + 1
            )
 
            # Packets-per-second (rolling 1-second window)
            now = time.time()
            self._pps_window.append(now)
            one_sec_ago = now - 1.0
            recent = sum(1 for t in self._pps_window if t >= one_sec_ago)
            self.stats["packets_per_sec"] = float(recent)
 
        # Fire callbacks outside the lock to avoid dead-locks
        for cb in self._callbacks:
            try:
                cb(parsed)
            except Exception as exc:
                print(f"[PacketCapture] Callback error: {exc}")
"""
capture/exporter.py  —  Day 6
-------------------------------
Export captured packets as .csv or .pcap files.
"""

import csv
import io
import json
from datetime import datetime


def export_csv(packets: list[dict]) -> bytes:
    """
    Convert a list of packet dicts to CSV bytes.
    Returns bytes ready to send as a file download.
    """
    if not packets:
        return b""

    output = io.StringIO()
    fields = [
        "timestamp", "src_ip", "src_port",
        "dst_ip", "dst_port", "protocol",
        "service", "size", "ttl", "flags"
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=fields,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()

    for pkt in packets:
        row = dict(pkt)
        # Flatten flags list to string
        if isinstance(row.get("flags"), list):
            row["flags"] = "|".join(row["flags"])
        writer.writerow(row)

    return output.getvalue().encode("utf-8")


def export_pcap(packets: list[dict]) -> bytes:
    """
    Export packets as a minimal .pcap file.
    Uses Scapy if available; falls back to a stub pcap with metadata.
    """
    try:
        from scapy.all import wrpcap, IP, TCP, UDP, ICMP, Ether
        import tempfile, os

        scapy_pkts = []
        for p in packets:
            try:
                ip = IP(src=p.get("src_ip", "0.0.0.0"),
                        dst=p.get("dst_ip", "0.0.0.0"))
                proto = p.get("protocol", "TCP")
                if proto == "TCP":
                    layer = TCP(sport=p.get("src_port") or 0,
                                dport=p.get("dst_port") or 0)
                elif proto == "UDP":
                    layer = UDP(sport=p.get("src_port") or 0,
                                dport=p.get("dst_port") or 0)
                elif proto == "ICMP":
                    layer = ICMP()
                else:
                    layer = TCP()

                pkt = Ether() / ip / layer
                scapy_pkts.append(pkt)
            except Exception:
                continue

        with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as f:
            tmp_path = f.name

        wrpcap(tmp_path, scapy_pkts)

        with open(tmp_path, "rb") as f:
            data = f.read()

        os.unlink(tmp_path)
        return data

    except ImportError:
        # Scapy not available — return JSON as fallback
        return json.dumps(packets, indent=2).encode("utf-8")


def generate_filename(fmt: str) -> str:
    """Generate a timestamped filename."""
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"packetpulse_{ts}.{fmt}"
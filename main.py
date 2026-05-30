"""
main.py
-------
PacketPulse entry point.
Run with:  sudo python main.py
(root/admin required for raw packet capture)
"""
 
import sys
import signal
from capture.engine import PacketCapture, SCAPY_AVAILABLE
 
 
def print_banner():
    banner = r"""
  ____            _        _   ____        _
 |  _ \ __ _  ___| | _____| |_|  _ \ _   _| |___  ___
 | |_) / _` |/ __| |/ / _ \ __| |_) | | | | / __|/ _ \
 |  __/ (_| | (__|   <  __/ |_|  __/| |_| | \__ \  __/
 |_|   \__,_|\___|_|\_\___|\__|_|    \__,_|_|___/\___|
 
  Real-time Network Traffic Visualizer  |  Day 1 — Engine
"""
    print(banner)
 
 
def on_packet(pkt: dict):
    """Simple console printer — will be replaced by WebSocket in Day 2."""
    proto  = pkt["protocol"].ljust(6)
    src    = f"{pkt['src_ip']}:{pkt['src_port'] or '–'}".ljust(24)
    dst    = f"{pkt['dst_ip']}:{pkt['dst_port'] or '–'}".ljust(24)
    size   = str(pkt["size"]).rjust(6)
    svc    = pkt["service"].ljust(12)
    ts     = pkt["timestamp"][11:19]   # HH:MM:SS
 
    print(f"  {ts}  [{proto}]  {src}  →  {dst}  {size}B  {svc}")
 
 
def main():
    print_banner()
 
    if not SCAPY_AVAILABLE:
        print("[ERROR] Scapy not installed. Run:  pip install -r requirements.txt")
        sys.exit(1)
 
    # Pick interface from CLI arg or default (all interfaces)
    interface = sys.argv[1] if len(sys.argv) > 1 else None
 
    cap = PacketCapture(interface=interface or 'Wi-Fi', buffer_size=500)
    cap.on_packet(on_packet)
 
    # Graceful shutdown on Ctrl+C
    def handle_sigint(sig, frame):
        print("\n\n[PacketPulse] Stopping capture...")
        cap.stop()
        stats = cap.get_stats()
        print(f"\n  Packets captured : {stats['total_packets']}")
        print(f"  Total bytes      : {stats['total_bytes']:,}")
        print(f"  By protocol      : {stats['by_protocol']}")
        print("\n  Goodbye!\n")
        sys.exit(0)
 
    signal.signal(signal.SIGINT, handle_sigint)
 
    print(f"  Interface : {interface or 'all (default)'}")
    print(f"  Buffer    : 500 packets")
    print(f"\n  Listening... (Ctrl+C to stop)\n")
    print(f"  {'TIME':8}  {'PROTO':8}  {'SOURCE':24}  {'DESTINATION':24}  {'SIZE':>6}  {'SERVICE':12}")
    print("  " + "─" * 90)
 
    cap.start()
 
    try:
        while cap.is_running():
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        handle_sigint(None, None)
 
 
if __name__ == "__main__":
    main()
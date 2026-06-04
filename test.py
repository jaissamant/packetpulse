from capture.engine import PacketCapture
import time

cap = PacketCapture(interface='Wi-Fi', buffer_size=500)

def on_pkt(p):
    print(f'  {p["protocol"]} {p["src_ip"]} -> {p["dst_ip"]}')

cap.on_packet(on_pkt)
cap.start()
print('Capturing for 10 seconds...')
time.sleep(10)
cap.stop()
print('Stats:', cap.get_stats())
from scapy.all import sniff, conf

print(f"Default interface: {conf.iface}")
print("Sniffing for 5 packets... open your browser!")

pkts = sniff(count=5, store=1)
for p in pkts:
    print(p.summary())

print("Done!")
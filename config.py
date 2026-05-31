"""
config.py
---------
Central configuration for PacketPulse.
"""
 
# Network interface to capture on (set to your interface)
CAPTURE_INTERFACE = "Wi-Fi"
 
# How many packets to keep in memory
BUFFER_SIZE = 500
 
# Flask server settings
HOST = "0.0.0.0"
PORT = 5000
DEBUG = False
 
# How often to emit stats via WebSocket (seconds)
STATS_INTERVAL = 2
 
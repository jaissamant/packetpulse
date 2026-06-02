"""
server.py
---------
PacketPulse Flask + WebSocket server.
Upgraded to Day 4: Full Charts & Analytics Engine Integration.
Run with:  python server.py
"""

import sys
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

from capture.engine import PacketCapture, SCAPY_AVAILABLE
from analytics import Analytics
from api.routes import api_bp, set_capture
from api.socket_events import init_socket, start_stats_broadcast
import config


def create_app():
    app = Flask(__name__, static_folder="frontend", static_url_path="")
    CORS(app)

    # Register REST blueprint
    app.register_blueprint(api_bp)

    # Serve frontend index.html at root
    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app


def main():
    print("""
  ____                     _        _    ____        _       
 |  _ \\ __ _  ___| | _____| |_|  _ \\ _   _| |___  ___ 
 | |_) / _` |/ __| |/ / _ \\ __| |_) | | | | / __|/ _ \\
 |  __/ (_| | (__|   <  __/ |_|  __/| |_| | \\__ \\  __/
 |_|    \\__,_|\\___|_|\\_\\___|\\__|_|    \\__,_|_|___/\\___|
 
   Real-time Network Traffic Visualizer  |  Day 4 — Integrated Engine
""")

    if not SCAPY_AVAILABLE:
        print("[ERROR] Scapy not installed or admin rights missing. Run terminal as Administrator.")
        sys.exit(1)

    # Create Flask app and SocketIO
    app = create_app()
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        logger=False,
        engineio_logger=False,
    )

    # 1. Initialize the Analytics System
    analytics = Analytics()

    # Create packet capture engine
    capture = PacketCapture(
        interface=config.CAPTURE_INTERFACE,
        buffer_size=config.BUFFER_SIZE,
    )

    # 2. Wire up Live Data Pipelines via Callbacks
    def handle_incoming_packet(parsed_pkt):
        analytics.ingest(parsed_pkt)  # Feed the graph processor
        socketio.emit("new_packet", parsed_pkt)  # Stream immediately to front-end table

    capture.on_packet(handle_incoming_packet)

    # 3. Hijack get_stats to feed the frontend rich graph snapshots
    capture.get_stats = analytics.snapshot

    # Wire blueprints and socket endpoints together
    set_capture(capture)
    init_socket(socketio, capture)

    # Start capturing background threads
    capture.start()

    # Start periodic rich stats broadcasting loop
    start_stats_broadcast(interval=config.STATS_INTERVAL)

    print(f"  Interface : {config.CAPTURE_INTERFACE}")
    print(f"  Server    : http://localhost:{config.PORT}")
    print(f"  API       : http://localhost:{config.PORT}/api/status")
    print(f"\n  Open http://localhost:{config.PORT} in your browser!")
    print(f"  Press Ctrl+C to stop.\n")

    # Run server
    socketio.run(
        app,
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
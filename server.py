"""
server.py  —  Day 6 update
---------------------------
Wires PacketCapture → AlertEngine → SocketIO.
"""

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

from capture.engine import PacketCapture
from api.routes import api_bp, set_capture, set_alert_engine
from api.socket_events import init_socket, start_stats_broadcast
from api.alerts import AlertEngine
import config


def create_app():
    app = Flask(__name__, static_folder="frontend", static_url_path="")
    CORS(app)
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app


def main():
    print("""
  ____            _        _   ____        _
 |  _ \\ __ _  ___| | _____| |_|  _ \\ _   _| |___  ___
 | |_) / _` |/ __| |/ / _ \\ __| |_) | | | | / __|/ _ \\
 |  __/ (_| | (__|   <  __/ |_|  __/| |_| | \\__ \\  __/
 |_|   \\__,_|\\___|_|\\_\\___|\\__|_|    \\__,_|_|___/\\___|

  Real-time Network Traffic Visualizer  |  Day 6 — Alerts & Export
""")

    app      = create_app()
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        logger=False,
        engineio_logger=False,
    )

    # Packet capture engine
    capture = PacketCapture(
        interface=config.CAPTURE_INTERFACE,
        buffer_size=config.BUFFER_SIZE,
    )

    # Alert engine
    alert_engine = AlertEngine(max_alerts=100)

    # Feed every packet into the alert engine
    capture.on_packet(alert_engine.process_packet)

    # Broadcast new alerts via WebSocket
    def broadcast_alert(alert):
        socketio.emit("new_alert", alert)

    alert_engine.on_alert(broadcast_alert)

    # Wire everything together
    set_capture(capture)
    set_alert_engine(alert_engine)
    init_socket(socketio, capture)

    # Start capture and stats broadcast
    capture.start()
    start_stats_broadcast(interval=config.STATS_INTERVAL)

    print(f"  Interface : {config.CAPTURE_INTERFACE}")
    print(f"  Server    : http://localhost:{config.PORT}")
    print(f"  API       : http://localhost:{config.PORT}/api/status")
    print(f"  Alerts    : http://localhost:{config.PORT}/api/alerts")
    print(f"  Export    : http://localhost:{config.PORT}/api/export/csv")
    print(f"\n  Open http://localhost:{config.PORT} in your browser!")
    print(f"  Press Ctrl+C to stop.\n")

    socketio.run(
        app,
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )


if __name__ == "__main__":
    main()
"""
server.py
---------
PacketPulse Flask + WebSocket server.
Run with:  python server.py
"""
 
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
 
from capture.engine import PacketCapture
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
  ____            _        _   ____        _
 |  _ \\ __ _  ___| | _____| |_|  _ \\ _   _| |___  ___
 | |_) / _` |/ __| |/ / _ \\ __| |_) | | | | / __|/ _ \\
 |  __/ (_| | (__|   <  __/ |_|  __/| |_| | \\__ \\  __/
 |_|   \\__,_|\\___|_|\\_\\___|\\__|_|    \\__,_|_|___/\\___|
 
  Real-time Network Traffic Visualizer  |  Day 2 — Server
""")
 
    # Create Flask app and SocketIO
    app = create_app()
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        logger=False,
        engineio_logger=False,
    )
 
    # Create packet capture engine
    capture = PacketCapture(
        interface=config.CAPTURE_INTERFACE,
        buffer_size=config.BUFFER_SIZE,
    )
 
    # Wire everything together
    set_capture(capture)
    init_socket(socketio, capture)
 
    # Start capturing
    capture.start()
 
    # Start periodic stats broadcast
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
    )
 
 
if __name__ == "__main__":
    main()
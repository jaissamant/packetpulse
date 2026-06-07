"""
demo_server.py  —  Day 7
-------------------------
PacketPulse Demo Mode — replays mock_data.json without
needing root privileges or Npcap/libpcap installed.
Run with:  python demo_server.py
"""

import json
import time
import threading
import os

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

MOCK_FILE = os.path.join(os.path.dirname(__file__), "demo", "mock_data.json")


def load_mock_data():
    with open(MOCK_FILE, "r") as f:
        return json.load(f)


def create_app():
    app = Flask(__name__, static_folder="frontend", static_url_path="")
    CORS(app)

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    # Minimal API stubs so the frontend doesn't break
    @app.route("/api/status")
    def status():
        from flask import jsonify
        return jsonify({"running": True, "interface": "demo", "buffer_size": 500})

    @app.route("/api/stats")
    def stats():
        from flask import jsonify
        data = load_mock_data()
        return jsonify(data["stats"])

    @app.route("/api/packets")
    def packets():
        from flask import jsonify
        data = load_mock_data()
        return jsonify(data["packets"])

    @app.route("/api/alerts")
    def alerts():
        from flask import jsonify
        return jsonify([])

    @app.route("/api/alerts/counts")
    def alert_counts():
        from flask import jsonify
        return jsonify({"info": 0, "warning": 0, "critical": 0})

    @app.route("/api/geo/both/<src>/<dst>")
    def geo_both(src, dst):
        from flask import jsonify
        # Return stub geo for demo
        return jsonify({
            "src": {"flag": "🌐", "country": "Demo", "city": "", "org": ""},
            "dst": {"flag": "🌐", "country": "Demo", "city": "", "org": ""}
        })

    @app.route("/api/export/csv")
    def export_csv():
        from flask import Response
        data = load_mock_data()
        lines = ["timestamp,src_ip,src_port,dst_ip,dst_port,protocol,service,size\n"]
        for p in data["packets"]:
            lines.append(
                f"{p['timestamp']},{p['src_ip']},{p.get('src_port','')},"
                f"{p['dst_ip']},{p.get('dst_port','')},{p['protocol']},"
                f"{p['service']},{p['size']}\n"
            )
        return Response("".join(lines), mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=demo_capture.csv"})

    return app


def replay_packets(socketio, packets, stats):
    """Replay mock packets in real-time via WebSocket."""
    time.sleep(1)  # wait for client to connect

    # Send history first
    socketio.emit("packet_history", packets[:10])
    socketio.emit("stats_update", stats)

    # Replay remaining packets one by one
    idx = 10
    while True:
        if idx < len(packets):
            socketio.emit("new_packet", packets[idx])
            idx += 1
        else:
            idx = 0  # loop back

        # Update stats periodically
        if idx % 5 == 0:
            stats["total_packets"] += 5
            stats["total_bytes"]   += 3200
            stats["packets_per_sec"] = round(3 + (idx % 8), 1)
            socketio.emit("stats_update", stats)

        time.sleep(0.4)  # replay at ~2.5 packets/sec


def main():
    print("""
  ____            _        _   ____        _
 |  _ \\ __ _  ___| | _____| |_|  _ \\ _   _| |___  ___
 | |_) / _` |/ __| |/ / _ \\ __| |_) | | | | / __|/ _ \\
 |  __/ (_| | (__|   <  __/ |_|  __/| |_| | \\__ \\  __/
 |_|   \\__,_|\\___|_|\\_\\___|\\__|_|    \\__,_|_|___/\\___|

  DEMO MODE — No root required · Replaying mock capture
""")

    data    = load_mock_data()
    packets = data["packets"]
    stats   = dict(data["stats"])

    app      = create_app()
    socketio = SocketIO(app, cors_allowed_origins="*",
                        async_mode="threading", logger=False,
                        engineio_logger=False)

    @socketio.on("connect")
    def on_connect():
        print("[Demo] Client connected — starting replay")
        t = threading.Thread(
            target=replay_packets,
            args=(socketio, packets, stats),
            daemon=True
        )
        t.start()

    print("  Server : http://localhost:5001")
    print("  Open   : http://localhost:5001 in your browser")
    print("  Mode   : Demo (mock data replay)")
    print("  Press Ctrl+C to stop.\n")

    socketio.run(app, host="0.0.0.0", port=5001, debug=False)


if __name__ == "__main__":
    main()
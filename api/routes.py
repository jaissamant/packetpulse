"""
api/routes.py  —  Day 6 update
--------------------------------
REST API — now includes alert endpoints and file export.
"""

from flask import Blueprint, jsonify, request, send_file, Response
from api.geo import lookup, lookup_both, get_cache_size
from capture.exporter import export_csv, export_pcap, generate_filename
import io

api_bp = Blueprint("api", __name__, url_prefix="/api")

_capture      = None
_alert_engine = None


def set_capture(capture_instance):
    global _capture
    _capture = capture_instance


def set_alert_engine(alert_engine_instance):
    global _alert_engine
    _alert_engine = alert_engine_instance


# ── Status ──
@api_bp.route("/status")
def status():
    return jsonify({
        "running":     _capture.is_running() if _capture else False,
        "interface":   _capture.interface or "Wi-Fi" if _capture else None,
        "buffer_size": _capture.buffer_size if _capture else 0,
        "geo_cache":   get_cache_size(),
    })


# ── Stats ──
@api_bp.route("/stats")
def stats():
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    return jsonify(_capture.get_stats())


# ── Packets ──
@api_bp.route("/packets")
def packets():
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    return jsonify(_capture.get_buffer())


# ── Capture control ──
@api_bp.route("/capture/start", methods=["POST"])
def start_capture():
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    if _capture.is_running():
        return jsonify({"message": "Already running"})
    _capture.start()
    return jsonify({"message": "Capture started"})


@api_bp.route("/capture/stop", methods=["POST"])
def stop_capture():
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    _capture.stop()
    return jsonify({"message": "Capture stopped"})


# ── Geo IP ──
@api_bp.route("/geo/<ip>")
def geo_single(ip):
    return jsonify(lookup(ip))


@api_bp.route("/geo/both/<src>/<dst>")
def geo_both(src, dst):
    return jsonify(lookup_both(src, dst))


# ── Alerts (Day 6) ──
@api_bp.route("/alerts")
def get_alerts():
    if not _alert_engine:
        return jsonify([])
    limit = request.args.get("limit", 50, type=int)
    return jsonify(_alert_engine.get_alerts(limit=limit))


@api_bp.route("/alerts/counts")
def alert_counts():
    if not _alert_engine:
        return jsonify({"info": 0, "warning": 0, "critical": 0})
    return jsonify(_alert_engine.get_alert_counts())


@api_bp.route("/alerts/clear", methods=["POST"])
def clear_alerts():
    if _alert_engine:
        _alert_engine.clear_alerts()
    return jsonify({"message": "Alerts cleared"})


@api_bp.route("/alerts/thresholds", methods=["POST"])
def update_thresholds():
    if not _alert_engine:
        return jsonify({"error": "Alert engine not initialized"}), 500
    data = request.get_json()
    if data:
        _alert_engine.update_thresholds(data)
    return jsonify({"message": "Thresholds updated", "thresholds": _alert_engine.thresholds})


# ── Export (Day 6) ──
@api_bp.route("/export/csv")
def export_csv_route():
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    data     = export_csv(_capture.get_buffer())
    filename = generate_filename("csv")
    return Response(
        data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@api_bp.route("/export/pcap")
def export_pcap_route():
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    data     = export_pcap(_capture.get_buffer())
    filename = generate_filename("pcap")
    return Response(
        data,
        mimetype="application/vnd.tcpdump.pcap",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
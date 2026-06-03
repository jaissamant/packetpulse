"""
api/routes.py  (Day 5 update)
------------------------------
REST API endpoints — now includes geo IP lookup.
"""

from flask import Blueprint, jsonify, request
from api.geo import lookup, lookup_both, get_cache_size

api_bp = Blueprint("api", __name__, url_prefix="/api")

_capture = None


def set_capture(capture_instance):
    global _capture
    _capture = capture_instance


@api_bp.route("/status")
def status():
    return jsonify({
        "running":     _capture.is_running() if _capture else False,
        "interface":   _capture.interface or "Wi-Fi" if _capture else None,
        "buffer_size": _capture.buffer_size if _capture else 0,
        "geo_cache":   get_cache_size(),
    })


@api_bp.route("/stats")
def stats():
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    return jsonify(_capture.get_stats())


@api_bp.route("/packets")
def packets():
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    return jsonify(_capture.get_buffer())


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


# ── NEW: Geo IP endpoint ──
@api_bp.route("/geo/<ip>")
def geo_single(ip):
    """Lookup geo info for a single IP."""
    return jsonify(lookup(ip))


@api_bp.route("/geo/both/<src>/<dst>")
def geo_both(src, dst):
    """Lookup geo info for both src and dst IPs."""
    return jsonify(lookup_both(src, dst))
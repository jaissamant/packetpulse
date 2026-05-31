"""
api/routes.py
-------------
REST API endpoints for PacketPulse.
"""
 
from flask import Blueprint, jsonify
 
# Blueprint registered in server.py
api_bp = Blueprint("api", __name__, url_prefix="/api")
 
# The capture engine is injected at runtime by server.py
_capture = None
 
 
def set_capture(capture_instance):
    """Called by server.py to inject the capture engine."""
    global _capture
    _capture = capture_instance
 
 
# ------------------------------------------------------------------ #
#  Routes                                                              #
# ------------------------------------------------------------------ #
 
@api_bp.route("/status")
def status():
    """Returns whether capture is running."""
    return jsonify({
        "running": _capture.is_running() if _capture else False,
        "interface": _capture.interface or "Wi-Fi" if _capture else None,
        "buffer_size": _capture.buffer_size if _capture else 0,
    })
 
 
@api_bp.route("/stats")
def stats():
    """Returns live traffic statistics."""
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    return jsonify(_capture.get_stats())
 
 
@api_bp.route("/packets")
def packets():
    """Returns the last N packets from the buffer."""
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    return jsonify(_capture.get_buffer())
 
 
@api_bp.route("/capture/start", methods=["POST"])
def start_capture():
    """Start packet capture."""
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    if _capture.is_running():
        return jsonify({"message": "Already running"})
    _capture.start()
    return jsonify({"message": "Capture started"})
 
 
@api_bp.route("/capture/stop", methods=["POST"])
def stop_capture():
    """Stop packet capture."""
    if not _capture:
        return jsonify({"error": "Capture not initialized"}), 500
    _capture.stop()
    return jsonify({"message": "Capture stopped"})
 
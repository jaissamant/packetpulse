"""
api/socket_events.py
--------------------
WebSocket events for real-time packet streaming.
"""
 
import threading
import time
from flask_socketio import SocketIO, emit
 
# Injected at runtime
_capture = None
_socketio = None
_stats_thread = None
_stats_running = False
 
 
def init_socket(socketio_instance, capture_instance):
    """Called by server.py to wire up SocketIO and capture."""
    global _capture, _socketio
    _capture = capture_instance
    _socketio = socketio_instance
 
    # Register the packet callback
    _capture.on_packet(_broadcast_packet)
 
    # Register SocketIO event handlers
    @socketio_instance.on("connect")
    def handle_connect():
        """Send buffered packets to a newly connected client."""
        print("[SocketIO] Client connected")
 
        # Send last N packets from buffer so client has data immediately
        buffer = _capture.get_buffer()
        emit("packet_history", buffer)
 
        # Send current stats
        emit("stats_update", _capture.get_stats())
 
    @socketio_instance.on("disconnect")
    def handle_disconnect():
        print("[SocketIO] Client disconnected")
 
    @socketio_instance.on("request_stats")
    def handle_request_stats():
        """Client explicitly asking for latest stats."""
        emit("stats_update", _capture.get_stats())
 
 
def _broadcast_packet(packet: dict):
    """Callback fired by PacketCapture for every new packet."""
    if _socketio:
        _socketio.emit("new_packet", packet)
 
 
def start_stats_broadcast(interval: int = 2):
    """
    Background thread that pushes stats to ALL clients
    every `interval` seconds.
    """
    global _stats_thread, _stats_running
    _stats_running = True
 
    def _loop():
        while _stats_running:
            if _socketio and _capture:
                _socketio.emit("stats_update", _capture.get_stats())
            time.sleep(interval)
 
    _stats_thread = threading.Thread(target=_loop, daemon=True)
    _stats_thread.start()
 
 
def stop_stats_broadcast():
    global _stats_running
    _stats_running = False
 
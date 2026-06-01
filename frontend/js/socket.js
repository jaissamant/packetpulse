/**
 * frontend/js/socket.js
 * Manages the Socket.IO connection and fires custom events
 * that the rest of the app listens to.
 */

const socket = io();

// ── Connection events ──
socket.on('connect', () => {
  document.dispatchEvent(new CustomEvent('pp:connected'));
});

socket.on('disconnect', () => {
  document.dispatchEvent(new CustomEvent('pp:disconnected'));
});

// ── Data events ──
socket.on('packet_history', (packets) => {
  document.dispatchEvent(new CustomEvent('pp:history', { detail: packets }));
});

socket.on('new_packet', (packet) => {
  document.dispatchEvent(new CustomEvent('pp:packet', { detail: packet }));
});

socket.on('stats_update', (stats) => {
  document.dispatchEvent(new CustomEvent('pp:stats', { detail: stats }));
});

// ── Expose for other modules ──
window.ppSocket = socket;
/**
 * frontend/js/socket.js  —  Day 6 update
 * Adds new_alert event from server.
 */

const socket = io();

socket.on('connect', () => {
  document.dispatchEvent(new CustomEvent('pp:connected'));
});

socket.on('disconnect', () => {
  document.dispatchEvent(new CustomEvent('pp:disconnected'));
});

socket.on('packet_history', (packets) => {
  document.dispatchEvent(new CustomEvent('pp:history', { detail: packets }));
});

socket.on('new_packet', (packet) => {
  document.dispatchEvent(new CustomEvent('pp:packet', { detail: packet }));
});

socket.on('stats_update', (stats) => {
  document.dispatchEvent(new CustomEvent('pp:stats', { detail: stats }));
});

// Day 6: alert events
socket.on('new_alert', (alert) => {
  document.dispatchEvent(new CustomEvent('pp:alert', { detail: alert }));
});

window.ppSocket = socket;
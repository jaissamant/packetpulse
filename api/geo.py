"""
api/geo.py
----------
Geo IP lookup using ip-api.com (free, no key needed).
Results are cached in memory to avoid re-querying same IPs.
"""

import urllib.request
import urllib.error
import json
import threading

# In-memory cache: ip → geo dict
_cache = {}
_lock  = threading.Lock()

# IPs to skip (private/loopback ranges)
SKIP_PREFIXES = (
    "127.", "10.", "192.168.", "172.",
    "0.0.0.0", "::1", "fe80", "localhost"
)


def is_private(ip: str) -> bool:
    return any(ip.startswith(p) for p in SKIP_PREFIXES)


def lookup(ip: str) -> dict:
    """
    Return geo info for an IP address.
    Uses cache; returns empty dict for private IPs or on error.
    """
    if not ip or is_private(ip):
        return {"status": "private", "country": "Local", "city": "", "org": ""}

    with _lock:
        if ip in _cache:
            return _cache[ip]

    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,city,org,isp,lat,lon"
        req = urllib.request.Request(url, headers={"User-Agent": "PacketPulse/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())

        result = {
            "status":      data.get("status", "unknown"),
            "country":     data.get("country", "Unknown"),
            "countryCode": data.get("countryCode", ""),
            "city":        data.get("city", ""),
            "org":         data.get("org", ""),
            "isp":         data.get("isp", ""),
            "lat":         data.get("lat", 0),
            "lon":         data.get("lon", 0),
            "flag":        _flag_emoji(data.get("countryCode", "")),
        }

        with _lock:
            _cache[ip] = result

        return result

    except Exception as e:
        err = {"status": "error", "country": "Unknown", "city": "", "org": "", "flag": "🌐"}
        with _lock:
            _cache[ip] = err
        return err


def lookup_both(src_ip: str, dst_ip: str) -> dict:
    """Lookup geo for both IPs in a packet."""
    return {
        "src": lookup(src_ip),
        "dst": lookup(dst_ip),
    }


def get_cache_size() -> int:
    with _lock:
        return len(_cache)


def _flag_emoji(country_code: str) -> str:
    """Convert 2-letter country code to flag emoji."""
    if not country_code or len(country_code) != 2:
        return "🌐"
    try:
        return chr(0x1F1E6 + ord(country_code[0]) - ord('A')) + \
               chr(0x1F1E6 + ord(country_code[1]) - ord('A'))
    except Exception:
        return "🌐"
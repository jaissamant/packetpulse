# PacketPulse — Setup Guide

## Requirements

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | 3.14 works |
| Npcap | 1.88+ | Windows only |
| Admin/root | — | Required for live capture |

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/packetpulse.git
cd packetpulse

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

## Running

### Live Mode (captures real packets)

**Windows** — open terminal as Administrator:
```
python server.py
```

**Mac/Linux:**
```
sudo python server.py
```

Then open `http://localhost:5000` in your browser.

### Demo Mode (no root required)

```bash
python demo_server.py
```

Then open `http://localhost:5001` in your browser.

## Windows — Npcap Setup

PacketPulse requires Npcap on Windows for raw packet capture:

1. Download from [https://npcap.com/#download](https://npcap.com/#download)
2. Run the installer with default settings
3. Make sure **"Install Npcap in WinPcap API-compatible mode"** is checked
4. Restart your computer after installation

## Finding Your Network Interface

```python
from scapy.all import get_working_ifaces
for i in get_working_ifaces():
    print(i.name, '|', i.description)
```

Update `config.py` with your interface name:
```python
CAPTURE_INTERFACE = "Wi-Fi"   # or "eth0", "en0", etc.
```

## Configuration

Edit `config.py` to change settings:

```python
CAPTURE_INTERFACE = "Wi-Fi"   # network interface
BUFFER_SIZE       = 500        # packets to keep in memory
HOST              = "0.0.0.0"  # server host
PORT              = 5000        # server port
STATS_INTERVAL    = 2          # stats broadcast interval (seconds)
```
# PacketPulse Makefile
# Usage: make <target>

.PHONY: install run demo export clean help

help:
	@echo ""
	@echo "  PacketPulse — Available commands"
	@echo "  ─────────────────────────────────"
	@echo "  make install   Install all dependencies"
	@echo "  make run       Start live capture server (requires admin/root)"
	@echo "  make demo      Start demo mode (no root required)"
	@echo "  make clean     Remove Python cache files"
	@echo ""

install:
	pip install -r requirements.txt

run:
	python server.py

demo:
	python demo_server.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.log" -delete 2>/dev/null || true
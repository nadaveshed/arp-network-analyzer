# Docker & Linux Setup Guide

Complete guide for running the ARP Network Analyzer in Docker or on Linux systems where packet capture works out of the box.

## 🐳 Docker Setup (Recommended)

Docker provides the easiest cross-platform setup with packet capture working immediately.

### Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

### Quick Start

```bash
# Navigate to project directory
cd C:\Users\nadav\.gemini\antigravity\scratch\arp-network-analyzer

# Build and start the container
docker-compose up --build

# The web UI will be available at: http://localhost:5000
```

### Docker Commands

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Access container shell
docker exec -it arp-network-analyzer bash
```

### How It Works

The Docker setup:
- ✅ Uses `network_mode: host` to access host network interfaces
- ✅ Adds `NET_ADMIN` and `NET_RAW` capabilities for packet capture
- ✅ Installs `libpcap-dev` for Scapy packet capture
- ✅ Mounts `snapshots/` and `static/` directories for persistence
- ✅ Automatically starts the web UI on port 5000

### Verify It's Working

```bash
# Check if container is capturing packets
docker-compose logs | grep "packets captured"

# You should see output like:
# INFO - Status: 5 nodes, 8 edges, 42 packets captured
```

### Generate Test Traffic

While the Docker container is running, generate ARP traffic:

```bash
# On Windows (PowerShell)
ping 192.168.1.1
ping 8.8.8.8
arp -a

# On Linux/Mac
ping -c 4 192.168.1.1
ping -c 4 8.8.8.8
arp -a
```

Then refresh `http://localhost:5000` to see the graph update.

---

## 🐧 Native Linux Setup

For running directly on Linux without Docker.

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip libpcap-dev tcpdump

# Fedora/RHEL
sudo dnf install -y python3 python3-pip libpcap-devel tcpdump

# Arch Linux
sudo pacman -S python python-pip libpcap tcpdump
```

### Installation

```bash
# Clone or copy the project
cd /path/to/arp-network-analyzer

# Install Python dependencies
pip3 install -r requirements.txt

# Or use a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running

```bash
# Run with sudo for packet capture privileges
sudo python3 main.py --api

# Or grant capabilities to Python (one-time setup)
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)
python3 main.py --api

# Specify network interface
sudo python3 main.py --api -i eth0
```

### List Network Interfaces

```bash
# Find your network interface name
ip link show

# Common names: eth0, wlan0, enp0s3, wlp2s0
```

### Systemd Service (Optional)

Create a systemd service to run on boot:

```bash
# Create service file
sudo nano /etc/systemd/system/arp-analyzer.service
```

```ini
[Unit]
Description=ARP Network Analyzer
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/arp-network-analyzer
ExecStart=/usr/bin/python3 /path/to/arp-network-analyzer/main.py --api
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable arp-analyzer
sudo systemctl start arp-analyzer

# Check status
sudo systemctl status arp-analyzer

# View logs
sudo journalctl -u arp-analyzer -f
```

---

## 🪟 Windows with WSL2

Run Linux Docker containers on Windows with full packet capture support.

### Prerequisites

1. **Install WSL2**: [WSL2 Installation Guide](https://docs.microsoft.com/en-us/windows/wsl/install)
   ```powershell
   wsl --install
   ```

2. **Install Docker Desktop**: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
   - Enable WSL2 backend in Docker Desktop settings

### Setup

```bash
# Open WSL2 terminal (Ubuntu)
wsl

# Navigate to project (Windows drives are mounted at /mnt/)
cd /mnt/c/Users/nadav/.gemini/antigravity/scratch/arp-network-analyzer

# Run with Docker Compose
docker-compose up --build
```

### Access from Windows

- Web UI: `http://localhost:5000`
- Works from both WSL2 and Windows browsers

---

## 🍎 macOS Setup

### Using Docker (Recommended)

```bash
# Install Docker Desktop for Mac
# Then run:
cd /path/to/arp-network-analyzer
docker-compose up --build
```

### Native Setup

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python libpcap

# Install Python packages
pip3 install -r requirements.txt

# Run with sudo
sudo python3 main.py --api
```

---

## 🔍 Troubleshooting

### Docker: "Permission denied" errors

```bash
# Add your user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker-compose up
```

### Docker: "No packets captured"

```bash
# Verify network mode
docker inspect arp-network-analyzer | grep NetworkMode
# Should show: "NetworkMode": "host"

# Check capabilities
docker inspect arp-network-analyzer | grep -A 5 CapAdd
# Should show: NET_ADMIN, NET_RAW
```

### Linux: "Operation not permitted"

```bash
# Run with sudo
sudo python3 main.py --api

# Or grant capabilities
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)
```

### No ARP traffic visible

```bash
# Generate test traffic
ping -c 10 192.168.1.1
ping -c 10 8.8.8.8

# Check if interface is correct
ip link show  # Linux
ifconfig      # macOS

# Specify interface explicitly
sudo python3 main.py --api -i eth0
```

---

## 📊 Verify Setup

### 1. Check Container Status

```bash
docker-compose ps

# Should show:
# NAME                    STATUS
# arp-network-analyzer    Up
```

### 2. Check Logs

```bash
docker-compose logs -f

# Should see:
# INFO - Started packet capture on interface: default
# INFO - Web UI available at http://localhost:5000
```

### 3. Test Web UI

Open browser to `http://localhost:5000`

You should see:
- Interactive graph visualization
- Statistics panel (nodes, edges, observations)
- Legend showing activity levels

### 4. Test API

```bash
# Get graph stats
curl http://localhost:5000/api/stats

# Get all nodes
curl http://localhost:5000/api/nodes

# Export graph
curl http://localhost:5000/api/export/json -o graph.json
```

---

## 🎯 Production Deployment

### Docker with Custom Network

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  arp-analyzer:
    build: .
    container_name: arp-analyzer-prod
    network_mode: host
    cap_add:
      - NET_ADMIN
      - NET_RAW
    volumes:
      - ./snapshots:/app/snapshots:rw
      - ./static:/app/static:rw
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=WARNING
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Behind Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/arp-analyzer
server {
    listen 80;
    server_name arp-analyzer.local;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 📝 Summary

| Platform | Method | Packet Capture | Difficulty |
|----------|--------|----------------|------------|
| **Any** | Docker | ✅ Works | ⭐ Easy |
| **Linux** | Native | ✅ Works | ⭐⭐ Medium |
| **Windows** | WSL2 + Docker | ✅ Works | ⭐⭐ Medium |
| **macOS** | Docker | ✅ Works | ⭐ Easy |
| **Windows** | Native | ⚠️ Needs Npcap | ⭐⭐⭐ Hard |

**Recommendation**: Use Docker for the best cross-platform experience with packet capture working out of the box.

---

## 🚀 Quick Reference

```bash
# Docker: Start
docker-compose up -d

# Docker: View logs
docker-compose logs -f

# Docker: Stop
docker-compose down

# Linux: Start
sudo python3 main.py --api

# Generate test traffic
ping -c 10 192.168.1.1

# Access UI
http://localhost:5000

# Export data
curl http://localhost:5000/api/export/json -o graph.json
```

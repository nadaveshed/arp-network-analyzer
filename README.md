# ARP Network Analyzer

A passive network monitoring tool that captures ARP traffic, builds a dynamic connections graph, and provides interactive visualization of network device relationships.

## 🎯 Overview

This tool demonstrates:
- **Passive network analysis** - observes ARP traffic without disrupting network behavior
- **Real-time graph building** - maintains a live connections graph with confidence scoring
- **Advanced analytics** - centrality metrics, community detection, anomaly detection
- **Interactive visualization** - D3.js-powered web interface
- **Multiple export formats** - JSON, GraphML, CSV

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Controller Layer                         │
│  ┌──────────────────┐         ┌─────────────────────┐       │
│  │  CLI Controller  │         │  API Controller     │       │
│  └──────────────────┘         └─────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Business Layer                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Packet    │→ │    Graph     │→ │   Analyzer   │       │
│  │   Capture   │  │   Builder    │  │              │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  NetworkGraph (NetworkX-based)                   │       │
│  │    ├─ NetworkNode (IP/MAC, metadata)             │       │
│  │    └─ Connection (confidence, observations)      │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Output Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Visualizer  │  │   Exporter   │  │  Web UI      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Design Decisions

**Graph Structure**
- Directed graph where edges represent ARP relationships
- Nodes: Network devices (identified by IP/MAC)
- Edges: ARP requests/replies with confidence scores

**Confidence Scoring**
- Time decay: Recent observations weighted higher (exponential decay)
- Frequency: More observations increase confidence (logarithmic scaling)
- Combined score: 70% recency + 30% frequency

**Data Model**
- `NetworkNode`: Represents devices with activity tracking
- `Connection`: Represents relationships with observation history
- `NetworkGraph`: Thread-safe wrapper around NetworkX

## 📋 Requirements

- Python 3.8+
- Administrator/root privileges (for packet capture)
- Network interface with ARP traffic

**Windows Users**: Packet capture requires [Npcap](https://npcap.com/#download). **We recommend using Docker instead** (see below).

## 🐳 Docker Setup (Recommended)

The easiest way to run the analyzer with packet capture working out of the box:

```bash
# Quick start (Windows PowerShell)
.\docker-start.ps1

# Quick start (Linux/Mac)
chmod +x docker-start.sh
./docker-start.sh

# Or manually
docker-compose up --build
```

Then open: **http://localhost:5000**

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for complete Docker and Linux setup guide.

## 🚀 Installation (Native)

```bash
cd C:\Users\nadav\.gemini\antigravity\scratch\arp-network-analyzer
pip install -r requirements.txt
```

## 💻 Usage

### CLI Mode (Console Only)

```bash
# Run with default interface
python main.py

# Specify network interface
python main.py -i "Wi-Fi"

# Set log level
python main.py --log-level DEBUG
```

### Web UI Mode (Recommended)

```bash
# Start with web interface
python main.py --api

# Then open browser to: http://localhost:5000
```

### Command-Line Options

```
-i, --interface    Network interface to capture on (default: auto-detect)
--api              Start web API server and UI
--log-level        Logging level: DEBUG, INFO, WARNING, ERROR
```

## 🌐 API Endpoints

When running with `--api` flag:

- `GET /` - Interactive web visualization
- `GET /api/graph` - Complete graph data (JSON)
- `GET /api/nodes` - All nodes
- `GET /api/edges` - All edges
- `GET /api/stats` - Graph statistics
- `GET /api/analysis` - Latest analysis results
- `GET /api/export/json` - Download graph as JSON
- `GET /api/export/graphml` - Download graph as GraphML
- `GET /api/d3` - D3.js compatible data

## 📊 Features

### Real-Time Monitoring
- Captures ARP requests and replies
- Builds graph as packets arrive
- Thread-safe concurrent updates

### Graph Enrichment
- **Centrality metrics** - identifies important nodes
- **Community detection** - finds network clusters
- **Confidence scoring** - time-decayed relationship strength
- **Activity classification** - high/medium/low activity nodes

### Anomaly Detection
- High activity nodes (potential issues)
- Potential scanners (many outgoing requests)
- Unusual patterns

### Visualization
- Interactive force-directed graph
- Color-coded by activity level
- Node size based on packet count
- Edge width based on confidence
- Hover tooltips with details
- Drag-and-drop nodes

### Export Options
- **JSON** - Complete graph data
- **GraphML** - Import into Gephi, Cytoscape
- **CSV** - Nodes and edges separately

## 🔍 How It Works

### 1. Packet Capture
- Uses Scapy to sniff ARP packets
- Filters for ARP traffic only (BPF filter)
- Runs in separate thread to avoid blocking

### 2. Packet Processing
- Extracts IP/MAC addresses
- Validates packet sanity
- Classifies as request or reply
- Normalizes MAC addresses

### 3. Graph Building
- Creates/updates nodes for devices
- Creates/updates edges for relationships
- Tracks observation timestamps
- Maintains packet counts

### 4. Analysis & Enrichment
- Calculates centrality metrics every 30s
- Updates confidence scores with time decay
- Detects anomalies and unusual patterns
- Identifies network communities

### 5. Visualization
- Generates D3.js force-directed graph
- Real-time updates via API
- Interactive exploration

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Capture settings
DEFAULT_INTERFACE = None  # Auto-detect
CAPTURE_FILTER = "arp"

# Graph settings
CONFIDENCE_DECAY_RATE = 0.95  # Per hour
MIN_CONFIDENCE_THRESHOLD = 0.1
MAX_GRAPH_AGE_HOURS = 24

# Analysis settings
ENABLE_ENRICHMENT = True
ENRICHMENT_INTERVAL = 30  # Seconds
ANOMALY_DETECTION = True

# API settings
API_PORT = 5000
```

## 🛡️ Limitations & Assumptions

### Limitations
1. **Passive only** - Cannot actively probe for information
2. **ARP-specific** - Only observes ARP traffic, not other protocols
3. **Local network** - Limited to broadcast domain
4. **In-memory** - Graph stored in RAM (mitigated by snapshots)
5. **No persistence** - Restarts lose history (use exports)

### Assumptions
1. Running in isolated test environment
2. Administrator/root privileges available
3. Network has ARP traffic to observe
4. Single network interface monitoring
5. Reasonable network size (< 10,000 nodes)

## 📁 Project Structure

```
arp-network-analyzer/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── models/
│   ├── node.py               # NetworkNode model
│   ├── edge.py               # Connection model
│   └── graph.py              # NetworkGraph model
├── services/
│   ├── packet_capture.py     # Packet sniffing
│   ├── graph_builder.py      # Graph construction
│   ├── analyzer.py           # Analytics & enrichment
│   ├── visualizer.py         # Visualization generation
│   └── exporter.py           # Data export
├── controllers/
│   ├── cli_controller.py     # CLI interface
│   └── api_controller.py     # REST API
├── utils/
│   ├── arp_parser.py         # ARP packet parsing
│   └── transformers.py       # Data transformations
├── static/                    # Generated visualizations
└── snapshots/                 # Exported graph data
```

## 🎨 Code Quality

- **Separation of concerns** - Clear layer boundaries
- **Short functions** - Single responsibility principle
- **Type hints** - Better IDE support and clarity
- **Logging** - Comprehensive debug information
- **Thread safety** - Concurrent access protection
- **Error handling** - Graceful degradation

## 📝 Example Output

```
=== ARP Network Analyzer Starting ===
INFO - Started packet capture on interface: Wi-Fi
INFO - Web UI available at http://localhost:5000
INFO - Status: 5 nodes, 8 edges, 42 packets captured, 38 processed
INFO - Starting network analysis...
INFO - Status: 12 nodes, 23 edges, 156 packets captured, 142 processed
```

## 🤝 Contributing

This is a demonstration project. Key areas for enhancement:
- Persistent storage (database)
- Historical analysis
- Additional protocol support
- Machine learning for anomaly detection
- Performance optimization for large networks

## 📄 License

This project is for educational and demonstration purposes.

---

**⚠️ Important**: This tool requires administrator/root privileges and should only be used in authorized test environments. Passive monitoring is non-intrusive but still requires proper authorization.

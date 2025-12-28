"""
Configuration settings for the ARP Network Analyzer
"""
import os

# Network Capture Settings
DEFAULT_INTERFACE = None  # None = auto-detect, or specify like "eth0" or "Wi-Fi"
CAPTURE_FILTER = "arp"  # BPF filter for ARP packets only
PACKET_COUNT = 0  # 0 = infinite capture
CAPTURE_TIMEOUT = 1  # Timeout in seconds for packet processing

# Graph Settings
CONFIDENCE_DECAY_RATE = 0.95  # Exponential decay factor per hour
MIN_CONFIDENCE_THRESHOLD = 0.1  # Minimum confidence to keep an edge
MAX_GRAPH_AGE_HOURS = 24  # Remove nodes not seen in this timeframe

# Analysis Settings
ENABLE_ENRICHMENT = True  # Calculate centrality and other metrics
ENRICHMENT_INTERVAL = 30  # Seconds between enrichment runs
ANOMALY_DETECTION = True  # Detect unusual patterns

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 5000
API_DEBUG = False

# Export Settings
SNAPSHOT_DIR = "snapshots"
AUTO_SNAPSHOT_INTERVAL = 300  # Seconds (5 minutes)
EXPORT_FORMAT = "json"  # Default export format

# Visualization Settings
VIZ_NODE_SIZE_MIN = 10
VIZ_NODE_SIZE_MAX = 50
VIZ_EDGE_WIDTH_MIN = 1
VIZ_EDGE_WIDTH_MAX = 5

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Ensure snapshot directory exists
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

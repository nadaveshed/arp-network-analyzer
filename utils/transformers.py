"""
Data Transformation Utilities
"""
import math
from datetime import datetime
from typing import Dict


def normalize_mac(mac: str) -> str:
    """
    Normalize MAC address to consistent format
    
    Args:
        mac: MAC address in various formats
    
    Returns:
        Normalized MAC in lowercase with colons
    """
    # Remove common separators
    
    mac = mac.replace("-", ":").replace(".", ":")
    # Ensure lowercase
    return mac.lower()


def calculate_confidence(
    observation_count: int,
    last_seen: datetime,
    decay_rate: float = 0.95
) -> float:
    """
    Calculate confidence score based on frequency and recency
    
    Args:
        observation_count: Number of times observed
        last_seen: Timestamp of last observation
        decay_rate: Exponential decay factor per hour
    
    Returns:
        Confidence score between 0 and 1
    """
    now = datetime.now()
    hours_since_last = (now - last_seen).total_seconds() / 3600
    
    # Time decay component (exponential)
    time_factor = decay_rate ** hours_since_last
    
    # Frequency component (logarithmic scaling)
    frequency_factor = min(1.0, math.log10(observation_count + 1) / 2)
    
    # Weighted combination: recency matters more
    confidence = (time_factor * 0.7) + (frequency_factor * 0.3)
    
    return max(0.0, min(1.0, confidence))


def enrich_node_metadata(node_data: Dict, graph_context: Dict) -> Dict:
    """
    Add derived attributes to node metadata
    
    Args:
        node_data: Node information dictionary
        graph_context: Context from graph analysis (centrality, etc.)
    
    Returns:
        Enriched metadata dictionary
    """
    metadata = {}
    
    # Add centrality metrics if available
    if "centrality" in graph_context:
        metadata["centrality"] = graph_context["centrality"]
    
    # Add activity level
    if "packet_count" in node_data:
        if node_data["packet_count"] > 100:
            metadata["activity_level"] = "high"
        elif node_data["packet_count"] > 20:
            metadata["activity_level"] = "medium"
        else:
            metadata["activity_level"] = "low"
    
    # Add age category
    if "first_seen" in node_data:
        first_seen = datetime.fromisoformat(node_data["first_seen"])
        hours_active = (datetime.now() - first_seen).total_seconds() / 3600
        
        if hours_active < 1:
            metadata["age_category"] = "new"
        elif hours_active < 24:
            metadata["age_category"] = "recent"
        else:
            metadata["age_category"] = "established"
    
    return metadata


def calculate_node_size(packet_count: int, min_size: int = 10, max_size: int = 50) -> int:
    """
    Calculate visual node size based on activity
    
    Args:
        packet_count: Number of packets observed
        min_size: Minimum node size
        max_size: Maximum node size
    
    Returns:
        Node size for visualization
    """
    # Logarithmic scaling
    if packet_count <= 1:
        return min_size
    
    scale = math.log10(packet_count + 1) / 3  # Normalize to ~0-1 range
    size = min_size + (max_size - min_size) * min(scale, 1.0)
    
    return int(size)


def calculate_edge_width(confidence: float, min_width: int = 1, max_width: int = 5) -> int:
    """
    Calculate visual edge width based on confidence
    
    Args:
        confidence: Confidence score (0-1)
        min_width: Minimum edge width
        max_width: Maximum edge width
    
    Returns:
        Edge width for visualization
    """
    width = min_width + (max_width - min_width) * confidence
    return int(width)

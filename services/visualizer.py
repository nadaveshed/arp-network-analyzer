import logging
from typing import Dict

from models.graph import NetworkGraph
from utils.transformers import calculate_node_size, calculate_edge_width
import config

logger = logging.getLogger(__name__)


class GraphVisualizer:
    def __init__(self, graph: NetworkGraph):
        self.graph = graph
    
    def generate_d3_data(self) -> Dict:
        nodes = []
        links = []
        
        # Build nodes array
        for node in self.graph.get_all_nodes():
            nodes.append({
                "id": node.get_id(),
                "label": node.ip or node.mac,
                "ip": node.ip,
                "mac": node.mac,
                "size": calculate_node_size(
                    node.packet_count,
                    config.VIZ_NODE_SIZE_MIN,
                    config.VIZ_NODE_SIZE_MAX
                ),
                "packet_count": node.packet_count,
                "centrality": node.metadata.get("centrality", 0),
                "group": node.metadata.get("activity_level", "low")
            })
        
        # Build links array
        for edge in self.graph.get_all_edges():
            links.append({
                "source": edge.source_id,
                "target": edge.target_id,
                "type": edge.relationship_type,
                "confidence": round(edge.confidence, 3),
                "width": calculate_edge_width(
                    edge.confidence,
                    config.VIZ_EDGE_WIDTH_MIN,
                    config.VIZ_EDGE_WIDTH_MAX
                ),
                "observations": edge.observation_count
            })
        
        return {
            "nodes": nodes,
            "links": links
        }

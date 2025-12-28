import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from models.graph import NetworkGraph
import config

logger = logging.getLogger(__name__)


class GraphExporter:
    
    def __init__(self, graph: NetworkGraph):
        self.graph = graph
        self.snapshot_dir = Path(config.SNAPSHOT_DIR)
        self.snapshot_dir.mkdir(exist_ok=True)
    
    def export_json(self, filepath: Optional[str] = None) -> str:
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.snapshot_dir / f"graph_{timestamp}.json"
        
        data = self.graph.to_dict()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported graph to JSON: {filepath}")
        return str(filepath)
    
    def export_graphml(self, filepath: Optional[str] = None) -> str:
        import networkx as nx
        
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.snapshot_dir / f"graph_{timestamp}.graphml"
        
        with self.graph.lock:
            # Create a clean graph for export
            export_graph = nx.DiGraph()
            
            # Add nodes with attributes
            for node in self.graph.get_all_nodes():
                export_graph.add_node(
                    node.get_id(),
                    ip=node.ip or "",
                    mac=node.mac or "",
                    packet_count=node.packet_count,
                    first_seen=node.first_seen.isoformat(),
                    last_seen=node.last_seen.isoformat()
                )
            
            # Add edges with attributes
            for edge in self.graph.get_all_edges():
                export_graph.add_edge(
                    edge.source_id,
                    edge.target_id,
                    type=edge.relationship_type,
                    confidence=edge.confidence,
                    observation_count=edge.observation_count
                )
            
            nx.write_graphml(export_graph, filepath)
        
        logger.info(f"Exported graph to GraphML: {filepath}")
        return str(filepath)
    
    def export_csv_nodes(self, filepath: Optional[str] = None) -> str:
        import csv
        
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.snapshot_dir / f"nodes_{timestamp}.csv"
        
        nodes = self.graph.get_all_nodes()
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'IP', 'MAC', 'Packet Count', 'First Seen', 'Last Seen'])
            
            for node in nodes:
                writer.writerow([
                    node.get_id(),
                    node.ip or '',
                    node.mac or '',
                    node.packet_count,
                    node.first_seen.isoformat(),
                    node.last_seen.isoformat()
                ])
        
        logger.info(f"Exported nodes to CSV: {filepath}")
        return str(filepath)
    
    def export_csv_edges(self, filepath: Optional[str] = None) -> str:
        import csv
        
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.snapshot_dir / f"edges_{timestamp}.csv"
        
        edges = self.graph.get_all_edges()
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Source', 'Target', 'Type', 'Confidence', 'Observations'])
            
            for edge in edges:
                writer.writerow([
                    edge.source_id,
                    edge.target_id,
                    edge.relationship_type,
                    round(edge.confidence, 3),
                    edge.observation_count
                ])
        
        logger.info(f"Exported edges to CSV: {filepath}")
        return str(filepath)

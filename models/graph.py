import threading
from typing import Dict, List, Optional, Set
import networkx as nx
from datetime import datetime

from models.node import NetworkNode
from models.edge import Connection


class NetworkGraph:
    """Thread-safe wrapper around NetworkX directed graph for network analysis"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, NetworkNode] = {}
        self.edges: Dict[tuple, Connection] = {}
        self.lock = threading.RLock()
        self.created_at = datetime.now()
    
    def add_or_update_node(self, node: NetworkNode) -> bool:
        with self.lock:
            node_id = node.get_id()
            is_new = node_id not in self.nodes
            
            if is_new:
                self.nodes[node_id] = node
                self.graph.add_node(node_id, node_obj=node)
            else:
                # Update existing node
                self.nodes[node_id].update_activity()
                # Merge metadata
                for key, value in node.metadata.items():
                    self.nodes[node_id].add_metadata(key, value)
            
            return is_new
    
    def add_or_update_edge(self, connection: Connection) -> bool:
        with self.lock:
            edge_key = (connection.source_id, connection.target_id, connection.relationship_type)
            is_new = edge_key not in self.edges
            
            if is_new:
                self.edges[edge_key] = connection
                self.graph.add_edge(
                    connection.source_id,
                    connection.target_id,
                    key=connection.relationship_type,
                    connection_obj=connection
                )
            else:
                # Update existing connection
                self.edges[edge_key].update_observation()
            
            return is_new
    
    def get_node(self, node_id: str) -> Optional[NetworkNode]:
        """Retrieve a node by ID"""
        with self.lock:
            return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> List[NetworkNode]:
        """Get all nodes in the graph"""
        with self.lock:
            return list(self.nodes.values())
    
    def get_all_edges(self) -> List[Connection]:
        """Get all edges in the graph"""
        with self.lock:
            return list(self.edges.values())
    
    def get_neighbors(self, node_id: str) -> Set[str]:
        """Get all neighbors (both incoming and outgoing) of a node"""
        with self.lock:
            if node_id not in self.graph:
                return set()
            predecessors = set(self.graph.predecessors(node_id))
            successors = set(self.graph.successors(node_id))
            return predecessors | successors
    
    def remove_old_nodes(self, max_age_hours: float):
        """Remove nodes that haven't been seen recently"""
        with self.lock:
            now = datetime.now()
            to_remove = []
            
            for node_id, node in self.nodes.items():
                hours_since_seen = (now - node.last_seen).total_seconds() / 3600
                if hours_since_seen > max_age_hours:
                    to_remove.append(node_id)
            
            for node_id in to_remove:
                self.graph.remove_node(node_id)
                del self.nodes[node_id]
                # Remove associated edges
                edges_to_remove = [
                    key for key in self.edges.keys()
                    if key[0] == node_id or key[1] == node_id
                ]
                for edge_key in edges_to_remove:
                    del self.edges[edge_key]
    
    def get_stats(self) -> dict:
        """Get graph statistics"""
        with self.lock:
            return {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "created_at": self.created_at.isoformat(),
                "total_observations": sum(e.observation_count for e in self.edges.values())
            }
    
    def to_dict(self) -> dict:
        """Export entire graph to dictionary"""
        with self.lock:
            return {
                "nodes": [node.to_dict() for node in self.nodes.values()],
                "edges": [edge.to_dict() for edge in self.edges.values()],
                "stats": self.get_stats()
            }

import logging
import networkx as nx
from typing import Dict, List
from datetime import datetime

from models.graph import NetworkGraph
import config

logger = logging.getLogger(__name__)


class NetworkAnalyzer:
   
    def __init__(self, graph: NetworkGraph):
        self.graph = graph
        self.last_analysis = None
        self.anomalies: List[Dict] = []
    
    def analyze(self) -> Dict:
        logger.info("Starting network analysis...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "centrality": self._calculate_centrality(),
            "communities": self._detect_communities(),
            "anomalies": self._detect_anomalies() if config.ANOMALY_DETECTION else []
        }
        
        self.last_analysis = results
        return results
    
    def _calculate_centrality(self) -> Dict[str, float]:
        with self.graph.lock:
            if len(self.graph.graph.nodes) == 0:
                return {}
            
            try:
                # Degree centrality: how many connections a node has
                # מספר הקשרים שיש לצומת ביחס לכלל הרשת
                centrality = nx.degree_centrality(self.graph.graph)
                
                # Update node metadata with centrality
                # עדכון metadata של כל צומת
                for node_id, score in centrality.items():
                    node = self.graph.get_node(node_id)
                    if node:
                        node.add_metadata("centrality", round(score, 3))
                
                return {k: round(v, 3) for k, v in centrality.items()}
            except Exception as e:
                logger.error(f"Error calculating centrality: {e}")
                return {}
    
    def _detect_communities(self) -> List[List[str]]:
        with self.graph.lock:
            if len(self.graph.graph.nodes) < 3:
                return []
            
            try:
                # Convert to undirected for community detection
                # המרה לגרף בלתי-מכוון לזיהוי קהילות
                undirected = self.graph.graph.to_undirected()
                
                # Use greedy modularity communities
                communities = nx.community.greedy_modularity_communities(undirected)
                
                return [list(community) for community in communities]
            except Exception as e:
                logger.error(f"Error detecting communities: {e}")
                return []
    
    def _detect_anomalies(self) -> List[Dict]:
        anomalies = []
        
        with self.graph.lock:
            # Check for nodes with unusually high activity
            nodes = self.graph.get_all_nodes()
            if not nodes:
                return anomalies
            
            avg_packet_count = sum(n.packet_count for n in nodes) / len(nodes)
            
            for node in nodes:
                # High activity anomaly - פעילות גבוהה חריגה
                if node.packet_count > avg_packet_count * 5:
                    anomalies.append({
                        "type": "high_activity",
                        "node_id": node.get_id(),
                        "packet_count": node.packet_count,
                        "average": round(avg_packet_count, 2),
                        "severity": "medium"
                    })
                
                # Check for nodes with only outgoing requests (potential scanner)
                # בדיקה לסורק פוטנציאלי - רק בקשות יוצאות
                neighbors = self.graph.get_neighbors(node.get_id())
                if len(neighbors) > 10:
                    outgoing = len(list(self.graph.graph.successors(node.get_id())))
                    if outgoing > len(neighbors) * 0.9:
                        anomalies.append({
                            "type": "potential_scanner",
                            "node_id": node.get_id(),
                            "outgoing_ratio": round(outgoing / len(neighbors), 2),
                            "severity": "high"
                        })
        
        self.anomalies = anomalies
        return anomalies
    
    def update_confidence_scores(self):
        edges = self.graph.get_all_edges()
        
        for edge in edges:
            edge.calculate_confidence(config.CONFIDENCE_DECAY_RATE)
        
        logger.debug(f"Updated confidence scores for {len(edges)} edges")
    
    def get_top_nodes(self, n: int = 10) -> List[Dict]:
        nodes = self.graph.get_all_nodes()
        sorted_nodes = sorted(nodes, key=lambda x: x.packet_count, reverse=True)
        
        return [
            {
                "id": node.get_id(),
                "ip": node.ip,
                "mac": node.mac,
                "packet_count": node.packet_count,
                "centrality": node.metadata.get("centrality", 0)
            }
            for node in sorted_nodes[:n]
        ]

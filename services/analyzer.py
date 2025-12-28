"""
Network Analyzer Service - Enriches graph with analytics and anomaly detection
שירות ניתוח רשת - מעשיר את הגרף בניתוחים וזיהוי אנומליות
"""
import logging
import networkx as nx
from typing import Dict, List
from datetime import datetime

from models.graph import NetworkGraph
import config

logger = logging.getLogger(__name__)


class NetworkAnalyzer:
    """
    Service for analyzing and enriching the network graph
    שירות לניתוח והעשרה של גרף הרשת - מוסיף מטריקות, מזהה קהילות ואנומליות
    """
    
    def __init__(self, graph: NetworkGraph):
        """
        אתחול שירות ניתוח הרשת
        
        מטרה: הכנת השירות לביצוע ניתוחים על הגרף
        
        קלט (Input):
            graph: אובייקט NetworkGraph לניתוח
        
        פלט (Output): אין
        
        משתנים פנימיים:
            - last_analysis: תוצאות הניתוח האחרון
            - anomalies: רשימת אנומליות שזוהו
        """
        self.graph = graph
        self.last_analysis = None
        self.anomalies: List[Dict] = []
    
    def analyze(self) -> Dict:
        """
        ביצוע ניתוח מקיף של הגרף
        
        מטרה: לחשב מטריקות, לזהות קהילות ואנומליות
        
        Perform comprehensive graph analysis
        
        קלט (Input): אין
        
        פלט (Output):
            dict: מילון עם תוצאות הניתוח:
                - timestamp: זמן הניתוח
                - centrality: מטריקות centrality לכל צומת
                - communities: קבוצות של צמתים קשורים
                - anomalies: אנומליות שזוהו
        
        דוגמת פלט:
            {
                "timestamp": "2025-12-24T11:48:00",
                "centrality": {"aa:bb:cc:dd:ee:ff": 0.75, ...},
                "communities": [["node1", "node2"], ["node3", "node4"]],
                "anomalies": [{"type": "high_activity", ...}]
            }
        
        הערות:
            - רץ כל 30 שניות בתהליך נפרד
            - שומר תוצאות ב-last_analysis
        """
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
        """
        חישוב מטריקות centrality לצמתים
        
        מטרה: לזהות צמתים חשובים/מרכזיים ברשת (hub devices)
        
        Calculate node centrality metrics
        
        קלט (Input): אין
        
        פלט (Output):
            dict: מיפוי של node ID לציון centrality (0.0-1.0)
                 ציון גבוה = צומת מרכזי עם הרבה קשרים
        
        אלגוריתם:
            - משתמש ב-degree centrality של NetworkX
            - מעדכן את metadata של כל צומת עם הציון
        
        הערות:
            - מחזיר {} אם אין צמתים בגרף
            - תופס שגיאות ומחזיר {} במקרה של בעיה
        """
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
        """
        זיהוי קהילות/צבירים ברשת
        
        מטרה: למצוא קבוצות של מכשירים שמתקשרים הרבה ביניהם
        
        Detect communities/clusters in the network
        
        קלט (Input): אין
        
        פלט (Output):
            list: רשימה של קהילות, כל קהילה היא רשימת node IDs
                 דוגמה: [["node1", "node2"], ["node3", "node4", "node5"]]
        
        אלגוריתם:
            - ממיר את הגרף המכוון לבלתי-מכוון
            - משתמש ב-greedy modularity communities של NetworkX
        
        הערות:
            - דורש לפחות 3 צמתים
            - מחזיר [] אם פחות מ-3 צמתים או שגיאה
        """
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
        """
        זיהוי דפוסים חריגים ברשת
        
        מטרה: למצוא התנהגויות חשודות כמו סורקים או פעילות יתר
        
        Detect unusual patterns in the network
        
        קלט (Input): אין
        
        פלט (Output):
            list: רשימת אנומליות, כל אחת מילון עם:
                - type: סוג האנומליה
                - node_id: מזהה הצומת החשוד
                - severity: רמת חומרה (low/medium/high)
                - נתונים נוספים ספציפיים לסוג
        
        סוגי אנומליות:
            1. high_activity: צומת עם פעילות גבוהה פי 5 מהממוצע
            2. potential_scanner: צומת עם 90%+ בקשות יוצאות (>10 שכנים)
        
        דוגמת פלט:
            [
                {
                    "type": "high_activity",
                    "node_id": "aa:bb:cc:dd:ee:ff",
                    "packet_count": 500,
                    "average": 100,
                    "severity": "medium"
                },
                {
                    "type": "potential_scanner",
                    "node_id": "11:22:33:44:55:66",
                    "outgoing_ratio": 0.95,
                    "severity": "high"
                }
            ]
        
        הערות:
            - שומר את התוצאות ב-self.anomalies
            - רץ רק אם config.ANOMALY_DETECTION = True
        """
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
        """
        עדכון ציוני אמון לכל הקשרים
        
        מטרה: לעדכן את ציוני האמון של כל הקשרים בגרף לפי דעיכת זמן
        
        Update confidence scores for all edges based on time decay
        
        קלט (Input): אין
        
        פלט (Output): אין
        
        תופעות לוואי:
            - קורא ל-calculate_confidence() לכל קשר
            - משתמש ב-config.CONFIDENCE_DECAY_RATE
            - קשרים ישנים מקבלים ציון נמוך יותר
        
        הערות:
            - רץ כל 30 שניות יחד עם analyze()
            - חשוב לשמירת רלוונטיות הגרף
        """
        edges = self.graph.get_all_edges()
        
        for edge in edges:
            edge.calculate_confidence(config.CONFIDENCE_DECAY_RATE)
        
        logger.debug(f"Updated confidence scores for {len(edges)} edges")
    
    def get_top_nodes(self, n: int = 10) -> List[Dict]:
        """
        קבלת N הצמתים הפעילים ביותר
        
        מטרה: לספק רשימה של הצמתים עם הכי הרבה פעילות
        
        Get top N most active nodes
        
        קלט (Input):
            n: כמה צמתים להחזיר (ברירת מחדל: 10)
        
        פלט (Output):
            list: רשימת מילונים, כל אחד מכיל:
                - id: מזהה הצומת
                - ip: כתובת IP
                - mac: כתובת MAC
                - packet_count: מספר חבילות
                - centrality: ציון centrality
        
        דוגמת פלט:
            [
                {
                    "id": "aa:bb:cc:dd:ee:ff",
                    "ip": "192.168.1.1",
                    "mac": "aa:bb:cc:dd:ee:ff",
                    "packet_count": 500,
                    "centrality": 0.85
                },
                ...
            ]
        
        שימוש:
            - מוצג ב-API endpoint /api/stats
            - עוזר לזהות מכשירים חשובים ברשת
        """
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

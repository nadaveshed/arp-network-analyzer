"""
Graph Export Service - Export graph data in various formats
שירות ייצוא גרף - ייצוא נתוני הגרף לפורמטים שונים
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from models.graph import NetworkGraph
import config

logger = logging.getLogger(__name__)


class GraphExporter:
    """
    Service for exporting graph data to various formats
    שירות לייצוא נתוני הגרף לפורמטים שונים - JSON, GraphML, CSV
    """
    
    def __init__(self, graph: NetworkGraph):
        """
        אתחול שירות ייצוא
        
        מטרה: הכנת השירות לייצוא הגרף לפורמטים שונים
        
        קלט (Input):
            graph: אובייקט NetworkGraph לייצוא
        
        פלט (Output): אין
        
        משתנים פנימיים:
            - snapshot_dir: תיקיית snapshots (נוצרת אוטומטית)
        """
        self.graph = graph
        self.snapshot_dir = Path(config.SNAPSHOT_DIR)
        self.snapshot_dir.mkdir(exist_ok=True)
    
    def export_json(self, filepath: Optional[str] = None) -> str:
        """
        ייצוא הגרף לפורמט JSON
        
        מטרה: לשמור את כל נתוני הגרף בקובץ JSON קריא
        
        Export graph to JSON format
        
        קלט (Input):
            filepath: נתיב מותאם אישית (אופציונלי)
                     אם None - יוצר שם אוטומטי עם timestamp
        
        פלט (Output):
            str: נתיב מלא לקובץ שנוצר
                דוגמה: "snapshots/graph_20251224_114800.json"
        
        תוכן הקובץ:
            {
                "nodes": [...],  // כל הצמתים עם metadata
                "edges": [...],  // כל הקשרים עם confidence
                "stats": {...}   // סטטיסטיקות כלליות
            }
        
        שימוש:
            - גיבוי אוטומטי כל 5 דקות
            - ייצוא ידני דרך API: /api/export/json
            - שמירה סופית בעת כיבוי התוכנית
        
        הערות:
            - קובץ JSON עם indent=2 לקריאות
            - ניתן לייבא חזרה לכלים אחרים
        """
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.snapshot_dir / f"graph_{timestamp}.json"
        
        data = self.graph.to_dict()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported graph to JSON: {filepath}")
        return str(filepath)
    
    def export_graphml(self, filepath: Optional[str] = None) -> str:
        """
        ייצוא הגרף לפורמט GraphML
        
        מטרה: לייצא לפורמט תקני שניתן לייבא ל-Gephi, Cytoscape, וכלים אחרים
        
        Export graph to GraphML format (for tools like Gephi)
        
        קלט (Input):
            filepath: נתיב מותאם אישית (אופציונלי)
        
        פלט (Output):
            str: נתיב מלא לקובץ GraphML שנוצר
        
        תכונות:
            - פורמט XML תקני לגרפים
            - כולל כל ה-attributes של nodes ו-edges
            - ניתן לפתוח ב-Gephi לויזואליזציה מתקדמת
        
        נתונים מיוצאים:
            Nodes: id, ip, mac, packet_count, first_seen, last_seen
            Edges: type, confidence, observation_count
        
        שימוש:
            - ניתוח מתקדם בכלים חיצוניים
            - יצירת ויזואליזציות מקצועיות
            - שיתוף עם חוקרים אחרים
        
        הערות:
            - יוצר גרף נקי ללא אובייקטים פנימיים
            - thread-safe עם lock
        """
        import networkx as nx
        
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.snapshot_dir / f"graph_{timestamp}.graphml"
        
        with self.graph.lock:
            # Create a clean graph for export
            # יצירת גרף נקי לייצוא
            export_graph = nx.DiGraph()
            
            # Add nodes with attributes
            # הוספת צמתים עם תכונות
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
            # הוספת קשרים עם תכונות
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
        """
        ייצוא הצמתים לקובץ CSV
        
        מטרה: לייצא רשימת צמתים לפורמט טבלה פשוט
        
        Export nodes to CSV
        
        קלט (Input):
            filepath: נתיב מותאם אישית (אופציונלי)
        
        פלט (Output):
            str: נתיב מלא לקובץ CSV שנוצר
        
        עמודות בקובץ:
            ID, IP, MAC, Packet Count, First Seen, Last Seen
        
        דוגמת שורה:
            aa:bb:cc:dd:ee:ff,192.168.1.1,aa:bb:cc:dd:ee:ff,142,2025-12-24T10:00:00,2025-12-24T11:48:00
        
        שימוש:
            - ניתוח ב-Excel
            - ייבוא למסדי נתונים
            - עיבוד עם pandas
        
        הערות:
            - קובץ נפרד מ-edges
            - פורמט פשוט וקריא
        """
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
        """
        ייצוא הקשרים לקובץ CSV
        
        מטרה: לייצא רשימת קשרים לפורמט טבלה פשוט
        
        Export edges to CSV
        
        קלט (Input):
            filepath: נתיב מותאם אישית (אופציונלי)
        
        פלט (Output):
            str: נתיב מלא לקובץ CSV שנוצר
        
        עמודות בקובץ:
            Source, Target, Type, Confidence, Observations
        
        דוגמת שורה:
            aa:bb:cc:dd:ee:ff,11:22:33:44:55:66,arp_request,0.856,15
        
        שימוש:
            - ניתוח קשרים ב-Excel
            - בניית מטריצת adjacency
            - ניתוח סטטיסטי של הקשרים
        
        הערות:
            - קובץ נפרד מ-nodes
            - כולל ציוני אמון (confidence)
            - מספר תצפיות לכל קשר
        """
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

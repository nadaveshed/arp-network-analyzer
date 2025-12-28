"""
CLI Controller - Command-line interface for the ARP analyzer
בקר ממשק שורת פקודה - ניהול הממשק הטקסטואלי של מנתח ה-ARP
"""
import argparse
import logging
import signal
import sys
import time
import threading

from models.graph import NetworkGraph
from services.packet_capture import PacketCaptureService
from services.graph_builder import GraphBuilderService
from services.analyzer import NetworkAnalyzer
from services.exporter import GraphExporter
from services.visualizer import GraphVisualizer
from controllers.api_controller import APIController
import config

logger = logging.getLogger(__name__)


class CLIController:
    """
    Command-line interface controller
    בקר ממשק שורת פקודה - מתאם בין המשתמש לשירותי המערכת
    """
    
    def __init__(self):
        """
        אתחול בקר CLI
        מטרה: יצירת כל השירותים הנדרשים להרצת המערכת
        """
        self.graph = NetworkGraph()  # גרף הרשת המרכזי
        self.capture_service = None  # שירות לכידת חבילות
        self.graph_builder = None  # שירות בניית הגרף
        self.analyzer = None  # שירות ניתוח הרשת
        self.api_controller = None  # בקר API אופציונלי
        self.running = False  # דגל ריצה
        self.analysis_thread = None  # תהליך ניתוח מקבילי
    
    def run(self, args):
        """
        פונקציית ההרצה הראשית
        מטרה: להפעיל את כל המערכת - לכידת חבילות, ניתוח, ו-API
        
        Main execution method
        
        Args:
            args: ארגומנטים מעובדים משורת הפקודה
        """
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, args.log_level),
            format=config.LOG_FORMAT
        )
        
        logger.info("=== ARP Network Analyzer Starting ===")
        
        # Initialize services
        self.capture_service = PacketCaptureService(args.interface)
        self.graph_builder = GraphBuilderService(self.graph)
        self.analyzer = NetworkAnalyzer(self.graph)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Start packet capture
        self.capture_service.start(self.graph_builder.process_packet)
        self.running = True
        
        # Start periodic analysis
        if config.ENABLE_ENRICHMENT:
            self.analysis_thread = threading.Thread(
                target=self._periodic_analysis,
                daemon=True
            )
            self.analysis_thread.start()
        
        # Start API server if requested
        if args.api:
            self.api_controller = APIController(self.graph, self.analyzer)
            logger.info(f"Web UI available at http://localhost:{config.API_PORT}")
            self.api_controller.run()
        else:
            # CLI-only mode: just wait
            logger.info("Running in CLI mode. Press Ctrl+C to stop.")
            self._status_loop()
    
    def _periodic_analysis(self):
        """
        הרצת ניתוח תקופתי של הגרף
        מטרה: לעדכן מטריקות ציון אמון וניתוחים כל 30 שניות
        רץ בתהליך נפרד (thread) כדי לא לחסום את לכידת החבילות
        """
        while self.running:
            time.sleep(config.ENRICHMENT_INTERVAL)
            if self.running:
                try:
                    self.analyzer.analyze()
                    self.analyzer.update_confidence_scores()
                except Exception as e:
                    logger.error(f"Analysis error: {e}")
    
    def _status_loop(self):
        """
        הדפסת עדכוני סטטוס במצב CLI
        מטרה: להציג למשתמש סטטיסטיקות כל 10 שניות כאשר רץ ללא ממשק ווב
        """
        while self.running:
            time.sleep(10)
            if self.running:
                stats = self.graph.get_stats()
                capture_stats = self.capture_service.get_status()
                builder_stats = self.graph_builder.get_stats()
                
                logger.info(
                    f"Status: {stats['node_count']} nodes, "
                    f"{stats['edge_count']} edges, "
                    f"{capture_stats['packets_captured']} packets captured, "
                    f"{builder_stats['packets_processed']} processed"
                )
    
    def _signal_handler(self, signum, frame):
        """
        טיפול באותות כיבוי (Ctrl+C)
        מטרה: לתפוס אותות SIGINT/SIGTERM ולבצע כיבוי מסודר
        """
        logger.info("\nShutting down gracefully...")
        self.shutdown()
    
    def shutdown(self):
        """
        ביצוע כיבוי מסודר של המערכת
        מטרה: לעצור לכידת חבילות, לייצא snapshot סופי, וליצור ויזואליזציה
        """
        self.running = False
        
        # Stop packet capture
        if self.capture_service:
            self.capture_service.stop()
        
        # Export final snapshot
        logger.info("Exporting final snapshot...")
        exporter = GraphExporter(self.graph)
        json_path = exporter.export_json()
        logger.info(f"Final snapshot saved to: {json_path}")
        
        # Generate visualization
        visualizer = GraphVisualizer(self.graph)
        html_path = visualizer.generate_html("snapshots/final_visualization.html")
        logger.info(f"Visualization saved to: {html_path}")
        
        # Print final stats
        stats = self.graph.get_stats()
        logger.info(f"Final stats: {stats}")
        
        logger.info("Shutdown complete.")
        sys.exit(0)


def main():
    """
    נקודת הכניסה הראשית לתוכנית
    מטרה: לפרסר ארגומנטים משורת הפקודה ולהפעיל את הבקר
    """
    parser = argparse.ArgumentParser(
        description="Passive ARP Network Analysis Tool"
    )
    
    parser.add_argument(
        '-i', '--interface',
        type=str,
        default=None,
        help='Network interface to capture on (default: auto-detect)'
    )
    
    parser.add_argument(
        '--api',
        action='store_true',
        help='Start web API server and UI'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default=config.LOG_LEVEL,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    controller = CLIController()
    controller.run(args)


if __name__ == '__main__':
    main()

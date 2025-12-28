"""
API Controller - Flask REST API for graph access
"""
from flask import Flask, jsonify, send_file
import logging

from models.graph import NetworkGraph
from services.analyzer import NetworkAnalyzer
from services.visualizer import GraphVisualizer
from services.exporter import GraphExporter
import config

logger = logging.getLogger(__name__)


class APIController:
    """Flask API controller for accessing graph data"""
    
    def __init__(self, graph: NetworkGraph, analyzer: NetworkAnalyzer):
        self.graph = graph
        self.analyzer = analyzer
        self.visualizer = GraphVisualizer(graph)
        self.exporter = GraphExporter(graph)
        
        self.app = Flask(__name__)
        self.app.config['JSON_SORT_KEYS'] = False
        self._setup_routes()
    
    def _setup_routes(self):
        """Configure API routes"""
        
        @self.app.route('/')
        def index():
            """Serve the visualization page"""
            html_path = self.visualizer.generate_html("static/index.html")
            return send_file(html_path)
        
        @self.app.route('/api/graph')
        def get_graph():
            """Get complete graph data"""
            return jsonify(self.graph.to_dict())
        
        @self.app.route('/api/nodes')
        def get_nodes():
            """Get all nodes"""
            nodes = [node.to_dict() for node in self.graph.get_all_nodes()]
            return jsonify({"nodes": nodes, "count": len(nodes)})
        
        @self.app.route('/api/edges')
        def get_edges():
            """Get all edges"""
            edges = [edge.to_dict() for edge in self.graph.get_all_edges()]
            return jsonify({"edges": edges, "count": len(edges)})
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get graph statistics"""
            stats = self.graph.get_stats()
            stats['top_nodes'] = self.analyzer.get_top_nodes(5)
            stats['anomalies'] = self.analyzer.anomalies
            return jsonify(stats)
        
        @self.app.route('/api/analysis')
        def get_analysis():
            """Get latest analysis results"""
            if self.analyzer.last_analysis:
                return jsonify(self.analyzer.last_analysis)
            return jsonify({"message": "No analysis performed yet"}), 404
        
        @self.app.route('/api/export/json')
        def export_json():
            """Export graph as JSON"""
            filepath = self.exporter.export_json()
            return send_file(filepath, as_attachment=True)
        
        @self.app.route('/api/export/graphml')
        def export_graphml():
            """Export graph as GraphML"""
            filepath = self.exporter.export_graphml()
            return send_file(filepath, as_attachment=True)
        
        @self.app.route('/api/d3')
        def get_d3_data():
            """Get D3.js compatible data"""
            return jsonify(self.visualizer.generate_d3_data())
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """
        Start the Flask API server
        
        Args:
            host: Host to bind to
            port: Port to listen on
            debug: Enable debug mode
        """
        host = host or config.API_HOST
        port = port or config.API_PORT
        debug = debug if debug is not None else config.API_DEBUG
        
        logger.info(f"Starting API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)

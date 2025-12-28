from flask import Flask, jsonify, send_file
import logging

from models.graph import NetworkGraph
from services.analyzer import NetworkAnalyzer
from services.exporter import GraphExporter
import config

logger = logging.getLogger(__name__)


class APIController:
    
    def __init__(self, graph: NetworkGraph, analyzer: NetworkAnalyzer):
        self.graph = graph
        self.analyzer = analyzer
        self.exporter = GraphExporter(graph)
        
        self.app = Flask(__name__)
        self.app.config['JSON_SORT_KEYS'] = False
        self._setup_routes()
    
    def _setup_routes(self):
        
        @self.app.route('/')
        def index():
            """
            Home page - returns API information
            """
            return jsonify({
                "name": "ARP Network Analyzer API",
                "version": "1.0",
                "endpoints": {
                    "GET /": "This help message",
                    "GET /api/graph": "Complete graph data (nodes + edges)",
                    "GET /api/nodes": "List of all nodes",
                    "GET /api/edges": "List of all edges",
                    "GET /api/stats": "Graph statistics + top nodes + anomalies",
                    "GET /api/analysis": "Latest analysis results",
                    "GET /api/d3": "D3.js compatible data format",
                    "GET /api/export/json": "Download graph as JSON file",
                    "GET /api/export/graphml": "Download graph as GraphML file"
                },
                "example": "curl http://localhost:5000/api/stats"
            })
        
        @self.app.route('/api/graph')
        def get_graph():
            return jsonify(self.graph.to_dict())
        
        @self.app.route('/api/nodes')
        def get_nodes():
            nodes = [node.to_dict() for node in self.graph.get_all_nodes()]
            return jsonify({"nodes": nodes, "count": len(nodes)})
        
        @self.app.route('/api/edges')
        def get_edges():
            edges = [edge.to_dict() for edge in self.graph.get_all_edges()]
            return jsonify({"edges": edges, "count": len(edges)})
        
        @self.app.route('/api/stats')
        def get_stats():
            stats = self.graph.get_stats()
            stats['top_nodes'] = self.analyzer.get_top_nodes(5)
            stats['anomalies'] = self.analyzer.anomalies
            return jsonify(stats)
        
        @self.app.route('/api/analysis')
        def get_analysis():
            if self.analyzer.last_analysis:
                return jsonify(self.analyzer.last_analysis)
            return jsonify({"message": "No analysis performed yet"}), 404
        
        @self.app.route('/api/export/json')
        def export_json():
            filepath = self.exporter.export_json()
            return send_file(filepath, as_attachment=True)
        
        @self.app.route('/api/export/graphml')
        def export_graphml():
            filepath = self.exporter.export_graphml()
            return send_file(filepath, as_attachment=True)
        
        @self.app.route('/api/d3')
        def get_d3_data():
            from services.visualizer import GraphVisualizer
            visualizer = GraphVisualizer(self.graph)
            return jsonify(visualizer.generate_d3_data())
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        host = host or config.API_HOST
        port = port or config.API_PORT
        debug = debug if debug is not None else config.API_DEBUG
        
        logger.info(f"Starting API server on {host}:{port}")
        logger.info("API endpoints available - visit http://localhost:5000/ for help")
        self.app.run(host=host, port=port, debug=debug, threaded=True)

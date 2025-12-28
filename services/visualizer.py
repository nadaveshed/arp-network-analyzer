import json
import logging
from typing import Dict, List
from pathlib import Path

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
    
    def generate_html(self, output_path: str = "visualization.html") -> str:
        d3_data = self.generate_d3_data()
        stats = self.graph.get_stats()
        
        html_content = self._get_html_template(d3_data, stats)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML visualization: {output_path}")
        return output_path
    
    def _get_html_template(self, data: Dict, stats: Dict) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARP Network Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e27;
            color: #e0e0e0;
        }}
        #header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        #stats {{
            display: flex;
            gap: 30px;
            margin-top: 10px;
            font-size: 14px;
        }}
        .stat {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .stat-value {{
            font-weight: bold;
            color: #ffd700;
        }}
        #graph {{
            width: 100%;
            height: calc(100vh - 120px);
        }}
        .node {{
            cursor: pointer;
            stroke: #fff;
            stroke-width: 2px;
        }}
        .node.high {{ fill: #ff6b6b; }}
        .node.medium {{ fill: #4ecdc4; }}
        .node.low {{ fill: #95e1d3; }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
        }}
        .link.arp_request {{
            stroke: #667eea;
            stroke-dasharray: 5,5;
        }}
        .link.arp_reply {{
            stroke: #764ba2;
        }}
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: #fff;
            padding: 12px;
            border-radius: 8px;
            pointer-events: none;
            font-size: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            display: none;
        }}
        .legend {{
            position: absolute;
            top: 140px;
            right: 20px;
            background: rgba(10, 14, 39, 0.9);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #667eea;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 5px 0;
            font-size: 12px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🌐 ARP Network Analysis</h1>
        <div id="stats">
            <div class="stat">
                <span>Nodes:</span>
                <span class="stat-value">{stats['node_count']}</span>
            </div>
            <div class="stat">
                <span>Connections:</span>
                <span class="stat-value">{stats['edge_count']}</span>
            </div>
            <div class="stat">
                <span>Total Observations:</span>
                <span class="stat-value">{stats['total_observations']}</span>
            </div>
        </div>
    </div>
    
    <div class="legend">
        <div style="font-weight: bold; margin-bottom: 10px;">Activity Level</div>
        <div class="legend-item">
            <div class="legend-color" style="background: #ff6b6b;"></div>
            <span>High</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #4ecdc4;"></div>
            <span>Medium</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #95e1d3;"></div>
            <span>Low</span>
        </div>
    </div>
    
    <svg id="graph"></svg>
    <div class="tooltip" id="tooltip"></div>
    
    <script>
        const data = {json.dumps(data)};
        
        const width = window.innerWidth;
        const height = window.innerHeight - 120;
        
        const svg = d3.select("#graph")
            .attr("width", width)
            .attr("height", height);
        
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => d.size + 5));
        
        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .enter().append("line")
            .attr("class", d => "link " + d.type)
            .attr("stroke-width", d => d.width);
        
        const node = svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .enter().append("circle")
            .attr("class", d => "node " + d.group)
            .attr("r", d => d.size)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip);
        
        const tooltip = d3.select("#tooltip");
        
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        function showTooltip(event, d) {{
            tooltip
                .style("display", "block")
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px")
                .html(`
                    <strong>${{d.label}}</strong><br>
                    IP: ${{d.ip || 'N/A'}}<br>
                    MAC: ${{d.mac || 'N/A'}}<br>
                    Packets: ${{d.packet_count}}<br>
                    Centrality: ${{d.centrality.toFixed(3)}}
                `);
        }}
        
        function hideTooltip() {{
            tooltip.style("display", "none");
        }}
    </script>
</body>
</html>"""

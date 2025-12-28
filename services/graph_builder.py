"""
Graph Builder Service - Processes ARP packets and builds the network graph
שירות בניית גרף - מעבד חבילות ARP ובונה את גרף הרשת
"""
import logging
from typing import Optional

from models.graph import NetworkGraph
from models.node import NetworkNode
from models.edge import Connection
from utils.arp_parser import (
    extract_arp_info,
    classify_arp_type,
    validate_arp_packet,
    get_relationship_endpoints
)
from utils.transformers import normalize_mac

logger = logging.getLogger(__name__)


class GraphBuilderService:
    """
    Service for building and maintaining the network graph from ARP packets
    שירות לבניה ותחזוקה של גרף הרשת מחבילות ARP - הלב של המערכת
    """
    
    def __init__(self, graph: NetworkGraph):
        self.graph = graph
        self.packets_processed = 0
        self.packets_rejected = 0
    
    def process_packet(self, packet):
        """
        Process a single ARP packet and update the graph
        
        Args:
            packet: Scapy packet object
        """
        # Extract ARP information
        arp_info = extract_arp_info(packet)
        if not arp_info:
            self.packets_rejected += 1
            return
        
        # Validate packet
        if not validate_arp_packet(arp_info):
            self.packets_rejected += 1
            logger.debug(f"Rejected invalid ARP packet: {arp_info}")
            return
        
        # Normalize MAC addresses
        arp_info["src_mac"] = normalize_mac(arp_info["src_mac"])
        if arp_info["dst_mac"]:
            arp_info["dst_mac"] = normalize_mac(arp_info["dst_mac"])
        
        # Get relationship endpoints
        source_info, target_info = get_relationship_endpoints(arp_info)
        
        # Create or update nodes
        source_node = self._create_node(source_info)
        target_node = self._create_node(target_info)
        
        self.graph.add_or_update_node(source_node)
        if target_node:  # Target might not have MAC in requests
            self.graph.add_or_update_node(target_node)
        
        # Create or update edge
        if source_node and target_node:
            connection = self._create_connection(
                source_node,
                target_node,
                classify_arp_type(arp_info)
            )
            self.graph.add_or_update_edge(connection)
        
        self.packets_processed += 1
        
        if self.packets_processed % 10 == 0:
            logger.debug(f"Processed {self.packets_processed} packets, "
                        f"rejected {self.packets_rejected}")
    
    def _create_node(self, node_info: dict) -> Optional[NetworkNode]:
        """
        Create a NetworkNode from parsed info
        
        Args:
            node_info: Dictionary with 'ip' and 'mac' keys
        
        Returns:
            NetworkNode or None if insufficient info
        """
        ip = node_info.get("ip")
        mac = node_info.get("mac")
        
        if not ip and not mac:
            return None
        
        try:
            return NetworkNode(ip=ip, mac=mac)
        except ValueError:
            return None
    
    def _create_connection(
        self,
        source: NetworkNode,
        target: NetworkNode,
        arp_type: str
    ) -> Connection:
        """
        Create a Connection between two nodes
        
        Args:
            source: Source NetworkNode
            target: Target NetworkNode
            arp_type: "request" or "reply"
        
        Returns:
            Connection object
        """
        relationship_type = (
            Connection.ARP_REQUEST if arp_type == "request"
            else Connection.ARP_REPLY
        )
        
        return Connection(
            source_id=source.get_id(),
            target_id=target.get_id(),
            relationship_type=relationship_type
        )
    
    def get_stats(self) -> dict:
        """Get processing statistics"""
        return {
            "packets_processed": self.packets_processed,
            "packets_rejected": self.packets_rejected,
            "rejection_rate": (
                self.packets_rejected / max(1, self.packets_processed + self.packets_rejected)
            )
        }
